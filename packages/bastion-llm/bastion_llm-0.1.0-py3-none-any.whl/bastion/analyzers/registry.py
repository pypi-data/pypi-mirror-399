"""Analyzer registry for mapping rules to analyzers."""

from bastion.models import Rule

from .base import Analyzer
from .dataflow_analyzers import (
    DatabaseDataFlowAnalyzer,
    MissingInputValidationAnalyzer,
    RequestDataFlowAnalyzer,
)
from .framework_analyzers import (
    AnthropicErrorHandlingAnalyzer,
    LangChainAnalyzer,
    OpenAIErrorHandlingAnalyzer,
    UnsafeToolCallingAnalyzer,
)
from .prompt_analyzers import (
    FormatStringAnalyzer,
    FStringAnalyzer,
    StringConcatAnalyzer,
    SystemPromptInjectionAnalyzer,
)
from .security_analyzers import (
    HardcodedSecretsAnalyzer,
    JailbreakPatternAnalyzer,
    SensitiveDataAnalyzer,
    UnsafeOutputUsageAnalyzer,
)


class AnalyzerRegistry:
    """Registry for security analyzers."""

    def __init__(self) -> None:
        """Initialize the analyzer registry with built-in analyzers."""
        self._analyzers: dict[str, Analyzer] = {
            "PS001": StringConcatAnalyzer(),
            "PS002": FStringAnalyzer(),
            "PS003": HardcodedSecretsAnalyzer(),
            "PS004": SystemPromptInjectionAnalyzer(),
            "PS005": MissingInputValidationAnalyzer(),
            "PS006": UnsafeOutputUsageAnalyzer(),
            "PS007": LangChainAnalyzer(),
            "PS008": FormatStringAnalyzer(),
            "PS009": RequestDataFlowAnalyzer(),
            "PS010": DatabaseDataFlowAnalyzer(),
            "PS011": JailbreakPatternAnalyzer(),
            "PS012": OpenAIErrorHandlingAnalyzer(),
            "PS013": AnthropicErrorHandlingAnalyzer(),
            "PS014": UnsafeToolCallingAnalyzer(),
            "PS015": SensitiveDataAnalyzer(),
        }

    def get_analyzer(self, rule: Rule) -> Analyzer | None:
        """Get the analyzer for a rule."""
        return self._analyzers.get(rule.id)

    def register_analyzer(self, rule_id: str, analyzer: Analyzer) -> None:
        """Register an analyzer for a rule."""
        self._analyzers[rule_id] = analyzer
