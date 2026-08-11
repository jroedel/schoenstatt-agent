"""Find defects in translations the site already has, without asking an agent.

Every correction applied to production on 2026-08-10 — twenty Spanish, two German — was of
a kind decidable by script: `existosamente`, seven counts of `exitósamente`, `coleción`,
`Volúmen`, `Santisima`, `Arcangel`, `Pais`, `Hermitas`, `¡Foto?`, `parentesis`, `Strasse`.
Six subagents hunted for those; a majority of what they returned was refuted, and the
survivors were almost all in this class. So this class stops being an agent's job.

What makes it decidable is the bibliography. `../reading-material` holds the
movement's own books — 3.8M characters of Portuguese, 15M of German, 2.1M of Spanish — and
a word that never occurs in millions of words of edited prose in its own language, while a
diacritic variant of it occurs hundreds of times, is a misspelling and not a stylistic
choice. That is evidence, not a guess, and it is the same evidence a native speaker would
give. Extract with `extract_reading_material.py` first; this reads the extraction.

    python3 tools/extract_reading_material.py --lang es --out /path/to/scratch/es_text
    python3 tools/hunt_lexical.py /path/to/scratch --lang es

The books are copyrighted. This tool reads the scratch extraction and writes out single
words with counts — never a clause, never a sentence. Keep it that way.

Writes  <lang>_mech_findings.json   ready for the verify phase of translate-revise

The rules, strongest first. Only the first three are strong enough to act on with one
reviewer; the rest are candidates.

  variant-attested   the value contains a word absent from the corpus whose accent variant
                     is attested many times. `exitósamente` 0, `exitosamente` 41.
  paired-punctuation Spanish opens with ¿ or ¡ and must close with the match. `¡Foto?`
  placeholder        the value's placeholders do not match the key's.
  truncated          the last word is a strict prefix of attested words and is not itself
                     attested. `Contato principa`
  doubled-word       the same word twice in a row.
  bleed              the value equals another language's value and the two are not cognate
                     languages. `Literature` -> `Literatur` in the Portuguese navigation.
  unattested         a word absent from the corpus with no attested variant. NOISY, and
                     capped: proper names, English loanwords and German compounds all land
                     here legitimately.

German precision is materially lower than Spanish or Portuguese, because German forms
compounds freely and a perfectly good compound is often unattested. The cap on `unattested`
exists for that reason.

**Nothing here may be applied unverified.** The rule that finds real misspellings also
produces false positives of four distinct kinds, and only three of them can be filtered.

1. **Proper names** — downgraded to `medium` when the flagged word is capitalized inside a
   name-shaped string, not suppressed, because `Cenaculo` for `Cenáculo` is a real defect
   while `Magnificat` (Latin) and `Berlin-Frohnau` (a German district) are correct as they
   stand. Judgement required, so the finding says so.
2. **Enclitic pronouns** — filtered. Portuguese `publicá-la` tokenises as `publicá`, whose
   fold-variant `pública` is attested; two correct rows were accused. A token followed by a
   hyphen is skipped.
3. **Extraction noise** — filtered by `plausible()`. The Portuguese books are the noisiest
   extraction here (146,887 distinct words from 379,135 total, against Spanish's 20,285 from
   231,574) and one artefact, `àñà`, occurs 6 times and folds to `ana`. That was enough to
   accuse `Santa Ana`. A variant must be spelt with the target language's own letters.
4. **A real word the corpus has no occasion to use — and this one cannot be filtered.**
   German `drucken` (to print) occurs **0** times in 1.85M words of Kentenich's writings
   while `drücken` (to press) occurs 364. It is reported at `high` confidence and it is
   wrong: `drucken` is ordinary German, and the corpus is theology, which has no reason to
   discuss printing labels. `gedruckt` does appear 6 times, which proves the stem is in the
   vocabulary. Applying that "correction" would have **inverted the meaning of a button**.

So the corpus tells you what the movement *writes about*, not what the language contains. It
is excellent evidence for a charism term and weak evidence for a household verb, and German
is worse affected than Spanish because it inflects and compounds more. The script is far
better than an agent at finding candidates and no better at all at knowing what a thing is
called or whether a word exists.
"""

import json
import os
import re
import sys
import unicodedata
import urllib.request
from collections import Counter, defaultdict

