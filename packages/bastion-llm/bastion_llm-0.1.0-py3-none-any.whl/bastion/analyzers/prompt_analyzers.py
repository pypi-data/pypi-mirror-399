"""Analyzers for prompt injection vulnerabilities."""

import re
from pathlib import Path
from typing import Any

from tree_sitter import Tree

from bastion.models import Confidence, Finding, Rule
from bastion.parsers import find_nodes_by_type, find_nodes_by_types, get_node_text

from .base import BaseAnalyzer


class StringConcatAnalyzer(BaseAnalyzer):
    """Detects user input concatenated into prompt strings (PS001)."""

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

        # Find binary expressions (concatenation with +)
        concat_nodes = find_nodes_by_type(tree.root_node, "binary_operator")

        for node in concat_nodes:
            # Check if this is string concatenation
            if not self._is_string_concat(node, source_bytes):
                continue

            # Check if it involves user input and prompt keywords
            node_text = get_node_text(node, source_bytes)
            if self._involves_user_input(node_text) and self._is_prompt_context(node, source_bytes):
                findings.append(self.create_finding(rule, node, source, file_path))

        return findings

    def _is_string_concat(self, node: Any, source_bytes: bytes) -> bool:
        """Check if node is string concatenation."""
        return any(child.type == "+" for child in node.children)

    def _involves_user_input(self, text: str) -> bool:
        """Check if the text involves user input variables."""
        text_lower = text.lower()
        return any(pattern.lower() in text_lower for pattern in self.USER_INPUT_PATTERNS)

    def _is_prompt_context(self, node: Any, source_bytes: bytes) -> bool:
        """Check if the node is in a prompt-related context."""
        prompt_keywords = {"prompt", "message", "system", "instruction", "content"}

        # Check parent assignment
        parent = node.parent
        while parent:
            if parent.type == "assignment":
                for child in parent.children:
                    if child.type == "identifier":
                        name = get_node_text(child, source_bytes).lower()
                        if any(kw in name for kw in prompt_keywords):
                            return True
            parent = parent.parent

        return False


class FStringAnalyzer(BaseAnalyzer):
    """Detects user input in f-string prompts (PS002)."""

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

        # Find formatted strings (f-strings in Python)
        fstring_nodes = find_nodes_by_types(
            tree.root_node,
            {"formatted_string", "string", "template_string"}
        )

        for node in fstring_nodes:
            node_text = get_node_text(node, source_bytes)

            # Check if it's an f-string with interpolation
            if not (node_text.startswith('f"') or node_text.startswith("f'")):
                continue

            # Check for user input variables in the f-string
            if (self._has_user_input_interpolation(node, source_bytes) and
                    self._is_prompt_related(node, source_bytes)):
                findings.append(self.create_finding(rule, node, source, file_path))

        return findings

    def _has_user_input_interpolation(self, node: Any, source_bytes: bytes) -> bool:
        """Check if f-string has user input interpolation."""
        interpolation_nodes = find_nodes_by_type(node, "interpolation")
        for interp in interpolation_nodes:
            text = get_node_text(interp, source_bytes).lower()
            for pattern in self.USER_INPUT_PATTERNS:
                if pattern.lower() in text:
                    return True
        return False

    def _is_prompt_related(self, node: Any, source_bytes: bytes) -> bool:
        """Check if the f-string is prompt-related."""
        node_text = get_node_text(node, source_bytes).lower()
        prompt_keywords = ["you are", "system:", "assistant:", "user:", "prompt", "instruction"]
        return any(kw in node_text for kw in prompt_keywords)


