"""Take rows off the translator's worklist, resolving ids against the target site.

**Dry run by default.** `--write` is the only thing that sends anything.

    python3 tools/apply_retirements.py retirements.json            # dry run
    python3 tools/apply_retirements.py retirements.json --write

Input is a list of `{text_domain, phrase, note}` objects — **keyed on the pair, never on
an id**, for the same reason `apply_translations.py` is: an id means nothing outside the
environment it was read from, and on 2026-08-10 six capsule ids held a *different phrase*
on production. A source string is the same string everywhere. The pair rather than the
string alone, because `Update on advances` is dead copy in `Application` and live text in
`SionModel`, and one of those is a retirement and the other is not.

This exists because `curl` was the wrong tool for the job once already. The first two
retirements were sent by hand with a 270-character note against a 255 limit, and the
server trimmed it mid-word — losing exactly the clause that said what to do if the phrase
came back, which is the part a retirement note exists for. See `docs/retire-queue.md`.

## What it refuses, and why each guard is here

- **A pair matching no live row**, or matching more than one. Reported, never guessed at.
- **An empty or non-string note.** The server answers 422, but failing here names the pair.
- **A row added after the caller was fixed.** `--added-before` is a cutoff; a row filed
  after the fix that was supposed to stop filing it is evidence the fix regressed, and
  `docs/retire-queue.md` says that belongs in a change request *before* it belongs in a
  retirement. Warned by default, fatal with `--strict-added-before`.

## The sibling check is the point of this tool

`UNIQUE (project, text_domain, phrase_hash)` makes the same string in two text domains two
rows, which is what the breadcrumb's two-domain lookup produces — a pair at a time. **Retiring
one does not retire the other**, so a string cleared through one domain keeps asking for work
through the other, and the untranslated count does not move by what you expected. Documented at
`retirement.siblings` in the phrase schema and in `docs/api-v3.md`.

So before sending anything this tool lists every live row of every string in the batch and
**fails if one of them is not in the batch**. Overriding that is `--allow-partial-siblings`,
which is right when the sibling is a designed row — an association name in the `Schoenstatt`
domain is `IsNameTranslateable`'s feature, and its `Application`/`default` copies are the
breadcrumb residue.

A note is per row, not per string: both entries land in one shared thread, so two copies of
one sentence read worse than one saying which domain this row is and why.

Environment: `SCHOENSTATT_ENV` selects exactly as the MCP server does — unset or `test` is
the capsule, and only the literal `production` is production. Credentials come from
`~/.config/schoenstatt/credentials.env`.
"""

import json
import os
import sys
import urllib.error
import urllib.request

CREDS = os.path.expanduser("~/.config/schoenstatt/credentials.env")
NOTE_MAX_FALLBACK = 255


