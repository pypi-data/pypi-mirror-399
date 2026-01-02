"""Taint analyzer for tracking data flow from sources to sinks."""

from pathlib import Path
from typing import Any

from tree_sitter import Tree

from bastion.models import Confidence, Finding, Location, Rule
from bastion.parsers import find_nodes_by_type, find_nodes_by_types, get_node_text

from .models import TaintFlow, TaintSink, TaintSource
from .tracker import TaintTracker


class TaintAnalyzer:
    """Analyzes code for tainted data flows from user input to LLM calls."""

    # User input sources (where tainted data enters)
    SOURCE_PATTERNS = {
        # Flask/FastAPI request data
        "request.args", "request.form", "request.json", "request.data",
        "request.query_params", "request.body", "request.get_json",
        # Function parameters with common user input names
        "user_input", "user_message", "user_query", "user_text",
        "user_content", "query", "input_text", "prompt_input",
        # Environment variables (could be attacker-controlled)
        "os.environ", "os.getenv",
    }

    # LLM API call patterns (sinks)
    SINK_PATTERNS = {
        # OpenAI
        "openai.ChatCompletion.create", "openai.Completion.create",
        "client.chat.completions.create", "client.completions.create",
        # Anthropic
        "anthropic.messages.create", "client.messages.create",
        # LangChain
        "llm.invoke", "llm.predict", "chain.invoke", "chain.run",
    }

    def __init__(self) -> None:
        self._tracker = TaintTracker()

    def analyze(
        self,
        tree: Tree,
        source: str,
        file_path: Path,
        rule: Rule,
    ) -> list[Finding]:
        """Analyze code for tainted data flows."""
        findings = []
        source_bytes = source.encode("utf-8")
        self._tracker.clear()

        # Phase 1: Identify sources and mark initial tainted variables
        sources = self._find_sources(tree.root_node, source_bytes)
        for src in sources:
            self._tracker.mark_tainted(src.name, src)

        # Phase 2: Track taint through assignments
        self._track_assignments(tree.root_node, source_bytes)

        # Phase 3: Identify sinks
        sinks = self._find_sinks(tree.root_node, source_bytes)

        # Phase 4: Check if tainted data reaches sinks
        flows = self._find_flows(sinks, source_bytes)

        # Phase 5: Create findings for each flow
        for flow in flows:
            finding = self._create_finding(flow, source, file_path, rule)
            findings.append(finding)

        return findings

    def _find_sources(self, node: Any, source_bytes: bytes) -> list[TaintSource]:
        """Find all taint sources in the AST."""
        sources = []

        # Find assignments from source patterns
        assignments = find_nodes_by_type(node, "assignment")
        for assign in assignments:
            assign_text = get_node_text(assign, source_bytes)

            # Check if right side contains a source pattern
            for pattern in self.SOURCE_PATTERNS:
                if pattern in assign_text:
                    # Get the variable being assigned (left side)
                    for child in assign.children:
                        if child.type == "identifier":
                            var_name = get_node_text(child, source_bytes)
                            source_type = self._classify_source_type(pattern)
                            sources.append(TaintSource(
                                name=var_name,
                                node=assign,
                                line=assign.start_point[0] + 1,
                                source_type=source_type,
                            ))
                            break
                    break

        # Find function parameters with user input names
        func_defs = find_nodes_by_types(node, {"function_definition", "function_declaration"})
        for func in func_defs:
            params = find_nodes_by_type(func, "identifier")
            for param in params:
                param_name = get_node_text(param, source_bytes)
                if any(p in param_name.lower() for p in ["user", "input", "query", "message"]):
                    sources.append(TaintSource(
                        name=param_name,
                        node=param,
                        line=param.start_point[0] + 1,
                        source_type="parameter",
                    ))

        return sources

    def _classify_source_type(self, pattern: str) -> str:
        """Classify the type of taint source."""
        if "request" in pattern:
            return "request"
        elif "environ" in pattern or "getenv" in pattern:
            return "environment"
        else:
            return "parameter"

    def _track_assignments(self, node: Any, source_bytes: bytes) -> None:
        """Track taint propagation through assignments."""
        assignments = find_nodes_by_type(node, "assignment")

        for assign in assignments:
            children = list(assign.children)
            if len(children) >= 2:
                # Get left side (target)
                target = None
                for child in children:
                    if child.type == "identifier":
                        target = get_node_text(child, source_bytes)
                        break

                if not target:
                    continue

                # Check if right side uses any tainted variable
                assign_text = get_node_text(assign, source_bytes)
                for tainted_var in list(self._tracker._tainted_vars.keys()):
                    if tainted_var in assign_text:
                        # Propagate taint
                        self._tracker.propagate(tainted_var, target)
                        break

    def _find_sinks(self, node: Any, source_bytes: bytes) -> list[TaintSink]:
        """Find all potential sinks in the AST."""
        sinks = []

        call_nodes = find_nodes_by_type(node, "call")
        for call in call_nodes:
            call_text = get_node_text(call, source_bytes)

            for pattern in self.SINK_PATTERNS:
                if pattern.lower() in call_text.lower():
                    sinks.append(TaintSink(
                        name=pattern,
                        node=call,
                        line=call.start_point[0] + 1,
                        sink_type="llm_call",
                    ))
                    break

        return sinks

    def _find_flows(self, sinks: list[TaintSink], source_bytes: bytes) -> list[TaintFlow]:
        """Find flows from tainted sources to sinks."""
        flows = []

        for sink in sinks:
            sink_text = get_node_text(sink.node, source_bytes)

            # Check if any tainted variable is used in the sink
            for var_name, source in self._tracker._tainted_vars.items():
                if var_name in sink_text:
                    flows.append(TaintFlow(
                        source=source,
                        sink=sink,
                        path=[var_name],
                    ))

        return flows

    def _create_finding(
        self,
        flow: TaintFlow,
        source: str,
        file_path: Path,
        rule: Rule,
    ) -> Finding:
        """Create a finding from a taint flow."""
        lines = source.split("\n")

        # Use the sink location for the finding
        node = flow.sink.node
        start_line = node.start_point[0] + 1
        end_line = node.end_point[0] + 1

        snippet_lines = lines[node.start_point[0]:node.end_point[0] + 1]
        snippet = "\n".join(snippet_lines)

        location = Location(
            file_path=file_path,
            start_line=start_line,
            start_column=node.start_point[1] + 1,
            end_line=end_line,
            end_column=node.end_point[1] + 1,
            snippet=snippet,
        )

        # Build detailed message with flow information
        message = (
            f"Tainted data flows from '{flow.source.name}' (line {flow.source.line}, "
            f"source: {flow.source.source_type}) to LLM call at line {flow.sink.line}"
        )

        return Finding(
            rule_id=rule.id,
            message=message,
            severity=rule.severity,
            confidence=Confidence.HIGH,
            location=location,
            category=rule.category,
            cwe_id=rule.cwe_id,
            fix_suggestion=rule.fix_suggestion,
            references=rule.references,
        )
