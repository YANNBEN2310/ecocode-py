"""Utilities to compare multiple implementations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .profiler import CarbonResult, profile_callable


@dataclass(slots=True)
class ComparisonResult:
    baseline: CarbonResult
    candidate: CarbonResult

    @property
    def better_function_name(self) -> str:
        if self.baseline.estimated_emissions_gco2 <= self.candidate.estimated_emissions_gco2:
            return self.baseline.function_name
        return self.candidate.function_name

    @property
    def delta_gco2(self) -> float:
        return self.candidate.estimated_emissions_gco2 - self.baseline.estimated_emissions_gco2

    def summary(self) -> str:
        return (
            f"Best implementation: {self.better_function_name}. "
            f"Delta: {self.delta_gco2:.4f} gCO2e "
            f"({self.baseline.function_name} vs {self.candidate.function_name})."
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "baseline": self.baseline.to_dict(),
            "candidate": self.candidate.to_dict(),
            "better_function_name": self.better_function_name,
            "delta_gco2": self.delta_gco2,
            "summary": self.summary(),
        }


def eco_compare(
    baseline: Callable[..., Any],
    candidate: Callable[..., Any],
    *args: Any,
    carbon_intensity: float | None = None,
    **kwargs: Any,
) -> ComparisonResult:
    """Run two implementations against the same inputs."""

    _, baseline_result = profile_callable(
        baseline,
        *args,
        carbon_intensity=carbon_intensity,
        **kwargs,
    )
    _, candidate_result = profile_callable(
        candidate,
        *args,
        carbon_intensity=carbon_intensity,
        **kwargs,
    )
    return ComparisonResult(baseline=baseline_result, candidate=candidate_result)