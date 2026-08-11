# Proposals for JTranslate — orphaned phrases and duplicate rows

> **Status: all three shipped, 2026-08-10.** Kept as the record of what was asked for
> and why, not as outstanding work. What landed, and where it differs from what is
> proposed below:
>
> - **Uniqueness** — `trans_phrases.phrase` is now `text`, with a `phrase_hash
>   binary(32)` and `UNIQUE (project, text_domain, phrase_hash)`. JTranslate grew a
>   migration runner (`bin/console jtranslate:migrate`, with `--pretend` and
>   `--status`); M003 adds the column and constraint, M004 merges duplicates and their
>   translations. The capsule went from 6,874 rows to 1,813.
> - **Retirement** — `retired_on` exists, set by `bin/console jtranslate:retire`, and
>   the un-retire-on-render branch works as described. The v3 API omits retired phrases
>   from the collection with no parameter to ask for them back, while
>   `GET /api/v3/phrases/{id}` still answers for one.
> - **The blog cleanup** — done by deletion (`database/db7.2.sql`), not by retirement.
>   That was a deliberate choice for a smaller table, and it accepts the cost this
>   document set out: the six live strings listed below come back on the next render,
>   but they come back untranslated, and their 39 non-English translations are gone.
>
> **The one thing this document got wrong is the mechanism**, and it is corrected in
> the last section rather than quietly patched here.

The prompt was a standing cost the site has accepted: **phrases are never removed
from the translation tables when they leave the project.** The blog's retirement
makes that concrete — 5,126 rows are about to become dead weight — and it is worth
asking whether the cost has to be accepted at all.

---

## What is actually in the table

| | |
|---|---|
| Rows for project `Schoenstatt` | 6,874 |
| Distinct phrases | **1,607** |
| Duplicate rows | **5,267 (77%)** |
| Rows under a `blog%` route | 5,126 |
| Distinct phrases under a `blog%` route | **40** |
| Non-English translations attached to `blog%` rows | 39 (25 es, 8 pt, 6 de) |

One string — a blog post opening `Hi everyone, \n\nit's been a few months…` —
holds **2,636 rows**. A second holds 2,452. Between them they are 74% of the
project's phrase table.

This is not a corpus problem, it is one insert path with no constraint behind it.

---

## 1. A uniqueness constraint on `trans_phrases`

**`trans_phrases` has no index at all except its primary key.** Not on `project`,
not on `phrase`, nothing:

```
Key_name  Column_name             Non_unique
PRIMARY   translation_phrase_id   0
```

The insert decision is made against a cached hash set, not the database —
`getPhraseIndex()` builds `[$text_domain][md5($phrase)] => true`, held in APCu and
in request memory. That is a good design and it is why there is no per-request
query. But it means the "have I seen this string?" check and the insert are not
atomic and are not protected by anything in the schema. On a cold or evicted
cache, concurrent renders all miss and all insert, and nothing refuses the second
write.

APCu evictions are known to happen here: `PhraseCache`'s own comments record a
production incident on 2026-08-03 where an oversized item cleared the entire
segment. A cache whose loss is survivable for reads is not survivable for a
check-then-insert with no backstop.

**Proposed:** a stored `phrase_hash` column with
`UNIQUE (project, text_domain, phrase_hash)`. The obvious form,
`UNIQUE (project, text_domain, phrase(255))`, does not survive this data — see the
second caveat.

Two caveats worth designing around rather than discovering:

- It cannot be added before deduplication, and deduplication has to **merge
  translations**, not just drop rows: duplicate phrase ids can each carry their
  own `trans_translations` rows. In this database **59 phrases** have more than one
  id carrying translations, so this is a real merge and not a theoretical one. Keep
  the lowest id, move translations the survivor lacks, and where two duplicates
  disagree on the same locale prefer the more recent `modified_on`.
- `phrase` is `varchar(2000)`, so a prefix index is unavoidable and the constraint
  would be on the first 255 characters. **There is already one collision**: two
  distinct German phrases in the `Schoenstatt` domain (517 and 772 characters,
  both beginning `Sie erreichen das Schönstattzentrum mit dem PKW/Bus von
  Grinzing…`) share their first 255 characters. They are different directions
  texts, not duplicates, and a `UNIQUE` prefix index would refuse the second.

  So the constraint needs a discriminator rather than a longer prefix — MySQL's
  index limit will not stretch to 2,000 characters of `utf8mb4`. A generated
  `phrase_hash` column (`SHA2(phrase, 256)`, stored) with
  `UNIQUE (project, text_domain, phrase_hash)` is exact, cheap, and matches what
  `getPhraseIndex()` already does conceptually — it hashes the phrase to test
  membership. Adding the column also gives the render path something to look the
  phrase up by, which the table currently has no index for at all.

**What this does not fix:** it prevents new duplicates. It does not remove
anything that has left the project — that is the rest of this document.

---

## 2. `retired_on` instead of `DELETE`

The reason nothing is ever removed is not that nobody wants to remove it. It is
that removal is irreversible and disproportionately punished: `deletePhrase()`
cascades the translations away, and `trans_translations` has no history to recover
them from. A wrong deletion silently destroys human work. Against that, doing
nothing is always the rational choice, and the table only grows.

**Proposed:** a nullable `retired_on DATETIME`.

- Retiring hides a phrase from the translator UI and the `/api/v3/phrases`
  collection. The row and its translations stay.
- The render path, on a phrase-index miss, checks for a retired row before
  inserting: if one exists, it **clears `retired_on`** instead of creating a new
  row. A phrase that turns out to still be in use un-retires itself the first time
  a page renders it, with its translations intact.
