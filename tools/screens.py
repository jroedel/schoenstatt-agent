"""Screen-by-screen: which untranslated phrases are visible on which Italian page,
and what element each one sits in.

The translation index answers "how many phrases were first seen on this route".
That is enough to plan, not enough to translate: a bare `Text` could be a heading, a
table column or a button, and Italian wants a different word for each. So this pass
opens the Italian page and finds each backlog phrase *in the markup*, recording the
enclosing element, the nearest heading, and whether the string sits inside a link, a
button, a label or a table header.

Reads only. Talks to the capsule and to the API; writes a JSON report to the scratch
directory named on the command line.

    python3 tools/screens.py /path/to/scratch

Inputs it expects in that directory:
    it_backlog.json   the API's untranslatedIn=it collection, dumped whole

Output:
    screens.json      one record per page, each listing the phrases visible on it
"""

import html
import json
import os
import re
import sys
import urllib.request
import http.cookiejar
from collections import defaultdict

BASE = os.environ.get("SCHOENSTATT_BASE_URL_TEST", "http://localhost:8080")
SCRATCH = sys.argv[1] if len(sys.argv) > 1 else "."
INDEX = os.path.join(os.path.dirname(__file__), "..", "docs", "translation-index.md")

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
opener.addheaders = [
    ("Cookie", "EU_COOKIE_LAW_CONSENT=true"),
    ("User-Agent", "schoenstatt-agent-screens/0.1"),
]

ROUTE_RE = re.compile(r"·\s*route\s+([A-Za-z0-9/_.-]+)\s*·")
# `| 1 | `/it/literature` | `publications` | 75 | |`
ROW_RE = re.compile(r"^\|\s*\d+\s*\|\s*`(/it/[^`]*)`\s*\|\s*`([^`]*)`\s*\|\s*(\d+)\s*\|")
SCRIPT_RE = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def fetch(path, lang=None):
    """Fetch a page. `lang` swaps the locale prefix, so /it/x can be read as /en/x."""
    if lang:
        path = re.sub(r"^/[a-z]{2}(/|$)", f"/{lang}\\1", path)
    try:
        with opener.open(BASE + path, timeout=20) as r:
            if "text/html" not in r.headers.get("Content-Type", ""):
                return None
            return r.read().decode("utf-8", "replace")
    except Exception:  # noqa: BLE001
        return None


def index_urls():
    with open(INDEX, encoding="utf-8") as fh:
        rows = [ROW_RE.match(line) for line in fh]
    return [(m.group(1), m.group(2), int(m.group(3))) for m in rows if m]


def strip(doc):
    doc = COMMENT_RE.sub(" ", SCRIPT_RE.sub(" ", doc))
    return html.unescape(re.sub(r"<[^>]+>", " ", doc))


def context_of(doc, idx, needle):
    """What element is this occurrence sitting in, and under which heading?

    Walks backwards from the match to the tag that opens it, and backwards again to
    the nearest preceding heading. Both are heuristics on flat markup — good enough to
    tell a `<th>` from a `<button>`, which is the distinction that changes the Italian.
    """
    before = doc[:idx]
    tags = re.findall(r"<(/?)([a-zA-Z][a-zA-Z0-9]*)\b([^>]*)>", before)
    stack = []
    for closing, name, attrs in tags:
        name = name.lower()
        if name in ("br", "img", "input", "hr", "meta", "link"):
            if name == "input":
                stack.append((name, attrs))
            continue
        if closing:
            for i in range(len(stack) - 1, -1, -1):
                if stack[i][0] == name:
                    del stack[i:]
                    break
        else:
            stack.append((name, attrs))
    enclosing = [n for n, _ in stack[-4:]]
    attrs = stack[-1][1] if stack else ""

    heads = re.findall(r"<h([1-6])[^>]*>(.*?)</h\1>", before, re.S | re.I)
    heading = re.sub(r"\s+", " ", strip(heads[-1][1])).strip() if heads else ""

    # a slice of visible text around the match, for reading it in place
    win = strip(doc[max(0, idx - 260): idx + len(needle) + 260])
    win = re.sub(r"\s+", " ", win).strip()
    return {
        "enclosing": "/".join(enclosing),
        "attrs": re.sub(r"\s+", " ", attrs).strip()[:120],
        "heading": heading[:120],
        "nearby": win[:400],
    }


def main():
    backlog = json.load(open(os.path.join(SCRATCH, "it_backlog.json"), encoding="utf-8"))
    # longest first, so `Contact Info` is attributed before `Contact`
    by_len = sorted(backlog, key=lambda p: -len(p["phrase"]))
    # only strings that could plausibly be matched in markup
    candidates = [p for p in by_len if 2 <= len(p["phrase"]) <= 400]

    seen_on = defaultdict(list)
    screens = []
    urls = index_urls()
    print(f"{len(urls)} pages from the index, {len(candidates)} candidate phrases")

    for n, (url, route, claimed) in enumerate(urls, 1):
        doc = fetch(url)
        if doc is None:
            screens.append({"url": url, "route": route, "error": "not fetched"})
            print(f"  [{n:3}/{len(urls)}] {url} — NOT FETCHED")
            continue
        footer = ROUTE_RE.search(doc)
        found = []
        for p in candidates:
            needle = p["phrase"]
            # match the escaped form as it appears in markup
            for form in {html.escape(needle, quote=False), needle}:
                idx = doc.find(form)
                if idx != -1:
                    found.append({
                        "phrase_id": p["phraseId"],
                        "phrase": needle,
                        "text_domain": p["textDomain"],
                        "origin_route": p["context"]["originRoute"],
                        "en": (p["translations"]["en"]["text"] or ""),
                        "es": (p["translations"]["es"]["text"] or ""),
                        "pt": (p["translations"]["pt"]["text"] or ""),
                        "de": (p["translations"]["de"]["text"] or ""),
                        **context_of(doc, idx, form),
                    })
                    seen_on[p["phraseId"]].append(url)
                    break
        screens.append({
            "url": url,
            "route": route,
            "footer_route": footer.group(1) if footer else None,
            "claimed_n": claimed,
            "visible_untranslated": found,
        })
        print(f"  [{n:3}/{len(urls)}] {url} — {len(found)} visible")

    out = {
        "base": BASE,
        "screens": screens,
        "coverage": {
            "phrases_seen_on_a_page": len(seen_on),
            "backlog": len(backlog),
        },
    }
    path = os.path.join(SCRATCH, "screens.json")
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n{len(seen_on)} of {len(backlog)} backlog phrases were visible on at least one page")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
