export const meta = {
  name: 'translate-bulk',
  description: 'Draft translations for a whole language gap on schoenstatt.link, one agent per route family, then reconcile the terms two agents settled independently. Produces files; writes nothing.',
  whenToUse: 'When a language has a large gap of empty translations to fill — hundreds of strings. Not for correcting existing translations; use translate-revise for that.',
  phases: [
    { title: 'Draft', detail: 'one agent per beat — a family of related routes, whole' },
    { title: 'Reconcile', detail: 'only the terms two beats decided differently' },
  ],
}

// args: { lang, scratch, beats: [{name, beat_file, seen_file, units, routes}, ...],
//         glossary, style }
//
// Build `beats` with:  python3 tools/build_worklist.py <scratch> --lang <lang>
// and pass <scratch>/<lang>_beats.json's `beats` array straight through.
//
// This workflow DRAFTS. It writes tr_<lang>_<beat>.json files into the scratch directory and
// returns a report. **It does not touch the site.** Every write goes through the main loop
// via tools/apply_translations.py after a dry run a person has read. Translation writes became
// recoverable on 2026-08-11 (`GET /api/v3/phrases/{id}/history`), which changes nothing here:
// a subagent still does not get to make an unreviewed write to a live public database, and
// recovery needs a reviewer who noticed.
//
// ---------------------------------------------------------------------------------------
// Why this is organised by route family and not by a count of strings
//
// The first version cut the worklist into fixed 110-unit chunks and gave each to an agent.
// That got the cost structure backwards. What a drafting agent spends tokens on is mostly
// not the strings:
//
//     per agent, before translating anything   SKILL.md 10k + glossary 15k + style 5k
//                                              + the existing-rows dump it makes itself 48k
//                                              = ~23k tokens
//     the entire Portuguese payload            374 units with all siblings quoted = ~24k
//
// Four chunks therefore paid ~92k tokens of preamble to carry ~24k of work. **The duplicated
// preamble was four times the job.** Every agent removed removes a whole preamble, so the
// cheapest workflow is the one with the fewest agents that still does the work well.
//
// Route families are what make a bigger beat *better* rather than merely cheaper. 301 of
// those 374 Portuguese units are one family — publications/libraries/books — and inside it 82
// English words recur across three or more units. `Call number`, `checkout`, `edition`,
// `label`: those are decisions, not strings. An agent that settles `call number` once applies
// it to 300 rows and cannot contradict itself, where two agents split down the middle of the
// same vocabulary each settle it alone and may disagree. The beat file puts the recurrent
// terms at the top for exactly this reason, and the agent declares what it settled.
//
// Only 25 of those 91 recurrent library terms appear anywhere in the account routes — the
// vocabularies barely overlap — which is what lets each beat be handed *its own slice* of the
// existing rows instead of the whole 48k table. That slice is where the saving actually
// lands, and it is also the skill's "mine the existing rows first" step, done for the agent
// rather than left to its initiative.
//
// The gain is not uniform, so the tool does not spread it evenly: a family whose terms do not
// recur is not a family, and it goes in one leftover pile rather than getting an agent and a
// preamble of its own.
//
// ---------------------------------------------------------------------------------------
// What is NOT an agent any more
//
// The mechanical conformance check used to be a subagent asked to write a script. It is now
// `tools/conform.py`, run from the main loop. Placeholder integrity, key collisions, retyped
// keys, length caps, sibling bleed and identical-to-source are decidable properties of two
// strings; an agent adjudicating 659 of them is slower, dearer and less reliable than the
// script, and it cannot die halfway. On the German drafts the script reduced 109 raw hits to
// **one** finding worth a human glance — and that one was real: `Branch moderator` had been
// rendered `Geistlicher Begleiter (Schwester, Priester, Pater)`, a gloss the source does not
// contain.
//
// Which leaves agents doing only what agents are for. The editorial check is gone too, but
// its useful half survives: `conform.py` collects the terms more than one beat rendered, and
// the single Reconcile agent below decides those and nothing else.

const A = typeof args === 'string' ? JSON.parse(args) : (args || {})
const { lang, scratch, beats, glossary, style } = A
if (!lang || !scratch || !Array.isArray(beats) || !beats.length) {
  throw new Error(`translate-bulk needs {lang, scratch, beats[], glossary, style}; got ` +
    `${JSON.stringify({ lang, scratch, beats: Array.isArray(beats) ? beats.length : beats })}. ` +
    `Build beats with tools/build_worklist.py and pass <lang>_beats.json's "beats" array.`)
}
for (const b of beats) {
  if (!b || !b.name || !b.beat_file) {
    throw new Error(`each beat needs {name, beat_file, seen_file}; got ${JSON.stringify(b)}`)
  }
}

