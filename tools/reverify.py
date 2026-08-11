"""Re-run the route-agreement check over the already-verified list.

Same rule as recheck.py: fetch each URL following redirects, and keep it only if
the URL did not move and the route in the page's own footer is the route the index
claims. Run again after the site changes, because a page that stopped existing or
started redirecting looks entirely normal in a stale index.
"""

import json
import re
import sys
import urllib.request
import http.cookiejar

if len(sys.argv) < 2:
    sys.exit(f"usage: python3 {sys.argv[0]} <scratch-dir>")
SC = sys.argv[1]
BASE = "http://localhost:8080"

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
opener.addheaders = [("Cookie", "EU_COOKIE_LAW_CONSENT=true"), ("Accept-Language", "it")]
ROUTE_RE = re.compile(r"·\s*route\s+([A-Za-z0-9/_.-]+)\s*·")

candidates = json.load(open(f"{SC}/final_urls.json"))

kept, dropped = [], []
for c in candidates:
    url = c.get("final") or c["url"]
    try:
        with opener.open(BASE + url, timeout=20) as r:
            final_url = r.url.replace(BASE, "")
            html = r.read().decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        c["drop_reason"] = f"unreachable ({exc})"
        dropped.append(c)
        continue

    m = ROUTE_RE.search(html)
    page_route = m.group(1) if m else None
    if page_route and page_route.endswith(".locale"):
        page_route = page_route[:-7]

    if final_url.rstrip("/") != url.rstrip("/"):
        c["drop_reason"] = f"redirects to {final_url}"
        dropped.append(c)
        continue
    if page_route != c["route"]:
        c["drop_reason"] = f"page reports route {page_route!r}, index claims {c['route']!r}"
        dropped.append(c)
        continue

    c["final"] = final_url
    kept.append(c)

json.dump(kept, open(f"{SC}/final_urls2.json", "w"), indent=1, ensure_ascii=False)
json.dump(dropped, open(f"{SC}/dropped2.json", "w"), indent=1, ensure_ascii=False)
print(f"kept {len(kept)}, dropped {len(dropped)}")
for d in dropped:
    print("  drop", d["url"], "->", d["drop_reason"])
