"""Second pass: breadth over routes rather than depth into one.

The first crawl spent 470 of 500 fetches inside two detail-page routes. The
index wants one or two good example URLs per route, not 263 compositions, so
this caps how many pages any single route may contribute and keeps walking.

Route names in the page footer carry a `.locale` suffix that the database's
origin_route column does not, so both forms are recorded.
"""

import re
import sys
import time
import json
import urllib.parse
import urllib.request
import http.cookiejar
from collections import deque, defaultdict

BASE = "http://localhost:8080"

if len(sys.argv) < 2:
    sys.exit(f"usage: python3 {sys.argv[0]} <scratch-dir> [max-fetches] [per-route]")
SC = sys.argv[1]
MAX_FETCHES = int(sys.argv[2]) if len(sys.argv) > 2 else 900
PER_ROUTE = int(sys.argv[3]) if len(sys.argv) > 3 else 4

SEEDS = [
    "/it/", "/it/shrines", "/it/wayside-shrines", "/it/literature", "/it/music",
    "/it/developers", "/it/texts", "/it/publications", "/it/libraries",
    "/it/associations", "/it/persons", "/it/books", "/it/blog", "/it/dictionary",
    "/it/assignments", "/it/user/login", "/it/user/register",
]

FORBIDDEN = re.compile(
    r"/(delete|do-work|logout|sign-out|checkout|check-in|send-book-notices|"
    r"import|export|activate|verify|resend|revoke|merge|upload-cover|"
    r"copy-to-main-corpus|create-new-edition)(/|$|\?)",
    re.I,
)

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
opener.addheaders = [
    ("Cookie", "EU_COOKIE_LAW_CONSENT=true"),
    ("User-Agent", "schoenstatt-agent-indexer/0.1"),
    ("Accept-Language", "it"),
]

ROUTE_RE = re.compile(r"·\s*route\s+([A-Za-z0-9/_.-]+)\s*·")
HREF_RE = re.compile(r'href="([^"#]+)"')
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)


def fetch(path):
    try:
        with opener.open(BASE + path, timeout=15) as r:
            if "text/html" not in r.headers.get("Content-Type", ""):
                return None, r.status
            return r.read().decode("utf-8", "replace"), r.status
    except Exception:  # noqa: BLE001
        return None, None


def normalise(href, current):
    href = urllib.parse.urljoin(current, href)
    parts = urllib.parse.urlsplit(href)
    if parts.netloc and parts.netloc != "localhost:8080":
        return None
    path = parts.path + (("?" + parts.query) if parts.query else "")
    if not path.startswith("/it"):
        return None
    return path


seen, results = set(), {}
per_route = defaultdict(int)
queue = deque(SEEDS)
fetches = 0

while queue and fetches < MAX_FETCHES:
    path = queue.popleft()
    if path in seen or FORBIDDEN.search(path):
        continue
    seen.add(path)
    fetches += 1

    html, status = fetch(path)
    if html is None:
        continue

    m = ROUTE_RE.search(html)
    route = m.group(1) if m else None
    db_route = route[:-7] if route and route.endswith(".locale") else route

    # Keep walking links even from a route we have enough of; the links are how
    # we reach routes we have none of.
    if route is None or per_route[db_route] < PER_ROUTE:
        t = TITLE_RE.search(html)
        results[path] = {
            "route": route,
            "db_route": db_route,
            "title": re.sub(r"\s+", " ", t.group(1)).strip() if t else "",
            "status": status,
        }
        if db_route:
            per_route[db_route] += 1

    for href in HREF_RE.findall(html):
        nxt = normalise(href, BASE + path)
        if nxt and nxt not in seen and not FORBIDDEN.search(nxt):
            queue.append(nxt)
    time.sleep(0.01)

out = f"{SC}/crawl2.json"
json.dump(results, open(out, "w"), indent=1, ensure_ascii=False)
print(f"fetched {fetches}, kept {len(results)}, distinct routes {len(per_route)}")
