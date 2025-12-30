# Contributing to ParentingBench

Thank you for your interest in contributing to ParentingBench! We welcome contributions from the community.

## How to Contribute

### Reporting Issues

- Use the GitHub issue tracker to report bugs or suggest features
- Provide clear descriptions and reproduction steps for bugs
- Include your Python version, OS, and relevant dependency versions

### Contributing Code

1. **Fork the repository** and create a new branch for your feature
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Make your changes** following our coding standards
4. **Run tests**: `pytest tests/ -v` to ensure all tests pass
5. **Update documentation** if you're adding new features
6. **Submit a pull request** with a clear description of your changes

### Adding New Scenarios

We especially welcome contributions of new evaluation scenarios!

1. Create a new YAML file in the appropriate directory:
   - `parentingbench/scenarios/school_age/` for ages 7-12
   - `parentingbench/scenarios/teenage/` for ages 13-18

2. Follow the scenario template structure:
   ```yaml
   scenario_id: "PB-XXX-###"  # Use appropriate domain code
   domain: ["Primary Domain", "Secondary Domain"]
   age_group: "school_age" or "teenage"
   age_specific: "7-9" or "10-12" or "13-15" or "16-18"
   complexity: "simple" or "moderate" or "complex"
   
   context: |
     Background about the situation...
   
   parent_question: |
     The actual question from the parent...
   
   challenge_elements:
     - Key challenge 1
     - Key challenge 2
   
   ideal_response_should_include:
     - Key element 1
     - Key element 2
   
   red_flags:
     - Warning sign 1
     - Warning sign 2
   
   metadata:
     created: "YYYY-MM-DD"
     difficulty_level: "simple/moderate/complex"
     requires_professional_referral: true/false
   ```

3. Test your scenario:
   ```bash
   python -m parentingbench.evaluate \
     --model gpt-4 \
     --scenario parentingbench/scenarios/your_scenario.yaml
   ```

4. Ensure your scenario addresses:
   - A real, common parenting challenge
   - Multiple evaluation dimensions (developmental, evidence-based, safety, etc.)
   - Clear criteria for what makes a good vs. problematic response
   - Cultural sensitivity considerations

### Domain Codes for Scenario IDs

- **ACA**: Academic & Learning
- **DIS**: Discipline & Behavior
- **EMH**: Emotional & Mental Health
- **SOC**: Social Development
- **SAF**: Safety & Risk
- **TEC**: Technology & Media
- **HEA**: Health & Development
- **COM**: Communication & Family Dynamics
- **IDE**: Identity & Independence

### Coding Standards

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and modular
- Add tests for new functionality

### Testing

- Write unit tests for new features
- Ensure all existing tests pass
- Aim for high test coverage
- Test edge cases and error conditions

### Documentation

- Update README.md if adding major features
- Add docstrings to new functions/classes
- Update SETUP.md if changing installation/usage
- Include examples for new features

## Code Review Process

All contributions go through code review:

1. Automated tests must pass
2. Code must follow style guidelines
3. Changes must be minimal and focused
4. Documentation must be updated

## Questions?

- Open an issue for questions about contributing
- Check existing issues and PRs for similar discussions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
