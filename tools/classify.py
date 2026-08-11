"""Sort the Italian backlog into what to translate and what to leave alone.

The backlog is not 1,745 translatable strings. A large part of it is machinery that
happens to have passed through `translate()` — printf templates, call-number formats,
JSON blobs from association records, error messages assembled by concatenation — and a
second part is German source material from the Kentenich text corpus, which is a
scholarly translation question rather than a UI one.

Deciding that once, in code, with the rule written next to it, is the point of this
file. Every phrase lands in exactly one bucket and every bucket has a reason. Re-run it
after a writing session and the counts move; re-run it after the application changes and
the rules may need revisiting.

    python3 tools/classify.py /path/to/scratch --fetch      # read the live corpus
    python3 tools/classify.py /path/to/scratch              # re-use backlog.json

Reads   backlog.json (or it_backlog.json), and screens.json if it exists
Writes  classified.json    every phrase, with bucket and reason
        skip_pairs.json    the skips as (text_domain, source string) pairs

**The skip list is keyed on the pair, not on the string, and not on the phrase id.** Not the
id, because an id means nothing outside the environment it was read from. Not the string
alone, because `Update on advances` is dead welcome-page copy in `Application` and live text
in `SionModel` — matching on the string resurrects every skip decision in the wrong place.
The pair is stable across environments, which is what lets one classification serve both.

`--fetch` exists because the corpus now moves on its own. Phrase discovery was dead on every
Symfony-served route until 2026-08-11; with it repaired, rows arrive as pages render — 160 of
them during one working session. A classification is therefore dated, and re-running it is a
normal part of starting work rather than a one-off setup step.
"""

import json
import os
import re
import sys
import urllib.request
from collections import Counter, defaultdict

SCRATCH = sys.argv[1] if len(sys.argv) > 1 else "."
CREDS = os.path.expanduser("~/.config/schoenstatt/credentials.env")

# ---------------------------------------------------------------------------
# Skip rules. Each returns a reason string, or None.
#
# Order matters: the first rule that fires wins, so the most specific come first.
# ---------------------------------------------------------------------------

GERMAN_MONTH = r"(Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)"

# printf/ICU/positional format machinery with no prose around it
FORMAT_ONLY = re.compile(
    r"^(?:[^%{$:a-zA-Z]*"
    r"(?:%\d*\$?[-0-9.]*[sdfx]|\{[a-zA-Z][a-zA-Z0-9_]*\}|:[a-z_]+|\$\d+)"
    r"[^%{$:a-zA-Z]*)+$"
)
# nothing a translator can act on: digits, punctuation, whitespace, year ranges
NO_WORDS = re.compile(r"^[\s ­\d\-–—.,;:|/()\[\]*+#'\"]*$")

# A filename, not a phrase. The Kentenich text corpus is stored as markdown files and
# their names reached the phrase table: `1963-0118t029.md`, `1964-GEDEN337.md`,
# `1962-0617PRED.md`. There is nothing in them to translate, and a "translation" would
# break any lookup that goes through the name.
FILENAME = re.compile(
    r"^[A-Za-z0-9_.\-]+\.(md|txt|pdf|docx?|html?|xlsx?|csv|jpe?g|png|gif|zip)$", re.I)

# the dead Laminas welcome page — docs/phrase-table-noise.md group 3
DEAD_WELCOME = {6188, 6189, 6193, 6196, 6198, 6216, 6285, 6727, 6728, 6855, 7074, 7161}

# error strings the application builds by concatenation — noise doc group 1
CONCATENATED = (
    re.compile(r"^Error in form submission, please review: ."),
    re.compile(r"^The following book id's are invalid: ."),
    re.compile(r"^File not imported due to duplicate \w+: ."),
    # the change log labels each entry by appending the record's id
    re.compile(r"^(Assignment|Association|Person|Publication|Book|Role) Id: \d+$"),
    # the email validator interpolates whatever hostname was typed, so every typo
    # somebody has ever made in an address becomes a permanent row — the table holds
    # six of these, each with a trailing space inside the quotes
    re.compile(r"^'[^']*' is not a valid hostname for the email address$"),
)

