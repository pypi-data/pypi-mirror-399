"""Calibration metrics for ATCB benchmark."""

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class CalibrationMetrics:
    """Comprehensive calibration metrics for an agent.

    Attributes:
        model: Model identifier.
        n_samples: Number of samples evaluated.
        accuracy: Overall accuracy (correct tool selections / total).
        ece: Expected Calibration Error.
        mce: Maximum Calibration Error.
        brier_score: Brier score for probability predictions.
        auroc: Area under ROC curve (confidence as correctness predictor).
        selective_accuracy_90: Accuracy on samples with confidence >= 0.9.
        selective_accuracy_80: Accuracy on samples with confidence >= 0.8.
        selective_accuracy_70: Accuracy on samples with confidence >= 0.7.
        abstention_rate: Proportion of "none" tool selections.
        avg_confidence: Average verbalized confidence.
        confidence_when_correct: Average confidence on correct predictions.
        confidence_when_wrong: Average confidence on incorrect predictions.
        avg_latency_ms: Average response time in milliseconds.
    """

    model: str
    n_samples: int
    accuracy: float
    ece: float
    mce: float
    brier_score: float
    auroc: float
    selective_accuracy_90: float
    selective_accuracy_80: float
    selective_accuracy_70: float
    abstention_rate: float
    avg_confidence: float
    confidence_when_correct: float
    confidence_when_wrong: float
    avg_latency_ms: float

    def summary(self) -> str:
        """Generate a human-readable summary."""
        return (
            f"Model: {self.model}\n"
            f"Accuracy: {self.accuracy:.1%} (n={self.n_samples})\n"
            f"ECE: {self.ece:.3f}, MCE: {self.mce:.3f}\n"
            f"AUROC: {self.auroc:.3f}, Brier: {self.brier_score:.3f}\n"
            f"Confidence gap: {self.confidence_when_correct - self.confidence_when_wrong:.3f}\n"
            f"  (Correct: {self.confidence_when_correct:.2f}, Wrong: {self.confidence_when_wrong:.2f})"
        )


@dataclass
class CategoryMetrics:
    """Per-category calibration metrics.

    Attributes:
        category: Category name.
        n_samples: Number of samples in this category.
        accuracy: Category-specific accuracy.
        ece: Category-specific ECE.
        auroc: Category-specific AUROC.
        avg_confidence: Average confidence in this category.
    """

    category: str
    n_samples: int
    accuracy: float
    ece: float
    auroc: float
    avg_confidence: float


def compute_ece(
    confidences: List[float], accuracies: List[bool], n_bins: int = 10
) -> float:
    """Compute Expected Calibration Error.

    ECE measures the average gap between confidence and accuracy across bins.
    A perfectly calibrated model has ECE = 0.

    Args:
        confidences: List of confidence values (0-1).
        accuracies: List of boolean correctness indicators.
        n_bins: Number of bins for grouping confidences.

    Returns:
        ECE value (0-1, lower is better).

    Example:
        >>> confidences = [0.9, 0.8, 0.7, 0.6]
        >>> accuracies = [True, True, False, False]
        >>> ece = compute_ece(confidences, accuracies)
    """
    if len(confidences) == 0:
        return 0.0

    bin_boundaries = [i / n_bins for i in range(n_bins + 1)]
    ece = 0.0

    for i in range(n_bins):
        low, high = bin_boundaries[i], bin_boundaries[i + 1]
        mask = [(low <= c < high) for c in confidences]
        bin_count = sum(mask)

        if bin_count > 0:
            bin_conf = sum(c for c, m in zip(confidences, mask) if m) / bin_count
            bin_acc = sum(a for a, m in zip(accuracies, mask) if m) / bin_count
            ece += bin_count * abs(bin_conf - bin_acc)

    return ece / len(confidences)


def compute_mce(
    confidences: List[float], accuracies: List[bool], n_bins: int = 10
) -> float:
    """Compute Maximum Calibration Error.

    MCE measures the worst-case gap between confidence and accuracy.

    Args:
        confidences: List of confidence values (0-1).
        accuracies: List of boolean correctness indicators.
        n_bins: Number of bins for grouping confidences.

    Returns:
        MCE value (0-1, lower is better).
    """
    if len(confidences) == 0:
        return 0.0

    bin_boundaries = [i / n_bins for i in range(n_bins + 1)]
    max_error = 0.0

    for i in range(n_bins):
        low, high = bin_boundaries[i], bin_boundaries[i + 1]
        mask = [(low <= c < high) for c in confidences]
        bin_count = sum(mask)

        if bin_count > 0:
            bin_conf = sum(c for c, m in zip(confidences, mask) if m) / bin_count
            bin_acc = sum(a for a, m in zip(accuracies, mask) if m) / bin_count
            max_error = max(max_error, abs(bin_conf - bin_acc))

    return max_error


def compute_brier(confidences: List[float], accuracies: List[bool]) -> float:
    """Compute Brier Score.

    Brier score measures the mean squared error of probability predictions.

    Args:
        confidences: List of confidence values (0-1).
        accuracies: List of boolean correctness indicators.

    Returns:
        Brier score (0-1, lower is better).
    """
    if len(confidences) == 0:
        return 0.0
    return sum((c - float(a)) ** 2 for c, a in zip(confidences, accuracies)) / len(
        confidences
    )


