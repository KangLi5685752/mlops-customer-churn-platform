"""Benchmark client-observed latency for the Azure-hosted churn API."""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import urlsplit, urlunsplit

import httpx

from scripts.benchmark_api_latency import compute_latency_statistics, repo_relative_path
from scripts.generate_sample_prediction_traffic import generate_payload
from src.utils.paths import REPORTS_DIR

AZURE_BENCHMARK_JSON_PATH = REPORTS_DIR / "azure_api_latency_benchmark.json"
AZURE_BENCHMARK_MARKDOWN_PATH = REPORTS_DIR / "azure_api_latency_benchmark.md"
DEFAULT_REQUESTS = 100
DEFAULT_WARMUP_REQUESTS = 5
DEFAULT_TIMEOUT_SECONDS = 15.0
READINESS_MAX_ATTEMPTS = 12
READINESS_RETRY_DELAY_SECONDS = 10.0
AZURE_BENCHMARK_NOTE = (
    "This is a client-observed synthetic benchmark of the Azure-hosted portfolio "
    "endpoint, not a production performance or SLA test. It is not a load test, "
    "stress test or pure model inference benchmark."
)
LATENCY_METRICS_SCOPE = (
    "client-observed end-to-end successful POST /predict requests only"
)
STARTUP_MEASUREMENT_SCOPE = "readiness and warm-up excluded from latency metrics"


class AzureBenchmarkError(RuntimeError):
    """Raised when hosted benchmark readiness or warm-up validation fails."""


def normalize_base_url(base_url: str) -> str:
    """Validate and normalize an Azure-hosted HTTPS base URL."""
    candidate = base_url.strip()
    parsed = urlsplit(candidate)

    if parsed.scheme.lower() != "https":
        raise ValueError("Azure-hosted benchmark base URL must use HTTPS.")
    if not parsed.netloc:
        raise ValueError("Azure-hosted benchmark base URL must include a host.")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("Azure-hosted benchmark base URL must not include credentials.")
    if parsed.query or parsed.fragment:
        raise ValueError(
            "Azure-hosted benchmark base URL must not include a query or fragment."
        )

    normalized_path = parsed.path.rstrip("/")
    return urlunsplit(("https", parsed.netloc, normalized_path, "", ""))


def endpoint_url(base_url: str, endpoint: str) -> str:
    """Append an API endpoint to a normalized base URL."""
    return f"{base_url}/{endpoint.lstrip('/')}"


def wait_for_readiness(
    client: httpx.Client,
    *,
    health_url: str,
    max_attempts: int = READINESS_MAX_ATTEMPTS,
    retry_delay_seconds: float = READINESS_RETRY_DELAY_SECONDS,
) -> int:
    """Wait until the hosted API satisfies the expected health contract."""
    for attempt in range(1, max_attempts + 1):
        failure: str
        try:
            response = client.get(health_url)
            payload = response.json()
            ready = (
                200 <= response.status_code < 300
                and isinstance(payload, dict)
                and payload.get("status") == "ok"
                and payload.get("model_artifact_exists") is True
            )
            if ready:
                print(f"Azure-hosted API readiness passed on attempt {attempt}.")
                return attempt

            if isinstance(payload, dict):
                failure = (
                    f"HTTP {response.status_code}, status={payload.get('status')!r}, "
                    "model_artifact_exists="
                    f"{payload.get('model_artifact_exists')!r}"
                )
            else:
                failure = f"HTTP {response.status_code} with non-object JSON"
        except (httpx.RequestError, ValueError) as exc:
            failure = f"{type(exc).__name__}: {exc}"

        print(
            f"Readiness attempt {attempt}/{max_attempts} not ready: {failure}",
            file=sys.stderr,
        )
        if attempt < max_attempts:
            time.sleep(retry_delay_seconds)

    raise AzureBenchmarkError(
        "Azure-hosted API readiness validation failed after the bounded retry limit."
    )


def run_warmup_requests(
    client: httpx.Client,
    *,
    predict_url: str,
    warmup_requests: int,
) -> None:
    """Send unmeasured sequential prediction requests before measurement."""
    for index in range(warmup_requests):
        try:
            response = client.post(predict_url, json=generate_payload(index))
        except httpx.RequestError as exc:
            raise AzureBenchmarkError(
                f"Warm-up request {index + 1} failed: {exc}"
            ) from exc

        if not 200 <= response.status_code < 300:
            raise AzureBenchmarkError(
                f"Warm-up request {index + 1} failed with HTTP "
                f"{response.status_code}: {response.text}"
            )