# Bibliographic citations for the Kentenich text corpus, on the `text` routes. They
# name a volume, a publisher's place and a page range — `in: KENTENICH, Josef, Die
# Vision vom Berge Sion, Berg Sion ²1975, 49-93`. A citation is a citation in every
# language; translating one makes it wrong. These slip past the German test because
# they carry no German words, only German bibliographic abbreviations.
#
# The same routes also carry the physical description of each typescript, in German
# bibliographic shorthand: `verv.W, A 5 quer, 185 S.` (duplicated, A5 landscape, 185
# pages), `o.O., o.J.` (no place, no year), `masch.` (typescript). Nothing in these is
# language, and `S.` for *Seiten* is not `p.` for *pagine* — it is part of a citation.
CITATION = re.compile(
    r"^in:\s|,\s*S\.\s*\d|\bBand\s+\d|\bS\.\s*\d+\s*-\s*\d+|\d\s*\+\s*\d+\s*S\."
    r"|\bTeil\s+[IVX0-9]|\b\d+\s*S\.|\bo\.[OJ]\.|\bverv\.|\bmasch\.|^Nr\.:")

# The same concatenation bug, but the variable part is a **credential**. The
# api-tokens screen builds its success message by appending the freshly minted JWT, so
# the translator listener captured the whole thing as a phrase key — token included,
# and again in the English row. See docs/phrase-table-noise.md.
#
# Matched on the message prefix, never on the token shape, so this file never needs to
# recognise or handle a secret.
# Matched on the *token*, not on the message. This rule used to be
# `^Token issued\. Copy it now`, which was right while the only such rows were leaks — and
# became wrong on 2026-08-11, when the fix (schoenstatt.link#59 §1) made the screen file the
# template instead: `Token issued. Copy it now — it is not shown again and we do not store
# it: %s`. That row is ordinary translatable work carrying a placeholder, and the prefix rule
# skipped it as a secret. Verified against capsule row 13086.
#
# Three base64url segments separated by dots, starting `eyJ` — a JWT header is almost always
# `{"alg"…` or `{"typ"…`, which base64s to that. The match is never printed or logged; only
# the fact of it is.
LEAKED_SECRET = re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}")

# Free prose belonging to one association record — directions, opening notes, the
# history of a particular shrine. The noise doc found these as JSON; they also arrive
# as plain text, in whatever language the moderator typed. They are per-record content:
# a translation is stale the moment the record is edited.
RECORD_PROSE_ROUTES = {
    "association", "associations/association", "association-edit",
    "associations/association/edit", "associations/create", "associations/do-work",
    "jtranslate/phrase/edit",
}

# A machine-readable example a form shows in a `placeholder`: an opening-hours JSON blob whose
# keys the application parses, a JSON-LD event skeleton, a call-number format string. Not
# translatable in any language — translating `"friday"` would break the thing the example
# exists to be copied into.
#
# This is the ONLY part of the old `skip-record-content` bucket that survived review; see the
# note on `record_prose_bucket()` below for why the rest of it was wrong.
MACHINE_EXAMPLE = re.compile(
    r'^\s*[\[{]'                                  # a JSON object or array
    r'|^\{[a-zA-Z]+\}|%\d+\$[-0-9.]*[a-z]'        # a call-number format template
    r'|"@(context|type)"\s*:'                     # JSON-LD
    r'|"(mon|tues|wednes|thurs|fri|satur|sun)day"\s*:'
)
# 120 rather than something rounder: the shortest confirmed piece of record prose is
# the 143-character driving direction for the Cambrai shrine ("Directly on the big
# road, do not enter in the village of Thun-Saint-Martin…"), and the longest genuine
# interface string on these routes is the 116-character `Parent organization` help
# text. The gap between them is where the line goes.
RECORD_PROSE_MIN = 120

