"""
Compare multiple LLMs on ParentingBench scenarios.
"""

import argparse
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import time

from parentingbench.schemas import Scenario, EvaluationResult
from parentingbench.models import OpenAIModel, AnthropicModel, LiteLLMModel
from parentingbench.models.base import BaseModel
from parentingbench.evaluators import LLMJudge
from parentingbench.utils import load_scenario, load_all_scenarios, save_results
from parentingbench.evaluate import generate_parenting_advice


def get_model(model_spec: str) -> BaseModel:
    """
    Get model from specification string.

    Formats:
        - "openai:gpt-4" -> OpenAIModel
        - "anthropic:claude-3-5-sonnet-20241022" -> AnthropicModel
        - "litellm:gpt-4" or just "gpt-4" -> LiteLLMModel
        - "litellm:ollama/llama3.2" -> LiteLLMModel with Ollama
        - "litellm:gemini/gemini-2.0-flash-exp" -> LiteLLMModel with Gemini

    Args:
        model_spec: Model specification string

    Returns:
        Model adapter instance
    """
    if ":" in model_spec:
        provider, model_name = model_spec.split(":", 1)
    else:
        # Default to LiteLLM for convenience
        provider = "litellm"
        model_name = model_spec

    provider = provider.lower()

    if provider == "openai":
        return OpenAIModel(model_name=model_name)
    elif provider == "anthropic":
        return AnthropicModel(model_name=model_name)
    elif provider == "litellm":
        return LiteLLMModel(model_name=model_name)
    else:
        raise ValueError(f"Unknown provider: {provider}. " f"Supported: openai, anthropic, litellm")


def evaluate_model_on_scenarios(
    model: BaseModel, scenarios: List[Scenario], judge: LLMJudge, verbose: bool = False
) -> List[EvaluationResult]:
    """
    Evaluate a single model on all scenarios.

    Args:
        model: The model to evaluate
        scenarios: List of scenarios
        judge: LLM judge evaluator
        verbose: Print progress

    Returns:
        List of evaluation results
    """
    results = []

    for i, scenario in enumerate(scenarios, 1):
        if verbose:
            print(f"  [{i}/{len(scenarios)}] {scenario.scenario_id}...", end=" ", flush=True)

        start_time = time.time()

        try:
            # Generate response
            model_response = generate_parenting_advice(model, scenario)

            # Evaluate response
            result = judge.evaluate(
                scenario=scenario, model_response=model_response, model_name=model.model_name
            )

            # Add timing info
            result.metadata["generation_time_seconds"] = time.time() - start_time

            results.append(result)

            if verbose:
                print(
                    f"✓ Score: {result.overall_score:.2f}/5.0 ({result.safety_classification.value})"
                )

        except Exception as e:
            if verbose:
                print(f"✗ Error: {e}")
            continue

    return results


def compute_comparison_stats(all_results: Dict[str, List[EvaluationResult]]) -> Dict:
    """
    Compute comparison statistics across models.

    Args:
        all_results: Dictionary mapping model_name -> results

    Returns:
        Comparison statistics
    """
    comparison = {"models": {}, "timestamp": datetime.now().isoformat(), "total_scenarios": 0}

    for model_name, results in all_results.items():
        if not results:
            continue

        # Overall stats
        overall_scores = [r.overall_score for r in results]
        avg_overall = sum(overall_scores) / len(overall_scores)

        # Safety classification counts
        safety_counts = {}
        for result in results:
            classification = result.safety_classification.value
            safety_counts[classification] = safety_counts.get(classification, 0) + 1

        # Dimension averages
        dimension_scores = {}
        for result in results:
            for score in result.rubric_scores:
                if score.dimension not in dimension_scores:
                    dimension_scores[score.dimension] = []
                dimension_scores[score.dimension].append(score.score)

        dimension_avgs = {
            dim: sum(scores) / len(scores) for dim, scores in dimension_scores.items()
        }

        # Generation time stats
        gen_times = [r.metadata.get("generation_time_seconds", 0) for r in results]
        avg_gen_time = sum(gen_times) / len(gen_times) if gen_times else 0

        comparison["models"][model_name] = {
            "num_scenarios": len(results),
            "overall_average_score": round(avg_overall, 3),
            "safety_classifications": safety_counts,
            "dimension_averages": {k: round(v, 3) for k, v in dimension_avgs.items()},
            "avg_generation_time_seconds": round(avg_gen_time, 2),
            "min_score": round(min(overall_scores), 3),
            "max_score": round(max(overall_scores), 3),
        }

        comparison["total_scenarios"] = len(results)

    return comparison


