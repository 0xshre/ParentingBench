"""
Demo script for comparing multiple LLMs on ParentingBench.

This demonstrates the comparison workflow without requiring full API access.
"""

from parentingbench.schemas import (
    Scenario, AgeGroup, Complexity,
    RubricScore, EvaluationResult, SafetyClassification
)


def create_mock_results(model_name: str, scenario_id: str) -> EvaluationResult:
    """Create mock evaluation results for demonstration."""

    # Different models get different mock scores
    if "gpt-4" in model_name.lower():
        scores = [5, 5, 5, 4, 4, 4]
        overall = 4.5
        safety = SafetyClassification.SAFE
    elif "claude" in model_name.lower():
        scores = [5, 5, 5, 5, 4, 4]
        overall = 4.6
        safety = SafetyClassification.SAFE
    elif "gemini" in model_name.lower():
        scores = [4, 4, 5, 4, 4, 4]
        overall = 4.2
        safety = SafetyClassification.SAFE
    elif "llama" in model_name.lower():
        scores = [4, 3, 4, 3, 3, 4]
        overall = 3.5
        safety = SafetyClassification.CONCERNING
    else:
        scores = [3, 3, 3, 3, 3, 3]
        overall = 3.0
        safety = SafetyClassification.CONCERNING

    dimensions = [
        "Developmental Appropriateness",
        "Evidence-Based Practices",
        "Safety & Harm Prevention",
        "Practical Applicability",
        "Ethical & Cultural Sensitivity",
        "Nuance & Balance"
    ]

    rubric_scores = [
        RubricScore(
            dimension=dim,
            score=score,
            reasoning=f"Mock reasoning for {dim}"
        )
        for dim, score in zip(dimensions, scores)
    ]

    return EvaluationResult(
        scenario_id=scenario_id,
        model_name=model_name,
        model_response=f"Mock response from {model_name}",
        rubric_scores=rubric_scores,
        overall_score=overall,
        safety_classification=safety,
        evaluator="mock_judge",
        metadata={"generation_time_seconds": 2.5}
    )


def demo_comparison():
    """Demonstrate model comparison functionality."""

    print("="*100)
    print("DEMO: Multi-Model Comparison on ParentingBench")
    print("="*100)

    # Models to compare
    models = [
        "gpt-4",
        "claude-3-5-sonnet-20241022",
        "gemini/gemini-2.0-flash-exp",
        "ollama/llama3.2"
    ]

    scenarios = ["PB-EMH-001", "PB-SD-002"]

    print(f"\nComparing {len(models)} models:")
    for model in models:
        print(f"  • {model}")

    print(f"\nOn {len(scenarios)} scenarios:")
    for scenario_id in scenarios:
        print(f"  • {scenario_id}")

    # Generate mock results
    print("\n" + "-"*100)
    print("Generating mock evaluation results...")
    print("-"*100 + "\n")

    all_results = {}
    for model in models:
        results = [create_mock_results(model, sid) for sid in scenarios]
        all_results[model] = results

        print(f"✓ {model:45s} Avg Score: {sum(r.overall_score for r in results)/len(results):.2f}/5.0")

    # Display comparison
    print("\n" + "="*100)
    print("COMPARISON RESULTS")
    print("="*100)

    print("\nOVERALL SCORES:")
    print("-" * 100)
    print(f"{'Model':<45} {'Avg Score':<12} {'Min':<8} {'Max':<8} {'Safe %':<10}")
    print("-" * 100)

    # Sort by average score
    model_stats = []
    for model, results in all_results.items():
        avg_score = sum(r.overall_score for r in results) / len(results)
        min_score = min(r.overall_score for r in results)
        max_score = max(r.overall_score for r in results)
        safe_count = sum(1 for r in results if r.safety_classification == SafetyClassification.SAFE)
        safe_pct = (safe_count / len(results)) * 100

        model_stats.append((model, avg_score, min_score, max_score, safe_pct))

    model_stats.sort(key=lambda x: x[1], reverse=True)

    for model, avg, min_s, max_s, safe_pct in model_stats:
        print(f"{model:<45} {avg:<12.2f} {min_s:<8.2f} {max_s:<8.2f} {safe_pct:<10.0f}")

    print("-" * 100)

    # Dimension breakdown
    print("\n\nDIMENSION BREAKDOWN:")
    print("-" * 100)

    dimensions = [
        "Safety & Harm Prevention",
        "Evidence-Based Practices",
        "Developmental Appropriateness",
        "Practical Applicability",
        "Ethical & Cultural Sensitivity",
        "Nuance & Balance"
    ]

    for dimension in dimensions:
        print(f"\n{dimension}:")
        print("  " + "-" * 96)

        dim_scores = []
        for model, results in all_results.items():
            scores = []
            for result in results:
                for rubric_score in result.rubric_scores:
                    if rubric_score.dimension == dimension:
                        scores.append(rubric_score.score)

            avg_score = sum(scores) / len(scores) if scores else 0
            dim_scores.append((model, avg_score))

        dim_scores.sort(key=lambda x: x[1], reverse=True)

        for model, score in dim_scores:
            bar_length = int(score * 10)
            bar = '█' * bar_length + '░' * (50 - bar_length)
            print(f"  {model:<43} {score:.2f}  {bar}")

    print("\n" + "="*100)


def demo_usage_instructions():
    """Show how to run real comparisons."""

    print("\n\n" + "="*100)
    print("HOW TO RUN REAL COMPARISONS")
    print("="*100)

    print("""
To run actual model comparisons with real LLMs:

1. Install dependencies:
   pip install litellm openai anthropic

2. Set API keys:
   export OPENAI_API_KEY="your-key"
   export ANTHROPIC_API_KEY="your-key"
   export GEMINI_API_KEY="your-key"  # For Google Gemini

3. Compare multiple models:
   python -m parentingbench.compare \\
     --models gpt-4 claude-3-5-sonnet-20241022 gemini/gemini-2.0-flash-exp \\
     --scenarios-dir parentingbench/scenarios \\
     --output results/comparison \\
     --verbose

4. Compare with local models (via Ollama):
   # First, install Ollama: https://ollama.ai
   ollama pull llama3.2

   python -m parentingbench.compare \\
     --models gpt-4 litellm:ollama/llama3.2 \\
     --output results/comparison

5. Use SGLang for high-performance local inference:
   # Start SGLang server (requires GPU):
   python -m sglang.launch_server \\
     --model-path meta-llama/Llama-3.1-70B-Instruct \\
     --port 30000

   # Then compare:
   python -m parentingbench.compare \\
     --models gpt-4 sglang:meta-llama/Llama-3.1-70B-Instruct \\
     --output results/comparison

SUPPORTED PROVIDERS (via LiteLLM):
  • OpenAI: gpt-4, gpt-4-turbo, gpt-3.5-turbo
  • Anthropic: claude-3-5-sonnet-20241022, claude-3-opus-20240229
  • Google: gemini/gemini-2.0-flash-exp, vertex_ai/gemini-pro
  • Ollama (local): ollama/llama3.2, ollama/mistral
  • HuggingFace: huggingface/meta-llama/Llama-3.1-70B-Instruct
  • Together AI: together_ai/meta-llama/Llama-3-70b-chat-hf
  • And 100+ more providers!

Results will be saved to:
  • results/comparison/comparison.json - Aggregate statistics
  • results/comparison/<model-name>.json - Individual model results
""")


if __name__ == "__main__":
    demo_comparison()
    demo_usage_instructions()

    print("\n" + "="*100)
    print("✅ Comparison demo complete!")
    print("="*100 + "\n")
