# German — orthography, register, and the fact that German is the original

Decisions made while translating, with the evidence. Verified 2026-08-10 against production
and the sources in [`../glossary/de.yaml`](../glossary/de.yaml).

## German is not a translation here — it is usually the original

The charism's vocabulary was coined in German: `Liebesbündnis`, `Gnadenkapital`,
`Urheiligtum`, `Werktagsheiligkeit`, `Vorsehungsglaube`, `Blankovollmacht`. When the German
row differs from the English key, **the German is more likely to be right than the key is**.

So the job for German is mostly filling gaps and standardising between two attested German
forms — not deciding what a term means. Do not "improve" an existing German term toward the
English.

## Settled: German is `Schönstatt`, with the umlaut

**The maintainer decided this on 2026-08-11: "Schönstatt in German".** It was the largest open
question in this file and it is now closed. Write `Schönstatt` in German. Do not drift back,
and do not "harmonise" a German row toward the `Schoenstatt` in its own phrase key.

The evidence already pointed this way — the books write `Schönstatt` 2,935 times against
`Schoenstatt` 1,167 — but the site's German mixed the two freely (`Schönstatt-Heiligtum`
beside `Schoenstatt Patres`), and consistency across dozens of rows is a house decision rather
than a translation one.

**The decision is about German, and only about German.** `Schoenstatt` stays exactly as it is
in the Italian, Spanish, Portuguese and English rows — `Santuario di Schoenstatt`,
`Padres de Schoenstatt` — and in every phrase *key*, which is a lookup string and read-only.

### What does not take the umlaut, even in a German row

Four kinds of thing, and the reason is the same each time: it is a name somebody else owns, or
a string a machine reads, not the movement's name in German prose.

| | |
|---|---|
| **`Schoenstatt Link`** | the site's own name. es, pt and de all keep it verbatim, and the site is literally `schoenstatt.link`. Eight rows plus the registration emails |
| **Non-German bodies' registered names** | `Santuario Schoenstatt Villa Ballester` in a postal-address block; `Schoenstatt of Ohio`; `Editorial Patris` |
| **URLs, domains and email addresses** | `schoenstatt.org`, `schoenstatt.ch`, `schoenstatt-info.com`, `facebook.com/SchoenstattBallester`, `support@schoenstatt.link` |
| **Literal strings the reader must copy** | the Waze search term `„La Ermita. Mov. Schoenstatt. Dulce Nombre, La Unión."`; the app-store title `(Schoenstatt Shrines)` |

The **adjective already needed no work**: the existing German rows say `Schönstätter`
(`Säkularinstitut der Schönstätter Marienschwestern`) and `schönstättische`, never a digraph
form.

### The sweep this required

Counted on production on 2026-08-11: **23 occurrences of `Schoenstatt` across 21 German rows**,
of which **17 fall under the exclusions above** and 6 needed changing — three rows of
`Schoenstatt Patres, Florencio Varela`, two of `Heilegtum Schoenstatt`, and one form-help
example containing `"Schoenstatt-Bewegung von [Ortsname]"`.

Two of those six carry a second, independent fix, recorded here so it is not mistaken for part
of the orthographic decision:

- **`Schoenstatt Patres` → `Schönstatt-Patres`**, hyphenated. That is the form the site already
  uses, 24 rows to 23, and it is the rule two sections below.
- **`Heilegtum Schoenstatt` → `Schönstatt-Heiligtum`**. `Heilegtum` is a misspelling of
  `Heiligtum`, and the compound is what the table below already prescribes for this exact
  English key (`Schoenstatt Shrine`).

## Compounds, not prepositional phrases

German compounds where the Romance languages use `de`/`di`. Follow the corpus:

| | |
|---|---|
| Schoenstatt Shrine | **`Schönstatt-Heiligtum`** |
| Original Shrine | **`Urheiligtum`** — not `Ursprüngliches Heiligtum` |
| home shrine | **`Hausheiligtum`** |
| Family Federation | **`Familienbund`** |
| Mothers' Federation | **`Mütterbund`** |
| Sisters of Mary | **`Marienschwestern`** |
| Brothers of Mary | **`Marienbrüder`** |

Hyphenate after the proper name (`Schönstatt-Patres`, `Schönstatt-Bewegung`), compound
plain nouns solid (`Hausheiligtum`, `Gnadenkapital`).

## Settled: address the reader as *du*

**The maintainer decided this on 2026-08-11: "Let's be consistent with du over Sie. I hope it goes
with more of the youthful spirit of the site."** Use *du* in German. It brings German into line
with the other four languages, which are all informal (`tu`/`tú`/`você`), and it settles the
last of this file's open questions.

Before that decision the site's German was genuinely split — `Nimm Kontakt zu uns auf` and
`Hilf uns dabei` were *du*, while `Sind Sie ein Mensch?` and `Sie löschen nun %s` were *Sie* —
and an earlier version of this section told a translator to write `Sie` for administrative and
form text. That is now wrong. Do not follow it, and do not take an old `Sie` row as evidence.

### The sweep, and the four rows it must not touch

**61 rows converted on 2026-08-11**, out of 65 carrying a formal-looking marker. It is a
register change rather than a find-and-replace: verbs, possessives and reflexives move with the
pronoun.

