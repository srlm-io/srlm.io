#!/usr/bin/env python3
import os
import re
import subprocess
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


def check_web_link(link: str) -> None:
    try:
        requests.head(link)
    except (requests.exceptions.ConnectionError, requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema):
        raise RuntimeError('Invalid web link')


def check_local_target_file_is_tracked(link: str) -> bool:
    try:
        subprocess.run('git ls-files --error-unmatch {}'.format(link.strip('/')),
                       shell=True,
                       check=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE
                       )
        return True
    except subprocess.CalledProcessError:
        return False


def check_local_link(link: str) -> None:
    if not os.path.isfile('.' + link):
        raise RuntimeError('Not a file')
    # It's important that the track check is last to avoid injection security issues
    if not check_local_target_file_is_tracked(link):
        raise RuntimeError('File not tracked in git')


def check_mail_link(link: str) -> None:
    if not bool(re.match(r'^mailto:.*@.*$', link)):
        raise RuntimeError('Invalid mailto link')


def check_link(data: Tuple[Path, str]) -> bool:
    path, link = data
    # Returns true if positively identified as a valid link
    # Raises exception with issue if fails check
    try:
        if link.startswith('/'):
            check_local_link(link)
        elif link.startswith('mailto'):
            check_mail_link(link)
        elif link.startswith('http'):
            check_web_link(link)
        else:
            raise RuntimeError('Unknown link')
        return True
    except RuntimeError as e:
        print('{}: {} [{}]'.format(str(path), str(e), link))
        return False


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
