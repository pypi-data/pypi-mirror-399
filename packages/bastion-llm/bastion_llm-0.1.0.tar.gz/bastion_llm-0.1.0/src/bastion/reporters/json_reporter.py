"""JSON reporter for structured output."""

import json
from typing import Any

from rich.console import Console

from bastion.config import Config
from bastion.models import Finding, ScanResult


class JsonReporter:
    """JSON output reporter."""

    def __init__(self, console: Console, config: Config) -> None:
        """Initialize the JSON reporter."""
        self.console = console
        self.config = config

    def report(self, result: ScanResult) -> None:
        """Display JSON output."""
        self.console.print(self.format(result))

    def format(self, result: ScanResult) -> str:
        """Format as JSON."""
        data = self._build_json_data(result)
        return json.dumps(data, indent=2)

    def _build_json_data(self, result: ScanResult) -> dict[str, Any]:
        """Build the JSON data structure."""
        return {
            "version": "1.0.0",
            "scan_time": result.scan_time_seconds,
            "files_scanned": result.files_scanned,
            "files_with_findings": result.files_with_findings,
            "rules_applied": result.rules_applied,
            "findings": [self._format_finding(f) for f in result.findings],
            "summary": {
                "critical": result.critical_count,
                "high": result.high_count,
                "medium": result.medium_count,
                "low": result.low_count,
            },
        }

    def _format_finding(self, finding: Finding) -> dict[str, Any]:
        """Format a single finding as JSON."""
        return {
            "rule_id": finding.rule_id,
            "message": finding.message,
            "severity": finding.severity.value,
            "confidence": finding.confidence.value,
            "category": finding.category,
            "cwe_id": finding.cwe_id,
            "location": {
                "file": str(finding.location.file_path),
                "start_line": finding.location.start_line,
                "start_column": finding.location.start_column,
                "end_line": finding.location.end_line,
                "end_column": finding.location.end_column,
                "snippet": finding.location.snippet,
            },
            "fix_suggestion": finding.fix_suggestion,
            "references": finding.references,
        }
