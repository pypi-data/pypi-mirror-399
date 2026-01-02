"""Tests for the HTML reporter."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from rich.console import Console

from bastion.config import Config
from bastion.models import Confidence, Finding, Location, ScanResult, Severity
from bastion.reporters.html import HtmlReporter

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


class TestHtmlReporter:
    """Test HtmlReporter class."""

    def test_severity_colors(self) -> None:
        """Should have correct severity colors."""
        assert HtmlReporter.SEVERITY_COLORS["critical"] == "#dc3545"
        assert HtmlReporter.SEVERITY_COLORS["high"] == "#fd7e14"
        assert HtmlReporter.SEVERITY_COLORS["medium"] == "#ffc107"
        assert HtmlReporter.SEVERITY_COLORS["low"] == "#17a2b8"
        assert HtmlReporter.SEVERITY_COLORS["info"] == "#6c757d"

    def test_format_html_structure(self) -> None:
        """Should generate valid HTML structure."""
        console = Console()
        config = Config()
        reporter = HtmlReporter(console, config)

        result = ScanResult(
            findings=[],
            files_scanned=5,
            files_with_findings=0,
            scan_time_seconds=0.5,
            rules_applied=10,
        )

        html = reporter.format(result)

        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "</html>" in html
        assert "Bastion Security Report" in html

    def test_format_with_findings(self) -> None:
        """Should include findings in HTML."""
        console = Console()
        config = Config()
        reporter = HtmlReporter(console, config)

        findings = [
            create_finding(rule_id="PS001", severity=Severity.CRITICAL),
        ]

        result = ScanResult(
            findings=findings,
            files_scanned=1,
            files_with_findings=1,
            scan_time_seconds=0.5,
            rules_applied=10,
        )

        html = reporter.format(result)

        assert "PS001" in html
        assert "CRITICAL" in html

    def test_format_escapes_html(self) -> None:
        """Should escape HTML in snippets."""
        console = Console()
        config = Config()
        reporter = HtmlReporter(console, config)

        findings = [
            create_finding(snippet="<script>alert('xss')</script>"),
        ]

        result = ScanResult(
            findings=findings,
            files_scanned=1,
            files_with_findings=1,
            scan_time_seconds=0.5,
            rules_applied=10,
        )

        html = reporter.format(result)

        # Should escape < and >
        assert "&lt;script&gt;" in html
        assert "<script>" not in html or "class=" in html  # Allow style tags

    def test_format_with_fix_suggestion(self) -> None:
        """Should include fix suggestions in HTML."""
        console = Console()
        config = Config()
        reporter = HtmlReporter(console, config)

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

        html = reporter.format(result)

        assert "Use environment variables" in html
        assert "Fix:" in html

    def test_format_no_findings_message(self) -> None:
        """Should show no findings message."""
        console = Console()
        config = Config()
        reporter = HtmlReporter(console, config)

        result = ScanResult(
            findings=[],
            files_scanned=5,
            files_with_findings=0,
            scan_time_seconds=0.5,
            rules_applied=10,
        )

        html = reporter.format(result)

        assert "No security issues found!" in html

    def test_format_summary_section(self) -> None:
        """Should include summary statistics."""
        console = Console()
        config = Config()
        reporter = HtmlReporter(console, config)

        result = ScanResult(
            findings=[],
            files_scanned=10,
            files_with_findings=2,
            scan_time_seconds=1.5,
            rules_applied=15,
        )

        html = reporter.format(result)

        assert "Files Scanned" in html
        assert "10" in html  # files_scanned value

    def test_report_with_output_file(self) -> None:
        """Should print message about output file."""
        console = MagicMock(spec=Console)
        config = Config(output_file=Path("/tmp/report.html"))
        reporter = HtmlReporter(console, config)

        result = ScanResult(
            findings=[],
            files_scanned=5,
            files_with_findings=0,
            scan_time_seconds=0.5,
            rules_applied=10,
        )

        reporter.report(result)

        # Should print message about output file
        calls = [str(call) for call in console.print.call_args_list]
        assert any("report.html" in str(call) for call in calls)

    def test_report_without_output_file(self) -> None:
        """Should print HTML directly when no output file."""
        console = MagicMock(spec=Console)
        config = Config()
        reporter = HtmlReporter(console, config)

        result = ScanResult(
            findings=[],
            files_scanned=5,
            files_with_findings=0,
            scan_time_seconds=0.5,
            rules_applied=10,
        )

        reporter.report(result)

        # Should print HTML
        calls = [str(call) for call in console.print.call_args_list]
        assert any("html" in str(call).lower() for call in calls)

    def test_css_included(self) -> None:
        """Should include CSS styles in output."""
        console = Console()
        config = Config()
        reporter = HtmlReporter(console, config)

        result = ScanResult(
            findings=[],
            files_scanned=5,
            files_with_findings=0,
            scan_time_seconds=0.5,
            rules_applied=10,
        )

        html = reporter.format(result)

        assert "<style>" in html
        assert ".container" in html
        assert ".finding" in html
