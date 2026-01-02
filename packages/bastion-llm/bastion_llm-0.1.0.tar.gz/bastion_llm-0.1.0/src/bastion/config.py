"""Configuration management for Bastion."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from bastion.models import Severity


@dataclass
class Config:
    """Bastion configuration."""

    # Scanning options
    paths: list[Path] = field(default_factory=lambda: [Path(".")])
    exclude_patterns: list[str] = field(default_factory=lambda: [
        "**/node_modules/**",
        "**/.venv/**",
        "**/venv/**",
        "**/__pycache__/**",
        "**/.git/**",
        "**/dist/**",
        "**/build/**",
        "**/*.min.js",
    ])
    include_patterns: list[str] = field(default_factory=lambda: [
        "**/*.py",
        "**/*.js",
        "**/*.ts",
    ])

    # Rule options
    rules_paths: list[Path] = field(default_factory=list)
    disabled_rules: list[str] = field(default_factory=list)
    enabled_rules: list[str] | None = None

    # Severity filtering
    min_severity: Severity = Severity.LOW
    fail_on: Severity = Severity.HIGH

    # Output options
    output_format: str = "text"  # text, json, sarif, html
    output_file: Path | None = None
    verbose: bool = False
    quiet: bool = False
    no_color: bool = False

    # Behavior options
    ignore_nosec: bool = False

    @classmethod
    def from_file(cls, path: Path) -> "Config":
        """Load configuration from a YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        """Create Config from a dictionary."""
        config = cls()

        if "paths" in data:
            config.paths = [Path(p) for p in data["paths"]]
        if "exclude" in data:
            config.exclude_patterns = data["exclude"]
        if "include" in data:
            config.include_patterns = data["include"]
        if "rules_paths" in data:
            config.rules_paths = [Path(p) for p in data["rules_paths"]]
        if "disabled_rules" in data:
            config.disabled_rules = data["disabled_rules"]
        if "enabled_rules" in data:
            config.enabled_rules = data["enabled_rules"]
        if "min_severity" in data:
            config.min_severity = Severity(data["min_severity"])
        if "fail_on" in data:
            config.fail_on = Severity(data["fail_on"])
        if "output_format" in data:
            config.output_format = data["output_format"]
        if "output_file" in data:
            config.output_file = Path(data["output_file"])
        if "verbose" in data:
            config.verbose = data["verbose"]
        if "quiet" in data:
            config.quiet = data["quiet"]
        if "ignore_nosec" in data:
            config.ignore_nosec = data["ignore_nosec"]

        return config

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "paths": [str(p) for p in self.paths],
            "exclude": self.exclude_patterns,
            "include": self.include_patterns,
            "rules_paths": [str(p) for p in self.rules_paths],
            "disabled_rules": self.disabled_rules,
            "enabled_rules": self.enabled_rules,
            "min_severity": self.min_severity.value,
            "fail_on": self.fail_on.value,
            "output_format": self.output_format,
            "output_file": str(self.output_file) if self.output_file else None,
            "verbose": self.verbose,
            "quiet": self.quiet,
            "ignore_nosec": self.ignore_nosec,
        }

    @classmethod
    def find_config_file(cls, start_path: Path = Path(".")) -> Path | None:
        """Find a config file in the directory tree."""
        config_names = [
            ".bastion.yml", ".bastion.yaml",
            "bastion.yml", "bastion.yaml",
        ]

        current = start_path.resolve()
        while current != current.parent:
            for name in config_names:
                config_path = current / name
                if config_path.exists():
                    return config_path
            current = current.parent

        return None