# The association edit form's own help text lives on the same routes as a moderator's note
# about one shrine, and is the same length. This set existed to rescue these four from being
# skipped by the length rule; nothing on these routes is skipped for length any more, so it
# now serves only to give them an accurate reason — they are instructions to the person
# filling the form, not an account of a particular shrine.
#
# Listed by id rather than matched by pattern, because the distinction is editorial and was
# made by reading them. Anything added here should be read the same way.
KNOWN_FORM_HELP = {
    6946,  # "Be as descriptive as possible, including closing days…" — opening-hours hint
    6948,  # "Please see OpeningHours::create([…]);" — points at spatie/opening-hours
    7055,  # "Please begin with '+' and the country code…" — phone format hint
    7169,  # "Instagram user names should begin with a letter…" — username format hint
}

TEXT_ROUTES = {"text", "texts", "texts/create", "text-edit"}

# The record show routes whose BREADCRUMB filed the record's own name as a phrase.
#
# The cause was misdiagnosed here until 2026-08-11. This file used to blame `headTitle()`, on
# the analogy of §7 — and `api-change-requests-response.md` §12 establishes that it was already
# `setTranslatorEnabled(false)` on `books/publications/show.phtml` and had been since 2019,
# while `books/compositions/show.phtml` never calls `headTitle()` at all. The actual path was
# `Application\Module::onBootstrap()`, which builds one navigation page per database row
# labelled with that row's own title, and §4's breadcrumb fix then translated those labels. So
# the rows arrived in bulk the day after a deploy rather than accumulating for years, and they
# arrived in the breadcrumb's own two lookup domains rather than in the page's domain.
#
# That matters here because it names the durable signal. **The page's real interface strings
# live in `Books` and `Schoenstatt`; nothing but the breadcrumb's two-step lookup files a
# phrase on these routes into `Application` or `default`.**
TITLE_ROUTES = {"publication", "composition"}
# The breadcrumb looks a label up in the navigation domain and falls back to `default`, filing
# a row on each miss. Both halves of that pair, and nothing else.
BREADCRUMB_DOMAINS = {"Application", "default"}


def is_title_artefact(p):
    """The signature of a record name that the breadcrumb filed as a phrase.

    Three conditions, mirroring the three in `database/db7.6.sql` statement 2, because any one
    of them alone is too broad among 10,166 publication titles.

    The third one used to be **"no other language has ever translated it"**, and
    `api-change-requests-response.md` §12 corrects that: it is not exact, and this file relied
    on it. `TranslationsTable::writeMissingPhrasesToDb()` copies translations onto a newly
    discovered phrase from any row of the same project holding the same text in another text
    domain — so a name that collides with an already-translated string arrives pre-translated
    in four languages seconds after it is filed, and then passes the old test. Six such rows
    survived `db7.4.sql` on production and needed a second migration.

    What the inherited copy cannot forge is being **different from the key**. Inheritance
    copies the same text, so an inherited row is still verbatim; a real interface string has at
    least one language that renders it differently. So the test is not "has anyone translated
    it" but "does any language DIFFER from it".

    Verified against production on 2026-08-11 over every live row on both routes. It catches
    13661/13662 (`Meu menino pequenino`, a composition name, whose inherited `pt` row is a
    verbatim copy and which the old test passed as ordinary work) and spares all fourteen
    genuine interface strings — including `Music`, which sits in `Application` on route
    `composition` and which conditions 1 and 2 alone would have caught wrongly.

    Deliberately NOT applied to `publications/publication` or to the `Schoenstatt` domain. The
    rows there that look like titles are **shrine names** — `Santuario del Padre`, `Heiligtum
    der Berufung` — which are §6's feature, translated in all five languages, and are what
    makes a shrine's name render in Italian. Retiring or skipping them would delete the
    feature. Their `origin_route` records only where the string was first seen, in 2019.
    """
    def val(l):
        return ((p["translations"].get(l) or {}).get("text") or "").strip()
    key = p["phrase"].strip()
    return (p["context"]["originRoute"] in TITLE_ROUTES              # 1. a record show route
            and p["textDomain"] in BREADCRUMB_DOMAINS                # 2. the breadcrumb's pair
            and not any(val(l) != key for l in ("en", "es", "pt", "de", "it") if val(l)))


