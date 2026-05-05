"""Public package API for EcoCode."""

from .compare import eco_compare
from .profiler import carbon_profiler, profile_callable
from .report import eco_report

__all__ = ["carbon_profiler", "eco_compare", "eco_report", "profile_callable"]