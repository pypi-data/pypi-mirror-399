"""Base analyzer classes and protocols."""

from pathlib import Path
from typing import Any, Protocol

from tree_sitter import Tree

from bastion.models import Confidence, Finding, Location, Rule


class Analyzer(Protocol):
    """Protocol for security analyzers."""

    def analyze(
        self,
        tree: Tree,
        source: str,
        file_path: Path,
        rule: Rule,
    ) -> list[Finding]:
        """Analyze the AST and return findings."""
        ...


class BaseAnalyzer:
    """Base class for analyzers with common utilities."""

    # Common patterns indicating user input sources (variable names)
    USER_INPUT_PATTERNS = {
        # Flask/FastAPI
        "request.args", "request.form", "request.json", "request.data",
        "request.query_params", "request.body",
        # Function parameters that commonly hold user input
        "user_input", "user_message", "user_query", "user_text", "user_content",
        "user_context", "user_data",
        "query", "input_text", "input_message",
        "question", "prompt_input",
    }

    # LLM API call patterns
    LLM_CALL_PATTERNS = {
        # OpenAI
        "openai.ChatCompletion.create", "openai.Completion.create",
        "client.chat.completions.create", "client.completions.create",
        "ChatCompletion.create", "Completion.create",
        # Anthropic
        "anthropic.messages.create", "client.messages.create",
        "anthropic.completions.create",
        # LangChain
        "llm.invoke", "llm.predict", "chain.invoke", "chain.run",
        "ChatOpenAI", "ChatAnthropic",
    }

    # Patterns indicating sensitive data
    SENSITIVE_PATTERNS = {
        "password", "secret", "token", "api_key", "apikey", "api-key",
        "private_key", "privatekey", "auth", "credential", "ssn",
        "credit_card", "creditcard",
    }

    def get_source_bytes(self, source: str) -> bytes:
        """Convert source string to bytes for tree-sitter."""
        return source.encode("utf-8")

    def create_finding(
        self,
        rule: Rule,
        node: Any,
        source: str,
        file_path: Path,
        confidence: Confidence = Confidence.HIGH,
    ) -> Finding:
        """Create a finding from a node."""
        self.get_source_bytes(source)
        lines = source.split("\n")

        start_line = node.start_point[0] + 1
        end_line = node.end_point[0] + 1

        # Get snippet (the relevant lines)
        snippet_lines = lines[node.start_point[0]:node.end_point[0] + 1]
        snippet = "\n".join(snippet_lines)

        location = Location(
            file_path=file_path,
            start_line=start_line,
            start_column=node.start_point[1] + 1,
            end_line=end_line,
            end_column=node.end_point[1] + 1,
            snippet=snippet,
        )

        return Finding(
            rule_id=rule.id,
            message=rule.message,
            severity=rule.severity,
            confidence=confidence,
            location=location,
            category=rule.category,
            cwe_id=rule.cwe_id,
            fix_suggestion=rule.fix_suggestion,
            references=rule.references,
        )
