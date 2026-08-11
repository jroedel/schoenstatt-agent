---
name: schoenstatt-translation
description: Translate or correct schoenstatt.link's UI phrases in one language. Use when filling a language gap (it/pt/es/de/en), auditing existing translations for errors, or writing to the phrase API at all. Encodes the irreversibility rules, the phrase-id trap, and the classify/draft/apply pipeline.
---

# Translating schoenstatt.link

The method that produced 1,401 Italian, 1,156 Portuguese, 1,421 German and 1,438 Spanish
translations on production.
Read this before writing anything; the rules in it were each learned by nearly getting
something wrong.

## The fact that shaped everything, and what replaced it

**Until 2026-08-11 a translation write could not be undone.** `trans_translations` had no
history at all, so the previous text was simply gone. Everything in this skill follows from
that: dry runs by default, gaps filled but text never overwritten, uncertainty recorded
rather than resolved by guessing, and a reviewable document produced *before* production
rather than after.

**That changed.** `trans_translations_history` is append-only and
`GET /api/v3/phrases/{phraseId}/history` serves it, with `operation` one of `update` /
`retract` / `retire` and a `previous` holding the destroyed text. A PATCH may carry a
reserved `_note` (≤255 chars) which attaches to the rows that write destroys — none if it
only fills gaps. **Send it on every overwrite**; the maintainers asked for it, and read in
order the notes are a conversation rather than a log.

Three things keep the caution anyway, and they are not sentiment:

- **The table does not backfill.** Nothing written before the deploy is recoverable, which
  includes the 1,041 rows and 22 corrections of 2026-08-10.
- **Recovery needs a reviewer who exists.** History protects against the mistake somebody
  notices, and a plausible mistranslation into a language nobody in the session reads is
  exactly the mistake nobody notices. The review queue is that reviewer.
- **Deletion is `_retract`, and a `null` is a 422.** `{"_retract": ["de"]}` removes a
  translation; `{"de": null}` is refused and names that alternative; `{"de": ""}` leaves it
  alone. This changed on 2026-08-11 — a bare `null` *used* to be the retraction, which made a
  serializer's default, a missed dict lookup or a Python `None` a deletion at a call site that
  did not look like one. Build PATCH bodies from non-empty strings only anyway: the server now
  refuses a null, but it refuses the whole batch. A language cannot be written and retracted in
  the same request, and `""` does not count as writing. See `docs/api-change-requests.md` §11.

So: gaps still get filled and text still does not get overwritten unless that is the task.
What has changed is that a mistake found later is now fixable, not that a mistake is now
cheap.

## Two traps that will cost you if you skip them

### 1. A phrase id means nothing outside the environment you read it from

The capsule and production share a database lineage, so **most** ids agree — which is
exactly what makes this dangerous rather than obvious. Measured 2026-08-10: 1,795 phrases
on production against 1,816 in the capsule, **68 ids different**, six of them live
production ids holding a *different phrase*. Reusing capsule ids would have written the
Italian for `Is draft?` onto production's `API Tokens`.

**Resolve ids against the target site on every run, by matching the source string.** The
phrase *is* its source string, and that is the same everywhere.
`tools/apply_translations.py` does this and will not accept an id map from anywhere else.

### 2. Skip decisions are per (text_domain, source string), not per string

`Update on advances` is dead welcome-page copy in the `Application` domain and live text in
`SionModel`. Match on the string alone and you resurrect every skip decision. The
exclusion list (`skip_pairs.json`) is keyed on the pair for that reason, and it carries
between environments where ids do not.

## Roughly a quarter of any language "gap" is not translatable work

Before translating, classify. Of Italian's 1,745-phrase gap, **397 were not work at all**:
bibliographic citations from the Kentenich corpus, markdown filenames, printf templates,
association record content, error strings the application built by concatenation, dead
copy from a retired page, and — in four rows — **a JWT the api-tokens screen appended to
its success message before translating.**

`tools/classify.py` holds the buckets with the reason beside each rule. Run it first. If you
find a new kind of noise, add a bucket rather than skipping by hand, and write down why in
`docs/*-skipped.md`.

