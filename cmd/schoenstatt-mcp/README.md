# schoenstatt-mcp

An MCP server exposing the schoenstatt.link translation API (`/api/v3/phrases`) as
tools. It carries one credential, holding the `sch_api_translator` role, and
therefore reaches one resource. The shrine endpoints are a different role and are
deliberately not implemented here.

## Setup

Credentials live outside this repository, in `~/.config/schoenstatt/credentials.env`
(mode `600`, in a directory that is mode `700`):

```
SCHOENSTATT_BASE_URL=http://localhost:8080
SCHOENSTATT_TRANSLATOR_JWT=<the JWT, shown once at /en/users/:id/api-tokens>
```

The server reads that file itself, so an MCP client needs no environment block. The
same variables in the environment take precedence if you'd rather pass them that way.
No token is ever accepted as a command-line argument — arguments are visible in `ps`
and land in shell history.

The repository ships a `.mcp.json` that runs the server with `go run`, so a Claude
Code session in this directory picks it up with no build step. For a standalone
binary:

```sh
go build -o bin/schoenstatt-mcp ./cmd/schoenstatt-mcp
```

## The tools

| tool | what it is for |
|---|---|
| `phrase_languages` | which languages this site writes, read live from the API's schema |
| `phrase_search` | find phrases by language coverage, text domain, or source text |
| `phrase_get` | one phrase: every translation, staleness dates, and the etag |
| `phrase_patch` | write one phrase, with an etag check |
| `phrase_batch_patch` | write up to 200 phrases, recompiling the catalogs once |

## The source string is not guaranteed to be English

A phrase *is* its source string — the key the site looks itself up by. That string is
usually English, but nothing requires it to be: phrases originating from the database
rather than a template can be in any language, and a book title is whatever language
the book is in. There is no source-language field to consult.

So `en` is a translatable target like any other — `untranslated_in: "en"` returns real
work — and every read reminds the caller to determine the source language rather than
assume it. `context_url` is always the English page, which means it shows the source
verbatim only when the source *is* English; otherwise it shows the English
translation, which must not be mistaken for the source.

## Language codes

**Tools speak ISO 639-1 language codes — `en`, `es`, `it`, `de`, `pt`.** The API
settled on these on 2026-08-10, reporting them under `writable.languages`; before
that it reported regional codes under `writable.locales`. The server reads either key
and maps whatever it finds, so the tool surface is identical against a site on either
side of that change. The regional form of a listed language is refused rather than
accepted as a synonym, matching the API.

A short code is used only where it is unambiguous. If the site ever writes both
`pt_BR` and `pt_PT`, `pt` names neither and the full code is required — guessing
would write a translation into the wrong language.

## Saying why: `note`

`phrase_patch` and `phrase_batch_patch` take a `note` — the API's reserved `_note`, one per
phrase. Send it whenever a write **replaces** an existing translation.

The server attaches it to the history row holding the text that write destroyed, and drops it
when the write only fills empty rows, so it is never noise. Read in order the notes are a
conversation: the next agent learns that the obvious rendering was already tried and abandoned
instead of trying it again. Humans read them too, on the phrase edit screen.

The key and its length bound come from `writable.note` in the live schema rather than from a
constant here. An over-long note is **trimmed and reported** rather than refused — the opposite
of how an over-long translation is handled, matching the API, because losing the tail of a
justification is a smaller harm than refusing the translation it justifies.

## What the tools refuse

An overwrite is recoverable from the phrase's history as of 2026-08-11, but reverting one still
needs somebody to notice it — so the server refuses the mistakes that are silent, and makes the
irrecoverable one unrepresentable:

- **An empty translation.** The API treats `""` as "leave this language alone", so it is a no-op
  that looks like a deletion. Refusing it is the difference between "nothing happened" and
  knowing why.
- **Removal, entirely.** `_retract` is the only way to delete a translation and is deliberately
  not exposed: these tools fill gaps and correct specific rows, and a retraction should come
  from a session that means it. `writable.retract` is parsed so a caller can tell a site that
  has retraction from one where a bare `null` still deleted — and never sent.
- **A JSON `null`, structurally.** Translations stay a `map[string]string` all the way to the
  wire, so a null cannot be emitted rather than merely being checked for. That matters because
  every way to produce one by accident — a serializer's default for an absent optional field, a
  map lookup that missed — looks nothing like a deletion at the call site.
- **An unknown language**, naming the valid ones — an agent that gets a bare
  rejection guesses again.
- **A translation longer than the column**, before it is sent.
- **A batch over 200**, which the API caps so a write cannot time out half finished.

These are guardrails, not a sandbox. Anything holding the token can call the API
directly and bypass all of them. The boundary that actually holds is the token's
role, enforced server-side.

## Development

```sh
go test ./...     # the locale mapping, which has to survive the en_US → en flip
go vet ./...
```

The capsule must be running for anything that talks to the API: `docker compose up -d`
in the schoenstatt.link checkout, which serves `http://localhost:8080`.
