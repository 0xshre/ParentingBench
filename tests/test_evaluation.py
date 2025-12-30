"""
Test the evaluation harness with a sample scenario.
"""

import pytest
from pathlib import Path
from parentingbench.schemas import Scenario, AgeGroup, Complexity
from parentingbench.utils import load_scenario


def test_load_scenario():
    """Test loading a scenario from YAML."""
    scenario_path = Path("parentingbench/scenarios/school_age/emotional_mental_health_anxiety_school.yaml")

    if scenario_path.exists():
        scenario = load_scenario(scenario_path)

        assert scenario.scenario_id == "PB-EMH-001"
        assert scenario.age_group == AgeGroup.SCHOOL_AGE
        assert scenario.complexity == Complexity.MODERATE
        assert len(scenario.domain) >= 1
        assert len(scenario.ideal_response_should_include) > 0
        assert len(scenario.red_flags) > 0


def test_scenario_structure():
    """Test that Scenario dataclass works correctly."""
    scenario = Scenario(
        scenario_id="TEST-001",
        domain=["Test Domain"],
        age_group=AgeGroup.TEENAGE,
        age_specific="14-16",
        complexity=Complexity.SIMPLE,
        context="Test context",
        parent_question="Test question?",
        ideal_response_should_include=["Element 1", "Element 2"],
        red_flags=["Red flag 1"]
    )

    assert scenario.scenario_id == "TEST-001"
    assert scenario.age_group == AgeGroup.TEENAGE
    assert len(scenario.ideal_response_should_include) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
