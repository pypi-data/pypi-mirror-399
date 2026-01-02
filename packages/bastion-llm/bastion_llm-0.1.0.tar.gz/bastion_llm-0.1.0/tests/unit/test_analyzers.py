"""Tests for analyzer modules."""

from pathlib import Path

import pytest

from bastion.analyzers import (
    AnalyzerRegistry,
    BaseAnalyzer,
    FStringAnalyzer,
    HardcodedSecretsAnalyzer,
    StringConcatAnalyzer,
)
from bastion.models import Rule, Severity
from bastion.parsers import ParserRegistry

pytestmark = pytest.mark.unit


def create_test_rule(rule_id: str = "PS001") -> Rule:
    """Create a test rule."""
    return Rule(
        id=rule_id,
        message="Test rule",
        severity=Severity.HIGH,
        category="test",
        description="Test rule description",
    )


class TestBaseAnalyzer:
    """Test BaseAnalyzer class."""

    def test_base_analyzer_abstract(self) -> None:
        """BaseAnalyzer should provide common functionality."""
        # BaseAnalyzer can be instantiated
        analyzer = BaseAnalyzer()
        assert analyzer is not None


class TestAnalyzerRegistry:
    """Test AnalyzerRegistry class."""

    def test_get_analyzer_for_rule(self) -> None:
        """Should return analyzer for known rule."""
        registry = AnalyzerRegistry()
        rule = create_test_rule("PS001")

        analyzer = registry.get_analyzer(rule)

        assert analyzer is not None
        assert isinstance(analyzer, StringConcatAnalyzer)

    def test_get_analyzer_for_unknown_rule(self) -> None:
        """Should return None for unknown rule."""
        registry = AnalyzerRegistry()
        rule = create_test_rule("UNKNOWN")

        analyzer = registry.get_analyzer(rule)

        assert analyzer is None

    def test_register_custom_analyzer(self) -> None:
        """Should register custom analyzer."""
        registry = AnalyzerRegistry()
        custom_analyzer = StringConcatAnalyzer()

        registry.register_analyzer("CUSTOM001", custom_analyzer)
        rule = create_test_rule("CUSTOM001")
        analyzer = registry.get_analyzer(rule)

        assert analyzer is custom_analyzer


class TestStringConcatAnalyzer:
    """Test StringConcatAnalyzer."""

    def test_detects_concat_with_user_input(self) -> None:
        """Should detect string concatenation with user input."""
        registry = ParserRegistry()
        parser = registry.get_parser("python")
        assert parser is not None

        analyzer = StringConcatAnalyzer()
        rule = create_test_rule("PS001")

        code = '''
def vulnerable(user_input):
    prompt = "Hello " + user_input
    return prompt
'''
        tree = parser.parse(code)
        findings = analyzer.analyze(tree, code, Path("test.py"), rule)

        assert len(findings) > 0
        assert findings[0].rule_id == "PS001"

    def test_no_detection_for_safe_code(self) -> None:
        """Should not flag safe concatenation."""
        registry = ParserRegistry()
        parser = registry.get_parser("python")
        assert parser is not None

        analyzer = StringConcatAnalyzer()
        rule = create_test_rule("PS001")

        code = '''
def safe():
    greeting = "Hello " + "World"
    return greeting
'''
        tree = parser.parse(code)
        findings = analyzer.analyze(tree, code, Path("test.py"), rule)

        assert len(findings) == 0


class TestFStringAnalyzer:
    """Test FStringAnalyzer."""

    def test_analyzes_fstring(self) -> None:
        """Should analyze f-string patterns."""
        registry = ParserRegistry()
        parser = registry.get_parser("python")
        assert parser is not None

        analyzer = FStringAnalyzer()
        rule = create_test_rule("PS002")

        code = '''
def process(user_input):
    prompt = f"Tell me about {user_input}"
    return prompt
'''
        tree = parser.parse(code)
        findings = analyzer.analyze(tree, code, Path("test.py"), rule)

        # Analyzer runs without error
        assert isinstance(findings, list)


class TestHardcodedSecretsAnalyzer:
    """Test HardcodedSecretsAnalyzer."""

    def test_detects_openai_key(self) -> None:
        """Should detect hardcoded OpenAI API key."""
        registry = ParserRegistry()
        parser = registry.get_parser("python")
        assert parser is not None

        analyzer = HardcodedSecretsAnalyzer()
        rule = create_test_rule("PS003")

        code = '''
api_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890ab"
'''
        tree = parser.parse(code)
        findings = analyzer.analyze(tree, code, Path("test.py"), rule)

        assert len(findings) > 0
        assert findings[0].rule_id == "PS003"

    def test_no_detection_for_env_var(self) -> None:
        """Should not flag environment variable usage."""
        registry = ParserRegistry()
        parser = registry.get_parser("python")
        assert parser is not None

        analyzer = HardcodedSecretsAnalyzer()
        rule = create_test_rule("PS003")

        code = '''
import os
api_key = os.environ.get("OPENAI_API_KEY")
'''
        tree = parser.parse(code)
        findings = analyzer.analyze(tree, code, Path("test.py"), rule)

        assert len(findings) == 0
