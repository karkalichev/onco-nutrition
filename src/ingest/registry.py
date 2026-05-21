from pathlib import Path

from src.config import CLINICAL_WEB_FILES, PEER_WEB_FILES, PROJECT_ROOT
from src.i18n import detect_language
from src.models import Tier

SKIP_NAMES = {"README.md", "TEMPLATE.md", "queries.json"}


def resolve_tier(path: Path) -> Tier | None:
    """Return tier for a file under docs/references or data/raw, or None to skip."""
    path = path.resolve()
    name = path.name

    if name in SKIP_NAMES or path.suffix.lower() not in {".md", ".pdf"}:
        return None

    try:
        rel = path.relative_to(PROJECT_ROOT)
    except ValueError:
        return None

    parts = rel.parts

    if "forums" in parts:
        return Tier.PEER

    if "user-queries" in parts and path.suffix == ".md" and name != "TEMPLATE.md":
        return Tier.PEER

    if path in PEER_WEB_FILES:
        return Tier.PEER

    if "sources" in parts and path.suffix == ".pdf":
        return Tier.CLINICAL

    if "web" in parts and path.suffix == ".md":
        if path in CLINICAL_WEB_FILES or path not in PEER_WEB_FILES:
            return Tier.CLINICAL

    return None


def infer_language(path: Path, text: str) -> str:
    return detect_language(text)


def source_title(path: Path) -> str:
    stem = path.stem.replace("-", " ")
    if "acs-nutrition" in path.name and "bg" in path.name:
        return "ACS — хранене по време на лечение (BG)"
    if "onco-bg" in path.name:
        return "Онко.БГ — проблеми с храненето"
    if "cancerinfo" in path.name:
        return "CancerInfo.bg"
    if "espen" in path.name:
        return "ESPEN clinical nutrition in cancer"
    if "nci" in path.name:
        return "NCI Eating Hints"
    return stem.title()