CREDS = os.path.expanduser("~/.config/schoenstatt/credentials.env")
SIBLINGS = ("en", "es", "pt", "de", "it")
COGNATE = {frozenset(("es", "pt")), frozenset(("es", "it")), frozenset(("pt", "it"))}
# Percent-encoding is `%` followed by EXACTLY TWO hex digits, and the lookahead has to say
# `{2}` or it over-reaches. `%C3%A1` in a Wikipedia link is not two placeholders — but `%sAPI`
# is one placeholder followed by a capital A, and a one-character lookahead threw that away
# because `A` is a hex digit. Both were real false positives, in opposite directions.
PLACEHOLDER = re.compile(
    r"%\d+\$[a-zA-Z]|%(?![0-9A-Fa-f]{2})[a-zA-Z]|%%|\{\d+\}|\{[a-zA-Z_]+\}|%[a-zA-Z_]+%")
TOKEN = re.compile(r"[^\W\d_]{3,}", re.UNICODE)
TAG = re.compile(r"</?([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>")

# How often a variant must appear in the corpus before its absent sibling is called a
# misspelling. Low enough to catch a rare word, high enough that an OCR artefact in the
# extraction cannot accuse a correct spelling.
ATTESTED_MIN = 5
UNATTESTED_CAP = 40


PARTICLES = {"de", "del", "da", "do", "dos", "das", "la", "el", "los", "las", "y", "e",
             "der", "die", "des", "dem", "den", "von", "vom", "zur", "zum", "im",
             "di", "dei", "della", "delle", "dello", "al", "a", "of", "the", "and", "van"}


def name_or_code(s):
    """A proper name, a title or a code — nothing to translate, so nothing to compare.

    The same test `conform.py` uses, and for the same reason: every rule in this file that
    compares two strings fires on names, because a name is the same word in both languages.
    """
    s = s.strip()
    if not s or len(s) <= 3 or any(c.isdigit() for c in s):
        return True
    toks = [t for t in re.split(r"[\s/,()–—\-]+", s) if t]
    alpha = [t for t in toks if any(c.isalpha() for c in t)]
    content = [t for t in alpha if t.lower() not in PARTICLES]
    if not content:
        return True
    capped = sum(1 for t in content if t[0].isupper()) / len(content)
    sentence = s[-1] in ".?!:" and len(alpha) > 3
    return capped >= 0.6 and not sentence


# The letters each language actually uses. A candidate "correct spelling" containing anything
# else is extraction noise, not evidence — the Portuguese books are the noisiest extraction
# here (146,887 distinct words from 379,135 total, against Spanish's 20,285 from 231,574), and
# one of its OCR artefacts, `àñà`, occurs 6 times and folds to `ana`. That was enough to accuse
# `Santa Ana` of a misspelling. A variant must look like the language before it can testify.
ALPHABET = {
    "es": set("abcdefghijklmnopqrstuvwxyzáéíóúüñ"),
    "pt": set("abcdefghijklmnopqrstuvwxyzáàâãéêíóôõúüç"),
    "it": set("abcdefghijklmnopqrstuvwxyzàèéìíîòóùú"),
    "de": set("abcdefghijklmnopqrstuvwxyzäöüß"),
    "en": set("abcdefghijklmnopqrstuvwxyz"),
}


def plausible(word, lang):
    letters = ALPHABET.get(lang)
    return letters is None or all(c in letters or c in "'-." for c in word.lower())


def fold(w):
    """Strip diacritics: the key under which `exitosamente` and `exitósamente` collide."""
    return "".join(c for c in unicodedata.normalize("NFD", w.lower())
                   if not unicodedata.combining(c))


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


