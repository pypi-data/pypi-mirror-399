import json
import os
from .compare import isLossless 

def _token_count(text: str) -> int:
    return max(1, len(text) // 4)


def _word_count(text: str) -> int:
    return len(text.split())


def _bytes(text: str) -> int:
    return len(text.encode("utf-8"))


def analyze(original, encoded, decoded=None):
    o = json.dumps(original, ensure_ascii=False)
    e = json.dumps(encoded, ensure_ascii=False)

    stats = {
        "original": {
            "chars": len(o),
            "bytes": _bytes(o),
            "tokens": _token_count(o),
            "words": _word_count(o),
        },
        "encoded": {
            "chars": len(e),
            "bytes": _bytes(e),
            "tokens": _token_count(e),
            "words": _word_count(e),
        }
    }

    stats["comparison"] = {
        "token_saving_%": round(
            (1 - stats["encoded"]["tokens"] / stats["original"]["tokens"]) * 100, 2
        ),
        "byte_saving_%": round(
            (1 - stats["encoded"]["bytes"] / stats["original"]["bytes"]) * 100, 2
        ),
        "twr_original": round(stats["original"]["tokens"] / max(1, stats["original"]["words"]), 3),
        "twr_encoded": round(stats["encoded"]["tokens"] / max(1, stats["encoded"]["words"]), 3),
    }

    if decoded is not None:
        stats["lossless"] = isLossless(original,decoded)

    return stats


def save_stats(stats, out_file="coil_stats.json"):
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    return out_file
