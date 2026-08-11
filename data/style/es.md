# Spanish — register, and the responsibility of being the pivot language

Decisions made while translating, with the evidence. Verified 2026-08-10 against production
and the sources in [`../glossary/es.yaml`](../glossary/es.yaml).

## Spanish's errors propagate, so they cost more

Spanish is the best-covered language after English (1,209 of 1,795), which makes it the row
translators reach for when the English key is ambiguous. Every error found in the site's
Portuguese came from copying Spanish and half-converting it, and at least one Spanish error
was copied into **German** (`Person creado con éxito.` sits in the German column).

Two consequences. Spanish deserves the most careful audit of any language. And a Spanish row
that is merely *odd* rather than wrong should still be flagged, because oddness travels.

## Address the reader as *tú*

The house voice, consistent across the site's existing Spanish: `Ayúdanos`,
`revísalo por favor`, `Contáctanos`, `Empieza tu número`. Use the *tú* imperative.

| | |
|---|---|
| `Sign in` | **`Acceder`** |
| `Search %s` | **`Buscar en %s`** |
| `Submit` | **`Confirmar`** |
| `Delete` | **`Eliminar`** |

Spanish uses the **infinitive** for form controls (`Buscar`, `Confirmar`, `Eliminar`) and the
*tú* imperative for prose addressed to the reader (`Ayúdanos`). Both are house style; the
distinction is the grammatical role, not the register.

## Questions take opening marks

`¿Activo?`, `¿Quién tiene acceso?`, `¿Publicado formalmente?`. The site's existing Spanish
mostly does this and occasionally forgets — `Interno para los Padres de Schoenstatt?` is
missing its `¿`. Do not propagate the omission.

## `Federación`, and why it must not be harmonised

Spanish uses **`Federación`** for the apostolic federations — 104 occurrences in the corpus.
Portuguese uses `União` and German uses `Bund`, and **no two of the three agree**. This is
the standing proof in this project that a sibling language is never evidence for a term:
all three sites are right, and they differ.

Do not "fix" Spanish toward Portuguese or German, or either toward Spanish.

## The branch names as the site has them

The existing Spanish is coherent and should be followed rather than re-derived:
`Federación de Familias`, `Federación de Señoras` (note: `Señoras`, not `Madres`, unlike
Portuguese `Mães` and Italian `Madri`), `Liga de Familias`, `Juventud Femenina`,
`Instituto Secular Hermanas de María`, `Padres de Schoenstatt`.

`Federación de Señoras` for *Mothers' Federation* is a real divergence from the other
languages and is deliberate Spanish usage.

## What stays in English

`Blog`, `Fax`, `Email`, `Token`, `URL`, `ISBN`, `Wikipedia`, `Media`, `Creative Commons`,
and proper or place names. Note the site uses `Email` rather than `Correo electrónico`.

`Password` → **`Contraseña`**.

## Known defects in the existing Spanish

Found while auditing other languages, not yet corrected — Spanish corrections need the
user to ask, as any overwrite does:

- **`Santuario Missionero`** — should be `Misionero`. One `s`.
- **`Fedración de sacerdotes de %s`** — missing the `e` in `Federación`.
- **`antuario Nacional, Florencio Varela`** — the leading `S` is missing.
- **`Esta persona ya está en la sistema.`** — `en el sistema`.
- **`Sábado-Domingo 9 a 11 de la mañana…`** — renders `Sun-Sat` as Sat–Sun and drops the
  second time range; the key says something else.
- **`¿Mostrar ediciones obsoletas?`** for `Show editions separately?` — translates a
  different question from the one the key asks.
- **`Inst. Nuestra Señora de Schoenstatt`** for `Ladies of Schoenstatt` — **not** an error;
  the institute's formal name is *Our Lady of Schoenstatt*. Confirmed from the Portuguese
  and German sources. Do not "fix" it.

## When the source string is Spanish and the Spanish row is empty

Four rows in the 2026-08-11 pass were like this, and it is a real situation rather than a
contradiction: the key is what a moderator typed into an association record, and nobody had ever
filled the `es` translation of it.

**The decision made was to write the key with its errors repaired** — `anunaciar` → `anunciar`,
`esta` → `está`, a run-on split into sentences, `cañada` capitalized as a place name. No words
were changed and no register was converted.

The argument for repairing: the key is uneditable, it is what the site falls back to when the row
is empty, and writing the row is the **only** way the site ever shows corrected Spanish. The
argument against, which is not weak: it makes the Spanish row silently differ from what the
moderator wrote, and nobody reviewing the record would see why.

Two things this deliberately did **not** do, because they are larger changes than repairing a
typo:

- **The register was left as the author had it.** 7062 keeps `usted` (`debe ingresar`), 7090 keeps
  *tú* (`Entras`, `pides`) — so two shrine notices now differ from each other and from the house
  *tú*. A shrine addressing its own pilgrims is not interface text, and converting it would be
  rewriting rather than translating.
- **No fact was corrected.** Where a record says something that looks wrong — a Rosary at
  midnight on Saturday — the fix belongs on the association, not in five translations of it.

On the review queue as [`../../docs/es-review-2026-08-11.md`](../../docs/es-review-2026-08-11.md)
§1. If a reviewer prefers verbatim, all four revert to their keys and this section becomes a rule
the other way.
