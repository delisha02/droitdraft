"""Standalone evaluation toolkit for DroitDraft benchmarks."""

from .metrics import (
    compute_extraction_metrics,
    compute_generation_metrics,
    compute_retrieval_metrics,
    compute_system_metrics,
)
from .reporting import build_benchmark_report, format_report_markdown
from .schema import BenchmarkConfig, BenchmarkDatasetDefinition, EvaluationRecord

__all__ = [
    "BenchmarkConfig",
    "BenchmarkDatasetDefinition",
    "EvaluationRecord",
    "build_benchmark_report",
    "format_report_markdown",
    "compute_extraction_metrics",
    "compute_generation_metrics",
    "compute_retrieval_metrics",
    "compute_system_metrics",
]
