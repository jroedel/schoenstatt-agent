"""Correct existing translations — the one path in this repository that overwrites.

Filling an empty row and replacing somebody's text are different acts.
`apply_translations.py` refuses to do the second at all. This file exists to do it
deliberately, for a reviewed list, and it is built so that it cannot do it by accident:

- **Every correction states the value it expects to find.** If the row does not currently
  hold that exact string, the correction is refused and reported. A translation that has
  moved since the list was written is a translation somebody else edited, and the list is
  stale rather than right.
- **Every correction carries a reason**, which is printed in the dry run, belongs in
  `docs/pt-audit.md` (or the equivalent) before anything is sent, and is now **sent to the
  API as `_note`**. It lands on the history row holding the text this write destroys, and is
  shown to humans on the phrase edit screen beside that text. Read in order, the notes on a
  phrase are a conversation: the next agent to consider the same row learns that the obvious
  rendering was already tried and abandoned, instead of trying it again.
- **`If-Match` on every write.** These are single-resource PATCHes precisely so the etag
  applies; the batch endpoint does not honour it.
- **Dry run by default.** `--write` is the only thing that sends anything.

    python3 tools/apply_corrections.py corrections.json            # dry run
    python3 tools/apply_corrections.py corrections.json --write

The corrections file is a list of objects:

    [{"phrase_id": 6565, "lang": "pt",
      "expect": "Codigorz de barra", "new": "Código de barras",
      "why": "typo; es has `Código de barras`"}]

Environment: SCHOENSTATT_ENV as everywhere else — unset or `test` is the capsule, only
the literal `production` is production.
"""

import json
import os
import sys
import urllib.error
import urllib.request

CREDS = os.path.expanduser("~/.config/schoenstatt/credentials.env")

# `JTranslate\Model\TranslationsTable::NOTE_LENGTH`. The server trims with `mb_substr`, so
# this is characters and not bytes. Not in `GET /api/v3/schema/phrase`, which is why it is a
# constant here rather than read at request time — see docs/api-change-requests.md §11 #2.
NOTE_MAX = 255


def load_env():
    if os.path.exists(CREDS):
        with open(CREDS, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    env = os.environ.get("SCHOENSTATT_ENV", "").strip() or "test"
    if env == "production":
        base, tok = os.environ.get("SCHOENSTATT_BASE_URL"), os.environ.get("SCHOENSTATT_TRANSLATOR_JWT")
    elif env == "test":
        base, tok = os.environ.get("SCHOENSTATT_BASE_URL_TEST"), os.environ.get("SCHOENSTATT_TRANSLATOR_JWT_TEST")
    else:
        sys.exit(f"SCHOENSTATT_ENV={env!r}: expected 'test' or 'production'")
    if not base or not tok:
        sys.exit(f"no base url / token for environment {env!r}")
    return env, base.rstrip("/"), tok


def call(base, tok, method, path, payload=None, etag=None):
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(base + path, data=data, method=method)
    r.add_header("Authorization", "Bearer " + tok)
    if data:
        r.add_header("Content-Type", "application/json")
    if etag:
        r.add_header("If-Match", etag)
    try:
        with urllib.request.urlopen(r, timeout=90) as resp:
            return resp.status, json.load(resp)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(body)
        except ValueError:
            return e.code, {"raw": body[:300]}


def main():
    path = sys.argv[1]
    write = "--write" in sys.argv
    env, base, tok = load_env()
    corrections = json.load(open(path, encoding="utf-8"))

    print(f"environment : {env}  ({base})")
    print(f"corrections : {len(corrections)} proposed\n")

    ready, refused = [], []
    for c in corrections:
        pid, lang = c["phrase_id"], c["lang"]
        status, p = call(base, tok, "GET", f"/api/v3/phrases/{pid}")
        if status != 200:
            refused.append((c, f"GET returned {status}"))
            continue
        cur = ((p["translations"].get(lang) or {}).get("text") or "")
        # Check "already applied" BEFORE "expect mismatch", so re-running a list that has
        # already been applied reports the reassuring answer rather than a scary one. This
        # is how a correction set is verified after the fact: every row should come back
        # "already correct".
        if cur == c["new"]:
            refused.append((c, "already correct — nothing to do"))
            continue
        if cur != c["expect"]:
            refused.append((c, f"holds {cur[:60]!r}, expected {c['expect'][:60]!r} "
                               f"— the row moved since this list was written, so the list "
                               f"is stale; re-check before forcing anything"))
            continue
        ready.append((c, p["meta"]["etag"], p["phrase"]))

    for c, etag, src in ready:
        print(f"  {c['phrase_id']:6} [{c['lang']}] {src[:48]!r}")
        print(f"         {c['expect']!r}")
        print(f"      -> {c['new']!r}")
        print(f"         {c['why']}")
    if refused:
        print(f"\n!! {len(refused)} refused:")
        for c, why in refused:
            print(f"     {c['phrase_id']} [{c['lang']}]: {why}")

    print(f"\n{len(ready)} ready, {len(refused)} refused")
    if not write:
        print("dry run — nothing sent. pass --write to apply.")
        return

    ok = fail = 0
    for c, etag, src in ready:
        # `why` was already required by this format and was only ever printed. Since
        # 2026-08-11 the API takes it: `_note` attaches to the history rows the write
        # produces — one per translation destroyed — and is shown to humans on the phrase
        # edit screen beside the version it replaced. The maintainers asked for a note on
        # every overwrite, and this tool is the only thing here that overwrites.
        #
        # Trimmed to NOTE_MAX rather than refused. The API trims too, for the same reason:
        # losing the tail of a justification is a smaller harm than refusing the correction
        # it justifies.
        body = {c["lang"]: c["new"], "_note": c["why"].strip()[:NOTE_MAX]}
        status, resp = call(base, tok, "PATCH", f"/api/v3/phrases/{c['phrase_id']}",
                            body, etag)
        if status == 200 and resp.get("changed"):
            ok += 1
            print(f"  {c['phrase_id']}: changed {resp['changed']}")
        elif status == 412:
            fail += 1
            print(f"  {c['phrase_id']}: 412 — the row moved between the read and the write, "
                  f"nothing written")
        else:
            fail += 1
            print(f"  {c['phrase_id']}: HTTP {status} {str(resp)[:160]}")
        if isinstance(resp, dict) and resp.get("warning"):
            print(f"      WARNING (row committed, not a retry): {resp['warning']}")
    print(f"\n{ok} corrected, {fail} failed")


if __name__ == "__main__":
    main()
