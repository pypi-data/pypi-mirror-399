"""Tests for the Bastion scanner."""

from pathlib import Path

import pytest

from bastion.config import Config
from bastion.models import Severity
from bastion.scanner import Scanner

pytestmark = pytest.mark.integration


class TestScanner:
    """Test the main Scanner class."""

    def test_scan_empty_directory(self, tmp_path: Path) -> None:
        """Scanning an empty directory should return no findings."""
        config = Config(paths=[tmp_path])
        scanner = Scanner(config)
        result = scanner.scan()

        assert result.files_scanned == 0
        assert result.has_findings is False

    def test_scan_safe_code(self, tmp_path: Path) -> None:
        """Safe code should not trigger findings."""
        safe_code = '''
def safe_function():
    """A safe function with no vulnerabilities."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ]
    return messages
'''
        test_file = tmp_path / "safe.py"
        test_file.write_text(safe_code)

        config = Config(paths=[tmp_path])
        scanner = Scanner(config)
        result = scanner.scan()

        assert result.files_scanned == 1
        assert result.has_findings is False

    def test_scan_concat_vulnerability(self, tmp_path: Path) -> None:
        """Detect string concatenation with user input."""
        vulnerable_code = '''
def vulnerable_function(user_input):
    prompt = "You are a helpful assistant. User says: " + user_input
    return prompt
'''
        test_file = tmp_path / "vulnerable.py"
        test_file.write_text(vulnerable_code)

        config = Config(paths=[tmp_path])
        scanner = Scanner(config)
        result = scanner.scan()

        assert result.files_scanned == 1
        assert result.has_findings is True
        assert any(f.rule_id == "PS001" for f in result.findings)

    def test_scan_fstring_vulnerability(self, tmp_path: Path) -> None:
        """Detect f-string prompts with user input."""
        vulnerable_code = '''
def vulnerable_fstring(user_message):
    prompt = f"You are an assistant. Respond to: {user_message}"
    return prompt
'''
        test_file = tmp_path / "fstring.py"
        test_file.write_text(vulnerable_code)

        config = Config(paths=[tmp_path])
        scanner = Scanner(config)
        result = scanner.scan()

        assert result.files_scanned == 1
        # PS002 should detect f-string with user input
        assert result.has_findings is True

    def test_scan_hardcoded_api_key(self, tmp_path: Path) -> None:
        """Detect hardcoded API keys."""
        vulnerable_code = '''
api_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890ab"
'''
        test_file = tmp_path / "secrets.py"
        test_file.write_text(vulnerable_code)

        config = Config(paths=[tmp_path])
        scanner = Scanner(config)
        result = scanner.scan()

        assert result.files_scanned == 1
        assert any(f.rule_id == "PS003" for f in result.findings)

    def test_suppression_comment(self, tmp_path: Path) -> None:
        """Test inline suppression comments."""
        code_with_suppression = '''
def suppressed_function(user_input):
    # bastion: ignore[PS001]
    prompt = "You are helpful. " + user_input
    return prompt
'''
        test_file = tmp_path / "suppressed.py"
        test_file.write_text(code_with_suppression)

        config = Config(paths=[tmp_path])
        scanner = Scanner(config)
        result = scanner.scan()

        # Should not find PS001 due to suppression
        assert not any(f.rule_id == "PS001" for f in result.findings)

    def test_severity_filtering(self, tmp_path: Path) -> None:
        """Test minimum severity filtering."""
        vulnerable_code = '''
api_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890ab"
'''
        test_file = tmp_path / "test.py"
        test_file.write_text(vulnerable_code)

        # Only show critical findings
        config = Config(paths=[tmp_path], min_severity=Severity.CRITICAL)
        scanner = Scanner(config)
        result = scanner.scan()

        # PS003 is HIGH, not CRITICAL, so should be filtered
        assert not any(f.rule_id == "PS003" for f in result.findings)

    def test_exclude_patterns(self, tmp_path: Path) -> None:
        """Test file exclusion patterns."""
        vulnerable_code = '''
def vulnerable(user_input):
    prompt = "Test: " + user_input
    return prompt
'''
        # Create files in different directories
        (tmp_path / "src").mkdir()
        (tmp_path / "vendor").mkdir()

        (tmp_path / "src" / "app.py").write_text(vulnerable_code)
        (tmp_path / "vendor" / "lib.py").write_text(vulnerable_code)

        config = Config(
            paths=[tmp_path],
            exclude_patterns=["**/vendor/**"],
        )
        scanner = Scanner(config)
        result = scanner.scan()

        # Should only scan src/app.py
        assert result.files_scanned == 1

    def test_disabled_rules(self, tmp_path: Path) -> None:
        """Test disabling specific rules."""
        vulnerable_code = '''
api_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890ab"
'''
        test_file = tmp_path / "test.py"
        test_file.write_text(vulnerable_code)

        config = Config(paths=[tmp_path], disabled_rules=["PS003"])
        scanner = Scanner(config)
        result = scanner.scan()

        # PS003 should be disabled
        assert not any(f.rule_id == "PS003" for f in result.findings)


class TestScanResult:
    """Test ScanResult methods."""

    def test_severity_counts(self, tmp_path: Path) -> None:
        """Test severity count properties."""
        from bastion.models import Confidence, Finding, Location, ScanResult

        findings = [
            Finding(
                rule_id="TEST1",
                message="Critical issue",
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
                rule_id="TEST2",
                message="High issue",
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
        ]

        result = ScanResult(
            findings=findings,
            files_scanned=1,
            files_with_findings=1,
            scan_time_seconds=0.1,
            rules_applied=15,
        )

        assert result.critical_count == 1
        assert result.high_count == 1
        assert result.medium_count == 0
        assert result.low_count == 0
        assert result.has_findings is True
