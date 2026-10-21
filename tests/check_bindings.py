"""Static binding audit, not a behavioral test or a replacement for pytest execution.

Run: python -m tests.check_bindings
Uses the Gherkin compiler and pytest-bdd 8.x's registered step contexts.
"""

from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path
from typing import Any

from tests.bdd import steps


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    contexts: list[Any] = []
    for value in vars(steps).values():
        wrapped = getattr(value, "__wrapped__", None)
        context = getattr(wrapped, "_pytest_bdd_step_context", None)
        if context is not None:
            contexts.append(context)
    assert contexts, "No registered step definitions"
    bindings: dict[tuple[str, str], str] = {}
    for source in (root / "tests/bdd").glob("test_*.py"):
        for node in ast.walk(ast.parse(source.read_text(encoding="utf-8"))):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                        if decorator.func.id == "scenario":
                            key = tuple(ast.literal_eval(arg) for arg in decorator.args)
                            assert len(key) == 2
                            assert key not in bindings, f"Duplicate scenario binding: {key}"
                            bindings[key] = node.name
    types = {"Context": "given", "Action": "when", "Outcome": "then"}
    cases = step_count = 0
    covered: set[tuple[str, str]] = set()
    fixtures = {"harness", "ui", "caplog", "monkeypatch"}
    # gherkin-official exposes an untyped public API; keep it at this tooling boundary.
    parser = importlib.import_module("gherkin.parser").Parser()
    compiler = importlib.import_module("gherkin.pickles.compiler").Compiler()
    for feature in sorted((root / "features").glob("*.feature")):
        document = parser.parse(feature.read_text(encoding="utf-8-sig"))
        document["uri"] = feature.name
        for case in compiler.compile(document):
            cases += 1
            key = (feature.name, case["name"])
            assert key in bindings, f"Scenario has no explicit test: {key}"
            covered.add(key)
            for step in case["steps"]:
                matches = [c for c in contexts if c.type == types[step["type"]]
                           and c.parser.is_matching(step["text"])]
                assert len(matches) == 1, f"Missing/ambiguous step: {step['text']} ({len(matches)})"
                context = matches[0]
                arguments = context.parser.parse_arguments(step["text"]) or {}
                parameters = inspect.signature(context.step_func).parameters
                assert set(parameters) <= fixtures | set(arguments), step["text"]
                step_count += 1
    assert covered == set(bindings), "Stale test binding to a removed Scenario"
    print(f"Binding audit: {len(covered)} scenarios/outlines, {cases} expanded cases, "
          f"{step_count} steps uniquely matched; fixture parameters resolved statically.")


if __name__ == "__main__":
    main()
