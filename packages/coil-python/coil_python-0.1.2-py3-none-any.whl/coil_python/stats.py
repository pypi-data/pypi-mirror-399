import json
import math
from pathlib import Path

# -----------------------------
# Token estimation (fallback)
# -----------------------------
def token_count(text: str) -> int:
    return max(1, len(text) // 4)

# -----------------------------
# Cost estimation (INR)
# -----------------------------
def token_cost(tokens, rate_per_1k=0.03):
    # approx ₹0.03 per 1k tokens (configurable)
    return round((tokens / 1000) * rate_per_1k, 4)

# -----------------------------
# Core Stats
# -----------------------------
def compute_stats(original, encoded):
    o_json = json.dumps(original, ensure_ascii=False)
    e_json = json.dumps(encoded, ensure_ascii=False)

    stats = {
        "original": {
            "chars": len(o_json),
            "bytes": len(o_json.encode("utf-8")),
            "tokens": token_count(o_json),
        },
        "encoded": {
            "chars": len(e_json),
            "bytes": len(e_json.encode("utf-8")),
            "tokens": token_count(e_json),
        }
    }

    stats["comparison"] = {
        "token_saving_%": round(
            (1 - stats["encoded"]["tokens"] / stats["original"]["tokens"]) * 100,
            2
        ),
        "byte_saving_%": round(
            (1 - stats["encoded"]["bytes"] / stats["original"]["bytes"]) * 100,
            2
        ),
        "token_cost_inr": token_cost(stats["encoded"]["tokens"]),
    }

    return stats


def save_stats(stats, path="coil_stats.json"):
    path = Path(path)
    path.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    return path
