"""Tests for calibration metrics."""

import pytest

from atcb_eval.metrics import (
    compute_auroc,
    compute_brier,
    compute_ece,
    compute_mce,
    compute_reliability_diagram,
    compute_selective_accuracy,
)


class TestComputeECE:
    """Tests for Expected Calibration Error computation."""

    def test_perfect_calibration(self):
        """ECE should be 0 for perfectly calibrated predictions."""
        confidences = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        accuracies = [False, False, False, False, True, True, True, True, True, True]
        ece = compute_ece(confidences, accuracies, n_bins=10)
        assert ece < 0.15  # Allow some tolerance

    def test_overconfident(self):
        """ECE should be high for overconfident predictions."""
        confidences = [0.9] * 10
        accuracies = [True, False, False, False, False, False, False, False, False, False]
        ece = compute_ece(confidences, accuracies)
        assert ece > 0.5

    def test_empty_input(self):
        """ECE should be 0 for empty input."""
        assert compute_ece([], []) == 0.0

    def test_all_correct_high_confidence(self):
        """Low ECE when high confidence matches high accuracy."""
        confidences = [0.95, 0.92, 0.98, 0.91, 0.96]
        accuracies = [True, True, True, True, True]
        ece = compute_ece(confidences, accuracies)
        assert ece < 0.1


class TestComputeMCE:
    """Tests for Maximum Calibration Error computation."""

    def test_empty_input(self):
        """MCE should be 0 for empty input."""
        assert compute_mce([], []) == 0.0

    def test_worst_case(self):
        """MCE should capture the worst bin."""
        confidences = [0.1, 0.1, 0.9, 0.9]
        accuracies = [True, True, False, False]  # Inverted
        mce = compute_mce(confidences, accuracies)
        assert mce > 0.5


class TestComputeBrier:
    """Tests for Brier Score computation."""

    def test_perfect_predictions(self):
        """Brier should be 0 for perfect predictions."""
        confidences = [1.0, 1.0, 0.0, 0.0]
        accuracies = [True, True, False, False]
        assert compute_brier(confidences, accuracies) == 0.0

    def test_worst_predictions(self):
        """Brier should be 1 for worst predictions."""
        confidences = [0.0, 0.0, 1.0, 1.0]
        accuracies = [True, True, False, False]
        assert compute_brier(confidences, accuracies) == 1.0

    def test_empty_input(self):
        """Brier should be 0 for empty input."""
        assert compute_brier([], []) == 0.0


class TestComputeAUROC:
    """Tests for AUROC computation."""

    def test_perfect_separation(self):
        """AUROC should be 1 for perfect separation."""
        confidences = [0.9, 0.8, 0.7, 0.3, 0.2, 0.1]
        accuracies = [True, True, True, False, False, False]
        assert compute_auroc(confidences, accuracies) == 1.0

    def test_random_separation(self):
        """AUROC should be ~0.5 for random predictions."""
        # Equal confidence for all
        confidences = [0.5] * 10
        accuracies = [True, False, True, False, True, False, True, False, True, False]
        auroc = compute_auroc(confidences, accuracies)
        assert 0.4 <= auroc <= 0.6

    def test_few_samples(self):
        """AUROC should return 0.5 for too few samples."""
        assert compute_auroc([0.5], [True]) == 0.5

    def test_all_same_class(self):
        """AUROC should be 0.5 when all samples are same class."""
        confidences = [0.9, 0.8, 0.7]
        accuracies = [True, True, True]
        assert compute_auroc(confidences, accuracies) == 0.5


class TestComputeSelectiveAccuracy:
    """Tests for selective accuracy computation."""

    def test_high_threshold_filters(self):
        """High threshold should filter to accurate predictions."""
        confidences = [0.95, 0.85, 0.5, 0.3]
        accuracies = [True, True, False, False]
        acc = compute_selective_accuracy(confidences, accuracies, threshold=0.8)
        assert acc == 1.0

    def test_no_samples_above_threshold(self):
        """Should return 0 when no samples above threshold."""
        confidences = [0.1, 0.2, 0.3]
        accuracies = [True, True, True]
        assert compute_selective_accuracy(confidences, accuracies, threshold=0.9) == 0.0


class TestComputeReliabilityDiagram:
    """Tests for reliability diagram generation."""

    def test_returns_bins(self):
        """Should return bin data."""
        confidences = [0.1, 0.5, 0.9]
        accuracies = [False, True, True]
        result = compute_reliability_diagram(confidences, accuracies, n_bins=10)

        assert "bins" in result
        assert "n_samples" in result
        assert len(result["bins"]) == 10

    def test_bin_structure(self):
        """Each bin should have required fields."""
        confidences = [0.5]
        accuracies = [True]
        result = compute_reliability_diagram(confidences, accuracies)

        required_fields = [
            "bin_start",
            "bin_end",
            "bin_center",
            "avg_confidence",
            "avg_accuracy",
            "count",
            "gap",
        ]
        for bin_info in result["bins"]:
            for field in required_fields:
                assert field in bin_info


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
