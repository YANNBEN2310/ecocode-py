"""Public package API for EcoCode."""

from .compare import eco_compare
from .profiler import (
	CARBON_INTENSITY_ENV_VAR,
	DEFAULT_GRID_CARBON_INTENSITY,
	carbon_profiler,
	profile_callable,
)
from .report import eco_report

__all__ = [
	"CARBON_INTENSITY_ENV_VAR",
	"DEFAULT_GRID_CARBON_INTENSITY",
	"carbon_profiler",
	"eco_compare",
	"eco_report",
	"profile_callable",
]