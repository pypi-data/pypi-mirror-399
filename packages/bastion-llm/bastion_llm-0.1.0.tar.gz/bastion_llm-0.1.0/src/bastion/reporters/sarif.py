"""SARIF 2.1.0 reporter for GitHub Security integration."""

import json
from datetime import UTC, datetime
from typing import Any

from rich.console import Console

from bastion.config import Config
from bastion.models import Finding, ScanResult, Severity


class SarifReporter:
    """SARIF 2.1.0 output reporter for GitHub Security integration."""

    SARIF_VERSION = "2.1.0"
    SCHEMA_URI = "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"

    SEVERITY_TO_SARIF = {
        Severity.CRITICAL: "error",
        Severity.HIGH: "error",
        Severity.MEDIUM: "warning",
        Severity.LOW: "note",
        Severity.INFO: "note",
    }

    SEVERITY_TO_LEVEL = {
        Severity.CRITICAL: "error",
        Severity.HIGH: "error",
        Severity.MEDIUM: "warning",
        Severity.LOW: "note",
        Severity.INFO: "none",
    }

    def __init__(self, console: Console, config: Config) -> None:
        """Initialize the SARIF reporter."""
        self.console = console
        self.config = config

    def report(self, result: ScanResult) -> None:
        """Display SARIF output."""
        self.console.print(self.format(result))

    def format(self, result: ScanResult) -> str:
        """Format as SARIF 2.1.0."""
        from bastion import __version__

        sarif = {
            "$schema": self.SCHEMA_URI,
            "version": self.SARIF_VERSION,
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "Bastion",
                            "version": __version__,
                            "informationUri": "https://github.com/en-yao/bastion",
                            "rules": self._build_rules_array(),
                        }
                    },
                    "results": [self._format_result(f) for f in result.findings],
                    "invocations": [
                        {
                            "executionSuccessful": True,
                            "endTimeUtc": datetime.now(UTC).isoformat(),
                        }
                    ],
                }
            ],
        }

        return json.dumps(sarif, indent=2)

    def _build_rules_array(self) -> list[dict[str, Any]]:
        """Build the SARIF rules array from builtin rules."""
        from bastion.rules import BUILTIN_RULES

        rules: list[dict[str, Any]] = []
        for rule_data in BUILTIN_RULES:
            rule_sarif = self._format_rule(rule_data)
            rules.append(rule_sarif)
        return rules

    def _format_rule(self, rule_data: dict[str, Any]) -> dict[str, Any]:
        """Format a single rule for SARIF output."""
        rule_sarif: dict[str, Any] = {
            "id": rule_data["id"],
            "name": rule_data["id"],
            "shortDescription": {"text": rule_data["message"]},
            "fullDescription": {"text": rule_data.get("description", rule_data["message"])},
            "defaultConfiguration": {
                "level": self.SEVERITY_TO_LEVEL.get(
                    Severity(rule_data.get("severity", "medium")),
                    "warning"
                )
            },
            "properties": {
                "category": rule_data.get("category", "security"),
            }
        }
        if rule_data.get("cwe_id"):
            rule_sarif["properties"]["cwe"] = rule_data["cwe_id"]
        return rule_sarif

    def _format_result(self, finding: Finding) -> dict[str, Any]:
        """Format a single finding as a SARIF result."""
        sarif_result: dict[str, Any] = {
            "ruleId": finding.rule_id,
            "level": self.SEVERITY_TO_SARIF.get(finding.severity, "warning"),
            "message": {"text": finding.message},
            "locations": [self._format_location(finding)],
        }
        if finding.fix_suggestion:
            sarif_result["fixes"] = [
                {"description": {"text": finding.fix_suggestion}}
            ]
        return sarif_result

    def _format_location(self, finding: Finding) -> dict[str, Any]:
        """Format the location for a SARIF result."""
        return {
            "physicalLocation": {
                "artifactLocation": {
                    "uri": str(finding.location.file_path).replace("\\", "/"),
                    "uriBaseId": "%SRCROOT%",
                },
                "region": {
                    "startLine": finding.location.start_line,
                    "startColumn": finding.location.start_column,
                    "endLine": finding.location.end_line,
                    "endColumn": finding.location.end_column,
                    "snippet": {"text": finding.location.snippet},
                },
            }
        }
