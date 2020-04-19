#!/usr/bin/env python3
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, List, Tuple

import requests

# TODO: check html files
# TODO: find the html link pattern in markdown as well (a, img, iframe)
# TODO: make sure that all local links are tracked in git

ignore = [
    Path('README.md')
]

source_dirs = [
    '_posts',
    './'
]


def check_web_link(link: str) -> bool:
    try:
        requests.head(link)
        return True
    except (requests.exceptions.ConnectionError, requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema):
        return False


def check_local_link(link: str) -> bool:
    return link[0] == '/' and os.path.isfile('.' + link)


def check_mail_link(link: str) -> bool:
    return bool(re.match(r'^mailto:.*@.*$', link))


def check_link(data: Tuple[Path, str]) -> bool:
    path, link = data
    result = check_local_link(link) or check_mail_link(link) or check_web_link(link)
    if result is False:
        print('{}: {}'.format(str(path), link))
    return result


def get_links_from_markdown(path: Path) -> Any:
    with open(path) as f:
        text = f.read()

    link_pattern = r'\[.*?\]\((.+?)\)'

    links = re.findall(link_pattern, text)
    return zip([str(path)] * len(links), links)


def get_all_links(all_files: List[Path]) -> List[Tuple[Path, str]]:
    all_links = []
    for file in all_files:
        all_links.extend(get_links_from_markdown(file))
    return all_links


def main() -> None:
    all_md_files: List[Path] = []
    for source_file in source_dirs:
        all_md_files.extend(Path(source_file).glob('*.md'))

    with ThreadPoolExecutor() as executor:
        results = executor.map(check_link, get_all_links([p for p in all_md_files if p not in ignore]))

    if not all(results):
        print('Broken links found')
        sys.exit(1)
    else:
        print('Links ok.')


if __name__ == '__main__':
    main()