class FormatStringAnalyzer(BaseAnalyzer):
    """Detects unsafe .format() calls on prompt strings (PS008)."""

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

        # Find call expressions
        call_nodes = find_nodes_by_type(tree.root_node, "call")

        for node in call_nodes:
            if (self._is_format_call(node, source_bytes) and
                    self._is_prompt_context_format(node, source_bytes)):
                findings.append(self.create_finding(
                    rule, node, source, file_path,
                    confidence=Confidence.MEDIUM
                ))

        return findings

    def _is_format_call(self, node: Any, source_bytes: bytes) -> bool:
        """Check if this is a .format() call."""
        node_text = get_node_text(node, source_bytes)
        return ".format(" in node_text

    def _is_prompt_context_format(self, node: Any, source_bytes: bytes) -> bool:
        """Check if format call is in prompt context."""
        node_text = get_node_text(node, source_bytes).lower()
        prompt_keywords = ["prompt", "message", "system", "you are", "instruction"]
        return any(kw in node_text for kw in prompt_keywords)


class SystemPromptInjectionAnalyzer(BaseAnalyzer):
    """Detects user input in system prompts (PS004)."""

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

        # Find dictionary literals and function calls that might set system prompts
        dict_nodes = find_nodes_by_type(tree.root_node, "dictionary")
        call_nodes = find_nodes_by_type(tree.root_node, "call")

        for node in dict_nodes:
            if (self._is_system_message_dict(node, source_bytes) and
                    self._has_user_input(node, source_bytes)):
                findings.append(self.create_finding(rule, node, source, file_path))

        for node in call_nodes:
            if (self._is_system_message_call(node, source_bytes) and
                    self._has_user_input(node, source_bytes)):
                findings.append(self.create_finding(rule, node, source, file_path))

        return findings

    def _is_system_message_dict(self, node: Any, source_bytes: bytes) -> bool:
        """Check if dictionary represents a system message."""
        node_text = get_node_text(node, source_bytes)
        return '"role"' in node_text and '"system"' in node_text

    def _is_system_message_call(self, node: Any, source_bytes: bytes) -> bool:
        """Check if call creates a system message."""
        node_text = get_node_text(node, source_bytes)
        # HumanMessage included for context
        patterns = ["SystemMessage", "system_message", "HumanMessage"]
        return any(p in node_text for p in patterns) and "system" in node_text.lower()

    def _has_user_input(self, node: Any, source_bytes: bytes) -> bool:
        """Check if node contains user input references."""
        node_text = get_node_text(node, source_bytes)

        if self._has_user_input_in_interpolation(node_text):
            return True

        if self._has_user_input_in_concat(node_text):
            return True

        return self._has_user_input_in_identifiers(node, source_bytes)

    def _has_user_input_in_interpolation(self, node_text: str) -> bool:
        """Check for user input in f-string interpolations."""
        interpolation_pattern = r'\{([^}]+)\}'
        interpolations = re.findall(interpolation_pattern, node_text)

        for interp in interpolations:
            interp_lower = interp.lower().strip()
            if self._matches_user_input_pattern(interp_lower):
                return True

        return False

    def _has_user_input_in_concat(self, node_text: str) -> bool:
        """Check for user input in string concatenation."""
        if " + " not in node_text:
            return False

        return self._matches_user_input_pattern(node_text.lower())

    def _has_user_input_in_identifiers(self, node: Any, source_bytes: bytes) -> bool:
        """Check for user input in identifier nodes."""
        identifiers = find_nodes_by_type(node, "identifier")
        return any(
            self._is_user_input_identifier(ident, source_bytes)
            for ident in identifiers
        )

    def _is_user_input_identifier(self, ident: Any, source_bytes: bytes) -> bool:
        """Check if an identifier represents user input."""
        ident_name = get_node_text(ident, source_bytes).lower()

        if not self._matches_user_input_pattern(ident_name):
            return False

        parent = ident.parent
        if not parent:
            return False

        # Not a dictionary key
        if parent.type != "pair":
            return True

        # For dict pairs, only match if identifier is the value (not the key)
        children = list(parent.children)
        return len(children) >= 2 and children[-1] == ident

    def _matches_user_input_pattern(self, text: str) -> bool:
        """Check if text matches any user input pattern."""
        text_lower = text.lower()
        return any(
            pattern.lower() in text_lower or text_lower == pattern.lower()
            for pattern in self.USER_INPUT_PATTERNS
        )