const COMMON = `
You are translating UI phrases for schoenstatt.link into ${lang}, for a public reference
database about Schoenstatt.

READ THESE FIRST, in full — repo-relative paths, and the repository root is your working
directory:
  .claude/skills/schoenstatt-translation/SKILL.md   the method and its rules
  ${glossary}    the agreed term renderings for ${lang}, with the evidence
  ${style}       register, variant, and what stays in English

Non-negotiable rules from the skill:
- Translate from the SOURCE KEY, never from another language's translation. Every error
  ever found in this site's existing translations came from copying a sibling language and
  half-converting it.
- The other languages (es/pt/de/it/en shown per entry) are evidence of HOUSE CONVENTION —
  whether a term is translated at all, how a name is shaped. They are NOT evidence of what
  the word is in ${lang}. Where two of them disagree with each other, that is your signal
  that the entry needs flagging.
- The source key is usually English but NOT always. If a key is in another language,
  translate that language. If a key is stale English that every sibling contradicts,
  follow the siblings and say so in your review note.
- Placeholders (%s, %1$s, {0}) must survive intact and in a position the sentence works in.
- Obey the glossary. If a glossary term is wrong for a specific context, do not silently
  depart from it — write the glossary form and flag the context in a review note.
- Where you are genuinely unsure, still produce your best translation, and write a review
  note saying what you chose, what the alternative was, and why. A flagged good-enough
  answer is worth far more than a confident wrong one.
`

phase('Draft')

const drafts = await parallel(beats.map(b => () =>
  agent(`${COMMON}

## Your beat: ${b.name}

You own one family of related routes, whole: ${(b.routes || []).join(', ') || b.name}.
That is deliberate. These screens share a vocabulary, so the terminology decisions are
yours to make once and apply everywhere, and nobody else is translating a string that
sits next to yours.

  ${scratch}/${b.beat_file}    your ${b.units || ''} strings, recurrent terms listed at the top
  ${scratch}/${b.seen_file}    what ${lang} ALREADY says on these same routes

**Work in this order. The first step is what makes the rest consistent.**

1. Read the recurrent terms at the top of your beat file. Those words appear in three or
   more of your strings, so each is one decision that lands in many rows. Settle each one
   now, before translating anything, using ${glossary} first, then ${b.seen_file}, then the
   movement's own publications and pages in ${lang}.
2. Read ${b.seen_file} properly. House convention lives in those rows, not only in the
   glossary — the glossary holds the decisions somebody wrote down, those hold every
   decision anybody ever made. **Where a source string there matches one in your beat,
   reuse its value verbatim** rather than writing a better one: the two rows render in the
   same places and must not drift apart. Improving one of a pair is worse than leaving both
   mediocre.
3. Then translate every entry in your beat, applying the terms you settled in step 1
   without exception. If step 1 turns out wrong for one entry, keep the settled term and
   flag that entry — do not quietly use a second rendering.

Write your output to ${scratch}/tr_${lang}_${b.name}.json in exactly this shape, with the
source string as the key, byte for byte as it appears after "SRC: ":

{
 "${lang}": { "<source string>": "<your translation>", ... },
 "terms":   { "<recurrent English term>": "<the ${lang} rendering you settled on>", ... },
 "review":  { "<source string>": "<what you chose, the alternative, and why>", ... }
}

The "terms" block is not decoration and it is not optional. It is checked against the other
beats' term blocks, and a term two beats settled differently is the one inconsistency this
whole arrangement can produce. Put every recurrent term from the top of your beat file in
it, plus any other term you had to decide.

Notes on getting the JSON right — these have bitten before:
- The key must match the source EXACTLY. Some strings contain a non-breaking space, or
  differ from a near-identical row only by \\r\\n vs \\n. If a source string spans multiple
  lines in the beat file, do not retype it: read ${scratch}/${lang}_units.json, find the
  entry whose "src" starts with the same 40 characters, and copy that value verbatim. A
  retyped key translates nothing and is reported as a blocking error.
- Put an entry in "review" only where there was a real judgement call. Do not flag routine
  labels.

Return {"file": "...", "translated": <count>, "flagged": <count>, "terms_settled": <count>,
"notes": "<anything the next agent should know — a term you had to invent, a source string
that looks broken, a place the glossary was silent>"}`,
    { label: `draft:${b.name}`, phase: 'Draft', schema: {
        type: 'object',
        required: ['file', 'translated', 'flagged', 'terms_settled', 'notes'],
        properties: {
          file: { type: 'string' },
          translated: { type: 'integer' },
          flagged: { type: 'integer' },
          terms_settled: { type: 'integer' },
          notes: { type: 'string' },
        },
      } })
)).then(rs => rs.filter(Boolean))

