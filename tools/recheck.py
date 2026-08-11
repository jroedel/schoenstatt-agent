"""Drop any URL whose page does not agree that it is the page we claim.

The crawl recorded a URL's *route* from whatever page finally rendered, and
urllib follows redirects silently — so an association URL that 302s to `/it/`
was filed as a `welcome` page under the association's URL. Nothing about the
recorded row looked wrong.

The check that catches it needs no knowledge of which URLs are special: fetch
each one following redirects, and require that the URL did not move and that the
route in the page's own footer is the route the index claims. Disagreement means
the row is wrong, whatever the reason.
"""

import json
import re
import sys
import urllib.request
import urllib.error
import http.cookiejar

if len(sys.argv) < 2:
    sys.exit(f"usage: python3 {sys.argv[0]} <scratch-dir>")
SC = sys.argv[1]
BASE = "http://localhost:8080"

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
opener.addheaders = [("Cookie", "EU_COOKIE_LAW_CONSENT=true"), ("Accept-Language", "it")]
ROUTE_RE = re.compile(r"·\s*route\s+([A-Za-z0-9/_.-]+)\s*·")

verified = json.load(open(f"{SC}/verified.json"))
candidates = [c for c in verified if c["status"] == 200 and c["note"] != "sign-in required"]

kept, dropped = [], []
for c in candidates:
    url = c.get("final") or c["url"]
    try:
        with opener.open(BASE + url, timeout=15) as r:
            final_url = r.url.replace(BASE, "")
            html = r.read().decode("utf-8", "replace")
            status = r.status
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
    c["page_route"] = page_route
    c["status"] = status
    kept.append(c)

json.dump(kept, open(f"{SC}/kept.json", "w"), indent=1, ensure_ascii=False)
json.dump(dropped, open(f"{SC}/dropped.json", "w"), indent=1, ensure_ascii=False)
print(f"kept {len(kept)}, dropped {len(dropped)}")
for d in dropped[:8]:
    print("  drop", d["url"], "->", d["drop_reason"])
