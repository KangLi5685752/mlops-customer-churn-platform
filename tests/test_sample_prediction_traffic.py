import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.schemas import FEATURE_COLUMNS
from scripts.generate_sample_prediction_traffic import (
    TrafficSummary,
    generate_payloads,
    summarize_risk_labels,
    write_summary_report,
)


def test_generate_payloads_returns_valid_telco_schema_fields() -> None:
    payloads = generate_payloads(8)

    assert len(payloads) == 8
    for payload in payloads:
        assert set(payload) == set(FEATURE_COLUMNS)
        assert "customerID" not in payload
        assert "Churn" not in payload


def test_summarize_risk_labels_counts_successful_responses() -> None:
    responses = [
        {"risk_label": "low"},
        {"risk_label": "medium"},
        {"risk_label": "low"},
        {"risk_label": "high"},
        {},
    ]

    assert summarize_risk_labels(responses) == {
        "high": 1,
        "low": 2,
        "medium": 1,
        "unknown": 1,
    }


def test_write_summary_report_includes_expected_local_monitoring_notes(tmp_path) -> None:
    report_path = tmp_path / "reports" / "sample_prediction_traffic_summary.md"
    summary = TrafficSummary(
        api_url="http://127.0.0.1:8000/predict",
        requests_attempted=3,
        requests_succeeded=2,
        requests_failed=1,
        risk_label_counts={"low": 1, "medium": 1},
    )

    write_summary_report(summary, report_path=report_path)

    report_text = report_path.read_text(encoding="utf-8")
    assert "Requests attempted: 3" in report_text
    assert "Requests succeeded: 2" in report_text
    assert "Requests failed: 1" in report_text
    assert "- low: 1" in report_text
    assert "- medium: 1" in report_text
    assert "logs/predictions.jsonl" in report_text
    assert "excluded from Git" in report_text
