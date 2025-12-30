# ParentingBench Examples

This directory contains example outputs and usage demonstrations for ParentingBench.

## Files

### example_results.json

Sample evaluation results showing the complete output structure from running ParentingBench evaluations. This demonstrates:

- Model responses to parenting scenarios
- Rubric scores across all 6 evaluation dimensions
- Safety classifications
- Detailed reasoning for each score
- Metadata including timing information

You can generate similar results by running:

```bash
python -m parentingbench.evaluate \
  --model gpt-4 \
  --scenario parentingbench/scenarios/school_age/emotional_mental_health_anxiety_school.yaml \
  --output results/my_evaluation.json
```

## Understanding the Output

Each evaluation result contains:

1. **scenario_id**: Unique identifier for the scenario evaluated
2. **model_name**: The LLM that generated the advice
3. **model_response**: The actual parenting advice generated
4. **rubric_scores**: Array of scores (0-5) for each of the 6 dimensions:
   - Developmental Appropriateness
   - Evidence-Based Practices
   - Safety & Harm Prevention
   - Practical Applicability
   - Ethical & Cultural Sensitivity
   - Nuance & Balance
5. **overall_score**: Average across all dimensions (0-5)
6. **safety_classification**: Overall safety rating (safe/concerning/harmful)
7. **evaluator**: The judging system used (e.g., "llm_judge:gpt-4")
8. **metadata**: Additional information like generation time

## Using Example Results

You can load and analyze example results:

```python
import json
from pathlib import Path

# Load example results
with open('examples/example_results.json') as f:
    results = json.load(f)

# Analyze scores
for result in results:
    print(f"Scenario: {result['scenario_id']}")
    print(f"Model: {result['model_name']}")
    print(f"Overall Score: {result['overall_score']}/5.0")
    print(f"Safety: {result['safety_classification']}")
    print()
```

## Comparing Models

To compare multiple models, use the compare tool:

```bash
python -m parentingbench.compare \
  --models gpt-4 claude-3-5-sonnet-20241022 gemini/gemini-2.0-flash-exp \
  --output results/comparison
```

This will generate a comparison report showing relative performance across all scenarios and dimensions.
