"""Build a language's translation worklist from the live site, grouped into *beats*.

A **beat** is one agent's assignment: a family of related routes, whole, plus the
translations that language already has *for those same routes*. The unit is the beat and
not a fixed count of strings, because the expensive thing about a drafting agent is not
the strings — it is the preamble. Measured on the Portuguese gap:

    prelude per agent   SKILL.md 10k + glossary 15k + style 5k + an existing-rows dump 48k
                        = ~23k tokens before a single string is translated
    the entire payload  374 units, all five languages quoted = ~24k tokens

At four fixed-size chunks that is ~92k tokens of prelude to carry ~24k of work: the
duplicated preamble was roughly **four times the job**. Cutting chunks does not just cut
agents, it cuts that multiplier.

Route families are what make the cut safe, and they are also where the quality is. 301 of
the Portuguese gap's 374 units are one family — publications/libraries/books — and inside
it 82 English words recur in three or more units (`call number`, `checkout`, `edition`,
`label`, `import`). Those are decisions, not strings: settle `call number` once and 300
rows follow. Only 25 of those 91 recurrent terms appear anywhere in the account routes, so
a beat can be given *its own* slice of the existing rows and lose almost nothing — which is
where the prelude saving actually comes from.

The gain is real but not uniform, so don't spread it evenly. In the same measurement the
leftover 25 units had **zero** terms recurring three times: genuine miscellany, no shared
context to amortise, and no reason to give it a beat of its own. It gets one pile.

    python3 tools/build_worklist.py /path/to/scratch --lang pt
    python3 tools/build_worklist.py /path/to/scratch --lang pt --max-units 150

Emits, per language:

    <lang>_units.json          one entry per distinct source string (unchanged; the apply
                               tool and the chunk files both read it)
    <lang>_beats.json          the manifest the workflow is launched with
    <lang>beat_<name>.txt      the assignment: recurrent terms first, then the units
    <lang>seen_<name>.txt      what <lang> already says on those same routes

Grouping within a beat is still by source string, not phrase id: one string can be a row in
up to seven text domains and the translation is the same for all of them. Ids are read from
the target at run time and only ever used by `apply_translations.py`, which resolves them
again itself — see the note about ids in the skill.

Rows the classifier says are not translatable work are excluded via `skip_pairs.json`,
keyed on (text_domain, source string) so the exclusion survives between environments.

Environment: SCHOENSTATT_ENV as everywhere else.
"""

import glob
import json
import os
import re
import sys
import urllib.request
from collections import Counter, defaultdict

CREDS = os.path.expanduser("~/.config/schoenstatt/credentials.env")
SIBLINGS = ("en", "es", "pt", "de", "it")

# Target size of a beat, in distinct source strings. A family larger than this splits along
# route boundaries; a family smaller than MIN_BEAT merges into the leftover pile. 110 is
# what the drafting agents handled well in the runs that produced 659 German and 220
# Spanish strings, so it is measured rather than chosen.
MAX_UNITS = 110
MIN_BEAT = 12

# Route families. The first path segment of `context.originRoute` is the module; these are
# the modules that share a vocabulary, so they share a beat.
#
# This map is derived from measured term recurrence, not from what the routes are called.
# Verify it rather than trusting it: --report prints, per beat, how many terms recur and how
# many of them leak into another beat. A family whose terms do not recur is not a family,
# and a term that leaks belongs in the glossary instead.
FAMILIES = {
    "library": {
        "publications", "publication", "publications-index", "libraries", "library",
        "library-imports", "books", "book", "collections", "collection", "borrowers",
        "borrower", "checkouts", "checkout", "music", "composition", "composition-edit",
        "compositions", "authors", "author", "publishers", "publisher",
    },
    "account": {
        "zfcuser", "juser", "persons", "person", "roles", "role", "user", "users",
        "login", "register",
    },
    "association": {
        "associations", "association", "association-edit", "shrines", "shrine",
        "communities", "community",
    },
    "admin": {
        "sion-model", "admin", "jtranslate", "assignments", "assignment", "changes",
    },
    "text": {"text", "texts", "blog", "articles", "article"},
}
LEFTOVER = "misc"

