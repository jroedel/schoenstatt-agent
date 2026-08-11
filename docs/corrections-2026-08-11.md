# Corrections applied to production, 2026-08-11

The first pass made under the rule the maintainer set the same day — *"I'm fine with you improving
previous translations now that we have history if you're reasonably certain"* — and the first
writes on this site to leave a recoverable trail. Every one carries a `_note` and every one is
readable at `GET /api/v3/phrases/{id}/history`.

**21 applied. 12 candidates held back.** The held-back list is the more useful half of this
document, because each entry names a class of thing this tooling finds and must not act on.

16 came from `hunt_lexical.py`, below. **Five more came from translating** — see
[`pt-pass-2026-08-11.md`](pt-pass-2026-08-11.md) — and they are a different and more
interesting kind, because no lexical check could have found them:

| phrase | language | was | now |
|---|---|---|---|
| `Lyricist(s)` | es | `Compositor(es)` — identical to `Composer(s)` | `Letrista(s)` |
| `Subedition(s)` | es | `Otras ediciones` — identical to `Other editions` | `Subedición(es)` |
| `Main publication (…)` | es | `Publicación actual` — *current*, not main | `Publicación principal (…)` |
| `Show editions separately?` | es | `¿Mostrar ediciones obsoletas?` | `¿Mostrar ediciones por separado?` |
| `Branch moderator` | pt | `Assessor` — dropped the branch | `Assessor de ramo` |

Three of those are **collapsed pairs**: two distinct source strings sharing one translation
inside a text domain, so a form showed the same label for two different fields. Every spelling
is correct, so no dictionary finds them; what finds them is reading a screen's strings together.
Two turning up in one session is enough to want the check written — **a script that reports two
source strings sharing a translation within a domain does not exist yet, and should.**

The `Branch moderator` entry is drift this session created: the new row was written better than
the old one, and both had to be set to the same value afterwards. Worth noting as a cost of the
looser rule — improving one row of a pair obliges you to improve the other.

## Applied

All found by `tools/hunt_lexical.py` against production, all written with
`tools/apply_corrections.py`, which asserts the current value before replacing it.

### Spanish — unpaired question and exclamation marks (12 rows)

Spanish requires an opener for every closer. These rows had only the closing mark. It is
orthography, not preference.

| id | was | now | where |
|---|---|---|---|
| 7004 | `Eventos?` | `¿Eventos?` | `shrines` |
| 7005 | `Nombre traducido?` | `¿Nombre traducido?` | `shrines` |
| 7003 | `Horario de apertura?` | `¿Horario de apertura?` | `shrines` |
| 6679 | `No registrado?` | `¿No registrado?` | `zfcuser/login` |
| 5546 | `Teléfono móvil tiene WhatsApp?` | `¿…?` | `persons/create` |
| 5698 | `Interno para los Padres de Schoenstatt?` | `¿…?` | `publications/create` |
| 7074, 7082 | `Publicación de la nueva app … para Android!` | `¡…!` | `welcome`, `sion-model/view-changes` |
| 12957, 7037 | `Gracias a Matías Fortuño … inicial!` | `¡…!` | `shrines.locale`, `shrines` |
| 6756 | `Gracias por crear una cuenta … Link!` | `¡…!` | `juser/thanks` |
| 6946 | `Sé lo más descriptivo posible … año!` | `¡…!` | `associations/association/edit` |

Two pairs there — 7074/7082 and 12957/7037 — are the same source string in different text
domains. Both members of each pair got the identical value, per the rule that paired rows must
not drift.

6756 and 6946 were **not** auto-proposed by the tool, deliberately: their `!` closes a clause
in mid-string rather than ending it, and where the opener goes is then a judgement. In both
cases the exclamatory clause is the first sentence, so the opener belongs at position 0. That
was checked by reading them, not inferred.

### Spanish — misspellings attested against the movement's own books (3 rows)

| id | was | now | evidence |
|---|---|---|---|
| 6189 | `contínuamente` | `continuamente` | 0 occurrences against 74, in 231,574 words of Spanish |
| 5414 | `pertenencia perpétua` | `pertenencia perpetua` | 0 against 7 |
| 5531 | `Comunidad perpétua` | `Comunidad perpetua` | 0 against 7 |

### Portuguese — one shrine name, two defects (1 row)

**6864**, key `Coenaculum-Heiligtum`: `Santuário de Cenaculo` → **`Santuário do Cenáculo`**.
The accent is attested 22 times and its absence 0; and the Cenacle takes the definite article,
as both siblings have it — es `Santuario del Cenáculo`, it `Santuario del Cenacolo`.

## Held back, and why

### 1. Not our layer: defects in association record content (2 rows, 5 defects)

`PublicNotes` is translated by design — see the maintainers' reply §6 — so for a
Spanish-language shrine note the `es` row *is* the source text. Correcting it here would make
the Spanish page disagree with the record while leaving the typo everywhere else.