**Two prefixes mean "not work", and the difference matters.** A `skip-` row exists
legitimately, or for a reason nobody here can fix, and translating it would be wrong. A
`retire-` row **should not exist at all** — a defect at the caller filed it — and should come
off the worklist with a note saying why. `is_writable()` excludes both.

Retire one with `phrase_retire { phrase_id, note }`. The `note` is **required** and is the
entire record of the judgement, so say what the row is and what it means if it comes back. A
retirement destroys nothing and self-heals, so the bar is lower than for correcting a
translation — but a row that is merely *untranslated* is work, not a mistake. Never reach for
`_retract` instead: it removes a *translation* and leaves the phrase on the worklist with one
more gap than before. Log what you retired in
[`docs/retire-queue.md`](../../../docs/retire-queue.md), and audit with
`phrase_search { only_retired: true }`.

**Do not classify a title-shaped row by its translation state.** Discovery copies translations
onto a newly discovered phrase from any same-text row in another text domain, so a record name
that collides with an already-translated string arrives pre-translated in four languages. Read
`originRoute` and `textDomain` first. See `is_title_artefact()` for the three conditions and
the shrine names they deliberately spare.

## Start by mining the language's own existing rows

Before translating anything, read every row the target language **already has** for the
screens you are working on. This was not in the first draft of this skill; the drafting
agents did it unprompted and it settled more than the glossary did — `Association` →
`Gruppierung` in German messages, `Entity` → `Objekt`, `Cenáculo` → the Latin `Coenaculum`,
`call number` → `número localizador`.

Two things follow from it:

- **House convention lives in the existing rows**, not only in the glossary. The glossary
  records decisions somebody wrote down; the rows record every decision anybody ever made.
- **Where a source string already has a translation in a different text domain, reuse it
  verbatim** rather than writing a better one. The two rows render in the same places and
  must not drift. Improving one of a pair is worse than leaving both mediocre.

`build_worklist.py` now does this for you, sliced per beat — see below.

## Work a family of routes at a time, not a count of strings

The unit of work is a **beat**: one family of related routes, whole, with the translations
that language already has for those same routes. Not a fixed number of strings. Two
different reasons, and the second is the one that matters.

**The cheap reason.** What a drafting pass spends is mostly not the strings. Per agent:
SKILL.md 10k + glossary 15k + style 5k + the existing-rows dump ≈ 23k tokens *before
translating anything*, against ~24k tokens for the entire 374-unit Portuguese payload. Cut
into four fixed chunks, that is ~92k tokens of preamble to carry ~24k of work — the
duplicated preamble was **four times the job**. Every agent you remove removes a whole
preamble.

**The real reason.** 301 of those 374 Portuguese units are one family —
publications/libraries/books — and inside it 82 English words recur across three or more
units: `call number`, `checkout`, `edition`, `label`, `import`. **Those are decisions, not
strings.** One agent owning the family settles `call number` once and applies it to 300 rows
and cannot contradict itself. Two agents splitting that vocabulary down the middle each
settle it alone, and may disagree — and a term rendered two ways across a screen is a defect
a reader sees.

So: settle the beat's recurrent terms *first*, write them down, then fill. The beat file
lists them at the top in recurrence order for exactly this.

Because the vocabularies barely overlap — only 25 of 91 recurrent library terms appear
anywhere in the account routes — each beat can be handed **its own slice** of the existing
rows rather than the whole table. That slice is where the token saving actually lands.

**The gain is not uniform; do not spread it evenly.** In the same measurement the leftover 25
units had *zero* terms recurring three times. Genuine miscellany, nothing to amortise. A
family whose terms do not recur is not a family — it is a pile that shares a URL prefix, and
giving it its own agent buys a second preamble and nothing else. It gets one leftover pile.

The one failure this arrangement can create is two beats settling a shared term differently,
so it is checked directly: every drafter declares its terms, and `conform.py` reports any the
beats disagree on.

## Give an agent the judgement and a script everything else

Two of the phases in the first version of these workflows were agents doing work that is
decidable, and they were worse at it than twenty lines of Python — slower, dearer, and able
to die halfway.

