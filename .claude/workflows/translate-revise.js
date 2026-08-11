export const meta = {
  name: 'translate-revise',
  description: 'Audit a language\'s existing translations for real defects and propose corrections. Two judgement lenses, then batched adversarial verification. Produces files; writes nothing.',
  whenToUse: 'When a language already has translations and you want the wrong ones found — not when filling empty rows, which is translate-bulk. Run tools/hunt_lexical.py first; this workflow expects its findings file.',
  phases: [
    { title: 'Hunt', detail: 'the two lenses a script cannot do' },
    { title: 'Verify', detail: 'two skeptics per batch, both must decline to refute' },
  ],
}

// args: { lang, scratch, corpus, glossary, style, cap }
//
// PREREQUISITE, run from the main loop before launching this:
//     python3 tools/extract_reading_material.py --lang <lang> --out <scratch>/<lang>_text
//     python3 tools/hunt_lexical.py <scratch> --lang <lang>
// The second writes <scratch>/<lang>_mech_findings.json, which this workflow requires.
//
// This workflow PROPOSES. It writes files and returns a report. **It does not touch the
// site.** Corrections overwrite text somebody wrote, permanently — `trans_translations` has
// no history — and that is not a decision a subagent gets to make.
//
// ---------------------------------------------------------------------------------------
// This workflow's first version cost 364 agents and exhausted an organisation's monthly
// spend limit, killing three unrelated runs. It found 119 English candidates and refuted 95
// of them. Both halves of that are the design input: the verification was doing real work,
// and the way it was arranged was indefensible.
//
// Three things changed.
//
// **1. The mechanical lenses are a script now, not agents.** Every correction actually
// applied to production on 2026-08-10 — twenty Spanish, two German — was of one kind:
// `exitósamente`, `coleción`, `Volúmen`, `Santisima`, `Arcangel`, `Pais`, `¡Foto?`,
// `Strasse`. Six agents hunted for those. `tools/hunt_lexical.py` finds them by checking
// each word against the movement's own books — a word absent from 231k words of edited
// Spanish whose accent variant occurs 74 times is a misspelling, and that is evidence rather
// than an opinion. Run against Spanish it independently rediscovered the corrections that
// pass had applied, plus `contínuamente`, `perpétua`, `calido`, `Linea` and `ADORACION` that
// six agents had missed. Cost: no agents at all.
//
// **2. Verification is batched.** It was one agent per skeptic per finding: 119 findings x 3
// = 357. But a skeptic's expensive context is the glossary, the style guide and the corpus —
// all of which are identical for every finding in the language. Loading them once and judging
// twenty-five findings costs a fraction of loading them twenty-five times. Independence is
// preserved where it matters: the two skeptics never see each other, and each renders a
// separate verdict per item with its own evidence.
//
// **3. Two skeptics, and BOTH must decline to refute.** Fewer agents and a *stricter* filter
// at once: majority-of-three let a finding through on 2-1, unanimity-of-two does not. For an
// irreversible write, refusing a real fix costs a re-run and accepting a wrong one costs the
// text. Those are not symmetric, so the tie does not go to the proposal.
//
// What is left for agents is the two lenses no script can do, and judgement.

const A = typeof args === 'string' ? JSON.parse(args) : (args || {})
const { lang, scratch, corpus, glossary, style } = A
if (!lang || !scratch) {
  throw new Error(`translate-revise needs {lang, scratch, glossary, style}; got ` +
    `${JSON.stringify({ lang, scratch })}`)
}
const MECH = `${scratch}/${lang}_mech_findings.json`
// A finding list whose size is set by an upstream count needs its cap written down in the
// same breath as the fan-out. This one is generous because a batch is cheap; what it must
// never be is absent.
const CAP = A.cap || 60
const BATCH = 25

