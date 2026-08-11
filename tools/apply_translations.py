"""Write the Italian translations to the site, in batches, with the contract enforced.

Reads the per-batch translation files (source string → Italian), **resolves the phrase
ids against the target environment at run time**, and PATCHes. **Dry run by default** —
it prints what it would write and exits. `--write` is the only thing that sends anything.

## Phrase ids are per-environment. Never carry them between sites.

This is the expensive lesson in this file. The capsule and production share a database
lineage, so most ids agree — and that is exactly what makes it dangerous. Compared on
2026-08-10: of 1,795 phrases on production and 1,816 in the capsule, **68 ids differed**,
and six of them were live ids holding a *different phrase*. Reusing the capsule's ids
would have written the Italian for `Is draft?` onto production's `API Tokens`, and five
more like it — silently, and with no way to undo it.

So the id map is built from the target itself, keyed on the source string, every run.
A source string is the same string in every environment; an id is not.

Two guards follow from that and are not optional:

- **Only rows whose Italian is empty are written.** Filling a gap and overwriting
  somebody's work are different acts, and only the first is authorised here.
- **A source string that matches nothing on the target is reported, not guessed at.**

The guards here are the same ones `cmd/schoenstatt-mcp` applies, restated because this
path bypasses it: no empty values, nothing over the length the schema reports, at most
200 phrases per batch, and language codes read from the live schema rather than assumed.
A batch recompiles the site's catalogs once instead of once per phrase.

**Read the dry run before passing `--write`.** Since 2026-08-11 a write that replaces text is
recoverable through `GET /api/v3/phrases/{id}/history`; this tool never replaces text anyway,
because it excludes rows that already have a value.

**A JSON `null` in a PATCH body retracts a translation.** `""` leaves a language alone but
`null` empties it, and no call site that produces one looks like a deletion. This tool asserts
that every value it sends is a non-empty string, immediately before sending — see `send()`.
That assertion is cheap and the failure it prevents is not.

    python3 tools/apply_translations.py /path/to/scratch            # dry run
    python3 tools/apply_translations.py /path/to/scratch --write

Environment: SCHOENSTATT_ENV selects the environment exactly as the MCP server does —
unset or `test` uses the capsule (`*_TEST`), and only the literal `production` uses the
production pair. Credentials come from ~/.config/schoenstatt/credentials.env.
"""

import glob
import json
import os
import sys
import urllib.error
import urllib.request
from collections import defaultdict

BATCH = 200
CREDS = os.path.expanduser("~/.config/schoenstatt/credentials.env")


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


def assert_no_retractions(payload):
    """Refuse to send anything that could remove a translation.

    **The API changed under this function on 2026-08-11 and it is worth being precise about
    which way.** A bare `null` used to BE the retraction. It is now a `422` naming the
    alternative, and removal takes an explicit `{"_retract": ["de"]}` — adopted at this
    repository's own suggestion (`api-change-requests-response.md` §11), on the argument that a
    `null` is what a serializer emits for an absent optional field, what a dict comprehension
    produces when one lookup misses, and what `json.dumps` does with a Python `None`. None of
    those look like a deletion at the call site and all of them were one.

    So this function is no longer the last line of defence against a null — the server is. It
    is kept, and still refuses one, for two reasons. It fails on this side with a message that
    says which phrase and which language, where the server's 422 fails a whole batch. And a
    null in a body built by this tool is a bug in this tool whichever way the server treats it.

    `_retract` is refused outright. This tool only ever fills empty rows, so it has no business
    naming a language for removal, and `_retract` is now the one key that can destroy a
    translation. `_note` and any other reserved key is passed through.
    """
    for pid, langs in (payload.get("phrases") or {}).items() if "phrases" in payload else [(None, payload)]:
        where = f"phrase {pid}, " if pid else ""
        if "_retract" in langs:
            sys.exit(f"REFUSING TO SEND: {where}the body carries _retract="
                     f"{langs['_retract']!r}, which REMOVES those translations. This tool only "
                     f"ever fills empty rows. Use tools/apply_corrections.py for a write that "
                     f"replaces something, and retract only from a session that means to.")
        for lang, text in langs.items():
            if lang.startswith("_"):          # reserved keys such as _note are not languages
                continue
            if text is None:
                sys.exit(f"REFUSING TO SEND: {where}{lang} is null. The server answers 422 for "
                         f"this and will fail the whole batch; more to the point a null here is "
                         f"a bug on this side, not a request. Removal is _retract, and this "
                         f"tool does not do removals.")
            if not isinstance(text, str) or not text.strip():
                sys.exit(f"REFUSING TO SEND: {where}{lang} is {text!r}, not a non-empty string.")


