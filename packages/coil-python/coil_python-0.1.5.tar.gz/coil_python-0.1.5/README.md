# COIL – Compact Object Intermediate Language

COIL is a token-optimized, LLM-friendly encoding format designed to reduce
JSON token cost while preserving semantic structure.

## Installation
```bash
pip install coil

```



```Usage
import COIL as C

C.debugMode(True)

encoded = C.encode(data)
decoded = C.decode(encoded)

```
Features

Token-efficient encoding

Schema-aware decoding

LLM-friendly structure

Zero external dependencies (except optional tokenizer)