- **Conformance was a subagent asked to write a script.** It is `tools/conform.py` now.
  Placeholder integrity, retyped keys, collisions, length caps, sibling bleed and
  identical-to-source are properties of two strings. On the German drafts it reduced 109 raw
  hits to **one** finding worth a human glance — and that one was real: `Branch moderator`
  rendered as `Geistlicher Begleiter (Schwester, Priester, Pater)`, a gloss the source does
  not contain.
- **Four of six revision lenses were mechanical.** They are `tools/hunt_lexical.py`, which
  checks each word against the movement's own books: a word absent from 231k words of edited
  Spanish whose accent variant occurs 74 times is a misspelling, and that is evidence rather
  than an opinion. Run against Spanish it rediscovered every correction the six-agent pass
  had applied, plus `contínuamente`, `perpétua`, `calido`, `Linea` and `ADORACION` that the
  agents missed.

What no script can do is read a rendered page, know what the movement calls a thing, or weigh
a register. That is what the remaining agents are for.

**Grade findings, do not just count them.** Both scripts would be useless if they reported
everything they matched: proper names and cognates set off every naive check. `identical to
its source` is expected for `Oasis de Misericordia`; a Spanish value equal to the Portuguese
one is expected because they are cognate languages, whereas German text in a Portuguese row is
the real `Literature` → `Literatur` defect. Bleed is matching **one** sibling; matching
several is house convention. A report where 108 of 109 findings are correct-as-they-stand is a
report nobody reads twice.

## Where the right answer comes from, in order of authority

1. **The movement's own publications in that language.** `../reading-material`
   holds Schoenstatt titles in pt, es, de and en. Mine them with
   `tools/extract_reading_material.py`. This is what settled `edicola` for the Italian
   wayside shrine and `União` (not `Federação`) for the Portuguese federations — neither
   of which could have been reasoned out from the other languages.
2. **The movement's own web pages in that language** — `schoenstatt.org/it`,
   `schoenstatt.com/it` and their siblings, plus each community's own site.
3. **The site's other four languages.** These settle **house convention** — whether a term
   is translated at all, whether a heading is pluralized, what shape a name takes. They do
   **not** settle what the word is in your language. Where two siblings disagree with each
   other, that disagreement is the signal that a decision is needed: flag it.
4. **The element the string sits in.** `Search` in a `<button>` wants an imperative; as a
   column header it wants a noun. `tools/screens.py` records the enclosing tag for exactly
   this, and it decided several dozen short labels.

**The books are copyrighted.** Extract to scratch, commit only short attestations — a
term, a count, a clause of context. Never their text.

## Do not translate the sibling language

Every error found in Portuguese's existing 719 rows came from copying a sibling and only
half-converting it: `Santuário de la Comunidad del Camino` (Spanish but for the first
word), `Persona criado com êxito`, `Estes datos`, and `Literature` → **`Literatur`**, the
German row sitting in the Portuguese column in the main navigation of every page.

Translate from the **key**. Read the siblings for convention, then look away and write.

## The source string is not guaranteed to be English

164 of Italian's phrases had a non-English source. Compare the key with its own `en` row:
identical means the key is English and current; different means either the key is not
English or it is stale English the site has moved past. Read both before deciding which.
Never edit the key — it is the lookup string.

## The pipeline

```
tools/extract_reading_material.py   mine the bibliography for terminology  (per language)
tools/screens.py                    which phrase is visible where, in what element
tools/classify.py                   sort the gap into translate / skip, with reasons
tools/build_worklist.py             the gap, grouped into beats, with per-beat prelude
  → data/glossary/<lang>.yaml       one entry per decision, with its evidence
  → data/style/<lang>.md            register, variant, what stays in English
tools/conform.py                    check drafts mechanically       (exit 1 if blocking)
tools/hunt_lexical.py               find defects in existing rows against the books
tools/apply_translations.py         fill empty rows in batches      (dry run by default)
tools/apply_corrections.py          overwrite existing rows        (dry run by default)
tools/build_review_queue.py         the flagged calls, for a native speaker
```

Two workflows automate the fan-out and are the normal entry point:

- **`translate-bulk`** — one drafting agent per beat, then one agent to reconcile the terms
  two beats settled differently. Typically **4–6 agents** for a whole language.
