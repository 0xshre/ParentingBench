"""Save and format evaluation results."""

import json
from pathlib import Path

from ..schemas import EvaluationResult


def save_results(results: list[EvaluationResult], output_path: str | Path) -> None:
    """
    Save evaluation results to a JSON file.

    Args:
        results: List of evaluation results
        output_path: Path to save the results
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert results to dictionaries
    results_data = []
    for result in results:
        result_dict = {
            "scenario_id": result.scenario_id,
            "model_name": result.model_name,
            "overall_score": result.overall_score,
            "safety_classification": result.safety_classification.value,
            "rubric_scores": [
                {"dimension": score.dimension, "score": score.score, "reasoning": score.reasoning}
                for score in result.rubric_scores
            ],
            "model_response": result.model_response,
            "evaluator": result.evaluator,
            "metadata": result.metadata,
        }
        results_data.append(result_dict)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results_data, f, indent=2, ensure_ascii=False)

    print(f"Results saved to {output_path}")


def format_results(results: list[EvaluationResult]) -> str:
    """
    Format results as a human-readable summary.

    Args:
        results: List of evaluation results

    Returns:
        Formatted string summary
    """
    if not results:
        return "No results to display."

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
    for result in results:
        for score in result.rubric_scores:
            if score.dimension not in dimension_scores:
                dimension_scores[score.dimension] = []
            dimension_scores[score.dimension].append(score.score)

    dimension_avgs = {dim: sum(scores) / len(scores) for dim, scores in dimension_scores.items()}

    # Build summary
    summary = f"""
{'='*80}
PARENTINGBENCH EVALUATION RESULTS
{'='*80}

Model: {results[0].model_name}
Total Scenarios: {total_scenarios}
Overall Average Score: {avg_overall:.2f}/5.0

SAFETY CLASSIFICATION:
  ✅ Safe: {safety_counts.get('safe', 0)} ({safety_counts.get('safe', 0)/total_scenarios*100:.1f}%)
  ⚠️  Concerning: {safety_counts.get('concerning', 0)} ({safety_counts.get('concerning', 0)/total_scenarios*100:.1f}%)
  ❌ Harmful: {safety_counts.get('harmful', 0)} ({safety_counts.get('harmful', 0)/total_scenarios*100:.1f}%)

AVERAGE SCORES BY DIMENSION:
"""

    for dim, avg in sorted(dimension_avgs.items(), key=lambda x: x[1], reverse=True):
        bar_length = int(avg * 10)
        bar = "█" * bar_length + "░" * (50 - bar_length)
        summary += f"  {dim:40s} {avg:.2f}/5.0  {bar}\n"

    summary += f"\n{'='*80}\n"

    return summary
