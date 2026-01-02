"""Core scanning engine for Bastion."""

import contextlib
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pathspec

from bastion.analyzers import AnalyzerRegistry
from bastion.config import Config
from bastion.models import FileError, Finding, Rule, ScanResult, Severity
from bastion.parsers import ParserRegistry
from bastion.rules import RuleRegistry
from bastion.taint import TaintAnalyzer


class Scanner:
    """Main scanner that orchestrates the security analysis."""

    def __init__(self, config: Config, enable_taint_analysis: bool = False) -> None:
        self.config = config
        self.rule_registry = RuleRegistry()
        self.parser_registry = ParserRegistry()
        self.analyzer_registry = AnalyzerRegistry()
        self.enable_taint_analysis = enable_taint_analysis
        self.taint_analyzer = TaintAnalyzer() if enable_taint_analysis else None

        # Load rules
        self.rule_registry.load_builtin_rules()
        for rules_path in config.rules_paths:
            self.rule_registry.load_rules_from_path(rules_path)

        # Apply rule filters
        if config.enabled_rules:
            for rule_id in list(self.rule_registry.rules.keys()):
                if rule_id not in config.enabled_rules:
                    self.rule_registry.rules[rule_id].enabled = False

        for rule_id in config.disabled_rules:
            if rule_id in self.rule_registry.rules:
                self.rule_registry.rules[rule_id].enabled = False

    def scan(self) -> ScanResult:
        """Scan all configured paths and return results."""
        findings: list[Finding] = []
        errors: list[FileError] = []
        files_scanned = 0
        files_with_findings: set[Path] = set()

        for file_path in self._discover_files():
            file_findings, file_error = self._scan_file(file_path)
            if file_error:
                errors.append(file_error)
            if file_findings:
                findings.extend(file_findings)
                files_with_findings.add(file_path)
            files_scanned += 1

        # Filter by severity
        findings = [
            f for f in findings
            if f.severity >= self.config.min_severity
        ]

        # Sort by severity (highest first), then by file
        findings.sort(
            key=lambda f: (f.severity, str(f.location.file_path), f.location.start_line),
            reverse=True,
        )

        enabled_rules = sum(1 for r in self.rule_registry.rules.values() if r.enabled)

        return ScanResult(
            findings=findings,
            files_scanned=files_scanned,
            files_with_findings=len(files_with_findings),
            scan_time_seconds=0.0,  # Set by caller
            rules_applied=enabled_rules,
            errors=errors,
        )

    def _discover_files(self) -> Iterator[Path]:
        """Discover files to scan based on configuration."""
        include_spec = pathspec.PathSpec.from_lines("gitwildmatch", self.config.include_patterns)
        exclude_spec = pathspec.PathSpec.from_lines("gitwildmatch", self.config.exclude_patterns)

        for base_path in self.config.paths:
            base_path = Path(base_path).resolve()

            if base_path.is_file():
                if self._should_scan_file(base_path, include_spec, exclude_spec):
                    yield base_path
            elif base_path.is_dir():
                for file_path in base_path.rglob("*"):
                    should_scan = self._should_scan_file(file_path, include_spec, exclude_spec)
                    if file_path.is_file() and should_scan:
                        yield file_path

    def _should_scan_file(
        self,
        file_path: Path,
        include_spec: pathspec.PathSpec,
        exclude_spec: pathspec.PathSpec,
    ) -> bool:
        """Check if a file should be scanned."""
        rel_path = str(file_path)
        with contextlib.suppress(ValueError):
            rel_path = str(file_path.relative_to(Path.cwd()))

        # Check exclusions first
        if exclude_spec.match_file(rel_path):
            return False

        # Then check inclusions
        return include_spec.match_file(rel_path)

    def _scan_file(self, file_path: Path) -> tuple[list[Finding], FileError | None]:
        """Scan a single file for vulnerabilities.

        Returns:
            A tuple of (findings list, error or None).
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            error = FileError(file_path, "UnicodeDecodeError", str(e))
            return [], error
        except PermissionError as e:
            error = FileError(file_path, "PermissionError", str(e))
            return [], error

        parser = self.parser_registry.get_parser_for_file(file_path)
        if not parser:
            return [], None

        try:
            tree = parser.parse(content)
        except (ValueError, RuntimeError) as e:
            error = FileError(file_path, "ParseError", str(e))
            return [], error

        language = self._get_language(file_path)
        suppressions = self._parse_suppressions(content)

        findings = self._run_analyzers(tree, content, file_path, language)
        findings.extend(self._run_taint_analysis(tree, content, file_path, language))

        return self._filter_suppressed(findings, suppressions), None

    def _run_analyzers(
        self,
        tree: Any,
        content: str,
        file_path: Path,
        language: str,
    ) -> list[Finding]:
        """Run all applicable analyzers on the parsed file."""
        findings: list[Finding] = []

        for rule in self.rule_registry.get_enabled_rules():
            if language not in rule.languages:
                continue

            analyzer = self.analyzer_registry.get_analyzer(rule)
            if analyzer:
                findings.extend(analyzer.analyze(tree, content, file_path, rule))

        return findings

    def _run_taint_analysis(
        self,
        tree: Any,
        content: str,
        file_path: Path,
        language: str,
    ) -> list[Finding]:
        """Run taint analysis if enabled and applicable."""
        if not self.taint_analyzer or language != "python":
            return []

        taint_rule = Rule(
            id="PS016",
            message="Tainted data flow detected from user input to LLM call",
            severity=Severity.CRITICAL,
            category="taint-analysis",
            description="Data from user input flows to LLM API without sanitization",
            cwe_id="CWE-77",
            fix_suggestion="Sanitize user input before including in LLM prompts",
        )
        return self.taint_analyzer.analyze(tree, content, file_path, taint_rule)

    def _filter_suppressed(
        self,
        findings: list[Finding],
        suppressions: dict[int, set[str]],
    ) -> list[Finding]:
        """Filter out suppressed findings."""
        if self.config.ignore_nosec:
            return findings

        return [f for f in findings if not self._is_suppressed(f, suppressions)]

    def _get_language(self, file_path: Path) -> str:
        """Get the language for a file based on extension."""
        ext = file_path.suffix.lower()
        return {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
        }.get(ext, "unknown")

    def _parse_suppressions(self, content: str) -> dict[int, set[str]]:
        """Parse inline suppressions from content."""
        suppressions: dict[int, set[str]] = {}

        # Match: # bastion: ignore[rule-id, rule-id]
        pattern = r"#\s*bastion:\s*ignore(?:\[([^\]]+)\])?"

        for i, line in enumerate(content.split("\n"), start=1):
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                # Specific rules if specified, otherwise all rules
                rules = (
                    {r.strip() for r in match.group(1).split(",")}
                    if match.group(1)
                    else {"*"}
                )
                suppressions[i] = rules

        return suppressions

    def _is_suppressed(self, finding: Finding, suppressions: dict[int, set[str]]) -> bool:
        """Check if a finding is suppressed."""
        line = finding.location.start_line

        # Check current line and previous line
        for check_line in [line, line - 1]:
            if check_line in suppressions:
                rules = suppressions[check_line]
                if "*" in rules or finding.rule_id in rules:
                    return True

        return False
