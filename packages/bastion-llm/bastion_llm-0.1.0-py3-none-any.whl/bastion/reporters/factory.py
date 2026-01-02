"""Factory function for creating reporters."""

from rich.console import Console

from bastion.config import Config

from .base import Reporter
from .html import HtmlReporter
from .json_reporter import JsonReporter
from .sarif import SarifReporter
from .text import TextReporter


def get_reporter(format_name: str, console: Console, config: Config) -> Reporter:
    """Get a reporter by format name.

    Args:
        format_name: The output format (text, json, sarif, html)
        console: Rich console for output
        config: Configuration options

    Returns:
        A reporter instance for the specified format
    """
    reporters: dict[str, type[TextReporter | JsonReporter | SarifReporter | HtmlReporter]] = {
        "text": TextReporter,
        "json": JsonReporter,
        "sarif": SarifReporter,
        "html": HtmlReporter,
    }

    reporter_class = reporters.get(format_name, TextReporter)
    return reporter_class(console, config)