const COMMON = `
You are auditing schoenstatt.link's existing ${lang} translations for a public reference
database about Schoenstatt.

READ THESE FIRST, in full — repo-relative paths, and the repository root is your working
directory:
  .claude/skills/schoenstatt-translation/SKILL.md   the method and its rules
  ${glossary}    the agreed term renderings for ${lang}, with the evidence
  ${style}       register, variant, and what stays in English
${corpus ? `  ${corpus}    the movement's own books in ${lang}, extracted — your best evidence\n` : ''}
**A correction destroys the version it replaces.** Since 2026-08-11 that version is readable
again at \`GET /api/v3/phrases/{id}/history\`, so a mistake found later can be reverted — but
only by somebody who notices, and a plausible mistranslation into a language nobody in the
session reads is exactly what nobody notices. The bar is therefore unchanged: not "could be
better", but "is demonstrably wrong". Do not report:
  - Proper names, place names, URLs, ISBN, Blog, Wikipedia, language codes left as-is
  - A translation identical to the English key where that is the right answer
  - A concise translation that is shorter than the English
  - Register or house-style choices you merely disagree with
  - Terms the glossary settles differently from your instinct — the glossary won
Report something only if you can say concretely what is wrong with it.

**Do not hunt for misspellings, missing accents, lost placeholders, doubled words or values
copied verbatim from another language.** A script has already done that pass over every row
— ${MECH} — far more exhaustively than you can, and duplicating it wastes the run. Your
value is entirely in what it cannot see.
`

phase('Hunt')

// Six lenses became two, because four of them were mechanical. These two are not:
// one needs a rendered page and the other needs to know what the movement calls things.
const LENSES = [
  { key: 'in-context', brief: `**Fetch real pages and read them.** Use
    https://schoenstatt.link with the /${lang}/ prefix and a Cookie of
    EU_COOKIE_LAW_CONSENT=true. Look for ${lang} text that is wrong, awkward, truncated in
    its element, or obviously foreign in the rendered page — navigation, headings, table
    columns, buttons, form labels, validation messages.

    This lens earns its cost because it sees what no query can. It is the one that found
    "Literatur" — the German word — sitting in the Portuguese main navigation of every page
    on the site. The row was not empty and its value was a real word, so nothing but looking
    at the page would have caught it.

    Also judge fit: a label correct in isolation can still be wrong in its element. A button
    wants an imperative, a column header wants a noun, and a string that overflows its column
    is a defect even when the words are right.

    Start with /${lang}/, /${lang}/shrines, /${lang}/literature, /${lang}/user/register, a
    shrine detail page and a publications listing. Go where the site leads you.` },

  { key: 'charism', brief: `**The vocabulary of the movement, and the register.** You are
    looking for values that are ordinary ${lang} but wrong *here*: a charism term rendered by
    its dictionary meaning instead of the movement's own word, a community or branch name in
    a shape the movement does not use, a doctrinal term flattened.

    Your evidence is the movement's own publications in ${lang}${corpus ? ` (${corpus})` : ''}
    and its own pages, then ${glossary}. A term the books use 800 times is what the movement
    calls the thing, whatever a dictionary says. Where the site renders one charism term two
    different ways across rows, that inconsistency is itself the finding — and the one that is
    wrong is usually the one the books do not attest.

    Check the register against ${style} too: formal against informal address, imperative
    against infinitive in the same kind of control, a heading pluralized on one screen and not
    the next. Report only breaks that are systematic enough to matter, not single wobbles.

    A real false positive to calibrate against: Portuguese "Santuário Missioneiro" looks like
    a misspelling of "missionário", but it is the regional adjective for the Guarani missions
    of Rio Grande do Sul, where that shrine is. It was correctly left alone.` },
]

const found = await parallel(LENSES.map(l => () =>
  agent(`${COMMON}

Your lens is **${l.key}**:
${l.brief}

Read ${MECH} first, and only to avoid repeating it — every phrase id in it has already been
found. Do not re-report those rows unless you have a *different* defect in the same row.

**Write your findings to ${scratch}/${lang}_hunt_${l.key}.json before you return**, as
{"lens": "${l.key}", "findings": [ ... ]}. Write the file even if you found nothing. This is
not busywork: the run journal truncates long returns, so a finding that exists only in your
return value is lost if a later phase dies — which is exactly how a 79-agent run of this
workflow lost every survivor it had.

Then return {"findings": [{"phrase_id": <int>, "source": "<the key>", "current": "<what
${lang} says now>", "proposed": "<what it should say>", "why": "<the concrete defect, and
your evidence>", "confidence": "high"|"medium"|"low"}]}

Be thorough within your lens and silent outside it. An empty findings list is a fine answer.`,
    { label: `hunt:${l.key}`, phase: 'Hunt', schema: {
        type: 'object', required: ['findings'],
        properties: { findings: { type: 'array', items: {
          type: 'object',
          required: ['phrase_id', 'source', 'current', 'proposed', 'why', 'confidence'],
          properties: {
            phrase_id: { type: 'integer' }, source: { type: 'string' },
            current: { type: 'string' }, proposed: { type: 'string' },
            why: { type: 'string' },
            confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
          } } } },
      } })
)).then(rs => rs.filter(Boolean))

