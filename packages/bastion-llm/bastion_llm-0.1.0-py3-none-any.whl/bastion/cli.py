"""Command-line interface for Bastion."""

import sys
import time
from dataclasses import dataclass
from pathlib import Path

import click
from rich.console import Console

from bastion import __version__
from bastion.config import Config
from bastion.models import Rule, ScanResult, Severity
from bastion.reporters import get_reporter
from bastion.scanner import Scanner

console = Console()


@dataclass
class ScanOptions:
    """Container for scan command options."""

    paths: tuple[str, ...]
    config: Path | None
    output_format: str
    output: Path | None
    severity: str
    fail_on: str
    verbose: bool
    quiet: bool
    no_color: bool
    exclude: tuple[str, ...]
    include: tuple[str, ...]
    disable_rule: tuple[str, ...]
    ignore_nosec: bool
    taint: bool
    diff_base: str | None
    staged: bool


def _load_config(options: ScanOptions) -> Config:
    """Load configuration from file or create default.

    Args:
        options: Scan command options

    Returns:
        Loaded or default Config instance
    """
    if options.config:
        return Config.from_file(options.config)

    config_file = Config.find_config_file()
    if config_file:
        if options.verbose:
            console.print(f"[dim]Using config: {config_file}[/dim]")
        return Config.from_file(config_file)

    return Config()


def _handle_incremental_scan(options: ScanOptions, cfg: Config) -> bool:
    """Handle git-aware incremental scanning.

    Args:
        options: Scan command options
        cfg: Configuration to update with changed files

    Returns:
        True if scan should continue, False if no files to scan
    """
    from bastion.git_utils import GitError, get_changed_files, get_staged_files, is_git_repo

    if not (options.staged or options.diff_base):
        if options.paths:
            cfg.paths = [Path(p) for p in options.paths]
        return True

    if not is_git_repo():
        console.print("[red]Error: --staged and --diff require a git repository[/red]")
        sys.exit(1)

    try:
        if options.staged:
            changed_files = get_staged_files()
            if options.verbose:
                console.print(f"[dim]Scanning {len(changed_files)} staged files[/dim]")
        else:
            changed_files = get_changed_files(base=options.diff_base or "HEAD")
            if options.verbose:
                msg = f"Scanning {len(changed_files)} files changed since {options.diff_base}"
                console.print(f"[dim]{msg}[/dim]")

        if not changed_files:
            if not options.quiet:
                console.print("[green]No files to scan[/green]")
            return False

        cfg.paths = changed_files
        return True

    except GitError as e:
        console.print(f"[red]Git error: {e}[/red]")
        sys.exit(1)


def _apply_cli_options(options: ScanOptions, cfg: Config) -> None:
    """Apply CLI options to configuration.

    Args:
        options: Scan command options
        cfg: Configuration to update
    """
    if options.exclude:
        cfg.exclude_patterns.extend(options.exclude)
    if options.include:
        cfg.include_patterns = list(options.include)
    if options.disable_rule:
        cfg.disabled_rules.extend(options.disable_rule)

    cfg.min_severity = Severity(options.severity)
    cfg.fail_on = Severity(options.fail_on)
    cfg.output_format = options.output_format
    cfg.output_file = options.output
    cfg.verbose = options.verbose
    cfg.quiet = options.quiet
    cfg.no_color = options.no_color
    cfg.ignore_nosec = options.ignore_nosec


def _run_scan(options: ScanOptions, cfg: Config) -> ScanResult:
    """Execute the scan and return results.

    Args:
        options: Scan command options
        cfg: Configuration for the scan

    Returns:
        Scan results
    """
    output_console = Console(no_color=options.no_color, force_terminal=not options.no_color)
    scanner = Scanner(cfg, enable_taint_analysis=options.taint)

    if not options.quiet:
        output_console.print(f"[bold blue]Bastion[/bold blue] v{__version__}")
        if options.taint:
            output_console.print("[dim]Taint analysis enabled[/dim]")
        output_console.print()

    start_time = time.time()
    result = scanner.scan()
    result.scan_time_seconds = time.time() - start_time

    return result


