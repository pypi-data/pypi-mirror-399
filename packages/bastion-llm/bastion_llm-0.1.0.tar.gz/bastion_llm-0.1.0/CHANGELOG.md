# Changelog

All notable changes to Bastion will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-01

### Added
- Initial release
- 15 built-in security rules for prompt injection detection
- Support for Python, JavaScript, and TypeScript
- Multiple output formats: text, JSON, SARIF, HTML
- Pre-commit hook integration
- Taint analysis for tracking user input to LLM calls
- Inline suppression comments (`# bastion: ignore[RULE]`)
- Configuration via `.bastion.yml`
