"""Tests for output reporters."""

import json
from pathlib import Path

import pytest
from rich.console import Console

from bastion.config import Config
from bastion.models import Confidence, Finding, Location, ScanResult, Severity
from bastion.reporters import (
    JsonReporter,
    SarifReporter,
    TextReporter,
    get_reporter,
)

pytestmark = pytest.mark.unit


def create_sample_result() -> ScanResult:
    """Create a sample scan result for testing."""
    findings = [
        Finding(
            rule_id="PS001",
            message="User input directly concatenated into prompt string",
            severity=Severity.CRITICAL,
            confidence=Confidence.HIGH,
            location=Location(
                file_path=Path("app/chat.py"),
                start_line=10,
                start_column=5,
                end_line=10,
                end_column=50,
                snippet='prompt = "You are helpful. " + user_input',
            ),
            category="prompt-injection",
            cwe_id="CWE-77",
            fix_suggestion="Sanitize user input before including in prompts.",
        ),
        Finding(
            rule_id="PS003",
            message="Hardcoded API key detected",
            severity=Severity.HIGH,
            confidence=Confidence.MEDIUM,
            location=Location(
                file_path=Path("config.py"),
                start_line=5,
                start_column=1,
                end_line=5,
                end_column=60,
                snippet='API_KEY = "sk-1234567890..."',
            ),
            category="secrets",
            cwe_id="CWE-798",
        ),
    ]

    return ScanResult(
        findings=findings,
        files_scanned=10,
        files_with_findings=2,
        scan_time_seconds=0.5,
        rules_applied=15,
    )


class TestJsonReporter:
    """Test JSON output reporter."""

    def test_format_output(self) -> None:
        """JSON output should be valid JSON."""
        config = Config()
        console = Console()
        reporter = JsonReporter(console, config)

        result = create_sample_result()
        output = reporter.format(result)

        # Should be valid JSON
        data = json.loads(output)
        assert "findings" in data
        assert "summary" in data
        assert len(data["findings"]) == 2

    def test_finding_structure(self) -> None:
        """Each finding should have required fields."""
        config = Config()
        console = Console()
        reporter = JsonReporter(console, config)

        result = create_sample_result()
        data = json.loads(reporter.format(result))

        finding = data["findings"][0]
        assert "rule_id" in finding
        assert "message" in finding
        assert "severity" in finding
        assert "location" in finding
        assert "file" in finding["location"]
        assert "start_line" in finding["location"]

    def test_summary_counts(self) -> None:
        """Summary should have correct counts."""
        config = Config()
        console = Console()
        reporter = JsonReporter(console, config)

        result = create_sample_result()
        data = json.loads(reporter.format(result))

        assert data["summary"]["critical"] == 1
        assert data["summary"]["high"] == 1


class TestSarifReporter:
    """Test SARIF output reporter."""

    def test_sarif_structure(self) -> None:
        """SARIF output should have correct structure."""
        config = Config()
        console = Console()
        reporter = SarifReporter(console, config)

        result = create_sample_result()
        output = reporter.format(result)

        data = json.loads(output)

        # SARIF structure validation
        assert data["$schema"].endswith("sarif-schema-2.1.0.json")
        assert data["version"] == "2.1.0"
        assert "runs" in data
        assert len(data["runs"]) == 1

        run = data["runs"][0]
        assert "tool" in run
        assert "results" in run

    def test_sarif_tool_info(self) -> None:
        """SARIF should include tool information."""
        config = Config()
        console = Console()
        reporter = SarifReporter(console, config)

        result = create_sample_result()
        data = json.loads(reporter.format(result))

        tool = data["runs"][0]["tool"]["driver"]
        assert tool["name"] == "Bastion"
        assert "version" in tool
        assert "rules" in tool

    def test_sarif_results(self) -> None:
        """SARIF results should map findings correctly."""
        config = Config()
        console = Console()
        reporter = SarifReporter(console, config)

        result = create_sample_result()
        data = json.loads(reporter.format(result))

        results = data["runs"][0]["results"]
        assert len(results) == 2

        first_result = results[0]
        assert "ruleId" in first_result
        assert "level" in first_result
        assert "message" in first_result
        assert "locations" in first_result

    def test_sarif_severity_mapping(self) -> None:
        """Severities should map to SARIF levels correctly."""
        config = Config()
        console = Console()
        reporter = SarifReporter(console, config)

        result = create_sample_result()
        data = json.loads(reporter.format(result))

        results = data["runs"][0]["results"]

        # Critical and High should map to "error"
        critical_result = next(r for r in results if r["ruleId"] == "PS001")
        assert critical_result["level"] == "error"


class TestTextReporter:
    """Test text output reporter."""

    def test_format_plain_text(self) -> None:
        """Format should produce plain text output."""
        config = Config()
        console = Console()
        reporter = TextReporter(console, config)

        result = create_sample_result()
        output = reporter.format(result)

        assert "PS001" in output
        assert "CRITICAL" in output
        # Check for path with either separator (Windows/Unix)
        assert "chat.py" in output


class TestGetReporter:
    """Test reporter factory function."""

    def test_get_text_reporter(self) -> None:
        """Get text reporter."""
        config = Config()
        console = Console()
        reporter = get_reporter("text", console, config)
        assert isinstance(reporter, TextReporter)

    def test_get_json_reporter(self) -> None:
        """Get JSON reporter."""
        config = Config()
        console = Console()
        reporter = get_reporter("json", console, config)
        assert isinstance(reporter, JsonReporter)

    def test_get_sarif_reporter(self) -> None:
        """Get SARIF reporter."""
        config = Config()
        console = Console()
        reporter = get_reporter("sarif", console, config)
        assert isinstance(reporter, SarifReporter)

    def test_unknown_format_defaults_to_text(self) -> None:
        """Unknown format should default to text."""
        config = Config()
        console = Console()
        reporter = get_reporter("unknown", console, config)
        assert isinstance(reporter, TextReporter)
