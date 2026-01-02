"""Command-line interface for ATCB benchmark."""

import argparse
import json
import sys
from pathlib import Path


def run_demo():
    """Run a quick demo of the benchmark."""
    from .benchmark import ATCBBenchmark

    print("=" * 60)
    print("  ATCB Demo - Agent Tool-Use Calibration Benchmark")
    print("=" * 60)
    print()
    print("Running evaluation with mock responses (no API keys needed)...")
    print()

    benchmark = ATCBBenchmark()
    metrics = benchmark.evaluate("mock-model", n_cases=50, seed=42)

    print()
    print("=" * 60)
    print("  Results")
    print("=" * 60)
    print(metrics.summary())
    print()
    print("Category breakdown:")

    breakdown = benchmark.get_category_breakdown("mock-model")
    for cat, cat_metrics in sorted(breakdown.items()):
        print(f"  {cat}: Acc={cat_metrics.accuracy:.1%}, ECE={cat_metrics.ece:.3f}")


def run_eval(args):
    """Run full evaluation."""
    from .benchmark import ATCBBenchmark

    print("=" * 60)
    print("  ATCB - Agent Tool-Use Calibration Benchmark")
    print("=" * 60)
    print()
    print(f"Model: {args.model}")
    print(f"Test cases: {args.n_cases}")
    print(f"Seed: {args.seed}")
    print()

    benchmark = ATCBBenchmark()
    metrics = benchmark.evaluate(args.model, n_cases=args.n_cases, seed=args.seed)

    print()
    print("=" * 60)
    print("  Results")
    print("=" * 60)
    print(metrics.summary())

    # Save results if output specified
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        results = {
            "model": args.model,
            "n_cases": args.n_cases,
            "seed": args.seed,
            "metrics": {
                "accuracy": metrics.accuracy,
                "ece": metrics.ece,
                "mce": metrics.mce,
                "brier_score": metrics.brier_score,
                "auroc": metrics.auroc,
                "selective_accuracy_90": metrics.selective_accuracy_90,
                "avg_confidence": metrics.avg_confidence,
                "confidence_when_correct": metrics.confidence_when_correct,
                "confidence_when_wrong": metrics.confidence_when_wrong,
            },
        }

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\nResults saved to: {output_path}")


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="ATCB - Agent Tool-Use Calibration Benchmark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  atcb-eval demo                    Run quick demo with mock responses
  atcb-eval run --model gpt-4o     Evaluate GPT-4o
  atcb-eval run --model gpt-4o --n-cases 100 --output results.json

For more information, visit: https://github.com/debu-sinha/atcb-benchmark
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run quick demo")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run full evaluation")
    run_parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="Model to evaluate (default: gpt-4o-mini)",
    )
    run_parser.add_argument(
        "--n-cases",
        type=int,
        default=500,
        help="Number of test cases (default: 500)",
    )
    run_parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default: 42)",
    )
    run_parser.add_argument(
        "--output",
        "-o",
        help="Output file for results (JSON)",
    )

    args = parser.parse_args()

    if args.command == "demo":
        run_demo()
    elif args.command == "run":
        run_eval(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
