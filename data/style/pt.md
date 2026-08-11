# Portuguese — variant, register, and the terms that differ from Spanish

Decisions actually made while translating, with the evidence that settled them. A rule
here means "this was chosen once, deliberately, and the next person should choose the same
way" — not "this is how Portuguese works".

Verified against production and the eleven Brazilian Schoenstatt titles listed in
[`../glossary/pt.yaml`](../glossary/pt.yaml), on 2026-08-10.

## The variant is Brazilian, and the site declares it

The database keys this locale **`pt_BR`** and the compiled catalog is `pt_BR.lang.php`.
Write Brazilian Portuguese. The supplied books are Brazilian too (Santa Maria RS,
São Paulo), so the sources and the locale agree.

| not this (pt-PT) | this (pt-BR) |
|---|---|
| `utilizador` | **`usuário`** |
| `contacto` | **`contato`** |
| `Registo` | **`Registro`** |
| `palavra-passe` | **`senha`** |
| `registada` | **`registrada`** |
| `ficheiro` | **`arquivo`** |
| `apelido` (surname) | **`sobrenome`** |

**Two of these are not stylistic.** `apelido` means *nickname* in Brazil, so a person
filling `Last name` types the wrong thing. And `direção postal` — which nine rows used — is
a calque of Spanish `dirección` and means *direction*: the Portuguese word is **`endereço`**.
Both were corrected; see [`../../docs/pt-audit.md`](../../docs/pt-audit.md).

## Do not translate the Spanish — translate the key

This is the single most important rule for Portuguese on this site, because the two
languages are close enough that copying looks like translating.

**Every error found in the existing 719 Portuguese rows came from copying Spanish and
only partly converting it.** `Disponibilidad de exemplares físicos`,
`Santuário de la Comunidad del Camino`, `Persona criado com êxito`, `Estes datos`. One of
them, `Person successfully created.`, was mis-copied into the **German** row as Spanish
too.

The most consequential case is a term, not a typo:

> **`Federation` is `União`, never `Federação`.**
> Spanish says `Federación` throughout. Portuguese Schoenstatt calls this tier the
> *Union* — `União Apostólica`, `Uniões Apostólicas` — and `Federação` does not occur once
> in 3.1 million characters of the movement's own Portuguese. The site's existing
> Portuguese already had this right. Following Spanish would have broken it.

So: Spanish is useful for *shape* — whether a term is translated at all, whether a heading
is pluralized — and is not evidence about Portuguese words.

## Imperatives for actions

As in the other languages, and matching what the site already does:

| | |
|---|---|
| `Sign in` | **`Acessar`** / `Entrar` |
| `Logout` | **`Sair`** |
| `Search %s` | **`Buscar em %s`** |
| `Delete` | **`Excluir`** — not `Apagar` or `Eliminar` |
| `Submit` | **`Confirmar`** |

**`Excluir` for deletion** is the house choice and the existing rows mostly use it;
`Usuário excluído` replaced `Utilizador apagado` partly for that consistency.

## Library terminology, following what is already there

Portuguese was translated before Italian was, and the library module's existing Portuguese
is coherent. Follow it rather than importing the Italian decisions:

| | |
|---|---|
| `Call number` | **`Número de localizador`** — the existing form. (Italian chose `Collocazione`; do not harmonize them, they are different catalogues' conventions) |
| `Checkout` (noun) | **`empréstimo`**; to check out → **`emprestar`**; to check in → **`devolver`** |
| `Barcode` | **`Código de barras`** — plural `barras` |
| `Publisher` | **`Editor`** (existing) |
| `Abbreviation` | **`Abreviatura`** |

## `Pe.`, not `P.`

The Brazilian abbreviation for *Padre* is **`Pe.`** — 313 occurrences against 20 for the
Spanish/Italian `P.` in the book corpus. The site's existing rows already use `Pe.`.
In prose, `Padre José Kentenich`; for the founder as founder, **`Pai e Fundador`**.

## Placeholder and example text is localized

`ex.` for *exemplo* — the site's existing Portuguese uses `ex.`, `p.ex.` and `p. ex.`
inconsistently; prefer the short **`ex.`**. Example names are localized as the other
languages do.

## Things left in English

`ISBN`, `Blog`, `Wikipedia`, `URL`, `Site` (ordinary Brazilian for *website*), `Media`,
`Token`, `Creative Commons`, `Chord pro`, `LilyPond`, `JSON`, and proper or place names.

`Site` is worth stating explicitly because it looks like an untranslated row and is not.

## Where the site is inconsistent with itself

Recorded rather than resolved — each needs one decision that applies to several rows.

- **`assignment`** appears as `cargo / tarefa`, `função / tarefa`, `nomeação / função`,
  `designação` and `tarefa` across different rows. New translations use `designação`,
  matching the existing `Editar Designação`, but the set should be unified.
- **`moderator`** appears as both `Assessor` and `Moderador`. New rows use `Assessor`,
  matching Spanish and the existing `Branch moderator`.
- **`Register`** exists as `Abrir conta` and as `Registrar`. New rows follow `Abrir conta`.
- **`schoenstattiano`/`schoenstatiano`** — the site uses two `t`, the books prefer one.
  Left as the site has it. See the glossary.
