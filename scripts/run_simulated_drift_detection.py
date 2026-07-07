"""Run simulated local drift detection from prediction logs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from src.monitoring.drift_detection import (
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    build_drift_report,
    load_prediction_events,
    prediction_events_to_dataframe,
    simulate_current_batch,
)
from src.utils.paths import PROJECT_ROOT

DEFAULT_LOG_PATH = PROJECT_ROOT / "logs" / "predictions.jsonl"
DEFAULT_OUTPUT_JSON = PROJECT_ROOT / "reports" / "drift_detection_results.json"
DEFAULT_OUTPUT_MD = PROJECT_ROOT / "reports" / "drift_detection_summary.md"


def build_markdown_summary(report: dict[str, Any]) -> str:
    """Build the Markdown drift detection summary."""
    numerical_rows = [
        "| Feature | Reference Mean | Current Mean | Difference | Percent Difference | Drift |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for feature, result in report["numerical_drift"].items():
        percentage = result["percentage_difference"]
        percentage_text = "n/a" if percentage is None else f"{percentage:.2%}"
        numerical_rows.append(
            "| "
            f"{feature} | "
            f"{result['reference_mean']} | "
            f"{result['current_mean']} | "
            f"{result['absolute_difference']} | "
            f"{percentage_text} | "
            f"{result['drift_flag']} |"
        )

    categorical_rows = [
        "| Feature | Max Proportion Difference | Drift |",
        "| --- | ---: | --- |",
    ]
    for feature, result in report["categorical_drift"].items():
        categorical_rows.append(
            "| "
            f"{feature} | "
            f"{result['max_absolute_proportion_difference']} | "
            f"{result['drift_flag']} |"
        )

    overall = "Drift detected" if report["overall_drift_detected"] else "No drift detected"

    return "\n".join(
        [
            "# Simulated Drift Detection Summary",
            "",
            f"- Timestamp: `{report['timestamp_utc']}`",
            f"- Reference records: {report['reference_record_count']}",
            f"- Simulated current records: {report['current_record_count']}",
            f"- Overall result: {overall}",
            "",
            "The current batch is simulated by applying controlled feature shifts to local prediction logs.",
            "",
            "## Numerical Drift",
            "",
            *numerical_rows,
            "",
            "## Categorical Drift",
            "",
            *categorical_rows,
            "",
            "## Limitations",
            "",
            "- Based on synthetic local prediction logs.",
            "- Not real production monitoring.",
            "- No ground-truth `Churn` labels are used.",
            "- Thresholds are simple demonstration thresholds, not validated alert thresholds.",
            "",
        ]
    )


def write_json_report(report: dict[str, Any], output_path: Path) -> None:
    """Write the drift report JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def write_markdown_summary(report: dict[str, Any], output_path: Path) -> None:
    """Write the drift report Markdown summary."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_markdown_summary(report), encoding="utf-8")


def run_drift_detection(
    *,
    log_path: Path,
    output_json: Path,
    output_md: Path,
    seed: int,
) -> dict[str, Any]:
    """Run the full simulated drift detection workflow."""
    events = load_prediction_events(log_path)
    if not events:
        raise ValueError(f"No valid prediction events found in {log_path}")

    reference_df = prediction_events_to_dataframe(events)
    if reference_df.empty:
        raise ValueError(f"No valid monitoring records found in {log_path}")

    current_df = simulate_current_batch(reference_df, random_seed=seed)
    report = build_drift_report(reference_df, current_df)
    write_json_report(report, output_json)
    write_markdown_summary(report, output_md)
    return report


def print_console_summary(report: dict[str, Any], output_json: Path, output_md: Path) -> None:
    """Print a concise command-line summary."""
    numerical_flags = {
        feature: result["drift_flag"]
        for feature, result in report["numerical_drift"].items()
    }
    categorical_flags = {
        feature: result["drift_flag"]
        for feature, result in report["categorical_drift"].items()
    }

    print("Simulated drift detection completed")
    print(f"Reference records: {report['reference_record_count']}")
    print(f"Simulated current records: {report['current_record_count']}")
    print(f"Numerical drift flags: {numerical_flags}")
    print(f"Categorical drift flags: {categorical_flags}")
    print(f"Overall drift detected: {report['overall_drift_detected']}")
    print(f"JSON report: {output_json}")
    print(f"Markdown summary: {output_md}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run simulated drift detection from local prediction logs."
    )
    parser.add_argument("--log-path", type=Path, default=DEFAULT_LOG_PATH)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run simulated drift detection from the command line."""
    args = parse_args(argv)

    try:
        report = run_drift_detection(
            log_path=args.log_path,
            output_json=args.output_json,
            output_md=args.output_md,
            seed=args.seed,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"Could not run drift detection: {exc}", file=sys.stderr)
        return 1

    print_console_summary(report, args.output_json, args.output_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
