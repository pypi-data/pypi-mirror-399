"""Base reporter protocol."""

from typing import Protocol

from bastion.models import ScanResult


class Reporter(Protocol):
    """Protocol for result reporters."""

    def report(self, result: ScanResult) -> None:
        """Display the result."""
        ...

    def format(self, result: ScanResult) -> str:
        """Format result as string."""
        ...
