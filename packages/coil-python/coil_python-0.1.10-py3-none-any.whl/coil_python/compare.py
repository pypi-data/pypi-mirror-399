import json


def normalize_semantic(v):
    """
    Exact semantic equivalent of the JS normalizeSemantic function.
    """

    # Array case
    if isinstance(v, list):
        normalized = [normalize_semantic(x) for x in v]

        # Sort by JSON string (same as JS)
        try:
            return sorted(normalized, key=lambda x: json.dumps(x, sort_keys=True))
        except TypeError:
            return normalized

    # Object case
    if isinstance(v, dict):
        return {
            k: normalize_semantic(v[k])
            for k in sorted(v.keys())
        }

    # Primitive — return as-is (NO type coercion)
    return v


def isLossless(original, decoded):
    """
    Semantic equality check (order-independent, type-safe).
    """
    try:
        return (
            json.dumps(normalize_semantic(original), sort_keys=True)
            ==
            json.dumps(normalize_semantic(decoded), sort_keys=True)
        )
    except Exception:
        return False
