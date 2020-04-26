import argparse
import dataclasses
import pathlib
import re
import shutil
from typing import Iterator, Optional

IMAGE = r"<img\s+(?P<img_attrs>.*?)\/>"
IMAGE_MD = rf"\[{IMAGE}\]\[[0-9]+\]"
SRC = r"src=\"(?P<src>.*?)\""
IMAGE_DIV_CONTAINER = r"<div\s+(?P<div_attrs>.*?)>(?P<div_body>.*?)</div>"
CAPTION = r"<p\s+class=\"wp-caption-text\"\s*>(?P<caption>.*?)</p>"

image_regex = re.compile(IMAGE, re.MULTILINE | re.DOTALL)
image_md_regex = re.compile(IMAGE_MD, re.MULTILINE | re.DOTALL)
caption_regex = re.compile(CAPTION, re.MULTILINE | re.DOTALL)
src_regex = re.compile(SRC, re.MULTILINE | re.DOTALL)
container = re.compile(IMAGE_DIV_CONTAINER, re.MULTILINE | re.DOTALL)


@dataclasses.dataclass
class ImageContainer:
    image: str
    start: int
    end: int


@dataclasses.dataclass
class ImageContainerWithCaption:
    caption: str
    image: ImageContainer
    start: int
    end: int


def _get_image_path(
    image_name: str, previous_url: str, source_dir: pathlib.Path
) -> pathlib.Path:
    image_path_url = image_name.lstrip(previous_url)
    image_path_url = image_path_url.lstrip("/")
    image_path = source_dir / image_path_url
    image_path = image_path.resolve()
    if not image_path.exists():
        raise RuntimeError(f"not exists: {image_path}")

    filename = image_path.stem
    names = filename.rsplit("-", 1)
    if len(names) == 1:
        print(f"  * non-resized-image found: {image_path}")
        return image_path

    assert len(names) == 2
    original_name, resize = names
    sizes = resize.split("x")
    if len(sizes) == 2 and sizes[0].isnumeric() and sizes[1].isnumeric():
        # might be a resize version
        original_path = image_path.parent / f"{original_name}{image_path.suffix}"
        if original_path.exists() and original_path.is_file():
            print(f"  * resized-image found: {image_path} -> {original_path}")
            return original_path

        raise RuntimeError(f"not exists: {original_path}")
    else:
        print(f"  * non-resized-image found: {image_path}")
        return image_path


def _find_src(content: str) -> Optional[str]:
    matches = list(src_regex.finditer(content))
    if len(matches) == 0:
        return None

    assert len(matches) == 1
    src = matches[0].group("src")
    return src


def _find_image(content: str) -> Optional[ImageContainer]:
    matches = list(image_regex.finditer(content))
    if len(matches) == 0:
        return None

    assert len(matches) == 1
    m = matches[0]
    attrs = m.group("img_attrs") or ""
    src = _find_src(attrs)
    if src is None:
        return None

    return ImageContainer(src, m.start(), m.end())


def _find_image_caption(content: str) -> Optional[str]:
    matches = list(caption_regex.finditer(content))
    if len(matches) == 0:
        return None

    assert len(matches) == 1
    caption = matches[0].group("caption") or ""
    return caption.strip()


def _find_image_md(content: str) -> Iterator[ImageContainer]:
    matches = list(image_md_regex.finditer(content))

    for m in matches:
        attrs = m.group("img_attrs") or ""
        src = _find_src(attrs)
        if src is None:
            continue

        yield ImageContainer(src, m.start(), m.end())


def _find_image_container(content: str) -> Iterator[ImageContainerWithCaption]:
    matches = container.finditer(content)
    for m in matches:
        attrs = m.group("div_attrs") or ""
        if "wp-caption" not in attrs:
            continue

        body = m.group("div_body") or ""
        caption = _find_image_caption(body)
        image = _find_image(body)
        if image is None:
            continue

        assert caption is not None
        yield ImageContainerWithCaption(caption, image, m.start(), m.end())


def _replace_div(s: str, m: ImageContainerWithCaption) -> str:
    block = f'{{{{<figure src="{m.image.image}" title="{m.caption}" alt="{m.caption}" >}}}}'  # NOQA
    return s[: m.start] + block + s[m.end :]


def _replace_image(s: str, m: ImageContainer) -> str:
    block = f'{{{{<figure src="{m.image}" >}}}}'
    return s[: m.start] + block + s[m.end :]


def convert(content: str, path: pathlib.Path, args: argparse.Namespace) -> str:
    source = pathlib.Path(args.data_source)
    base_dir = path.resolve().parent
    if not source.exists() or not source.is_dir():
        raise RuntimeError("invalid data_source is specified")

    matches = list(_find_image_container(content))
    previous_url = args.previous_url
    for idx, m in enumerate(matches[::-1]):
        fpath = _get_image_path(m.image.image, previous_url, source)
        copied_path = base_dir / fpath.name
        shutil.copy2(fpath, copied_path)
        m.image.image = fpath.name
        content = _replace_div(content, m)

    matches_image = list(_find_image_md(content))
    for i in matches_image[::-1]:
        fpath = _get_image_path(i.image, previous_url, source)
        copied_path = base_dir / fpath.name
        shutil.copy2(fpath, copied_path)
        i.image = fpath.name
        content = _replace_image(content, i)

    return content


def setup_argparse(args: argparse.ArgumentParser) -> None:
    args.add_argument("previous_url", type=str)
    args.add_argument("data_source", type=str)
