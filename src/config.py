from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DOCS_REFERENCES = PROJECT_ROOT / "docs" / "references"
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
CHUNKS_FILE = DATA_PROCESSED / "chunks.jsonl"

# Ingest paths by tier (see docs/decisions/003-two-tier-knowledge.md)
CLINICAL_DIRS = [
    DOCS_REFERENCES / "sources",
    DOCS_REFERENCES / "web",
]
PEER_DIRS = [
    DOCS_REFERENCES / "forums",
    DATA_RAW / "user-queries",
]

PEER_WEB_FILES = {
    DOCS_REFERENCES / "web" / "anticancer-bratan-dieta.md",
}

CLINICAL_WEB_FILES = {
    DOCS_REFERENCES / "web" / "onco-bg-problemi-hranene.md",
    DOCS_REFERENCES / "web" / "bgpatients-obshti-preporaki.md",
    DOCS_REFERENCES / "web" / "cancerinfo-hranene-po-vreme-na-lechenie.md",
}

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

CLINICAL_TOP_K = 5
PEER_TOP_K = 3

# Anthropic — see docs/decisions/001-llm-provider.md
DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-5"

# Deprecated / invalid IDs → working alias (e.g. old .env values)
ANTHROPIC_MODEL_ALIASES: dict[str, str] = {
    "claude-sonnet-4-20250514": DEFAULT_ANTHROPIC_MODEL,
    "claude-sonnet-4-0": DEFAULT_ANTHROPIC_MODEL,
    "claude-opus-4-20250514": "claude-opus-4-5",
    "claude-opus-4-0": "claude-opus-4-5",
}
