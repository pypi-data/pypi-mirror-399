"""Tests for the rules engine."""

from pathlib import Path

import pytest

from bastion.models import Rule, Severity
from bastion.rules import BUILTIN_RULES, RuleRegistry

pytestmark = pytest.mark.unit


class TestRuleRegistry:
    """Test the RuleRegistry class."""

    def test_load_builtin_rules(self) -> None:
        """Built-in rules should load correctly."""
        registry = RuleRegistry()
        registry.load_builtin_rules()

        assert len(registry.rules) == len(BUILTIN_RULES)
        assert "PS001" in registry.rules
        assert "PS002" in registry.rules
        assert "PS003" in registry.rules

    def test_get_rule(self) -> None:
        """Get a specific rule by ID."""
        registry = RuleRegistry()
        registry.load_builtin_rules()

        rule = registry.get_rule("PS001")
        assert rule is not None
        assert rule.id == "PS001"
        assert rule.severity == Severity.CRITICAL

    def test_get_nonexistent_rule(self) -> None:
        """Getting a nonexistent rule returns None."""
        registry = RuleRegistry()
        registry.load_builtin_rules()

        rule = registry.get_rule("NONEXISTENT")
        assert rule is None

    def test_get_enabled_rules(self) -> None:
        """Get all enabled rules."""
        registry = RuleRegistry()
        registry.load_builtin_rules()

        enabled = list(registry.get_enabled_rules())
        assert len(enabled) == len(BUILTIN_RULES)

    def test_disable_rule(self) -> None:
        """Disable a rule by ID."""
        registry = RuleRegistry()
        registry.load_builtin_rules()

        initial_count = len(list(registry.get_enabled_rules()))
        registry.disable_rule("PS001")

        enabled = list(registry.get_enabled_rules())
        assert len(enabled) == initial_count - 1
        assert "PS001" not in [r.id for r in enabled]

    def test_enable_rule(self) -> None:
        """Enable a previously disabled rule."""
        registry = RuleRegistry()
        registry.load_builtin_rules()

        registry.disable_rule("PS001")
        registry.enable_rule("PS001")

        enabled = list(registry.get_enabled_rules())
        assert "PS001" in [r.id for r in enabled]

    def test_get_rules_by_severity(self) -> None:
        """Get rules by minimum severity."""
        registry = RuleRegistry()
        registry.load_builtin_rules()

        critical_rules = list(registry.get_rules_by_severity(Severity.CRITICAL))
        assert all(r.severity >= Severity.CRITICAL for r in critical_rules)

    def test_get_rules_by_category(self) -> None:
        """Get rules by category."""
        registry = RuleRegistry()
        registry.load_builtin_rules()

        injection_rules = list(registry.get_rules_by_category("prompt-injection"))
        assert len(injection_rules) > 0
        assert all(r.category == "prompt-injection" for r in injection_rules)

    def test_load_custom_rules(self, tmp_path: Path) -> None:
        """Load custom rules from YAML file."""
        custom_rule = """
rules:
  - id: CUSTOM001
    message: Custom rule for testing
    severity: high
    category: custom
    description: A custom test rule
"""
        rule_file = tmp_path / "custom_rules.yml"
        rule_file.write_text(custom_rule)

        registry = RuleRegistry()
        registry.load_rules_from_path(rule_file)

        assert "CUSTOM001" in registry.rules
        rule = registry.rules["CUSTOM001"]
        assert rule.severity == Severity.HIGH
        assert rule.category == "custom"


class TestRule:
    """Test the Rule model."""

    def test_rule_from_dict(self) -> None:
        """Create a rule from dictionary."""
        data = {
            "id": "TEST001",
            "message": "Test message",
            "severity": "high",
            "category": "test",
            "description": "Test description",
        }

        rule = Rule.from_dict(data)

        assert rule.id == "TEST001"
        assert rule.message == "Test message"
        assert rule.severity == Severity.HIGH
        assert rule.category == "test"
        assert rule.enabled is True

    def test_rule_default_values(self) -> None:
        """Test default values for optional fields."""
        data = {
            "id": "TEST002",
            "message": "Minimal rule",
        }

        rule = Rule.from_dict(data)

        assert rule.severity == Severity.MEDIUM
        assert rule.category == "prompt-injection"
        assert rule.languages == ["python"]
        assert rule.enabled is True


class TestBuiltinRules:
    """Test that built-in rules are valid."""

    def test_all_rules_have_required_fields(self) -> None:
        """All built-in rules should have required fields."""
        for rule_data in BUILTIN_RULES:
            assert "id" in rule_data
            assert "message" in rule_data
            assert "severity" in rule_data

    def test_rule_ids_are_unique(self) -> None:
        """All rule IDs should be unique."""
        rule_ids = [r["id"] for r in BUILTIN_RULES]
        assert len(rule_ids) == len(set(rule_ids))

    def test_rule_ids_follow_pattern(self) -> None:
        """Rule IDs should follow PS### pattern."""
        import re
        pattern = r"^PS\d{3}$"
        for rule_data in BUILTIN_RULES:
            assert re.match(pattern, rule_data["id"]), f"Invalid rule ID: {rule_data['id']}"

    def test_severities_are_valid(self) -> None:
        """All severities should be valid."""
        valid_severities = {"critical", "high", "medium", "low", "info"}
        for rule_data in BUILTIN_RULES:
            assert rule_data["severity"] in valid_severities
