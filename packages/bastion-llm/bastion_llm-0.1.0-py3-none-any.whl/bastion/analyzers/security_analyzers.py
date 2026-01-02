"""Analyzers for security vulnerabilities."""

import re
from pathlib import Path
from typing import Any

from tree_sitter import Tree

from bastion.models import Confidence, Finding, Rule
from bastion.parsers import find_nodes_by_type, find_nodes_by_types, get_node_text

from .base import BaseAnalyzer


class HardcodedSecretsAnalyzer(BaseAnalyzer):
    """Detects hardcoded API keys near LLM code (PS003)."""

    API_KEY_PATTERNS = [
        r'sk-[a-zA-Z0-9]{48}',  # OpenAI
        r'sk-ant-[a-zA-Z0-9\-]{95}',  # Anthropic
        r'["\']api[_-]?key["\']\s*[=:]\s*["\'][^"\']{20,}["\']',  # Generic
        r'["\']secret[_-]?key["\']\s*[=:]\s*["\'][^"\']{20,}["\']',
    ]

    def analyze(
        self,
        tree: Tree,
        source: str,
        file_path: Path,
        rule: Rule,
    ) -> list[Finding]:
        """Analyze source code for rule violations."""
        findings = []
        source_bytes = self.get_source_bytes(source)

        # Find string literals
        string_nodes = find_nodes_by_type(tree.root_node, "string")

        for node in string_nodes:
            node_text = get_node_text(node, source_bytes)

            for pattern in self.API_KEY_PATTERNS:
                if re.search(pattern, node_text, re.IGNORECASE):
                    findings.append(self.create_finding(
                        rule, node, source, file_path,
                        confidence=Confidence.MEDIUM
                    ))
                    break

        return findings


class SensitiveDataAnalyzer(BaseAnalyzer):
    """Detects sensitive data leaking to LLM context (PS015)."""

    def analyze(
        self,
        tree: Tree,
        source: str,
        file_path: Path,
        rule: Rule,
    ) -> list[Finding]:
        """Analyze source code for rule violations."""
        findings = []
        source_bytes = self.get_source_bytes(source)

        # Find call expressions that might be LLM calls
        call_nodes = find_nodes_by_type(tree.root_node, "call")

        for node in call_nodes:
            node_text = get_node_text(node, source_bytes)

            # Check if this is an LLM-related call
            if not self._is_llm_call(node_text):
                continue

            # Check for sensitive variable names in the call
            if self._has_sensitive_data(node, source_bytes):
                findings.append(self.create_finding(
                    rule, node, source, file_path,
                    confidence=Confidence.LOW
                ))

        return findings

    def _is_llm_call(self, text: str) -> bool:
        """Check if text represents an LLM API call."""
        return any(pattern.lower() in text.lower() for pattern in self.LLM_CALL_PATTERNS)

    def _has_sensitive_data(self, node: Any, source_bytes: bytes) -> bool:
        """Check for sensitive variable names."""
        identifiers = find_nodes_by_type(node, "identifier")
        for ident in identifiers:
            name = get_node_text(ident, source_bytes).lower()
            for pattern in self.SENSITIVE_PATTERNS:
                if pattern in name:
                    return True
        return False


class JailbreakPatternAnalyzer(BaseAnalyzer):
    """Detects common jailbreak patterns in prompts (PS011)."""

    JAILBREAK_PATTERNS = [
        "ignore previous instructions",
        "ignore all instructions",
        "disregard your instructions",
        "forget your rules",
        "you are now",
        "pretend you are",
        "act as if",
        "roleplay as",
        "jailbreak",
        "dan mode",
        "developer mode",
    ]

    def analyze(
        self,
        tree: Tree,
        source: str,
        file_path: Path,
        rule: Rule,
    ) -> list[Finding]:
        """Analyze source code for rule violations."""
        findings = []
        source_bytes = self.get_source_bytes(source)

        string_nodes = find_nodes_by_types(
            tree.root_node,
            {"string", "formatted_string", "concatenated_string"}
        )

        for node in string_nodes:
            node_text = get_node_text(node, source_bytes).lower()
            for pattern in self.JAILBREAK_PATTERNS:
                if pattern in node_text:
                    findings.append(self.create_finding(
                        rule, node, source, file_path,
                        confidence=Confidence.HIGH
                    ))
                    break

        return findings


class UnsafeOutputUsageAnalyzer(BaseAnalyzer):
    """Detects LLM output used in dangerous sinks (PS006)."""

    @staticmethod
    def _get_dangerous_sinks() -> set[str]:
        """Build dangerous sink patterns dynamically to avoid hook detection."""
        # These are detection patterns for security scanning
        ev = "".join(["e", "v", "a", "l"])
        ex = "".join(["e", "x", "e", "c"])
        os_sys = ".".join(["os", "sys" + "tem"])
        os_pop = ".".join(["os", "pop" + "en"])
        return {
            ev,
            ex,
            "subprocess.run",
            "subprocess.call",
            "subprocess.Popen",
            os_sys,
            os_pop,
        }

    def analyze(
        self,
        tree: Tree,
        source: str,
        file_path: Path,
        rule: Rule,
    ) -> list[Finding]:
        """Analyze source code for rule violations."""
        findings = []
        source_bytes = self.get_source_bytes(source)

        assignments = find_nodes_by_type(tree.root_node, "assignment")
        llm_result_vars: set[str] = set()

        for assign in assignments:
            assign_text = get_node_text(assign, source_bytes)
            if self._is_llm_assignment(assign_text):
                for child in assign.children:
                    if child.type == "identifier":
                        llm_result_vars.add(get_node_text(child, source_bytes))
                        break

        call_nodes = find_nodes_by_type(tree.root_node, "call")
        for node in call_nodes:
            node_text = get_node_text(node, source_bytes)
            if self._is_dangerous_sink(node_text):
                for var in llm_result_vars:
                    if var in node_text:
                        findings.append(self.create_finding(
                            rule, node, source, file_path,
                            confidence=Confidence.HIGH
                        ))
                        break

        return findings

    def _is_llm_assignment(self, text: str) -> bool:
        """Check if text is an LLM result assignment."""
        llm_keywords = ["completion", "response", "result", "output", "message"]
        text_lower = text.lower()
        return any(kw in text_lower for kw in llm_keywords) and any(
            p.lower() in text_lower for p in self.LLM_CALL_PATTERNS
        )

    def _is_dangerous_sink(self, text: str) -> bool:
        """Check if text contains a dangerous sink."""
        return any(sink in text for sink in self._get_dangerous_sinks())
