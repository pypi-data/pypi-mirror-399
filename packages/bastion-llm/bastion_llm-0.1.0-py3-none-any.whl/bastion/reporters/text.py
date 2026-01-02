"""Text reporter for terminal output."""

from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.text import Text

from bastion.config import Config
from bastion.models import Finding, ScanResult, Severity


class TextReporter:
    """Rich terminal output reporter."""

    SEVERITY_COLORS = {
        Severity.CRITICAL: "red bold",
        Severity.HIGH: "red",
        Severity.MEDIUM: "yellow",
        Severity.LOW: "blue",
        Severity.INFO: "dim",
    }

    SEVERITY_ICONS = {
        Severity.CRITICAL: "[X]",
        Severity.HIGH: "[!]",
        Severity.MEDIUM: "[~]",
        Severity.LOW: "[-]",
        Severity.INFO: "[i]",
    }

    def __init__(self, console: Console, config: Config) -> None:
        """Initialize the text reporter."""
        self.console = console
        self.config = config

    def report(self, result: ScanResult) -> None:
        """Display findings in the terminal."""
        if self.config.quiet and not result.has_findings:
            return

        if not result.has_findings:
            self.console.print("[green]No security issues found![/green]")
            self._print_summary(result)
            return

        # Group findings by file
        findings_by_file: dict[Path, list[Finding]] = {}
        for finding in result.findings:
            path = finding.location.file_path
            if path not in findings_by_file:
                findings_by_file[path] = []
            findings_by_file[path].append(finding)

        # Print findings
        for file_path, findings in findings_by_file.items():
            self.console.print(f"\n[bold]{file_path}[/bold]")

            for finding in findings:
                self._print_finding(finding)

        self._print_summary(result)

    def _print_finding(self, finding: Finding) -> None:
        """Print a single finding."""
        color = self.SEVERITY_COLORS.get(finding.severity, "white")
        icon = self.SEVERITY_ICONS.get(finding.severity, "[ ]")

        # Header line
        header = Text()
        header.append(f"  {icon} ", style=color)
        header.append(f"[{finding.rule_id}] ", style="bold")
        header.append(finding.message)
        self.console.print(header)

        # Location
        loc = finding.location
        self.console.print(f"     [dim]Line {loc.start_line}:{loc.start_column}[/dim]")

        # Code snippet
        if loc.snippet:
            for line in loc.snippet.split("\n")[:3]:  # Show max 3 lines
                self.console.print(f"     [dim]|[/dim] {line.rstrip()}")

        # Fix suggestion
        if finding.fix_suggestion and self.config.verbose:
            self.console.print(f"     [green]Fix:[/green] {finding.fix_suggestion}")

        self.console.print()

    def _print_summary(self, result: ScanResult) -> None:
        """Print scan summary."""
        self.console.print()

        # Summary table
        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="dim")
        table.add_column("Value")

        table.add_row("Files scanned", str(result.files_scanned))
        table.add_row("Files with issues", str(result.files_with_findings))
        table.add_row("Rules applied", str(result.rules_applied))
        table.add_row("Scan time", f"{result.scan_time_seconds:.2f}s")

        self.console.print(table)

        # Severity breakdown
        if result.has_findings:
            self.console.print()
            breakdown = []
            if result.critical_count:
                breakdown.append(f"[red bold]{result.critical_count} critical[/red bold]")
            if result.high_count:
                breakdown.append(f"[red]{result.high_count} high[/red]")
            if result.medium_count:
                breakdown.append(f"[yellow]{result.medium_count} medium[/yellow]")
            if result.low_count:
                breakdown.append(f"[blue]{result.low_count} low[/blue]")

            self.console.print("Findings: " + ", ".join(breakdown))

    def format(self, result: ScanResult) -> str:
        """Format as plain text."""
        lines = []

        for finding in result.findings:
            loc = finding.location
            lines.append(
                f"{loc.file_path}:{loc.start_line}:{loc.start_column}: "
                f"{finding.severity.value.upper()} [{finding.rule_id}] {finding.message}"
            )

        return "\n".join(lines)