| | |
|---|---|
| `Sie` (nom.) | **`du`**, and the verb to 2sg — `Sie erreichen` → `Du erreichst`, `Sie kommen` → `Du kommst` |
| `Sie` (acc.) | **`dich`** — `damit wir Sie empfangen` → `damit wir dich empfangen` |
| `Ihnen` | **`dir`** — `wir senden Ihnen` → `wir senden dir` |
| `Ihr`/`Ihre`/`Ihren`/`Ihrem` | **`dein`**-forms — `auf Ihren Namen` → `auf deinen Namen` |
| polite imperative | 2sg imperative — `Prüfen Sie` → `Prüfe`, `Nehmen Sie` → `Nimm`, `Geben Sie … ein` → `Gib … ein`, `Fahren Sie` → `Fahr`, `Vergeben Sie` → `Vergib` |
| reflexive | `melden Sie sich an` → `melde dich an`; `Sie müssen sich … merken` → `Du musst dir … merken` |
| `Guten Tag %s,` | **`Hallo %s,`** — the greeting has a register too, and the newer of the two sign-in emails already said `Hallo` |

**Four rows were deliberately left alone, and they are the whole risk in this change.** Their
`Sie` is not address at all — it is *it* or *she*:

| id | the text | what `Sie` means |
|---|---|---|
| 6427 | `Sie enthält außerdem eine gute Auswahl` | the library |
| 7086 | `Sie wird von Mitgliedern … organisiert` | die Missionsfahrt |
| 6989 | `Sie wurde am 30. Mai 1998 … gesegnet` | the shrine |
| 6987 | `Sie ist da, um sie zu hören` | Mary |

A fifth, **6573**, was converted only in part: `Verwenden Sie dieses Feld` → `Verwende dieses
Feld`, while the following `Sie wird auf die nächsten … Etiketten übernommen` stays, because
that `Sie` is the call number. A regex sweep would have written second-person address into all
five. **This is the reason the conversion was done row by row.**

### Buttons stay in the infinitive

The decision is about **prose addressed to the reader**, not about form controls. German
interfaces use the infinitive on a button whatever the register of the surrounding text, so the
table two sections below is unaffected: `Submit` is still `Bestätigen`, not `Bestätige`, and
`Search %s` is still `In %s suchen`. Do not "finish the job" on the labels.

## Nouns are capitalized — including in labels

Obvious, but it is the commonest mechanical error when translating from English labels:
`Postal address` → `Postadresse`, not `Postadresse` lowercased mid-phrase. Every noun in a
compound label takes a capital: `Gründungsdatum`, `Öffnungszeiten`, `Kontaktinformation`.

## Verbs in labels: infinitive, not imperative

Where Italian and Portuguese use the imperative for buttons, **German interfaces use the
infinitive**, and the site's existing rows do too. **The 2026-08-11 move to *du* does not change
this** — a du-register site still labels its buttons with an infinitive:

| | |
|---|---|
| `Submit` | **`Bestätigen`** |
| `Search %s` | **`In %s suchen`** |
| `Delete` | **`Löschen`** |
| `Cancel` | **`Abbrechen`** |
| `Import` | **`Importieren`** |

This is a real divergence from the Romance languages and should not be harmonised.

## What stays in English

`Blog`, `Fax`, `Link`/`Links`, `Token`, `URL`, `ISBN`, `Wikipedia`, `JSON`, `Media`,
`Creative Commons`, `Chord pro`, `LilyPond`, and proper or place names. German technical
usage takes these without translation.

`Password` → **`Passwort`** (unlike Italian, which keeps the English word).

## Where the site's German is already inconsistent

Recorded rather than resolved — each needs one decision across several rows.

- ~~**`Schönstatt` vs `Schoenstatt`**~~ — **settled 2026-08-11: `Schönstatt`.** See above.
- **`Schönstattpatres` vs `Schönstatt-Patres`** — 24 to 23 in the corpus, genuinely split.
  The site uses the hyphenated form; keep it.
- **`Liebesbündnis` vs `Liebesbund`** — 807 to 11 in the corpus, so `Liebesbündnis` should
  win, but the site has one shrine name using each.
- ~~**`du` vs `Sie`**~~ — **settled 2026-08-11: `du`**, and the 61 affected rows were converted.
  See above.

**Two of the four are now settled**, both on 2026-08-11: `Schönstatt` and `du`. What is left is
`Schönstattpatres` vs `Schönstatt-Patres` (where the site's own preference is clear enough to
follow) and the one shrine name using `Liebesbund`.

## Record prose is *du* as well, which resolves a divergence from Italian

For a few hours on 2026-08-11 this file said record prose — a shrine's own directions and
visiting notes — should take `Sie`, on the grounds that the Spanish and Portuguese siblings are
formal. Italian went the other way on the very same records, following its house *tu*, and the
two languages ended up addressing the same pilgrim differently.

**The `du` decision settles it in Italian's favour and the divergence is gone.** A shrine's
notice reads `Du erreichst das Schönstatt-Zentrum …`, `Bitte kündige deinen Besuch vorher an`,
`Frag einfach direkt die Anbetungsschwestern`.

Worth stating because it cuts against a rule elsewhere in this repository: several of those
records were *written by their shrine in formal Spanish or German*, and the German row now
departs from its author's register on purpose. Register is a house decision here, not a property
of the source string.

## Where a German source string had an empty German row

Four rows in that pass. The German written was **the key with its slips repaired**, not the key
copied verbatim: a missing subject pronoun in `Aktuell befindet sich in dem Haus`, the dative in
`wurde für … geschenkt`, `Schönstattzentrum` → `Schönstatt-Zentrum`, and an English tail on a
German row rendered into German.

The judgement was that an empty German row under a German key is a gap to fill rather than a
translation to preserve. A reviewer may prefer the untouched original, in which case those rows
revert to their key text — and this becomes a rule the other way, which is worth having either
way.
