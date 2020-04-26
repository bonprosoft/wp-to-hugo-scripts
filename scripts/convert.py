import argparse
import pathlib
import sys

import convert_img
import convert_pre_code


def main():
    converters = {
        "code": convert_pre_code,
        "img": convert_img,
    }

    parser = argparse.ArgumentParser()
    parser.add_argument("dir", type=str, help="target directory")
    subparser = parser.add_subparsers()

    for k, c in converters.items():
        p = subparser.add_parser(k)
        c.setup_argparse(p)
        p.set_defaults(func=c.convert)

    args = parser.parse_args()

    if "func" not in args:
        parser.print_help()
        sys.exit(1)

    base = pathlib.Path(args.dir)
    paths = list(base.glob("**/*.md"))
    for path in paths:
        print(f"- Updating {path}")
        with path.open("r") as f:
            content = f.read()

        modified = args.func(content, path, args)
        with path.open("w") as f:
            f.write(modified)


if __name__ == "__main__":
    main()