def measure_prediction_requests(
    client: httpx.Client,
    *,
    predict_url: str,
    n_requests: int,
    payload_index_offset: int,
) -> tuple[list[float], int]:
    """Measure sequential successful prediction requests and count failures."""
    latencies_ms: list[float] = []
    failed = 0

    for index in range(n_requests):
        payload = generate_payload(payload_index_offset + index)
        start_time = time.perf_counter()
        try:
            response = client.post(predict_url, json=payload)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            if 200 <= response.status_code < 300:
                latencies_ms.append(elapsed_ms)
            else:
                failed += 1
                print(
                    f"Measured request {index + 1} failed with HTTP "
                    f"{response.status_code}: {response.text}",
                    file=sys.stderr,
                )
        except httpx.RequestError as exc:
            failed += 1
            print(f"Measured request {index + 1} failed: {exc}", file=sys.stderr)

    return latencies_ms, failed


def build_azure_benchmark_result(
    *,
    base_url: str,
    health_url: str,
    predict_url: str,
    warmup_requests: int,
    readiness_attempts: int,
    latencies_ms: Sequence[float],
    requests_attempted: int,
    requests_failed: int,
) -> dict[str, Any]:
    """Build a serializable Azure-hosted benchmark result."""
    requests_succeeded = len(latencies_ms)
    statistics = compute_latency_statistics(
        latencies_ms=latencies_ms,
        requests_attempted=requests_attempted,
        requests_succeeded=requests_succeeded,
        requests_failed=requests_failed,
    )

    return {
        "benchmark_type": "azure_hosted_synthetic_api_latency",
        "benchmark_origin": "local_workstation",
        "transport": "HTTPS",
        "request_mode": "sequential",
        "note": AZURE_BENCHMARK_NOTE,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "base_url": base_url,
        "health_url": health_url,
        "predict_url": predict_url,
        "readiness_attempts": readiness_attempts,
        "warmup_requests": warmup_requests,
        "latency_metrics_scope": LATENCY_METRICS_SCOPE,
        "startup_measurement": STARTUP_MEASUREMENT_SCOPE,
        **statistics,
    }


def run_azure_latency_benchmark(
    *,
    base_url: str,
    n_requests: int,
    warmup_requests: int,
    timeout_seconds: float,
) -> dict[str, Any]:
    """Validate readiness, warm up and measure the Azure-hosted endpoint."""
    if n_requests < 1:
        raise ValueError("Number of measured requests must be at least 1.")
    if warmup_requests < 0:
        raise ValueError("Number of warm-up requests must be at least 0.")
    if timeout_seconds <= 0:
        raise ValueError("Timeout must be greater than 0.")

    normalized_base_url = normalize_base_url(base_url)
    health_url = endpoint_url(normalized_base_url, "health")
    predict_url = endpoint_url(normalized_base_url, "predict")

    with httpx.Client(timeout=timeout_seconds) as client:
        readiness_attempts = wait_for_readiness(client, health_url=health_url)
        run_warmup_requests(
            client,
            predict_url=predict_url,
            warmup_requests=warmup_requests,
        )
        latencies_ms, failed = measure_prediction_requests(
            client,
            predict_url=predict_url,
            n_requests=n_requests,
            payload_index_offset=warmup_requests,
        )

    return build_azure_benchmark_result(
        base_url=normalized_base_url,
        health_url=health_url,
        predict_url=predict_url,
        warmup_requests=warmup_requests,
        readiness_attempts=readiness_attempts,
        latencies_ms=latencies_ms,
        requests_attempted=n_requests,
        requests_failed=failed,
    )


def _format_latency(value: float | None) -> str:
    """Format an optional latency value for display."""
    return "n/a" if value is None else f"{value:.3f} ms"


