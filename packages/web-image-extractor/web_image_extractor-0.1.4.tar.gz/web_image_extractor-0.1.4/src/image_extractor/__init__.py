"""Use `from image_extractor import <function>` for image extraction"""

import os

from helpers import get_web_text
from web_classes import ImageFromHTML, ImageGetter, SVGMaker

build_image = ImageGetter().start
build_svg = SVGMaker().start


def extract_images(url: str, is_file: bool = False) -> dict[str, set[str]]:
    html_text = get_web_text(url, is_file=is_file)
    img_srcs, svg_texts = ImageFromHTML(url).feed(html_text, url)
    ret = {"img_srcs": img_srcs, "svg_texts": svg_texts}
    return ret


def download_images(
    url: str, destination: str, img_srcs: set[str] = set(), svg_texts: set[str] = set()
) -> None:
    """Make this track number of successful downloads.
    Like img_srcs: 3, 6 (for 3 out of 6), svg_text: like img_srcs
    """
    if not all((destination, img_srcs or svg_texts)): return
    cwd = os.getcwd()
    os.chdir(destination)
    # download images
    for img_src in img_srcs:
        try:
            build_image(url, img_src, destination)
        except Exception as error:
            print(f"{img_src} -> {error}")

    # download svgs
    for svg_text in svg_texts:
        try:
            build_svg(svg_text, destination)
        except Exception as error:
            print(error)

    os.startfile(destination)
    os.chdir(cwd)
