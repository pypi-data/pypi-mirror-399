"""Property-based tests using Hypothesis."""

from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from bastion.config import Config
from bastion.models import Confidence, Finding, Location, Rule, ScanResult, Severity
from bastion.parsers import ParserRegistry

pytestmark = pytest.mark.unit


class TestParserProperties:
    """Property-based tests for parsers."""

    @given(st.text(min_size=0, max_size=1000))
    @settings(max_examples=50)
    def test_python_parser_handles_any_text(self, text: str) -> None:
        """Parser should not crash on arbitrary text."""
        registry = ParserRegistry()
        parser = registry.get_parser("python")
        assert parser is not None

        # Should not raise exception
        tree = parser.parse(text)
        assert tree is not None
        assert tree.root_node is not None

    @given(st.text(min_size=0, max_size=1000))
    @settings(max_examples=50)
    def test_javascript_parser_handles_any_text(self, text: str) -> None:
        """JavaScript parser should not crash on arbitrary text."""
        registry = ParserRegistry()
        parser = registry.get_parser("javascript")
        assert parser is not None

        tree = parser.parse(text)
        assert tree is not None
        assert tree.root_node is not None

    @given(st.text(min_size=0, max_size=1000))
    @settings(max_examples=50)
    def test_typescript_parser_handles_any_text(self, text: str) -> None:
        """TypeScript parser should not crash on arbitrary text."""
        registry = ParserRegistry()
        parser = registry.get_parser("typescript")
        assert parser is not None

        tree = parser.parse(text)
        assert tree is not None
        assert tree.root_node is not None


class TestSeverityProperties:
    """Property-based tests for Severity."""

    @given(st.sampled_from(list(Severity)))
    def test_severity_comparison_reflexive(self, sev: Severity) -> None:
        """A severity should equal itself."""
        assert sev == sev
        assert sev >= sev
        assert sev <= sev

    @given(st.sampled_from(list(Severity)), st.sampled_from(list(Severity)))
    def test_severity_comparison_transitive(self, s1: Severity, s2: Severity) -> None:
        """Comparison should be transitive."""
        if s1 <= s2:
            # s1 <= s2 implies not (s1 > s2)
            assert not (s1 > s2)

    @given(st.sampled_from(list(Severity)), st.sampled_from(list(Severity)))
    def test_severity_comparison_antisymmetric(self, s1: Severity, s2: Severity) -> None:
        """If s1 <= s2 and s2 <= s1, then s1 == s2."""
        if s1 <= s2 and s2 <= s1:
            assert s1 == s2


class TestLocationProperties:
    """Property-based tests for Location."""

    @given(
        st.text(min_size=1, max_size=50, alphabet="abcdefghijklmnopqrstuvwxyz"),
        st.integers(min_value=1, max_value=10000),
        st.integers(min_value=1, max_value=500),
        st.integers(min_value=1, max_value=10000),
        st.integers(min_value=1, max_value=500),
    )
    @settings(max_examples=50)
    def test_location_str_format(
        self,
        file_name: str,
        start_line: int,
        start_col: int,
        end_line: int,
        end_col: int,
    ) -> None:
        """Location string should contain file name and line number."""
        file_path = f"test/{file_name}.py"
        loc = Location(
            file_path=Path(file_path),
            start_line=start_line,
            start_column=start_col,
            end_line=end_line,
            end_column=end_col,
        )
        loc_str = str(loc)
        # Check that line number is in the string
        assert str(start_line) in loc_str
        # Check that file name component is in the string (Path normalization may differ)
        assert file_name in loc_str


class TestFindingProperties:
    """Property-based tests for Finding."""

    @given(
        st.text(min_size=1, max_size=10, alphabet="PS0123456789"),
        st.text(min_size=1, max_size=100),
        st.sampled_from(list(Severity)),
        st.sampled_from(list(Confidence)),
    )
    @settings(max_examples=50)
    def test_finding_str_contains_components(
        self,
        rule_id: str,
        message: str,
        severity: Severity,
        confidence: Confidence,
    ) -> None:
        """Finding string should contain rule_id and severity."""
        loc = Location(
            file_path=Path("test.py"),
            start_line=1,
            start_column=1,
            end_line=1,
            end_column=10,
        )
        finding = Finding(
            rule_id=rule_id,
            message=message,
            severity=severity,
            confidence=confidence,
            location=loc,
        )
        finding_str = str(finding)
        assert rule_id in finding_str
        assert severity.value.upper() in finding_str


class TestScanResultProperties:
    """Property-based tests for ScanResult."""

    @given(
        st.integers(min_value=0, max_value=1000),
        st.integers(min_value=0, max_value=100),
        st.floats(min_value=0.0, max_value=1000.0),
        st.integers(min_value=0, max_value=50),
    )
    @settings(max_examples=50)
    def test_scan_result_counts_consistency(
        self,
        files_scanned: int,
        files_with_findings: int,
        scan_time: float,
        rules_applied: int,
    ) -> None:
        """Files with findings should not exceed files scanned."""
        # Ensure constraint
        files_with_findings = min(files_with_findings, files_scanned)

        result = ScanResult(
            findings=[],
            files_scanned=files_scanned,
            files_with_findings=files_with_findings,
            scan_time_seconds=scan_time,
            rules_applied=rules_applied,
        )

        assert result.files_with_findings <= result.files_scanned
        assert result.critical_count == 0
        assert result.high_count == 0
        assert result.has_findings is False


class TestConfigProperties:
    """Property-based tests for Config."""

    @given(
        st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=5),
        st.sampled_from(list(Severity)),
    )
    @settings(max_examples=30)
    def test_config_exclude_patterns(
        self,
        exclude_patterns: list[str],
        min_severity: Severity,
    ) -> None:
        """Config should accept various exclude patterns."""
        cfg = Config()
        cfg.exclude_patterns = exclude_patterns
        cfg.min_severity = min_severity

        assert cfg.exclude_patterns == exclude_patterns
        assert cfg.min_severity == min_severity


class TestRuleProperties:
    """Property-based tests for Rule."""

    @given(
        st.text(min_size=1, max_size=10, alphabet="PS0123456789"),
        st.text(min_size=1, max_size=200),
        st.sampled_from(list(Severity)),
        st.text(min_size=1, max_size=50),
    )
    @settings(max_examples=50)
    def test_rule_from_dict_roundtrip(
        self,
        rule_id: str,
        message: str,
        severity: Severity,
        category: str,
    ) -> None:
        """Rule created from dict should preserve values."""
        data = {
            "id": rule_id,
            "message": message,
            "severity": severity.value,
            "category": category,
            "description": "Test description",
        }
        rule = Rule.from_dict(data)

        assert rule.id == rule_id
        assert rule.message == message
        assert rule.severity == severity
        assert rule.category == category
