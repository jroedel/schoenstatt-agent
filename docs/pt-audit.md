# Audit of the existing Portuguese translations

Production held 719 Portuguese translations before this pass. **24 of them were wrong and
were corrected on 2026-08-10.** This document says which, why, and what was deliberately
left alone.

## Where Portuguese stands (2026-08-10)

| | |
|---|---|
| Portuguese before | 719 |
| Existing rows corrected | 24 |
| New translations written | 323 |
| **Portuguese now** | **1,042** of 1,795 |
| Left untranslated, documented skips | 375 |
| Still genuine work | **378 rows / 372 distinct strings** |

The pass is **unfinished and deliberately stopped part-way** rather than rushed: every row
written is on production and irreversible, and the remaining 372 strings are mostly the
publication and library forms, which want the same care. The method is in place —
`pt_units.json` and the `ptchunk_*.txt` files are the worklist, and the glossary and style
guide are written — so it resumes without re-deriving anything.

Corrections were applied with [`tools/apply_corrections.py`](../tools/apply_corrections.py),
which is the only path in this repository that overwrites an existing translation. It
refuses to write unless the row currently holds the exact string the correction expects,
so a stale list fails loudly instead of clobbering someone's later edit. All 24 matched;
none was refused.

**Overwriting is not covered by the standing permission to write.** Filling an empty row
and replacing somebody's text are different acts. These were done because the user asked
for them explicitly.

## The site declares pt_BR

The database keys this locale `pt_BR` and the compiled catalog is
`module/Schoenstatt/language/pt_BR.lang.php`. That matters, because a good deal of the
existing Portuguese was written in European Portuguese, and two of those differences are
not stylistic:

- **`Apelido` for `Last name`.** In Brazilian Portuguese `apelido` means *nickname*. A
  Brazilian filling that field types the wrong thing, so this is a data-quality bug rather
  than a register preference. → `Sobrenome`.
- **`Direção postal` for `Postal address`** and eight `Street line …` rows. `direção` is a
  calque of Spanish `dirección`; in Portuguese it means *direction*. Wrong in both
  variants. → `Endereço`.

The rest of the pt-PT forms are ordinary variant differences, corrected for consistency
with the declared locale: `utilizador` → `usuário` (5 rows), `contacto` → `contato` (2),
`Registo` → `Registro`, `palavra-passe` → `senha`, `registada` → `registrada`.

One of these was inconsistent with *itself*: **`Username` appears in five text domains,
and four already read `Usuário` while the fifth read `Utilizador`.**

## Spanish had bled into the Portuguese rows

Six rows contained Spanish. These are the clearest errors in the set, because nothing
about them is a judgement call.

| phrase | was | now |
|---|---|---|
| 6669 | `Disponibilidad de exemplares físicos` | `Disponibilidade de exemplares físicos` |
| 6829 | `Santuário de la Comunidad del Camino` | `Santuário da Comunidade do Caminho` |
| 5571 | `Persona criado com êxito.` | `Pessoa criada com sucesso.` |
| 7000 | `Estes datos … deseje reciber …` | `Estes dados … deseje receber …` |
| 6565 | `Codigorz de barra` | `Código de barras` |
| 5145 | `Contato principa` | `Contato principal` |

6829 is the worst of them: apart from the first word, the whole "translation" is Spanish.

## And German had bled in too — in the main navigation

`Literature` reads **`Literatur`** in both its Portuguese rows (7592, 6493). That is the
**German** translation of the same phrase, copied into the Portuguese row. Portuguese is
`Literatura`, which is also what Spanish has.

This one was in the **main navigation of every Portuguese page** — found by loading
`/pt/shrines` and reading the menu, not by any query. Corrected. `Music` beside it had no
Portuguese at all and is now `Música`.

So the copying went in more than one direction: Spanish into Portuguese, Spanish into
German, and German into Portuguese.

**5571 shows the mechanism.** Its Portuguese row read `Persona criado com êxito.` and its
**German** row reads `Person creado con éxito.` — Spanish in the German row. One string was
mis-copied across several languages at once, which suggests a bulk edit rather than a
translator's slip. **The German row is still wrong**; German is out of scope for this pass
and it is listed in [`api-change-requests.md`](api-change-requests.md) §9.

## Left alone deliberately

- **`Santuário Missioneiro` (7018).** `missioneiro` looks like a misspelling of
  `missionário`, and the Spanish row `Santuario Missionero` is misspelled. But in Rio
  Grande do Sul — where these books were published — *missioneiro* refers to the region of
  the Guarani missions, and this is a Brazilian shrine. It reads as deliberate. Not
  changed.
- **`Site` for `Website` (5142).** Ordinary Brazilian usage.
- **`schoenstattiano` vs `schoenstatiano`.** The site uses the two-`t` spelling
  throughout. The eleven Brazilian books prefer one `t`, 86 occurrences to 9. Both are
  attested in movement publications, the difference is orthographic, and rewriting 20-odd
  rows to match a book series' house style is not a translation improvement. Recorded in
  [`../data/glossary/pt.yaml`](../data/glossary/pt.yaml) so nobody "fixes" it in either
  direction by accident.
- **`União` for `Federation`.** Not a correction — a confirmation. The existing Portuguese
  says `União de Famílias`, `União de Mães`, `União Apostólica Feminina` where Spanish says
  `Federación`. The books show the existing Portuguese is **right**: `União Apostólica` is
  the tier's name and `Federação` does not occur once in 3.1 million characters. This is
  the clearest case in the whole project of the site's own translation beating the obvious
  inference from a sibling language.
- **`Bem-vind@s` and `ajuda-nos` (6999).** The `@` as a gender-neutral ending and the
  tu-imperative are register choices, not errors. Only the typo (`casa pessoa` →
  `cada pessoa`) and the pt-PT forms in that row were touched.
- **45 rows where Portuguese equals English.** Nearly all legitimate — proper names, place
  names, `ISBN`, `Blog`, `Wikipedia`, URLs. Two were real and were fixed:
  `City/State (post)` had never been translated, and `Logout` was left in English while
  Spanish and German translate it.

## The pattern behind almost all of it

**Nearly every error in this set came from copying a sibling language and only partly
converting it** — Spanish into Portuguese in six rows, German into Portuguese in two, and
Spanish into German in at least one. None of them looks like a translator's slip; they look
like bulk edits.

Two things follow. **German is likely to hold the same class of error** — it trails
Portuguese by one row and already shows the fingerprint in `Person successfully created.`.
And the reason this repository translates from the *key* and treats sibling languages as
evidence of convention rather than of wording is not fastidiousness: it is what these
twenty-four rows look like when that discipline is missing.