- `getPhraseIndex()` should keep including retired phrases, so a retired row is
  still found rather than duplicated. The retirement state belongs in the miss
  path, not in the membership test.

This inverts the economics. A wrong retirement costs nothing and repairs itself;
a wrong deletion costs translations nobody can get back. It is the difference
between a decision that needs to be right and one that only needs to be roughly
right.

### It also makes the blog cleanup safe

**`origin_route` records where a phrase was first *seen*, not where it is *used*.**
The index is keyed by phrase text, so whichever page rendered a string first owns
its `origin_route` permanently. Deleting `WHERE origin_route LIKE 'blog%'`
therefore removes live strings that merely had the bad luck to appear on a blog
page first. In this database that includes at least:

| phrase | `origin_route` | what it actually is |
|---|---|---|
| `Switch kernel` | `blog` | the Symfony canary toggle in the site chrome |
| `Italian` | `blog/create` | a language name, used on every create form |
| `Original language` | `blog/create` | a form label |
| `Is draft?` | `blog/create` | a form label |
| `Text successfully created.` | `blog/blog-post` | the **texts** module's flash message |
| `Text successfully updated.` | `blog/blog-post` | the same |

With `retired_on`, none of that has to be adjudicated in advance. Retire
everything matching `blog%`; the six above un-retire themselves the next time
those pages render, keeping their translations. Without it, each one is a
judgement call made under threat of unrecoverable loss.

---

## 3. Finding orphans offline, not at request time

The obvious way to know whether a phrase is dead is to record when it was last
rendered. **That was proposed and rejected, correctly**, and it is written down
here so it does not get re-proposed: the site compiles translations down to PHP
arrays precisely so that rendering touches neither the database nor, on a warm
cache, anything but request memory. A `last_seen` column would put a write on the
hot path to answer a question asked once a year. The architecture is right and the
column is wrong.

The signal can be reconstructed offline instead, because the set of phrases the
application *can* render is enumerable without running it:

- **Template-originated phrases** — static extraction of literal arguments to
  `translate()` / `$this->translate()` across `.phtml` and PHP, in the manner of
  `xgettext`. This is the majority of UI strings.
- **Content-originated phrases** — enumerable from the tables that feed them:
  `sch_associations.AssociationName`, `sch_publications.Title`, `texts.Title`, and
  whichever others the project registers.

A phrase in neither set is an orphan candidate. This costs nothing per request,
runs on demand or in CI, and fits where the module already has a console —
`jtranslate:export-catalogs` rebuilds the catalogs today, so a
`jtranslate:find-orphans` sits naturally beside it.

**Its output should propose retirement, never deletion.** Static extraction cannot
see a string built at runtime, and the content-table list will be incomplete the
day someone adds an entity type. Those are exactly the false positives that
`retired_on` makes harmless: the report retires, and anything still live comes
back on its own. The two proposals are worth the most together — the report is
only safe because retirement is reversible, and retirement is only systematic
because something proposes candidates.

---

## Suggested order

1. **Dedup + merge translations, then the unique constraint.** Stops the
   recurrence, and shrinks the table by 77% in this database. The blog cleanup is
   the natural moment: it removes 5,086 of the 5,267 duplicate rows anyway.
2. **`retired_on` + the un-retire-on-miss branch.** Makes cleanup reversible, and
   makes the blog retirement a one-line operation rather than an audit.
3. **`jtranslate:find-orphans`.** Turns "we should clean this up sometime" into a
   report somebody can act on.

Steps 1 and 2 are independent of each other and both are small. Step 3 is the only
one that is real work, and it is the only one that can wait.

---

## Notes on what was and was not verified

Verified by query or by reading the source in this capsule: the row and duplicate
counts; the absence of any index but the primary key; the `md5`-keyed phrase index
and its APCu caching; the 2026-08-03 eviction incident (from `PhraseCache`'s own
comments); that `origin_route` is first-seen rather than in-use, demonstrated by
the six strings above; that `deletePhrase()` cascades translations with no history.

Not verified at the time: the exact mechanism that produced 2,636 copies of one
string. A check-then-insert race against an evicted cache was consistent with
everything observed, and it was wrong.

**The actual cause was silent truncation.** `trans_phrases.phrase` was
`varchar(2000)` and these tables were created under a non-strict `sql_mode`, so a
phrase longer than 2,000 characters was truncated on insert without an error. From
that moment the row could never be recognised again: JTranslate hashes the *full*
phrase and compares it against an index built from the *stored* one, and those two
can never match. So every render of those two blog posts inserted another row — one
row per pageview, for years. `database/db7.2.sql` records the tell this document
missed: 5,088 of the blog rows are exactly 2,000 characters long.

This is a better failure than the one guessed at, because it is deterministic rather
than a race, and because it explains the shape of the data instead of merely being
compatible with it. It does not change the fix — the constraint and the widened
column are what stop it either way — but the difference between "concurrency, maybe"
and "the column was too short and nobody was told" is the difference between a theory
and a cause, and only one of them can be checked for elsewhere.

Also worth knowing: because `getPhraseIndex()` keys on `md5($phrase)`, the
duplicate rows **do not** inflate the cached index — they collapse into the same
key. Duplication costs a wider cache-miss query and a badly polluted moderator and
API view (a 20-row page of `/api/v3/phrases?originRoute=blog/blog-post` is two
distinct strings), but it is not a memory-pressure problem. An earlier draft of
this document claimed otherwise; it was wrong.
