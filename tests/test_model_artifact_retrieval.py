import hashlib
import io
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.fetch_model_artifact import (
    DEFAULT_MANIFEST_PATH,
    ArtifactChecksumMismatch,
    construct_release_url,
    fetch_model_artifact,
    load_manifest,
    verify_artifact_checksum,
)


def test_load_manifest_reads_expected_deployment_metadata() -> None:
    manifest = load_manifest(DEFAULT_MANIFEST_PATH)

    assert manifest["artifact_name"] == "model_pipeline.joblib"
    assert manifest["runtime_path"] == "artifacts/model_pipeline.joblib"
    assert manifest["planned_release_tag"] == "model-v1.0.0"
    assert manifest["release_status"] == "published"


def test_construct_release_url_uses_planned_tag_and_asset_name() -> None:
    release_url = construct_release_url(
        "KangLi5685752/mlops-customer-churn-platform",
        "model-v1.0.0",
        "model_pipeline.joblib",
    )

    assert release_url == (
        "https://github.com/KangLi5685752/mlops-customer-churn-platform/"
        "releases/download/model-v1.0.0/model_pipeline.joblib"
    )


def test_verify_artifact_checksum_accepts_matching_file(tmp_path: Path) -> None:
    artifact_path = tmp_path / "model_pipeline.joblib"
    artifact_bytes = b"verified deployment artifact"
    artifact_path.write_bytes(artifact_bytes)
    expected_sha256 = hashlib.sha256(artifact_bytes).hexdigest()

    actual_sha256 = verify_artifact_checksum(artifact_path, expected_sha256)

    assert actual_sha256 == expected_sha256.upper()


def test_verify_artifact_checksum_rejects_mismatch(tmp_path: Path) -> None:
    artifact_path = tmp_path / "model_pipeline.joblib"
    artifact_path.write_bytes(b"untrusted artifact")

    with pytest.raises(ArtifactChecksumMismatch, match="checksum mismatch"):
        verify_artifact_checksum(artifact_path, "0" * 64)


def test_mismatched_download_is_not_installed(tmp_path: Path) -> None:
    manifest = load_manifest(DEFAULT_MANIFEST_PATH)
    manifest["runtime_path"] = "artifacts/model_pipeline.joblib"
    manifest["artifact_sha256"] = hashlib.sha256(b"trusted artifact").hexdigest()
    manifest_path = tmp_path / "deployment" / "model_artifact.json"
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    requested_urls: list[str] = []

    def fake_opener(url: str, timeout: float) -> io.BytesIO:
        requested_urls.append(url)
        return io.BytesIO(b"untrusted artifact")

    final_path = tmp_path / "artifacts" / "model_pipeline.joblib"
    with pytest.raises(ArtifactChecksumMismatch):
        fetch_model_artifact(
            manifest_path=manifest_path,
            project_root=tmp_path,
            opener=fake_opener,
        )

    assert requested_urls == [
        "https://github.com/KangLi5685752/mlops-customer-churn-platform/"
        "releases/download/model-v1.0.0/model_pipeline.joblib"
    ]
    assert not final_path.exists()
    assert not list(final_path.parent.glob("*.download"))