def load_env():
    """Read the credentials file the same way the MCP server does."""
    if os.path.exists(CREDS):
        with open(CREDS, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

    env = os.environ.get("SCHOENSTATT_ENV", "").strip() or "test"
    if env == "production":
        base = os.environ.get("SCHOENSTATT_BASE_URL")
        tok = os.environ.get("SCHOENSTATT_TRANSLATOR_JWT")
    elif env == "test":
        base = os.environ.get("SCHOENSTATT_BASE_URL_TEST")
        tok = os.environ.get("SCHOENSTATT_TRANSLATOR_JWT_TEST")
    else:
        sys.exit(f"SCHOENSTATT_ENV={env!r}: expected 'test' or 'production'")
    if not base or not tok:
        sys.exit(f"no base url / translator token for environment {env!r}")
    return env, base.rstrip("/"), tok


def call(base, tok, method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(base + path, data=data, method=method)
    req.add_header("Authorization", "Bearer " + tok)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(body)
        except ValueError:
            return e.code, {"raw": body[:500]}


def note_limit(base):
    """The note's length bound, from the live schema rather than from this file.

    Trimming matches the server: it trims rather than refusing, and losing the tail of a
    justification is a smaller harm than refusing the retirement it justifies. But the trim
    is *reported*, because the incident that motivated this tool was a silent one.
    """
    try:
        req = urllib.request.Request(base + "/api/v3/schema/phrase")
        schema = json.load(urllib.request.urlopen(req, timeout=60))
        return int(((schema.get("writable") or {}).get("note") or {}).get(
            "maxLength") or NOTE_MAX_FALLBACK)
    except Exception:
        return NOTE_MAX_FALLBACK


def fetch_live(base, tok):
    """Every live phrase on the target, so ids are resolved from the target itself."""
    items, off = [], 0
    while True:
        status, d = call(base, tok, "GET", f"/api/v3/phrases?limit=500&offset={off}")
        if status != 200:
            sys.exit(f"GET /api/v3/phrases failed: {status} {d}")
        items += d["items"]
        off += 500
        if len(items) >= d["total"]:
            return items


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = sys.argv[1]
    write = "--write" in sys.argv
    allow_partial = "--allow-partial-siblings" in sys.argv
    strict_added = "--strict-added-before" in sys.argv
    cutoff = None
    if "--added-before" in sys.argv:
        cutoff = sys.argv[sys.argv.index("--added-before") + 1]

    candidates = json.load(open(path, encoding="utf-8"))
    env, base, tok = load_env()
    limit = note_limit(base)
    print(f"environment {env} -> {base}   note limit {limit}   "
          f"{len(candidates)} candidates from {path}")

    live = fetch_live(base, tok)
    by_pair, by_text = {}, {}
    for p in live:
        by_pair.setdefault((p["textDomain"], p["phrase"]), []).append(p)
        by_text.setdefault(p["phrase"], []).append(p)
    print(f"{len(live)} live phrases on the target")

    # ---- resolve, and refuse anything ambiguous ------------------------------------
    resolved, problems = [], []
    for c in candidates:
        td, ph = c.get("text_domain"), c.get("phrase")
        note = (c.get("note") or "")
        if not isinstance(note, str) or not note.strip():
            problems.append(f"({td}, {ph[:40]!r}): note is empty or not a string. A "
                            f"retirement's note is the entire record of the judgement.")
            continue
        rows = by_pair.get((td, ph), [])
        if not rows:
            problems.append(f"({td}, {ph[:40]!r}): matches no live row on {env}. Not "
                            f"guessed at — it may be retired already, or the string may "
                            f"differ by whitespace, which is part of the key.")
            continue
        if len(rows) > 1:
            problems.append(f"({td}, {ph[:40]!r}): matches {len(rows)} live rows "
                            f"{[r['phraseId'] for r in rows]}, which the unique constraint "
                            f"says cannot happen. Refusing rather than picking one.")
            continue
        row = rows[0]
        trimmed = note.strip()
        if len(trimmed) > limit:
            print(f"  NOTE TRIMMED {len(trimmed)} -> {limit} for {row['phraseId']}: "
                  f"...{trimmed[limit - 40:limit]!r} | LOST {trimmed[limit:]!r}")
            trimmed = trimmed[:limit]
        resolved.append({"id": row["phraseId"], "text_domain": td, "phrase": ph,
                         "note": trimmed, "added_on": row["meta"]["addedOn"]})

    # ---- the sibling check ---------------------------------------------------------
    batch_ids = {r["id"] for r in resolved}
    for r in resolved:
        siblings = [s for s in by_text[r["phrase"]] if s["phraseId"] != r["id"]]
        left = [s for s in siblings if s["phraseId"] not in batch_ids]
        if left:
            msg = (f"{r['id']} ({r['text_domain']}) {r['phrase'][:40]!r}: "
                   f"{len(left)} live sibling row(s) NOT in this batch — "
                   + ", ".join(f"{s['phraseId']} in {s['textDomain']}" for s in left)
                   + ". Retiring one row does not retire its sibling, so the string keeps "
                     "asking for work through the domain left behind.")
            if allow_partial:
                print(f"  sibling left live (allowed): {msg}")
            else:
                problems.append(msg)

    # ---- the regression check ------------------------------------------------------
    if cutoff:
        for r in resolved:
            if r["added_on"] >= cutoff:
                msg = (f"{r['id']} {r['phrase'][:40]!r} was added {r['added_on']}, at or "
                       f"after {cutoff}. A row filed after the caller was fixed is evidence "
                       f"the fix regressed, and belongs in a change request before it "
                       f"belongs in a retirement.")
                if strict_added:
                    problems.append(msg)
                else:
                    print(f"  WARNING: {msg}")

    if problems:
        print(f"\n{len(problems)} problem(s) — nothing sent:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)

    print(f"\n{len(resolved)} rows resolved, {len({r['phrase'] for r in resolved})} distinct "
          f"strings:")
    for r in sorted(resolved, key=lambda r: (r["phrase"], r["text_domain"])):
        print(f"  {r['id']:>6} {r['text_domain']:<12} added={r['added_on'][:16]} "
              f"{r['phrase'][:52]!r}")
        print(f"         note: {r['note']}")

    if not write:
        print("\ndry run — nothing sent. pass --write to apply.")
        return

    print()
    changed = unchanged = failed = 0
    for r in resolved:
        status, body = call(base, tok, "POST", f"/api/v3/phrases/{r['id']}/retire",
                            {"_note": r["note"]})
        if status != 200:
            failed += 1
            print(f"  FAILED {r['id']} ({r['text_domain']}): {status} {body}")
            continue
        # `changed: false` means it was already retired — a 200, and no second history
        # entry, so a retry cannot forge a second judgement.
        if body.get("changed"):
            changed += 1
        else:
            unchanged += 1
            print(f"  already retired: {r['id']} ({r['text_domain']})")
    print(f"\n{changed} retired, {unchanged} already retired, {failed} failed")

    # ---- close the loop -----------------------------------------------------------
    #
    # A retired row is invisible in the collection, so the retirement has to be read back
    # or nothing would notice one that came back.
    #
    # **Read it back per id, not out of `?onlyRetired=1`.** The first version of this
    # function asked for `?onlyRetired=1&limit=500` and compared the batch against the
    # answer — which reported `0/2 present` for two rows that were both correctly retired,
    # because production has 4,475 retired rows and 500 is one page of them. A paging bug
    # that reads as "the retirement silently failed" is worse than no check, and paging
    # through nine pages to find two ids is worse than asking for the two ids.
    # `GET /api/v3/phrases/{id}` answers for a retired row — that is the documented
    # guarantee that an old link does not 404 — and `meta.retiredOn` is the flag.
    print()
    for r in resolved:
        status, d = call(base, tok, "GET", f"/api/v3/phrases/{r['id']}")
        if status != 200:
            print(f"  could not read back {r['id']}: {status} {d}")
            continue
        if not d["meta"].get("retiredOn"):
            print(f"  NOT RETIRED: {r['id']} ({r['text_domain']}) {r['phrase'][:40]!r} is "
                  f"live. A row live again with a retire entry and no unretire after it "
                  f"came back on its own, which means the retirement was wrong — read "
                  f"{d['meta'].get('history')} and treat it as a defect report at the "
                  f"caller, not a row to retire again.")
    print(f"read back {len(resolved)} rows; any not retired are named above")


if __name__ == "__main__":
    main()