def _report_results(options: ScanOptions, cfg: Config, result: ScanResult) -> None:
    """Report scan results and write to file if specified.

    Args:
        options: Scan command options
        cfg: Configuration
        result: Scan results to report
    """
    output_console = Console(no_color=options.no_color, force_terminal=not options.no_color)
    reporter = get_reporter(cfg.output_format, output_console, cfg)
    reporter.report(result)

    if cfg.output_file:
        with open(cfg.output_file, "w") as f:
            f.write(reporter.format(result))
        if not options.quiet:
            output_console.print(f"\n[dim]Results written to {cfg.output_file}[/dim]")


def _determine_exit_code(cfg: Config, result: ScanResult) -> int:
    """Determine the exit code based on scan results.

    Args:
        cfg: Configuration with fail_on severity
        result: Scan results

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if result.has_findings:
        max_severity = max(f.severity for f in result.findings)
        if max_severity >= cfg.fail_on:
            return 1
    return 0


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="bastion")
@click.pass_context
def main(ctx: click.Context) -> None:
    """Bastion - Pre-commit security scanner for LLM applications.

    Detects prompt injection vulnerabilities through static analysis.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option("-c", "--config", type=click.Path(exists=True, path_type=Path),
              help="Path to configuration file")
@click.option("-f", "--format", "output_format",
              type=click.Choice(["text", "json", "sarif", "html"]), default="text",
              help="Output format")
@click.option("-o", "--output", type=click.Path(path_type=Path),
              help="Output file path")
@click.option("--severity", type=click.Choice(["critical", "high", "medium", "low", "info"]),
              default="low", help="Minimum severity to report")
@click.option("--fail-on", type=click.Choice(["critical", "high", "medium", "low", "info"]),
              default="high", help="Minimum severity to fail with non-zero exit code")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.option("-q", "--quiet", is_flag=True, help="Suppress all output except errors")
@click.option("--no-color", is_flag=True, help="Disable colored output")
@click.option("--exclude", multiple=True, help="Glob patterns to exclude")
@click.option("--include", multiple=True, help="Glob patterns to include")
@click.option("--disable-rule", multiple=True, help="Rule IDs to disable")
@click.option("--ignore-nosec", is_flag=True, help="Ignore # bastion: ignore comments")
@click.option("--taint", is_flag=True,
              help="Enable taint analysis for advanced data flow tracking")
@click.option("--diff", "diff_base", type=str, default=None,
              help="Scan only files changed since specified commit/branch (e.g., --diff main)")
@click.option("--staged", is_flag=True,
              help="Scan only staged files (useful for pre-commit hooks)")
def scan(
    paths: tuple[str, ...],
    config: Path | None,
    output_format: str,
    output: Path | None,
    severity: str,
    fail_on: str,
    verbose: bool,
    quiet: bool,
    no_color: bool,
    exclude: tuple[str, ...],
    include: tuple[str, ...],
    disable_rule: tuple[str, ...],
    ignore_nosec: bool,
    taint: bool,
    diff_base: str | None,
    staged: bool,
) -> None:
    """Scan files for prompt injection vulnerabilities.

    PATHS are files or directories to scan. Defaults to current directory.
    """
    options = ScanOptions(
        paths=paths, config=config, output_format=output_format, output=output,
        severity=severity, fail_on=fail_on, verbose=verbose, quiet=quiet,
        no_color=no_color, exclude=exclude, include=include, disable_rule=disable_rule,
        ignore_nosec=ignore_nosec, taint=taint, diff_base=diff_base, staged=staged,
    )

    cfg = _load_config(options)

    if not _handle_incremental_scan(options, cfg):
        sys.exit(0)

    _apply_cli_options(options, cfg)

    result = _run_scan(options, cfg)
    _report_results(options, cfg, result)

    sys.exit(_determine_exit_code(cfg, result))


