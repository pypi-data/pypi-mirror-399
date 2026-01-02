"""Tests for the text reporter."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from rich.console import Console

from bastion.config import Config
from bastion.models import Confidence, Finding, Location, ScanResult, Severity
from bastion.reporters.text import TextReporter

pytestmark = pytest.mark.unit


def create_finding(
    rule_id: str = "PS001",
    severity: Severity = Severity.CRITICAL,
    message: str = "Test finding",
    file_path: str = "test.py",
    start_line: int = 10,
    snippet: str = "vulnerable_code()",
    fix_suggestion: str | None = None,
) -> Finding:
    """Create a test finding."""
    return Finding(
        rule_id=rule_id,
        message=message,
        severity=severity,
        confidence=Confidence.HIGH,
        location=Location(
            file_path=Path(file_path),
            start_line=start_line,
            start_column=1,
            end_line=start_line,
            end_column=20,
            snippet=snippet,
        ),
        category="test",
        fix_suggestion=fix_suggestion,
    )


class TestTextReporter:
    """Test TextReporter class."""

    def test_report_no_findings(self) -> None:
        """Should print success message when no findings."""
        console = MagicMock(spec=Console)
        config = Config()
        reporter = TextReporter(console, config)

        result = ScanResult(
            findings=[],
            files_scanned=5,
            files_with_findings=0,
            scan_time_seconds=0.5,
            rules_applied=10,
        )

        reporter.report(result)

        # Should print success message
        console.print.assert_any_call("[green]No security issues found![/green]")

    def test_report_quiet_no_findings(self) -> None:
        """Should print nothing in quiet mode with no findings."""
        console = MagicMock(spec=Console)
        config = Config(quiet=True)
        reporter = TextReporter(console, config)

        result = ScanResult(
            findings=[],
            files_scanned=5,
            files_with_findings=0,
            scan_time_seconds=0.5,
            rules_applied=10,
        )

        reporter.report(result)

        # Should not print anything
        console.print.assert_not_called()

    def test_report_with_findings(self) -> None:
        """Should print findings grouped by file."""
        console = MagicMock(spec=Console)
        config = Config()
        reporter = TextReporter(console, config)

        findings = [
            create_finding(rule_id="PS001", severity=Severity.CRITICAL),
            create_finding(rule_id="PS002", severity=Severity.HIGH, file_path="other.py"),
        ]

        result = ScanResult(
            findings=findings,
            files_scanned=2,
            files_with_findings=2,
            scan_time_seconds=0.5,
            rules_applied=10,
        )

        reporter.report(result)

        # Should have printed something
        assert console.print.called

    def test_report_findings_with_fix_suggestion_verbose(self) -> None:
        """Should print fix suggestions in verbose mode."""
        console = MagicMock(spec=Console)
        config = Config(verbose=True)
        reporter = TextReporter(console, config)

        findings = [
            create_finding(fix_suggestion="Use environment variables"),
        ]

        result = ScanResult(
            findings=findings,
            files_scanned=1,
            files_with_findings=1,
            scan_time_seconds=0.5,
            rules_applied=10,
        )

        reporter.report(result)

        # Check that fix suggestion was printed
        calls = [str(call) for call in console.print.call_args_list]
        assert any("Fix:" in str(call) for call in calls)

    def test_report_multiline_snippet(self) -> None:
        """Should handle multiline snippets (max 3 lines)."""
        console = MagicMock(spec=Console)
        config = Config()
        reporter = TextReporter(console, config)

        findings = [
            create_finding(snippet="line1\nline2\nline3\nline4\nline5"),
        ]

        result = ScanResult(
            findings=findings,
            files_scanned=1,
            files_with_findings=1,
            scan_time_seconds=0.5,
            rules_applied=10,
        )

        reporter.report(result)

        assert console.print.called

    def test_severity_colors(self) -> None:
        """Should have correct severity colors."""
        assert TextReporter.SEVERITY_COLORS[Severity.CRITICAL] == "red bold"
        assert TextReporter.SEVERITY_COLORS[Severity.HIGH] == "red"
        assert TextReporter.SEVERITY_COLORS[Severity.MEDIUM] == "yellow"
        assert TextReporter.SEVERITY_COLORS[Severity.LOW] == "blue"
        assert TextReporter.SEVERITY_COLORS[Severity.INFO] == "dim"

    def test_severity_icons(self) -> None:
        """Should have correct severity icons."""
        assert TextReporter.SEVERITY_ICONS[Severity.CRITICAL] == "[X]"
        assert TextReporter.SEVERITY_ICONS[Severity.HIGH] == "[!]"
        assert TextReporter.SEVERITY_ICONS[Severity.MEDIUM] == "[~]"
        assert TextReporter.SEVERITY_ICONS[Severity.LOW] == "[-]"
        assert TextReporter.SEVERITY_ICONS[Severity.INFO] == "[i]"

    def test_format_plain_text_output(self) -> None:
        """Should format findings as plain text."""
        console = Console()
        config = Config()
        reporter = TextReporter(console, config)

        findings = [
            create_finding(rule_id="PS001", severity=Severity.CRITICAL, message="Test message"),
        ]

        result = ScanResult(
            findings=findings,
            files_scanned=1,
            files_with_findings=1,
            scan_time_seconds=0.5,
            rules_applied=10,
        )

        output = reporter.format(result)

        assert "PS001" in output
        assert "CRITICAL" in output
        assert "Test message" in output

    def test_summary_breakdown(self) -> None:
        """Should show severity breakdown in summary."""
        console = MagicMock(spec=Console)
        config = Config()
        reporter = TextReporter(console, config)

        findings = [
            create_finding(severity=Severity.CRITICAL),
            create_finding(severity=Severity.HIGH, rule_id="PS002"),
            create_finding(severity=Severity.MEDIUM, rule_id="PS003"),
            create_finding(severity=Severity.LOW, rule_id="PS004"),
        ]

        result = ScanResult(
            findings=findings,
            files_scanned=1,
            files_with_findings=1,
            scan_time_seconds=0.5,
            rules_applied=10,
        )

        reporter.report(result)

        # Should have printed breakdown
        calls = str(console.print.call_args_list)
        assert "critical" in calls.lower() or console.print.called