def print_comparison_table(comparison: Dict) -> None:
    """Print a formatted comparison table."""

    print("\n" + "=" * 100)
    print("PARENTINGBENCH MODEL COMPARISON")
    print("=" * 100)
    print(f"\nTotal Scenarios: {comparison['total_scenarios']}")
    print(f"Evaluated at: {comparison['timestamp']}\n")

    # Overall scores table
    print("OVERALL SCORES:")
    print("-" * 100)
    print(
        f"{'Model':<40} {'Avg Score':<12} {'Min':<8} {'Max':<8} {'Safe %':<10} {'Avg Time (s)':<12}"
    )
    print("-" * 100)

    # Sort by average score (descending)
    sorted_models = sorted(
        comparison["models"].items(), key=lambda x: x[1]["overall_average_score"], reverse=True
    )

    for model_name, stats in sorted_models:
        safe_count = stats["safety_classifications"].get("safe", 0)
        safe_pct = (safe_count / stats["num_scenarios"] * 100) if stats["num_scenarios"] > 0 else 0

        print(
            f"{model_name:<40} "
            f"{stats['overall_average_score']:<12.3f} "
            f"{stats['min_score']:<8.3f} "
            f"{stats['max_score']:<8.3f} "
            f"{safe_pct:<10.1f} "
            f"{stats['avg_generation_time_seconds']:<12.2f}"
        )

    print("-" * 100)

    # Dimension comparison
    print("\n\nDIMENSION BREAKDOWN:")
    print("-" * 100)

    # Get all dimensions
    all_dimensions = set()
    for stats in comparison["models"].values():
        all_dimensions.update(stats["dimension_averages"].keys())

    for dimension in sorted(all_dimensions):
        print(f"\n{dimension}:")
        print("  " + "-" * 96)

        dim_scores = []
        for model_name, stats in sorted_models:
            score = stats["dimension_averages"].get(dimension, 0)
            dim_scores.append((model_name, score))

        # Sort by score for this dimension
        dim_scores.sort(key=lambda x: x[1], reverse=True)

        for model_name, score in dim_scores:
            bar_length = int(score * 10)
            bar = "█" * bar_length + "░" * (50 - bar_length)
            print(f"  {model_name:<38} {score:.3f}  {bar}")

    print("\n" + "=" * 100 + "\n")


def main():
    """Main comparison function."""
    parser = argparse.ArgumentParser(description="Compare multiple LLMs on ParentingBench")
    parser.add_argument(
        "--models",
        type=str,
        nargs="+",
        required=True,
        help="Models to compare (e.g., gpt-4 claude-3-5-sonnet-20241022 litellm:gemini/gemini-2.0-flash-exp)",
    )
    parser.add_argument(
        "--judge-model", type=str, default="gpt-4", help="Model to use as judge (default: gpt-4)"
    )
    parser.add_argument("--scenario", type=str, help="Path to a single scenario file to evaluate")
    parser.add_argument(
        "--scenarios-dir",
        type=str,
        default="parentingbench/scenarios",
        help="Directory containing scenarios (default: parentingbench/scenarios)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/comparison",
        help="Output directory for results (default: results/comparison)",
    )
    parser.add_argument("--verbose", action="store_true", help="Print detailed progress")

    args = parser.parse_args()

    # Initialize judge
    print(f"Initializing judge: {args.judge_model}")
    judge_model = get_model(args.judge_model)
    judge = LLMJudge(judge_model=judge_model, verbose=False)

    # Load scenarios
    if args.scenario:
        scenarios = [load_scenario(args.scenario)]
        print(f"Loaded 1 scenario from {args.scenario}")
    else:
        scenarios = load_all_scenarios(args.scenarios_dir)
        print(f"Loaded {len(scenarios)} scenarios from {args.scenarios_dir}")

    if not scenarios:
        print("No scenarios found!")
        return

    # Evaluate each model
    print(f"\nComparing {len(args.models)} models on {len(scenarios)} scenario(s)...\n")

    all_results = {}

    for model_spec in args.models:
        print(f"{'='*100}")
        print(f"Evaluating: {model_spec}")
        print(f"{'='*100}\n")

        try:
            model = get_model(model_spec)
            results = evaluate_model_on_scenarios(
                model=model, scenarios=scenarios, judge=judge, verbose=args.verbose
            )
            all_results[model.model_name] = results

            # Save individual results
            output_dir = Path(args.output)
            output_dir.mkdir(parents=True, exist_ok=True)

            model_filename = model.model_name.replace("/", "_").replace(":", "_")
            save_results(results, output_dir / f"{model_filename}.json")

        except Exception as e:
            print(f"Error evaluating {model_spec}: {e}\n")
            continue

    # Compute and display comparison
    if all_results:
        comparison = compute_comparison_stats(all_results)

        # Save comparison
        output_dir = Path(args.output)
        comparison_path = output_dir / "comparison.json"
        with open(comparison_path, "w", encoding="utf-8") as f:
            json.dump(comparison, f, indent=2, ensure_ascii=False)
        print(f"\nComparison saved to {comparison_path}")

        # Print comparison table
        print_comparison_table(comparison)
    else:
        print("No results to compare.")


if __name__ == "__main__":
    main()
