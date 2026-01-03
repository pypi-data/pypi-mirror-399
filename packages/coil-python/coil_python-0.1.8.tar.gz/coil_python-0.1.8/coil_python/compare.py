
def normalize(obj):
    """
    Canonicalize data for semantic comparison.
    Order-insensitive, type-stable.
    """

    # Normalize dicts
    if isinstance(obj, dict):
        return {
            k: normalize(obj[k])
            for k in sorted(obj.keys())
        }

    # Normalize lists (order-independent)
    if isinstance(obj, list):
        norm = [normalize(x) for x in obj]

        # Sort safely by string repr
        try:
            return sorted(norm, key=lambda x: str(x))
        except Exception:
            return norm

    # Normalize numbers in string form
    if isinstance(obj, str):
        if obj.isdigit():
            return int(obj)
        try:
            return float(obj)
        except:
            return obj

    return obj


def isLossless(original, decoded):
    return normalize(original) == normalize(decoded)

