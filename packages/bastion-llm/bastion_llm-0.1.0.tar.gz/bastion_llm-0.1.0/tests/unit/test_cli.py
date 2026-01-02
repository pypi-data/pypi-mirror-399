"""Tests for the CLI module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from bastion.cli import (
    ScanOptions,
    _apply_cli_options,
    _determine_exit_code,
    _load_config,
    _print_rule,
    _write_default_config,
    init,
    main,
    rules,
    scan,
    setup_precommit,
)
from bastion.config import Config
from bastion.models import Confidence, Finding, Location, Rule, ScanResult, Severity

pytestmark = pytest.mark.unit


def create_scan_options(**kwargs) -> ScanOptions:
    """Create ScanOptions with defaults."""
    defaults = {
        "paths": (),
        "config": None,
        "output_format": "text",
        "output": None,
        "severity": "low",
        "fail_on": "high",
        "verbose": False,
        "quiet": False,
        "no_color": False,
        "exclude": (),
        "include": (),
        "disable_rule": (),
        "ignore_nosec": False,
        "taint": False,
        "diff_base": None,
        "staged": False,
    }
    defaults.update(kwargs)
    return ScanOptions(**defaults)


class TestScanOptions:
    """Test ScanOptions dataclass."""

    def test_create_default_options(self) -> None:
        """Should create options with defaults."""
        options = create_scan_options()

        assert options.paths == ()
        assert options.output_format == "text"
        assert options.verbose is False

    def test_create_custom_options(self) -> None:
        """Should create options with custom values."""
        options = create_scan_options(
            paths=("/src",),
            output_format="json",
            verbose=True,
        )

        assert options.paths == ("/src",)
        assert options.output_format == "json"
        assert options.verbose is True


class TestLoadConfig:
    """Test _load_config function."""

    def test_load_from_explicit_path(self, tmp_path: Path) -> None:
        """Should load config from explicit path."""
        config_file = tmp_path / "config.yml"
        config_file.write_text("min_severity: high")

        options = create_scan_options(config=config_file)
        cfg = _load_config(options)

        assert cfg.min_severity == Severity.HIGH

    @patch("bastion.cli.Config.find_config_file")
    def test_load_from_found_file(self, mock_find: MagicMock, tmp_path: Path) -> None:
        """Should load config from found config file."""
        config_file = tmp_path / ".bastion.yml"
        config_file.write_text("output_format: json")
        mock_find.return_value = config_file

        options = create_scan_options()
        cfg = _load_config(options)

        assert cfg.output_format == "json"

    @patch("bastion.cli.Config.find_config_file")
    def test_load_default_when_not_found(self, mock_find: MagicMock) -> None:
        """Should return default config when no file found."""
        mock_find.return_value = None

        options = create_scan_options()
        cfg = _load_config(options)

        assert cfg.output_format == "text"


class TestApplyCliOptions:
    """Test _apply_cli_options function."""

    def test_apply_severity(self) -> None:
        """Should apply severity options."""
        cfg = Config()
        options = create_scan_options(severity="high", fail_on="critical")

        _apply_cli_options(options, cfg)

        assert cfg.min_severity == Severity.HIGH
        assert cfg.fail_on == Severity.CRITICAL

    def test_apply_output_format(self) -> None:
        """Should apply output format."""
        cfg = Config()
        options = create_scan_options(output_format="sarif")

        _apply_cli_options(options, cfg)

        assert cfg.output_format == "sarif"

    def test_apply_exclude_patterns(self) -> None:
        """Should extend exclude patterns."""
        cfg = Config()
        initial_count = len(cfg.exclude_patterns)
        options = create_scan_options(exclude=("*.test.py", "**/fixtures/**"))

        _apply_cli_options(options, cfg)

        assert len(cfg.exclude_patterns) == initial_count + 2

    def test_apply_include_patterns(self) -> None:
        """Should replace include patterns."""
        cfg = Config()
        options = create_scan_options(include=("**/*.py",))

        _apply_cli_options(options, cfg)

        assert cfg.include_patterns == ["**/*.py"]

    def test_apply_disable_rules(self) -> None:
        """Should extend disabled rules."""
        cfg = Config()
        options = create_scan_options(disable_rule=("PS001", "PS002"))

        _apply_cli_options(options, cfg)

        assert "PS001" in cfg.disabled_rules
        assert "PS002" in cfg.disabled_rules

    def test_apply_flags(self) -> None:
        """Should apply boolean flags."""
        cfg = Config()
        options = create_scan_options(
            verbose=True, quiet=True, no_color=True, ignore_nosec=True
        )

        _apply_cli_options(options, cfg)

        assert cfg.verbose is True
        assert cfg.quiet is True
        assert cfg.no_color is True
        assert cfg.ignore_nosec is True

    def test_apply_output_file(self, tmp_path: Path) -> None:
        """Should apply output file."""
        cfg = Config()
        output_file = tmp_path / "report.json"
        options = create_scan_options(output=output_file)

        _apply_cli_options(options, cfg)

        assert cfg.output_file == output_file


class TestDetermineExitCode:
    """Test _determine_exit_code function."""

    def test_no_findings(self) -> None:
        """Should return 0 when no findings."""
        cfg = Config(fail_on=Severity.HIGH)
        result = ScanResult(
            findings=[],
            files_scanned=5,
            files_with_findings=0,
            scan_time_seconds=0.5,
            rules_applied=10,
        )

        exit_code = _determine_exit_code(cfg, result)

        assert exit_code == 0

    def test_findings_below_threshold(self) -> None:
        """Should return 0 when findings below fail_on threshold."""
        cfg = Config(fail_on=Severity.CRITICAL)
        result = ScanResult(
            findings=[
                Finding(
                    rule_id="PS001",
                    message="Test",
                    severity=Severity.HIGH,  # Below CRITICAL
                    confidence=Confidence.HIGH,
                    location=Location(
                        file_path=Path("test.py"),
                        start_line=1,
                        start_column=1,
                        end_line=1,
                        end_column=10,
                    ),
                )
            ],
            files_scanned=1,
            files_with_findings=1,
            scan_time_seconds=0.5,
            rules_applied=10,
        )

        exit_code = _determine_exit_code(cfg, result)

        assert exit_code == 0

    def test_findings_at_threshold(self) -> None:
        """Should return 1 when findings at fail_on threshold."""
        cfg = Config(fail_on=Severity.HIGH)
        result = ScanResult(
            findings=[
                Finding(
                    rule_id="PS001",
                    message="Test",
                    severity=Severity.HIGH,
                    confidence=Confidence.HIGH,
                    location=Location(
                        file_path=Path("test.py"),
                        start_line=1,
                        start_column=1,
                        end_line=1,
                        end_column=10,
                    ),
                )
            ],
            files_scanned=1,
            files_with_findings=1,
            scan_time_seconds=0.5,
            rules_applied=10,
        )

        exit_code = _determine_exit_code(cfg, result)

        assert exit_code == 1


class TestWriteDefaultConfig:
    """Test _write_default_config function."""

    def test_writes_config_file(self, tmp_path: Path) -> None:
        """Should write default config file."""
        config_path = tmp_path / ".bastion.yml"

        _write_default_config(config_path)

        assert config_path.exists()
        content = config_path.read_text()
        assert "Bastion Configuration" in content
        assert "exclude:" in content
        assert "include:" in content


class TestPrintRule:
    """Test _print_rule function."""

    @patch("bastion.cli.console")
    def test_prints_rule_info(self, mock_console: MagicMock) -> None:
        """Should print rule information."""
        rule = Rule(
            id="PS001",
            message="Test rule",
            severity=Severity.CRITICAL,
            category="test",
            description="Test description",
        )

        _print_rule(rule)

        # Should have printed something
        assert mock_console.print.called


class TestMainCommand:
    """Test main CLI group."""

    def test_help_output(self) -> None:
        """Should show help when invoked without command."""
        runner = CliRunner()
        result = runner.invoke(main)

        assert result.exit_code == 0
        assert "Bastion" in result.output

    def test_version_option(self) -> None:
        """Should show version."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        assert "bastion" in result.output.lower()


