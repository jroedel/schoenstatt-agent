# CLAUDE.md

## What this repository is

**schoenstatt-agent** is the agent-side workspace for maintaining a public reference
database of information about Schoenstatt. It is volunteer work, maintained by one
person.

It is not the database. The database is [schoenstatt.link](https://schoenstatt.link),
a separate application with its own repository. This repository holds the **context,
conventions, curated reference data and tooling** an agent needs to do careful,
attributable work against that database — starting with translations, later with the
Schoenstatt Shrines.

**It is not an official publication of the Schoenstatt movement and does not speak for
it or for any of its bodies.** That is a statement of scope rather than of modesty:
nothing here decides what Schoenstatt teaches, what a shrine is, or who is responsible
for anything. Where the movement's own sources settle a question, they settle it — and
where they and this repository disagree, the disagreement is a finding to report, not
something to resolve here.

The work is ordinary stewardship: gather information, correct it, keep it current, and
make it easy for someone else to check. Three commitments follow from that and govern
everything below.

- **Accuracy over throughput.** A wrong translation of a charism term or a wrong
  address for a shrine is worse than a missing one, because a missing one is visibly
  missing. Nobody re-checks a filled field.
- **Attributability over speed.** Every write this repository's tooling makes is
  recorded against a named account. That is the safety model — writes are not
  reviewed before they land, they are recorded so they can be found afterwards.
- **The tooling decides nothing that matters.** It fills gaps, checks its own work
  mechanically, and reports what it could not settle. What a thing is called, what
  belongs in the database and who is responsible for it are decisions for people. An
  agent that is unsure says so and leaves the field empty — an empty field is visibly
  empty, and a confidently wrong one is not.

## This repository is public

Write every file as though a stranger will read it, because one may. It is expected
to be published on GitHub once it has content worth publishing.

- **Never commit credentials.** No JWTs, no passwords, no database dumps, no
  `.env`. Secrets live in `.env` (gitignored) or the environment, never in tracked
  files, never in a committed example, never pasted into a doc as "the one we used".
  If a credential reaches a commit, it is compromised — revoke it (see
  [Credentials](#credentials)) rather than rewriting history and hoping.
- No internal hostnames, no server paths, no personal contact details, no anyone's
  home address. Shrine addresses are public information and are the point; a
  volunteer's phone number is not.
- **Write paths relative to the repository root**, including paths to things outside it:
  `../schoenstatt.link`, `../reading-material`, both sibling checkouts. An absolute path
  is a fact about one machine, and a scratch directory pasted into a script as a
  constant stops working the moment the session that made it ends — which is what five
  of the index scripts did until 2026-08-11. In code, derive the root from `__file__`
  rather than the working directory, and take a scratch directory as an argument.
- No unreleased plans, no unannounced anything. `docs/` is for how the work is done.
- **Don't quote record content verbatim — describe it and give the phrase id.** A phrase
  whose source is a database record can be anyone's candid administrative note, and a
  document illustrating a classifier bucket does not need the words to make its point. The
  id is enough for anybody who needs to look. Shrine directions and opening hours are the
  exception: they are public information and quoting them is the job.
- **Don't write anything that implies official standing, and don't announce virtues.**
  No "approved by", no "official", no citing a Church document to lend weight to a
  tooling decision. A file that declares its own transparency invites the reader to
  test the claim; one that simply records what it did — and what it could not settle —
  does not have to. The register to aim for throughout is a maintenance log: plain,
  specific, checkable, quiet. When in doubt, under-claim.
- **License:** Apache-2.0 for code, CC BY-SA 4.0 for curated data under `data/`.
  Keep the two clearly separated so downstream users can tell which applies.

## Layout

```
README.md              what this is, for a reader who arrives from GitHub
CLAUDE.md              this file — the working contract
cmd/schoenstatt-mcp/   the MCP server exposing the translation API as tools
internal/schoenstatt/  the API client, and the language-code mapping it depends on
tools/                 the pipeline that regenerates the translation index
data/
  glossary/            de en es it pt — Schoenstatt terms, their agreed rendering in each
                       language, and the source each was attested against
  style/               de es it pt — register, address forms, capitalization, and for pt
                       why not to copy Spanish. No en, because most source strings are
                       already English; there is an en glossary because terms still differ
docs/
  de-du-corrections.json     the du/Sie sweep, as sent
  de-umlaut-corrections.json the Schönstatt umlaut sweep, as sent
  translation-index.md    which page shows which untranslated phrase
  phrase-table-noise.md   what is in the phrase table that is not a phrase
  it-skipped.md           the phrases deliberately left untranslated, and why
  api-change-requests.md  what this repo would like changed in the application
  retire-queue.md         phrases added by mistake, and why each should leave the worklist
  it-pass-2026-08-10.md   the Italian pass: what was written to each site, and how
  it-review-queue.md      100 written translations awaiting a native speaker
  pt-audit.md             24 existing Portuguese translations found wrong, and corrected
  corrections-2026-08-11.md  21 corrections, 12 held back, and why each was held
  pt-pass-2026-08-11.md   Portuguese closed: 344 rows, and the two classifier errors
  close-2026-08-11.md     all five languages to 0: 141 translations, 64 retirements
  it-review-2026-08-11.md the 16 of that pass's Italian writes worth a second opinion
  de-review-2026-08-11.md the same for German — 13, two of them house decisions
  es-review-2026-08-11.md the same for Spanish — 10, four with a Spanish source string
  pt-review-2026-08-11.md the same for Portuguese — 6, plus one defect found in an old row
  workflow-review.md      what running the workflows taught, and the 2026-08-11 rewrite
  jtranslate-proposals.md the 2026-08-10 schema changes, as asked for and as shipped
```

`.claude/skills/schoenstatt-translation/` holds the method as a skill, and
`.claude/workflows/translate-bulk.js` / `translate-revise.js` automate the fan-out —
**both produce proposals; every write to the site goes through the main loop.**

`tools/` holds the pipeline behind those documents: `screens.py` finds which untranslated
phrase is visible on which page and in what element; `classify.py` sorts the backlog into
translate-or-skip with a reason per bucket; `build_worklist.py` groups the gap into **beats**
(one family of related routes, whole — one agent's assignment); `conform.py` checks drafted
translations mechanically; `hunt_lexical.py` finds defects in existing ones using the books as
a lexicon; `apply_translations.py` writes the batches (dry run by default);
`apply_corrections.py` is the only path that **overwrites** an existing translation, and
asserts the current value before replacing it; `apply_retirements.py` takes rows off the worklist
and **refuses a batch that would leave a live sibling row of the same string behind**;
`build_review_queue.py` produces the review documents; `extract_reading_material.py` pulls text out of the Schoenstatt books in
`../reading-material` for terminology mining. See
[`tools/README.md`](tools/README.md).

**Prefer a script to a subagent wherever the question is decidable.** The last three of those
tools were subagents first and were worse at the job — one of them was literally instructed to
*write a script*. Moving them cut a language's drafting workflow from seven agents to five and
its revision workflow from 79 to six, and made both results reproducible. An agent's place in
this pipeline is judgement: what the movement calls a thing, how a page reads, which of two
renderings is right.

**The books in `../reading-material` are copyrighted.** Extract them to a
scratch directory for mining and put only short attestations — a term, a count, a clause —
into `data/`. Their text must never be committed.

`data/` is **curated reference input, not a mirror.** The schoenstatt.link database
stays the source of truth for phrases and associations. Files here exist to make the
agent's judgement reproducible and reviewable — a glossary entry is a decision
somebody made once, written down so it is made the same way next time. Never
regenerate `data/` from the API and never treat it as a cache.

## The system this repository talks to

schoenstatt.link is a PHP application (Symfony).
**Its `docs/api-v3.md` is the
authoritative API contract — read it before writing any client code, and prefer it to
this file wherever the two disagree.** That repository has its own `CLAUDE.md`
governing changes to the application itself; this file governs only this one.

**Treat `../schoenstatt.link` as read-only from here.** Other agents are
working in that checkout. Read it freely — the API doc, the source, the config are
all worth reading and are often the fastest way to settle a question — but do not
edit files, do not run its test suites, and do not `git` anything there. A change
that belongs in the application belongs in a session working on the application.
Two consequences follow. Its working tree may move under you mid-session, so
re-read rather than trusting what you read an hour ago; and the API contract itself
may change under you, which is why nothing here hardcodes what the schema endpoint
can tell you at request time.

The v3 API exposes two unrelated resources, each gated on its own role:

| resource | role | what it is for |
|---|---|---|
| `/api/v3/phrases` | `sch_api_translator` | reading and improving translations |
| `/api/v3/associations` | `sch_api_bot` | keeping the shrine database current |

**Hold one role per credential, never both.** The separation is the whole point: a
leaked token reaches one resource, not "the API". An agent that does both jobs is an
agent whose leaked token reaches everything.

Start every session against the API with `GET /api/v3/schema` (public, no token) and
then `GET /api/v3/schema/{entity}`. The entity schemas are generated from the same
specification the web forms and the `PATCH` endpoints validate with, so they cannot
drift. Validate locally against them rather than discovering rules by rejection.

### It is not reachable in production yet

v3 is served by the Symfony front controller. It was **canary-gated** — only a request
carrying `sl_symfony_canary=1` reached it — and an agent will not send a staging
cookie and should not be asked to.

**In the capsule that gate is already open**: as of 2026-08-10 the site footer there
reports `SYMFONY_KERNEL=1, the site default`, and `/api/v3/*` answers without any
cookie.

**Production works, as of 2026-08-10.** The canary gate is open there too: `GET
/api/v3/schema` and `GET /api/v3/schema/phrase` answer `200` with no cookie, and the
phrase schema reports exactly what the capsule reports — `writable.languages` =
`es de pt it en`, `maxLength` 2000. `SCHOENSTATT_TRANSLATOR_JWT` authenticates, and
**1,383 Italian translations were written to production through
`PATCH /api/v3/phrases` on 2026-08-10, 0 failures.** The phrase endpoints are therefore
verified against production, which this file previously said they never had been.

Earlier the same day the production token returned `401` on the collection while the
schema answered `200`. It was re-minted and works. That is the fourth item on the 401
checklist behaving exactly as documented — do not spend time diagnosing a 401 from its
body.

The capsule is still the right place to *develop* a pass — it is disposable and
production is not. But it is no longer the only place work can land. Don't write code
that assumes either base URL; take it from configuration.

## Phase 1 — translations

This is the current work. It is deliberately low-stakes: a bad UI string is visible,
cheap to notice and cheap to fix.

### The languages

`de` · `en` · `es` · `it` · `pt`

### The source string is not guaranteed to be English

A phrase *is* its source string — the key the site looks itself up by. That string is
**usually English, but nothing requires it to be.** The data structure has no notion
of a source language, and phrases originating from the database rather than from a
template can be in any language. `Books` is the obvious place to expect this: a title
is whatever language the book is in.

This is the assumption most likely to produce a confidently wrong translation, so
treat it as a rule:

- **Read the source string and determine what language it is in before translating
  it.** Do not infer the language from the fact that it is the key, from the text
  domain, or from the other translations already present.
- **`en` is a translatable target like any other.** When the key is German, the
  English row is a real translation and can be missing — `untranslated_in: "en"` is a
  legitimate query that returns real work, not a contradiction.
- **When the source is not English, the key still must not be edited.** It is the
  lookup key, not editable content. A source string in the wrong language, or with a
  typo, is fixed where the phrase is generated — not here.
- If you cannot tell what language a source string is in, say so and leave it. A
  translation written from a misread source is not recoverable.

**Language codes are ISO 639-1 — always `en`, never `en_US`.** The API settled this
on 2026-08-10: `GET /api/v3/schema/phrase` now reports `writable.languages` as
`es de pt it en`, and its own notes say the region subtag "is an artefact of how
catalogs are keyed internally and is never part of this API". The regional form of a
listed language is **refused, not accepted as a synonym** — sending `it_IT` is an
error, not a slightly-wrong spelling.

Before that date the same field was called `writable.locales` and carried `en_US`,
`it_IT` and so on. Anything written against the old shape reads no languages at all
from the new one and refuses every write, which is how the change was noticed here.

The rule that survives both shapes is the one that was always true: **never hardcode
the language list, and never hardcode which key it lives under.** Read it at request
time. `internal/schoenstatt` reads `writable.languages` and falls back to
`writable.locales`, maps whatever it finds to simple codes, and has tests pinning
both shapes — so the same tool surface works against a site on either side of the
change.

One rule for the mapping, which the server enforces and any other client should too:
**a short code is only used where it is unambiguous.** If the site ever writes both
`pt_BR` and `pt_PT`, `pt` names neither and the full code is required. Picking one
would write a translation into the wrong language, and a translation cannot be
unwritten.

### Italian is the gap

Italian is fully wired up — a supported language, writable through the API, present in
routing — and almost entirely untranslated. Counted in the database on 2026-08-10,
after the deduplication and the blog cleanup, over phrases that are **not retired**:

| text domain | phrases | en | es | pt | de | **it** |
|---|---|---|---|---|---|---|
| Books | 802 | 802 | 379 | 113 | 120 | **0** |
| Schoenstatt | 698 | 697 | 661 | 471 | 465 | **7** |
| default | 87 | 87 | 52 | 37 | 37 | **0** |
| JUser | 76 | 76 | 28 | 24 | 24 | **3** |
| SionModel | 43 | 43 | 30 | 20 | 20 | **1** |
| Application | 36 | 36 | 35 | 33 | 33 | **7** |
| ZfcUser | 29 | 29 | 14 | 12 | 12 | **0** |
| JTranslate | 25 | 25 | 5 | 4 | 4 | **0** |
| Bible | 19 | 19 | 15 | 5 | 5 | **2** |

**1,815 phrases; 20 of them have Italian.** That is the whole corpus now — before the
cleanup the same table held 6,874 rows, and the difference was duplicates and blog
strings, not work.

**That table is the state before the 2026-08-10 translation pass.** After it:

| | capsule | production |
|---|---|---|
| phrases with Italian | **1,420** | **1,401** |
| without | 396 | 394 |
| total | 1,816 | 1,795 |

The remaining ones are all deliberate — see [`docs/it-skipped.md`](docs/it-skipped.md)
for what they are and why. The two sites do not hold the same corpus: 17 phrases exist
only on production, 38 only in the capsule. The table above is kept because it is what
the gap looked like, and because the German and Portuguese columns have not moved.

Take the live numbers from the API rather than from this table —
`phrase_search(untranslated_in="it", text_domain="Application")` is a `WHERE`
clause, not a filter applied after paging. (Against the raw API the parameter is
`?untranslatedIn=` and takes whatever code the schema reports.)

**Do not count the compiled catalogs in `../schoenstatt.link/language/`.**
They are gitignored build output, the exporter overwrites but never deletes, and a
file with no rows behind it simply stays on disk looking authoritative. An earlier
version of this table was read from there and got `Books` wrong by 157: the Italian
Books catalog is a leftover benchmark fixture whose every value reads
`prova di misurazione 6388`. Anything the database does not have, the site does not
really have.

Note the shape of the gap: German and Portuguese trail Spanish too, so Italian is the
priority but not the only work.

**`Books` is not books.** An earlier version of this file warned that the `Books` domain
was the risky one because "a book with a real published Italian edition needs that
edition's title found, not a translation invented". That was wrong, and it was wrong in
a way that would have made somebody treat the largest block as unapproachable research.
Counted on 2026-08-10, the 802 `Books` phrases are:

- **~380 interface strings** for the library and publication modules — `Admin notes`,
  `Call number`, `Enable checkouts?`, `Publisher`. Ordinary UI, and already translated
  into Spanish, which is how they are identifiable.
- **~220 text-corpus artefacts** — markdown filenames, bibliographic citations and
  German physical descriptions of typescripts. Not translatable in any language.
- **the rest** German date and heading metadata from the Kentenich texts.

**`Books` is the text domain the library module happens to use, not a domain of books.**

**Record names reached the phrase table, and the cause was the breadcrumb — not
`headTitle()`.** This file blamed `headTitle()` until 2026-08-11 and was wrong, which matters
because it aimed a fix at code that had been correct since 2019:
`books/publications/show.phtml` already called `setTranslatorEnabled(false)` and
`books/compositions/show.phtml` never calls `headTitle()` at all.

The real path was `Application\Module::onBootstrap()`, which builds **one navigation page per
database row** — 10,166 publications, every composition, every library, every association —
labelled with that row's own name. Nothing translated a breadcrumb label until the §4 fix did,
and a translator miss is how a phrase is filed. So the corpus captured the library's whole
catalogue in a day, two rows per record because the breadcrumb falls back to `default` when the
navigation domain misses. That also explains the two things `headTitle()` never accounted for:
why the rows appeared the day *after* a deploy rather than over years, and why they arrived in
`Application` **and** `default` rather than in the page's own domain.

**Fixed, and ~4,100 rows have left the worklist** — `db7.4.sql` retired 3,698 publication
titles, 302 composition names, 108 association names and 24 navigation labels; `db7.6.sql` took
the last six. So **any "how much is left to translate" figure predating 2026-08-11 is wrong in
our favour.** Route `publication` is down from 436 rows to 10, `composition` from 87 to 7, and
the whole corpus from 2,155 to about 1,600.

Measured on production twice on the afternoon of 2026-08-11, roughly forty minutes apart:

| | total | it | de | pt | es | en |
|---|---|---|---|---|---|---|
| first read | 1,599 | 138 | 117 | 35 | — | 1 |
| second read | **1,581** | **120** | **99** | **17** | 84 | 1 |

**Both reads were correct; the corpus moved between them.** 18 rows left, and `it`, `de` and
`pt` each fell by exactly 18 — one retirement sweep of rows untranslated in all three. That is
the useful lesson rather than either number: work is landing on the application side during a
session, so **take these figures from the API at the moment you need them.** Anything written
down here, including this table, is a reading and not a fact.

**Later the same day the gap closed in every language, and then did not stay closed.** Both
readings are in [`docs/close-2026-08-11.md`](docs/close-2026-08-11.md):

```
12:47 UTC   it: 0    de: 0    pt: 0    es: 0    en: 0     live 1,515   retired 4,537
13:05 UTC   it: 2    de: 2    pt: 2    es: 2    en: 1     live 1,543
```

173 translations written and 64 rows retired. Three things to hold on to, because none of them is
what "zero" sounds like:

- **Zero untranslated is not fully translated.** It means no *live* row lacks a language. 4,537
  rows are retired, each with a note saying why it is not work, and `?onlyRetired=1` is how you
  audit that rather than take it on trust.
- **The number will not stay zero**, and a new row is work rather than a defect unless it matches
  a signature in `tools/classify.py`. Eleven arrived eighteen minutes after that zero, from
  application-side work. Re-run the classifier; do not read a count from this file.
- **The 2 in the second row are a retirement that the site reversed**, not new work, and they were
  left alone on purpose. A row live again with a `retire` and no `unretire` after it is the
  feedback signal; see the retirement section below.

Two things this leaves that are easy to get backwards:

- **A title-shaped row is not automatically the defect.** The ones that remain on
  `publications/publication` in the `Schoenstatt` domain are **shrine names** — `Santuario del
  Padre`, `Heiligtum der Berufung` — translated in all five languages, and they are what makes
  a shrine's name render in Italian. That is §6's feature. Do not retire them or skip them.
  Their `origin_route` records only where the string was first seen, in 2019.
- **The signature this repo gave for a title is not exact, and `classify.py` relied on it.**
  It was "the English row is a verbatim copy of the key **and** no other language has ever
  translated it". But `TranslationsTable::writeMissingPhrasesToDb()` **copies translations onto
  a newly discovered phrase** from any same-text row in another text domain, so a name that
  collides with an already-translated string arrives pre-translated in four languages and then
  passes the second test. Six rows survived `db7.4` that way.

  **Classify on `originRoute` + `textDomain` first.** Nothing but the breadcrumb's own two-step
  lookup files a phrase on these routes into `Application` or `default`; the page's real
  interface strings live in `Books` and `Schoenstatt`. What an inherited copy cannot forge is
  being *different* from the key — so the third test is "does any language **differ**", not "has
  anyone translated it". `classify.py` was rebuilt on those three conditions and verified
  against every live row on both routes: it catches the composition name `Meu menino pequenino`
  (which the old test passed as ordinary work) and spares all fourteen interface strings,
  including `Music`, which sits in `Application` on route `composition` and which the route and
  domain alone would have caught wrongly.

  **The forger does not have to be inheritance — it can be us.** `db7.4.sql` statement 4 was
  written to retire association names on route `association` in those two domains, and it missed
  nineteen of them, because its last condition is "nothing has translated this beyond English"
  and **this repository's own Portuguese pass had filled `pt` on all nineteen hours before the
  migration ran.** So the rule is stronger than §12 states it: *"somebody has translated it"* is
  never evidence about what a row is, whoever the somebody was. Those 38 rows — 19 sibling pairs —
  were retired on 2026-08-11; see [`docs/retire-queue.md`](docs/retire-queue.md).

  **A `Schoenstatt`-domain sibling is the discriminator that survives all of this.** The
  translatable shrine names live there by design, because `IsNameTranslateable` and the kind-name
  formats put them there. A string with such a row is one whose `Application`/`default` copies are
  breadcrumb duplication of §6's feature; a string without one is a name nothing was ever designed
  to translate. On route `association`, seventeen strings have one and were left alone, nineteen
  had none and were retired.

**Expect the corpus to keep moving.** It grows as pages render — 1,798 rows on 2026-08-10,
2,155 the next afternoon, 1,599 after the retirements. Re-run
`python3 tools/classify.py <scratch> --fetch` at the start of a session rather than trusting a
number here, and treat a new bulk arrival as a probable defect at the caller before treating it
as work. A row matching the breadcrumb signature but added *after* the 2026-08-11 deploy is
evidence the fix regressed, and should be reported before it is retired.

### How to work

**Start from [`docs/translation-index.md`](docs/translation-index.md).** It maps the
backlog onto 109 verified pages, so the work can be done a page at a time with the
phrase visible in place — which is the hard part of this project, not the
translating. Read its first sections before trusting any count: 164 phrases have a
non-English source and they concentrate in the pages with the most work, and one
compiled catalog in the capsule serves 157 fake Italian strings left over from a
benchmark, which will otherwise read as "already translated" on a Books page.

1. **Read a filtered page.** `phrase_search` with `untranslated_in`, `text_domain`,
   `search`, `limit` (default 100, max 500). An unknown parameter is a `422`, not a
   silent full collection, and an unknown language is refused rather than ignored.
2. **Identify the source language**, then look at where the phrase came from.
   `context.url` is the page, and it is always the **English** one. When the source
   string is English you therefore see the key verbatim, in situ. When it is not, that
   page shows the *English translation* of the phrase — which is a translation, not
   the source, and must not be mistaken for it. Translate from the key.
   **The URL is `null` more often than not** — most routes take parameters, and the
   largest sources are `text` (219 phrases), `associations/association` (151) and
   `associations/association/edit` (149), none of which can be turned into a URL
   without knowing *which* text or association. A null means "you cannot see this one
   in situ". Accept that; never guess a URL by substituting an id.
3. **Check `data/glossary/` and `data/style/` before choosing a rendering.** If the
   term is not there and it is a Schoenstatt term, add it as part of the same piece
   of work. The glossary is how a decision survives the session that made it.
4. **Batch the writes.** `phrase_batch_patch` takes up to 200 at a time. Every
   single-phrase write recompiles every translation catalog; the batch recompiles
   once. Five individual PATCHes take 1.26 s where the same five batched take 0.24 s.
5. **Send the etag** on single-phrase writes — `phrase_get` returns it, `phrase_patch`
   takes it. The batch endpoint does not honour it: a conditional request is defined
   over one resource.

### The MCP server

`cmd/schoenstatt-mcp` exposes the phrase API as seven tools — `phrase_languages`,
`phrase_search`, `phrase_get`, `phrase_patch`, `phrase_batch_patch`, and, since the retirement
endpoints shipped on 2026-08-11, `phrase_retire` and `phrase_unretire`. Build it with
`go build ./cmd/schoenstatt-mcp` and register the binary in your MCP client; it reads
`~/.config/schoenstatt/credentials.env` itself, so the client needs no env block.

It holds one credential, so it reaches one resource. **The association endpoints are
deliberately not implemented** — a leaked translator token should have nothing
shrine-shaped to reach even by accident. When phase 2 starts, that is a second
binary with a second token, not another tool here. The line is the *resource*, not the tool
count: retirement was added because it is the phrase resource under the same role, which is
exactly what the association endpoints are not.

The tools encode the contract rather than restating it: language codes are resolved
against the live schema, an empty translation is refused with the reason, an
over-long one is refused before it is sent, and a batch over 200 is refused rather
than truncated. **This is guidance, not a sandbox.** An agent with a shell and the
token can bypass every one of these. What actually bounds the damage is the token's
role, server-side. The tools exist so the correct path is also the easy one.

`phrase_patch` and `phrase_batch_patch` take a **`note`** — the `_note` of the API, one per
phrase. Until 2026-08-11 they did not, which meant the rule three sections below ("send `_note`
on every write that overwrites something") could not be honoured through the only surface an
agent normally has. The key and its length bound are read from `writable.note` in the schema
rather than hardcoded, and an over-long note is **trimmed and reported** rather than refused,
matching the server — losing the tail of a justification is a smaller harm than refusing the
translation it justifies.

**Removal is deliberately not exposed.** `_retract` is parsed from the schema so the client can
tell a site that has retraction from one that does not, and is never sent: these tools exist to
fill gaps and correct specific translations, and a retraction should come from a session that
means it. Translations stay a `map[string]string` all the way to the wire, so a JSON `null` is
impossible to emit rather than merely checked for — there is no guard to forget.

### Rules that are not negotiable

- **A phrase id means nothing outside the environment you read it from.** The capsule and
  production share a database lineage, so **most** ids agree — which is what makes this
  dangerous rather than obvious. Compared on 2026-08-10: 1,795 phrases on production
  against 1,816 in the capsule, **68 ids different**, and six of those were live
  production ids holding a *different phrase*. Reusing capsule ids would have written the
  Italian for `Is draft?` onto production's `API Tokens`, silently and permanently.
  **Resolve ids against the target site, every run, by matching the source string** —
  which is the same everywhere, because the phrase *is* its source string.
  `tools/apply_translations.py` does this and refuses to do anything else.
- **Fill gaps; do not overwrite.** Only write a language whose value is currently empty,
  unless correcting a specific translation is the task you were given. The tool enforces
  this by reading the target first and excluding rows that already have Italian —
  production had 18 and all 18 survived the pass untouched.
- **`phrase` is read-only.** It is a key, not content. Editing it orphans the row: the
  next page render looks up the original string, misses, and inserts a fresh row with
  the translations missing all over again.
- **The writable set is the languages. Nothing else.**
- **Removal is `_retract`. A `null` is a 422, and an empty string still means "leave this
  language alone".** Four cases, and the difference is the whole reason it is spelled out:

  | you send | what happens |
  |---|---|
  | the language is absent | left alone |
  | `""` | left alone — the untouched-textarea case |
  | `null` | **422**, naming `_retract` as the way to do it |
  | any other string, including `"0"` | written |

  ```jsonc
  {"_retract": ["de", "pt"], "_note": "Both were machine-translated from the Spanish."}
  ```

  **This changed on 2026-08-11 and it is the one breaking change in that batch.** A bare
  `null` used to *be* the retraction. It was adopted as a 422 at this repository's own
  suggestion, and the argument is worth keeping because it generalizes: a `null` is what a
  serializer emits for an absent optional field, what a dict comprehension over the language
  list produces when one lookup misses, and what `json.dumps` does with a Python `None`. None
  of those look like a deletion at the call site and all of them were one. A destructive
  operation reachable by a default value has no confirmation step in it.

  Three rules around `_retract`, all `422` rather than a guess — **verified against production
  on 2026-08-11**, every case: the value is a **list** of language codes (a bare string is
  refused); an unknown language or a locale like `de_DE` is refused as it is in the body; and a
  language cannot be **written and retracted in the same request**. `""` does not count as
  writing, so `{"de": "", "_retract": ["de"]}` is accepted — a client that sends every language
  every time need not special-case it. Retracting an empty language is a `200` with
  `changed: []`.

  It is published as `writable.retract`, so it is discoverable the documented way. The schema's
  old claim that removal was impossible is **gone** — that contradiction is fixed, and this
  file said otherwise until 2026-08-11.

  **Still never let a `None`/`null` reach a PATCH body.** The server now refuses it, but it
  refuses the whole batch. `internal/schoenstatt` keeps translations as `map[string]string` all
  the way to the wire so a null is impossible to emit rather than merely checked for, and
  `tools/apply_translations.py` refuses both a null and a `_retract` before sending.
- **Retired phrases are never in the collection, and there is no parameter to ask for
  them.** `jtranslate:retire` takes a string off the worklist without destroying it —
  the row and its translations stay, and the site keeps rendering them. `GET
  /api/v3/phrases/{id}` still answers for one, so an old link does not 404. A phrase
  appearing in your results that you have not seen before is normal: if a retired
  phrase turns out to still be rendered, the site un-retires it on the next page load.

  **A phrase can also now vanish because it was superseded.** Editing an association
  description retires the phrase the old text was, automatically and reversibly, with a
  history note naming the association. So a row leaving your queue is not necessarily a row
  you finished — `GET /api/v3/phrases/{id}/history` will say which happened.
- **A translation write is recoverable from 2026-08-11, and not before.**
  `trans_translations_history` is append-only with no foreign key in either direction, so
  neither a retraction nor a phrase deletion erases it, and
  `GET /api/v3/phrases/{phraseId}/history` serves it — linked from `meta.history` on the
  phrase document, `?language=` to narrow, `operation` one of `update` / `retract` /
  `retire`. One entry per *event*: filling an empty language writes nothing, so an empty
  history means "nothing was lost here", not "nothing is recorded".

  **The table does not backfill.** Everything written before the deploy — the 1,041 rows of
  2026-08-10 and the 22 corrections — is still gone beyond recovery. Recoverability starts at
  the deploy, so the older passes keep the weight they were given.

  Verified in the capsule on 2026-08-11 by round-tripping phrase 10028: `_note` was accepted
  and appears on the history row, `previous` gave back the exact text to restore, the restore
  succeeded, and the row ended byte-identical to where it started. Two details the reply does
  not mention. `replacedBy` is the acting account and is what attributes the write; `writtenBy`
  is the author of the *destroyed* version and is **null for anything written before the table
  existed**, so for older rows the previous author still comes from `/admin/translations`. And
  a phrase can carry a lot of history — 10028 had 88 entries, 73 of them German — so read
  `?language=` and the first entry rather than the whole thread.

  This was the single most important fact in this document, and it is worth understanding
  what its replacement does *not* say. A recoverable write is not a free one: reverting needs
  somebody to notice, and a plausible mistranslation is exactly what nobody notices. A
  filtered read and a considered batch still beat a broad speculative rewrite.
- **Send `_note` on every write that overwrites something.** A reserved PATCH key, ≤255
  characters, trimmed rather than refused if longer, a 422 if not a string; batch entries take
  it too. It attaches to the history rows the write produces — one per translation destroyed,
  **none if the write only fills gaps**, so it is never noise. The maintainers asked for this
  specifically and the reason is good: read in order the notes are a conversation, so the next
  agent learns that the obvious rendering was already tried and abandoned instead of trying it
  again. Humans read them too, on the phrase edit screen. Write them for people.

  It is published as `writable.note` as of schoenstatt.link#61, so it *is* discoverable the
  documented way — this file said it was not until 2026-08-11. Read the key and its length
  bound from the schema rather than hardcoding either. `phrase_patch` and `phrase_batch_patch`
  take it as `note`.
- 2000 characters per translation, matching the column.
- Nothing validates meaning. The rules are thin on purpose — optional, trimmed,
  length-bounded — and no validator was ever going to catch a plausible
  mistranslation. What catches it is that the write is attributable.
- A response carrying a `warning` that the compiled catalogs could not be written is
  **not a failure to retry**. The row is committed; retrying writes nothing. It means
  somebody has to fix the filesystem.

### Autonomy

**Write directly, audit after.** You may PATCH translations without prior approval.
Writes carry the bot's user id in `trans_translations.modified_by` and appear at
`/admin/translations` beside human ones.

That freedom was bounded by the irreversibility above, which no longer holds.

**The maintainer settled this on 2026-08-11:** *"I'm fine with you improving previous translations
now that we have history if you're reasonably certain."* So correcting an existing translation
no longer needs to have been the assigned task. The bound moved from *permission* to
*certainty*, and the standard is his phrase — **reasonably certain** — not "defensible" and
not "probably better".

What that means in practice, because a loosened rule needs a sharper edge than a strict one:

- **Correct what is demonstrably wrong.** A misspelling attested against the movement's own
  books, a lost placeholder, mismatched Spanish question marks, a word from another language
  sitting in the row, an invented gloss the source does not contain. `hunt_lexical.py` exists
  to find exactly this class and to carry the evidence with it.
- **Do not "improve" what is merely not your preference.** A defensible synonym, a regional
  variant, a register choice, a concise rendering — leave them. `Santuário Missioneiro` looks
  like a misspelling and is the regional adjective for the Guarani missions.
- **A house decision is not a correction.** `Schönstatt` vs `Schoenstatt`, `du` vs `Sie`,
  `Edition` vs `Auflage`: these are consistency policies affecting hundreds of rows, and
  "reasonably certain" is not available to an agent about them. Ask.
- **A doctrinal or charism naming question is not a correction either**, even with an
  attestation. Where the movement's own sources and the maintainers disagree — as they do
  about `Ladies of Schoenstatt` — the disagreement is the finding. Report it; do not resolve
  it by picking the source you read most recently.
- **Send `_note` on every one**, saying what was wrong and what the evidence was. That is the
  maintainers' one condition and it is what makes the write reviewable afterwards.
- **Still work in reviewable units** — one language, one batch, one kind of defect — and say
  plainly in the session what was written and where. `apply_corrections.py` asserts the
  current value before replacing it, so a stale list fails loudly instead of clobbering
  somebody's later edit.

The reason to stay careful anyway, now that the rule permits more: recoverability protects
against the mistake somebody notices, and a plausible mistranslation into a language nobody in
the session reads is precisely the mistake nobody notices. History turned "unrecoverable" into
"recoverable by a reviewer who exists" — so the review queues still matter, and a finding held
back for a native speaker is not a failure to act.

### Retiring a phrase that should not exist

**The maintainer directed this on 2026-08-11:** retire any phrase you judge was added by mistake,
with a note saying why. The reasoning is that retirement is reversible and self-healing — if the
phrase really is still rendered, the next render that misses clears `retired_on` and it comes
back — and the note is then already in the database explaining what was believed and why, which
is the evidence needed to find the bug at that point. **The accepted cost is one request's
translation miss**, and the goal is to bring the phrase counts to zero in the short term.

So the standard here is deliberately lower than for correcting a translation: a retirement is
recoverable *by the application itself*, without anyone noticing, which is the guarantee a
mistranslation does not have.

**It is on the API as of 2026-08-11**, requested as
[`docs/api-change-requests.md`](docs/api-change-requests.md) §14 and shipped the same day with
every ask granted:

```
POST /api/v3/phrases/{id}/retire     {"_note": "why"}     # _note REQUIRED — 422 without
POST /api/v3/phrases/{id}/unretire   {"_note": "why"}
GET  /api/v3/phrases?onlyRetired=1                        # audit your own retirements
GET  /api/v3/phrases?includeRetired=1
```

Use `phrase_retire` and `phrase_unretire`; the whole contract is published under `retirement`
in the phrase schema. Four properties worth holding on to:

- **`_note` is required here**, unlike on a write, and the asymmetry is right: a write's note
  explains a replacement the history records anyway, while a retirement's note is the *entire*
  record of the judgement. Verified — no note, empty note, or non-string note is a 422.
- **It is idempotent — per *row*.** Retiring an already-retired phrase is a `200` with
  `changed: false` and **no second history entry**, so a retry cannot forge a second judgement.
  "One event per state change" is true of a row and reads as though it were true of a string,
  which is the next bullet.
- **One string in two text domains is two rows, and retiring one does not retire the other.**
  `UNIQUE (project, text_domain, phrase_hash)` makes them two rows sharing one hash, which is
  exactly what the breadcrumb's two-domain lookup produces — a pair at a time, so most of what
  you retire arrives in pairs. **Clear every row of a string or it keeps asking for work through
  the domain you left**, and your count does not move by what you expected. Verified on
  production 2026-08-11 on the pair 12995/12996.

  **The thread is shared**, because it is keyed on the hash rather than the id — that is what
  lets it survive a merge or a delete-and-rediscover. So a history read on *either* id returns
  **both** retirements, and two entries with two notes is the correct answer for a string that
  existed twice, not a double-record. Each entry names its own `phraseId` and `textDomain`;
  filter on those to narrow a thread to one row. Published as `retirement.siblings`.

  Two consequences for practice. Write the note **per row, saying which domain and why** — both
  land in one thread, so two copies of one sentence read worse than one that distinguishes them.
  And use `tools/apply_retirements.py`, which fails a batch that would leave a sibling live;
  `--allow-partial-siblings` is for when the sibling is a genuinely different row that happens to
  share a string, which does happen — `Update on advances` is dead welcome-page copy in
  `Application` and live change-log text in `SionModel`.
- **Self-healing writes no history.** A phrase the site still renders un-retires itself on the
  next missed lookup. So **a row that is live again carrying a `retire` with no `unretire` after
  it is the signal that the retirement was wrong** — and its note says what was believed. Do not
  call `phrase_unretire` to tidy a note or redo a retirement: that replaces a true signal with a
  false account of a judgement.
- **`?onlyRetired=1` is how the loop closes.** Without it a retired row is invisible except by
  id, so nothing would notice one that came back.

**Do not reach for `_retract` instead.** It removes a *translation*, not a phrase. Retracting
all five languages would destroy good translations **and leave the phrase on the worklist**,
pushing the untranslated count up — the opposite of the intent, and close enough in name that
the schema now warns about it under `writable.retract.notRetirement`.

**Retirement is not deletion either**, and the difference matters for the four
`skip-leaked-secret` rows: those require that the string *cease to exist*, which no API surface
does. That stays a task for a human with database access.

`classify.py` buckets candidates under a `retire-` prefix and writes them to
`retire_candidates.json` — and, like `skip-`, excludes them from the worklist. See
[`docs/retire-queue.md`](docs/retire-queue.md) for the standing list and, more usefully, for the
rows that look retirable and are not.

Two things about that file changed on 2026-08-11 and both were corrections of it, not additions:

- **A candidate now carries a bounded `note` separately from its `reason`.** This file used to
  say the reason was "already phrased to serve as the `_note`". That stopped being true as the
  reasons grew — 275 to 452 characters against a 255 limit — and it is how the very first
  retirement note was truncated mid-word, losing the clause that said what to do if the phrase
  came back. `NOTE_MAX` is asserted at import now.
- **The test for `retire-` is "does anything still look this string up", not "can it be
  translated".** This was learned by getting it wrong on 2026-08-11. Five `skip-` buckets were
  moved to `retire-` on the argument that a call-number format is rendered, legitimate, and
  untranslatable in every language — so leaving it alone means a count can never reach zero.
  Right about the rows, wrong about the mechanism: **retirement self-heals on lookup**, so a
  rendered row comes straight back. Two did, within five minutes, on the two routes that happened
  to be rendered. Three of the five buckets are `skip-` again; the two where *nothing* renders the
  string — the dead welcome page, and the site's own retranslated output — held, all fifteen rows.

  A rendered-but-untranslatable row therefore cannot be taken off the worklist from this side at
  all, and the fix belongs at the caller. Filed as
  [`docs/api-change-requests.md`](docs/api-change-requests.md) §16. `is_writable()` carries the
  argument and names the two buckets that stay `skip-` for unrelated reasons.

## Phase 2 — the Schoenstatt Shrines

**Not started. Do not begin without being asked.** Recorded here so the shape of the
repository anticipates it.

The goal is to make it easier for people to find and visit the shrines: accurate
locations, opening hours, contact points, the wayside shrines as well as the shrines.
The endpoint already exists — `/api/v3/associations`, role `sch_api_bot`,
`?kind=sch-shrine` or `?kind=sch-wayside-shrine`.

Two things to know now. A patch is merged onto the stored record and the **whole**
record re-validated by the moderator form's own `InputFilter`, so an agent is refused
exactly what a moderator is refused. And **there is no create and no delete** — what
a shrine is, what it belongs to and who is responsible for it are human decisions.
Association writes *are* recorded in `sch_changes` and are revertible, which makes
this phase materially safer than translations.

Verification standard for this phase, since it is the thing people will act on:
prefer a primary source (the shrine's own or its region's official page) and record
where a fact came from in `data/shrines/notes/`. Don't launder a guess into the
database by writing it down confidently.

## Credentials

**Credentials live at `~/.config/schoenstatt/credentials.env`** — outside this
repository, mode `600`, in a directory that is mode `700`. Nothing in this repo
reads a token from a tracked file, and no tool in this repo should ever accept a
token as a command-line argument (arguments are visible in `ps` and land in shell
history).

```
SCHOENSTATT_BASE_URL            production          SCHOENSTATT_BASE_URL_TEST
SCHOENSTATT_TRANSLATOR_JWT      production          SCHOENSTATT_TRANSLATOR_JWT_TEST
SCHOENSTATT_BOT_JWT             production          SCHOENSTATT_BOT_JWT_TEST
```

**Two environments, one variable apart — so test is the default and production is
opt-in.** `SCHOENSTATT_ENV` selects: unset or `test` reads the `_TEST` pair (the
capsule), and only the literal `production` reads the unsuffixed pair. Nothing
picks an environment by "whichever variable happens to be set", because the
difference between the two is a disposable capsule and the live site, and a
translation written to the wrong one cannot be taken back. The MCP server logs
which environment it resolved at startup.

Load the file with `set -a; . ~/.config/schoenstatt/credentials.env; set +a`, or read
it directly from a program. The repo keeps no copy, not even an example with a fake
value in the right shape — `.env.dist` is unignored for non-secret settings only.

An API credential is a normal account holding **one** extra role, plus a JWT.

- **Issuing one.** The admin screen at `/en/users/:id/api-tokens` is the intended
  path and needs an administrator session. Without one, the capsule route is: register
  the bot account at `/en/user/register` (the form takes an email address and nothing
  else, needs an `EU_COOKIE_LAW_CONSENT=true` cookie, and the address must have a real
  TLD — `example.com` is what the site's own smoke tests use), read the code out of
  Mailpit at `http://localhost:8025`, and exchange it at
  `POST /en/api/v1/users/login-with-verification-token` with `identity` and `token`.
  That endpoint both signs and registers, which is why it yields a usable token and a
  hand-rolled JWT would not. Then grant the single role. Registration grants the
  default roles including `sch_user`, which opens the moderator edit form for every
  association — **replace the account's roles rather than adding to them**, and verify
  the account holds exactly the one role before using the token.

  Two shapes of code arrive by email and both redeem at the same endpoint:
  registration sends a long link carrying `token=<64 hex>`, while
  `POST /en/api/v1/users/request-verification-token` sends a six-character code in the
  body of the message. The second is the one to use when the account already exists.
- **The capsule's database gets rebuilt, and that silently destroys the credential.**
  The account and every row of `user_api_token` go with it, and because the API fails
  closed on an unregistered `jti`, the surviving token in `credentials.env` then 401s
  exactly like an expired or malformed one. That is not a bug to debug; it is the
  fourth item on the 401 checklist below. Re-mint and move on.
- **Never let a token reach a terminal transcript.** Write it straight into
  `credentials.env` from the program that fetched it rather than printing it and
  copying. If one does get printed, revoke that `jti` and issue another — a capsule
  token is cheap and a habit of tolerating exposed ones is not.
- The JWT is shown **once** and is not recoverable — only its identifier (`jti`) is
  stored. Put it in the credentials file immediately or it is lost.
- Six-month lifetime by default. Every issued token is registered, and the API
  refuses any token it has no record of. Fail closed.
- **Revocation is per token, not per account**, takes effect on the token's next
  request, and happens on the same screen. If a token is exposed — a commit, a log, a
  pasted terminal transcript — revoke it and say so. Revoking one agent credential
  does not cut off the others.
- Send it as `Authorization: Bearer <jwt>`.
- Every refusal is a `401` with one uninformative message, deliberately. Missing,
  malformed, expired, revoked, unregistered, unknown user and wrong role are
  indistinguishable — so don't try to diagnose a 401 by its body. Check, in order:
  is the capsule up, is the token in the environment, **does the account still exist
  and does `user_api_token` still hold this token's `jti`** (a rebuilt capsule
  database is the usual answer, and the commonest cause of all), does the account hold
  the role the message names, has `db6.8.sql` been applied.

## Working conventions

- **Don't guess.** Ask a concise question rather than assume. Clarify options, take
  the answer, then proceed — and afterwards say what remains uncovered.
- Plan a change with the user before making it; small direct edits may skip this.
- Don't estimate work in hours. Find the right solution.
- **Don't trust docs over code**, including this one. When you find this file wrong,
  fix it as part of the work rather than working around it.
- Prefer reading `../schoenstatt.link/docs/api-v3.md` to re-deriving the
  contract from its source, and prefer reading its source to assuming.

### Git

- You may stage, commit and push to feature branches, and open or update PRs.
- Never merge, never push to the main branch, never force-push, never delete branches
  or tags. If asked, give the user the commands to run instead.
- Do not add a `Co-Authored-By` trailer to commits.
