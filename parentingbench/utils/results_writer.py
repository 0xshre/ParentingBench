"""Save and format evaluation results."""

import json
from pathlib import Path

from ..schemas import EvaluationResult, MultiJudgeEvaluationResult


def _serialize_single_judge_result(result: EvaluationResult) -> dict:
    """Serialize a single-judge evaluation result."""
    return {
        "scenario_id": result.scenario_id,
        "model_name": result.model_name,
        "overall_score": result.overall_score,
        "safety_classification": result.safety_classification.value,
        "evaluation_type": "single_judge",
        "evaluator": result.evaluator,
        "rubric_scores": [
            {"dimension": score.dimension, "score": score.score, "reasoning": score.reasoning}
            for score in result.rubric_scores
        ],
        "model_response": result.model_response,
        "metadata": result.metadata,
    }


def _serialize_multi_judge_result(result: MultiJudgeEvaluationResult) -> dict:
    """Serialize a multi-judge evaluation result."""
    return {
        "scenario_id": result.scenario_id,
        "model_name": result.model_name,
        "overall_score": result.overall_score,
        "overall_std": result.overall_std,
        "safety_classification": result.safety_classification.value,
        "evaluation_type": "multi_judge",
        "judge_models": result.judge_models,
        "consensus_method": result.consensus_method,
        "consensus_scores": [
            {
                "dimension": cs.dimension,
                "final_score": cs.final_score,
                "agreement": cs.agreement,
                "score_std": cs.score_std,
                "votes": [
                    {
                        "judge_model": vote.judge_model,
                        "score": vote.score,
                        "reasoning": vote.reasoning,
                    }
                    for vote in cs.votes
                ],
            }
            for cs in result.consensus_scores
        ],
        "model_response": result.model_response,
        "metadata": result.metadata,
    }


def save_results(
    results: list[EvaluationResult | MultiJudgeEvaluationResult], output_path: str | Path
) -> None:
    """
    Save evaluation results to a JSON file.

    Args:
        results: List of evaluation results (single or multi-judge)
        output_path: Path to save the results
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert results to dictionaries
    results_data = []
    for result in results:
        if isinstance(result, MultiJudgeEvaluationResult):
            result_dict = _serialize_multi_judge_result(result)
        else:
            result_dict = _serialize_single_judge_result(result)
        results_data.append(result_dict)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results_data, f, indent=2, ensure_ascii=False)

    print(f"Results saved to {output_path}")


def format_results(results: list[EvaluationResult | MultiJudgeEvaluationResult]) -> str:
    """
    Format results as a human-readable summary.

    Args:
        results: List of evaluation results (single or multi-judge)

    Returns:
        Formatted string summary
    """
    if not results:
        return "No results to display."

    # Detect if this is multi-judge
    is_multi_judge = isinstance(results[0], MultiJudgeEvaluationResult)

    # Calculate aggregate statistics
    total_scenarios = len(results)
    avg_overall = sum(r.overall_score for r in results) / total_scenarios

    # Count safety classifications
    safety_counts = {}
    for result in results:
        classification = result.safety_classification.value
        safety_counts[classification] = safety_counts.get(classification, 0) + 1

    # Calculate average scores by dimension
    dimension_scores = {}
    dimension_agreements = {}  # For multi-judge

    for result in results:
        if is_multi_judge:
            for cs in result.consensus_scores:
                if cs.dimension not in dimension_scores:
                    dimension_scores[cs.dimension] = []
                    dimension_agreements[cs.dimension] = []
                dimension_scores[cs.dimension].append(cs.final_score)
                dimension_agreements[cs.dimension].append(cs.agreement)
        else:
            for score in result.rubric_scores:
                if score.dimension not in dimension_scores:
                    dimension_scores[score.dimension] = []
                dimension_scores[score.dimension].append(score.score)

    dimension_avgs = {dim: sum(scores) / len(scores) for dim, scores in dimension_scores.items()}

    # Build header
    summary = f"""
{'='*80}
PARENTINGBENCH EVALUATION RESULTS
{'='*80}

Model: {results[0].model_name}
Total Scenarios: {total_scenarios}
Overall Average Score: {avg_overall:.2f}/5.0
"""

    # Add multi-judge specific info
    if is_multi_judge:
        avg_std = sum(r.overall_std for r in results) / total_scenarios
        summary += f"Score Std Dev: {avg_std:.2f}\n"
        summary += f"Judge Panel: {', '.join(results[0].judge_models)}\n"
        summary += f"Consensus Method: {results[0].consensus_method}\n"

    summary += f"""
SAFETY CLASSIFICATION:
  Safe: {safety_counts.get('safe', 0)} ({safety_counts.get('safe', 0)/total_scenarios*100:.1f}%)
  Concerning: {safety_counts.get('concerning', 0)} ({safety_counts.get('concerning', 0)/total_scenarios*100:.1f}%)
  Harmful: {safety_counts.get('harmful', 0)} ({safety_counts.get('harmful', 0)/total_scenarios*100:.1f}%)

AVERAGE SCORES BY DIMENSION:
"""

    for dim, avg in sorted(dimension_avgs.items(), key=lambda x: x[1], reverse=True):
        bar_length = int(avg * 10)
        bar = "█" * bar_length + "░" * (50 - bar_length)

        if is_multi_judge and dim in dimension_agreements:
            avg_agreement = sum(dimension_agreements[dim]) / len(dimension_agreements[dim])
            summary += f"  {dim:35s} {avg:.2f}/5.0 (agr: {avg_agreement:.0%})  {bar}\n"
        else:
            summary += f"  {dim:35s} {avg:.2f}/5.0  {bar}\n"

    summary += f"\n{'='*80}\n"

    return summary
