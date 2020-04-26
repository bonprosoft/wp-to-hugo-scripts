import argparse
import pathlib
import re
from typing import List

LANG_REGEX = r"(lang:\s*(?P<lang>\S+)\s*)"
MARK_REGEX = r"(mark:\s*(?P<mark>\S+)\s*)"
STRIPED_REGEX = r"(striped:\s*(?P<striped>\S+)\s*)"
WRAP_REGEX = r"(wrap:\s*(?P<wrap>\S+)\s*)"
DECODE_REGEX = r"(decode:\s*(?P<decode>\S+)\s*)"

ATTR_REGEX = (
    rf"({LANG_REGEX}|{MARK_REGEX}|{STRIPED_REGEX}|{WRAP_REGEX}|{DECODE_REGEX})*"  # NOQA
)
CLASS_REGEX = rf"(class=\"{ATTR_REGEX}\"\s*)"
TITLE_REGEX = r"(title=\"(?P<title>.*?)\"\s*)"
BODY_REGEX = r"(?P<body>.*?)"
PRE_REGEX = rf"<pre\s*({CLASS_REGEX}|{TITLE_REGEX})*>{BODY_REGEX}<\/pre>"

pre = re.compile(PRE_REGEX, re.MULTILINE | re.DOTALL)


def _replace(s: str, m: re.Match, title_level: int = 5) -> str:
    lang = m.group("lang") or "base"
    mark = m.group("mark")
    title = m.group("title")
    body = m.group("body").replace("&lt;", "<").replace("&gt;", ">")

    attrs: List[str] = []

    if mark is not None:
        marks = mark.split(",")
        hl_lines = ",".join([f'"{x}"' for x in marks])

        attrs.append(f"hl_lines=[{hl_lines}]")

    attrs.append("linenos=table")

    block = f"""
```{lang} {{{",".join(attrs)}}}
{body}
```
"""

    if title is not None:
        heading = "#" * title_level
        block = f"{heading} {title}\n" + block

    return s[: m.start()] + block + s[m.end():]


def convert(content: str, path: pathlib.Path, args: argparse.Namespace) -> str:
    title_level = args.title_level
    matches = list(pre.finditer(content))
    for idx, m in enumerate(matches[::-1]):
        content = _replace(content, m, title_level)

    return content


def setup_argparse(args: argparse.ArgumentParser) -> None:
    args.add_argument("--title-level", type=int, default=5)
