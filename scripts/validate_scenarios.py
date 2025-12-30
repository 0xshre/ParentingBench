"""
Validate scenario YAML files against the expected schema.

This script checks that scenario files:
- Have all required fields
- Use correct data types
- Follow naming conventions
- Include appropriate metadata
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any

import yaml

from parentingbench.schemas import AgeGroup, Complexity
from parentingbench.utils import load_scenario


def validate_scenario_structure(scenario_data: Dict[str, Any], file_path: str) -> List[str]:
    """
    Validate a scenario dictionary structure.

    Args:
        scenario_data: The loaded scenario dictionary
        file_path: Path to the scenario file (for error messages)

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Required fields
    required_fields = [
        "scenario_id",
        "domain",
        "age_group",
        "age_specific",
        "complexity",
        "context",
        "parent_question",
        "ideal_response_should_include",
        "red_flags",
    ]

    for field in required_fields:
        if field not in scenario_data:
            errors.append(f"Missing required field: {field}")

    # Validate scenario_id format
    if "scenario_id" in scenario_data:
        scenario_id = scenario_data["scenario_id"]
        if not scenario_id.startswith("PB-"):
            errors.append(f"scenario_id should start with 'PB-', got: {scenario_id}")

        parts = scenario_id.split("-")
        if len(parts) != 3:
            errors.append(f"scenario_id should be format 'PB-XXX-###', got: {scenario_id}")

    # Validate domain
    if "domain" in scenario_data:
        domain = scenario_data["domain"]
        if not isinstance(domain, list) or len(domain) == 0:
            errors.append("domain must be a non-empty list")

    # Validate age_group
    if "age_group" in scenario_data:
        age_group = scenario_data["age_group"]
        valid_age_groups = [e.value for e in AgeGroup]
        if age_group not in valid_age_groups:
            errors.append(f"age_group must be one of {valid_age_groups}, got: {age_group}")

    # Validate complexity
    if "complexity" in scenario_data:
        complexity = scenario_data["complexity"]
        valid_complexities = [e.value for e in Complexity]
        if complexity not in valid_complexities:
            errors.append(f"complexity must be one of {valid_complexities}, got: {complexity}")

    # Validate lists
    list_fields = ["challenge_elements", "ideal_response_should_include", "red_flags"]

    for field in list_fields:
        if field in scenario_data:
            value = scenario_data[field]
            if not isinstance(value, list):
                errors.append(f"{field} must be a list, got: {type(value).__name__}")
            elif len(value) == 0 and field in required_fields:
                errors.append(f"{field} must not be empty")

    # Validate string fields are not empty
    string_fields = ["context", "parent_question", "age_specific"]
    for field in string_fields:
        if field in scenario_data:
            value = scenario_data[field]
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{field} must be a non-empty string")

    # Check for metadata
    if "metadata" in scenario_data:
        metadata = scenario_data["metadata"]
        if not isinstance(metadata, dict):
            errors.append("metadata must be a dictionary")
        else:
            # Recommended metadata fields
            recommended = ["created", "difficulty_level", "requires_professional_referral"]
            missing_recommended = [f for f in recommended if f not in metadata]
            if missing_recommended:
                errors.append(
                    f"metadata missing recommended fields: {', '.join(missing_recommended)}"
                )
    else:
        errors.append("metadata field is recommended but missing")

    return errors


def validate_scenario_file(file_path: Path) -> bool:
    """
    Validate a single scenario file.

    Args:
        file_path: Path to the scenario YAML file

    Returns:
        True if valid, False otherwise
    """
    print(f"\nValidating: {file_path}")

    try:
        # Try to load the YAML
        with open(file_path) as f:
            scenario_data = yaml.safe_load(f)

        if scenario_data is None:
            print(f"  ❌ ERROR: File is empty or invalid YAML")
            return False

        # Validate structure
        errors = validate_scenario_structure(scenario_data, str(file_path))

        if errors:
            print(f"  ❌ VALIDATION FAILED: {len(errors)} error(s)")
            for error in errors:
                print(f"     - {error}")
            return False

        # Try to load with the actual schema
        try:
            scenario = load_scenario(str(file_path))
            print(f"  ✅ VALID: {scenario.scenario_id}")
            print(f"     Domain: {', '.join(scenario.domain)}")
            print(f"     Age: {scenario.age_specific} ({scenario.age_group.value})")
            print(f"     Complexity: {scenario.complexity.value}")
            return True
        except Exception as e:
            print(f"  ❌ ERROR loading scenario: {e}")
            return False

    except yaml.YAMLError as e:
        print(f"  ❌ YAML ERROR: {e}")
        return False
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(description="Validate ParentingBench scenario files")
    parser.add_argument("files", nargs="+", help="Scenario file(s) to validate")

    args = parser.parse_args()

    print("=" * 80)
    print("ParentingBench Scenario Validator")
    print("=" * 80)

    all_valid = True
    valid_count = 0
    invalid_count = 0

    for file_path_str in args.files:
        file_path = Path(file_path_str)

        if not file_path.exists():
            print(f"\n❌ File not found: {file_path}")
            invalid_count += 1
            all_valid = False
            continue

        if file_path.suffix not in [".yaml", ".yml"]:
            print(f"\n⚠️  Skipping non-YAML file: {file_path}")
            continue

        is_valid = validate_scenario_file(file_path)

        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1
            all_valid = False

    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Total files validated: {valid_count + invalid_count}")
    print(f"✅ Valid: {valid_count}")
    print(f"❌ Invalid: {invalid_count}")

    if all_valid:
        print("\n✅ All scenarios are valid!")
        sys.exit(0)
    else:
        print("\n❌ Some scenarios have validation errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
