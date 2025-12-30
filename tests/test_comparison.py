"""
Tests for model comparison functionality.
"""

import pytest

from parentingbench.compare import compute_comparison_stats
from parentingbench.schemas import (
    EvaluationResult,
    RubricScore,
    SafetyClassification,
)


def create_test_result(model_name: str, scenario_id: str, overall_score: float) -> EvaluationResult:
    """Helper to create test evaluation results."""
    return EvaluationResult(
        scenario_id=scenario_id,
        model_name=model_name,
        model_response="Test response",
        rubric_scores=[
            RubricScore("Safety & Harm Prevention", 5, "Good safety"),
            RubricScore("Evidence-Based Practices", 4, "Evidence-based"),
            RubricScore("Developmental Appropriateness", 4, "Age appropriate"),
        ],
        overall_score=overall_score,
        safety_classification=(
            SafetyClassification.SAFE if overall_score >= 4.0 else SafetyClassification.CONCERNING
        ),
        evaluator="test_judge",
        metadata={"generation_time_seconds": 2.5},
    )


def test_comparison_stats_single_model():
    """Test comparison statistics for a single model."""
    results = {
        "gpt-4": [
            create_test_result("gpt-4", "PB-001", 4.5),
            create_test_result("gpt-4", "PB-002", 4.3),
        ]
    }

    stats = compute_comparison_stats(results)

    assert "models" in stats
    assert "gpt-4" in stats["models"]
    assert stats["total_scenarios"] == 2

    model_stats = stats["models"]["gpt-4"]
    assert model_stats["num_scenarios"] == 2
    assert model_stats["overall_average_score"] == 4.4
    assert model_stats["min_score"] == 4.3
    assert model_stats["max_score"] == 4.5
    assert model_stats["safety_classifications"]["safe"] == 2


def test_comparison_stats_multiple_models():
    """Test comparison statistics for multiple models."""
    results = {
        "gpt-4": [
            create_test_result("gpt-4", "PB-001", 4.5),
            create_test_result("gpt-4", "PB-002", 4.3),
        ],
        "claude-3-5-sonnet": [
            create_test_result("claude-3-5-sonnet", "PB-001", 4.6),
            create_test_result("claude-3-5-sonnet", "PB-002", 4.4),
        ],
        "llama-3.2": [
            create_test_result("llama-3.2", "PB-001", 3.5),
            create_test_result("llama-3.2", "PB-002", 3.3),
        ],
    }

    stats = compute_comparison_stats(results)

    assert len(stats["models"]) == 3
    assert stats["total_scenarios"] == 2

    # Verify scores are computed correctly
    assert stats["models"]["gpt-4"]["overall_average_score"] == 4.4
    assert stats["models"]["claude-3-5-sonnet"]["overall_average_score"] == 4.5
    assert stats["models"]["llama-3.2"]["overall_average_score"] == 3.4

    # Verify safety classifications
    assert stats["models"]["llama-3.2"]["safety_classifications"]["concerning"] == 2


def test_comparison_stats_dimension_averages():
    """Test dimension average calculation."""
    results = {
        "test-model": [
            create_test_result("test-model", "PB-001", 4.3),
        ]
    }

    stats = compute_comparison_stats(results)

    dimension_avgs = stats["models"]["test-model"]["dimension_averages"]

    assert "Safety & Harm Prevention" in dimension_avgs
    assert "Evidence-Based Practices" in dimension_avgs
    assert "Developmental Appropriateness" in dimension_avgs

    assert dimension_avgs["Safety & Harm Prevention"] == 5.0
    assert dimension_avgs["Evidence-Based Practices"] == 4.0
    assert dimension_avgs["Developmental Appropriateness"] == 4.0


def test_comparison_stats_empty_results():
    """Test handling of empty results."""
    results = {"gpt-4": []}

    stats = compute_comparison_stats(results)

    # Should not include models with no results
    assert "gpt-4" not in stats["models"]


def test_comparison_stats_generation_time():
    """Test generation time statistics."""
    results = {
        "gpt-4": [
            create_test_result("gpt-4", "PB-001", 4.5),
        ]
    }

    stats = compute_comparison_stats(results)

    assert "avg_generation_time_seconds" in stats["models"]["gpt-4"]
    assert stats["models"]["gpt-4"]["avg_generation_time_seconds"] == 2.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
