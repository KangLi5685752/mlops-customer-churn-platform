"""Run a local synthetic latency benchmark against the FastAPI churn API."""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import httpx

from scripts.generate_sample_prediction_traffic import generate_payload
from src.utils.paths import PROJECT_ROOT, REPORTS_DIR

DEFAULT_API_URL = "http://127.0.0.1:8000/predict"
BENCHMARK_JSON_PATH = REPORTS_DIR / "api_latency_benchmark.json"
BENCHMARK_MARKDOWN_PATH = REPORTS_DIR / "api_latency_benchmark.md"
LOCAL_BENCHMARK_NOTE = (
    "This is a local synthetic benchmark, not a production performance test."
)


def _round_metric(value: float | None, digits: int = 3) -> float | None:
    """Round latency metrics while preserving missing values."""
    if value is None:
        return None
    return round(value, digits)


def percentile(values: Sequence[float], percentile_value: float) -> float | None:
    """Return a linearly interpolated percentile for a sequence of values."""
    if not values:
        return None
    if not 0 <= percentile_value <= 100:
        raise ValueError("Percentile must be between 0 and 100.")

    sorted_values = sorted(values)
    if len(sorted_values) == 1:
        return sorted_values[0]

    rank = (len(sorted_values) - 1) * (percentile_value / 100)
    lower_index = math.floor(rank)
    upper_index = math.ceil(rank)

    if lower_index == upper_index:
        return sorted_values[lower_index]

    lower_value = sorted_values[lower_index]
    upper_value = sorted_values[upper_index]
    weight = rank - lower_index
    return lower_value + (upper_value - lower_value) * weight


def compute_latency_statistics(
    *,
    latencies_ms: Sequence[float],
    requests_attempted: int,
    requests_succeeded: int,
    requests_failed: int,
) -> dict[str, float | int | None]:
    """Compute latency and success-rate metrics for a benchmark run."""
    average_latency = (
        sum(latencies_ms) / len(latencies_ms) if latencies_ms else None
    )
    success_rate = (
        requests_succeeded / requests_attempted if requests_attempted else 0.0
    )

    return {
        "requests_attempted": requests_attempted,
        "requests_succeeded": requests_succeeded,
        "requests_failed": requests_failed,
        "average_latency_ms": _round_metric(average_latency),
        "p50_latency_ms": _round_metric(percentile(latencies_ms, 50)),
        "p95_latency_ms": _round_metric(percentile(latencies_ms, 95)),
        "min_latency_ms": _round_metric(min(latencies_ms) if latencies_ms else None),
        "max_latency_ms": _round_metric(max(latencies_ms) if latencies_ms else None),
        "success_rate": round(success_rate, 4),
    }


def build_benchmark_result(
    *,
    api_url: str,
    latencies_ms: Sequence[float],
    requests_attempted: int,
    requests_failed: int,
) -> dict[str, Any]:
    """Build the serialisable benchmark result dictionary."""
    requests_succeeded = len(latencies_ms)
    statistics = compute_latency_statistics(
        latencies_ms=latencies_ms,
        requests_attempted=requests_attempted,
        requests_succeeded=requests_succeeded,
        requests_failed=requests_failed,
    )

    return {
        "benchmark_type": "local_synthetic_api_latency",
        "note": LOCAL_BENCHMARK_NOTE,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "api_url": api_url,
        "latency_metrics_scope": "successful requests only",
        **statistics,
    }


def run_latency_benchmark(
    *,
    n_requests: int,
    api_url: str,
    timeout_seconds: float,
) -> dict[str, Any]:
    """Send sequential synthetic requests and collect local latency metrics."""
    if n_requests < 1:
        raise ValueError("Number of requests must be at least 1.")
    if timeout_seconds <= 0:
        raise ValueError("Timeout must be greater than 0.")

    latencies_ms: list[float] = []
    failed = 0

    with httpx.Client(timeout=timeout_seconds) as client:
        for index in range(n_requests):
            payload = generate_payload(index)
            start_time = time.perf_counter()
            try:
                response = client.post(api_url, json=payload)
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                if 200 <= response.status_code < 300:
                    latencies_ms.append(elapsed_ms)
                else:
                    failed += 1
                    print(
                        f"Request {index + 1} failed with status "
                        f"{response.status_code}: {response.text}",
                        file=sys.stderr,
                    )
            except httpx.RequestError as exc:
                failed += 1
                print(f"Request {index + 1} failed: {exc}", file=sys.stderr)

    return build_benchmark_result(
        api_url=api_url,
        latencies_ms=latencies_ms,
        requests_attempted=n_requests,
        requests_failed=failed,
    )


