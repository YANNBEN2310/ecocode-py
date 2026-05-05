import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

try:
    from ecocode import (
        CARBON_INTENSITY_ENV_VAR,
        carbon_profiler,
        eco_compare,
        eco_report,
        get_runtime_config,
        profile_callable,
    )
    from ecocode.cli import main as ecocode_cli
    from ecocode.report import render_html_report
except ModuleNotFoundError:
    sys.path.insert(0, str(PROJECT_ROOT))
    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from ecocode import (
        CARBON_INTENSITY_ENV_VAR,
        carbon_profiler,
        eco_compare,
        eco_report,
        get_runtime_config,
        profile_callable,
    )
    from ecocode.cli import main as ecocode_cli
    from ecocode.report import render_html_report


APP_CARBON_INTENSITY = float(os.getenv(CARBON_INTENSITY_ENV_VAR, "95"))
OUTPUT_DIR = PROJECT_ROOT / "experment" / "app1" / "output"


def load_orders() -> list[dict[str, object]]:
    return [
        {"customer": "Alice", "items": [12.5, 4.0, 8.0], "country": "FR"},
        {"customer": "Bob", "items": [3.0, 9.5], "country": "FR"},
        {"customer": "Alice", "items": [6.5], "country": "FR"},
        {"customer": "Chloe", "items": [22.0, 5.5, 3.5], "country": "BE"},
    ]


@carbon_profiler(carbon_intensity=APP_CARBON_INTENSITY)
def summarize_orders_loop(orders: list[dict[str, object]]) -> dict[str, float]:
    totals: dict[str, float] = {}
    for index in range(len(orders)):
        order = orders[index]
        customer = str(order["customer"])
        items = order["items"]
        order_total = 0.0
        for item_index in range(len(items)):
            order_total += float(items[item_index])
        totals[customer] = totals.get(customer, 0.0) + order_total
    return totals


def summarize_orders_builtin(orders: list[dict[str, object]]) -> dict[str, float]:
    totals: dict[str, float] = {}
    for order in orders:
        customer = str(order["customer"])
        order_total = sum(float(item) for item in order["items"])
        totals[customer] = totals.get(customer, 0.0) + order_total
    return totals


def export_reports(orders: list[dict[str, object]]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    _, profiled_result = profile_callable(
        summarize_orders_loop,
        orders,
        carbon_intensity=APP_CARBON_INTENSITY,
    )
    text_report = eco_report(
        summarize_orders_loop,
        orders,
        carbon_intensity=APP_CARBON_INTENSITY,
    )
    html_report = render_html_report(profiled_result)
    comparison = eco_compare(
        summarize_orders_loop,
        summarize_orders_builtin,
        orders,
        carbon_intensity=APP_CARBON_INTENSITY,
    )

    (OUTPUT_DIR / "api-report.txt").write_text(text_report, encoding="utf-8")
    (OUTPUT_DIR / "api-report.html").write_text(html_report, encoding="utf-8")
    (OUTPUT_DIR / "comparison.json").write_text(
        json.dumps(comparison.to_dict(), indent=2),
        encoding="utf-8",
    )


def run_cli_exports() -> None:
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    orders_literal = repr(load_orders())
    ecocode_cli([
        "config",
        "--carbon-intensity",
        str(APP_CARBON_INTENSITY),
        "--format",
        "json",
    ])
    ecocode_cli([
        "report",
        "experment.app1.app:summarize_orders_loop",
        "--arg",
        orders_literal,
        "--carbon-intensity",
        str(APP_CARBON_INTENSITY),
        "--format",
        "html",
        "--output",
        str(OUTPUT_DIR / "cli-report.html"),
    ])
    ecocode_cli([
        "compare",
        "experment.app1.app:summarize_orders_loop",
        "experment.app1.app:summarize_orders_builtin",
        "--arg",
        orders_literal,
        "--carbon-intensity",
        str(APP_CARBON_INTENSITY),
        "--format",
        "json",
    ])


def main() -> None:
    orders = load_orders()

    print("== EcoCode experiment app 1 ==")
    print(json.dumps(get_runtime_config(APP_CARBON_INTENSITY), indent=2))
    print()

    loop_summary = summarize_orders_loop(orders)
    builtin_summary, builtin_metrics = profile_callable(
        summarize_orders_builtin,
        orders,
        carbon_intensity=APP_CARBON_INTENSITY,
    )

    print("Loop summary:")
    print(json.dumps(loop_summary, indent=2))
    print()
    print("Builtin summary:")
    print(json.dumps(builtin_summary, indent=2))
    print()
    print("Profiled builtin implementation:")
    print(builtin_metrics.summary())
    print()

    comparison = eco_compare(
        summarize_orders_loop,
        summarize_orders_builtin,
        orders,
        carbon_intensity=APP_CARBON_INTENSITY,
    )
    print("Comparison:")
    print(comparison.summary())
    print()

    print("Text report from API:")
    print(eco_report(summarize_orders_loop, orders, carbon_intensity=APP_CARBON_INTENSITY))
    print()

    export_reports(orders)
    run_cli_exports()

    print()
    print(f"Artifacts written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()