def is_german(s):
    """Cheap German test, for source strings on the Kentenich text routes."""
    if re.search(GERMAN_MONTH, s):
        return True
    if re.search(r"[äöüßÄÖÜ]", s):
        return True
    return bool(re.search(
        r"\b(und|der|die|das|des|dem|den|nicht|ist|sind|Vortrag|vormittags|"
        r"nachmittags|abends|Ordnung|Heiligtum|Gottesmutter|Liebe|werden|haben|"
        # seasons and feasts date the text records as surely as the months do
        r"Weihnachten|Ostern|Pfingsten|Advent|Fastenzeit|Sommer|Winter|Herbst|"
        r"Frühling|Predigt|Tagung|Exerzitien|Brief|Gedenken)\b", s))


# ---------------------------------------------------------------------------
# The retirement note, per bucket. Bounded, and separate from the reason.
#
# **This used to be the same string, and that is how the first retirement note was
# truncated mid-word.** `docs/retire-queue.md` records the incident: a 270-character reason
# was sent against a 255-character limit and the server trimmed it, losing exactly the
# clause that said what to do if the phrase came back — the part a retirement note exists
# for. The reasons above have since grown well past 255 because they are written for a
# reader of this repository, which is a different audience with different needs.
#
# So they are two strings now. `reason` explains a classification to whoever is reading the
# classifier. `note` is addressed to one person in one situation: somebody looking at a
# phrase that is back on the translator's worklist, asking whether the retirement was wrong
# or the code that files the phrase is. It says what the row is, and what its return means.
#
# The limit is asserted here rather than trimmed at the call site, because a note that fits
# is a property of this file and discovering it does not fit at send time is too late.
# `writable.note.maxLength` in the phrase schema is the authority; 255 is its value and the
# assertion leaves room to spare.
# ---------------------------------------------------------------------------
NOTE_MAX = 255

RETIREMENT_NOTES = {
    "retire-breadcrumb-record-name":
        "A record's own NAME, filed by the breadcrumb's two-domain lookup, not interface text "
        "(api-change-requests-response.md 12). Not translatable in any language. Back on the "
        "worklist = the markDataLabels() fix regressed; report it, do not re-retire.",
    "retire-dead-page":
        "Copy from the retired Laminas welcome page. Checked on production 2026-08-11: the "
        "live English page does not contain this string; it says 'Our mission...' instead. "
        "Back on the worklist means the page renders it after all, so this was wrong.",
    "retire-retranslated-output":
        "The key is itself a translation — the site rendered its own translated output back "
        "through translate() and filed it. The caller was fixed on 2026-08-10, so this is "
        "residue. Back on the worklist = that fix regressed; report it, do not re-retire.",
}

for _bucket, _note in RETIREMENT_NOTES.items():
    assert len(_note) <= NOTE_MAX, f"{_bucket} note is {len(_note)} chars, over {NOTE_MAX}"


