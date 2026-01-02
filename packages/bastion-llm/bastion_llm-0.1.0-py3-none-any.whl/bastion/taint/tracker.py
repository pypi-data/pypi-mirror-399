"""Taint tracking for variable propagation."""

from .models import TaintSource


class TaintTracker:
    """Tracks tainted variables through assignments and function calls."""

    def __init__(self) -> None:
        self._tainted_vars: dict[str, TaintSource] = {}

    def mark_tainted(self, var_name: str, source: TaintSource) -> None:
        """Mark a variable as tainted from a source."""
        self._tainted_vars[var_name] = source

    def is_tainted(self, var_name: str) -> bool:
        """Check if a variable is tainted."""
        return var_name in self._tainted_vars

    def get_source(self, var_name: str) -> TaintSource | None:
        """Get the source of taint for a variable."""
        return self._tainted_vars.get(var_name)

    def propagate(self, from_var: str, to_var: str) -> None:
        """Propagate taint from one variable to another."""
        if from_var in self._tainted_vars:
            self._tainted_vars[to_var] = self._tainted_vars[from_var]

    def clear(self) -> None:
        """Clear all taint tracking."""
        self._tainted_vars.clear()
