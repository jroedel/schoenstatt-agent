# The retire queue

Phrases this repository judges were **added by mistake** — rows that should not exist, because a
defect at the caller filed them — together with the reason each one should come off the
translator's worklist.

**The endpoint shipped on 2026-08-11 and the standing candidates have been retired.** This file
is now a log of what left the worklist and why, and — more usefully — of what looks retirable and
is not.

**66 rows were retired on 2026-08-11 and 64 of them are still retired.** Two of the 66 were the
first use of the endpoint; 64 followed in this pass, alongside 173 translations, and the count
reached 0 in all five languages before new rows arrived.

**Two of those retirements were wrong, the site said so, and that is the most useful thing in
this file.** See [26 rows retired 12:47 UTC](#26-rows-retired-2026-08-11-1247-utc--15-held-11-should-not-have-been):
retirement cannot hold a row the application still renders, however untranslatable that row is.
Nine more are expected back for the same reason. [`close-2026-08-11.md`](close-2026-08-11.md)
records the whole pass.

**The one-line version, if you retire nothing else this session:** ask *does anything still look
this string up*, not *can this string be translated*. Only the first question predicts whether a
retirement holds.

## The direction this serves

The maintainer, 2026-08-11: retire any phrase we judge was added by mistake, adding a note as to why.
The note is recorded in the database, so if the phrase comes back from retirement the note
documents what was believed and the underlying bug can be addressed at that moment. The accepted
cost is a translation miss for a single request. The goal is to bring the phrase counts down to
zero in the short term.

Two properties make that a good trade, and they are worth stating because they are *not* the
properties an overwrite has:

- **A retirement destroys nothing.** `retired_on` is a statement about the translator's
  worklist. The row stays, its translations stay, and the site keeps rendering them.
- **It self-heals.** A phrase the application still looks up un-retires itself on the next miss.
  So a wrong retirement is corrected by the site, without anybody noticing — where a wrong
  translation is corrected only by a reviewer who happens to read that language.

That is why the standard here is deliberately lower than the "reasonably certain" bar that
governs correcting an existing translation. The failure mode is a phrase reappearing with an
explanation attached, which is a useful event rather than a harmful one.

**It is not a licence to retire the backlog.** A row that is merely *untranslated* is work, not a
mistake. The candidates below are rows whose existence is a defect — and the test for that is
mechanical and written down in `tools/classify.py`, not a judgement made per row in a session.

## How to retire one

```
phrase_retire    { phrase_id, note }      # note REQUIRED — 422 without one
phrase_unretire  { phrase_id, note }      # read the warning below first
phrase_search    { only_retired: true }   # audit what you retired
```

Requested as [`api-change-requests.md`](api-change-requests.md) §14 and shipped the same day
with all three asks granted, including the `?onlyRetired=1` filter — without which a retired row
is invisible except by id, so nothing would notice one that came back. The full contract is
published under `retirement` in `GET /api/v3/schema/phrase`; read it there rather than here.

Four properties, all verified against production:

| | |
|---|---|
| `_note` required | no note, `""`, or a non-string is a **422**. Unlike on a write. |
| idempotent | retiring an already-retired row is `200`, `changed: false`, **no second history entry** |
| self-healing | a phrase the site still renders un-retires itself on the next missed lookup, **writing no history** |
| destroys nothing | translations intact, catalogs unchanged, the site renders what it rendered before |

**Do not call `phrase_unretire` to tidy up.** Because self-healing writes no history, the
*absence* of an `unretire` entry is what carries information: a row that is live again with a
`retire` and no `unretire` after it came back **on its own**, which means the retirement was
wrong. Calling un-retire by hand writes "a human put this back", overwriting a true signal with
a false account of a judgement. Use it when the retirement itself was the mistake.

**`_retract` is not a stronger retirement.** It removes a *translation*, not a phrase. Retracting
all five languages would destroy good translations **and leave the phrase on the worklist**,
pushing the untranslated count up. `tools/apply_translations.py` refuses a `_retract` outright,
and the schema now warns about the confusion under `writable.retract.notRetirement`.

**Retirement is not deletion.** The row is not removed and cannot be through this API. A string
that must *cease to exist* — the four leaked JWTs — is a task for a human with database access.

## How the queue is produced

`tools/classify.py` buckets these under a `retire-` prefix. Two consequences, both deliberate:

- Each candidate carries **two** strings, and this used to be one. `reason` explains the
  classification to a reader of this repository; `note` is what goes to the API, is addressed to
  whoever finds the phrase back on the worklist, and is asserted at import to fit
  `writable.note.maxLength`.

  **They were the same string until 2026-08-11, and that is how the first retirement note was
  truncated mid-word.** The reasons had grown to 275–452 characters against a 255 limit — the
  breadcrumb one to about 700 — so "verbatim as the `_note`" had quietly stopped being true. The
  assertion caught four of the seven notes on its first run, one of them over by a single
  character.
- `is_writable()` treats `retire-` as not-writable, exactly like `skip-`. A row that should not be
  offered as work is the last thing that should be offered as work while it waits.
- **`retire-` covers two judgements, not one** — *this row should not exist*, and *this row exists
  legitimately and can never be translated in any language*. The second was `skip-` until
  2026-08-11. `is_writable()`'s docstring carries the argument.

```
SCHOENSTATT_ENV=production python3 tools/classify.py <scratch> --fetch
# -> <scratch>/retire_candidates.json      (bucket, reason, and the bounded note)

python3 tools/apply_retirements.py <scratch>/retirements.json --added-before 2026-08-11T08:50
python3 tools/apply_retirements.py <scratch>/retirements.json --write
```

**Retire through the tooling, not through `curl`.** That rule is why the tool exists, and the
truncated note below is what it cost to learn.

## Retired

**64 rows were retired on 2026-08-11 12:24–12:47 UTC**, in two batches, and they took every
language's untranslated count to zero. [`close-2026-08-11.md`](close-2026-08-11.md) is the full
record; the two sections below are the queue's own log.

### `retire-breadcrumb-record-name` — 38 more rows, retired 2026-08-11 12:24–12:31 UTC

Nineteen `Application`/`default` **sibling pairs** on route `association`, all shrine names:
`Bahía Blanca, Buenos Aires` · `Belo Horizonte` · `Confidentia, Buenos Aires` ·
`Frederico Westphalen` · `Freiburg-Merzhausen` · `Józefow - Syjon` · `Kreuzland-Kapellchen` ·
`Lamar, Texas` · `Madurai, Tamil Nadu` · `María Madre de los Pobres` · `Miami, Florida` ·
`Milwaukee, Wisconsin` · `Quinta Normal` · `Samborondón, Guayaquil` ·
`Santa Cruz de la Sierra` · `Santuario Ciudad de Madrid` · `Santuario de la Fidelidad` ·
`Tucumán` · `Waukesha, Wisconsin`. All filed between 00:44 and 01:39 UTC on 2026-08-11.

`db7.4.sql` statement 4 was written to retire exactly these and did not, because its last
condition is `NOT EXISTS (… a translation in a locale other than en_US)` and **this repository's
own Portuguese pass had filled `pt` on all nineteen a few hours before the migration ran.** Same
forgeable condition as §12's inherited copies; different forger. The lesson generalises: *"somebody
has translated it"* is never evidence about what a row is.

Four checks before retiring, because a shrine name is the thing this document warns hardest against
retiring — all 19 confirmed as live association names against the public `/en/shrines` and
`/en/wayside-shrines` listings; none has a `Schoenstatt`-domain sibling, so no `IsNameTranslateable`
row is touched; all `added_on` precede the ~08:50 UTC `markDataLabels()` deploy, so residue rather
than regression; and a flagged breadcrumb label is now rendered untranslated, so they cannot
self-heal back.

**Seventeen other strings on the same route were left alone.** They *do* have a `Schoenstatt`
sibling from 2017–2019, are fully translated by inheritance, and their `Application`/`default`
copies are breadcrumb duplication of §6's feature rather than of a defect.

Retired in pairs, which is the operational half of
[schoenstatt.link#71](../../schoenstatt.link/docs/api-v3.md). Verified on the first pair
(12995/12996): retiring one left the other live, the shared thread read from either id returned
**both** entries with their own `phraseId` and `textDomain`, and the counts fell by two rather than
one. Retiring only the `Application` half would have left every language 19 rows short with nothing
to say why.

### 26 rows retired 2026-08-11 12:47 UTC — 15 held, 11 should not have been

**This is the entry to read if you are about to retire something.** All five buckets were `skip-`
before this pass; all five were moved to `retire-`; three of them have been moved back, because
**retirement cannot hold a row the site still renders.**

| bucket | rows | outcome | why |
|---|---|---|---|
| `retire-dead-page` | 12 | **held** | nothing on the live page looks these up |
| `retire-retranslated-output` | 3 | **held** | the caller was fixed, so nothing translates its own output any more |
| `skip-format-template` | 5 | reverted | rendered on the library edit form |
| `skip-machine-readable-example` | 3 | reverted | rendered as a form placeholder |
| `skip-nothing-to-translate` | 3 | reverted | rendered on a publication page |

The argument for retiring the last three was that a call-number format exists legitimately, is
rendered, and can never be translated in any language — so leaving it alone means the count can
never reach zero and nobody can tell a deliberate omission from unfinished work. **That is right
about the rows and wrong about the mechanism.** `retirement.selfHealing` un-retires on the next
missed lookup, and within five minutes:

- **7231**, the opening-hours JSON, was live again because somebody opened `associations/create`.
- **7469**, the non-breaking space, was live again because a `publication` page rendered.

Both carry a `retire` with no `unretire` — the documented signature of the site disagreeing with
whoever retired the row. The other nine are still retired **only because nobody has opened the
library or publication edit forms since**, and they will return the same way.

So the test is not *is this row translatable* but **does anything still look it up**, and that is
what `is_writable()` says now. The fix for a rendered-but-untranslatable row is not on this side:
those call sites should not pass a parsed JSON example through `translate()` at all. Filed as
[`api-change-requests.md`](api-change-requests.md) §16.

**The nine were left retired rather than un-retired by hand**, per the warning above: self-healing
writes no history, so the *absence* of an `unretire` is what carries the information. Their return
is the evidence.

The `retire-dead-page` claim, by contrast, was **checked rather than inherited** — and that is why
it held. Twelve rows had been skipped since before this tooling on the assertion that the live page
says something different, and nothing had tested it. `https://schoenstatt.link/en/` contains none of
the twelve; it now opens `Our mission — Schoenstatt Link is effectively a database…`. Checking the
claim is what distinguished the buckets that held from the ones that did not.

Two rows needed `--allow-partial-siblings` and the reason is a good one — see
[Candidates deliberately *not* retired](#candidates-deliberately-not-retired) below.

### `retire-breadcrumb-record-name` — the first 2 rows, retired 2026-08-11 11:45 UTC

| id | domain | route | phrase | added |
|---|---|---|---|---|
| 13661 | `Application` | `composition` | `Meu menino pequenino` | 2026-08-11 01:38 UTC |
| 13662 | `default` | `composition` | `Meu menino pequenino` | 2026-08-11 01:38 UTC |

A composition's own name, filed twice by the breadcrumb's two-domain lookup. Not translatable in
any language — it is the title of one work, and rendering it in German would invent an edition
that does not exist. Production went from 1,581 live phrases to 1,579.

**These were the residual of a defect fixed the same morning.** `db7.4.sql` retired 302
composition names and `db7.6.sql` the last six publication ones; this pair matched neither
migration's scope, because `db7.6` statement 2 is scoped to `origin_route = 'publication'` and
joins `sch_publications.Title`. Both rows were filed at 01:38 UTC, **before** that morning's
09:00 deploy, so they are residue rather than evidence of a regression. Reported anyway as
[`api-change-requests.md`](api-change-requests.md) §15, because the migration's scope missing a
whole route is worth the maintainers knowing.

The note that landed on both:

> Retired as a composition name filed by the breadcrumb's two-domain lookup, not an interface
> string (api-change-requests-response.md 12). Not translatable in any language. If this is back
> on the worklist, the breadcrumb data-label fix has regressed for rou

**That note is truncated, and the truncation is the lesson.** It was written at 270 characters
against a 255 limit and sent by hand with `curl` rather than through the client, so the server
trimmed it mid-word — losing exactly the clause that says what to do if the phrase comes back,
which is the part a retirement note exists for. The meaning survives; the craft did not.

It has deliberately **not** been corrected. Fixing it would mean un-retiring and re-retiring,
which writes an `unretire` entry saying a human judged the retirement wrong — replacing a true
audit signal with a false account of a judgement, to fix a cosmetic defect. The wrong trade.

What was done instead: `Client.Retire` now refuses an empty reason and **trims an over-long one
while telling the caller**, `prepareRetirementNote` is a pure function so the rule is testable,
and `TestOverLongRetirementNoteIsReportedNotSilentlyTrimmed` pins it with this incident named in
the comment. The general rule — **retire through the tooling, not through `curl`** — is why the
tooling exists.

This pair is also the test case that proves the corrected classifier signature works. The **old**
test — "the English row is a verbatim copy of the key and no other language has ever translated
it" — passed it as ordinary translatable work, because its `pt` row was filled two minutes after
discovery by `writeMissingPhrasesToDb()`'s inheritance copy. So until 2026-08-11 this repository
was offering a Portuguese song title for translation into German, Spanish and Italian.

## Candidates deliberately *not* retired

Recorded because each one looks like a mistake and is not. This list is the more useful half of
the document.

- **Shrine names that double as book titles.** `Santuario del Padre` (6785), `Heiligtum der
  Berufung` (6815), in the `Schoenstatt` domain on route `publications/publication`, translated
  in all five languages. Title-shaped, on a publication route, and they are **§6's feature** —
  what makes a shrine's name render in Italian. Their `origin_route` records only where the
  string was first seen, in 2019. Retiring them would delete the feature.
- **Navigation labels in `default` and `Application`.** `Shrines`, `Africa`, `Music`. The
  breadcrumb files one row per label when the navigation-domain lookup misses; the maintainers
  left this deliberately because they are a few dozen **real interface strings worth
  translating**. `Music` in particular sits in `Application` on route `composition`, so the
  route-and-domain pair alone would catch it wrongly — which is why the third condition exists.
- **Association public notes.** Free prose belonging to one shrine — directions, opening notes.
  Translated once per locale **on purpose**, and if the record is edited the application retires
  the superseded phrase itself. `write-record-prose`, 37 rows.
- **A string that is also a live row somewhere else.** `Update on advances` and
  `Launch of new "Schoenstatt Shrines" app for Android!` are dead welcome-page copy in
  `Application` **and** live change-log text in `SionModel`, translated in all five languages on
  route `sion-model/view-changes`. `apply_retirements.py`'s sibling check refused both until
  `--allow-partial-siblings` was passed, and passing it was correct here: the sibling is a
  genuinely different row that happens to share a string. Read the sibling before overriding —
  that is what the flag is for, and it is why the check fails rather than warns.
- **The four JWT rows.** 13013, 12940, 12978, 12996 **as capsule ids** — on production those same
  ids hold `Tucumán` and `Miami, Florida`, which is this project's standing lesson about carrying
  ids between environments, appearing in its own documentation. Production has **no** rows of this
  shape: `classify.py`'s `LEAKED_SECRET` matched zero on 2026-08-11. Where they do exist they need
  **deleting**, not retiring — the requirement is that the string cease to exist, and
  `jtranslate:retire` leaves the row. `api-change-requests-response.md` §1.
- **Everything merely untranslated.** This was "120 rows in Italian, 99 in German. That is the
  work." As of 2026-08-11 that work is done — 141 translations written — so the category is empty
  rather than gone. The next row that arrives is work, not a mistake, and the test for the
  difference is still mechanical and still in `tools/classify.py`.

## When a candidate comes back

The signal this strategy is built on, and it is now mechanically checkable:

```
phrase_search { only_retired: true }    # what is retired
phrase_search {}                        # what is live
```

A phrase that appears in the second having been in the first came back **on its own** — the
self-healing path writes no history, so there will be no `unretire` entry after its `retire`.
That means the retirement was wrong, and the note says what was believed.

Treat it as a defect report at the caller, not as a row to re-retire. For the breadcrumb bucket
specifically: a row matching that signature with an `added_on` **after** the 2026-08-11 09:00 UTC
deploy is evidence the data-label fix regressed, and belongs in a change request before it
belongs in this file.

**There are now six buckets and 66 rows, so the check is worth building** — the note above said
two rows did not warrant it. What exists so far is `tools/apply_retirements.py`, which reads every
row it retired back by id and reports any that is live. That closes the loop at the moment of
retirement; it does not close it a week later, which is when a resurrection actually happens.

One thing to fix in whatever does: the first version of that read-back asked for
`?onlyRetired=1&limit=500` and compared the batch against the answer. It reported `0/2 present`
for two rows that were both correctly retired, because production has 4,537 retired rows and 500
is one page. **A paging bug that reads as "the retirement silently failed" is worse than no
check.** Reading `GET /api/v3/phrases/{id}` per row and testing `meta.retiredOn` is exact and
cheaper; that a retired row still answers by id is a documented guarantee, so it is safe to rely on.
