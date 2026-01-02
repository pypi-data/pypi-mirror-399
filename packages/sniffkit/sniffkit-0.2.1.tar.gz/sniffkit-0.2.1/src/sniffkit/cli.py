import argparse

from sniffkit.okru import okru_m3u8p
from sniffkit.core import sniff_m3u8_g

def main():
    p = argparse.ArgumentParser(prog="sniffkit")
    p.add_argument("-g",  "--generic", help="Generic extractor URL")
    p.add_argument("-ok", "--okru",    help="OK.ru extractor URL")

    args = p.parse_args()

    if args.okru:
        print(okru_m3u8p(args.okru))
        return

    if args.generic:
        print(sniff_m3u8_g(args.generic))
        return

    p.error("choose one of -g/--generic or -ok/--okru")

if __name__ == "__main__":
    main()
