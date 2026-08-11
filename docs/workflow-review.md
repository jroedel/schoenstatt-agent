# Reviewing the skill and the two workflows against what running them taught

The skill and the two workflows were drafted before being used, then used on four languages
in one session. This is what they got wrong. It is written down because the drafts read
plausibly and were still wrong in ways only execution exposed.

## What the runs actually did

| run | agents | outcome |
|---|---|---|
| `translate-bulk` de | 8 | 659 strings drafted, applied to production |
| `translate-bulk` es | 5 | 220 drafted, applied |
| `translate-bulk` pt | 6 | **1 of 4 chunks survived** — 110 drafted, applied |
| `translate-revise` es | 79 | 98 candidates, 24 verified, 21 survived; synthesis died |
| `translate-revise` de | 79 | 49 candidates, 24 verified, 12 survived; synthesis died |
| `translate-revise` en | **364** | 119 candidates, 24 survived; synthesis died |

**The en revise run spawned 364 agents and exhausted the organisation's monthly spend
limit**, which then killed three other runs mid-flight. That is the headline failure and
every lesson below is downstream of it.

## 1. Both workflows crashed on the first launch, before any agent ran

`args` arrived as a JSON-encoded **string**, not an object. Destructuring a string yields
`undefined` for every field, so the first symptom was
`undefined is not an object (evaluating 'chunks.map')` — an error 40 lines from the cause.

**Fixed.** Both scripts now normalise `typeof args === 'string'` and validate the fields up
front with a message naming what is missing. Cost: two dead runs and a confusing stack
trace. Cheap, but it should have been in the draft — a script whose entire input arrives
from outside should never trust its shape.

## 2. Verification cost was unbounded, and that is what broke the budget

The draft ran three skeptics per finding with no cap: `agents = findings × 3`. On English,
119 candidates became 364 agents.

The mistake was not the fan-out — adversarial verification is the right pattern for
irreversible writes. The mistake was **not bounding it at design time**. A phase whose size
is a function of an unknown upstream count needs a cap in the same breath as the fan-out.

**Fixed**, but note the order of events: the cap was added after the de and es runs were
already in flight and *before* they hit verification, which is why those two capped at 24
and en did not. So the fix is real but was not what saved them.

The cap logs what it defers, per the skill's own "no silent caps" rule. That mattered
enormously — see below.

## 3. The revise workflow lost its work; the bulk workflow did not. This is the real lesson

Both had agents die. The difference in what survived is entirely architectural.

- **`translate-bulk`: each drafting agent writes its own file.** When three of four
  Portuguese chunks died, the surviving chunk was on disk, valid, and applied to production.
  Nothing was lost that had been done.
- **`translate-revise`: agents returned data, and one final agent wrote the file.** When
  `propose` died on the spend limit, **every survivor from a 79-agent run became
  unrecoverable** — three times over.

Recovery attempts and why they failed:

- The run journal (`journal.jsonl`) holds one `result` line per agent, but **the result
  strings are truncated mid-value**. Findings could not be read back out.
- The verify agents' schema was `{refuted, reason, better_proposal}` — **no `phrase_id`**.
  Even with intact journal records, a verdict could not be matched to its finding, because
  the only linkage was the agent's `label`, which the journal does not store.

What *did* survive was the `deferred_unverified` list, because the script returned it from
the top-level and the harness stores that intact. **74 Spanish and 25 German findings, with
full detail, were recovered from the one list that existed for an unrelated reason.**

Three fixes, all now in `translate-revise.js`:

1. **Every hunt agent writes `<lang>_hunt_<lens>.json` before returning.** The durable copy
   is the file; the return value is a summary.
2. **Every verify verdict echoes its own `phrase_id`.** A result that does not carry its
   subject is unusable the moment synthesis fails.
3. **The script checkpoints the survivors to disk before `propose` runs**, so the final
   agent formats a file that already exists rather than being the only thing that creates it.

Generalised: **in a workflow whose phases can die independently, durability belongs to the
phase that produced the data, not to the phase that consumes it.**

## 4. The drafting agents did something better than they were told to

Unprompted, several drafting agents dumped the site's **existing** translations for their
language and mined those before translating. That turned out to settle far more than the
glossary did — `Association` → `Gruppierung` in German messages, `Entity` → `Objekt`,
`Cenáculo` → the Latin `Coenaculum`, `call number` → `número localizador`.

It also let them do something the draft never asked for and should have: where a source
string already had a translation **in a different text domain**, they reused it verbatim
rather than writing a better one, so the two rows cannot drift apart.

**Added to the skill** as a step, not a suggestion.

## 5. The in-context lens earns its place

The `in-context` lens — fetch real pages and read them — was the only lens that could have
found `Literatur` in the Portuguese navigation, because that row was not empty and no query
would flag it. It is slow and it is worth it. Keep it.

## 6. What the drafts got right

Worth recording so it is not "improved" away:

- **Agents propose, the main loop writes.** Held under pressure. Not one subagent touched
  production across 540 agents, and every one of the 1,041 rows written this session went
  through a dry run first.
