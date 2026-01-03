# __init__.py — COIL Public API
# Stable, production-safe interface

import json
import os

from .enc import encode as _encode
from .dec import decode as _decode
from .stats import compute_stats, save_stats


__all__ = [
    "encode",
    "decode",
    "stats",
    "debugMode",
    "set_model",
    "info"
]

# =========================
# GLOBAL STATE
# =========================

_DEBUG = False
_DEFAULT_STRUCTURE_FILE = "coil_types.json"
_ACTIVE_MODEL = "default"

# -------------------------
# TOKENIZER MAP (logical only)
# -------------------------

TOKENIZER_MAP = {
    "gpt-4o": "tiktoken:gpt-4o",
    "gpt-4o-mini": "tiktoken:gpt-4o-mini",
    "gpt-4.1": "tiktoken:gpt-4.1",
    "claude-3": "anthropic",
    "gemini": "google",
    "mistral": "mistral",
    "default": "generic"
}

# =========================
# INTERNAL UTILITIES
# =========================

def _log(msg):
    if _DEBUG:
        print(f"[COIL] {msg}")


def _ensure_json_ext(path: str):
    return path if path.endswith(".json") else path + ".json"


# =========================
# PUBLIC API
# =========================

def debugMode(flag: bool = True):
    """Enable or disable debug logging."""
    global _DEBUG
    _DEBUG = bool(flag)
    _log("Debug mode enabled" if _DEBUG else "Debug mode disabled")


def set_model(model_name: str):
    """Select tokenizer backend (logical mapping only)."""
    global _ACTIVE_MODEL
    _ACTIVE_MODEL = model_name if model_name in TOKENIZER_MAP else "default"
    _log(f"Tokenizer set to: {_ACTIVE_MODEL}")


def encode(
    data,
    *,
    structure_file: str | None = None,
    return_structure: bool = False
):
    """
    Encode JSON into COIL format.
    """
    structure_file = _ensure_json_ext(
        structure_file or _DEFAULT_STRUCTURE_FILE
    )

    _log("Encoding started")
    _log(f"Structure file: {structure_file}")
    _log(f"Tokenizer: {_ACTIVE_MODEL}")

    encoded = _encode(data)

    if return_structure:
        if os.path.exists(structure_file):
            with open(structure_file, "r", encoding="utf-8") as f:
                return encoded, json.load(f)
        return encoded, None

    return encoded


def decode(
    encoded_data,
    *,
    structure_file: str | None = None
):
    """
    Decode COIL encoded data using structure metadata.
    """
    structure_file = _ensure_json_ext(
        structure_file or _DEFAULT_STRUCTURE_FILE
    )

    _log("Decoding started")
    _log(f"Structure file: {structure_file}")

    if not os.path.exists(structure_file):
        raise FileNotFoundError(
            f"Structure file not found: {structure_file}"
        )

    return _decode(encoded_data)


def info():
    return {
        "library": "pycoil",
        "module": "coil",
        "version": "0.1.1",
        "tokenizer": _ACTIVE_MODEL,
        "debug": _DEBUG,
        "structure_file": _DEFAULT_STRUCTURE_FILE,
    }


def stats(original, encoded, *, out="coil_stats.json"):
    """
    Compare original vs encoded data and generate stats.
    """
    stats = compute_stats(original, encoded)
    save_stats(stats, out)
    return stats
