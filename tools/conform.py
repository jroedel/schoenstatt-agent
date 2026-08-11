"""Check drafted translations mechanically, before anything is written.

This was a subagent. It should never have been: every check below is a decidable property
of two strings, and an agent asked to verify 220 of them by eye is slower, more expensive
and less reliable than twenty lines of Python. The one thing the agent version did that a
script cannot — judge whether a term was rendered two ways *on purpose* — is not decided
here either. It is collected into a terms report for one reviewer to settle.

    python3 tools/conform.py /path/to/scratch --lang pt
    python3 tools/conform.py /path/to/scratch --lang pt --json pt_conformance.json

Reads   <lang>_units.json          the worklist, which holds the authoritative source keys
        <lang>_beats.json          optional; lets a term be traced to the beat that chose it
        tr_<lang>_*.json           whatever the drafting agents wrote
Writes  <lang>_conformance.json    the findings, machine-readable

Exit status is 1 if anything BLOCKING was found — a lost placeholder, two beats disagreeing
on one key, a key that does not exist in the worklist. Those three stop `apply_translations`
dead, so they are worth an exit code the caller can gate on.

Everything else is reported and not fatal: a translation identical to its source is
sometimes right (`Blog`, `ISBN`, a proper name), and a length outlier is sometimes just a
language that needs more words.
"""

import glob
import json
import os
import re
import sys
from collections import defaultdict

SIBLINGS = ("en", "es", "pt", "de", "it")

# printf-style, positional printf, brace-style, and the two token styles this codebase uses.
# `%(?![0-9A-Fa-f]{2})` keeps percent-encoded URLs out — `%C3%A1` in a link is not two
# placeholders. The `{2}` matters: a one-character lookahead also discards `%sAPI`, where the
# capital A merely happens to be a hex digit.
PLACEHOLDER = re.compile(
    r"%\d+\$[a-zA-Z]|%(?![0-9A-Fa-f]{2})[a-zA-Z]|%%|\{\d+\}|\{[a-zA-Z_]+\}|%[a-zA-Z_]+%")
TAG = re.compile(r"</?([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>")
WORD = re.compile(r"[A-Za-z][A-Za-z'\-]{2,}")

# Lowercase inside a proper name in all five languages.
PARTICLES = {"de", "del", "da", "do", "dos", "das", "la", "el", "los", "las", "y", "e",
             "der", "die", "das", "des", "dem", "den", "von", "vom", "zur", "zum", "im",
             "di", "dei", "della", "delle", "dello", "al", "a", "of", "the", "and", "van"}

# Spanish, Portuguese and Italian share so much vocabulary that two of them producing the
# same string is ordinary, not evidence of copying: `Casa de retiros`, `Emitir token` and
# `Tokens registrados` are each correct in both es and pt. The copy-a-sibling errors this
# project actually found crossed a family line — `Literature` rendered `Literatur`, German
# sitting in the Portuguese column. So a match is graded by distance, not just by count.
COGNATE = {frozenset(("es", "pt")), frozenset(("es", "it")), frozenset(("pt", "it"))}

# Read from GET /api/v3/schema/phrase at request time when you can; this is the fallback and
# it matches the column. A translation over the cap is refused by the API, not truncated.
MAXLEN = 2000


