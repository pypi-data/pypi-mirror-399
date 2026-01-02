"""Tests for data models."""

from pathlib import Path

import pytest

from bastion.models import Confidence, Finding, Location, Rule, ScanResult, Severity

pytestmark = pytest.mark.unit


class TestSeverity:
    """Test Severity enum."""

    def test_severity_ordering(self) -> None:
        """Severities should be ordered correctly."""
        assert Severity.CRITICAL > Severity.HIGH
        assert Severity.HIGH > Severity.MEDIUM
        assert Severity.MEDIUM > Severity.LOW
        assert Severity.LOW > Severity.INFO

    def test_severity_values(self) -> None:
        """Severity values should match expected strings."""
        assert Severity.CRITICAL.value == "critical"
        assert Severity.HIGH.value == "high"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.LOW.value == "low"
        assert Severity.INFO.value == "info"


class TestConfidence:
    """Test Confidence enum."""

    def test_confidence_values(self) -> None:
        """Confidence values should match expected strings."""
        assert Confidence.HIGH.value == "high"
        assert Confidence.MEDIUM.value == "medium"
        assert Confidence.LOW.value == "low"


class TestLocation:
    """Test Location dataclass."""

    def test_location_str(self) -> None:
        """Location should format as string correctly."""
        loc = Location(
            file_path=Path("test.py"),
            start_line=10,
            start_column=5,
            end_line=10,
            end_column=20,
        )

        loc_str = str(loc)

        assert "test.py" in loc_str
        assert "10" in loc_str

    def test_location_with_snippet(self) -> None:
        """Location should store snippet."""
        loc = Location(
            file_path=Path("test.py"),
            start_line=1,
            start_column=1,
            end_line=1,
            end_column=10,
            snippet="test code",
        )

        assert loc.snippet == "test code"


class TestFinding:
    """Test Finding dataclass."""

    def test_finding_str(self) -> None:
        """Finding should format as string correctly."""
        finding = Finding(
            rule_id="PS001",
            message="Test message",
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

        finding_str = str(finding)

        assert "PS001" in finding_str
        assert "HIGH" in finding_str

    def test_finding_optional_fields(self) -> None:
        """Finding should handle optional fields."""
        finding = Finding(
            rule_id="PS001",
            message="Test",
            severity=Severity.MEDIUM,
            confidence=Confidence.LOW,
            location=Location(
                file_path=Path("test.py"),
                start_line=1,
                start_column=1,
                end_line=1,
                end_column=10,
            ),
            category="test",
            cwe_id="CWE-77",
            fix_suggestion="Fix it",
            references=["http://example.com"],
        )

        assert finding.category == "test"
        assert finding.cwe_id == "CWE-77"
        assert finding.fix_suggestion == "Fix it"
        assert "http://example.com" in finding.references


class TestScanResult:
    """Test ScanResult dataclass."""

    def test_has_findings(self) -> None:
        """has_findings should return True when findings exist."""
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

        assert result.has_findings is True

    def test_no_findings(self) -> None:
        """has_findings should return False when no findings."""
        result = ScanResult(
            findings=[],
            files_scanned=5,
            files_with_findings=0,
            scan_time_seconds=0.5,
            rules_applied=10,
        )

        assert result.has_findings is False

    def test_severity_counts(self) -> None:
        """Should count findings by severity correctly."""
        findings = [
            Finding(
                rule_id="P1",
                message="Critical",
                severity=Severity.CRITICAL,
                confidence=Confidence.HIGH,
                location=Location(
                    file_path=Path("test.py"),
                    start_line=1,
                    start_column=1,
                    end_line=1,
                    end_column=10,
                ),
            ),
            Finding(
                rule_id="P2",
                message="High",
                severity=Severity.HIGH,
                confidence=Confidence.HIGH,
                location=Location(
                    file_path=Path("test.py"),
                    start_line=2,
                    start_column=1,
                    end_line=2,
                    end_column=10,
                ),
            ),
            Finding(
                rule_id="P3",
                message="Medium",
                severity=Severity.MEDIUM,
                confidence=Confidence.HIGH,
                location=Location(
                    file_path=Path("test.py"),
                    start_line=3,
                    start_column=1,
                    end_line=3,
                    end_column=10,
                ),
            ),
        ]

        result = ScanResult(
            findings=findings,
            files_scanned=1,
            files_with_findings=1,
            scan_time_seconds=0.5,
            rules_applied=10,
        )

        assert result.critical_count == 1
        assert result.high_count == 1
        assert result.medium_count == 1
        assert result.low_count == 0


class TestRule:
    """Test Rule dataclass."""

    def test_rule_from_dict_minimal(self) -> None:
        """Should create rule from minimal dict."""
        data = {
            "id": "TEST001",
            "message": "Test message",
        }

        rule = Rule.from_dict(data)

        assert rule.id == "TEST001"
        assert rule.message == "Test message"
        assert rule.severity == Severity.MEDIUM
        assert rule.enabled is True

    def test_rule_from_dict_full(self) -> None:
        """Should create rule from complete dict."""
        data = {
            "id": "TEST002",
            "message": "Full test",
            "severity": "critical",
            "category": "security",
            "description": "Description",
            "pattern_type": "ast",
            "languages": ["python", "javascript"],
            "cwe_id": "CWE-77",
            "fix_suggestion": "Fix it",
            "references": ["http://example.com"],
            "enabled": False,
        }

        rule = Rule.from_dict(data)

        assert rule.id == "TEST002"
        assert rule.severity == Severity.CRITICAL
        assert rule.category == "security"
        assert "python" in rule.languages
        assert rule.enabled is False
