import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.benchmark_api_latency import (
    BENCHMARK_JSON_PATH,
    BENCHMARK_MARKDOWN_PATH,
)
from scripts.benchmark_azure_api_latency import (
    AZURE_BENCHMARK_JSON_PATH,
    AZURE_BENCHMARK_MARKDOWN_PATH,
    AZURE_BENCHMARK_NOTE,
    LATENCY_METRICS_SCOPE,
    STARTUP_MEASUREMENT_SCOPE,
    build_azure_benchmark_result,
    build_markdown_report,
    normalize_base_url,
)


def make_result() -> dict:
    return build_azure_benchmark_result(
        base_url="https://example.azurecontainerapps.io",
        health_url="https://example.azurecontainerapps.io/health",
        predict_url="https://example.azurecontainerapps.io/predict",
        warmup_requests=5,
        readiness_attempts=2,
        latencies_ms=[10.0, 20.0, 30.0, 40.0],
        requests_attempted=5,
        requests_failed=1,
    )


def test_hosted_result_metadata_is_distinct_from_local_benchmark() -> None:
    result = make_result()

    assert result["benchmark_type"] == "azure_hosted_synthetic_api_latency"
    assert result["benchmark_type"] != "local_synthetic_api_latency"
    assert result["benchmark_origin"] == "local_workstation"
    assert result["transport"] == "HTTPS"
    assert result["request_mode"] == "sequential"
    assert result["note"] == AZURE_BENCHMARK_NOTE


def test_markdown_report_states_hosted_client_observed_scope() -> None:
    report = build_markdown_report(make_result())

    assert "Azure-Hosted API Latency Benchmark" in report
    assert "client-observed" in report
    assert "synthetic" in report
    assert "not a production performance or SLA test" in report
    assert "Unmeasured warm-up requests: 5" in report
    assert "public network latency" in report


def test_hosted_report_paths_do_not_overwrite_local_reports() -> None:
    assert AZURE_BENCHMARK_JSON_PATH != BENCHMARK_JSON_PATH
    assert AZURE_BENCHMARK_MARKDOWN_PATH != BENCHMARK_MARKDOWN_PATH
    assert AZURE_BENCHMARK_JSON_PATH.name == "azure_api_latency_benchmark.json"
    assert AZURE_BENCHMARK_MARKDOWN_PATH.name == "azure_api_latency_benchmark.md"


@pytest.mark.parametrize(
    "base_url",
    [
        "http://example.azurecontainerapps.io",
        "example.azurecontainerapps.io",
    ],
)
def test_non_https_base_url_is_rejected(base_url: str) -> None:
    with pytest.raises(ValueError, match="must use HTTPS"):
        normalize_base_url(base_url)


def test_base_url_trailing_slash_is_normalized() -> None:
    assert normalize_base_url("https://example.azurecontainerapps.io/") == (
        "https://example.azurecontainerapps.io"
    )


def test_hosted_result_reuses_expected_latency_statistics() -> None:
    result = make_result()

    assert result["average_latency_ms"] == 25.0
    assert result["p50_latency_ms"] == 25.0
    assert result["p95_latency_ms"] == 38.5
    assert result["min_latency_ms"] == 10.0
    assert result["max_latency_ms"] == 40.0
    assert result["success_rate"] == 0.8


def test_readiness_and_warmup_are_excluded_from_measured_statistics() -> None:
    result = build_azure_benchmark_result(
        base_url="https://example.azurecontainerapps.io",
        health_url="https://example.azurecontainerapps.io/health",
        predict_url="https://example.azurecontainerapps.io/predict",
        warmup_requests=5,
        readiness_attempts=3,
        latencies_ms=[12.0, 18.0],
        requests_attempted=2,
        requests_failed=0,
    )

    assert result["readiness_attempts"] == 3
    assert result["warmup_requests"] == 5
    assert result["requests_attempted"] == 2
    assert result["requests_succeeded"] == 2
    assert result["average_latency_ms"] == 15.0
    assert result["latency_metrics_scope"] == LATENCY_METRICS_SCOPE
    assert result["startup_measurement"] == STARTUP_MEASUREMENT_SCOPE
