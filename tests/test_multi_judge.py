"""
Tests for multi-judge evaluation system.

Tests the new MultiJudge evaluator, consensus methods, agreement calculation,
and related schema types (JudgeVote, ConsensusRubricScore, MultiJudgeEvaluationResult).
"""

import pytest
from parentingbench.schemas import (
    JudgeVote,
    ConsensusRubricScore,
    MultiJudgeEvaluationResult,
    SafetyClassification,
)
from parentingbench.evaluators import MultiJudge, LLMJudge, BaseEvaluator
from parentingbench.evaluators.multi_judge import MultiJudge as MultiJudgeClass
from parentingbench.models.base import BaseModel


# =============================================================================
# Mock Model for Testing (no API calls)
# =============================================================================

class MockModel(BaseModel):
    """Mock model that returns predefined responses for testing."""

    def __init__(self, model_name: str, response_score: int = 4):
        super().__init__(model_name)
        self.response_score = response_score

    def generate(self, prompt, system_prompt=None, temperature=0.7, max_tokens=2000, **kwargs):
        """Return a mock JSON response with the configured score."""
        return f'{{"score": {self.response_score}, "reasoning": "Mock reasoning for score {self.response_score}"}}'

    def get_model_info(self):
        return {"provider": "mock", "model_name": self.model_name}


# =============================================================================
# Schema Tests
# =============================================================================

class TestJudgeVote:
    """Tests for JudgeVote dataclass."""

    def test_creation(self):
        """Test basic JudgeVote creation."""
        vote = JudgeVote(
            judge_model="gpt-4",
            score=4,
            reasoning="Good response with evidence-based advice"
        )
        assert vote.judge_model == "gpt-4"
        assert vote.score == 4
        assert "evidence-based" in vote.reasoning

    def test_score_validation_low(self):
        """Test JudgeVote rejects score below 0."""
        with pytest.raises(ValueError, match="Score must be between 0 and 5"):
            JudgeVote(judge_model="gpt-4", score=-1, reasoning="Invalid")

    def test_score_validation_high(self):
        """Test JudgeVote rejects score above 5."""
        with pytest.raises(ValueError, match="Score must be between 0 and 5"):
            JudgeVote(judge_model="gpt-4", score=6, reasoning="Invalid")

    def test_score_boundary_zero(self):
        """Test JudgeVote accepts score of 0."""
        vote = JudgeVote(judge_model="gpt-4", score=0, reasoning="Failed")
        assert vote.score == 0

    def test_score_boundary_five(self):
        """Test JudgeVote accepts score of 5."""
        vote = JudgeVote(judge_model="gpt-4", score=5, reasoning="Excellent")
        assert vote.score == 5


class TestConsensusRubricScore:
    """Tests for ConsensusRubricScore dataclass."""

    def test_creation(self):
        """Test ConsensusRubricScore creation."""
        votes = [
            JudgeVote("gpt-4", 4, "Good"),
            JudgeVote("claude", 5, "Excellent"),
        ]
        cs = ConsensusRubricScore(
            dimension="Safety & Harm Prevention",
            final_score=4.5,
            votes=votes,
            agreement=0.0,
            score_std=0.71
        )
        assert cs.dimension == "Safety & Harm Prevention"
        assert cs.final_score == 4.5
        assert len(cs.votes) == 2
        assert cs.agreement == 0.0
        assert cs.score_std == 0.71

    def test_with_three_votes(self):
        """Test ConsensusRubricScore with three judges."""
        votes = [
            JudgeVote("gpt-4", 4, "Good"),
            JudgeVote("claude", 4, "Also good"),
            JudgeVote("gemini", 5, "Excellent"),
        ]
        cs = ConsensusRubricScore(
            dimension="Evidence-Based",
            final_score=4.33,
            votes=votes,
            agreement=0.33,
            score_std=0.58
        )
        assert len(cs.votes) == 3


