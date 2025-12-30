"""Load scenarios from YAML files."""

import yaml
from pathlib import Path
from typing import List
from ..schemas import Scenario, AgeGroup, Complexity


def load_scenario(scenario_path: str | Path) -> Scenario:
    """
    Load a single scenario from a YAML file.

    Args:
        scenario_path: Path to the scenario YAML file

    Returns:
        Loaded Scenario object
    """
    scenario_path = Path(scenario_path)

    if not scenario_path.exists():
        raise FileNotFoundError(f"Scenario file not found: {scenario_path}")

    with open(scenario_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Convert string enums to enum types
    if isinstance(data.get('age_group'), str):
        data['age_group'] = AgeGroup(data['age_group'])

    if isinstance(data.get('complexity'), str):
        data['complexity'] = Complexity(data['complexity'])

    return Scenario(**data)


def load_all_scenarios(scenarios_dir: str | Path = "parentingbench/scenarios") -> List[Scenario]:
    """
    Load all scenarios from a directory tree.

    Args:
        scenarios_dir: Root directory containing scenario files

    Returns:
        List of all loaded scenarios
    """
    scenarios_dir = Path(scenarios_dir)

    if not scenarios_dir.exists():
        raise FileNotFoundError(f"Scenarios directory not found: {scenarios_dir}")

    scenarios = []
    for yaml_file in scenarios_dir.rglob("*.yaml"):
        try:
            scenario = load_scenario(yaml_file)
            scenarios.append(scenario)
        except Exception as e:
            print(f"Warning: Failed to load {yaml_file}: {e}")

    return scenarios
