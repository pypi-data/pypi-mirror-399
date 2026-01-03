import argparse
import json
from . import encode, decode, stats

def main():
    parser = argparse.ArgumentParser("coil")
    sub = parser.add_subparsers(dest="cmd")

    enc = sub.add_parser("encode")
    enc.add_argument("input")
    enc.add_argument("-o", "--out", default="encoded.json")

    dec = sub.add_parser("decode")
    dec.add_argument("input")
    dec.add_argument("-o", "--out", default="decoded.json")

    st = sub.add_parser("stats")
    st.add_argument("original")
    st.add_argument("encoded")
    st.add_argument("-o", "--out", default="coil_stats.json")

    args = parser.parse_args()

    if args.cmd == "encode":
        with open(args.input) as f:
            data = json.load(f)
        result = encode(data)
        with open(args.out, "w") as f:
            json.dump(result, f, indent=2)

    elif args.cmd == "decode":
        with open(args.input) as f:
            data = json.load(f)
        result = decode(data)
        with open(args.out, "w") as f:
            json.dump(result, f, indent=2)

    elif args.cmd == "stats":
        with open(args.original) as f:
            o = json.load(f)
        with open(args.encoded) as f:
            e = json.load(f)

        result = stats(o, e, out=args.out)
        print(json.dumps(result, indent=2))

    else:
        parser.print_help()
