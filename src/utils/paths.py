"""Repository-relative paths for the Telco churn MLOps project."""

from pathlib import Path

DATASET_FILENAME = "WA_Fn-UseC_-Telco-Customer-Churn.csv"


def find_project_root(start_path: Path) -> Path:
    """Walk upward from start_path and return the repository root.

    The project root is identified by the presence of README.md and data/raw.
    """
    start_path = start_path.resolve()
    candidates = [start_path, *start_path.parents]

    for candidate in candidates:
        if (candidate / "README.md").is_file() and (candidate / "data" / "raw").is_dir():
            return candidate

    raise FileNotFoundError(
        "Could not find the project root. Expected a parent directory containing "
        "README.md and data/raw/."
    )


def _resolve_project_root() -> Path:
    """Resolve the project root from the current working directory or this file."""
    try:
        return find_project_root(Path.cwd())
    except FileNotFoundError:
        return find_project_root(Path(__file__).resolve())


PROJECT_ROOT = _resolve_project_root()
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / DATASET_FILENAME
REPORTS_DIR = PROJECT_ROOT / "reports"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
MODEL_ARTIFACT_PATH = ARTIFACTS_DIR / "telco_churn_model.joblib"