def repo_relative_path(path: Path) -> str:
    """Return a repository-relative path when possible."""
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(path)


def build_markdown_report(result: dict[str, Any]) -> str:
    """Build the Markdown report for a local API latency benchmark."""
    success_rate_percent = result["success_rate"] * 100

    def format_latency(value: float | None) -> str:
        return "n/a" if value is None else f"{value:.3f} ms"

    return "\n".join(
        [
            "# API Latency Benchmark",
            "",
            LOCAL_BENCHMARK_NOTE,
            "",
            "- Benchmark type: local synthetic API latency",
            f"- Timestamp: `{result['timestamp_utc']}`",
            f"- API URL: `{result['api_url']}`",
            f"- Requests attempted: {result['requests_attempted']}",
            f"- Requests succeeded: {result['requests_succeeded']}",
            f"- Requests failed: {result['requests_failed']}",
            f"- Success rate: {success_rate_percent:.2f}%",
            "",
            "Latency metrics are calculated from successful requests only.",
            "",
            "## Latency Metrics",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            f"| Average | {format_latency(result['average_latency_ms'])} |",
            f"| p50 | {format_latency(result['p50_latency_ms'])} |",
            f"| p95 | {format_latency(result['p95_latency_ms'])} |",
            f"| Minimum | {format_latency(result['min_latency_ms'])} |",
            f"| Maximum | {format_latency(result['max_latency_ms'])} |",
            "",
        ]
    )


def write_reports(
    result: dict[str, Any],
    *,
    json_path: Path = BENCHMARK_JSON_PATH,
    markdown_path: Path = BENCHMARK_MARKDOWN_PATH,
) -> None:
    """Write benchmark results to JSON and Markdown files."""
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(build_markdown_report(result), encoding="utf-8")


def print_summary(
    result: dict[str, Any],
    *,
    json_path: Path = BENCHMARK_JSON_PATH,
    markdown_path: Path = BENCHMARK_MARKDOWN_PATH,
) -> None:
    """Print a concise command-line benchmark summary."""
    success_rate_percent = result["success_rate"] * 100

    def format_latency(value: float | None) -> str:
        return "n/a" if value is None else f"{value:.3f} ms"

    print("Local synthetic API latency benchmark completed")
    print(LOCAL_BENCHMARK_NOTE)
    print(f"API URL: {result['api_url']}")
    print(f"Requests attempted: {result['requests_attempted']}")
    print(f"Requests succeeded: {result['requests_succeeded']}")
    print(f"Requests failed: {result['requests_failed']}")
    print(f"Success rate: {success_rate_percent:.2f}%")
    print(f"Average latency: {format_latency(result['average_latency_ms'])}")
    print(f"p50 latency: {format_latency(result['p50_latency_ms'])}")
    print(f"p95 latency: {format_latency(result['p95_latency_ms'])}")
    print(f"JSON report: {repo_relative_path(json_path)}")
    print(f"Markdown report: {repo_relative_path(markdown_path)}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Run a local synthetic latency benchmark against the Telco churn API."
        )
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_API_URL,
        help=f"Prediction endpoint URL. Defaults to {DEFAULT_API_URL}.",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=100,
        help="Number of sequential prediction requests to send. Defaults to 100.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Per-request timeout in seconds. Defaults to 10.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the benchmark from the command line."""
    args = parse_args(argv)

    try:
        result = run_latency_benchmark(
            n_requests=args.n,
            api_url=args.url,
            timeout_seconds=args.timeout,
        )
    except ValueError as exc:
        print(f"Invalid arguments: {exc}", file=sys.stderr)
        return 2

    write_reports(result)
    print_summary(result)

    return 0 if result["requests_succeeded"] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