- **Adversarial verification pays.** English refuted **95 of 119** candidates, German 12 of
  24. A workflow that proposed all 119 English "corrections" to a language that is the
  site's pivot would have been actively harmful.
- **The mechanical/editorial split in `translate-bulk`.** The mechanical check verified
  placeholder integrity across 220 Spanish and 659 German entries and found zero
  mismatches — a claim worth having, and not one a reviewer could make by eye.

## 7. What is still unfinished

- **English findings are lost.** 119 candidates, 24 survivors, no detail — the en run
  predated both the cap and the durability fixes. A re-run is needed and will now produce
  files.
- **The editorial findings are proposals, not corrections.** 54 Spanish and 23 German
  findings sit in `es_editorial_candidates.json` / `de_editorial_candidates.json`. Only the
  23 objectively verifiable ones (misspellings, wrong accents, mismatched punctuation, one
  untranslated row) were applied. The rest need a decision, several of them a house
  decision — `Schönstatt` vs `Schoenstatt`, `du` vs `Sie`, `Edition` vs `Auflage`.
- **Portuguese has 3 of 4 chunks left**, ~264 strings.

## The one-line version

The draft's *content* was mostly right and its *failure modes* were not thought through. A
workflow is not finished when its happy path works; it is finished when you know what
survives each phase dying, and the phase that makes data owns writing it down.

---

# The rewrite, 2026-08-11

The maintainer asked for fewer subagents, slightly fewer skeptics, and — the substantive
suggestion — for agents to be organised around a *context*, moving laterally through the
phrases of a route family rather than through an arbitrary slice of the backlog. That is
right, and measuring it turned out to justify a larger change than it first sounds like.

| | before | after |
|---|---|---|
| `translate-bulk`, a 374-string language | 4 draft + 2 conform + 1 repair = **7** | 4 beats + 1 reconcile = **5** |
| `translate-revise`, ~50 findings | 6 hunt + 150 verify + 1 propose = **157** | 2 hunt + 4 verify = **6** |
| `translate-revise` as actually run on English | **364** | ~6 |

## 1. The preamble was four times the job

The thing a drafting agent spends tokens on is not the strings. Measured on the Portuguese
gap:

```
per agent, before translating anything   SKILL.md 10k + glossary 15k + style 5k
                                         + the existing-rows dump it makes itself 48k
                                         = ~23k tokens
the entire payload                       374 units, all siblings quoted = ~24k tokens
```

Four fixed chunks paid **~92k tokens of preamble to carry ~24k of work**. That is the whole
argument for fewer agents, and it is not a marginal effect — it is the dominant term. Every
agent removed removes a preamble.

## 2. Route families are where the quality is, not just the savings

The old `build_worklist.py` sorted by route and then cut every 110 units, so chunks were
route-coherent by accident and cut across a screen wherever the counter landed. Grouping
properly, the Portuguese gap is not 374 scattered strings:

| beat | units | terms recurring ≥3× |
|---|---|---|
| library1 | 110 | 18 |
| library2 | 81 | 10 |
| account | 48 | 21 |
| misc | 25 | **0** |

**301 of the 374 units are one family** — publications/libraries/books — and inside it 82
English words recur across three or more units: `call number`, `checkout`, `edition`, `label`,
`import`. Those are decisions, not strings. One agent owning the family settles `call number`
once and cannot contradict itself; two agents splitting that vocabulary each settle it alone
and may disagree.

So the beat file now lists the recurrent terms at the top, in recurrence order, and the
drafter is told to settle them *before* translating and to return a `terms` block recording
what it chose. `conform.py` then checks the term blocks against each other. The one failure
this arrangement can introduce is checked directly rather than hoped away.

Two measurements shaped the rest of the design:

- **Only 25 of 91 recurrent library terms appear anywhere in the account routes.** The
  vocabularies barely overlap, so each beat gets *its own slice* of the existing rows — 25k
  characters instead of the whole 48k table, and 7.4k for the account beat. That slice is
  where the saving lands, and it also makes the skill's "mine the existing rows first" step
  automatic instead of dependent on the agent's initiative.
- **The leftover 25 units had zero terms recurring three times.** The gain is real but not
  uniform, so the tool does not spread it evenly: a family whose terms do not recur is not a
  family, it is a pile sharing a URL prefix, and giving it an agent buys a second preamble and
  nothing else. The merge test is recurrence, not size.

## 3. Two phases were agents doing decidable work

This is the largest reduction and it came out of asking what the agents in each phase were
actually deciding.

**Conformance.** The `conform:mechanical` agent was *instructed to write a script* —
"write Python, do not eyeball this". An agent whose job is to write a script should be a
script. It is `tools/conform.py` now, run from the main loop, and it exits 1 on anything
blocking so the caller can gate on it.

**Four of the six revision lenses.** Every correction applied to production on 2026-08-10 —
twenty Spanish, two German — was of one kind: `exitósamente`, `coleción`, `Volúmen`,
`Santisima`, `Arcangel`, `Pais`, `¡Foto?`, `Strasse`. Six agents hunted for those and a
majority of what they returned was refuted.

