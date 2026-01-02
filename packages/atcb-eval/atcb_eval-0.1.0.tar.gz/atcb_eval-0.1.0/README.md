# ATCB-Eval

[![PyPI version](https://badge.fury.io/py/atcb-eval.svg)](https://badge.fury.io/py/atcb-eval)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Agent Tool-Use Calibration Benchmark - Evaluate if AI agents know when they'll fail.**

---

## The Problem

Tool-using AI agents express confidence in their decisions, but can you trust that confidence? Our research reveals a disturbing pattern:

**Key Finding:** Agents exhibit an *inverse* accuracy-calibration relationship—**the better they perform, the worse they are at knowing their limitations.**

| Model | Accuracy | ECE | Insight |
|-------|----------|-----|---------|
| GPT-4o | 78.4% | 0.156 | High accuracy, poor calibration |
| Claude 3.5 | 76.2% | 0.148 | Similar pattern |
| Gemini 2.0 | 74.8% | 0.142 | Consistent across families |

This means a high-confidence prediction from a state-of-the-art agent may be *less* reliable than you think.

---

## Where This Fits in Your AI Pipeline

```
Agent Dev --> Tool Integration --> [CALIBRATION TEST] --> Deployment --> Monitoring
                                           ^
                                    YOU ARE HERE
```

**Pipeline Stage:** After tool integration, before deployment. Use ATCB-Eval to verify your agent knows when it might fail.

### The Calibration Problem

```
Agent says: "I'm 95% confident"
              |
              v
      Actually correct?
        /           \
    78% YES       22% NO  <-- Calibration gap
```

**The gap between confidence and accuracy is the calibration error.**

| Model | Accuracy | Avg Confidence | Gap |
|-------|----------|----------------|-----|
| GPT-4o | 78.4% | 82.1% | 3.7% overconfident |
| Claude 3.5 | 76.2% | 79.4% | 3.2% overconfident |
| Gemini 2.0 | 74.8% | 77.2% | 2.4% overconfident |

### ATCB Evaluation Flow

| Stage | What Happens |
|-------|--------------|
| **1. Input** | 500+ test cases across 6 categories |
| **2. Evaluate** | Agent selects tool + reports confidence |
| **3. Measure** | Compute ECE, AUROC, Brier Score |
| **4. Verdict** | ECE < 0.1 = Calibrated, else Needs work |

### When to Use This Library

| Scenario | Why You Need ATCB-Eval |
|----------|----------------------|
| Deploying agentic systems | Validate agents know when to abstain |
| Comparing models | Calibration differs across families |
| Safety-critical applications | High confidence ≠ high reliability |
| Agent self-monitoring | Build uncertainty-aware agents |
| Research | Benchmark calibration methods |

---

## Installation

```bash
pip install atcb-eval
```

With API client support:
```bash
pip install atcb-eval[openai]      # OpenAI models
pip install atcb-eval[anthropic]   # Anthropic models
pip install atcb-eval[google]      # Google models
pip install atcb-eval[all]         # All providers
```

For development:
```bash
pip install atcb-eval[dev]
```

---

## Quick Start (5 Minutes)

### Option 1: Command Line

```bash
# Run interactive demo (no API keys needed)
atcb-eval demo

# Evaluate a specific model
export OPENAI_API_KEY=your_key
atcb-eval run --model gpt-4o --n-cases 100 --output results.json
```

### Option 2: Python API

```python
from atcb_eval import ATCBBenchmark

# Initialize benchmark
benchmark = ATCBBenchmark()

# Evaluate a model
results = benchmark.evaluate(model="gpt-4o", n_cases=100)

# Print summary
print(f"Accuracy: {results.accuracy:.1%}")
print(f"ECE: {results.ece:.3f}")
print(f"AUROC: {results.auroc:.3f}")
print(f"Confidence gap: {results.confidence_when_correct - results.confidence_when_wrong:.3f}")
```

### Option 3: Quick Metrics Computation

```python
from atcb_eval import compute_ece, compute_auroc, compute_reliability_diagram

# Your agent's predictions
confidences = [0.9, 0.85, 0.7, 0.6, 0.95]
correct = [True, True, False, True, False]

# Compute calibration metrics
ece = compute_ece(confidences, correct)
auroc = compute_auroc(confidences, correct)

print(f"ECE: {ece:.3f}")  # Lower is better
print(f"AUROC: {auroc:.3f}")  # Higher is better

# Generate reliability diagram data
diagram_data = compute_reliability_diagram(confidences, correct)
for bin_info in diagram_data["bins"]:
    print(f"Conf: {bin_info['avg_confidence']:.2f}, Acc: {bin_info['avg_accuracy']:.2f}")
```

---

## Practitioner Tutorial: Agent Calibration Audit

This tutorial walks through evaluating whether your tool-using agent knows when it'll fail.

### Step 1: Understand the Test Categories

ATCB includes 6 categories designed to probe different failure modes:

| Category | % of Tests | What It Tests |
|----------|------------|---------------|
| **clear_match** | 35% | Unambiguous tool requirements |
| **ambiguous** | 20% | Multiple valid interpretations |
| **no_tool** | 15% | Should abstain (conversational) |
| **adversarial** | 15% | Should refuse (harmful requests) |
| **multi_step** | 10% | Requires reasoning |
| **edge_case** | 5% | Unusual/malformed inputs |

### Step 2: Run the Evaluation

```python
from atcb_eval import ATCBBenchmark

benchmark = ATCBBenchmark()

# Evaluate with multiple seeds for statistical significance
results = []
for seed in [42, 123, 456]:
    metrics = benchmark.evaluate("gpt-4o", n_cases=500, seed=seed)
    results.append(metrics)

# Compute mean and std
import numpy as np
ece_mean = np.mean([r.ece for r in results])
ece_std = np.std([r.ece for r in results])

print(f"ECE: {ece_mean:.3f} ± {ece_std:.3f}")
```

### Step 3: Analyze Category Breakdown

```python
# Get per-category analysis
breakdown = benchmark.get_category_breakdown("gpt-4o")

print("\nCategory Analysis:")
print("-" * 50)
for category, metrics in sorted(breakdown.items()):
    print(f"{category:15s} | Acc: {metrics.accuracy:.1%} | ECE: {metrics.ece:.3f} | AUROC: {metrics.auroc:.3f}")
```

Expected output:
```
Category Analysis:
--------------------------------------------------
adversarial     | Acc: 62.3% | ECE: 0.234 | AUROC: 0.612
ambiguous       | Acc: 71.5% | ECE: 0.178 | AUROC: 0.654
clear_match     | Acc: 89.2% | ECE: 0.089 | AUROC: 0.823
edge_case       | Acc: 58.1% | ECE: 0.312 | AUROC: 0.534
multi_step      | Acc: 68.4% | ECE: 0.198 | AUROC: 0.621
no_tool         | Acc: 74.3% | ECE: 0.156 | AUROC: 0.689
```

### Step 4: Interpret Results

| Metric | Good | Concerning | Action |
|--------|------|------------|--------|
| **ECE < 0.1** | Calibrated | > 0.15 | Consider post-hoc calibration |
| **AUROC > 0.8** | Confidence separates correct/wrong | < 0.6 | Confidence not useful |
| **Confidence gap > 0.2** | Self-aware | < 0.1 | Agent doesn't know its errors |

### Step 5: Compare Models

```python
# Compare multiple models
models = ["gpt-4o", "claude-3-5-sonnet-20241022", "gemini-2.0-flash"]
comparison = benchmark.compare_models(models, n_cases=100)

print("\nModel Comparison:")
print("-" * 70)
print(f"{'Model':<30} {'Accuracy':>10} {'ECE':>10} {'AUROC':>10}")
print("-" * 70)
for model, metrics in comparison.items():
    print(f"{model:<30} {metrics.accuracy:>10.1%} {metrics.ece:>10.3f} {metrics.auroc:>10.3f}")
```

---

## Understanding the Metrics

### Expected Calibration Error (ECE)

ECE measures the average gap between confidence and accuracy:

$$\text{ECE} = \sum_{b=1}^{B} \frac{|B_b|}{n} \left| \text{acc}(B_b) - \text{conf}(B_b) \right|$$

- **ECE = 0**: Perfectly calibrated
- **ECE = 0.1**: 10% average gap
- **ECE > 0.2**: Poorly calibrated

### AUROC (Confidence as Correctness Predictor)

AUROC measures how well confidence separates correct from incorrect predictions:

- **AUROC = 1.0**: Confidence perfectly predicts correctness
- **AUROC = 0.5**: Confidence is random
- **AUROC < 0.5**: Confidence is anti-correlated with correctness

### Selective Accuracy

Accuracy when only acting on high-confidence predictions:

```python
# Only act when confidence >= 0.9
selective_acc = results.selective_accuracy_90
print(f"Accuracy at 90% confidence threshold: {selective_acc:.1%}")
```

---

## API Reference

### Core Classes

```python
from atcb_eval import (
    # Main benchmark
    ATCBBenchmark,
    generate_test_cases,

    # Evaluator
    MultiModelEvaluator,

    # Data types
    ToolUseCase,
    AgentResponse,

    # Metrics
    CalibrationMetrics,
    CategoryMetrics,
    compute_ece,
    compute_mce,
    compute_brier,
    compute_auroc,
    compute_selective_accuracy,
    compute_reliability_diagram,
)
```

### ATCBBenchmark

```python
benchmark = ATCBBenchmark()

# Evaluate single model
metrics = benchmark.evaluate(
    model: str,              # Model identifier
    n_cases: int = 500,      # Number of test cases
    seed: int = 42,          # Random seed
    api_key: str = None,     # Optional API key
) -> CalibrationMetrics

# Compare multiple models
results = benchmark.compare_models(
    models: List[str],
    n_cases: int = 500,
    seed: int = 42,
) -> Dict[str, CalibrationMetrics]

# Get category breakdown
breakdown = benchmark.get_category_breakdown(model: str) -> Dict[str, CategoryMetrics]
```

### Supported Models

```python
from atcb_eval import MultiModelEvaluator

# List all supported models
models = MultiModelEvaluator.list_supported_models()
for name, config in models.items():
    print(f"{name}: {config['provider']}, logprobs={config['supports_logprobs']}")
```

Currently supported:
- **OpenAI**: gpt-4o, gpt-4o-mini, gpt-4-turbo
- **Anthropic**: claude-sonnet-4, claude-3-5-sonnet, claude-3-opus, claude-3-5-haiku
- **Google**: gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash

---

## Integration Examples

### With LangChain Agents

```python
from atcb_eval import compute_ece, compute_auroc
from langchain.agents import AgentExecutor

def evaluate_langchain_agent(agent: AgentExecutor, test_cases):
    confidences = []
    correct = []

    for case in test_cases:
        result = agent.invoke({"input": case.query})

        # Extract confidence from agent output
        confidence = extract_confidence(result)
        is_correct = check_correctness(result, case)

        confidences.append(confidence)
        correct.append(is_correct)

    return {
        "ece": compute_ece(confidences, correct),
        "auroc": compute_auroc(confidences, correct),
    }
```

### With MLOps Pipeline

```python
from atcb_eval import ATCBBenchmark

def pre_deployment_calibration_check(model_id: str) -> bool:
    """Gate deployment on calibration quality."""
    benchmark = ATCBBenchmark()
    metrics = benchmark.evaluate(model_id, n_cases=200)

    # Deployment criteria
    if metrics.ece > 0.15:
        raise ValueError(f"ECE too high: {metrics.ece:.3f} > 0.15")
    if metrics.auroc < 0.65:
        raise ValueError(f"AUROC too low: {metrics.auroc:.3f} < 0.65")

    return True
```

---

## Citation

```bibtex
@article{sinha2025atcb,
  title={Do Agents Know When They Will Fail? Benchmarking Tool-Use Calibration Across LLM Families},
  author={Sinha, Debu},
  journal={arXiv preprint},
  year={2025}
}
```

---

## Related Research

This library is part of a research program on **AI reliability under distribution shift**:

| Paper | Focus | Link |
|-------|-------|------|
| **The Semantic Illusion** | Embedding-based detection fails on RLHF | [arXiv:2512.15068](https://arxiv.org/abs/2512.15068) |
| **ATCB** | Agents don't know when they'll fail | This repo |
| **ConformalDrift** | Conformal guarantees collapse under shift | [GitHub](https://github.com/debu-sinha/conformaldrift) |
| **DRIFTBENCH** | RAG reliability degrades over time | [GitHub](https://github.com/debu-sinha/driftbench) |

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Contributing

Contributions welcome! Please see our [Contributing Guide](CONTRIBUTING.md).

**Author:** [Debu Sinha](https://github.com/debu-sinha)
