import os
import urllib.parse as ps
import urllib.request as rq
from pathlib import Path

# Todo: Use headers to prevent forbidden requests in future


def check_some(base: str, *possibles: str) -> bool:
    """This function returns true if any member of possibles is present in base"""
    return any(value in base for value in possibles)


def str_attr(attrs: list[tuple[str, str | None]]):
    """Works for html elements with both start and end tags
    Turns the dict to string replace commas by nothing
    replace colons by equals
    """
    return " " + " ".join(f'{name}="{value}"' for name, value in attrs) if attrs else ""


def join_url(website: str, src: str) -> str:
    # use urllib.parse to query url given
    full_src = ps.urlparse(src)
    website_rich: ps.ParseResult = ps.urlparse(website)
    src_path = full_src.path
    if full_src.netloc:
        scheme = full_src.scheme or website_rich.scheme
        src = f"{scheme}://{full_src.netloc}{src_path}"
    else:
        # turn 'daniel.jpg' to 'https://danielongithub17.github.io/daniel.jpg'
        scheme = website_rich.scheme or full_src.scheme
        src = f"{scheme}://{website_rich.netloc}{(not src_path.startswith('/')) * '/'}{src_path}"
    return src


def find_right_name(name: str, folder: str) -> str:
    name_hold = Path(name).stem
    extension = Path(name).suffix
    same_name_count = 1
    files = set(os.listdir(folder))
    # if name already exists, add a digit (like version) to the end of name
    while name in files:
        name = f"{name_hold}_{same_name_count}{extension}"
        same_name_count += 1
    return name


def get_web_text(url: str, is_file: bool = False) -> str:
    if is_file:
        with open(url, errors="ignore") as html_file:
            return html_file.read()
    else:
        with rq.urlopen(url) as html_file:
            return html_file.read().decode(errors="ignore")


__all__ = ["check_some", "str_attr", "join_url", "find_right_name", "get_web_text"]