WORD = re.compile(r"[A-Za-z][A-Za-z'\-]{2,}")
# Function words carry no terminology, so counting them as recurrence would make every beat
# look coherent.
#
# All five languages, not just English, because **a source string is not guaranteed to be
# English** — that is one of this project's standing facts, and it showed up here: the
# association beat's "terms to settle" list led with `que`, `por`, `del`, `der`, `die`, `dem`
# and `des`, because the shrine descriptions on those routes were typed by moderators in
# Spanish and German. An English-only stop list turns a beat of Spanish prose into a list of
# Spanish articles and calls them decisions.
STOP = set("""the and for you your this that with are not from all has have was were will
can may its our their any than then out off per via such into onto both each other more
most only also just very much many some what when where which while who whom whose how
does did done being been but nor yet had shall should would could must about above after
again against before below between during further here once same too under until upon
que por para con los las una uno unos unas del como pero más muy sus está esto esta ese
esa eso son sea ser tiene hay desde hasta sobre entre cuando donde porque también sin
dos tres nos les nas dos das aos ao pelo pela pelos pelas isso essa esse não são está
com sem mais muito seus suas onde quando porque também depois antes ainda
der die das den dem des ein eine einen einem eines auch aber oder wenn dann noch nur
sich sie ihr ihre ihren nach bei von vom zur zum aus vor beim durch über unter wird
sind ist war waren haben hatte kann muss soll wie was wer wo dass
che con del della delle dello nel nella nelle dei degli sono essere alla alle agli
questo questa questi queste anche però quando dove perché molto piu""".split())


