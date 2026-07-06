"""Generate synthetic local prediction traffic for the FastAPI churn API."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from src.utils.paths import REPORTS_DIR

DEFAULT_API_URL = "http://127.0.0.1:8000/predict"
SUMMARY_REPORT_PATH = REPORTS_DIR / "sample_prediction_traffic_summary.md"

BASE_PAYLOADS: list[dict[str, Any]] = [
    {
        "gender": "Female",
        "SeniorCitizen": 0,
        "Partner": "Yes",
        "Dependents": "No",
        "tenure": 12,
        "PhoneService": "Yes",
        "MultipleLines": "No",
        "InternetService": "DSL",
        "OnlineSecurity": "Yes",
        "OnlineBackup": "No",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 59.9,
        "TotalCharges": 718.8,
    },
    {
        "gender": "Male",
        "SeniorCitizen": 1,
        "Partner": "No",
        "Dependents": "No",
        "tenure": 3,
        "PhoneService": "Yes",
        "MultipleLines": "Yes",
        "InternetService": "Fiber optic",
        "OnlineSecurity": "No",
        "OnlineBackup": "No",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "Yes",
        "StreamingMovies": "Yes",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 95.4,
        "TotalCharges": 286.2,
    },
    {
        "gender": "Female",
        "SeniorCitizen": 0,
        "Partner": "Yes",
        "Dependents": "Yes",
        "tenure": 48,
        "PhoneService": "Yes",
        "MultipleLines": "No",
        "InternetService": "DSL",
        "OnlineSecurity": "Yes",
        "OnlineBackup": "Yes",
        "DeviceProtection": "Yes",
        "TechSupport": "Yes",
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": "Two year",
        "PaperlessBilling": "No",
        "PaymentMethod": "Credit card (automatic)",
        "MonthlyCharges": 64.2,
        "TotalCharges": 3081.6,
    },
    {
        "gender": "Male",
        "SeniorCitizen": 0,
        "Partner": "No",
        "Dependents": "No",
        "tenure": 18,
        "PhoneService": "Yes",
        "MultipleLines": "Yes",
        "InternetService": "Fiber optic",
        "OnlineSecurity": "No",
        "OnlineBackup": "Yes",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "Yes",
        "StreamingMovies": "No",
        "Contract": "One year",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Bank transfer (automatic)",
        "MonthlyCharges": 84.65,
        "TotalCharges": 1523.7,
    },
    {
        "gender": "Female",
        "SeniorCitizen": 0,
        "Partner": "No",
        "Dependents": "Yes",
        "tenure": 6,
        "PhoneService": "No",
        "MultipleLines": "No phone service",
        "InternetService": "DSL",
        "OnlineSecurity": "No",
        "OnlineBackup": "Yes",
        "DeviceProtection": "No",
        "TechSupport": "Yes",
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": "Month-to-month",
        "PaperlessBilling": "No",
        "PaymentMethod": "Mailed check",
        "MonthlyCharges": 35.4,
        "TotalCharges": 212.4,
    },
    {
        "gender": "Male",
        "SeniorCitizen": 0,
        "Partner": "Yes",
        "Dependents": "Yes",
        "tenure": 72,
        "PhoneService": "Yes",
        "MultipleLines": "No",
        "InternetService": "No",
        "OnlineSecurity": "No internet service",
        "OnlineBackup": "No internet service",
        "DeviceProtection": "No internet service",
        "TechSupport": "No internet service",
        "StreamingTV": "No internet service",
        "StreamingMovies": "No internet service",
        "Contract": "Two year",
        "PaperlessBilling": "No",
        "PaymentMethod": "Bank transfer (automatic)",
        "MonthlyCharges": 20.15,
        "TotalCharges": 1450.8,
    },
]


@dataclass(frozen=True)
class TrafficSummary:
    """Summary of a local synthetic traffic generation run."""

    api_url: str
    requests_attempted: int
    requests_succeeded: int
    requests_failed: int
    risk_label_counts: dict[str, int]


def generate_payload(index: int) -> dict[str, Any]:
    """Return a deterministic Telco-like payload for the given request index."""
    return dict(BASE_PAYLOADS[index % len(BASE_PAYLOADS)])


def generate_payloads(n_requests: int) -> list[dict[str, Any]]:
    """Generate deterministic synthetic Telco payloads."""
    if n_requests < 1:
        raise ValueError("Number of requests must be at least 1.")

    return [generate_payload(index) for index in range(n_requests)]


def summarize_risk_labels(responses: list[dict[str, Any]]) -> dict[str, int]:
    """Count risk labels from successful prediction responses."""
    counts = Counter(response.get("risk_label", "unknown") for response in responses)
    return dict(sorted(counts.items()))


def send_prediction_traffic(
    *,
    n_requests: int,
    api_url: str,
    timeout_seconds: float = 10.0,
) -> TrafficSummary:
    """Send synthetic payloads to the running FastAPI prediction endpoint."""
    payloads = generate_payloads(n_requests)
    successful_responses: list[dict[str, Any]] = []
    failed = 0

    try:
        with httpx.Client(timeout=timeout_seconds) as client:
            for payload in payloads:
                try:
                    response = client.post(api_url, json=payload)
                    response.raise_for_status()
                    successful_responses.append(response.json())
                except httpx.HTTPStatusError as exc:
                    failed += 1
                    print(
                        f"Request failed with status {exc.response.status_code}: "
                        f"{exc.response.text}",
                        file=sys.stderr,
                    )
                except httpx.RequestError as exc:
                    raise RuntimeError(
                        f"Could not reach API at {api_url}. Start the FastAPI app first "
                        "with `python -m uvicorn app.main:app --reload`."
                    ) from exc
    except RuntimeError:
        raise

    return TrafficSummary(
        api_url=api_url,
        requests_attempted=n_requests,
        requests_succeeded=len(successful_responses),
        requests_failed=failed,
        risk_label_counts=summarize_risk_labels(successful_responses),
    )


def build_summary_report(summary: TrafficSummary) -> str:
    """Build the Markdown summary written after sample traffic generation."""
    risk_label_lines = [
        f"- {label}: {count}" for label, count in summary.risk_label_counts.items()
    ]
    if not risk_label_lines:
        risk_label_lines = ["- none"]

    return "\n".join(
        [
            "# Sample Prediction Traffic Summary",
            "",
            f"- Timestamp: `{datetime.now(timezone.utc).isoformat()}`",
            f"- API URL: `{summary.api_url}`",
            f"- Requests attempted: {summary.requests_attempted}",
            f"- Requests succeeded: {summary.requests_succeeded}",
            f"- Requests failed: {summary.requests_failed}",
            "",
            "## Risk Label Counts",
            "",
            *risk_label_lines,
            "",
            "Detailed prediction events are written to `logs/predictions.jsonl`.",
            "`logs/predictions.jsonl` is excluded from Git.",
            "",
        ]
    )


def write_summary_report(
    summary: TrafficSummary,
    report_path: Path = SUMMARY_REPORT_PATH,
) -> None:
    """Write the sample traffic summary report."""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_summary_report(summary), encoding="utf-8")


def print_summary(summary: TrafficSummary, report_path: Path = SUMMARY_REPORT_PATH) -> None:
    """Print a concise command-line summary."""
    print("Sample prediction traffic completed")
    print(f"API URL: {summary.api_url}")
    print(f"Requests attempted: {summary.requests_attempted}")
    print(f"Requests succeeded: {summary.requests_succeeded}")
    print(f"Requests failed: {summary.requests_failed}")
    print(f"Risk label counts: {summary.risk_label_counts}")
    print("Detailed prediction events: logs/predictions.jsonl")
    print(f"Summary report: {report_path}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic local traffic for the Telco churn API."
    )
    parser.add_argument(
        "--n",
        type=int,
        default=30,
        help="Number of prediction requests to send. Defaults to 30.",
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_API_URL,
        help=f"Prediction endpoint URL. Defaults to {DEFAULT_API_URL}.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run sample prediction traffic generation from the command line."""
    args = parse_args(argv)

    try:
        summary = send_prediction_traffic(n_requests=args.n, api_url=args.url)
    except ValueError as exc:
        print(f"Invalid arguments: {exc}", file=sys.stderr)
        return 2
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    write_summary_report(summary)
    print_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
