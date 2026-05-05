"""Runtime profiling helpers for EcoCode."""

from __future__ import annotations

import functools
import os
import time
import tracemalloc
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, TypeVar

from .static_analysis import Suggestion, analyze_callable

try:
    import codecarbon  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    codecarbon = None

FuncT = TypeVar("FuncT", bound=Callable[..., Any])

CARBON_INTENSITY_ENV_VAR = "ECOCODE_CARBON_INTENSITY"
DEFAULT_GRID_CARBON_INTENSITY = 475.0


@dataclass(slots=True)
class CarbonResult:
    """Structured result returned by the profiler."""

    function_name: str
    execution_time_s: float
    peak_memory_mb: float
    cpu_time_s: float
    estimated_energy_kwh: float
    estimated_emissions_gco2: float
    carbon_intensity_gco2_per_kwh: float
    suggestions: list[Suggestion] = field(default_factory=list)

    def summary(self) -> str:
        suggestions = "; ".join(s.message for s in self.suggestions) or "No static suggestions."
        return (
            f"{self.function_name}: {self.estimated_emissions_gco2:.4f} gCO2e, "
            f"{self.execution_time_s:.4f}s, {self.peak_memory_mb:.2f} MB peak. "
            f"Suggestions: {suggestions}"
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _resolve_carbon_intensity(carbon_intensity: float | None) -> float:
    if carbon_intensity is not None:
        return carbon_intensity
    env_value = os.getenv(CARBON_INTENSITY_ENV_VAR)
    if env_value:
        return float(env_value)
    return DEFAULT_GRID_CARBON_INTENSITY


def get_runtime_config(carbon_intensity: float | None = None) -> dict[str, Any]:
    """Return the effective runtime configuration used by EcoCode."""

    env_value = os.getenv(CARBON_INTENSITY_ENV_VAR)
    if carbon_intensity is not None:
        carbon_intensity_source = "argument"
    elif env_value is not None:
        carbon_intensity_source = "environment"
    else:
        carbon_intensity_source = "default"

    return {
        "carbon_intensity": _resolve_carbon_intensity(carbon_intensity),
        "carbon_intensity_source": carbon_intensity_source,
        "carbon_intensity_env_var": CARBON_INTENSITY_ENV_VAR,
        "carbon_intensity_env_value": env_value,
        "default_grid_carbon_intensity": DEFAULT_GRID_CARBON_INTENSITY,
        "codecarbon_available": codecarbon is not None,
    }


def _estimate_energy_kwh(cpu_time_s: float, peak_memory_mb: float) -> float:
    cpu_power_watts = 35.0
    memory_power_watts_per_gb = 0.4
    memory_gb = peak_memory_mb / 1024.0
    power_watts = cpu_power_watts + (memory_gb * memory_power_watts_per_gb)
    return power_watts * cpu_time_s / 3_600_000.0


def profile_callable(
    func: Callable[..., Any],
    *args: Any,
    carbon_intensity: float | None = None,
    **kwargs: Any,
) -> tuple[Any, CarbonResult]:
    """Execute a callable and return both result and carbon estimate."""

    if codecarbon is not None:
        tracker = codecarbon.OfflineEmissionsTracker(country_iso_code="FRA", save_to_file=False)
        tracker.start()
    else:
        tracker = None

    tracemalloc.start()
    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    try:
        value = func(*args, **kwargs)
    finally:
        cpu_end = time.process_time()
        wall_end = time.perf_counter()
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        emissions = tracker.stop() if tracker is not None else None

    cpu_time_s = cpu_end - cpu_start
    execution_time_s = wall_end - wall_start
    peak_memory_mb = peak_bytes / (1024 * 1024)
    intensity = _resolve_carbon_intensity(carbon_intensity)
    energy_kwh = _estimate_energy_kwh(cpu_time_s=cpu_time_s, peak_memory_mb=peak_memory_mb)
    estimated_emissions_gco2 = (
        float(emissions) * 1000 if emissions is not None else energy_kwh * intensity
    )
    suggestions = analyze_callable(func)

    result = CarbonResult(
        function_name=func.__name__,
        execution_time_s=execution_time_s,
        peak_memory_mb=peak_memory_mb,
        cpu_time_s=cpu_time_s,
        estimated_energy_kwh=energy_kwh,
        estimated_emissions_gco2=estimated_emissions_gco2,
        carbon_intensity_gco2_per_kwh=intensity,
        suggestions=suggestions,
    )
    return value, result


def carbon_profiler(func: FuncT | None = None, *, carbon_intensity: float | None = None):
    """Decorator that profiles a function and prints a concise carbon summary."""

    def decorator(inner: FuncT) -> FuncT:
        @functools.wraps(inner)
        def wrapper(*args: Any, **kwargs: Any):
            value, result = profile_callable(
                inner,
                *args,
                carbon_intensity=carbon_intensity,
                **kwargs,
            )
            print(result.summary())
            return value

        return wrapper  # type: ignore[return-value]

    if func is None:
        return decorator
    return decorator(func)