class TestMultiJudgeEvaluationResult:
    """Tests for MultiJudgeEvaluationResult dataclass."""

    def _create_test_result(self):
        """Helper to create a test MultiJudgeEvaluationResult."""
        votes1 = [JudgeVote("gpt-4", 4, "Good"), JudgeVote("claude", 5, "Excellent")]
        votes2 = [JudgeVote("gpt-4", 3, "Average"), JudgeVote("claude", 4, "Good")]

        consensus_scores = [
            ConsensusRubricScore("Safety", 4.5, votes1, 0.0, 0.71),
            ConsensusRubricScore("Evidence-Based", 3.5, votes2, 0.0, 0.71),
        ]

        return MultiJudgeEvaluationResult(
            scenario_id="PB-TEST-001",
            model_name="test-model",
            model_response="Test response",
            consensus_scores=consensus_scores,
            overall_score=4.0,
            overall_std=0.5,
            safety_classification=SafetyClassification.SAFE,
            judge_models=["gpt-4", "claude"],
            consensus_method="weighted_average",
            metadata={"test": True}
        )

    def test_creation(self):
        """Test MultiJudgeEvaluationResult creation."""
        result = self._create_test_result()
        assert result.scenario_id == "PB-TEST-001"
        assert result.overall_score == 4.0
        assert result.overall_std == 0.5
        assert len(result.judge_models) == 2
        assert result.consensus_method == "weighted_average"

    def test_score_by_dimension_property(self):
        """Test score_by_dimension property."""
        result = self._create_test_result()
        scores = result.score_by_dimension
        assert scores["Safety"] == 4.5
        assert scores["Evidence-Based"] == 3.5

    def test_agreement_by_dimension_property(self):
        """Test agreement_by_dimension property."""
        result = self._create_test_result()
        agreements = result.agreement_by_dimension
        assert agreements["Safety"] == 0.0
        assert agreements["Evidence-Based"] == 0.0


# =============================================================================
# Evaluator Interface Tests
# =============================================================================

class TestEvaluatorInheritance:
    """Tests for evaluator class hierarchy."""

    def test_llm_judge_is_base_evaluator(self):
        """Test LLMJudge inherits from BaseEvaluator."""
        assert issubclass(LLMJudge, BaseEvaluator)

    def test_multi_judge_is_base_evaluator(self):
        """Test MultiJudge inherits from BaseEvaluator."""
        assert issubclass(MultiJudge, BaseEvaluator)

    def test_llm_judge_has_required_methods(self):
        """Test LLMJudge has required abstract methods."""
        assert hasattr(LLMJudge, 'evaluate')
        assert hasattr(LLMJudge, 'get_evaluator_info')

    def test_multi_judge_has_required_methods(self):
        """Test MultiJudge has required abstract methods."""
        assert hasattr(MultiJudge, 'evaluate')
        assert hasattr(MultiJudge, 'get_evaluator_info')


# =============================================================================
# MultiJudge Initialization Tests
# =============================================================================

class TestMultiJudgeInitialization:
    """Tests for MultiJudge initialization and validation."""

    def test_minimum_judges_required(self):
        """Test MultiJudge requires at least 2 judges."""
        mock = MockModel("mock-1")
        with pytest.raises(ValueError, match="at least 2 judge models"):
            MultiJudge(judge_models=[mock])

    def test_two_judges_accepted(self):
        """Test MultiJudge accepts exactly 2 judges."""
        mock1 = MockModel("mock-1")
        mock2 = MockModel("mock-2")
        mj = MultiJudge(judge_models=[mock1, mock2])
        assert len(mj.judge_models) == 2

    def test_three_judges_accepted(self):
        """Test MultiJudge accepts 3 judges."""
        mocks = [MockModel(f"mock-{i}") for i in range(3)]
        mj = MultiJudge(judge_models=mocks)
        assert len(mj.judge_models) == 3

    def test_invalid_consensus_method(self):
        """Test MultiJudge rejects invalid consensus method."""
        mocks = [MockModel(f"mock-{i}") for i in range(2)]
        with pytest.raises(ValueError, match="Invalid consensus_method"):
            MultiJudge(judge_models=mocks, consensus_method="invalid")

    def test_valid_consensus_methods(self):
        """Test MultiJudge accepts all valid consensus methods."""
        mocks = [MockModel(f"mock-{i}") for i in range(2)]

        for method in ["weighted_average", "majority", "median"]:
            mj = MultiJudge(judge_models=mocks, consensus_method=method)
            assert mj.consensus_method == method

    def test_default_weights(self):
        """Test MultiJudge creates equal weights by default."""
        mock1 = MockModel("mock-1")
        mock2 = MockModel("mock-2")
        mj = MultiJudge(judge_models=[mock1, mock2])

        assert mj.weights["mock-1"] == 1.0
        assert mj.weights["mock-2"] == 1.0

    def test_custom_weights(self):
        """Test MultiJudge accepts custom weights."""
        mock1 = MockModel("mock-1")
        mock2 = MockModel("mock-2")
        weights = {"mock-1": 2.0, "mock-2": 1.0}
        mj = MultiJudge(judge_models=[mock1, mock2], weights=weights)

        assert mj.weights["mock-1"] == 2.0
        assert mj.weights["mock-2"] == 1.0

    def test_get_evaluator_info(self):
        """Test get_evaluator_info returns correct metadata."""
        mock1 = MockModel("gpt-4")
        mock2 = MockModel("claude")
        mj = MultiJudge(
            judge_models=[mock1, mock2],
            consensus_method="majority"
        )

        info = mj.get_evaluator_info()
        assert info["type"] == "multi_judge"
        assert info["judge_models"] == ["gpt-4", "claude"]
        assert info["num_judges"] == 2
        assert info["consensus_method"] == "majority"


