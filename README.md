# schoenstatt-agent

Working notes and small tools for looking after the data behind
[schoenstatt.link](https://schoenstatt.link), a public reference site about Schoenstatt.

This is not the website. The site is a separate application. What lives here is the
material needed to change that site's data without getting it wrong: glossaries of terms
and the rendering agreed for each language, per-language style notes, a client for the
site's API, and scripts that settle the decidable parts of the job mechanically so a
person is left with only the judgement calls. Much of the work is done with the help of
an AI assistant, which is what `CLAUDE.md` is — the rules it is held to here.

It is a volunteer effort, maintained by one person. It is not an official publication of
the Schoenstatt movement and does not speak for the movement or for any of its bodies.

The repository is public for a plain reason. Everything in it is a record of a decision
someone made about someone else's information, and such records are more useful where
they can be read and corrected than where they cannot.

## What is here

| | |
|---|---|
| `data/glossary/` | Schoenstatt terms and the rendering agreed for each language, with the source each was attested against |
| `data/style/` | per-language notes — register, forms of address, capitalisation |
| `cmd/schoenstatt-mcp/` | an MCP server exposing the site's translation API as tools |
| `internal/schoenstatt/` | the API client |
| `tools/` | the pipeline — find the gap, sort it, check a draft, apply a batch |
| `docs/` | what each pass changed, and what it deliberately left alone |

## The work

Translating the site's interface into the languages it already supports — German,
English, Spanish, Italian, Portuguese — and correcting existing translations that are
demonstrably wrong. After that, keeping its directory of Schoenstatt shrines current, so
that someone looking for a shrine can find it.

Two rules run through all of it.

A missing entry is better than a wrong one. A missing one is visibly missing; nobody
re-checks a field that is already filled.

Every change made through this tooling is written to the site under its own named
account, so it can be found, questioned and undone afterwards. No credentials are kept
in this repository — they live outside it, and nothing here reads a token from a tracked
file.

## Using any of it

The tools are specific to schoenstatt.link's API and are unlikely to be much use
elsewhere; `tools/README.md` and `cmd/schoenstatt-mcp/README.md` describe them if you
want to look. The glossaries and style notes may travel better: they are ordinary
terminology work on a vocabulary that general dictionaries cover poorly, and they are
licensed for reuse.

## Corrections

If something here is wrong — a term rendered badly in your language, a fact about a
shrine, a decision recorded that should not have been — an issue pointing it out is the
most useful thing this repository can receive.

## License

Copyright 2026 the schoenstatt.link maintainer.

Code is Apache-2.0 (see `LICENSE`). The curated data under `data/` is CC BY-SA 4.0 (see
`data/LICENSE`).
