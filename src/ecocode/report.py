"""Simple text report generator for the prototype."""

from __future__ import annotations

from typing import Any, Callable

from .profiler import profile_callable


def eco_report(func: Callable[..., Any], *args: Any, **kwargs: Any) -> str:
    """Generate a plain-text report for one function execution."""

    _, result = profile_callable(func, *args, **kwargs)
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