def load(scratch, lang):
    units = json.load(open(os.path.join(scratch, f"{lang}_units.json"), encoding="utf-8"))
    by_src = {u["src"]: u for u in units}

    beats = {}
    bp = os.path.join(scratch, f"{lang}_beats.json")
    if os.path.exists(bp):
        m = json.load(open(bp, encoding="utf-8"))
        # a source string belongs to exactly one beat, so index it that way
        for b in m.get("beats", []):
            for line in open(os.path.join(scratch, b["beat_file"]), encoding="utf-8"):
                if line.startswith("  SRC: "):
                    beats[line[7:].rstrip("\n")] = b["name"]

    # A draft file whose keys are almost all absent from the worklist is an ALREADY-APPLIED
    # draft left in the scratch directory, not a set of retyped keys. The distinction is
    # decidable and worth making: a stale file from the previous pass produced 110 blocking
    # `unknown-key` findings here, which is the same report a serious error would give and
    # buries the one real finding underneath it.
    #
    # A gap shrinks every time it is worked, so its worklist stops containing what was
    # written last time. Stale drafts are the normal state of a scratch directory, not an
    # anomaly.
    drafts, stale = {}, {}
    for path in sorted(glob.glob(os.path.join(scratch, f"tr_{lang}_*.json"))):
        d = json.load(open(path, encoding="utf-8"))
        tr = d.get(lang) or {}
        known = sum(1 for s in tr if s in by_src)
        name = os.path.basename(path)
        if tr and known / len(tr) < 0.2:
            stale[name] = (len(tr), known)
            continue
        drafts[name] = {
            "tr": tr,
            "review": d.get("review") or {},
            "terms": d.get("terms") or {},
        }
    return units, by_src, beats, drafts, stale


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    scratch = sys.argv[1]
    lang = sys.argv[sys.argv.index("--lang") + 1] if "--lang" in sys.argv else "de"
    units, by_src, beats, drafts, stale = load(scratch, lang)
    if not drafts:
        sys.exit(f"no tr_{lang}_*.json in {scratch} — nothing to check")

    issues = []

    def report(kind, src, detail, severity="check", file=None):
        issues.append({"kind": kind, "source": src, "detail": detail,
                       "severity": severity, "blocking": severity == "blocking",
                       "beat": beats.get(src), "file": file})

    # Three checks — identical-to-source, sibling-bleed, length — fire constantly on things
    # that are perfectly correct, and a report where 108 of 109 findings are proper names is
    # a report nobody reads twice. So each of them is graded, and the grading rules are the
    # interesting part of this script:
    #
    #   a name or a code   `María Ayuda`, `Sr. Jessy`, `Ciudad Celeste`, `Tabor Magnificat`,
    #                      `ISBN` — every token capitalized, or digits, or an abbreviation.
    #                      Nothing to translate; matching a sibling is not evidence of copying.
    #   convention         a value that equals what TWO OR MORE other languages say. Bleed is
    #                      matching ONE sibling; matching all of them is the site's own house
    #                      decision to leave a loanword alone (`Moderator`, `Blog`, `Import`).
    #   left as the key    when the translation equals the source, `sibling-bleed` is the same
    #                      fact reported twice with the wrong cause. Report it once, as
    #                      identical-to-source, and say nothing about siblings.
    def name_or_code(s):
        s = s.strip()
        if not s or len(s) <= 2 or any(c.isdigit() for c in s):
            return True
        toks = [t for t in re.split(r"[\s/,()–—-]+", s) if t]
        alpha = [t for t in toks if any(c.isalpha() for c in t)]
        # Particles stay lowercase inside a proper name in every language the site holds, so
        # requiring every token to be capitalized rejects `Oasis de Misericordia` and
        # `Nuevo Schoenstatt, Santuario del Padre` — both of which are shrine names and both
        # of which are correctly left as they are.
        content = [t for t in alpha if t.lower() not in PARTICLES]
        if not content:
            return True
        capped = sum(1 for t in content if t[0].isupper()) / len(content)
        # A trailing period ends a sentence — but `Pfr.` and `Frau Dr.` are abbreviations,
        # and those are two or three tokens, not sentences.
        sentence = s[-1] in ".?!:" and len(alpha) > 3
        return capped >= 0.6 and not sentence

    def sibling_agreement(u, tr):
        return sum(1 for l in SIBLINGS
                   if l != lang and u.get(l) and u[l].strip() == tr.strip())

    # ---- per entry -------------------------------------------------------------
    seen = defaultdict(dict)          # src -> {translation: [files]}
    for fname, d in drafts.items():
        for src, tr in d["tr"].items():
            seen[src].setdefault(tr, []).append(fname)

            u = by_src.get(src)
            if u is None:
                # The key is the lookup string; a retyped one silently translates nothing.
                near = [s for s in by_src if s[:40] == src[:40]]
                report("unknown-key", src,
                       "not in the worklist — retyped rather than copied. " +
                       (f"Closest by first 40 chars: {near[0]!r}" if near else "No near match."),
                       "blocking", file=fname)
                continue

            if not tr.strip():
                report("empty", src, "empty translation; the API reads empty as "
                       "'leave this language alone', so this row would silently not be written",
                       "blocking", file=fname)
                continue

            ps, pt_ = sorted(PLACEHOLDER.findall(src)), sorted(PLACEHOLDER.findall(tr))
            if ps != pt_:
                report("placeholder", src, f"source has {ps or 'none'}, translation has "
                       f"{pt_ or 'none'} — a lost or invented placeholder breaks the page",
                       "blocking", file=fname)

            ts, tt = sorted(TAG.findall(src)), sorted(TAG.findall(tr))
            if ts != tt:
                report("markup", src, f"source tags {ts or 'none'}, translation tags "
                       f"{tt or 'none'}", file=fname)

            if len(tr) > MAXLEN:
                report("too-long", src, f"{len(tr)} characters; the column cap is {MAXLEN} "
                       "and the API refuses rather than truncating", "blocking", file=fname)

            agree = sibling_agreement(u, tr)
            if tr.strip() == src.strip():
                why = ("looks like a name or a code" if name_or_code(src)
                       else f"{agree} other languages say the same" if agree >= 2 else "")
                report("identical-to-source", src,
                       f"translation equals the source key — {why}" if why else
                       "translation equals the source key, and it is neither a name nor "
                       "something the other languages left alone: probably not translated",
                       "expected" if why else "check", file=fname)
            else:
                # Bleed is matching ONE sibling. Matching several is house convention.
                for l in SIBLINGS:
                    if l != lang and u.get(l) and tr.strip() == u[l].strip():
                        cognate = frozenset((lang, l)) in COGNATE
                        if agree >= 2 or name_or_code(tr) or cognate:
                            why = ("a name or code" if name_or_code(tr)
                                   else f"{lang} and {l} are cognate languages" if cognate
                                   else f"{agree} languages agree on it")
                            report("sibling-match", src,
                                   f"equals the {l} value — {why}, so this is convention "
                                   f"rather than bleed", "expected", file=fname)
                        else:
                            report("sibling-bleed", src, f"identical to the {l} value {u[l]!r} "
                                   f"and to no other language's. This is the copy-a-sibling "
                                   f"error the audits keep finding, in our own output",
                                   file=fname)
                        break

            if (src[:1].isspace() != tr[:1].isspace()) or (src[-1:].isspace() != tr[-1:].isspace()):
                report("edge-whitespace", src, "leading/trailing whitespace differs from the "
                       "source; these strings are sometimes concatenated, so the space is content",
                       file=fname)

            n, m = len(src.strip()), len(tr.strip())
            if n >= 12 and (m > 3 * n or m < 0.3 * n):
                report("length-outlier", src, f"source {n} chars, translation {m} — usually "
                       "means something was dropped or a note leaked into the value", file=fname)

    # ---- across files ----------------------------------------------------------
    for src, variants in seen.items():
        if len(variants) > 1:
            report("collision", src, "translated differently in " +
                   "; ".join(f"{','.join(fs)}: {t!r}" for t, fs in variants.items()) +
                   " — apply_translations refuses to run while this stands", "blocking")

    missing = [u["src"] for u in units if u["src"] not in seen]

    # ---- the part a script cannot decide, prepared for whoever can -------------
    # A term recurring in more than one beat was settled independently by more than one
    # agent. Whether they agree is a judgement, so collect the evidence rather than guess.
    tcount = defaultdict(set)
    for src in seen:
        for w in {mo.group().lower() for mo in WORD.finditer(src)}:
            tcount[w].add(beats.get(src))
    cross = {w: bs for w, bs in tcount.items() if len(bs - {None}) > 1}
    terms_report = {}
    for w in cross:
        rows = [{"beat": beats.get(s), "source": s, "translation": next(iter(v))}
                for s, v in seen.items() if w in s.lower() and len(s) < 60]
        if len(rows) > 1:
            terms_report[w] = rows[:8]

    # Each drafting agent declares the terms it settled. Two agents declaring the same term
    # differently is the one cross-beat failure this design can actually create, so it is
    # checked directly rather than inferred from the output.
    declared = defaultdict(lambda: defaultdict(list))
    for fname, d in drafts.items():
        for term, choice in d["terms"].items():
            declared[term.lower()][choice].append(fname)
    disputed = {t: {c: fs for c, fs in v.items()} for t, v in declared.items() if len(v) > 1}

    out = {
        "language": lang,
        "checked": sum(len(d["tr"]) for d in drafts.values()),
        "files": sorted(drafts),
        "issues": issues,
        "missing_from_drafts": missing,
        "cross_beat_terms": terms_report,
        "disputed_declared_terms": disputed,
    }
    dest = os.path.join(scratch, f"{lang}_conformance.json")
    json.dump(out, open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    blocking = [i for i in issues if i["severity"] == "blocking"]
    check = [i for i in issues if i["severity"] == "check"]
    expected = [i for i in issues if i["severity"] == "expected"]
    print(f"language   : {lang}")
    print(f"drafts     : {len(drafts)} files, {out['checked']} translations")
    for name, (n, known) in stale.items():
        print(f"  SKIPPED {name}: {n} entries, only {known} still in the worklist — an "
              f"already-applied draft, not a set of bad keys")
    print(f"worklist   : {len(units)} units, {len(missing)} not drafted")
    print(f"findings   : {len(blocking)} blocking, {len(check)} to check, "
          f"{len(expected)} expected (names, codes, house loanwords)")
    for sev, group in (("blocking", blocking), ("check", check), ("expected", expected)):
        if not group:
            continue
        by_kind = defaultdict(int)
        for i in group:
            by_kind[i["kind"]] += 1
        print(f"  {sev}:")
        for k, n in sorted(by_kind.items(), key=lambda kv: -kv[1]):
            print(f"    {n:4}  {k}")
    if disputed:
        print(f"\n{len(disputed)} terms two beats declared differently — these need one decision:")
        for t, v in list(disputed.items())[:12]:
            print(f"  {t}: " + " vs ".join(f"{c!r} ({','.join(f)})" for c, f in v.items()))
    if terms_report:
        print(f"\n{len(terms_report)} terms recur across beats; {dest} has the renderings side "
              "by side for a consistency review.")
    print(f"\nwrote {dest}")
    if missing:
        print(f"\n{len(missing)} worklist units have no translation. First few:")
        for s in missing[:5]:
            print(f"  {s[:100]!r}")
    sys.exit(1 if blocking else 0)


if __name__ == "__main__":
    main()