// A barrier is right here: findings must be merged and deduplicated across the script's pass
// and both lenses before verification, or one row gets verified twice.
const agentFindings = found.flatMap(r => r.findings || [])
log(`${agentFindings.length} findings from ${found.length} judgement lenses; ` +
    `the mechanical pass in ${MECH} is merged in by the verifiers`)

const byId = new Map()
for (const f of agentFindings) {
  if (!byId.has(`${f.phrase_id}`)) byId.set(`${f.phrase_id}`, f)
}
const RANK = { high: 0, medium: 1, low: 2 }
const deduped = [...byId.values()].sort((a, b) => (RANK[a.confidence] ?? 3) - (RANK[b.confidence] ?? 3))
const toVerify = deduped.slice(0, CAP)
const deferred = deduped.slice(CAP)
if (deferred.length) {
  log(`verifying the ${toVerify.length} highest-confidence; DEFERRING ${deferred.length} ` +
      `unverified — they are in the return value, not silently gone`)
}

if (!toVerify.length) {
  return {
    language: lang, agents: found.length,
    findings: 0,
    note: `The judgement lenses found nothing. The mechanical findings in ${MECH} still need ` +
          `review — read that file; it does not go through this workflow's verification when ` +
          `there is nothing to batch it with.`,
  }
}

phase('Verify')

// Batches, not findings, are the unit of fan-out. Each skeptic loads the glossary, the style
// guide and the corpus once and judges up to BATCH findings against them, rendering a separate
// verdict per item. Agents = ceil(findings / BATCH) x 2, so this phase cannot run away.
const batches = []
for (let i = 0; i < toVerify.length; i += BATCH) batches.push(toVerify.slice(i, i + BATCH))

const SKEPTICS = [
  { n: 0, angle: `Is the claim TRUE? Check each row still holds what the claim says it holds,
    and that the defect is real in the language — not a regionalism, not an accepted synonym,
    not a proper name, not a deliberate house choice.` },
  { n: 1, angle: `Is this a style preference dressed up as an error, and is the PROPOSAL
    actually right? A fix that introduces a new error, contradicts the glossary, or merely
    swaps one acceptable rendering for another is a refusal. Judge the proposal as harshly as
    the claim.` },
]

const verdicts = await pipeline(
  batches,
  (batch, _orig, bi) => parallel(SKEPTICS.map(s => () =>
    agent(`${COMMON}

A previous pass claims each of the ${batch.length} ${lang} translations below is WRONG.
**Your job is to refute those claims.** Default to refuted: call something a real error only
if you can confirm the defect yourself, from the corpus and the sources.

${s.angle}

Verify them one at a time and independently — a run of confirmations is not a reason to
confirm the next one, and a run of refusals is not a reason to refuse it.

${batch.map(f => `--- phrase id ${f.phrase_id}
  source key: ${JSON.stringify(f.source)}
  current   : ${JSON.stringify(f.current)}
  proposed  : ${JSON.stringify(f.proposed)}
  claim     : ${f.why}`).join('\n')}

Also read ${MECH} and check it for the same phrase ids — the script may already have evidence
about these rows (a word's count in the corpus, for instance), and that evidence is stronger
than an impression.

**Write your verdicts to ${scratch}/${lang}_verify_b${bi}_s${s.n}.json before you return**, as
{"batch": ${bi}, "skeptic": ${s.n}, "verdicts": [ ... ]}. The file is the durable copy: the
phase that produces data owns writing it down, because a return value that only exists in the
journal is truncated there and lost.

Then return {"verdicts": [{"phrase_id": <int>, "refuted": true|false, "reason": "<one or two
sentences, naming your evidence>", "better_proposal": "<a different fix if BOTH the current
and the proposed are wrong, else empty string>"}]}

**One verdict per phrase id above, every one of them, each carrying its own phrase_id.** A
verdict that does not carry its subject cannot be matched back to it if a later phase dies —
which is exactly what happened on the first real run: 79 agents' work was unrecoverable
because the verdicts had no ids in them. A phrase id you omit is treated as unverified and
its finding is dropped.`,
      { label: `verify:b${bi}:s${s.n}`, phase: 'Verify', schema: {
          type: 'object', required: ['verdicts'],
          properties: { verdicts: { type: 'array', items: {
            type: 'object', required: ['phrase_id', 'refuted', 'reason', 'better_proposal'],
            properties: {
              phrase_id: { type: 'integer' }, refuted: { type: 'boolean' },
              reason: { type: 'string' }, better_proposal: { type: 'string' },
            } } } },
        } })
  ))
)

