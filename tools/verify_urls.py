"""Verify every candidate URL and record what it actually does.

An index of URLs nobody checked is worse than no index: a 302 to the sign-in page
looks like a page until you open it. Each URL is fetched once, following
redirects, and classified.
"""

import json
import csv
import sys
import urllib.request
import urllib.error
import http.cookiejar
import re

if len(sys.argv) < 2:
    sys.exit(f"usage: python3 {sys.argv[0]} <scratch-dir>")
SC = sys.argv[1]
BASE = "http://localhost:8080"

jar = http.cookiejar.CookieJar()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, newurl, headers, fp)


plain = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
plain.addheaders = [("Cookie", "EU_COOKIE_LAW_CONSENT=true"), ("Accept-Language", "it")]
norod = urllib.request.build_opener(NoRedirect, urllib.request.HTTPCookieProcessor(jar))
norod.addheaders = plain.addheaders

ROUTE_RE = re.compile(r"·\s*route\s+([A-Za-z0-9/_.-]+)\s*·")

candidates = []
for f, kind in [("assoc_urls", "association"), ("pub_urls", "publication"), ("text_urls", "text")]:
    with open(f"{SC}/{f}.tsv") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            candidates.append({
                "url": row["url"], "route": row["route"],
                "own_phrase": row["own_phrase"], "src": row["src"], "kind": kind,
            })

crawl = json.load(open(f"{SC}/crawl2.json"))
for url, meta in crawl.items():
    if meta.get("db_route"):
        candidates.append({
            "url": url, "route": meta["db_route"],
            "own_phrase": "", "src": "", "kind": "listing",
        })

seen, out = set(), []
for c in candidates:
    if c["url"] in seen:
        continue
    seen.add(c["url"])

    # First: does it redirect, and where?
    final, note = c["url"], ""
    try:
        norod.open(BASE + c["url"], timeout=15).read(1)
        status = 200
    except urllib.error.HTTPError as e:
        status = e.code
        if status in (301, 302, 303, 307, 308):
            target = e.reason if isinstance(e.reason, str) else e.headers.get("Location", "")
            if "/user/login" in target:
                c.update(status=status, final=c["url"], note="sign-in required")
                out.append(c)
                continue
            final = target
            note = f"redirects to {target}"
        else:
            c.update(status=status, final=c["url"], note="error")
            out.append(c)
            continue
    except Exception:
        c.update(status=0, final=c["url"], note="unreachable")
        out.append(c)
        continue

    # Then fetch the (possibly redirected) page and read its route from the footer.
    try:
        with plain.open(BASE + final, timeout=15) as r:
            html = r.read().decode("utf-8", "replace")
            status = r.status
        m = ROUTE_RE.search(html)
        page_route = m.group(1) if m else None
        if page_route and page_route.endswith(".locale"):
            page_route = page_route[:-7]
    except Exception:
        page_route = None

    c.update(status=status, final=final, note=note, page_route=page_route)
    out.append(c)

json.dump(out, open(f"{SC}/verified.json", "w"), indent=1, ensure_ascii=False)

ok = [c for c in out if c["status"] == 200 and c["note"] != "sign-in required"]
login = [c for c in out if c["note"] == "sign-in required"]
print(f"checked {len(out)}: {len(ok)} usable, {len(login)} sign-in required, "
      f"{len(out) - len(ok) - len(login)} other")
