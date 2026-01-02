import importlib
import re
from re import Match
from typing import Any, Dict, List, Optional, Tuple

import polars as pl

PARENT_TOPIC_RE = re.compile(
    r"\*\*Parent topic:\*\*\s*(.+?)(?:\n|$)",
    re.IGNORECASE,
)

IMAGE_MD_RE = re.compile(r"!\[[^\]]*\]\([^)]+\)")
BASE64_RE = re.compile(r"data:image/[^)\s]+")
HTML_TAG_RE = re.compile(r"<[^>]+>")
GUID_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
TORQUE_RE = re.compile(r"^\s*\d+(\.\d+)?\s*Nm.*$", re.MULTILINE)

MULTI_NEWLINE_RE = re.compile(r"\n{2,}")
HEADER_NEWLINE_RE = re.compile(r"(#+ .+)\n+")
HEADER_RE = re.compile(r"(#+ .+)\n+")
LIST_ITEM_RE = re.compile(r"(\n\d+\. .+)\n+(?=\d+\. )")
BULLET_ITEM_RE = re.compile(r"(\n- .+)\n+(?=- )")
TOP_LEVEL_HEADER_RE = re.compile(
    r"^\s*# (.+)$",
    re.MULTILINE,
)
ADMIN_PATTERNS = [
    r"Correction code.*",
    r"Do not stack correction codes.*",
    r"Flat Rate Times.*",
    r"ServiceManualFeedback@tesla\.com.*",
    r"^\d{4}-\d{2}-\d{2}\s*$",  # dates alone on a line
]
OP_RE = re.compile(r"\((Remove and Replace|Remove and Install|Adjust)\)", re.IGNORECASE)
BLOCK_HEADERS_TO_DROP = {
    "note",
    "tip",
    "warning",
    "caution",
}


# =========================
# Core helpers
# =========================


def _extract_parent_topic(text: str) -> Tuple[str, str | None]:
    parent_topic = None

    def _replace(match: Match) -> str:
        nonlocal parent_topic
        raw = match.group(1).strip()
        # remove markdown link if present
        parent_topic = GUID_LINK_RE.sub(r"\1", raw)
        return ""

    text = PARENT_TOPIC_RE.sub(_replace, text)
    return text, parent_topic


def _extract_procedure_title(text: str) -> Tuple[str, str | None]:
    """
    Extract the first top-level markdown header (# ...) as procedure title.
    """
    match = TOP_LEVEL_HEADER_RE.search(text)
    if not match:
        return text, None

    title = match.group(1).strip()

    # remove ONLY the first occurrence
    text = TOP_LEVEL_HEADER_RE.sub("", text, count=1)

    return text.strip(), title


def _merge_indented_lines(text: str) -> str:
    lines = text.splitlines()
    out: List[str] = []
    buffer = ""

    for line in lines:
        if line.startswith("    ") or line.startswith("\t"):
            buffer += " " + line.strip()
        else:
            if buffer:
                out[-1] += buffer
                buffer = ""
            out.append(line)

    if buffer and out:
        out[-1] += buffer

    return "\n".join(out)


def _normalize_spacing(text: str) -> str:
    if not text:
        return ""

    # 1️⃣ Remove whitespace-only lines
    lines = [line.rstrip() for line in text.splitlines()]
    text = "\n".join(lines)

    # 2️⃣ Remove empty lines immediately after headers
    text = HEADER_RE.sub(r"\1\n", text)

    # 3️⃣ Remove empty lines between numbered list items
    text = LIST_ITEM_RE.sub(r"\1\n", text)

    # 4️⃣ Remove empty lines between bullet list items
    text = BULLET_ITEM_RE.sub(r"\1\n", text)

    # 5️⃣ Collapse remaining multiple newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# =========================
# Public API
# =========================


def metadata_struct_dtype(metadata_keys: List[str]) -> pl.Struct:
    return pl.Struct(
        {
            "page_content": pl.Utf8,
            **{k: pl.Utf8 for k in metadata_keys},
        }
    )


def clean_markdown_with_metadata(text: str) -> Dict[str, Optional[str]]:
    """
    Clean markdown content for embeddings and extract useful metadata.

    Returns:
        cleaned_text (str)
        metadata (dict)  -> e.g. {"parent_topic": "..."}
    """
    if not text:
        return {}

    metadata: Dict[str, str] = {}

    # --- Extract procedure title (# ...) ---
    text, procedure_title = _extract_procedure_title(text)
    if procedure_title:
        metadata["procedure_title"] = procedure_title

    # --- Extract Parent topic first ---
    text, parent_topic = _extract_parent_topic(text)
    if parent_topic:
        metadata["parent_topic"] = parent_topic

    # --- Remove images & binary junk ---
    text = IMAGE_MD_RE.sub("", text)
    text = BASE64_RE.sub("", text)

    # --- Remove HTML tags ---
    text = HTML_TAG_RE.sub("", text)

    # --- Replace markdown links with text only ---
    text = GUID_LINK_RE.sub(r"\1", text)

    # --- Remove torque-only lines ---
    text = TORQUE_RE.sub("", text)

    # --- Remove admin boilerplate ---
    for p in ADMIN_PATTERNS:
        text = re.sub(p, "", text, flags=re.IGNORECASE | re.MULTILINE)

    # --- Drop Note / Tip / Warning blocks ---
    lines = []
    skip = False

    for line in text.splitlines():
        stripped = line.strip().lower()

        if stripped in BLOCK_HEADERS_TO_DROP:
            skip = True
            continue

        if skip:
            if not stripped:
                skip = False
            continue

        lines.append(line)

    text = "\n".join(lines)

    text = _merge_indented_lines(text)

    # --- Normalize spacing ---
    text = _normalize_spacing(text)

    return {"page_content": text, **{key: metadata.get(key) for key in metadata}}


def merge_metadata(existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    return {**existing, **new}


def load_class(path: str) -> Any:
    module_path, class_name = path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)