def is_writable(bucket):
    """Is this bucket ordinary translatable work?

    Two prefixes mean no. `retire-` is a row to take off the worklist with a note saying why;
    `skip-` is a row to leave exactly where it is.

    ## What separates them is NOT whether the row is translatable

    It is whether **anything still looks the row up**, and that took an experiment to learn.

    On 2026-08-11 this function said the line was *should this row exist*, and drew a second
    kind of retirement out of it: a row that exists legitimately and can never be translated
    in any language — a call-number format, a JSON-LD skeleton the form parses, `2007`, a lone
    non-breaking space, a corpus filename. The argument was that no language renders
    `%1$s%2$-8s%3$04d` differently, so the row cannot be completed by translating it, and a
    count including it can never reach zero.

    **The argument was right about the rows and wrong about the mechanism.** Retirement
    self-heals on lookup: a phrase the site still renders un-retires itself on the next missed
    lookup and writes no history. So retirement cannot durably remove a *rendered* row from the
    worklist, however untranslatable it is. Eleven such rows were retired; within five minutes
    two were live again — `7231`, the opening-hours JSON, because somebody loaded
    `associations/create`, and `7469`, the non-breaking space, because a `publication` page
    rendered. The other nine are on form routes nobody happened to open and will come back the
    same way. Meanwhile all fifteen rows in the two buckets below held, because nothing looks
    those up at all.

    That is the real test, and it is the one the schema states under `retirement.selfHealing`:

    - **`retire-`** — nothing renders this string. Copy from a page that no longer exists; a
      string the site translated back through `translate()` before the caller was fixed; a
      breadcrumb data label the breadcrumb no longer translates. Retirement holds because there
      is no lookup to heal it.
    - **`skip-`** — everything else, including rows that are rendered and untranslatable. The
      reason strings for those now say so, and say that retiring them was tried.

    A rendered-but-untranslatable row therefore cannot be taken off a translator's worklist
    from this side at all. That is a real gap and the fix belongs in the application — those
    call sites should not pass a parsed JSON example or a call-number format through
    `translate()` in the first place. Filed as `docs/api-change-requests.md` §16.

    Two buckets stay `skip-` for reasons that have nothing to do with rendering:

    - `skip-leaked-secret` — needs **deleting**, not retiring: the requirement is that the
      string cease to exist, which no API surface does. Retiring it would look like the
      problem had been handled.
    - `skip-concatenated-key` — `db7.7` retired the ones that existed, and the call sites were
      fixed on 2026-08-10. A new one is therefore evidence of a regression, and should be
      reported rather than quietly swept off the worklist.

    Anything that is not one of those is written. That default is deliberate: a new bucket
    added without thought becomes work rather than silently disappearing, which is the failure
    that is noticed rather than the one that is not.
    """
    return not bucket.startswith(("skip-", "retire-"))


