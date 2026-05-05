"""Command line interface for EcoCode."""

from __future__ import annotations

import argparse
import ast
import importlib
from typing import Any

from .report import eco_report


def _load_callable(target: str):
    if ":" not in target:
        raise ValueError("Target must use the format module:function")

    module_name, function_name = target.split(":", maxsplit=1)
    module = importlib.import_module(module_name)
    func = getattr(module, function_name, None)
    if func is None or not callable(func):
        raise ValueError(f"Callable not found: {target}")
    return func


def _parse_cli_value(raw_value: str) -> Any:
    try:
        return ast.literal_eval(raw_value)
    except (SyntaxError, ValueError):
        return raw_value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="EcoCode command line interface")
    subparsers = parser.add_subparsers(dest="command", required=True)

    report_parser = subparsers.add_parser("report", help="Generate a report for one callable")
    report_parser.add_argument("target", help="Callable target in the form module:function")
    report_parser.add_argument(
        "--arg",
        action="append",
        default=[],
        help="Positional argument passed to the callable. Repeat the flag for multiple args.",
    )
    report_parser.add_argument(
        "--carbon-intensity",
        type=float,
        default=None,
        help="Carbon intensity in gCO2e/kWh used by the fallback estimator.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "report":
        func = _load_callable(args.target)
        call_args = [_parse_cli_value(value) for value in args.arg]
        report = eco_report(func, *call_args, carbon_intensity=args.carbon_intensity)
        print(report)
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())