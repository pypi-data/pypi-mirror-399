"""Shared pytest fixtures for Bastion tests."""

from pathlib import Path

import pytest
from rich.console import Console

from bastion.config import Config
from bastion.models import Confidence, Finding, Location, ScanResult, Severity
from bastion.rules import RuleRegistry


@pytest.fixture
def console() -> Console:
    """Create a Rich Console for testing."""
    return Console(force_terminal=False, no_color=True)


@pytest.fixture
def default_config() -> Config:
    """Create a default Config instance."""
    return Config()


@pytest.fixture
def sample_location() -> Location:
    """Create a sample Location for testing."""
    return Location(
        file_path=Path("app/chat.py"),
        start_line=10,
        start_column=5,
        end_line=10,
        end_column=50,
        snippet='prompt = "You are helpful. " + user_input',
    )


@pytest.fixture
def sample_finding(sample_location: Location) -> Finding:
    """Create a sample Finding for testing."""
    return Finding(
        rule_id="PS001",
        message="User input directly concatenated into prompt string",
        severity=Severity.CRITICAL,
        confidence=Confidence.HIGH,
        location=sample_location,
        category="prompt-injection",
        cwe_id="CWE-77",
        fix_suggestion="Sanitize user input before including in prompts.",
    )


@pytest.fixture
def sample_findings() -> list[Finding]:
    """Create a list of sample findings for testing."""
    return [
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


@pytest.fixture
def sample_scan_result(sample_findings: list[Finding]) -> ScanResult:
    """Create a sample ScanResult for testing."""
    return ScanResult(
        findings=sample_findings,
        files_scanned=10,
        files_with_findings=2,
        scan_time_seconds=0.5,
        rules_applied=15,
    )


@pytest.fixture
def empty_scan_result() -> ScanResult:
    """Create an empty ScanResult for testing."""
    return ScanResult(
        findings=[],
        files_scanned=5,
        files_with_findings=0,
        scan_time_seconds=0.1,
        rules_applied=15,
    )


@pytest.fixture
def rule_registry() -> RuleRegistry:
    """Create a RuleRegistry with built-in rules loaded."""
    registry = RuleRegistry()
    registry.load_builtin_rules()
    return registry


@pytest.fixture
def vulnerable_python_code() -> str:
    """Sample Python code with prompt injection vulnerability."""
    return '''
def vulnerable_function(user_input):
    prompt = "You are a helpful assistant. User says: " + user_input
    return prompt
'''


@pytest.fixture
def safe_python_code() -> str:
    """Sample safe Python code without vulnerabilities."""
    return '''
def safe_function():
    """A safe function with no vulnerabilities."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ]
    return messages
'''


@pytest.fixture
def vulnerable_file(tmp_path: Path, vulnerable_python_code: str) -> Path:
    """Create a temporary file with vulnerable code."""
    file_path = tmp_path / "vulnerable.py"
    file_path.write_text(vulnerable_python_code)
    return file_path


@pytest.fixture
def safe_file(tmp_path: Path, safe_python_code: str) -> Path:
    """Create a temporary file with safe code."""
    file_path = tmp_path / "safe.py"
    file_path.write_text(safe_python_code)
    return file_path
