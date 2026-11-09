#!/usr/bin/env python3
"""Fetches all news feeds and writes site/feeds.json for the CW News web app.

Runs on GitHub Actions every few minutes. Uses only the Python standard library.
"""
import html
import json
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET

FEEDS = [
    ("bbc-top", "BBC – Top stories", "https://feeds.bbci.co.uk/news/rss.xml"),
    ("bbc-world", "BBC – World", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("bbc-uk", "BBC – UK", "https://feeds.bbci.co.uk/news/uk/rss.xml"),
    ("bbc-business", "BBC – Business", "https://feeds.bbci.co.uk/news/business/rss.xml"),
    ("bbc-tech", "BBC – Technology", "https://feeds.bbci.co.uk/news/technology/rss.xml"),
    ("bbc-science", "BBC – Science & Environment", "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml"),
    ("bbc-health", "BBC – Health", "https://feeds.bbci.co.uk/news/health/rss.xml"),
    ("tvn24-latest", "PL · TVN24 – Najnowsze", "https://tvn24.pl/najnowsze.xml"),
    ("tvn24-gnews", "PL · TVN24 (via Google News)", "https://news.google.com/rss/search?q=site:tvn24.pl&hl=pl&gl=PL&ceid=PL:pl"),
    ("onet", "PL · Onet – Wiadomości", "https://wiadomosci.onet.pl/.feed"),
    ("polsat-all", "PL · Polsat News – Wszystkie", "https://www.polsatnews.pl/rss/wszystkie.xml"),
    ("polsat-pl", "PL · Polsat News – Polska", "https://www.polsatnews.pl/rss/polska.xml"),
    ("polsat-world", "PL · Polsat News – Świat", "https://www.polsatnews.pl/rss/swiat.xml"),
]

MAX_ITEMS = 40


def clean(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def local(tag):
    return tag.rsplit("}", 1)[-1]


def child_text(el, *names):
    for c in el:
        if local(c.tag) in names:
            if local(c.tag) == "link" and c.get("href"):
                return c.get("href")
            return "".join(c.itertext())
    return ""


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "CWNews/1.0 (+github pages)"})
    with urllib.request.urlopen(req, timeout=25) as r:
        root = ET.fromstring(r.read())
    items = []
    for el in root.iter():
        if local(el.tag) not in ("item", "entry"):
            continue
        title = clean(child_text(el, "title"))
        if not title:
            continue
        desc = clean(child_text(el, "description", "summary"))
        uid = child_text(el, "guid", "id") or child_text(el, "link") or title
        if "news.google.com" in url:
            title = re.sub(r"\s+-\s+[^-]+$", "", title)  # drop " - Source"
            desc = ""                                     # Google descriptions are link lists
        items.append({"id": uid.strip(), "title": title, "desc": desc})
        if len(items) >= MAX_ITEMS:
            break
    return items


def main(out_path):
    data = {"updated": int(time.time()), "feeds": []}
    for key, name, url in FEEDS:
        try:
            items = fetch(url)
            err = None
        except Exception as e:  # keep going; one broken feed must not break the rest
            items, err = [], f"{type(e).__name__}: {e}"
        print(f"{key:14} {len(items):3} items {err or ''}")
        data["feeds"].append({"key": key, "name": name, "items": items, "error": err})
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "site/feeds.json")
