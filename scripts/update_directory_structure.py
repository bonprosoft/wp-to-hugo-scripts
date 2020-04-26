import argparse
import shutil
import pathlib


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", type=str, help="target directory")
    args = parser.parse_args()

    base = pathlib.Path(args.dir)
    paths = list(base.glob("**/*.md"))
    for path in paths:
        md_path = pathlib.Path(path).resolve()
        dir_path = md_path.parent / md_path.stem
        md_moved_path = dir_path / "index.md"
        print(f"- Updating {md_path} -> {md_moved_path}")
        dir_path.mkdir()
        shutil.move(md_path, md_moved_path)


if __name__ == "__main__":
    main()