def compute_auroc(confidences: List[float], accuracies: List[bool]) -> float:
    """Compute AUROC for confidence as a correctness predictor.

    AUROC measures how well confidence scores separate correct from incorrect
    predictions. A perfect model has AUROC = 1.0.

    Args:
        confidences: List of confidence values (0-1).
        accuracies: List of boolean correctness indicators.

    Returns:
        AUROC value (0.5-1.0, higher is better).
    """
    if len(confidences) < 2:
        return 0.5

    pairs = list(zip(confidences, accuracies))
    pairs.sort(key=lambda x: -x[0])

    n_pos = sum(accuracies)
    n_neg = len(accuracies) - n_pos

    if n_pos == 0 or n_neg == 0:
        return 0.5

    auc = 0.0
    tp = 0
    for _, acc in pairs:
        if acc:
            tp += 1
        else:
            auc += tp

    return auc / (n_pos * n_neg)


def compute_selective_accuracy(
    confidences: List[float], accuracies: List[bool], threshold: float
) -> float:
    """Compute accuracy on samples above a confidence threshold.

    This measures how reliable high-confidence predictions are.

    Args:
        confidences: List of confidence values (0-1).
        accuracies: List of boolean correctness indicators.
        threshold: Minimum confidence for inclusion.

    Returns:
        Accuracy on selected samples (0-1).
    """
    selected = [(c, a) for c, a in zip(confidences, accuracies) if c >= threshold]
    if len(selected) == 0:
        return 0.0
    return sum(a for _, a in selected) / len(selected)


def compute_reliability_diagram(
    confidences: List[float], accuracies: List[bool], n_bins: int = 10
) -> Dict:
    """Generate data for a reliability diagram.

    A reliability diagram plots average accuracy vs average confidence per bin.
    A perfectly calibrated model would show points on the diagonal.

    Args:
        confidences: List of confidence values (0-1).
        accuracies: List of boolean correctness indicators.
        n_bins: Number of bins.

    Returns:
        Dictionary with bin data for plotting.

    Example:
        >>> data = compute_reliability_diagram(confidences, accuracies)
        >>> for bin_info in data["bins"]:
        ...     print(f"Conf: {bin_info['avg_confidence']:.2f}, Acc: {bin_info['avg_accuracy']:.2f}")
    """
    bin_boundaries = [i / n_bins for i in range(n_bins + 1)]
    bins = []

    for i in range(n_bins):
        low, high = bin_boundaries[i], bin_boundaries[i + 1]
        mask = [(low <= c < high) for c in confidences]
        bin_count = sum(mask)

        if bin_count > 0:
            bin_conf = sum(c for c, m in zip(confidences, mask) if m) / bin_count
            bin_acc = sum(a for a, m in zip(accuracies, mask) if m) / bin_count
        else:
            bin_conf = (low + high) / 2
            bin_acc = 0.0

        bins.append(
            {
                "bin_start": low,
                "bin_end": high,
                "bin_center": (low + high) / 2,
                "avg_confidence": bin_conf,
                "avg_accuracy": bin_acc,
                "count": bin_count,
                "gap": bin_conf - bin_acc,
            }
        )

    return {"bins": bins, "n_samples": len(confidences)}


def compute_all_metrics(model: str, responses: List) -> CalibrationMetrics:
    """Compute all calibration metrics from a list of agent responses.

    Args:
        model: Model identifier.
        responses: List of AgentResponse objects.

    Returns:
        CalibrationMetrics with all computed values.
    """
    confidences = [r.verbalized_confidence for r in responses]
    accuracies = [r.is_correct for r in responses]
    latencies = [r.latency_ms for r in responses]

    correct_conf = [r.verbalized_confidence for r in responses if r.is_correct]
    wrong_conf = [r.verbalized_confidence for r in responses if not r.is_correct]

    return CalibrationMetrics(
        model=model,
        n_samples=len(responses),
        accuracy=sum(accuracies) / len(accuracies) if accuracies else 0.0,
        ece=compute_ece(confidences, accuracies),
        mce=compute_mce(confidences, accuracies),
        brier_score=compute_brier(confidences, accuracies),
        auroc=compute_auroc(confidences, accuracies),
        selective_accuracy_90=compute_selective_accuracy(confidences, accuracies, 0.9),
        selective_accuracy_80=compute_selective_accuracy(confidences, accuracies, 0.8),
        selective_accuracy_70=compute_selective_accuracy(confidences, accuracies, 0.7),
        abstention_rate=(
            sum(1 for r in responses if r.selected_tool == "none") / len(responses)
        ),
        avg_confidence=sum(confidences) / len(confidences) if confidences else 0.0,
        confidence_when_correct=(
            sum(correct_conf) / len(correct_conf) if correct_conf else 0.0
        ),
        confidence_when_wrong=(
            sum(wrong_conf) / len(wrong_conf) if wrong_conf else 0.0
        ),
        avg_latency_ms=sum(latencies) / len(latencies) if latencies else 0.0,
    )