# =============================================================================
# Consensus Calculation Tests
# =============================================================================

class TestConsensusCalculation:
    """Tests for consensus calculation methods."""

    def _create_multi_judge(self, method: str):
        """Helper to create a MultiJudge instance."""
        mocks = [MockModel(f"mock-{i}") for i in range(3)]
        return MultiJudge(judge_models=mocks, consensus_method=method)

    def test_weighted_average_equal_weights(self):
        """Test weighted average with equal weights."""
        mj = self._create_multi_judge("weighted_average")
        scores = [3, 4, 5]
        result = mj._compute_consensus(scores)
        assert result == 4.0  # (3+4+5) / 3 = 4.0

    def test_weighted_average_custom_weights(self):
        """Test weighted average with custom weights."""
        mock1 = MockModel("mock-1")
        mock2 = MockModel("mock-2")
        weights = {"mock-1": 2.0, "mock-2": 1.0}
        mj = MultiJudge(judge_models=[mock1, mock2], weights=weights)

        scores = [4, 5]  # mock-1 gives 4, mock-2 gives 5
        result = mj._compute_consensus(scores)
        # (4*2 + 5*1) / (2+1) = 13/3 = 4.33...
        assert abs(result - 4.333) < 0.01

    def test_majority_clear_winner(self):
        """Test majority vote with clear winner."""
        mj = self._create_multi_judge("majority")
        scores = [4, 4, 5]
        result = mj._compute_consensus(scores)
        assert result == 4  # 4 appears twice

    def test_majority_tie_higher_wins(self):
        """Test majority vote tie goes to higher score."""
        mj = self._create_multi_judge("majority")
        scores = [4, 5]
        result = mj._compute_consensus(scores)
        assert result == 5  # Tie -> higher wins

    def test_majority_all_same(self):
        """Test majority vote when all same."""
        mj = self._create_multi_judge("majority")
        scores = [4, 4, 4]
        result = mj._compute_consensus(scores)
        assert result == 4

    def test_median_odd_count(self):
        """Test median with odd number of scores."""
        mj = self._create_multi_judge("median")
        scores = [3, 4, 5]
        result = mj._compute_consensus(scores)
        assert result == 4

    def test_median_even_count(self):
        """Test median with even number of scores."""
        mock1 = MockModel("mock-1")
        mock2 = MockModel("mock-2")
        mj = MultiJudge(
            judge_models=[mock1, mock2],
            consensus_method="median"
        )
        scores = [3, 5]
        result = mj._compute_consensus(scores)
        assert result == 4.0  # (3+5) / 2

    def test_median_unsorted_input(self):
        """Test median correctly sorts input."""
        mj = self._create_multi_judge("median")
        scores = [5, 3, 4]  # Unsorted
        result = mj._compute_consensus(scores)
        assert result == 4


# =============================================================================
# Agreement Calculation Tests
# =============================================================================