def build_lexicon(corpus_dir):
    """word -> count, and fold-key -> {word: count}, from the extracted books."""
    freq = Counter()
    for name in sorted(os.listdir(corpus_dir)):
        path = os.path.join(corpus_dir, name)
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                for m in TOKEN.finditer(line):
                    freq[m.group().lower()] += 1
    groups = defaultdict(dict)
    for w, n in freq.items():
        groups[fold(w)][w] = n
    return freq, groups


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    scratch = sys.argv[1]
    lang = sys.argv[sys.argv.index("--lang") + 1] if "--lang" in sys.argv else "pt"
    corpus = (sys.argv[sys.argv.index("--corpus") + 1] if "--corpus" in sys.argv
              else os.path.join(scratch, f"{lang}_text"))
    if not os.path.isdir(corpus):
        sys.exit(f"no corpus at {corpus} — run extract_reading_material.py --lang {lang} first")

    env, base, tok = load_env()
    items, off = [], 0
    while True:
        r = urllib.request.Request(f"{base}/api/v3/phrases?limit=500&offset={off}",
                                   headers={"Authorization": "Bearer " + tok})
        d = json.load(urllib.request.urlopen(r, timeout=120))
        items += d["items"]
        off += 500
        if len(items) >= d["total"]:
            break

    freq, groups = build_lexicon(corpus)
    print(f"environment : {env}")
    print(f"corpus      : {sum(freq.values())} words, {len(freq)} distinct, from {corpus}")

    def val(p, l):
        return (p["translations"].get(l) or {}).get("text") or ""

    rows = [p for p in items if val(p, lang).strip()]
    # The language's own rows, as a second lexicon. Used only to suppress a truncation report:
    # a word the site uses elsewhere is a word, whatever a 231k-word book corpus happens to
    # hold. Never used to *confirm* a spelling — these rows are what is under audit.
    site_words = {m.group().lower() for p in rows for m in TOKEN.finditer(val(p, lang))}
    print(f"rows        : {len(rows)} phrases have {lang}, using {len(site_words)} distinct "
          f"words of their own as a second lexicon\n")

    findings, unattested = [], []

    def add(kind, p, cur, proposed, why, confidence="high"):
        findings.append({
            "kind": kind, "phrase_id": p["phraseId"], "text_domain": p["textDomain"],
            "route": p["context"]["originRoute"] or "", "source": p["phrase"],
            "current": cur, "proposed": proposed, "why": why, "confidence": confidence,
        })

    for p in rows:
        cur = val(p, lang)
        src = p["phrase"]

        # --- placeholders -------------------------------------------------------
        ps, pc = sorted(PLACEHOLDER.findall(src)), sorted(PLACEHOLDER.findall(cur))
        if ps != pc:
            add("placeholder", p, cur, "", f"key has {ps or 'none'}, {lang} has {pc or 'none'}")

        # --- paired punctuation -------------------------------------------------
        # Spanish requires one opener per closer. Counting them is right where "ends with ?"
        # is wrong: a value holding two sentences, or a question followed by more text, is
        # perfectly correct and the first version of this check flagged several — and
        # proposed turning `¡Tu mail ha sido verificado!` into `¿Tu mail ...!`, which would
        # have introduced an error rather than fixed one.
        if lang == "es":
            for opener, closer in (("¿", "?"), ("¡", "!")):
                if cur.count(opener) != cur.count(closer):
                    # Only propose the fix for the unambiguous shape: one closer, at the very
                    # end, no opener. Where the closer ends a clause in the middle of a
                    # multi-sentence value the opener belongs at that clause's start, not at
                    # the front of the string, and guessing would introduce a new error.
                    fix = (opener + cur if cur.count(opener) == 0 and cur.count(closer) == 1
                           and cur.rstrip().endswith(closer) else "")
                    add("paired-punctuation", p, cur, fix,
                        f"{cur.count(opener)}x {opener!r} against {cur.count(closer)}x "
                        f"{closer!r}; Spanish needs one opener per closer"
                        + ("" if fix else " — more than one clause, so where the opener goes "
                                         "is a judgement, not a substitution"))

        # --- bleed --------------------------------------------------------------
        # Names, titles and abbreviations match across languages because they are the same
        # word in both. Measured against production Spanish, every single bleed hit was one
        # of those: `P.` (Padre and Pater alike), `Doctor`, `Rector`, `Lo Barnechea`. A rule
        # that fires eight times and is wrong eight times is not a rule.
        for l in SIBLINGS:
            if l == lang or not val(p, l):
                continue
            if val(p, l).strip() == cur.strip() and cur.strip() != src.strip():
                if frozenset((lang, l)) not in COGNATE and not name_or_code(cur):
                    add("bleed", p, cur, "", f"identical to the {l} value; {lang} and {l} are "
                        f"not cognate languages, so this is the wrong row's text",
                        "medium")
                break

        # --- doubled word -------------------------------------------------------
        # Tokenise the text WITHOUT its markup, and only within one run of words. Both
        # exclusions come from real false positives: `<strong>%s</strong>` reads as "strong
        # strong", and `"Santuarios de Schoenstatt" (Schoenstatt Shrines)` repeats a word
        # across a quote boundary, which is how the phrase is meant to read.
        # `run_toks`, not `toks`: the lexical pass below iterates `toks` over the whole value,
        # and reusing the name here left it holding only the last fragment — which silently
        # stopped six real findings being reported, including `contínuamente` and `perpétua`.
        # Caught by checking that known defects still appeared, not by reading the counts.
        for run in re.split(r"[^\w\s]+|\n", TAG.sub(" ", cur)):
            run_toks = TOKEN.findall(run)
            hit = next((a for a, b in zip(run_toks, run_toks[1:])
                        if a.lower() == b.lower() and len(a) > 3), None)
            if hit:
                add("doubled-word", p, cur, "", f"{hit!r} appears twice in a row")
                break

        # --- lexical ------------------------------------------------------------
        # Every word of the whole value, markup stripped so tag names are not treated as
        # vocabulary. This is the pass that finds the misspellings, so its scope matters.
        stripped = TAG.sub(" ", cur)
        toks = [m for m in TOKEN.finditer(stripped)]
        for i, m in enumerate(toks):
            w = m.group()
            lw = w.lower()
            if freq.get(lw):
                continue
            # An enclitic pronoun makes a verb stem look like a misspelling. Portuguese
            # `publicá-la` and `verificá-lo` tokenise as `publicá` and `verificá`, neither of
            # which is a word on its own, and the fold-variants `pública` and `verifica` are
            # both attested — so the rule reported two perfectly correct rows. A token
            # immediately followed by a hyphen is part of a longer form; skip it.
            if stripped[m.end():m.end() + 1] == "-":
                continue
            variants = {v: n for v, n in groups.get(fold(lw), {}).items()
                        if v != lw and n >= ATTESTED_MIN and plausible(v, lang)}
            if variants:
                best = max(variants, key=variants.get)
                # Capitalized inside a name-shaped string: still worth reporting, because
                # `Cenaculo` for `Cenáculo` is real, but not worth acting on unverified,
                # because `Magnificat` and `Berlin-Frohnau` are names and correct as they are.
                conf = "medium" if w[:1].isupper() and name_or_code(cur) else "high"
                add("variant-attested", p, cur, cur.replace(w, best if w.islower() else
                                                            best.capitalize()),
                    f"{w!r} does not occur in {sum(freq.values())} words of {lang}; "
                    f"{best!r} occurs {variants[best]}x"
                    + ("; but this looks like a proper name, so confirm before changing it"
                       if conf == "medium" else ""), conf)
            elif i == len(toks) - 1 and len(lw) >= 5 and lw not in site_words:
                # Last word, unattested in the books — possibly a truncation. But only if the
                # site itself does not use the word either. The book corpus is small (231k
                # words of Spanish), so a perfectly ordinary word can be missing from it:
                # `Fecha de inicio` was reported as truncated because `inicio` is absent while
                # `inicios` occurs 8 times, and the proposed "fix" was `Fecha de inicios`,
                # which is wrong. The site's own 1,461 Spanish rows are a second lexicon and
                # they know `inicio` perfectly well.
                longer = [v for v in freq if v.startswith(lw) and len(v) > len(lw)
                          and freq[v] >= ATTESTED_MIN]
                if longer:
                    best = max(longer, key=lambda v: freq[v])
                    add("truncated", p, cur, cur[: len(cur) - len(w)] + best,
                        f"ends in {w!r}, which is unattested but is the start of "
                        f"{best!r} ({freq[best]}x) — the string looks cut off", "medium")
                else:
                    unattested.append((p, cur, w))
            else:
                unattested.append((p, cur, w))

    # The noisy bucket, capped and ordered by how odd the word is. Proper names, English
    # loanwords and (in German) legitimate compounds all live here, so it is a candidate list
    # and not a finding list.
    seen_ids = {f["phrase_id"] for f in findings}
    candidates = {}
    for p, cur, w in unattested:
        if p["phraseId"] not in seen_ids:
            candidates.setdefault(p["phraseId"], (p, cur, w))
    dropped = max(0, len(candidates) - UNATTESTED_CAP)
    for p, cur, w in list(candidates.values())[:UNATTESTED_CAP]:
        findings.append({
            "kind": "unattested", "phrase_id": p["phraseId"], "text_domain": p["textDomain"],
            "route": p["context"]["originRoute"] or "", "source": p["phrase"],
            "current": cur, "proposed": "", "confidence": "low",
            "why": f"{w!r} does not occur anywhere in the {lang} corpus and has no accent "
                   f"variant that does. Often a proper name or a loanword — check, do not assume",
        })

    dest = os.path.join(scratch, f"{lang}_mech_findings.json")
    json.dump({"language": lang, "environment": env, "corpus_words": sum(freq.values()),
               "rows_checked": len(rows), "findings": findings,
               "unattested_dropped": dropped},
              open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    by_kind = Counter(f["kind"] for f in findings)
    for k in ("variant-attested", "paired-punctuation", "placeholder", "truncated",
              "doubled-word", "bleed", "unattested"):
        if by_kind[k]:
            print(f"  {by_kind[k]:4}  {k}")
    if dropped:
        print(f"\n{dropped} further unattested words not reported (cap is {UNATTESTED_CAP}). "
              "Raise --cap or fix these first and re-run; they are not silently gone.")
    print(f"\nwrote {dest}")

    strong = [f for f in findings if f["kind"] in
              ("variant-attested", "paired-punctuation", "placeholder")]
    if strong:
        print(f"\nThe {len(strong)} strong findings:")
        for f in strong[:40]:
            print(f"  {f['phrase_id']:>5}  {f['kind']:<18} {f['why']}")
            print(f"         in: {f['current'][:96]!r}")


if __name__ == "__main__":
    main()
