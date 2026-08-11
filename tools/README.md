# tools/

Two pipelines. The first builds the translation index; the second does the translating.

## The translation pipeline

In the order it runs. Only `apply_translations.py` writes anything, and only when
given `--write`.

| step | what it does |
|---|---|
| `extract_reading_material.py` | Pulls text out of the movement's own books for terminology mining. **They are copyrighted** — it extracts to scratch, and only short attestations (a term, a count, a clause) belong in `data/`. |
| `screens.py` | Opens each Italian page from the index and finds which backlog phrases are visible on it, recording the **enclosing element** and the nearest heading. This is what tells you whether `Search` is a button or a column header, which decides the Italian. |
| `classify.py` | Sorts the backlog into translate, skip, or retire, each bucket with the reason next to the rule. This is where the decision that something is *not* translatable work lives — see [`docs/it-skipped.md`](../docs/it-skipped.md). A `skip-` row exists legitimately; a `retire-` row should not exist at all, and its reason is phrased to be used verbatim as the `_note` on the retirement — see [`docs/retire-queue.md`](../docs/retire-queue.md). Writes `retire_candidates.json` alongside `classified.json` and `skip_pairs.json`. |
| `build_worklist.py` | Groups the gap into **beats** — one family of related routes, whole, with the recurrent terms listed first and a per-beat slice of what the language already says on those routes. One beat is one agent's assignment. |
| `conform.py` | Checks the drafts mechanically before anything is written: placeholder integrity, retyped keys, collisions, length caps, sibling bleed, identical-to-source, and the terms two beats settled differently. **Exit 1 on anything blocking.** |
| `hunt_lexical.py` | Finds defects in translations the site *already* has, using the books as a lexicon. A word absent from 231k words of edited Spanish whose accent variant occurs 74 times is a misspelling. |
| `apply_translations.py` | Joins the per-batch translation files to phrase ids and PATCHes in batches of 200. **Dry run by default.** Enforces the same guards as the MCP server: no empty values, the length cap from the live schema, languages read at request time. |
| `apply_corrections.py` | The only path that **overwrites** an existing translation. Asserts the current value before replacing it, so a stale list fails loudly instead of clobbering a later edit. Dry run by default. |
| `apply_retirements.py` | Takes rows off the worklist, resolving ids from the target by `(text_domain, source string)` as `apply_translations.py` does. Dry run by default. Two checks are specific to retirement: it **fails** if a live sibling row of the same string is not in the batch, and `--added-before` warns when a row was filed after the caller that files it was fixed. |
| `build_review_queue.py` | Collects the judgement calls recorded during translation into [`docs/it-review-queue.md`](../docs/it-review-queue.md) and a page to hand a reviewer. |

`build_worklist.py`, `conform.py` and `hunt_lexical.py` exist because they were subagents
first, and worse at the job. The conformance agent was literally instructed to *write a
script*; the lexical checks were four of six hunting lenses whose findings were mostly
refuted. Between them they cut a language's drafting workflow from seven agents to five and
its revision workflow from 79 to six. See [`docs/workflow-review.md`](../docs/workflow-review.md).

**A script that reports everything it matches is not usable.** `conform.py` first produced
109 findings on the German drafts of which 108 were correct as they stood, all proper names
and loanwords. Three rules fixed it: bleed is matching *one* sibling and matching several is
house convention; es/pt/it agreeing is cognacy, not copying; particles stay lowercase inside a
proper name. 109 → 1, and that one was real.

**A check that fails is worth more than one that warns, when the failure is cheap to override.**
`apply_retirements.py`'s sibling check refuses the whole batch rather than printing a note,
because the thing it catches — retiring one row of a pair and leaving the string on the worklist
through the other — is invisible afterwards. It fired on its second use, on two rows whose
siblings turned out to be legitimately different rows sharing a string, and
`--allow-partial-siblings` was the right answer. The point is that the override was a decision
somebody made after reading the siblings, which a warning would not have produced.

Its read-back also shows the opposite lesson: the first version compared the batch against
`?onlyRetired=1&limit=500` and reported `0/2 present` for two rows that were correctly retired,
because production has 4,537 retired rows. **A check whose failure mode looks exactly like the
bug it is meant to catch is worse than no check.** It reads each row by id now.

Three things `apply_translations.py` learned the hard way and encodes:

- **A phrase id means nothing outside the environment it was read from.** Production and
  the capsule share a lineage, so most ids agree — which is what makes this dangerous
  rather than obvious. On 2026-08-10, 68 of them differed and six were live production ids
  holding a *different phrase*. The tool resolves ids from the target on every run, by
  matching the source string, and will not accept an id map from anywhere else.
- **The batch payload is an object keyed by phrase id**, per `docs/api-v3.md` —
  `{"phrases": {"10028": {"it": "…"}}}`. Send an array and each element gets keyed by its
  index, so every item fails `404` — correctly reported in `results` and
  `summary.failed`, with an HTTP 200 overall because a batch's outcome is per-item.
  **Read `summary`, not the status.** An earlier version of this tool looked for response
  keys that do not exist and reported "0 written, 0 failed", which looked like the API
  swallowing the request and was really a bug on this side.
- Whitespace in a source string is part of the key. Several phrases differ from each
  other only by `\r\n` vs `\n`, or carry a non-breaking space, and cannot be typed by
  hand. Match those by prefix against the real key rather than retyping them.

## The index pipeline

The steps that produce [`docs/translation-index.md`](../docs/translation-index.md),
in order. They talk to the **capsule** (`http://localhost:8080`) and its database;
none of them writes anything to either.

| step | what it does |
|---|---|
| `crawl.py` | Walks the site in Italian, reading each page's route out of its own footer. Capped per route so it spreads across the site instead of drowning in one detail page. |
| `verify_urls.py` | Fetches every candidate once and classifies it: usable, redirect, or sign-in required. |
| `recheck.py` | Re-fetches the usable ones and **drops any whose page disagrees** — different final URL, or a footer route other than the one claimed. |
| `build_index.py` | Joins the survivors with the per-route counts and writes the index. |
| `reverify.py` | The same check as `recheck.py`, run over an index that already exists. Use it after the application changes: a page that stopped existing or started redirecting looks entirely normal in a stale index. |

**Re-run `reverify.py` before `build_index.py` whenever the site has moved**, then
refresh the two `.tsv` count files from the SQL at the foot of the index. That is what
the 2026-08-10 rebuild did after the deduplication and the blog cleanup — all 109 URLs
survived, but every count in the document had changed.

`recheck.py` is the one that earns its place. The crawler follows redirects
silently, so an association URL that 302s to `/it/` was recorded under its own
URL with the *welcome* page's route — a row that looked entirely normal. Requiring
each page to agree that it is the page we claim caught 44 of them, and needs no
list of known-bad URLs to do it.

Every step takes the scratch directory as its first argument — `python3 tools/crawl.py
<scratch> [max-fetches] [per-route]`, then the rest as `python3 tools/<step>.py
<scratch>` — and reads and writes its intermediates there. The counts come from SQL run
separately (the queries are at the foot of the index). This is a **snapshot
pipeline, not a live service** — re-run it when the numbers matter, and treat the
committed index as dated.

The candidate URLs come from two places: the crawl, and ids read from the database
and turned into `SL…` identifiers per
`module/Schoenstatt/src/Validator/SchoenstattLinkIdentifier.php` (association
100000/`A`, publication 200000/`L`, person 300000/`P`, text 400000/`T`,
composition 500000/`C`).