def build_markdown_report(result: dict[str, Any]) -> str:
    """Build the Azure-hosted latency benchmark Markdown report."""
    success_rate_percent = result["success_rate"] * 100
    return "\n".join(
        [
            "# Azure-Hosted API Latency Benchmark",
            "",
            AZURE_BENCHMARK_NOTE,
            "",
            "- Benchmark type: Azure-hosted synthetic API latency",
            "- Benchmark origin: local workstation",
            "- Transport: HTTPS",
            "- Request mode: sequential",
            f"- Timestamp: `{result['timestamp_utc']}`",
            f"- Base URL: `{result['base_url']}`",
            f"- Prediction URL: `{result['predict_url']}`",
            f"- Readiness attempts: {result['readiness_attempts']}",
            f"- Unmeasured warm-up requests: {result['warmup_requests']}",
            f"- Requests attempted: {result['requests_attempted']}",
            f"- Requests succeeded: {result['requests_succeeded']}",
            f"- Requests failed: {result['requests_failed']}",
            f"- Success rate: {success_rate_percent:.2f}%",
            "",
            "Latency measurement begins after readiness validation and unmeasured "
            "warm-up requests. This does not completely characterize or eliminate "
            "all cold-start effects.",
            "",
            f"Latency scope: {LATENCY_METRICS_SCOPE}.",
            "The duration may include client-side handling, public network latency, "
            "HTTPS transport, Azure Container Apps ingress, FastAPI handling, "
            "preprocessing, model inference and response transmission.",
            "",
            "## Latency Metrics",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            f"| Average | {_format_latency(result['average_latency_ms'])} |",
            f"| p50 | {_format_latency(result['p50_latency_ms'])} |",
            f"| p95 | {_format_latency(result['p95_latency_ms'])} |",
            f"| Minimum | {_format_latency(result['min_latency_ms'])} |",
            f"| Maximum | {_format_latency(result['max_latency_ms'])} |",
            "",
        ]
    )


def write_reports(
    result: dict[str, Any],
    *,
    json_path: Path = AZURE_BENCHMARK_JSON_PATH,
    markdown_path: Path = AZURE_BENCHMARK_MARKDOWN_PATH,
) -> None:
    """Write separate Azure-hosted benchmark evidence files."""
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
    json_path: Path = AZURE_BENCHMARK_JSON_PATH,
    markdown_path: Path = AZURE_BENCHMARK_MARKDOWN_PATH,
) -> None:
    """Print a concise hosted benchmark summary."""
    print("Azure-hosted synthetic API latency benchmark completed")
    print(AZURE_BENCHMARK_NOTE)
    print(f"Prediction URL: {result['predict_url']}")
    print(f"Warm-up requests: {result['warmup_requests']}")
    print(f"Requests attempted: {result['requests_attempted']}")
    print(f"Requests succeeded: {result['requests_succeeded']}")
    print(f"Requests failed: {result['requests_failed']}")
    print(f"Success rate: {result['success_rate'] * 100:.2f}%")
    print(f"Average latency: {_format_latency(result['average_latency_ms'])}")
    print(f"p50 latency: {_format_latency(result['p50_latency_ms'])}")
    print(f"p95 latency: {_format_latency(result['p95_latency_ms'])}")
    print(f"JSON report: {repo_relative_path(json_path)}")
    print(f"Markdown report: {repo_relative_path(markdown_path)}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Run a client-observed Azure-hosted synthetic API latency benchmark. "
            "This is not a production performance or SLA test."
        )
    )
    parser.add_argument(
        "--base-url",
        required=True,
        help="Azure Container App HTTPS base URL, without /health or /predict.",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=DEFAULT_REQUESTS,
        help=f"Number of sequential measured requests. Defaults to {DEFAULT_REQUESTS}.",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=DEFAULT_WARMUP_REQUESTS,
        help=(
            "Number of unmeasured sequential warm-up requests. "
            f"Defaults to {DEFAULT_WARMUP_REQUESTS}."
        ),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Per-request timeout in seconds. Defaults to {DEFAULT_TIMEOUT_SECONDS:g}.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the Azure-hosted benchmark from the command line."""
    args = parse_args(argv)
    try:
        result = run_azure_latency_benchmark(
            base_url=args.base_url,
            n_requests=args.n,
            warmup_requests=args.warmup,
            timeout_seconds=args.timeout,
        )
    except ValueError as exc:
        print(f"Invalid arguments: {exc}", file=sys.stderr)
        return 2
    except AzureBenchmarkError as exc:
        print(f"Benchmark validation failed: {exc}", file=sys.stderr)
        return 1

    write_reports(result)
    print_summary(result)
    return 0 if result["requests_succeeded"] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
