# Italian — register, address forms, capitalization

Decisions actually made while translating, with the evidence that settled them. A rule
here means "this was chosen once, deliberately, and the next person should choose the
same way" — not "this is how Italian works". Where the site's own four other languages
already agreed on something, that agreement is the evidence and it is cited.

Everything below was verified against the capsule on 2026-08-10.

## Address the reader as *tu*

The site is informal in every language that marks it. Spanish uses *tú*
(`Ayúdanos`, `revísalo por favor`, `Contáctanos`), German uses *du*
(`Nimm Kontakt zu uns auf`, `Hilf uns dabei`), Portuguese uses *você*. Italian follows:
**`Contact us` → `Contattaci`**, not `Ci contatti`.

This is a movement's own site talking to its own people, and the informal register is
the house voice rather than an accident of whoever translated first — it is consistent
across three languages and dozens of strings.

## Imperatives for actions, not infinitives

A button or a link that performs an action takes the imperative:

| | |
|---|---|
| `Sign in` | **`Accedi`** — not `Accedere` |
| `Register` | **`Registrati`** |
| `Logout` | **`Esci`** |
| `Submit` | **`Conferma`** — following es `Confirmar`, pt `Confirmar`, de `Bestätigen`, which all say *confirm* rather than *send* |
| `Search %s` | **`Cerca in %s`** — not `Cercare a %s` |

`Cerca in %s` corrects an existing translation which rendered `Buscar en Colegio Mayor`
as `Cercare a Colegio Mayor`. Two faults: the infinitive where the site wants an
imperative, and `a` where a container takes `in`.

**Provenance, corrected.** An earlier version of this note called that a translation "of
this repository's own". It was not: on production, phrase 6652 was written by **user 104
on 2019-07-13**, years before any of this tooling existed. The capsule copy was rewritten
by the bot on 2026-08-10 and production on the same day, the latter only after the user
asked for it explicitly — overwriting a person's translation is a different act from
filling an empty row, and it is not covered by the standing permission to write.

`Accedi` was not invented — it was already the rendered label in the Italian site
chrome before any of this work, so the whole of the sign-in vocabulary was built to
match what was there.

## Months are lowercase

`gennaio`, `febbraio`, `marzo`, … `dicembre`. Italian does not capitalize month names.
Spanish agrees (`enero`, `abril`); German does not and cannot, because they are nouns.
Follow Italian, not the German column.

## What is left in English

- **`Home`** — kept, because Spanish and German both keep it. Translating it here would
  make Italian the only language that did.
- **`Password`** — the English word is the ordinary Italian one.
- **Proper names**: `Schoenstatt Link`, place names (`Aulendorf`, `Bellavista`,
  `Lo Barnechea`), URLs, and external service names (`Open Street Maps`) are copied
  verbatim. A translation identical to its key is still worth writing: it takes the
  phrase off the worklist, and it is what the other four languages did.
- **Technical loanwords Italian has adopted**: `Link`, `Token`, `Account`, `Blog`,
  `Fax`, `Media`, `Album`, `EBook`, `Graphic novel`, `kernel`, `debug`, `Tag`,
  `Controller`, `Locale`. Where Spanish translated one of these (`Enlaces`,
  `Controlador`, `NovelaGrafica`) Italian did not follow — Spanish is more resistant to
  English loanwords than Italian is, and following it here would produce stilted
  Italian. The four that are most arguable are on the review queue.
- **Latin that the movement keeps in Latin**: `Lumen Patris`, `Cor unum in Patre`,
  `Dilexit Ecclesiam`, `Mater Ter Admirabilis`, `Patres`. See the note on Latin shrine
  names below — the site is not consistent about this and neither, now, is Italian.

## Shrine names take `di`, not `de`

The commonest single pattern in this corpus. Spanish and Portuguese write
`Santuario/Santuário **de** Schoenstatt`; Italian takes **`di`** —
`Santuario di Schoenstatt`, `Santuari di Schoenstatt`, `Padri di Schoenstatt`,
`Movimento di Schoenstatt`, `Edicola di Schoenstatt`. Where a Spanish key already
contains `de` and is being rendered into Italian, the preposition changes with the rest
of the phrase: `Santuario de Schoenstatt Asunción` → `Santuario di Schoenstatt Asunción`.

Place names inside such a name stay as they are: `Santuario di La Loma`, not
`Santuario della Loma`.

## Latin shrine names — the site is inconsistent and Italian inherited it

Some shrines have Latin names that every language translates (`Via ad Patrem
Misericordem` → `Camino al Padre Misericordioso` in Spanish) and some that every
language keeps (`Cor unum in Patre`, `Dilexit Ecclesiam`). There is no rule behind the
split; it is whatever each translator did first.

Italian followed the siblings case by case, which reproduces the inconsistency rather
than fixing it. **This is flagged rather than resolved** — deciding it means deciding it
for all five languages at once, which is not a translation decision. The affected names
are on the review queue: `Victoria Patris`, `Providentia`, `Ver Sacrum Marianum`,
`Via ad Patrem Misericordem`.

## Language names are translated; language codes are not

Two families of phrase look alike and are handled oppositely.

