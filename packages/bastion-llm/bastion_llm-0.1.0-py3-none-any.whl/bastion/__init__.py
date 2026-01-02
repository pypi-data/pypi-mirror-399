"""Bastion - Pre-commit security scanner for LLM applications.

A static analysis tool that detects prompt injection vulnerabilities
in LLM application codebases before deployment.
"""

__version__ = "0.1.0"

from bastion.config import Config
from bastion.models import Confidence, FileError, Finding, ScanError, ScanResult, Severity
from bastion.scanner import Scanner

__all__ = [
    "__version__",
    "Scanner",
    "Config",
    "Finding",
    "FileError",
    "ScanError",
    "ScanResult",
    "Severity",
    "Confidence",
]