def load_env():
    if os.path.exists(CREDS):
        with open(CREDS, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    env = os.environ.get("SCHOENSTATT_ENV", "").strip() or "test"
    pair = (("SCHOENSTATT_BASE_URL", "SCHOENSTATT_TRANSLATOR_JWT") if env == "production"
            else ("SCHOENSTATT_BASE_URL_TEST", "SCHOENSTATT_TRANSLATOR_JWT_TEST"))
    base, tok = os.environ.get(pair[0]), os.environ.get(pair[1])
    if not base or not tok:
        sys.exit(f"no base url / token for environment {env!r}")
    return env, base.rstrip("/"), tok


def fetch_all(base, tok):
    items, off = [], 0
    while True:
        r = urllib.request.Request(f"{base}/api/v3/phrases?limit=500&offset={off}",
                                   headers={"Authorization": "Bearer " + tok})
        d = json.load(urllib.request.urlopen(r, timeout=120))
        items += d["items"]
        off += 500
        if len(items) >= d["total"]:
            break
    return items


def module(route):
    return (route or "").split("/")[0] or "(none)"


def family(route):
    m = module(route)
    for name, mods in FAMILIES.items():
        if m in mods:
            return name
    return LEFTOVER


def terms_of(strings, floor=3):
    """Words appearing in `floor` or more distinct strings — the beat's real vocabulary."""
    c = Counter()
    for s in strings:
        for w in {m.group().lower() for m in WORD.finditer(s)}:
            if w not in STOP:
                c[w] += 1
    return {w: n for w, n in c.items() if n >= floor}


def pack(units, max_units):
    """Split one family's units into beats along route boundaries, never mid-route.

    A single route bigger than max_units becomes its own oversized beat rather than being
    cut: a route is one screen, and half a screen is exactly the context loss this whole
    grouping exists to avoid.
    """
    by_route = defaultdict(list)
    for u in units:
        by_route[u["routes"][0] or ""].append(u)
    # biggest route first, so the leftovers fill in around the screens that matter
    order = sorted(by_route.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    beats = []
    for route, rows in order:
        for b in beats:
            if len(b["units"]) + len(rows) <= max_units:
                b["units"] += rows
                b["routes"].append(route)
                break
        else:
            beats.append({"units": list(rows), "routes": [route]})
    for b in beats:
        b["units"].sort(key=lambda u: (u["routes"][0], u["src"].lower()))
        b["routes"].sort()
    return beats


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    scratch = sys.argv[1]
    lang = sys.argv[sys.argv.index("--lang") + 1] if "--lang" in sys.argv else "de"
    max_units = int(sys.argv[sys.argv.index("--max-units") + 1]) if "--max-units" in sys.argv else MAX_UNITS
    env, base, tok = load_env()
    items = fetch_all(base, tok)

    sp = os.path.join(scratch, "skip_pairs.json")
    excl = {tuple(x) for x in json.load(open(sp, encoding="utf-8"))} if os.path.exists(sp) else set()
    if not excl:
        print("note: no skip_pairs.json — the worklist will include non-translatable rows")

    def val(p, l):
        return (p["translations"].get(l) or {}).get("text") or ""

    # ---- the gap ---------------------------------------------------------------
    miss = [p for p in items
            if not val(p, lang).strip() and (p["textDomain"], p["phrase"]) not in excl]

    groups = defaultdict(list)
    for p in miss:
        groups[p["phrase"]].append(p)

    units = []
    for src, rows in groups.items():
        # prefer the row with the most sibling context to quote from
        pick = max(rows, key=lambda p: sum(1 for l in SIBLINGS if val(p, l)))
        u = {"src": src,
             "ids": sorted(p["phraseId"] for p in rows),
             "domains": sorted({p["textDomain"] for p in rows}),
             "routes": sorted({p["context"]["originRoute"] or "" for p in rows})}
        for l in SIBLINGS:
            if l != lang:
                u[l] = val(pick, l)
        units.append(u)
    units.sort(key=lambda u: (u["routes"][0], u["src"].lower()))

    json.dump(units, open(os.path.join(scratch, f"{lang}_units.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # ---- what the language already says, by family -----------------------------
    # This is the "mine the existing rows first" step of the skill, pre-done and sliced.
    # In the runs that produced this design the drafting agents did it themselves,
    # unprompted, each dumping the whole 48k-character table. Sliced per beat it is a
    # fraction of that, and it is the same evidence.
    seen, seen_route = defaultdict(dict), defaultdict(dict)
    for p in items:
        cur = val(p, lang).strip()
        if cur:
            route = p["context"]["originRoute"] or ""
            seen[family(route)].setdefault(p["phrase"], cur)
            seen_route[route].setdefault(p["phrase"], cur)

    # ---- beats -----------------------------------------------------------------
    byfam = defaultdict(list)
    for u in units:
        byfam[family(u["routes"][0])].append(u)

    # A family with no recurring vocabulary is not a family — it is a pile that happens to
    # share a URL prefix, and giving it its own agent buys a second prelude and nothing else.
    # The test is recurrence, not size: that is the thing being amortised.
    for fam in [f for f in list(byfam) if f != LEFTOVER]:
        if len(byfam[fam]) < MIN_BEAT or not terms_of([u["src"] for u in byfam[fam]]):
            byfam[LEFTOVER] += byfam.pop(fam)

    beats = []
    for fam in sorted(byfam, key=lambda f: (f == LEFTOVER, -len(byfam[f]))):
        parts = pack(byfam[fam], max_units)
        for i, b in enumerate(parts):
            name = fam if len(parts) == 1 else f"{fam}{i + 1}"
            beats.append({"name": name, "family": fam, "routes": b["routes"], "units": b["units"]})

    # ---- write the assignments -------------------------------------------------
    # Delete last run's beat files first. The gap shrinks every pass, so a stale
    # `<lang>beat_admin.txt` left behind by a wider run is a file full of strings that have
    # already been written — and it looks exactly like a current assignment.
    for stale in glob.glob(os.path.join(scratch, f"{lang}beat_*.txt")) + \
                 glob.glob(os.path.join(scratch, f"{lang}seen_*.txt")):
        os.unlink(stale)

    manifest = []
    for b in beats:
        srcs = [u["src"] for u in b["units"]]
        rec = terms_of(srcs)
        bf, sf = f"{lang}beat_{b['name']}.txt", f"{lang}seen_{b['name']}.txt"

        with open(os.path.join(scratch, bf), "w", encoding="utf-8") as fh:
            fh.write(f"# beat: {b['name']}   language: {lang}   {len(b['units'])} source strings\n")
            fh.write(f"# routes: {', '.join(r or '(none)' for r in b['routes'])}\n#\n")
            if rec:
                fh.write("# These words recur across this beat. They are decisions, not strings:\n"
                         "# settle each one ONCE, write it into your terms block, then be\n"
                         "# consistent with yourself for every entry below.\n")
                for w, n in sorted(rec.items(), key=lambda kv: -kv[1])[:40]:
                    fh.write(f"#   {n:3}x  {w}\n")
            else:
                fh.write("# No word recurs three times in this beat: it is miscellany, and there\n"
                         "# is no shared vocabulary to settle. Translate each entry on its own.\n")
            fh.write(f"#\n# What {lang} already says on these routes: {sf}\n\n")
            for n, u in enumerate(b["units"]):
                fh.write(f"[{b['name']}:{n}] dom={','.join(u['domains'])} route={u['routes'][0]}\n")
                fh.write(f"  SRC: {u['src']}\n")
                for l in SIBLINGS:
                    if l == lang or not u.get(l):
                        continue
                    # the en row is only interesting when it differs from the key
                    if l == "en" and u[l].strip() == u["src"].strip():
                        continue
                    fh.write(f"  {l.upper()} : {u[l]}\n")
                fh.write("\n")

        # A real family beat gets its whole family's existing rows: that is the vocabulary it
        # has to be consistent with. The leftover pile is not a vocabulary — it spans every
        # family — so slicing it by family would hand 25 unrelated strings the largest
        # prelude of the run. It gets the rows from its own exact routes and nothing more.
        rows = {}
        if b["family"] == LEFTOVER:
            for r in b["routes"]:
                rows.update(seen_route.get(r, {}))
        else:
            for f in sorted({family(r) for r in b["routes"]}):
                rows.update(seen.get(f, {}))
        with open(os.path.join(scratch, sf), "w", encoding="utf-8") as fh:
            fh.write(f"# {len(rows)} translations {lang} already has on the {b['family']} routes.\n"
                     "# House convention lives here, not only in the glossary: the glossary holds\n"
                     "# the decisions somebody wrote down, these hold every decision anybody made.\n"
                     "# Where a source string here matches one in your beat, REUSE THIS VALUE\n"
                     "# VERBATIM — the two rows render in the same places and must not drift.\n\n")
            for s, v in sorted(rows.items(), key=lambda kv: kv[0].lower()):
                fh.write(f"{s}\n\t-> {v}\n")

        manifest.append({
            "name": b["name"], "family": b["family"], "routes": b["routes"],
            "units": len(b["units"]), "beat_file": bf, "seen_file": sf,
            "recurrent_terms": len(rec), "seen": len(rows),
            "chars": sum(len(u["src"]) + sum(len(u.get(l) or "") for l in SIBLINGS) + 60
                         for u in b["units"]),
        })

    json.dump({"language": lang, "environment": env, "beats": manifest},
              open(os.path.join(scratch, f"{lang}_beats.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # ---- report ----------------------------------------------------------------
    print(f"environment : {env}")
    print(f"language    : {lang}")
    print(f"corpus      : {len(items)} phrases, {len(excl)} skip pairs excluded")
    print(f"gap         : {len(miss)} rows -> {len(units)} distinct source strings")
    print(f"beats       : {len(beats)}  (one drafting agent each)\n")
    print(f"  {'beat':<14}{'units':>6}{'terms':>7}{'seen':>6}  routes")
    for m in manifest:
        print(f"  {m['name']:<14}{m['units']:>6}{m['recurrent_terms']:>7}"
              f"{m['seen']:>6}  "
              f"{', '.join(r or '(none)' for r in m['routes'])[:74]}")

    # Term leakage across beats is the check on the FAMILIES map: a term recurring in two
    # beats is one both agents will decide independently, and they may disagree.
    tsets = {m["name"]: set(terms_of([u["src"] for u in b["units"]]))
             for m, b in zip(manifest, beats)}
    shared = Counter()
    names = list(tsets)
    for i, a in enumerate(names):
        for b_ in names[i + 1:]:
            for w in tsets[a] & tsets[b_]:
                shared[w] += 1
    if shared:
        print(f"\n{len(shared)} terms recur in more than one beat. These are the ones two agents\n"
              f"will settle independently, so they belong in data/glossary/{lang}.yaml first:")
        print("  " + ", ".join(w for w, _ in shared.most_common(24)))

    long_ = [u for u in units if "\n" in u["src"] or "\r" in u["src"]]
    if long_:
        print(f"\n{len(long_)} source strings contain newlines — these cannot be retyped by "
              f"hand; copy them from {lang}_units.json")


if __name__ == "__main__":
    main()