const translated = drafts.reduce((n, d) => n + (d.translated || 0), 0)
log(`drafted ${translated} strings across ${drafts.length} of ${beats.length} beats`)

// Each agent wrote its own file, and that is load-bearing rather than tidy. On the run that
// exhausted the org's spend limit, three of four drafting agents and both checking agents
// died — and the one file that had been written was still on disk, still valid, and was
// applied to production. A workflow whose output exists only in return values loses
// everything upstream of the first failure.
if (drafts.length < beats.length) {
  log(`${beats.length - drafts.length} beats died. Their files are absent; the rest are on ` +
      `disk and usable. Re-run only the missing beats.`)
}

phase('Reconcile')

// conform.py has already found everything decidable. The only thing left for an agent is the
// question a script cannot answer: two beats settled one term differently — which is right?
// That agent gets the term list and nothing else, so it is cheap and cannot wander.
const reconciled = await agent(`${COMMON}

Run the mechanical check yourself and act only on what it cannot decide:

    python3 tools/conform.py ${scratch} --lang ${lang}

It writes ${scratch}/${lang}_conformance.json. Read it. It has already settled placeholder
integrity, retyped keys, collisions, length caps, sibling bleed and identical-to-source, and
graded each as blocking / check / expected. **Do not redo any of that.** Your job is the two
fields a script has no opinion about:

1. **disputed_declared_terms** — terms two beats settled differently. For each, decide which
   rendering is right (glossary first, then the existing rows, then the movement's own
   publications), then EDIT the tr_${lang}_*.json files so every beat uses it. This is the one
   inconsistency the one-agent-per-route-family arrangement can create, so it is the one thing
   worth an agent here.
2. **cross_beat_terms** — terms that recur across beats with their renderings side by side.
   Skim for a real inconsistency the term blocks missed. Report; do not rewrite wholesale.

Then fix anything the script graded **blocking**, in place, in the JSON files — those stop
apply_translations dead. A lost placeholder goes back in a position where the ${lang} sentence
still works. A retyped key gets copied verbatim from ${lang}_units.json.

Leave everything graded **check** alone and just list it: those need a person, and several
are legitimate (a name, a code, a language that needs more words).

Re-run conform.py when you are done and confirm it reports zero blocking.

Return {"terms_reconciled": [{"term": "...", "chose": "...", "over": "...", "why": "..."}],
"blocking_fixed": <count>, "still_blocking": [{"source": "...", "why": "..."}],
"needs_a_person": [{"source": "...", "detail": "..."}]}`,
  { label: 'reconcile', phase: 'Reconcile', schema: {
      type: 'object',
      required: ['terms_reconciled', 'blocking_fixed', 'still_blocking', 'needs_a_person'],
      properties: {
        blocking_fixed: { type: 'integer' },
        terms_reconciled: { type: 'array', items: {
          type: 'object', required: ['term', 'chose', 'over', 'why'],
          properties: { term: { type: 'string' }, chose: { type: 'string' },
                        over: { type: 'string' }, why: { type: 'string' } } } },
        still_blocking: { type: 'array', items: {
          type: 'object', required: ['source', 'why'],
          properties: { source: { type: 'string' }, why: { type: 'string' } } } },
        needs_a_person: { type: 'array', items: {
          type: 'object', required: ['source', 'detail'],
          properties: { source: { type: 'string' }, detail: { type: 'string' } } } },
      },
    } })

return {
  language: lang,
  agents: drafts.length + 1,
  beats: drafts.length,
  beats_missing: beats.length - drafts.length,
  translated,
  flagged: drafts.reduce((n, d) => n + (d.flagged || 0), 0),
  drafter_notes: drafts.map(d => d.notes).filter(n => n && n.trim()),
  reconciled,
  next_step: `Nothing has been written to the site. From the main loop: ` +
    `\`python3 tools/conform.py ${scratch} --lang ${lang}\` must report zero blocking, then ` +
    `dry-run \`python3 tools/apply_translations.py ${scratch} --lang ${lang}\`, read it, and ` +
    `only then add --write. Capsule first unless told otherwise. Fold the reconciled terms ` +
    `into data/glossary/${lang}.yaml so the next pass does not decide them again.`,
}
