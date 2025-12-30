# ParentingBench Setup Guide

## Quick Start (3 steps)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) Auto-update docs on commit
pip install pre-commit
pre-commit install

# 3. Run demo
python demo_usage.py
```

That's it! 🎉

---

## API Keys

Set environment variables for the models you want to use:

```bash
# For OpenAI (GPT-4, etc.)
export OPENAI_API_KEY="your-key"

# For Anthropic (Claude)
export ANTHROPIC_API_KEY="your-key"

# For Google Gemini
export GEMINI_API_KEY="your-key"
```

---

## Usage Examples

### Evaluate a Single Model

```bash
python -m parentingbench.evaluate \
  --model gpt-4 \
  --scenario parentingbench/scenarios/school_age/emotional_mental_health_anxiety_school.yaml
```

### Compare Multiple Models

```bash
python -m parentingbench.compare \
  --models gpt-4 claude-3-5-sonnet-20241022 gemini/gemini-2.0-flash-exp \
  --output results/comparison
```

### Use Local Models (Ollama)

```bash
# First install Ollama: https://ollama.ai
ollama pull llama3.2

# Then evaluate
python -m parentingbench.evaluate --model ollama/llama3.2
```

---

## Development

```bash
# Run tests
pytest tests/ -v

# Update documentation
python scripts/update_docs.py

# Or let pre-commit do it automatically
git commit -m "Your changes"  # Docs update automatically!
```

---

## Troubleshooting

**"Module not found" errors**
```bash
pip install -r requirements.txt
```

**"API key not found"**
```bash
export OPENAI_API_KEY="your-key"
```

**Pre-commit not running**
```bash
pre-commit install  # Run this once
```

---

That's everything you need! For detailed documentation, see [README.md](README.md).
