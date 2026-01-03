import json
from collections import Counter


def normalize_value(v):
    """Normalize primitive values."""
    if isinstance(v, str):
        # normalize numeric strings
        if v.isdigit():
            return int(v)
        try:
            return float(v)
        except:
            return v.strip()

    return v


def normalize_obj(obj):
    """
    Canonicalize any JSON-like object.
    """
    if isinstance(obj, dict):
        return {
            k: normalize_obj(v)
            for k, v in sorted(obj.items())
        }

    if isinstance(obj, list):
        return [normalize_obj(x) for x in obj]

    return normalize_value(obj)


def canonical_row(row):
    """
    Convert a dict row into a hashable canonical form.
    """
    return tuple(sorted((k, json.dumps(v, sort_keys=True)) for k, v in row.items()))


def multiset_equal(a, b):
    """
    Compare two lists of dicts ignoring order.
    """
    if not isinstance(a, list) or not isinstance(b, list):
        return False

    return Counter(map(canonical_row, a)) == Counter(map(canonical_row, b))


def isLossless(original, decoded):
    """
    Semantic equality check.
    """

    # Normalize everything
    o = normalize_obj(original)
    d = normalize_obj(decoded)

    # Case 1: Both are lists → compare as multisets
    if isinstance(o, list) and isinstance(d, list):
        return multiset_equal(o, d)

    # Case 2: Dicts
    if isinstance(o, dict) and isinstance(d, dict):
        return o == d

    return o == d