def call(base, tok, method, path, payload=None):
    if payload is not None and method in ("PATCH", "POST", "PUT"):
        assert_no_retractions(payload)
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


def main():
    scratch = sys.argv[1]
    write = "--write" in sys.argv
    lang = "it"
    if "--lang" in sys.argv:
        lang = sys.argv[sys.argv.index("--lang") + 1]
    # Per-language batch files are `tr_<lang>_NN.json`; the original Italian pass used a
    # bare `tr_NN.json` and is left as it is rather than renamed, since renaming files
    # already applied would only invite a re-run.
    pattern = f"tr_{lang}_*.json"
    if lang == "it" and not glob.glob(os.path.join(scratch, pattern)):
        pattern = "tr_*.json"
    env, base, tok = load_env()

    # the writable languages and the length cap, from the schema, at request time
    status, schema = call(base, tok, "GET", "/api/v3/schema/phrase")
    if status != 200:
        sys.exit(f"schema fetch failed: {status} {schema}")
    writable = schema.get("writable", {})
    langs = writable.get("languages") or writable.get("locales") or []
    langs = [str(l).split("_")[0] for l in langs]
    maxlen = int(writable.get("maxLength") or schema.get("maxLength") or 2000)
    if lang not in langs:
        sys.exit(f"the site does not report {lang!r} as writable; it reports {langs}")

    # ---- resolve ids from the target, not from a file written against another site ----
    target, off = [], 0
    while True:
        status, d = call(base, tok, "GET", f"/api/v3/phrases?limit=500&offset={off}")
        if status != 200:
            sys.exit(f"could not read the target's phrases: {status} {d}")
        target += d["items"]
        off += 500
        if len(target) >= d["total"]:
            break

    # Skip decisions are made per (text_domain, source string) by tools/classify.py, and
    # they have to survive the join — because a string skipped in one domain can be
    # perfectly translatable in another. `Update on advances` is dead copy in the
    # Application domain and live text in SionModel; matching on the string alone would
    # write the dead one too. Keyed on the pair rather than the id so it carries between
    # environments.
    excl = set()
    sp = os.path.join(scratch, "skip_pairs.json")
    if os.path.exists(sp):
        excl = {(d, p) for d, p in json.load(open(sp, encoding="utf-8"))}
    else:
        print(f"note: no skip_pairs.json in {scratch} — every matching row will be "
              f"written, including any the classifier would skip")

    # source string -> ids whose Italian is empty, and which ones already have it
    open_ids, already = defaultdict(list), defaultdict(list)
    excluded = 0
    for p in target:
        if (p["textDomain"], p["phrase"]) in excl:
            excluded += 1
            continue
        cur = ((p["translations"].get(lang) or {}).get("text") or "").strip()
        (already if cur else open_ids)[p["phrase"]].append(p["phraseId"])

    trans, reviews, seen = {}, {}, {}
    for path in sorted(glob.glob(os.path.join(scratch, pattern))):
        doc = json.load(open(path, encoding="utf-8"))
        for src, it in doc.get(lang, {}).items():
            if src in seen and seen[src] != it:
                sys.exit(f"conflicting translations for {src!r}: "
                         f"{seen[src]!r} in {seen['__file__' + src]} vs {it!r} in {path}")
            seen[src] = it
            seen["__file__" + src] = path
            trans[src] = it
        for src, why in doc.get("review", {}).items():
            reviews[src] = {"why": why, "file": os.path.basename(path)}

    # ---- validate before sending anything ----
    items, problems, unmatched, skipped_filled = [], [], [], []
    for src, it in trans.items():
        it = it.strip()
        if not it:
            problems.append((src, "empty translation — there is no way to blank a row"))
            continue
        if len(it) > maxlen:
            problems.append((src, f"{len(it)} chars exceeds the {maxlen} cap"))
            continue
        ids = open_ids.get(src, [])
        if not ids:
            # either the string is not on this site at all, or every row already has
            # Italian — very different situations, so distinguish them
            if src in already:
                skipped_filled.append((src, already[src]))
            else:
                unmatched.append(src)
            continue
        for pid in ids:
            items.append((pid, it))

    print(f"environment : {env}  ({base})")
    print(f"writable    : {' '.join(langs)}   max {maxlen} chars")
    print(f"language    : {lang}   (batch files {pattern})")
    print(f"target holds: {len(target)} phrases, "
          f"{sum(len(v) for v in already.values())} already with {lang}")
    print(f"excluded    : {excluded} rows the classifier says are not translatable work")
    print(f"translations: {len(trans)} source strings -> {len(items)} phrase rows to write")
    print(f"reviews     : {len(reviews)} flagged for native-speaker review")
    if skipped_filled:
        print(f"\n   {len(skipped_filled)} source strings already have {lang} on this "
              f"site — NOT overwritten:")
        for s, ids in skipped_filled[:15]:
            print(f"     {s[:62]!r} (phrase {', '.join(str(i) for i in ids)})")
        if len(skipped_filled) > 15:
            print(f"     … and {len(skipped_filled) - 15} more")
    if unmatched:
        print(f"\n   {len(unmatched)} source strings do not exist on this site "
              f"(nothing written for them):")
        for s in unmatched[:15]:
            print(f"     {s[:70]!r}")
        if len(unmatched) > 15:
            print(f"     … and {len(unmatched) - 15} more")
    if problems:
        print(f"\n!! {len(problems)} refused before sending:")
        for s, why in problems[:20]:
            print(f"     {s[:50]!r}: {why}")
    if not write:
        print("\ndry run — nothing sent. pass --write to apply.")
        return

    ok = failed = 0
    for i in range(0, len(items), BATCH):
        chunk = items[i:i + BATCH]
        # The batch payload is an OBJECT KEYED BY PHRASE ID, per docs/api-v3.md:
        #   { "phrases": { "10028": {"de": "…"}, "6197": {"es": "…"} } }
        #
        # Send an array instead and the API does the right thing: each element is keyed
        # by its array index, so `0` is not a phrase id and the item fails 404 — reported
        # per id in `results` and counted in `summary.failed`. The HTTP status is still
        # 200, because a batch's outcome is per-item by design.
        #
        # The lesson is about the caller, not the endpoint: **trust `summary`, not the
        # HTTP status.** An earlier version of this file looked for response keys that do
        # not exist (`patched`, `failures`), read nothing, and printed "0 written,
        # 0 failed" — which looked like silence and was really a parsing bug.
        payload = {"phrases": {str(pid): {lang: it} for pid, it in chunk}}
        status, resp = call(base, tok, "PATCH", "/api/v3/phrases", payload)
        if status not in (200, 207):
            print(f"  batch {i // BATCH + 1}: HTTP {status} {str(resp)[:300]}")
            failed += len(chunk)
            continue
        results = resp.get("results") or {}
        summary = resp.get("summary") or {}
        applied = int(summary.get("applied", sum(1 for r in results.values() if r.get("ok"))))
        fails = {pid: r for pid, r in results.items() if not r.get("ok")}
        ok += applied
        failed += len(fails)
        print(f"  batch {i // BATCH + 1}: {applied} applied, {len(fails)} failed"
              f"  (received {summary.get('received', len(chunk))})")
        for pid, r in list(fails.items())[:5]:
            print(f"      {pid}: {r.get('status')} {r.get('message')}")
        if resp.get("warning"):
            # the row is committed; this is a filesystem problem, not a retry
            print(f"      WARNING (not a retry): {resp['warning']}")
    print(f"\n{ok} rows applied, {failed} failed")


if __name__ == "__main__":
    main()
