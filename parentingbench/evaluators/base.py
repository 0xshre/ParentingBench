"""Base evaluator interface for ParentingBench."""

from abc import ABC, abstractmethod

from ..schemas import EvaluationResult, MultiJudgeEvaluationResult, Scenario


class BaseEvaluator(ABC):
    """
    Abstract base class for evaluation strategies.

    All evaluators (single judge, multi-judge, etc.) should inherit from this class
    and implement the required methods.
    """

    @abstractmethod
    def evaluate(
        self, scenario: Scenario, model_response: str, model_name: str
    ) -> EvaluationResult | MultiJudgeEvaluationResult:
        """
        Evaluate a model's response to a parenting scenario.

        Args:
            scenario: The parenting scenario
            model_response: The model's response to evaluate
            model_name: Name of the model being evaluated

        Returns:
            Evaluation result (single or multi-judge)
        """
        pass

    @abstractmethod
    def get_evaluator_info(self) -> dict:
        """
        Return metadata about this evaluator configuration.

        Returns:
            Dictionary containing evaluator type, model(s) used, and other config
        """
        pass