- **Codes** — `de`, `en`, `es`, `pt` exist as phrases in the `default` domain and every
  one of the four other languages renders them **unchanged**. Italian does the same.
- **Names** — `German`, `Inglés`, `Tedesco`, `Portugiesisch` are the *values* of a
  publication's language field, and the key is in whatever language the record was
  entered in. All of them get the Italian name: `Tedesco`, `Inglese`, `Portoghese`,
  `Spagnolo`, `Francese`, `Polacco`, `Ceco`, `Croato`, `Ungherese`, `Latino`,
  `Italiano`. Several keys are *already* Italian (`Inglese`, `Tedesco`) and are written
  verbatim.

## Placeholder and example text is localized

`ex. John Andrew` → `es. Mario Andrea`; `ex. Smith Johnson` → `es. Rossi Bianchi`;
`ex. fr_johnsmith` → `es. p_mariorossi`; `you@example.com` → `tu@esempio.com`. Spanish,
Portuguese and German all localize these, and the point of an example is that it looks
native.

**`ex.` becomes `es.`** (*esempio*), not `p. es.` — shorter, and it is what fits a form
hint.

Two exceptions, both deliberate: real song titles used as examples
(`ex. María de la Alianza`) keep their own language, because they are titles rather than
invented placeholders; and coordinates, ISBNs and dates are not language.

## Where Italian forces a gender that English does not

English `Dear %s,` and `Welcome` say nothing about who is reading. Italian must choose.
The decisions made here, all on the review queue because they are the reader-facing ones:

- **`Dear %s,` → `Caro %s,`** — masculine, following es `Querido`, pt `Querido`,
  de `Lieber`. All three siblings chose masculine.
- **`Welcome` in the registration emails → `Benvenuto/a`**, and
  `registered` → `registrato/a`. The slashed form avoids assuming, and is ordinary in
  Italian institutional writing.

These two are inconsistent with each other — one picks a gender, one refuses to. That is
worth settling, and it is why both are flagged.

## Library terminology, standardized once

The library module is the largest block of interface text, and Italian librarianship has
settled terms that are not literal translations of the English:

| | |
|---|---|
| `Call number` | **`Collocazione`** — not `Numero di catalogo`. Used consistently across all eight `Call number …` strings |
| `Publisher` | **`Editore`** |
| `Editor(s)` | **`Curatore(i)`** — *not* `Editore`, which would collide with `Publisher`. Spanish uses `Editor` for both; Italian cannot |
| `Paperback` | **`Brossura`** |
| `Hardcover` | **`Copertina rigida`** |
| `Checkout` (noun) | **`prestito`**; `check in` → **`restituire`** |

The `Editore` / `Curatore` distinction is the one that matters: conflating them, as the
Spanish rows do, makes a bibliographic record ambiguous in Italian.

## Placeholders

`%s` and `%1$s`-style placeholders are part of the string and must survive intact, in a
position the sentence still works in. `Search %s` → `Cerca in %s` moves nothing;
where Italian word order forces a move, use the numbered form rather than reordering
bare `%s` tokens.

## Where the source string is not English

164 phrases have a non-English source key. Translate from the **key**, because the key
is the phrase — but read the other languages first, because the key is also the one
string nobody can edit, and it goes stale.

**Two cases, and they need opposite handling:**

- *The key is in another language.* `Buscar en Colegio Mayor` is Spanish. Translate the
  Spanish.
- *The key is stale English.* `Schoenstatt Link hopes to … by the end of 2018!` still
  has that deadline in the key, while the English, Spanish, Portuguese and German rows
  all say "on an ongoing basis". Here the key is a lookup string the site has moved
  past, and translating it faithfully would put a 2018 deadline into Italian alone.
  **When every other language agrees against the key, follow them and say so.**

The test that separates the two costs nothing: compare the key with its own English
row. Identical means the key is English and current. Different means either the key is
not English, or it is English that has been revised — and reading the two tells you
which.

## Record prose is not interface text, and the register question is open

The *tu* rule above was established on interface strings. The 2026-08-11 pass applied it to 29
rows of **association record prose** — a shrine's own directions, Mass times and visiting notes,
written by that shrine's people — and that is an extension rather than the same decision.

It matters because those sources are often emphatically formal. The Villa Ballester notice
(phrases 7285, 7468) is Spanish `lo espera`, `anticipe su visita`, `brindarle`; Portuguese kept
that formality. Italian here reads `questo luogo di accoglienza ti attende` — the house voice,
against the author's register.

**Flagged rather than settled**, and the German pass went the other way on the same paragraphs,
using `Sie`. So the two languages now disagree about the same records. One decision fixes both,
and it needs somebody to say whether a shrine's own notice keeps the register its author chose.

Two smaller decisions from the same rows, both on the review queue:

- **`a 10 isolati`** for Argentine `a 10 cuadras`. `isolato` is the standard Italian for a city
  block; `quadra` would be a borrowing.
- **A community's name is capitalized, a description of its members is not.** Row 14180 is
  `Sorelle dell'Adorazione`; 7198's prose reads `alle sorelle dell'adorazione`, following the
  English's own lowercase. The same rule put `capitale di grazie` lowercase in 6989 and
  `Capitale di Grazie` in 6988, because each follows its own source's casing — which may be the
  wrong rule.
