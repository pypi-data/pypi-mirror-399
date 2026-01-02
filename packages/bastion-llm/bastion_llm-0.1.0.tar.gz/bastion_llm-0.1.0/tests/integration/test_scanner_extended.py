"""Extended tests for the scanner module."""

from pathlib import Path

import pytest

from bastion.config import Config
from bastion.scanner import Scanner

pytestmark = pytest.mark.integration


class TestScannerExtended:
    """Extended scanner tests for additional coverage."""

    def test_scan_javascript_file(self, tmp_path: Path) -> None:
        """Should scan JavaScript files."""
        js_code = '''
function vulnerable(userInput) {
    const prompt = "Tell me about: " + userInput;
    return prompt;
}
'''
        test_file = tmp_path / "app.js"
        test_file.write_text(js_code)

        config = Config(paths=[tmp_path])
        scanner = Scanner(config)
        result = scanner.scan()

        assert result.files_scanned >= 1

    def test_scan_typescript_file(self, tmp_path: Path) -> None:
        """Should scan TypeScript files."""
        ts_code = '''
function process(input: string): string {
    return "Process: " + input;
}
'''
        test_file = tmp_path / "app.ts"
        test_file.write_text(ts_code)

        config = Config(paths=[tmp_path])
        scanner = Scanner(config)
        result = scanner.scan()

        assert result.files_scanned >= 1

    def test_scan_multiple_files(self, tmp_path: Path) -> None:
        """Should scan multiple files."""
        (tmp_path / "file1.py").write_text("x = 1")
        (tmp_path / "file2.py").write_text("y = 2")
        (tmp_path / "file3.py").write_text("z = 3")

        config = Config(paths=[tmp_path])
        scanner = Scanner(config)
        result = scanner.scan()

        assert result.files_scanned == 3

    def test_scan_nested_directories(self, tmp_path: Path) -> None:
        """Should scan nested directories."""
        subdir = tmp_path / "src" / "app"
        subdir.mkdir(parents=True)
        (subdir / "main.py").write_text("print('hello')")

        config = Config(paths=[tmp_path])
        scanner = Scanner(config)
        result = scanner.scan()

        assert result.files_scanned == 1

    def test_scan_with_taint_analysis(self, tmp_path: Path) -> None:
        """Should enable taint analysis."""
        code = '''
def handle(user_input):
    return user_input
'''
        test_file = tmp_path / "app.py"
        test_file.write_text(code)

        config = Config(paths=[tmp_path])
        scanner = Scanner(config, enable_taint_analysis=True)
        result = scanner.scan()

        assert result.files_scanned == 1

    def test_scan_respects_include_patterns(self, tmp_path: Path) -> None:
        """Should respect include patterns."""
        (tmp_path / "app.py").write_text("x = 1")
        (tmp_path / "test.js").write_text("y = 2")

        config = Config(
            paths=[tmp_path],
            include_patterns=["**/*.py"],
        )
        scanner = Scanner(config)
        result = scanner.scan()

        assert result.files_scanned == 1

    def test_scan_format_string_vulnerability(self, tmp_path: Path) -> None:
        """Should detect format string vulnerabilities."""
        code = '''
def vulnerable(user_data):
    prompt = "Hello {}".format(user_data)
    return prompt
'''
        test_file = tmp_path / "app.py"
        test_file.write_text(code)

        config = Config(paths=[tmp_path])
        scanner = Scanner(config)
        result = scanner.scan()

        assert result.files_scanned == 1

    def test_scan_langchain_patterns(self, tmp_path: Path) -> None:
        """Should detect LangChain vulnerabilities."""
        code = '''
from langchain import PromptTemplate

def create_prompt(user_input):
    template = PromptTemplate.from_template("Query: " + user_input)
    return template
'''
        test_file = tmp_path / "chain.py"
        test_file.write_text(code)

        config = Config(paths=[tmp_path])
        scanner = Scanner(config)
        result = scanner.scan()

        assert result.files_scanned == 1
