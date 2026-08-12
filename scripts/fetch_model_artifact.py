"""Retrieve and verify the versioned deployment model artifact."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import shutil
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any, BinaryIO
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST_PATH = PROJECT_ROOT / "deployment" / "model_artifact.json"
DEFAULT_REPOSITORY = "KangLi5685752/mlops-customer-churn-platform"
DEFAULT_TIMEOUT_SECONDS = 30.0
CHUNK_SIZE_BYTES = 1024 * 1024


class ArtifactRetrievalError(RuntimeError):
    """Raised when the deployment artifact cannot be safely retrieved."""


class ArtifactChecksumMismatch(ArtifactRetrievalError):
    """Raised when a downloaded artifact does not match the manifest checksum."""


def load_manifest(manifest_path: Path = DEFAULT_MANIFEST_PATH) -> dict[str, Any]:
    """Load the deployment artifact manifest from JSON."""
    manifest_path = Path(manifest_path)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ArtifactRetrievalError(f"Manifest not found: {manifest_path}") from exc
    except json.JSONDecodeError as exc:
        raise ArtifactRetrievalError(f"Manifest is not valid JSON: {manifest_path}") from exc

    required_fields = {
        "artifact_name",
        "artifact_sha256",
        "planned_release_tag",
        "runtime_path",
    }
    missing_fields = sorted(required_fields.difference(manifest))
    if missing_fields:
        raise ArtifactRetrievalError(
            f"Manifest is missing required fields: {', '.join(missing_fields)}"
        )

    return manifest


def construct_release_url(repository: str, release_tag: str, artifact_name: str) -> str:
    """Construct the expected GitHub Release asset URL."""
    repository = repository.strip().strip("/")
    if repository.count("/") != 1:
        raise ValueError("Repository must use the 'owner/name' format.")
    if not release_tag or not artifact_name:
        raise ValueError("Release tag and artifact name must not be empty.")

    encoded_tag = quote(release_tag, safe="")
    encoded_artifact_name = quote(artifact_name, safe="")
    return (
        f"https://github.com/{repository}/releases/download/"
        f"{encoded_tag}/{encoded_artifact_name}"
    )


def calculate_sha256(file_path: Path) -> str:
    """Calculate an uppercase SHA-256 digest for a file."""
    digest = hashlib.sha256()
    with Path(file_path).open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(CHUNK_SIZE_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def verify_artifact_checksum(file_path: Path, expected_sha256: str) -> str:
    """Verify a file against the authoritative manifest checksum."""
    expected_sha256 = expected_sha256.strip().upper()
    if len(expected_sha256) != 64 or any(
        character not in "0123456789ABCDEF" for character in expected_sha256
    ):
        raise ArtifactRetrievalError("Manifest artifact_sha256 is not a valid SHA-256 digest.")

    actual_sha256 = calculate_sha256(file_path)
    if not hmac.compare_digest(actual_sha256, expected_sha256):
        raise ArtifactChecksumMismatch(
            "Artifact checksum mismatch. "
            f"Expected {expected_sha256}, calculated {actual_sha256}. "
            "The downloaded file was not installed."
        )
    return actual_sha256


def _resolve_runtime_path(project_root: Path, runtime_path: str) -> Path:
    """Resolve a manifest runtime path while keeping it inside the project root."""
    project_root = Path(project_root).resolve()
    relative_path = Path(runtime_path)
    if relative_path.is_absolute():
        raise ArtifactRetrievalError("Manifest runtime_path must be repository-relative.")

    destination_path = (project_root / relative_path).resolve()
    try:
        destination_path.relative_to(project_root)
    except ValueError as exc:
        raise ArtifactRetrievalError(
            "Manifest runtime_path must remain inside the project root."
        ) from exc
    return destination_path


def _download_to_file(
    url: str,
    destination_path: Path,
    timeout: float,
    opener: Callable[..., BinaryIO],
) -> None:
    """Download a URL to a temporary destination without interpreting its contents."""
    try:
        with opener(url, timeout=timeout) as response:
            with destination_path.open("wb") as destination:
                shutil.copyfileobj(response, destination)
    except HTTPError as exc:
        if exc.code == 404:
            raise ArtifactRetrievalError(
                "The planned GitHub Release asset is not available at the expected URL. "
                "It may not have been published yet."
            ) from exc
        raise ArtifactRetrievalError(
            f"GitHub Release asset download failed with HTTP {exc.code}."
        ) from exc
    except URLError as exc:
        raise ArtifactRetrievalError(
            f"GitHub Release asset download failed: {exc.reason}"
        ) from exc


def fetch_model_artifact(
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    repository: str = DEFAULT_REPOSITORY,
    project_root: Path = PROJECT_ROOT,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    opener: Callable[..., BinaryIO] = urlopen,
) -> Path:
    """Download, verify and atomically install the deployment artifact."""
    manifest = load_manifest(manifest_path)
    release_url = construct_release_url(
        repository,
        str(manifest["planned_release_tag"]),
        str(manifest["artifact_name"]),
    )
    destination_path = _resolve_runtime_path(project_root, str(manifest["runtime_path"]))
    destination_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_file = tempfile.NamedTemporaryFile(
        prefix=f".{manifest['artifact_name']}.",
        suffix=".download",
        dir=destination_path.parent,
        delete=False,
    )
    temporary_path = Path(temporary_file.name)
    temporary_file.close()

    try:
        _download_to_file(release_url, temporary_path, timeout, opener)
        verify_artifact_checksum(temporary_path, str(manifest["artifact_sha256"]))
        os.replace(temporary_path, destination_path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise

    return destination_path


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Retrieve the planned versioned model artifact and install it only after "
            "SHA-256 verification."
        )
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST_PATH,
        help="Path to the deployment artifact manifest.",
    )
    parser.add_argument(
        "--repository",
        default=DEFAULT_REPOSITORY,
        help="GitHub repository in owner/name format.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Download timeout in seconds.",
    )
    return parser.parse_args()


def main() -> int:
    """Run artifact retrieval from the command line."""
    args = parse_args()
    if args.timeout <= 0:
        print("Error: --timeout must be greater than zero.", file=sys.stderr)
        return 2

    try:
        destination_path = fetch_model_artifact(
            manifest_path=args.manifest,
            repository=args.repository,
            timeout=args.timeout,
        )
    except (ArtifactRetrievalError, OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Verified and installed model artifact at {destination_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