class TestScanCommand:
    """Test scan command."""

    def test_scan_empty_directory(self, tmp_path: Path) -> None:
        """Should scan empty directory successfully."""
        runner = CliRunner()
        result = runner.invoke(scan, [str(tmp_path)])

        assert result.exit_code == 0

    def test_scan_with_format(self, tmp_path: Path) -> None:
        """Should accept format option."""
        runner = CliRunner()
        result = runner.invoke(scan, [str(tmp_path), "--format", "json"])

        assert result.exit_code == 0

    def test_scan_quiet_mode(self, tmp_path: Path) -> None:
        """Should respect quiet mode."""
        runner = CliRunner()
        result = runner.invoke(scan, [str(tmp_path), "--quiet"])

        assert result.exit_code == 0


class TestInitCommand:
    """Test init command."""

    def test_init_creates_config(self, tmp_path: Path) -> None:
        """Should create config file."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(init)

            assert result.exit_code == 0
            assert Path(".bastion.yml").exists()

    def test_init_refuses_overwrite(self, tmp_path: Path) -> None:
        """Should refuse to overwrite without --force."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Create existing config
            Path(".bastion.yml").write_text("existing: true")

            result = runner.invoke(init)

            assert result.exit_code == 1
            assert "already exists" in result.output

    def test_init_force_overwrite(self, tmp_path: Path) -> None:
        """Should overwrite with --force."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Create existing config
            Path(".bastion.yml").write_text("existing: true")

            result = runner.invoke(init, ["--force"])

            assert result.exit_code == 0


class TestSetupPrecommitCommand:
    """Test setup-precommit command."""

    def test_shows_instructions(self) -> None:
        """Should show pre-commit instructions."""
        runner = CliRunner()
        result = runner.invoke(setup_precommit)

        assert result.exit_code == 0
        assert "pre-commit" in result.output
        assert "bastion" in result.output


class TestRulesCommand:
    """Test rules command."""

    def test_lists_rules(self) -> None:
        """Should list available rules."""
        runner = CliRunner()
        result = runner.invoke(rules)

        assert result.exit_code == 0
        assert "PS001" in result.output
        assert "Available Rules" in result.output
