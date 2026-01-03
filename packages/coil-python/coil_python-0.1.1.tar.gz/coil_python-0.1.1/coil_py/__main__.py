import argparse
import json
from . import encode, decode

def main():
    parser = argparse.ArgumentParser(description="COIL encoder/decoder")
    sub = parser.add_subparsers(dest="cmd")

    enc = sub.add_parser("encode")
    enc.add_argument("input")
    enc.add_argument("-o", "--output", default="encoded.json")

    dec = sub.add_parser("decode")
    dec.add_argument("input")
    dec.add_argument("-o", "--output", default="decoded.json")

    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    if args.cmd == "encode":
        out = encode(data)
    elif args.cmd == "decode":
        out = decode(data)
    else:
        parser.print_help()
        return

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"✔ Written → {args.output}")


if __name__ == "__main__":
    main()
