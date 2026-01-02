import argparse, sys
from .core import sniff_m3u8_g

def main() -> int:
    p = argparse.ArgumentParser(prog="sniffkit")
    p.add_argument("-g", "--get-url", dest="url", help="Print best detected m3u8 URL")
    p.add_argument("--wait", type=float, default=6.0)
    p.add_argument("--timeout", type=float, default=10.0)
    args = p.parse_args()

    if not args.url:
        p.print_help()
        return 2

    out = sniff_m3u8_g(args.url, wait_seconds=args.wait, timeout_seconds=args.timeout)
    if not out:
        return 1

    print(out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
