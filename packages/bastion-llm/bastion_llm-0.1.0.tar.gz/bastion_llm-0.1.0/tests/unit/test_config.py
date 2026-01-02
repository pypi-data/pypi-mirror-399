"""Tests for configuration management."""

from pathlib import Path

import pytest

from bastion.config import Config
from bastion.models import Severity

pytestmark = pytest.mark.unit


class TestConfig:
    """Test the Config class."""

    def test_default_config(self) -> None:
        """Default config should have sensible defaults."""
        config = Config()

        assert config.paths == [Path(".")]
        assert len(config.exclude_patterns) > 0
        assert "**/node_modules/**" in config.exclude_patterns
        assert config.min_severity == Severity.LOW
        assert config.output_format == "text"
        assert config.verbose is False
        assert config.quiet is False

    def test_from_dict_paths(self) -> None:
        """Config should parse paths from dict."""
        data = {"paths": ["/tmp/test", "/tmp/other"]}
        config = Config.from_dict(data)

        assert len(config.paths) == 2
        assert config.paths[0] == Path("/tmp/test")

    def test_from_dict_exclude(self) -> None:
        """Config should parse exclude patterns from dict."""
        data = {"exclude": ["*.test.py", "**/tests/**"]}
        config = Config.from_dict(data)

        assert config.exclude_patterns == ["*.test.py", "**/tests/**"]

    def test_from_dict_include(self) -> None:
        """Config should parse include patterns from dict."""
        data = {"include": ["**/*.py"]}
        config = Config.from_dict(data)

        assert config.include_patterns == ["**/*.py"]

    def test_from_dict_rules_paths(self) -> None:
        """Config should parse rules paths from dict."""
        data = {"rules_paths": ["/custom/rules"]}
        config = Config.from_dict(data)

        assert config.rules_paths == [Path("/custom/rules")]

    def test_from_dict_disabled_rules(self) -> None:
        """Config should parse disabled rules from dict."""
        data = {"disabled_rules": ["PS001", "PS002"]}
        config = Config.from_dict(data)

        assert config.disabled_rules == ["PS001", "PS002"]

    def test_from_dict_enabled_rules(self) -> None:
        """Config should parse enabled rules from dict."""
        data = {"enabled_rules": ["PS003"]}
        config = Config.from_dict(data)

        assert config.enabled_rules == ["PS003"]

    def test_from_dict_severity(self) -> None:
        """Config should parse severity settings from dict."""
        data = {"min_severity": "high", "fail_on": "critical"}
        config = Config.from_dict(data)

        assert config.min_severity == Severity.HIGH
        assert config.fail_on == Severity.CRITICAL

    def test_from_dict_output(self) -> None:
        """Config should parse output settings from dict."""
        data = {
            "output_format": "json",
            "output_file": "/tmp/report.json",
            "verbose": True,
            "quiet": False,
        }
        config = Config.from_dict(data)

        assert config.output_format == "json"
        assert config.output_file == Path("/tmp/report.json")
        assert config.verbose is True
        assert config.quiet is False

    def test_from_dict_ignore_nosec(self) -> None:
        """Config should parse ignore_nosec from dict."""
        data = {"ignore_nosec": True}
        config = Config.from_dict(data)

        assert config.ignore_nosec is True

    def test_to_dict(self) -> None:
        """Config should serialize to dict."""
        config = Config()
        config.min_severity = Severity.HIGH
        config.output_format = "sarif"

        data = config.to_dict()

        assert data["min_severity"] == "high"
        assert data["output_format"] == "sarif"
        assert "paths" in data
        assert "exclude" in data

    def test_from_file(self, tmp_path: Path) -> None:
        """Config should load from YAML file."""
        config_content = """
paths:
  - /app/src
exclude:
  - "**/tests/**"
min_severity: medium
output_format: json
"""
        config_file = tmp_path / "bastion.yml"
        config_file.write_text(config_content)

        config = Config.from_file(config_file)

        assert config.paths == [Path("/app/src")]
        assert "**/tests/**" in config.exclude_patterns
        assert config.min_severity == Severity.MEDIUM
        assert config.output_format == "json"

    def test_from_file_empty(self, tmp_path: Path) -> None:
        """Config should handle empty YAML file."""
        config_file = tmp_path / "empty.yml"
        config_file.write_text("")

        config = Config.from_file(config_file)

        # Should have default values
        assert config.paths == [Path(".")]

    def test_find_config_file(self, tmp_path: Path) -> None:
        """Should find config file in directory tree."""
        # Create a nested directory structure
        subdir = tmp_path / "project" / "src"
        subdir.mkdir(parents=True)

        # Create config file in project root
        config_file = tmp_path / "project" / ".bastion.yml"
        config_file.write_text("min_severity: high")

        # Should find config from subdir
        found = Config.find_config_file(subdir)

        assert found is not None
        assert found.name == ".bastion.yml"

    def test_find_config_file_not_found(self, tmp_path: Path) -> None:
        """Should return None if no config file exists."""
        subdir = tmp_path / "empty_project"
        subdir.mkdir()

        found = Config.find_config_file(subdir)

        assert found is None