// Fail closed. A finding survives only if BOTH skeptics returned a verdict for it and NEITHER
// refuted it. A missing verdict is not a pass — an agent that died, or that skipped an item,
// must not thereby promote a correction to a production write.
const votes = new Map()
for (const pair of verdicts) {
  for (const skeptic of (pair || []).filter(Boolean)) {
    for (const v of skeptic.verdicts || []) {
      if (!votes.has(v.phrase_id)) votes.set(v.phrase_id, [])
      votes.get(v.phrase_id).push(v)
    }
  }
}

const judged = toVerify.map(f => {
  const vs = votes.get(f.phrase_id) || []
  const against = vs.filter(v => v.refuted)
  return {
    ...f,
    votes: vs.length,
    refuted_by: against.length,
    survives: vs.length >= SKEPTICS.length && against.length === 0,
    reasons: vs.map(v => v.reason),
    better: vs.map(v => v.better_proposal).find(x => x && x.trim()) || '',
  }
})
const survivors = judged.filter(v => v.survives)
const unverified = judged.filter(v => v.votes < SKEPTICS.length)
log(`${survivors.length} of ${judged.length} findings survived two skeptics` +
    (unverified.length ? `; ${unverified.length} got fewer than ${SKEPTICS.length} verdicts ` +
      `and are treated as NOT verified` : ''))

// There is no `propose` agent and no `checkpoint` agent, and both absences are deliberate.
//
// The first version had one final agent that was the only thing writing to disk; it died on
// the spend limit and took a 79-agent run's entire output with it, three times. The reflex fix
// was a checkpoint agent that wrote the state before `propose` ran — but that is still an
// agent, and it was still the single point of failure, just an earlier one.
//
// Durability belongs to the phase that produces the data. Every hunt agent writes its own
// findings file and every verify agent writes its own verdicts file, so the survivors can be
// reconstructed from disk by the main loop even if this script dies mid-pipeline. And what
// this returns is returned at the TOP LEVEL, which the harness stores intact — that is not a
// guess, it is how 74 Spanish and 25 German findings were recovered from the run that lost
// everything else. Two independent copies, neither of them an agent.
//
// The document a person reads is built afterwards, from the main loop, by
// tools/build_review_queue.py. Formatting is not a thing to spend an agent on.

return {
  language: lang,
  agents: found.length + batches.length * SKEPTICS.length,
  mechanical_findings: MECH,
  candidates: deduped.length,
  verified: judged.length,
  survivors: survivors.length,
  survivors_detail: survivors,
  refuted: judged.filter(v => !v.survives && v.votes >= SKEPTICS.length),
  unverified,
  deferred,
  files: [`${scratch}/${lang}_hunt_*.json`, `${scratch}/${lang}_verify_b*_s*.json`],
  next_step: `Nothing has been written to the site. From the main loop:\n` +
    `1. Read ${MECH} — the mechanical findings did not pass through this verification unless ` +
    `a lens re-raised them. The strong kinds (variant-attested, paired-punctuation, ` +
    `placeholder) carry their own evidence; proper names are their one false-positive class.\n` +
    `2. The survivors are in this return value, and reconstructible from ` +
    `${scratch}/${lang}_verify_b*_s*.json if it is lost.\n` +
    `3. Corrections need the user to have asked for them — filling an empty row and ` +
    `rewriting somebody's text are different acts. Then ` +
    `\`python3 tools/apply_corrections.py\`, which asserts the current value before ` +
    `replacing it and refuses if the row has moved.\n` +
    `4. \`python3 tools/build_review_queue.py ${scratch} --lang ${lang}\` for the judgement ` +
    `calls a native speaker should see.`,
}
