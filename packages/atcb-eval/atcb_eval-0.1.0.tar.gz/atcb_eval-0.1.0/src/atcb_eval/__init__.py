"""
ATCB-Eval: Agent Tool-Use Calibration Benchmark.

This package provides tools for evaluating whether AI agents know when they'll fail.
The core insight: agents exhibit an *inverse* accuracy-calibration relationship—
the better they perform, the worse they are at knowing their limitations.

Where This Fits in Your AI Pipeline:
    Agent Development → **CALIBRATION TESTING WITH ATCB** → Deployment → Monitoring

Key Features:
    - Multi-model evaluation (GPT-4, Claude, Gemini, Llama)
    - 500+ diverse test cases across 6 difficulty categories
    - Standard calibration metrics (ECE, MCE, Brier Score, AUROC)
    - Reliability diagram generation
    - Verbalized vs token-probability confidence comparison

Quick Start:
    >>> from atcb_eval import ATCBBenchmark, CalibrationMetrics
    >>> benchmark = ATCBBenchmark()
    >>> results = benchmark.evaluate(model="gpt-4o", n_cases=100)
    >>> print(f"Accuracy: {results.accuracy:.1%}, ECE: {results.ece:.3f}")

When to Use This Library:
    - Before deploying tool-using agents
    - To compare calibration across model families
    - To identify which task categories cause miscalibration
    - For AI safety research on agent self-knowledge

For more details, see: https://github.com/debu-sinha/atcb-benchmark
"""

__version__ = "0.1.0"
__author__ = "Debu Sinha"
__email__ = "debusinha2009@gmail.com"

from .benchmark import ATCBBenchmark, generate_test_cases
from .evaluator import MultiModelEvaluator
from .metrics import (
    CalibrationMetrics,
    CategoryMetrics,
    compute_auroc,
    compute_brier,
    compute_ece,
    compute_mce,
    compute_reliability_diagram,
    compute_selective_accuracy,
)
from .types import AgentResponse, ToolUseCase

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    # Main benchmark
    "ATCBBenchmark",
    "generate_test_cases",
    # Evaluator
    "MultiModelEvaluator",
    # Data types
    "ToolUseCase",
    "AgentResponse",
    # Metrics
    "CalibrationMetrics",
    "CategoryMetrics",
    "compute_ece",
    "compute_mce",
    "compute_brier",
    "compute_auroc",
    "compute_selective_accuracy",
    "compute_reliability_diagram",
]