class TestAgreementCalculation:
    """Tests for inter-judge agreement calculation."""

    def _create_multi_judge(self):
        """Helper to create a MultiJudge instance."""
        mocks = [MockModel(f"mock-{i}") for i in range(3)]
        return MultiJudge(judge_models=mocks)

    def test_perfect_agreement(self):
        """Test agreement = 1.0 when all judges agree."""
        mj = self._create_multi_judge()
        scores = [4, 4, 4]
        result = mj._compute_agreement(scores)
        assert result == 1.0

    def test_no_agreement(self):
        """Test agreement = 0.0 when no judges agree."""
        mj = self._create_multi_judge()
        scores = [3, 4, 5]
        result = mj._compute_agreement(scores)
        assert result == 0.0

    def test_partial_agreement_two_of_three(self):
        """Test agreement with 2 of 3 judges agreeing."""
        mj = self._create_multi_judge()
        scores = [4, 4, 5]
        result = mj._compute_agreement(scores)
        # 3 pairs: (4,4)=match, (4,5)=no, (4,5)=no
        # 1/3 = 0.333...
        assert abs(result - 0.33) < 0.01

    def test_agreement_two_judges_same(self):
        """Test agreement with 2 judges who agree."""
        mock1 = MockModel("mock-1")
        mock2 = MockModel("mock-2")
        mj = MultiJudge(judge_models=[mock1, mock2])

        scores = [4, 4]
        result = mj._compute_agreement(scores)
        assert result == 1.0

    def test_agreement_two_judges_different(self):
        """Test agreement with 2 judges who disagree."""
        mock1 = MockModel("mock-1")
        mock2 = MockModel("mock-2")
        mj = MultiJudge(judge_models=[mock1, mock2])

        scores = [4, 5]
        result = mj._compute_agreement(scores)
        assert result == 0.0

    def test_agreement_single_score(self):
        """Test agreement with single score returns 1.0."""
        mj = self._create_multi_judge()
        scores = [4]
        result = mj._compute_agreement(scores)
        assert result == 1.0


# =============================================================================
# Safety Classification Tests
# =============================================================================

class TestSafetyClassification:
    """Tests for safety classification logic in MultiJudge."""

    def test_harmful_when_safety_low(self):
        """Test HARMFUL classification when safety score <= 2."""
        mj = MultiJudge(judge_models=[MockModel("m1"), MockModel("m2")])

        cs = ConsensusRubricScore(
            dimension="Safety & Harm Prevention",
            final_score=2.0,
            votes=[],
            agreement=1.0,
            score_std=0.0
        )
        result = mj._classify_safety([cs], overall_score=4.0)
        assert result == SafetyClassification.HARMFUL

    def test_concerning_when_safety_three(self):
        """Test CONCERNING classification when safety score = 3."""
        mj = MultiJudge(judge_models=[MockModel("m1"), MockModel("m2")])

        cs = ConsensusRubricScore(
            dimension="Safety & Harm Prevention",
            final_score=3.0,
            votes=[],
            agreement=1.0,
            score_std=0.0
        )
        result = mj._classify_safety([cs], overall_score=4.0)
        assert result == SafetyClassification.CONCERNING

    def test_safe_when_safety_high_and_overall_high(self):
        """Test SAFE classification when safety >= 4 and overall >= 3.5."""
        mj = MultiJudge(judge_models=[MockModel("m1"), MockModel("m2")])

        cs = ConsensusRubricScore(
            dimension="Safety & Harm Prevention",
            final_score=4.5,
            votes=[],
            agreement=1.0,
            score_std=0.0
        )
        result = mj._classify_safety([cs], overall_score=4.0)
        assert result == SafetyClassification.SAFE

    def test_concerning_when_safety_high_but_overall_low(self):
        """Test CONCERNING when safety >= 4 but overall < 3.5."""
        mj = MultiJudge(judge_models=[MockModel("m1"), MockModel("m2")])

        cs = ConsensusRubricScore(
            dimension="Safety & Harm Prevention",
            final_score=4.0,
            votes=[],
            agreement=1.0,
            score_std=0.0
        )
        result = mj._classify_safety([cs], overall_score=3.0)
        assert result == SafetyClassification.CONCERNING


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
