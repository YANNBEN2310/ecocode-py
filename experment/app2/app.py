import json
import os
import re
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


APP_CARBON_INTENSITY = float(os.getenv(CARBON_INTENSITY_ENV_VAR, "110"))
OUTPUT_DIR = PROJECT_ROOT / "experment" / "app2" / "output"


def load_documents() -> list[str]:
    return [
        "EcoCode helps developers reason about code efficiency and carbon-aware tradeoffs.",
        "This second experiment counts words and highlights repeated text patterns.",
        "Static analysis and runtime profiling complement each other in this demo.",
    ]


@carbon_profiler(carbon_intensity=APP_CARBON_INTENSITY)
def count_words_loop(documents: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for doc_index in range(len(documents)):
        tokens = re.findall(r"[a-zA-Z]+", documents[doc_index].lower())
        for token_index in range(len(tokens)):
            token = tokens[token_index]
            counts[token] = counts.get(token, 0) + 1
    return counts


def count_words_pythonic(documents: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for document in documents:
        for token in re.findall(r"[a-zA-Z]+", document.lower()):
            counts[token] = counts.get(token, 0) + 1
    return counts


def export_reports(documents: list[str]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    _, profiled_result = profile_callable(
        count_words_loop,
        documents,
        carbon_intensity=APP_CARBON_INTENSITY,
    )
    text_report = eco_report(
        count_words_loop,
        documents,
        carbon_intensity=APP_CARBON_INTENSITY,
    )
    html_report = render_html_report(profiled_result)
    comparison = eco_compare(
        count_words_loop,
        count_words_pythonic,
        documents,
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

    documents_literal = repr(load_documents())
    ecocode_cli([
        "config",
        "--carbon-intensity",
        str(APP_CARBON_INTENSITY),
        "--format",
        "json",
    ])
    ecocode_cli([
        "report",
        "experment.app2.app:count_words_loop",
        "--arg",
        documents_literal,
        "--carbon-intensity",
        str(APP_CARBON_INTENSITY),
        "--format",
        "html",
        "--output",
        str(OUTPUT_DIR / "cli-report.html"),
    ])
    ecocode_cli([
        "compare",
        "experment.app2.app:count_words_loop",
        "experment.app2.app:count_words_pythonic",
        "--arg",
        documents_literal,
        "--carbon-intensity",
        str(APP_CARBON_INTENSITY),
        "--format",
        "json",
    ])


def main() -> None:
    documents = load_documents()

    print("== EcoCode experiment app 2 ==")
    print(json.dumps(get_runtime_config(APP_CARBON_INTENSITY), indent=2))
    print()

    loop_counts = count_words_loop(documents)
    pythonic_counts, pythonic_metrics = profile_callable(
        count_words_pythonic,
        documents,
        carbon_intensity=APP_CARBON_INTENSITY,
    )

    print("Loop counts:")
    print(json.dumps(loop_counts, indent=2, sort_keys=True))
    print()
    print("Pythonic counts:")
    print(json.dumps(pythonic_counts, indent=2, sort_keys=True))
    print()
    print("Profiled pythonic implementation:")
    print(pythonic_metrics.summary())
    print()

    comparison = eco_compare(
        count_words_loop,
        count_words_pythonic,
        documents,
        carbon_intensity=APP_CARBON_INTENSITY,
    )
    print("Comparison:")
    print(comparison.summary())
    print()

    print("Text report from API:")
    print(eco_report(count_words_loop, documents, carbon_intensity=APP_CARBON_INTENSITY))
    print()

    export_reports(documents)
    run_cli_exports()

    print()
    print(f"Artifacts written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()