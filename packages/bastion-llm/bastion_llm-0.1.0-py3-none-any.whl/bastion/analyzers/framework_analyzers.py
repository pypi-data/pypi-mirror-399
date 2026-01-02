"""Analyzers for LLM framework-specific patterns."""

from pathlib import Path
from typing import Any

from tree_sitter import Tree

from bastion.models import Confidence, Finding, Rule
from bastion.parsers import find_nodes_by_type, get_node_text

from .base import BaseAnalyzer


class LangChainAnalyzer(BaseAnalyzer):
    """Detects unsafe LangChain patterns (PS007)."""

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

        # Find LangChain prompt template usages
        call_nodes = find_nodes_by_type(tree.root_node, "call")

        for node in call_nodes:
            node_text = get_node_text(node, source_bytes)

            # Check for PromptTemplate with potential injection
            is_template = "PromptTemplate" in node_text or "ChatPromptTemplate" in node_text
            if is_template and self._has_unsafe_template(node, source_bytes):
                findings.append(self.create_finding(rule, node, source, file_path))

        return findings

    def _has_unsafe_template(self, node: Any, source_bytes: bytes) -> bool:
        """Check if template has unsafe patterns."""
        node_text = get_node_text(node, source_bytes)

        # Check for string concatenation in template
        has_concat = " + " in node_text
        has_user_input = any(p in node_text.lower() for p in self.USER_INPUT_PATTERNS)
        return bool(has_concat and has_user_input)


class OpenAIErrorHandlingAnalyzer(BaseAnalyzer):
    """Detects OpenAI API calls without error handling (PS012)."""

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

        openai_patterns = ["openai.", "ChatCompletion", "Completion.create"]

        call_nodes = find_nodes_by_type(tree.root_node, "call")

        for node in call_nodes:
            node_text = get_node_text(node, source_bytes)
            is_openai = any(p in node_text for p in openai_patterns)
            if is_openai and not self._is_in_try_block(node):
                findings.append(self.create_finding(
                    rule, node, source, file_path,
                    confidence=Confidence.MEDIUM
                ))

        return findings

    def _is_in_try_block(self, node: Any) -> bool:
        """Check if node is inside a try block."""
        parent = node.parent
        while parent:
            if parent.type == "try_statement":
                return True
            parent = parent.parent
        return False


class AnthropicErrorHandlingAnalyzer(BaseAnalyzer):
    """Detects Anthropic API calls without error handling (PS013)."""

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

        anthropic_patterns = ["anthropic.", "messages.create", "Claude"]

        call_nodes = find_nodes_by_type(tree.root_node, "call")

        for node in call_nodes:
            node_text = get_node_text(node, source_bytes)
            is_anthropic = any(p in node_text for p in anthropic_patterns)
            if is_anthropic and not self._is_in_try_block(node):
                findings.append(self.create_finding(
                    rule, node, source, file_path,
                    confidence=Confidence.MEDIUM
                ))

        return findings

    def _is_in_try_block(self, node: Any) -> bool:
        """Check if node is inside a try block."""
        parent = node.parent
        while parent:
            if parent.type == "try_statement":
                return True
            parent = parent.parent
        return False


class UnsafeToolCallingAnalyzer(BaseAnalyzer):
    """Detects unsafe tool/function calling patterns (PS014)."""

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

        tool_patterns = ["tools=", "functions=", "function_call", "tool_choice"]

        call_nodes = find_nodes_by_type(tree.root_node, "call")

        for node in call_nodes:
            node_text = get_node_text(node, source_bytes)
            is_tool_call = any(p in node_text for p in tool_patterns)
            if is_tool_call and self._has_unsafe_tool_config(node, source_bytes):
                findings.append(self.create_finding(
                    rule, node, source, file_path,
                    confidence=Confidence.MEDIUM
                ))

        return findings

    def _has_unsafe_tool_config(self, node: Any, source_bytes: bytes) -> bool:
        """Check if tool configuration is unsafe."""
        node_text = get_node_text(node, source_bytes)
        unsafe = ['"auto"', "'auto'", "tool_choice='any'", 'tool_choice="any"']
        return any(p in node_text for p in unsafe)
