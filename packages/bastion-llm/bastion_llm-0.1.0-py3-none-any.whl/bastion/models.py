"""Core data models for Bastion."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class Severity(Enum):
    """Severity levels for security findings."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

    def _order(self) -> int:
        """Get numeric order for comparison."""
        order = {
            Severity.INFO: 0,
            Severity.LOW: 1,
            Severity.MEDIUM: 2,
            Severity.HIGH: 3,
            Severity.CRITICAL: 4,
        }
        return order[self]

    def __lt__(self, other: "Severity") -> bool:
        return self._order() < other._order()

    def __le__(self, other: "Severity") -> bool:
        return self._order() <= other._order()

    def __gt__(self, other: "Severity") -> bool:
        return self._order() > other._order()

    def __ge__(self, other: "Severity") -> bool:
        return self._order() >= other._order()


class Confidence(Enum):
    """Confidence levels for findings."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ScanError(Exception):
    """Exception raised during file scanning."""

    def __init__(self, file_path: Path, message: str, cause: Exception | None = None) -> None:
        self.file_path = file_path
        self.message = message
        self.cause = cause
        super().__init__(f"{file_path}: {message}")


@dataclass
class FileError:
    """Record of an error encountered while scanning a file."""

    file_path: Path
    error_type: str
    message: str

    def __str__(self) -> str:
        return f"{self.file_path}: [{self.error_type}] {self.message}"


@dataclass
class Location:
    """Source code location of a finding."""

    file_path: Path
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    snippet: str = ""

    def __str__(self) -> str:
        return f"{self.file_path}:{self.start_line}:{self.start_column}"


@dataclass
class Finding:
    """A security finding detected by Bastion."""

    rule_id: str
    message: str
    severity: Severity
    confidence: Confidence
    location: Location
    category: str = "prompt-injection"
    cwe_id: str | None = None
    fix_suggestion: str | None = None
    references: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        return f"[{self.rule_id}] {self.severity.value.upper()}: {self.message} at {self.location}"


@dataclass
class Rule:
    """A security rule definition."""

    id: str
    message: str
    severity: Severity
    category: str
    description: str
    pattern: str | None = None
    pattern_type: str = "ast"  # ast, regex, semantic
    languages: list[str] = field(default_factory=lambda: ["python"])
    cwe_id: str | None = None
    fix_suggestion: str | None = None
    references: list[str] = field(default_factory=list)
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Rule":
        """Create a Rule from a dictionary."""
        severity = Severity(data.get("severity", "medium"))
        return cls(
            id=data["id"],
            message=data["message"],
            severity=severity,
            category=data.get("category", "prompt-injection"),
            description=data.get("description", ""),
            pattern=data.get("pattern"),
            pattern_type=data.get("pattern_type", "ast"),
            languages=data.get("languages", ["python"]),
            cwe_id=data.get("cwe_id"),
            fix_suggestion=data.get("fix_suggestion"),
            references=data.get("references", []),
            enabled=data.get("enabled", True),
        )


@dataclass
class ScanResult:
    """Result of a scan operation."""

    findings: list[Finding]
    files_scanned: int
    files_with_findings: int
    scan_time_seconds: float
    rules_applied: int
    errors: list[FileError] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        """Check if any errors occurred during scanning."""
        return len(self.errors) > 0

    @property
    def has_findings(self) -> bool:
        """Check if any findings were detected."""
        return len(self.findings) > 0

    @property
    def critical_count(self) -> int:
        """Count of critical severity findings."""
        return sum(1 for f in self.findings if f.severity == Severity.CRITICAL)

    @property
    def high_count(self) -> int:
        """Count of high severity findings."""
        return sum(1 for f in self.findings if f.severity == Severity.HIGH)

    @property
    def medium_count(self) -> int:
        """Count of medium severity findings."""
        return sum(1 for f in self.findings if f.severity == Severity.MEDIUM)

    @property
    def low_count(self) -> int:
        """Count of low severity findings."""
        return sum(1 for f in self.findings if f.severity == Severity.LOW)
