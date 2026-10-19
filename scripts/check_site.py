#!/usr/bin/env python3
"""Check a built Jekyll site for broken internal references and oversized files.

Usage:
    python3 scripts/check_site.py [SITE_DIR] [--max-mb 10] [--site-url https://olicar-del.github.io]

Every <a href>, <img src/srcset>, <video>/<source>, <iframe>, <script>, <link> and
og:image/twitter:image URL that points at this site must resolve to a file in
SITE_DIR. External links are not fetched. Exits with status 1 if anything is broken
or any file is larger than --max-mb.
"""
import argparse
import os
import posixpath
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urljoin, urlsplit

BASE = "https://site.invalid"
URL_ATTRS = {
    "a": ["href"],
    "img": ["src", "srcset"],
    "source": ["src", "srcset"],
    "video": ["src", "poster"],
    "audio": ["src"],
    "iframe": ["src"],
    "script": ["src"],
    "link": ["href"],
}
SKIP_SCHEMES = ("mailto:", "tel:", "javascript:", "data:")
SKIP_LINK_RELS = {"preconnect", "dns-prefetch"}


class RefCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs = []  # (tag, attr, value)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta":
            prop = attrs.get("property") or attrs.get("name") or ""
            if prop in ("og:image", "twitter:image") and attrs.get("content"):
                self.refs.append((tag, prop, attrs["content"]))
            return
        if tag == "link" and SKIP_LINK_RELS & set((attrs.get("rel") or "").split()):
            return
        for attr in URL_ATTRS.get(tag, []):
            value = attrs.get(attr)
            if not value:
                continue
            if attr == "srcset":
                for candidate in value.split(","):
                    url = candidate.strip().split(" ")[0]
                    if url:
                        self.refs.append((tag, attr, url))
            else:
                self.refs.append((tag, attr, value.strip()))

    handle_startendtag = handle_starttag


def target_exists(site_dir, url_path):
    path = posixpath.normpath(unquote(url_path)).lstrip("/")
    full = os.path.join(site_dir, *path.split("/")) if path not in ("", ".") else site_dir
    if os.path.isfile(full):
        return True
    if os.path.isdir(full):
        return os.path.isfile(os.path.join(full, "index.html"))
    return os.path.isfile(full + ".html")


def page_url(site_dir, file_path):
    rel = os.path.relpath(file_path, site_dir).replace(os.sep, "/")
    return BASE + "/" + rel


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("site_dir", nargs="?", default="_site")
    parser.add_argument("--max-mb", type=float, default=10.0)
    parser.add_argument("--site-url", default="https://olicar-del.github.io")
    args = parser.parse_args()

    site_dir = os.path.abspath(args.site_dir)
    own_host = urlsplit(args.site_url).netloc.lower()
    broken, oversized = [], []
    pages = checked = 0

    for root, _dirs, files in os.walk(site_dir):
        for name in files:
            file_path = os.path.join(root, name)
            size_mb = os.path.getsize(file_path) / 1_000_000
            if size_mb > args.max_mb:
                oversized.append((os.path.relpath(file_path, site_dir), size_mb))
            if not name.endswith(".html"):
                continue
            pages += 1
            with open(file_path, encoding="utf-8", errors="replace") as fh:
                collector = RefCollector()
                collector.feed(fh.read())
            base = page_url(site_dir, file_path)
            for tag, attr, value in collector.refs:
                if not value or value.startswith("#") or value.lower().startswith(SKIP_SCHEMES):
                    continue
                if "{{" in value or "{%" in value:
                    broken.append((base, tag, attr, value, "unrendered Liquid"))
                    continue
                absolute = urljoin(base, value)
                parts = urlsplit(absolute)
                host = parts.netloc.lower()
                if host not in ("site.invalid", own_host):
                    continue  # external link: not checked
                checked += 1
                if not target_exists(site_dir, parts.path or "/"):
                    broken.append((base, tag, attr, value, "missing"))

    print(f"Checked {checked} internal references across {pages} HTML pages.")
    if broken:
        print(f"\nBROKEN ({len(broken)}):")
        for base, tag, attr, value, why in sorted(set(broken)):
            print(f"  {base[len(BASE):]}  <{tag} {attr}> {value}  [{why}]")
    if oversized:
        print(f"\nOVER {args.max_mb:g} MB ({len(oversized)}):")
        for rel, size_mb in sorted(oversized, key=lambda item: -item[1]):
            print(f"  {size_mb:8.1f} MB  {rel}")
    if broken or oversized:
        return 1
    print("No broken internal references or oversized files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
