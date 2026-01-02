# Bastion

**A pre-commit security scanner that detects prompt injection vulnerabilities in LLM application codebases through static analysis.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Bastion is a static analysis tool that scans your codebase for prompt injection vulnerabilities before they reach production. Unlike runtime tools that require your application to be running, Bastion analyzes source code directly—catching security issues in your pre-commit hooks, CI/CD pipelines, or IDE.

### Key Features

- **Pre-commit integration** - Catch vulnerabilities before code is committed
- **Static analysis** - No API calls or running infrastructure required
- **15+ built-in rules** - Detect common LLM security antipatterns
- **SARIF output** - Integrates with GitHub Security and VS Code
- **Framework-aware** - Understands LangChain, OpenAI, and Anthropic patterns
- **Zero runtime cost** - Works completely offline

## Installation

```bash
pip install bastion-llm
```

Or with pipx (recommended for CLI tools):

```bash
pipx install bastion-llm
```

## Quick Start

```bash
# Scan current directory
bastion scan

# Scan specific files or directories
bastion scan src/ app/

# Output in different formats
bastion scan --format json
bastion scan --format sarif -o results.sarif

# Initialize configuration
bastion init
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Developer Workflow                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Pre-Commit Hook                                 │
│   $ git commit -m "Add chat feature"                                   │
│   Running Bastion... ⏳                                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Bastion Engine                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │   Parser     │  │   Analyzer   │  │   Reporter   │                  │
│  │ (tree-sitter)│──▶  (Rules DB)  │──▶  (SARIF)     │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
│         │                 │                 │                           │
│         ▼                 ▼                 ▼                           │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ AST Analysis    │ Taint Tracking  │ Pattern Match │ Output      │  │
│  │ - Function calls│ - User input    │ - Known vulns │ - SARIF     │  │
│  │ - String concat │ - Request data  │ - Antipatterns│ - JSON/CLI  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Built-in Rules

| Rule ID | Severity | Description |
|---------|----------|-------------|
| PS001 | Critical | User input directly concatenated into prompt string |
| PS002 | Critical | User input in f-string prompt template |
| PS003 | High | Hardcoded API key detected near LLM code |
| PS004 | Critical | System prompt accepts user-controlled content |
| PS005 | Medium | Missing input validation before LLM call |
| PS006 | Medium | LLM output used directly without validation |
| PS007 | High | Unsafe string concatenation in LangChain prompt |
| PS008 | High | Unsafe .format() call on prompt string |
| PS009 | Critical | Request/form data flows to LLM without sanitization |
| PS010 | Medium | Database content used in prompt without escaping |
| PS011 | Info | Jailbreak pattern detected in prompt |
| PS012 | Low | OpenAI API call without error handling |
| PS013 | Low | Anthropic API call without error handling |
| PS014 | High | Unsafe tool/function calling pattern |
| PS015 | Medium | Sensitive data may leak to LLM context |

## Usage

### Command Line

```bash
# Basic scan
bastion scan

# Scan with specific severity threshold
bastion scan --severity high

# Fail CI on high or critical findings
bastion scan --fail-on high

# Output formats
bastion scan --format text     # Default: colored terminal output
bastion scan --format json     # JSON for programmatic use
bastion scan --format sarif    # SARIF for GitHub Security
bastion scan --format html     # HTML report

# Save to file
bastion scan --format sarif -o security-results.sarif

# Disable specific rules
bastion scan --disable-rule PS011 --disable-rule PS012

# List available rules
bastion rules
```

### Pre-commit Integration

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: bastion
        name: Bastion Security Scan
        entry: bastion scan
        language: python
        types: [python]
        pass_filenames: false
```

Or install from the repository:

```yaml
repos:
  - repo: https://github.com/en-yao/bastion
    rev: v0.1.0
    hooks:
      - id: bastion
```

### GitHub Actions

```yaml
name: Security Scan

on: [push, pull_request]

jobs:
  bastion:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Bastion
        run: pip install bastion-llm

      - name: Run security scan
        run: bastion scan --format sarif -o results.sarif

      - name: Upload SARIF to GitHub
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
```

## Configuration

Create a `.bastion.yml` file in your project root:

```yaml
# Paths to scan (defaults to current directory)
paths:
  - src/
  - app/

# File patterns to exclude
exclude:
  - "**/node_modules/**"
  - "**/.venv/**"
  - "**/tests/**"

# File patterns to include
include:
  - "**/*.py"
  - "**/*.js"
  - "**/*.ts"

# Minimum severity to report
min_severity: low  # critical, high, medium, low, info

# Minimum severity to fail with non-zero exit code
fail_on: high

# Rules to disable
disabled_rules:
  - PS011  # Jailbreak pattern detection
  - PS012  # Error handling checks

# Additional custom rules directories
# rules_paths:
#   - ./custom-rules/
```

## Inline Suppressions

Suppress specific findings with comments:

```python
# Suppress all rules on next line
# bastion: ignore
prompt = "You are helpful. " + user_input

# Suppress specific rule
# bastion: ignore[PS001]
prompt = "You are helpful. " + validated_input

# Suppress multiple rules
# bastion: ignore[PS001, PS002]
prompt = f"Context: {user_input}"
```

## Writing Custom Rules

Create a YAML file with custom rules:

```yaml
# custom-rules/my-rules.yml
rules:
  - id: CUSTOM001
    message: "Custom company policy violation"
    severity: high
    category: policy
    description: "Detects violations of company LLM usage policy"
    pattern_type: ast
    languages:
      - python
    fix_suggestion: "Follow the company LLM security guidelines"
```

Load custom rules:

```bash
bastion scan --rules-path ./custom-rules/
```

Or in config:

```yaml
rules_paths:
  - ./custom-rules/
```

## Vulnerability Examples

### PS001: String Concatenation

**Vulnerable:**
```python
def chat(user_input):
    prompt = "You are a helpful assistant. User says: " + user_input
    return llm.complete(prompt)
```

**Fixed:**
```python
def chat(user_input):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": sanitize(user_input)}
    ]
    return llm.chat(messages)
```

### PS004: User Input in System Prompt

**Vulnerable:**
```python
def chat(user_context, user_query):
    messages = [
        {"role": "system", "content": f"You are an assistant. Context: {user_context}"},
        {"role": "user", "content": user_query}
    ]
```

**Fixed:**
```python
def chat(user_context, user_query):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Context: {sanitize(user_context)}\n\nQuestion: {user_query}"}
    ]
```

## Comparison with Other Tools

| Tool | Type | When It Runs | LLM-Specific |
|------|------|--------------|--------------|
| **Bastion** | Static Analysis | Pre-commit | Yes |
| Promptfoo | Runtime Testing | Post-deployment | Yes |
| NeMo Guardrails | Runtime Filtering | Production | Yes |
| Garak | Runtime Probing | Post-deployment | Yes |
| Semgrep | Static Analysis | Pre-commit | No |
| Bandit | Static Analysis | Pre-commit | No |

Bastion fills the gap: **pre-deployment, LLM-specific static analysis**.

## Development

```bash
# Clone the repository
git clone https://github.com/en-yao/bastion
cd bastion

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check src/

# Type checking
mypy src/
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Security

If you discover a security vulnerability in Bastion itself, please report it responsibly by emailing security@bastion.dev.