- **7285** (`association-edit`, the Ballester shrine's public notes): `calido` → `cálido`,
  ` pagina` → `página`, and the all-caps headings `ADORACION`, `SANTISIMO`, `MIERCOLES`,
  `Sabados` missing accents.
- **6978** (`associations/association`, a Chilean school network): `Colegio Pablo Apostol` →
  `Apóstol`.

**These should be fixed on the association records**, by a moderator or by whoever maintains
those shrines. Worth passing on.

### 2. Proper names the corpus mistakes for misspellings (4 rows)

- **6831, 7027** `Magnificat` → `magníficat`. Latin, and the name of the shrine and of Tabor
  Magnificat. The Spanish common noun takes an accent; the name does not.
- **6545** `Berlin-Frohnau` → `Berlín-Frohnau`. Spanish writes `Berlín`, but this is a German
  district name inside a shrine name. Genuinely arguable, which is why it is here.
- **5421, 7261** (German) `María Ayuda`, `z. B. María de la Alianza`. Spanish text quoted
  inside German rows; correct as they stand.

### 3. A charism role name the sources cannot settle (2 rows)

**6244, 6221** `Branch moderator` → German `Geistlicher Begleiter (Schwester, Priester,
Pater)`. Two things are demonstrably wrong with it: the parenthetical enumeration is not in
the source, and German is the only language that drops the *branch* element —

| en | es | pt | it | de |
|---|---|---|---|---|
| `Branch moderator` | `Asesor de rama` | `Assessor` | `Moderatore di ramo` | `Geistlicher Begleiter (Schwester, Priester, Pater)` |

But the German corpus attests **none** of the candidate repairs: `Moderator` 0,
`Zweigmoderator` 0, `Zweigleiter` 0, `geistlicher Begleiter` 0, `des Zweigs`/`des Zweiges` 0
in 1.85M words. `Zweig` itself occurs 84 times and `geistliche Begleitung` 16.

So the defect is certain and the repair is not. **To the German review queue**, with this
evidence, rather than to production. It is also worth noting that this row is ours — written
2026-08-10 by this tooling — and that `conform.py`'s length check is what caught it, at 50
characters against a 16-character source.

### 4. Not a correction at all: house decisions (77 findings, unchanged)

The 54 Spanish and 23 German editorial findings from the 2026-08-10 revise runs still need a
decision rather than a fix: `Schönstatt` vs `Schoenstatt`, `du` vs `Sie`, `Edition` vs
`Auflage`, German `Login` left untranslated beside `Abmelden`. "Reasonably certain" is not
available to an agent about a consistency policy affecting hundreds of rows.

Likewise the two items the maintainers' reply §9 assigns to us but which turn on what a
community is *called* — `Ladies of Schoenstatt` and `Madrugadores of %s` — remain open. On the
first, the reply and the Portuguese books disagree with each other; that disagreement is the
finding.

## What the pass taught the tooling

`hunt_lexical.py` produced false positives of four kinds today. Three are now filtered and the
fourth cannot be, which is the important one.

| class | example | fixed? |
|---|---|---|
| proper names | `Magnificat`, `Berlin-Frohnau`, `Santa Ana` | downgraded to `medium`, not suppressed — `Cenaculo` was real |
| enclitic pronouns | pt `publicá-la` tokenises as `publicá`, variant `pública` attested | filtered: a token followed by `-` is skipped |
| extraction noise | the OCR artefact `àñà` occurs 6× and folds to `ana`, accusing `Santa Ana` | filtered: a variant must use the language's own letters |
| **a real word the corpus never uses** | German `drucken` 0× against `drücken` 364× | **cannot be filtered** |

That last one is the sharpest warning available. `drucken` is ordinary German for *to print*;
`drücken` means *to press*. The corpus is Kentenich's theology, which has no occasion to
discuss printing labels — though `gedruckt` does occur 6 times, proving the stem is in the
vocabulary. The finding is reported at **high** confidence and applying it would have inverted
the meaning of a button on the library screens.

**So the corpus tells you what the movement writes about, not what the language contains.** It
is strong evidence for a charism term and weak evidence for a household verb, and German
suffers worst because it inflects and compounds most. Nothing from this tool may be applied
unverified.

Counts before and after the filters, against production:

| | before | after |
|---|---|---|
| Spanish | 11 variant + 12 punctuation + 2 truncated + 4 doubled + 8 bleed | 7 variant + 12 punctuation |
| Portuguese | 4 variant | 1 variant |
| German | 4 variant | 4 variant (all four false, none filterable) |

The `truncated`, `doubled-word` and `bleed` rules went to **zero false positives and zero
findings** — every hit they had ever produced was wrong. `truncated` had proposed
`Fecha de inicio` → `Fecha de inicios` and `Cor unum in Patre` → `in patres`; `doubled-word`
was reading `<strong>` twice in `<strong>%s</strong>`; `bleed` was flagging `P.`, `Doctor`,
`Rector` and `Lo Barnechea`, each of which is the same word in both languages.

One regression was introduced and caught during the same session: a rewrite of the
doubled-word check reused the variable `toks`, which the lexical pass iterates, so the lexical
pass silently began scanning only the last fragment of each value and six real findings
disappeared. It was found by checking that known defects still appeared — not by reading the
counts, which merely looked tidier.

## The corpus is moving

Worth recording because it invalidates every cached number in this repository:

| | phrases |
|---|---|
| 2026-08-10 | 1,798 |
| 2026-08-11, after the deploy | 1,757 |
| 2026-08-11, a few hours later | **1,917** |

The drop is §7's retirements. The rise is the discovery fix: phrase discovery was dead on
every Symfony-served route, so a missing phrase was queued and thrown away, and now it is
recorded. **+160 rows arrived during one working session**, simply because pages were being
rendered. Coverage rose too — es, de, it and pt each gained 23–27 translations that nobody
wrote, because a duplicate row arrives carrying the existing translations of the same text.

Consequences: the per-language gaps are now es 456, de 473, it 493, pt 736 before
classification; every worklist built before today is stale; and `classify.py` needs a run over
the new rows. Closing a gap is now a moving target rather than a finite list.
