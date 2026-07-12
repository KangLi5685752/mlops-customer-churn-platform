import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.benchmark_api_latency import (
    LOCAL_BENCHMARK_NOTE,
    build_benchmark_result,
    build_markdown_report,
    compute_latency_statistics,
)


def test_compute_latency_statistics_reports_expected_metrics() -> None:
    statistics = compute_latency_statistics(
        latencies_ms=[10.0, 20.0, 30.0, 40.0],
        requests_attempted=5,
        requests_succeeded=4,
        requests_failed=1,
    )

    assert statistics["requests_attempted"] == 5
    assert statistics["requests_succeeded"] == 4
    assert statistics["requests_failed"] == 1
    assert statistics["average_latency_ms"] == 25.0
    assert statistics["p50_latency_ms"] == 25.0
    assert statistics["p95_latency_ms"] == 38.5
    assert statistics["min_latency_ms"] == 10.0
    assert statistics["max_latency_ms"] == 40.0
    assert statistics["success_rate"] == 0.8


def test_compute_latency_statistics_handles_no_successes() -> None:
    statistics = compute_latency_statistics(
        latencies_ms=[],
        requests_attempted=3,
        requests_succeeded=0,
        requests_failed=3,
    )

    assert statistics["average_latency_ms"] is None
    assert statistics["p50_latency_ms"] is None
    assert statistics["p95_latency_ms"] is None
    assert statistics["min_latency_ms"] is None
    assert statistics["max_latency_ms"] is None
    assert statistics["success_rate"] == 0.0


def test_build_markdown_report_includes_local_synthetic_scope() -> None:
    result = build_benchmark_result(
        api_url="http://127.0.0.1:8000/predict",
        latencies_ms=[12.3456, 20.0],
        requests_attempted=2,
        requests_failed=0,
    )

    report_text = build_markdown_report(result)

    assert LOCAL_BENCHMARK_NOTE in report_text
    assert "local synthetic API latency" in report_text
    assert "Latency metrics are calculated from successful requests only." in report_text
    assert "http://127.0.0.1:8000/predict" in report_text
    assert "| p95 |" in report_text