def classify(p):
    """Return (bucket, reason).

    Buckets prefixed `skip-` are left alone; `retire-` are taken off the worklist with the
    reason as the `_note`; everything else is written. See `is_writable()`.
    """
    ph = p["phrase"]
    pid = p["phraseId"]
    route = p["context"]["originRoute"] or ""
    en = (p["translations"]["en"]["text"] or "").strip()
    es = (p["translations"]["es"]["text"] or "").strip()
    de = (p["translations"]["de"]["text"] or "").strip()
    pt = (p["translations"]["pt"]["text"] or "").strip()

    if is_title_artefact(p):
        return "retire-breadcrumb-record-name", (
            "a publication or composition's own NAME, filed as a phrase by the breadcrumb "
            "rather than by headTitle() — see api-change-requests-response.md §12 for the "
            "corrected mechanism. Not translatable in any language: rendering `Apologia pro "
            "vita mea` or `Meu menino pequenino` in Italian would invent an edition that does "
            "not exist, and where a real translated edition exists its title belongs on that "
            "publication's own record. The caller was fixed on 2026-08-11 and db7.4/db7.6 "
            "retired the bulk, so a row of this shape added AFTER that deploy is evidence the "
            "fix regressed and should be reported before it is retired")

    if pid in DEAD_WELCOME:
        return "retire-dead-page", (
            "copy from the retired Laminas welcome page. Verified against production on "
            "2026-08-11: not one of these twelve strings appears on the live English page, "
            "which now says 'Our mission — Schoenstatt Link is effectively a database…' "
            "instead (docs/phrase-table-noise.md group 3). Nothing renders it, so it cannot "
            "be seen in place and cannot be translated in context. If it is back on the "
            "worklist the welcome page renders it after all, and the skip was wrong")

    if LEAKED_SECRET.search(ph):
        return "skip-leaked-secret", (
            "the api-tokens screen appended a freshly issued JWT to its success "
            "message, so the token is baked into the phrase key and into the English "
            "row. Never translate it — a translation makes a third copy. The token "
            "needs revoking and the row needs deleting; retiring is not enough, because "
            "the requirement is that the string cease to exist. The caller was fixed on "
            "2026-08-11, so no new rows of this shape arrive")

    for rx in CONCATENATED:
        if rx.match(ph):
            return "skip-concatenated-key", (
                "the application built this string by concatenation, so the variable "
                "part is baked into the key; it is not translatable as written and the "
                "fix is at the caller (docs/phrase-table-noise.md group 1)")

    # ---- association routes: the rule this file got wrong -----------------------------
    #
    # Until 2026-08-11 everything long on an association route was skipped as "record
    # content, stale the moment a moderator edits the record". The maintainers' reply to
    # `docs/api-change-requests.md` §6 establishes that this was wrong twice over.
    #
    # It is not stale. A phrase's identity IS its text, so editing a description does not
    # corrupt its translations — the new description is a *different* phrase that renders as
    # itself until somebody translates it. Nothing on the site was ever stale; what went
    # stale was the worklist, and editing a description now retires the superseded phrase
    # automatically, reversibly, with a history note naming the association.
    #
    # And it is not noise. `SchoenstattTable` runs `PublicNotes` through the translator once
    # per locale **on purpose**: it is how an Italian-speaking pilgrim gets a shrine's
    # directions in Italian, and 60 live rows are exactly a `PublicNotes` value. Skipping them
    # was declining the feature the movement asked for. For a repository whose stated goal is
    # to make the shrines easier to find and visit, these were the *most* valuable rows in the
    # backlog and this file was excluding them.
    #
    # So the line is not interface-versus-content. It is **machine-readable versus prose**.
    if route in RECORD_PROSE_ROUTES or route in ("associations/create",):
        if MACHINE_EXAMPLE.search(ph):
            return "skip-machine-readable-example", (
                "a machine-readable example the form shows in a placeholder — an "
                "opening-hours JSON blob, a JSON-LD event skeleton, a call-number format. "
                "The application parses these keys, so translating one breaks the thing the "
                "example exists to be copied into. **Retiring these was tried on 2026-08-11 "
                "and does not hold**: the form renders the placeholder, so the next missed "
                "lookup un-retires the row. 7231 came back within five minutes. The fix is at "
                "the caller — see api-change-requests.md 16 and is_writable()")
        if pid in KNOWN_FORM_HELP:
            return "write-form-help", (
                "the association form's own help text, which sits on the same routes as "
                "record content and is the same length. Ordinary interface text: translate "
                "it, and keep any format example inside it intact")
        if len(ph) > RECORD_PROSE_MIN:
            return "write-record-prose", (
                "an association's own public notes — directions, opening times, a shrine's "
                "history — translated once per locale by design so a pilgrim reads them in "
                "their own language (api-change-requests-response.md §6). Long-form, and the "
                "SOURCE LANGUAGE VARIES: these are typed by moderators in Spanish, German or "
                "Portuguese as often as English, so identify the language before translating. "
                "If the record is superseded the phrase retires itself, so this does not rot")

    if NO_WORDS.match(ph):
        return "skip-nothing-to-translate", (
            "no words in it — digits, punctuation or whitespace only. `1`, `2007` and a lone "
            "non-breaking space are the same string in every language, so no translator can "
            "ever complete this row. **Retiring them was tried on 2026-08-11 and does not "
            "hold** for any that a page still renders: 7469, the non-breaking space on a "
            "publication page, was live again within five minutes. See is_writable()")

    if FILENAME.match(ph):
        return "skip-filename", (
            "a filename from the Kentenich text corpus, not a phrase. Translating it would "
            "change a string the corpus is indexed by, so it is untranslatable in every "
            "language rather than merely untranslated. Not retired: the corpus pages render "
            "these, so a retirement would self-heal on the next lookup — the same reason the "
            "format templates are skipped rather than retired")

    if FORMAT_ONLY.match(ph):
        return "skip-format-template", (
            "a format template, not prose: the placeholders are the whole string and the site "
            "interpolates into it. Nothing here any language renders differently, so the row "
            "can never be completed by translating it. **Retiring these was tried on "
            "2026-08-11**; they are still retired only because nobody has opened the library "
            "edit form since, and they will return on the next render. See is_writable()")

    if route in TEXT_ROUTES and CITATION.search(ph):
        return "skip-bibliographic-citation", (
            "a bibliographic citation for the Kentenich text corpus — volume, place "
            "and page range. A citation is the same in every language and translating "
            "it would make it wrong")

    # the Kentenich text corpus: German metadata and prose, on the text routes
    if route in TEXT_ROUTES and is_german(ph):
        if en and en != ph:
            # A handful were translated into English (and 2 of 67 into Spanish), so
            # there is *some* precedent — but a precedent set on 2 strings out of 300
            # is not a house convention, and the corpus is one decision, not 300.
            return "skip-german-source-precedent", (
                "German source material that does have an English rendering, so this "
                "one string has precedent — but the corpus should be decided as a "
                "whole, not string by string. Listed separately so the precedent is "
                "visible to whoever decides")
        return "skip-german-source-material", (
            "German source material from the Kentenich text corpus, not interface "
            "text. No language has systematically translated these: of the 67 "
            "date-shaped strings only 2 have Spanish, and English copies the German "
            "verbatim. Whether the corpus should be translated at all is a decision "
            "for the movement, not a gap to fill")

    # A phrase whose key is already a *translation* — the site translated its own output.
    # `headTitle()` translates whatever it holds, so a template that handed it an
    # already-translated string made the page translate that, and the result was filed as a
    # phrase in its own right. Fixed at the caller on 2026-08-11 (api-change-requests §5), so
    # no new ones arrive; the existing rows should be retired and must never be translated —
    # translating `Registrar` into Portuguese would produce a third copy of a bug.
    #
    # One list per language the artefacts were found in. Italian came first because the
    # Italian pass met them; Spanish and German turned up in the account beat on the same
    # routes — `Acceder`, `Anmelden`, `Registrar` sitting on `zfcuser/login` and
    # `zfcuser/register`, each identical to its own English row.
    RETRANSLATED = r"^(Registrati|Accedi|Esci|Acceder|Registrar|Anmelden|Abmelden|Registrarse)$"
    if pid == 13032 or (ph == en and re.match(RETRANSLATED, ph)):
        return "retire-retranslated-output", (
            "the key is itself a translation: the site rendered an already-translated "
            "string back through translate() and captured it as a new phrase. Writing a "
            "translation here would legitimize a row that should not exist. The caller was "
            "fixed on 2026-08-10 — the layout no longer hands headTitle() a string it has "
            "already translated — so a row of this shape added after that deploy is "
            "evidence the fix regressed and should be reported before it is retired")

    # ---- everything below gets written ----

    # proper names and codes that every language keeps verbatim
    if ph in ("Schoenstatt Link", "Schoenstatt", "Schoenstatt Link Team"):
        return "write-verbatim", "proper name; es, pt and de all keep it unchanged"
    if re.match(r"^https?://", ph):
        return "write-verbatim", "a URL"
    if re.match(r"^[a-z]{2}$", ph) and es == ph and de == ph:
        return "write-verbatim", (
            "a language code the site displays raw; all four other languages render "
            "it unchanged (the language *names* are separate phrases and are translated)")

    guides = sum(1 for x in (es, de, pt) if x)
    if guides >= 2:
        return "write-guided", f"interface text with {guides} sibling renderings to follow"
    if guides == 1:
        return "write-thin", "interface text with only one sibling rendering to follow"
    return "write-cold", (
        "no sibling language has translated this, so there is no house convention to "
        "follow — translate from the source and flag anything charism-specific")


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