@main.command()
@click.option("--force", is_flag=True, help="Overwrite existing configuration")
def init(force: bool) -> None:
    """Initialize Bastion configuration in the current directory."""
    config_path = Path(".bastion.yml")

    if config_path.exists() and not force:
        console.print(f"[yellow]Configuration file already exists: {config_path}[/yellow]")
        console.print("Use --force to overwrite")
        sys.exit(1)

    _write_default_config(config_path)
    _print_init_success(config_path)


def _write_default_config(config_path: Path) -> None:
    """Write default configuration file.

    Args:
        config_path: Path to write configuration to
    """
    default_config = """\
# Bastion Configuration
# https://github.com/en-yao/bastion

# Paths to scan (defaults to current directory)
# paths:
#   - src/
#   - app/

# File patterns to exclude
exclude:
  - "**/node_modules/**"
  - "**/.venv/**"
  - "**/venv/**"
  - "**/__pycache__/**"
  - "**/.git/**"
  - "**/dist/**"
  - "**/build/**"

# File patterns to include
include:
  - "**/*.py"
  - "**/*.js"
  - "**/*.ts"

# Minimum severity to report (critical, high, medium, low, info)
min_severity: low

# Minimum severity to fail with non-zero exit code
fail_on: high

# Rules to disable
# disabled_rules:
#   - PS001

# Additional rules directories
# rules_paths:
#   - ./custom-rules/
"""
    with open(config_path, "w") as f:
        f.write(default_config)


def _print_init_success(config_path: Path) -> None:
    """Print success message after initialization.

    Args:
        config_path: Path to the created configuration file
    """
    console.print(f"[green]Created configuration file: {config_path}[/green]")
    console.print("\nNext steps:")
    console.print("  1. Edit .bastion.yml to customize settings")
    console.print("  2. Run 'bastion scan' to scan your code")
    console.print("  3. Add to pre-commit: see 'bastion setup-precommit'")


@main.command("setup-precommit")
def setup_precommit() -> None:
    """Show instructions for pre-commit hook setup."""
    console.print("[bold]Setting up Bastion with pre-commit[/bold]\n")

    console.print("Add this to your .pre-commit-config.yaml:\n")
    console.print("""\
[dim]repos:
  - repo: local
    hooks:
      - id: bastion
        name: Bastion Security Scan
        entry: bastion scan
        language: python
        types: [python]
        pass_filenames: false[/dim]
""")

    console.print("Or install directly from the repository:\n")
    console.print("""\
[dim]repos:
  - repo: https://github.com/en-yao/bastion
    rev: v0.1.0
    hooks:
      - id: bastion[/dim]
""")


@main.command()
def rules() -> None:
    """List all available rules."""
    from bastion.rules import RuleRegistry

    registry = RuleRegistry()
    registry.load_builtin_rules()

    console.print("[bold]Available Rules[/bold]\n")

    for rule in sorted(registry.rules.values(), key=lambda r: r.id):
        _print_rule(rule)


def _print_rule(rule: Rule) -> None:
    """Print a single rule's information.

    Args:
        rule: Rule to print
    """
    severity_color = {
        Severity.CRITICAL: "red",
        Severity.HIGH: "red",
        Severity.MEDIUM: "yellow",
        Severity.LOW: "blue",
        Severity.INFO: "dim",
    }.get(rule.severity, "white")

    sev = rule.severity.value.upper()
    console.print(f"[bold]{rule.id}[/bold] [{severity_color}]{sev}[/{severity_color}]")
    console.print(f"  {rule.message}")
    if rule.description:
        console.print(f"  [dim]{rule.description}[/dim]")
    console.print()


if __name__ == "__main__":
    main()