`tools/hunt_lexical.py` does it with the bibliography as a lexicon: a word absent from 231k
words of edited Spanish whose accent variant occurs 74 times is a misspelling, and that is
evidence rather than an opinion. Run against Spanish it **independently rediscovered the
corrections that pass had applied**, plus `contínuamente`, `perpétua` (×3), `calido`,
`pagina`, `Linea` and `ADORACION` which six agents missed. Cost: no agents.

## 4. Grading is what makes a script's output usable

Both scripts were useless in their first version, in the same way: they reported everything
they matched. `conform.py` produced 109 findings on the German drafts of which 108 were
correct as they stood — proper names (`María Ayuda`, `Sr. Jessy`, `Tabor Magnificat`) and
loanwords the whole site keeps (`Moderator`, `Information`, `Barcode`).

Three rules fixed it, and each is a fact about the data rather than a threshold:

- **Bleed is matching *one* sibling. Matching several is house convention.** A value equal to
  what two or more other languages say is the site's own decision to leave a loanword alone.
- **es/pt/it agreeing is not evidence of copying.** They are cognate languages: `Casa de
  retiros`, `Emitir token` and `Tokens registrados` are each correct in both Spanish and
  Portuguese. The copy-a-sibling errors this project actually found crossed a family line —
  German `Literatur` in the Portuguese column. So a match is graded by distance, not count.
- **Particles stay lowercase inside a proper name.** Requiring every token capitalized
  rejected `Oasis de Misericordia` and `Nuevo Schoenstatt, Santuario del Padre`, both shrine
  names, both correctly left alone.

109 findings → **1 worth a human glance**, per language. And that one was real: German `Branch
moderator` had been rendered `Geistlicher Begleiter (Schwester, Priester, Pater)`, a
parenthetical gloss the source does not contain. It is live on production and it is a
correction candidate.

The same discipline caught two bugs in `hunt_lexical.py` before it was trusted: `%C3%A1` in a
Wikipedia URL read as two placeholders, and a paired-punctuation rule that flagged the
perfectly correct `¡Tu mail ha sido verificado!` *and proposed changing its `¡` to `¿`* — a
check that would have introduced an error. Counting openers against closers is right where
"ends with `?`" is wrong.

**What no amount of grading fixes:** `variant-attested` still flags proper names.
`Magnificat` is Latin and right as it stands against the Spanish common noun `magníficat`;
`Berlin-Frohnau` is a German place name inside a shrine name. Both are names. That is exactly
why the findings still go to verification instead of straight to `apply_corrections.py` — the
script is far better than an agent at finding candidates and no better at all at knowing what
a thing is called.

## 5. Batch the item, fan out the phase

Verification was one agent per skeptic per finding: 119 × 3 = 357. But a skeptic's expensive
context is the glossary, the style guide and the corpus, and those are **identical for every
finding in the language**. Loading them once to judge twenty-five findings costs a fraction of
loading them twenty-five times.

Independence survives batching, which is the part worth being careful about: the skeptics never
see each other, each has a distinct angle, and each renders a separate per-item verdict with
its own evidence. What is lost is per-finding blindness within one skeptic's context, and the
mitigation is explicit — a per-item verdict schema, and an instruction that a run of
confirmations is not a reason to confirm the next one.

**Two skeptics, unanimity to survive.** Fewer agents and a stricter filter at the same time:
majority-of-three passes a finding on 2-1, unanimity-of-two does not. Refusing a real fix
costs a re-run; accepting a wrong one costs the text permanently. The tie does not go to the
proposal.

And reassembly now **fails closed**: a finding whose verdicts are missing is unverified, not
approved. An agent that dies must not thereby promote a correction to a production write.

## 6. What the durability rule actually rules out

The reflex fix for the lost 79-agent run was a `checkpoint` agent that wrote the state before
`propose` ran. That was wrong in the same shape as the original bug — still one agent, still a
single point of failure, just an earlier one.

Both the `propose` and `checkpoint` agents are gone. Every hunt agent writes its own findings
file and every verify agent writes its own verdicts file, so survivors are reconstructible from
disk even if the script dies mid-pipeline; and the return value is at the top level, which the
harness stores intact — not a guess, that is how 74 Spanish and 25 German findings were
recovered from the run that lost everything else. Two independent copies, neither an agent.
Formatting the document is `build_review_queue.py`, which was already a tool.

## What is unchanged, deliberately

- **Agents propose, the main loop writes.** Held across 540 agents without one touching
  production.
- **Adversarial verification.** It refuted 95 of 119 English candidates. Cheaper, not weaker.
- **The in-context lens.** Fetching real pages is the only way `Literatur` in the Portuguese
  navigation was ever going to be found — the row was not empty and its value was a real word.
  It is slow and it stays.

## The one-line version of the rewrite

Ask what each agent is *deciding*. Where the answer is "nothing — it is checking a property of
two strings", that is a script; where it is "which of these two renderings is right", that is
an agent, and it should be given one screen's worth of vocabulary and the authority to settle
it once.
