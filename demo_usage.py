"""
Demo script showing how to use ParentingBench.

This demonstrates the basic workflow without requiring API keys.
"""

from parentingbench.schemas import Scenario, AgeGroup, Complexity, RubricScore, EvaluationResult, SafetyClassification
from parentingbench.utils import load_scenario, load_all_scenarios, format_results


def demo_scenario_loading():
    """Demonstrate loading scenarios."""
    print("="*80)
    print("DEMO: Loading Scenarios")
    print("="*80)

    # Load a single scenario
    scenario = load_scenario("parentingbench/scenarios/school_age/emotional_mental_health_anxiety_school.yaml")

    print(f"\n📋 Loaded Scenario: {scenario.scenario_id}")
    print(f"   Domain: {', '.join(scenario.domain)}")
    print(f"   Age Group: {scenario.age_specific} years")
    print(f"   Complexity: {scenario.complexity.value}")

    print(f"\n📝 Parent's Question:")
    print(f"   {scenario.parent_question}")

    print(f"\n✅ Ideal Response Should Include:")
    for item in scenario.ideal_response_should_include:
        print(f"   - {item}")

    print(f"\n⚠️  Red Flags to Avoid:")
    for flag in scenario.red_flags:
        print(f"   - {flag}")

    # Load all scenarios
    print(f"\n\n{'='*80}")
    print("Loading all scenarios...")
    all_scenarios = load_all_scenarios("parentingbench/scenarios")
    print(f"✓ Found {len(all_scenarios)} scenarios total")

    for s in all_scenarios:
        print(f"  - {s.scenario_id}: {s.domain[0]}")


def demo_mock_evaluation():
    """Demonstrate evaluation result structure (without actually calling LLMs)."""
    print("\n\n" + "="*80)
    print("DEMO: Evaluation Result Structure")
    print("="*80)

    # Create a mock evaluation result
    mock_result = EvaluationResult(
        scenario_id="PB-EMH-001",
        model_name="gpt-4-demo",
        model_response="This is a mock response demonstrating the structure.",
        rubric_scores=[
            RubricScore(
                dimension="Developmental Appropriateness",
                score=4,
                reasoning="Response considers the child's age and developmental stage appropriately."
            ),
            RubricScore(
                dimension="Evidence-Based Practices",
                score=5,
                reasoning="Aligns well with research on childhood anxiety and references CBT approaches."
            ),
            RubricScore(
                dimension="Safety & Harm Prevention",
                score=5,
                reasoning="Appropriately recommends professional evaluation and identifies warning signs."
            ),
            RubricScore(
                dimension="Practical Applicability",
                score=4,
                reasoning="Provides actionable advice with specific strategies parents can implement."
            ),
            RubricScore(
                dimension="Ethical & Cultural Sensitivity",
                score=4,
                reasoning="Acknowledges different approaches while respecting parental values."
            ),
            RubricScore(
                dimension="Nuance & Balance",
                score=4,
                reasoning="Balances immediate needs with long-term considerations effectively."
            ),
        ],
        overall_score=4.3,
        safety_classification=SafetyClassification.SAFE,
        evaluator="llm_judge:gpt-4"
    )

    print("\n📊 Mock Evaluation Result:")
    print(f"   Scenario: {mock_result.scenario_id}")
    print(f"   Model: {mock_result.model_name}")
    print(f"   Overall Score: {mock_result.overall_score}/5.0")
    print(f"   Safety: {mock_result.safety_classification.value}")

    print(f"\n📈 Dimension Scores:")
    for score in mock_result.rubric_scores:
        print(f"   {score.dimension:35s} {score.score}/5")
        print(f"      → {score.reasoning}")

    # Show formatted summary
    print("\n\n" + format_results([mock_result]))


def demo_usage_example():
    """Show example command-line usage."""
    print("\n\n" + "="*80)
    print("DEMO: How to Run Real Evaluations")
    print("="*80)

    print("""
To run ParentingBench with real LLM APIs, you need API keys:

1. Set environment variables:
   export OPENAI_API_KEY="your-key"
   export ANTHROPIC_API_KEY="your-key"

2. Evaluate a single scenario:
   python -m parentingbench.evaluate \\
     --model gpt-4 \\
     --scenario parentingbench/scenarios/school_age/emotional_mental_health_anxiety_school.yaml \\
     --verbose

3. Evaluate all scenarios:
   python -m parentingbench.evaluate \\
     --model claude-3-5-sonnet-20241022 \\
     --scenarios-dir parentingbench/scenarios \\
     --output results/claude-3-5-sonnet.json

4. Use a different judge model:
   python -m parentingbench.evaluate \\
     --model gpt-4o \\
     --judge-model claude-3-5-sonnet-20241022 \\
     --output results/gpt4o_judged_by_claude.json

The evaluation will:
  a) Load the scenario(s)
  b) Generate parenting advice using the model
  c) Evaluate the advice using LLM-as-judge
  d) Score across 6 dimensions (0-5 each)
  e) Classify safety (Safe/Concerning/Harmful)
  f) Save detailed results to JSON
""")


if __name__ == "__main__":
    demo_scenario_loading()
    demo_mock_evaluation()
    demo_usage_example()

    print("\n" + "="*80)
    print("✅ Demo complete! ParentingBench is ready to use.")
    print("="*80 + "\n")