- **`translate-revise`** — two judgement lenses, then batched adversarial verification.
  **2 + 2×⌈findings/25⌉ agents**; run `hunt_lexical.py` first, it is a prerequisite.

Filling a 374-string gap and auditing a language are each a handful of agents. If a run of
either is heading for dozens, something is being done by an agent that should be done by a
script.

**Both produce proposals. Neither writes.** All writes go through the main loop, after a
dry run somebody has read. That is deliberate: a subagent cannot be given an
irreversible, unreviewed write. This held across 540 agents in one session without a single
subagent touching production.

**Bound any fan-out whose size depends on an upstream count**, in the same breath as writing
the fan-out. Verification at three skeptics per finding once spawned 364 agents and exhausted
an organisation's monthly spend limit, killing three unrelated runs. Two fixes, and the second
is the general one:

- Cap it, and log what the cap dropped — a silent cap reads as "we checked everything".
- **Batch the item, fan out the phase.** A skeptic's expensive context is the glossary, the
  style guide and the corpus, and those are identical for every finding in the language.
  Loading them once and judging twenty-five findings costs a fraction of loading them
  twenty-five times. Independence survives batching: the skeptics never see each other and
  each renders a per-item verdict with its own evidence.

**Two skeptics, and both must decline to refute.** Fewer agents and a *stricter* filter at
once — majority-of-three passes a finding on 2-1, unanimity-of-two does not. Refusing a real
fix costs a re-run; accepting a wrong one costs the text. Those are not symmetric, so the tie
does not go to the proposal. Verification is not optional cost: adversarial checking refuted
**95 of 119** English candidates, and proposing those to the site's pivot language would have
been actively harmful.

**Two durability rules, learned by losing work.** A `translate-revise` run of 79 agents lost
every verified finding because one final agent was the only thing that wrote to disk, and it
died. Meanwhile a `translate-bulk` run lost three of four chunks and the fourth was still on
disk and still usable.

- **The phase that produces data writes it down.** Do not let output exist only in return
  values — the run journal truncates them, so a dead downstream phase takes everything with it.
  Note what this rules out: a dedicated checkpoint agent is not the fix, because it is still a
  single point of failure, just an earlier one. Each producing agent writes its own file.
- **Every agent result carries its own identity.** A verdict without the id of what it
  judged cannot be matched back to its subject, and is worthless the moment synthesis fails.
- And **fail closed** when you reassemble: a finding with a missing verdict is unverified, not
  approved. An agent that died must not thereby promote a correction to a production write.

See [`docs/workflow-review.md`](../../../docs/workflow-review.md).

## Filling a gap and correcting a row are different acts

- **Filling** an empty row is covered by the standing permission to write. Use
  `apply_translations.py`, which refuses to touch a row that already has text.
- **Correcting** existing text is not. It needs the user to ask for it. Use
  `apply_corrections.py`, which states the value it expects to find and refuses if the row
  has moved — so a stale list fails loudly instead of clobbering somebody's later edit.
  Re-running it after the fact is how you verify: every row should say *already correct*.

Send `If-Match` on single writes. The batch endpoint does not honour it, by design — a
conditional request is defined over one resource.

## Flag rather than guess

When a term is doctrinal, charism-specific, or you cannot tell the register, record it in
the review queue with **what you wrote, what the alternative was, and why you chose**.
That is worth more than a confident answer. 100 Italian entries went to a native speaker
this way; two of them (`Heiligtum der Verbundenheit`, `Heiligtum der Werktagsheiligkeit`)
are Kentenich terms of art where the Romance siblings coined words Italian cannot borrow.

If you genuinely cannot tell what language a source string is in, say so and leave it.

## Report the numbers so they reconcile

`written + skipped + already-present = the whole corpus`, or explain the difference. After
Italian: 1,349 written + 396 skipped = 1,745, and the one row of discrepancy against the
classifier was named and explained rather than smoothed over.

## Check the API contract, don't remember it

`GET /api/v3/schema/phrase` at request time for the writable languages and the length cap;
they are configuration, not constants. Read
`../schoenstatt.link/docs/api-v3.md` for the payload shapes — the batch
endpoint takes an object keyed by phrase id, the single endpoint takes a bare language map,
and a batch's outcome is per-item so you trust `summary`, not the HTTP status.
