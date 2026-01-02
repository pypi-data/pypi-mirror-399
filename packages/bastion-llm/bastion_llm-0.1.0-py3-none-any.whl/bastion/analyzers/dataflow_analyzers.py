"""Analyzers for data flow vulnerabilities."""

from pathlib import Path
from typing import Any

from tree_sitter import Tree

from bastion.models import Confidence, Finding, Rule
from bastion.parsers import find_nodes_by_type, get_node_text

from .base import BaseAnalyzer


class MissingInputValidationAnalyzer(BaseAnalyzer):
    """Detects LLM calls without input validation (PS005)."""

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

        call_nodes = find_nodes_by_type(tree.root_node, "call")

        for node in call_nodes:
            node_text = get_node_text(node, source_bytes)

            is_llm = self._is_llm_call(node_text)
            has_user_input = self._has_direct_user_input(node, source_bytes)
            lacks_validation = not self._has_validation_nearby(node, source_bytes, source)

            if is_llm and has_user_input and lacks_validation:
                findings.append(self.create_finding(
                    rule, node, source, file_path,
                    confidence=Confidence.MEDIUM
                ))

        return findings

    def _is_llm_call(self, text: str) -> bool:
        """Check if text is an LLM call."""
        return any(pattern.lower() in text.lower() for pattern in self.LLM_CALL_PATTERNS)

    def _has_direct_user_input(self, node: Any, source_bytes: bytes) -> bool:
        """Check if node has direct user input."""
        node_text = get_node_text(node, source_bytes).lower()
        return any(pattern.lower() in node_text for pattern in self.USER_INPUT_PATTERNS)

    def _has_validation_nearby(self, node: Any, source_bytes: bytes, source: str) -> bool:
        """Check if validation exists nearby."""
        validation_patterns = ["validate", "sanitize", "clean", "strip", "escape", "filter"]
        lines = source.split("\n")
        start_line = max(0, node.start_point[0] - 10)
        end_line = node.start_point[0]
        context = "\n".join(lines[start_line:end_line]).lower()
        return any(p in context for p in validation_patterns)


class RequestDataFlowAnalyzer(BaseAnalyzer):
    """Detects request data flowing to LLM without sanitization (PS009)."""

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

        request_patterns = {"request.args", "request.form", "request.json",
                          "request.data", "request.query_params", "request.body"}

        call_nodes = find_nodes_by_type(tree.root_node, "call")

        for node in call_nodes:
            node_text = get_node_text(node, source_bytes)
            if self._is_llm_call(node_text):
                for pattern in request_patterns:
                    if pattern in node_text:
                        findings.append(self.create_finding(
                            rule, node, source, file_path,
                            confidence=Confidence.HIGH
                        ))
                        break

        return findings

    def _is_llm_call(self, text: str) -> bool:
        """Check if text is an LLM call."""
        return any(pattern.lower() in text.lower() for pattern in self.LLM_CALL_PATTERNS)


class DatabaseDataFlowAnalyzer(BaseAnalyzer):
    """Detects database data flowing to LLM context (PS010)."""

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

        db_patterns = {".query(", ".execute(", ".fetchone(", ".fetchall(",
                      ".filter(", ".all()", ".get(", "cursor."}

        assignments = find_nodes_by_type(tree.root_node, "assignment")
        db_vars: set[str] = set()

        for assign in assignments:
            assign_text = get_node_text(assign, source_bytes)
            if any(p in assign_text for p in db_patterns):
                for child in assign.children:
                    if child.type == "identifier":
                        db_vars.add(get_node_text(child, source_bytes))
                        break

        call_nodes = find_nodes_by_type(tree.root_node, "call")
        for node in call_nodes:
            node_text = get_node_text(node, source_bytes)
            if self._is_llm_call(node_text):
                for var in db_vars:
                    if var in node_text:
                        findings.append(self.create_finding(
                            rule, node, source, file_path,
                            confidence=Confidence.MEDIUM
                        ))
                        break

        return findings

    def _is_llm_call(self, text: str) -> bool:
        """Check if text is an LLM call."""
        return any(pattern.lower() in text.lower() for pattern in self.LLM_CALL_PATTERNS)
