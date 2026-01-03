
def normalize(obj):
    """
    Convert object into a canonical form:
    - dicts: sorted by key
    - lists: sorted by normalized representation
    - primitives: unchanged
    """

    if isinstance(obj, dict):
        return {
            k: normalize(obj[k])
            for k in sorted(obj.keys())
        }

    if isinstance(obj, list):
        # Normalize each item
        normalized = [normalize(x) for x in obj]

        # Sort lists deterministically
        try:
            return sorted(normalized, key=lambda x: str(x))
        except TypeError:
            return normalized

    return obj

def isLossless(original, decoded):
    return normalize(a) == normalize(b)

