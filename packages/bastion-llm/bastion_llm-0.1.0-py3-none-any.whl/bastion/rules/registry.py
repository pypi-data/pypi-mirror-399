"""Rule registry for managing security rules."""

from collections.abc import Iterator
from pathlib import Path

import yaml

from bastion.models import Rule, Severity

from .builtin_rules import BUILTIN_RULES


class RuleRegistry:
    """Registry for managing security rules."""

    def __init__(self) -> None:
        self.rules: dict[str, Rule] = {}

    def load_builtin_rules(self) -> None:
        """Load the built-in rules."""
        for rule_data in BUILTIN_RULES:
            rule = Rule.from_dict(rule_data)
            self.rules[rule.id] = rule

    def load_rules_from_path(self, path: Path) -> None:
        """Load custom rules from a file or directory."""
        path = Path(path)
        if path.is_file():
            self._load_rules_from_file(path)
        elif path.is_dir():
            for file_path in path.glob("**/*.yml"):
                self._load_rules_from_file(file_path)
            for file_path in path.glob("**/*.yaml"):
                self._load_rules_from_file(file_path)

    def _load_rules_from_file(self, file_path: Path) -> None:
        """Load rules from a YAML file."""
        with open(file_path) as f:
            data = yaml.safe_load(f)

        if not data:
            return

        rules_data = data.get("rules", [data] if "id" in data else [])
        for rule_data in rules_data:
            rule = Rule.from_dict(rule_data)
            self.rules[rule.id] = rule

    def get_rule(self, rule_id: str) -> Rule | None:
        """Get a rule by ID."""
        return self.rules.get(rule_id)

    def get_enabled_rules(self) -> Iterator[Rule]:
        """Get all enabled rules."""
        for rule in self.rules.values():
            if rule.enabled:
                yield rule

    def get_rules_by_category(self, category: str) -> Iterator[Rule]:
        """Get rules by category."""
        for rule in self.rules.values():
            if rule.category == category:
                yield rule

    def get_rules_by_severity(self, min_severity: Severity) -> Iterator[Rule]:
        """Get rules with at least the specified severity."""
        for rule in self.rules.values():
            if rule.severity >= min_severity:
                yield rule

    def disable_rule(self, rule_id: str) -> bool:
        """Disable a rule by ID."""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            return True
        return False

    def enable_rule(self, rule_id: str) -> bool:
        """Enable a rule by ID."""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            return True
        return False
