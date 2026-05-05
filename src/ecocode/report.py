"""Simple text report generator for the prototype."""

from __future__ import annotations

import html
from typing import Any, Callable

from .profiler import CarbonResult, profile_callable


def render_text_report(result: CarbonResult) -> str:
    """Render a CarbonResult as a plain-text report."""

    lines = [
        "EcoCode execution report",
        f"Function: {result.function_name}",
        f"Execution time: {result.execution_time_s:.6f} s",
        f"CPU time: {result.cpu_time_s:.6f} s",
        f"Peak memory: {result.peak_memory_mb:.4f} MB",
        f"Estimated energy: {result.estimated_energy_kwh:.10f} kWh",
        f"Estimated emissions: {result.estimated_emissions_gco2:.6f} gCO2e",
        f"Carbon intensity: {result.carbon_intensity_gco2_per_kwh:.2f} gCO2e/kWh",
        "Suggestions:",
    ]
    if result.suggestions:
        lines.extend(f"- {suggestion.message}" for suggestion in result.suggestions)
    else:
        lines.append("- No static suggestions.")
    return "\n".join(lines)


def render_html_report(result: CarbonResult) -> str:
    """Render a CarbonResult as a small standalone HTML report."""

    suggestion_items = "".join(
        f"<li>{html.escape(suggestion.message)}</li>" for suggestion in result.suggestions
    ) or "<li>No static suggestions.</li>"
    return f"""<!doctype html>
<html lang=\"en\">
    <head>
        <meta charset=\"utf-8\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
        <title>EcoCode report - {html.escape(result.function_name)}</title>
        <style>
            :root {{ color-scheme: light; }}
            body {{ font-family: Georgia, serif; margin: 2rem; background: #f4f1ea; color: #17211b; }}
            main {{ max-width: 840px; margin: 0 auto; background: #fffdf8; padding: 2rem; border: 1px solid #d9d2c3; }}
            h1, h2 {{ margin-top: 0; }}
            dl {{ display: grid; grid-template-columns: max-content 1fr; gap: 0.5rem 1rem; }}
            dt {{ font-weight: bold; }}
            .accent {{ color: #2f6b3b; }}
        </style>
    </head>
    <body>
        <main>
            <h1>EcoCode execution report</h1>
            <p class=\"accent\">Function: {html.escape(result.function_name)}</p>
            <dl>
                <dt>Execution time</dt><dd>{result.execution_time_s:.6f} s</dd>
                <dt>CPU time</dt><dd>{result.cpu_time_s:.6f} s</dd>
                <dt>Peak memory</dt><dd>{result.peak_memory_mb:.4f} MB</dd>
                <dt>Estimated energy</dt><dd>{result.estimated_energy_kwh:.10f} kWh</dd>
                <dt>Estimated emissions</dt><dd>{result.estimated_emissions_gco2:.6f} gCO2e</dd>
                <dt>Carbon intensity</dt><dd>{result.carbon_intensity_gco2_per_kwh:.2f} gCO2e/kWh</dd>
            </dl>
            <h2>Suggestions</h2>
            <ul>{suggestion_items}</ul>
        </main>
    </body>
</html>
"""


def eco_report(func: Callable[..., Any], *args: Any, **kwargs: Any) -> str:
    """Generate a plain-text report for one function execution."""

    _, result = profile_callable(func, *args, **kwargs)
    return render_text_report(result)