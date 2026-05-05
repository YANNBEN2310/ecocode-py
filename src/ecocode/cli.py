"""Command line interface for EcoCode."""

from __future__ import annotations

import argparse
import ast
import importlib
import json
from pathlib import Path
from typing import Any

from .compare import eco_compare
from .profiler import profile_callable
from .report import eco_report, render_html_report, render_text_report


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


def _emit_output(content: str, output_path: str | None) -> None:
    if output_path is None:
        print(content)
        return

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    print(f"Wrote report to {target}")


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
    report_parser.add_argument(
        "--format",
        choices=("text", "json", "html"),
        default="text",
        help="Output format.",
    )
    report_parser.add_argument(
        "--output",
        default=None,
        help="Optional file path where the rendered report will be written.",
    )

    compare_parser = subparsers.add_parser("compare", help="Compare two callables with the same inputs")
    compare_parser.add_argument("baseline", help="Baseline callable in the form module:function")
    compare_parser.add_argument("candidate", help="Candidate callable in the form module:function")
    compare_parser.add_argument(
        "--arg",
        action="append",
        default=[],
        help="Positional argument passed to both callables. Repeat the flag for multiple args.",
    )
    compare_parser.add_argument(
        "--carbon-intensity",
        type=float,
        default=None,
        help="Carbon intensity in gCO2e/kWh used by the fallback estimator.",
    )
    compare_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "report":
        func = _load_callable(args.target)
        call_args = [_parse_cli_value(value) for value in args.arg]
        if args.format == "json":
            _, result = profile_callable(func, *call_args, carbon_intensity=args.carbon_intensity)
            _emit_output(json.dumps(result.to_dict(), indent=2), args.output)
        elif args.format == "html":
            _, result = profile_callable(func, *call_args, carbon_intensity=args.carbon_intensity)
            _emit_output(render_html_report(result), args.output)
        else:
            report = eco_report(func, *call_args, carbon_intensity=args.carbon_intensity)
            _emit_output(report, args.output)
        return 0

    if args.command == "compare":
        baseline = _load_callable(args.baseline)
        candidate = _load_callable(args.candidate)
        call_args = [_parse_cli_value(value) for value in args.arg]
        comparison = eco_compare(
            baseline,
            candidate,
            *call_args,
            carbon_intensity=args.carbon_intensity,
        )
        if args.format == "json":
            print(json.dumps(comparison.to_dict(), indent=2))
        else:
            print(comparison.summary())
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())