# ParentingBench Troubleshooting Guide

This guide helps resolve common issues when using ParentingBench.

## Installation Issues

### "Module not found" errors

**Problem**: `ModuleNotFoundError: No module named 'parentingbench'` or similar errors.

**Solutions**:
```bash
# Option 1: Install dependencies only
pip install -r requirements.txt

# Option 2: Install as a package (recommended)
pip install -e .

# Option 3: Set PYTHONPATH (temporary)
export PYTHONPATH=/path/to/ParentingBench:$PYTHONPATH
```

### "No module named 'pytest'" when running tests

**Problem**: pytest not installed.

**Solution**:
```bash
pip install pytest
# Or install all dev dependencies
pip install -e ".[dev]"
```

### Version conflicts with dependencies

**Problem**: Conflicting package versions.

**Solution**:
```bash
# Create a fresh virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## API Key Issues

### "API key not found" or authentication errors

**Problem**: Missing or invalid API keys for LLM providers.

**Solutions**:

For **OpenAI** (GPT-4, GPT-3.5, etc.):
```bash
export OPENAI_API_KEY="sk-..."
```

For **Anthropic** (Claude):
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

For **Google Gemini**:
```bash
export GEMINI_API_KEY="..."
```

**Tip**: Add these to your `~/.bashrc` or `~/.zshrc` for persistence:
```bash
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.bashrc
source ~/.bashrc
```

**Check if keys are set**:
```bash
echo $OPENAI_API_KEY
```

### Rate limiting errors

**Problem**: `RateLimitError` or `429` status codes.

**Solutions**:
- Wait a few minutes before retrying
- Reduce the number of concurrent evaluations
- Check your API usage limits on the provider's dashboard
- Consider upgrading your API plan

---

## Evaluation Issues

### Evaluation takes too long

**Problem**: Evaluations are very slow.

**Solutions**:
- Use faster models for initial testing (e.g., `gpt-3.5-turbo` instead of `gpt-4`)
- Evaluate a single scenario first: `--scenario path/to/scenario.yaml`
- Check your internet connection
- Consider using local models with Ollama or SGLang

### Invalid scenario file errors

**Problem**: Errors when loading scenario YAML files.

**Solution**: Validate your scenarios:
```bash
python scripts/validate_scenarios.py parentingbench/scenarios/**/*.yaml
```

Common issues:
- Missing required fields
- Incorrect YAML syntax (indentation)
- Invalid enum values for `age_group` or `complexity`
- Empty lists where content is required

### "Results directory not found"

**Problem**: Can't save results to output directory.

**Solution**:
```bash
# The directory will be created automatically, but ensure parent exists
mkdir -p results
```

---

## Model-Specific Issues

### OpenAI models

**Problem**: `InvalidRequestError` with GPT-4.

**Solutions**:
- Verify you have GPT-4 API access
- Check model name is correct: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`
- Verify your API key has not expired

### Anthropic (Claude) models

**Problem**: Authentication errors with Claude.

**Solutions**:
- Use full model name: `claude-3-5-sonnet-20241022`
- Verify API key starts with `sk-ant-`
- Check you have access to Claude-3.5 Sonnet

### LiteLLM (100+ providers)

**Problem**: Model not found when using LiteLLM.

**Solution**: Check [LiteLLM documentation](https://docs.litellm.ai/docs/) for correct model format:
```python
# Examples
--model openai/gpt-4
--model anthropic/claude-3-5-sonnet-20241022
--model gemini/gemini-2.0-flash-exp
--model ollama/llama3.2
```

### Ollama (local models)

**Problem**: Connection refused when using Ollama.

**Solutions**:
1. Install Ollama: https://ollama.ai
2. Pull the model: `ollama pull llama3.2`
3. Verify Ollama is running: `ollama list`
4. Use correct format: `--model ollama/llama3.2`

### SGLang (high-performance local inference)

**Problem**: SGLang server not available.

**Solutions**:
```bash
# Install SGLang
pip install "sglang[all]"

# Start SGLang server
python -m sglang.launch_server --model-path meta-llama/Llama-3.2-8B-Instruct --port 8000

# Use in ParentingBench
--model sglang/meta-llama/Llama-3.2-8B-Instruct
```

---

## Testing Issues

### Tests fail with import errors

**Problem**: Tests can't import `parentingbench` module.

**Solution**:
```bash
# Install the package in development mode
pip install -e .

# Or run with PYTHONPATH
PYTHONPATH=. pytest tests/
```

### Pre-commit hooks failing

**Problem**: Git commits blocked by pre-commit hooks.

**Solutions**:
```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run manually to fix issues
pre-commit run --all-files

# Skip hooks temporarily (not recommended)
git commit --no-verify -m "message"
```

---

## Performance Issues

### High memory usage

**Problem**: Python process using too much memory.

**Solutions**:
- Process scenarios one at a time instead of batch
- Use streaming for large evaluations
- Clear results frequently
- Consider using a machine with more RAM

### Slow scenario loading

**Problem**: Loading scenarios takes a long time.

**Solution**: Scenarios are small YAML files and should load instantly. If slow:
- Check disk I/O performance
- Verify antivirus isn't scanning files
- Ensure files aren't on a network drive

---

## Output and Results Issues

### JSON output is malformed

**Problem**: Can't parse results JSON file.

**Solution**:
```bash
# Validate JSON
python -m json.tool results/your_file.json

# Pretty-print for debugging
python -c "import json; print(json.dumps(json.load(open('results/your_file.json')), indent=2))"
```

### Missing evaluation dimensions in results

**Problem**: Not all 6 dimensions are scored.

**Solution**: This indicates an evaluation error. Check:
- Judge model responses in verbose mode: `--verbose`
- Judge model has sufficient context length
- No API errors occurred during evaluation

---

## Getting Help

If you're still experiencing issues:

1. **Check existing issues**: https://github.com/0xshre/ParentingBench/issues
2. **Run in verbose mode**: Add `--verbose` to see detailed progress
3. **Enable debug logging**: 
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```
4. **Create a new issue** with:
   - Your Python version: `python --version`
   - Your OS and version
   - The full error message
   - Steps to reproduce
   - Command you ran

## Useful Debugging Commands

```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -E 'openai|anthropic|litellm|pyyaml|pydantic'

# Test basic functionality
python demo_usage.py

# Validate all scenarios
python scripts/validate_scenarios.py parentingbench/scenarios/**/*.yaml

# Run tests
pytest tests/ -v

# Check for code issues
ruff check parentingbench tests
```

---

## Common Error Messages and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'openai'` | Missing dependency | `pip install openai` |
| `AuthenticationError` | Invalid/missing API key | Set correct API key environment variable |
| `RateLimitError` | Too many API requests | Wait and retry, or upgrade API plan |
| `InvalidRequestError` | Wrong model name | Check model name spelling |
| `ConnectionError` | Network/API unavailable | Check internet connection |
| `FileNotFoundError` | Scenario file missing | Verify file path is correct |
| `ValidationError` | Invalid scenario format | Run `validate_scenarios.py` |
| `KeyError` | Missing expected field | Check scenario has all required fields |

---

Still stuck? Don't hesitate to [open an issue](https://github.com/0xshre/ParentingBench/issues/new)!
