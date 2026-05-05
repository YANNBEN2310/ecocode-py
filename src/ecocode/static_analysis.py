"""Static rules that suggest greener Python patterns."""

from __future__ import annotations

import ast
import inspect
import textwrap
from dataclasses import dataclass
from typing import Callable


@dataclass(slots=True)
class Suggestion:
    """A lightweight recommendation extracted from the AST."""

    rule_id: str
    message: str
    line: int | None = None


class _EcoVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.suggestions: list[Suggestion] = []

    def visit_For(self, node: ast.For) -> None:  # noqa: N802
        iterator = node.iter
        if (
            isinstance(iterator, ast.Call)
            and isinstance(iterator.func, ast.Name)
            and iterator.func.id == "range"
            and len(iterator.args) == 1
            and isinstance(iterator.args[0], ast.Call)
            and isinstance(iterator.args[0].func, ast.Name)
            and iterator.args[0].func.id == "len"
        ):
            self.suggestions.append(
                Suggestion(
                    rule_id="loop-range-len",
                    message="Prefer iterating directly on the collection instead of range(len(...)) when indexing is not required.",
                    line=node.lineno,
                )
            )
        self.generic_visit(node)

    def visit_ListComp(self, node: ast.ListComp) -> None:  # noqa: N802
        if isinstance(node.elt, ast.Name):
            self.suggestions.append(
                Suggestion(
                    rule_id="listcomp-identity",
                    message="An identity list comprehension may allocate unnecessarily. Consider reusing the iterable or a generator.",
                    line=node.lineno,
                )
            )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "sum"
            and node.args
            and isinstance(node.args[0], ast.ListComp)
        ):
            self.suggestions.append(
                Suggestion(
                    rule_id="sum-listcomp",
                    message="sum(...) over a list comprehension builds an intermediate list. Prefer a generator expression.",
                    line=node.lineno,
                )
            )
        self.generic_visit(node)


def analyze_callable(func: Callable[..., object]) -> list[Suggestion]:
    """Analyze a callable and return simple optimization suggestions."""

    try:
        source = inspect.getsource(func)
    except (OSError, TypeError):
        return []

    tree = ast.parse(textwrap.dedent(source))
    visitor = _EcoVisitor()
    visitor.visit(tree)
    return visitor.suggestions