# dec.py — General COIL Decoder (COIL v2)
# Restores:
# - nested COIL tables
# - original scalar types (via side-channel)
# - categorical logs (table -> list[str])

import json
from copy import deepcopy

ESC = "\\"
PAIR = ","
REC = "|"
TYPE_FILE = "coil_types.json"

# ---------------- UNESCAPE ----------------

def unesc(v: str) -> str:
    out = []
    i = 0
    while i < len(v):
        if v[i] == ESC and i + 1 < len(v):
            out.append(v[i + 1])
            i += 2
        else:
            out.append(v[i])
            i += 1
    return "".join(out)

# ---------------- TYPE RESTORE ----------------

def restore_type(v, t):
    if t == "int":
        return int(v)
    if t == "float":
        return float(v)
    if t == "bool":
        return v.lower() == "true"
    if t == "NoneType":
        return None
    return v  # str / fallback

# ---------------- TABLE DECODER ----------------

def decode_table(meta: str, body: str, types: dict):
    meta = meta[len("META&"):]
    body = body[len("BODY|"):]

    meta_kv = dict(p.split("=", 1) for p in meta.split("&") if "=" in p)

    keys = meta_kv["ORDER"].split(",")
    table_id = meta_kv.get("tid")

    col_types = types.get(table_id, {})
    vmap = {}

    if "vmap" in meta_kv:
        for e in meta_kv["vmap"].split(";"):
            tok, val = e.split(":", 1)
            vmap[tok] = val

    rows = body.split(REC)[1:]
    records = []

    for row in rows:
        vals = row.split(PAIR)
        rec = {}
        for i, k in enumerate(keys):
            raw = vals[i] if i < len(vals) else ""
            val = vmap.get(raw, unesc(raw))
            rec[k] = restore_type(val, col_types.get(k, "str"))
        records.append(rec)

    # 🔑 LOG AUTO-FLATTEN (single-column categorical table)
    if list(col_types.keys()) == ["msg"]:
        return [r["msg"] for r in records]

    return records

# ---------------- RECURSIVE DECODER ----------------

def decode_any(obj, types):
    if isinstance(obj, dict):
        if "meta" in obj and "body" in obj:
            return decode_table(obj["meta"], obj["body"], types)
        return {k: decode_any(v, types) for k, v in obj.items()}

    if isinstance(obj, list):
        return [decode_any(x, types) for x in obj]

    return obj

# ---------------- ENTRY POINT ----------------

def decode(payload):
    with open(TYPE_FILE, "r", encoding="utf-8") as f:
        types = json.load(f)

    return decode_any(deepcopy(payload), types)