def fetch_corpus():
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
    print(f"fetched {len(items)} phrases from {env}")
    json.dump(items, open(os.path.join(SCRATCH, "backlog.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return items


def main():
    if "--fetch" in sys.argv:
        backlog = fetch_corpus()
    else:
        for name in ("backlog.json", "it_backlog.json"):
            path = os.path.join(SCRATCH, name)
            if os.path.exists(path):
                backlog = json.load(open(path, encoding="utf-8"))
                break
        else:
            sys.exit(f"no backlog.json in {SCRATCH} — pass --fetch to read the live corpus")

    # Where each phrase is visible, and in what element. Optional: screens.py is an Italian
    # pass over 109 known pages, so it has nothing to say about rows that arrived since.
    sp = os.path.join(SCRATCH, "screens.json")
    screens = json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else {"screens": []}
    visible = defaultdict(list)
    for s in screens["screens"]:
        for f in s.get("visible_untranslated", []):
            visible[f["phrase_id"]].append({
                "url": s["url"],
                "enclosing": f["enclosing"],
                "heading": f["heading"],
                "nearby": f["nearby"],
            })

    out = []
    for p in backlog:
        bucket, reason = classify(p)
        seen = visible.get(p["phraseId"], [])
        out.append({
            "phrase_id": p["phraseId"],
            "text_domain": p["textDomain"],
            "route": p["context"]["originRoute"],
            "url": p["context"]["url"],
            "phrase": p["phrase"],
            "en": p["translations"]["en"]["text"] or "",
            "es": p["translations"]["es"]["text"] or "",
            "pt": p["translations"]["pt"]["text"] or "",
            "de": p["translations"]["de"]["text"] or "",
            "bucket": bucket,
            "reason": reason,
            "pages_visible_on": len(seen),
            "element": seen[0]["enclosing"].split("/")[-1] if seen else "",
            "seen": seen[:2],
        })

    json.dump(out, open(os.path.join(SCRATCH, "classified.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # The exclusion list every downstream tool reads. Writing it here rather than by hand is
    # the point: a skip decision is a judgement made once, and it should be produced by the
    # file that holds the reasoning, not retyped alongside it.
    #
    # `retire-` counts as an exclusion here as well as `skip-`. It has to: a retire candidate is
    # a row that should not exist, so it is the last thing that should be offered as work while
    # it waits for the retirement to be actioned.
    pairs = sorted({(r["text_domain"], r["phrase"]) for r in out
                    if not is_writable(r["bucket"])})
    json.dump([list(p) for p in pairs],
              open(os.path.join(SCRATCH, "skip_pairs.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # The retire candidates, separately, because these need an action taken rather than merely
    # being left alone. Each carries both strings: `reason` for a reader of this repository,
    # and `note` — bounded, and what actually goes to the API. See RETIREMENT_NOTES.
    missing_notes = sorted({r["bucket"] for r in out
                            if r["bucket"].startswith("retire-")
                            and r["bucket"] not in RETIREMENT_NOTES})
    if missing_notes:
        sys.exit(f"no RETIREMENT_NOTES entry for {missing_notes}. A retirement's note is "
                 f"required by the API and is the entire record of the judgement, so a new "
                 f"retire- bucket needs one written for it — see RETIREMENT_NOTES.")
    retire = [dict(r, note=RETIREMENT_NOTES[r["bucket"]]) for r in out
              if r["bucket"].startswith("retire-")]
    json.dump(retire,
              open(os.path.join(SCRATCH, "retire_candidates.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print(f"{len(out)} phrases\n")
    counts = Counter(r["bucket"] for r in out)
    skip = sum(c for b, c in counts.items() if not is_writable(b))
    for b, c in sorted(counts.items(), key=lambda kv: (is_writable(kv[0]), -kv[1])):
        print(f"  {c:5}  {b}")
    print(f"\n  {skip:5}  TOTAL NOT WRITTEN")
    print(f"  {len(out) - skip:5}  TOTAL TO WRITE")
    print(f"  {len(retire):5}  of the not-written are RETIRE candidates -> retire_candidates.json")
    print(f"  {len(pairs):5}  distinct (text_domain, phrase) skip pairs -> skip_pairs.json")
    print("\nto-write by text domain:")
    for d, c in Counter(r["text_domain"] for r in out
                        if is_writable(r["bucket"])).most_common():
        print(f"  {c:5}  {d}")


if __name__ == "__main__":
    main()
