# Change requests for schoenstatt.link

Everything this repository would like changed in the application, found while translating
1,383 phrases into Italian on 2026-08-10 and writing them to production.

**These are requests, not changes.** This repository does not edit
`../schoenstatt.link`; a change that belongs in the application belongs in a
session working on the application. Each entry says what is wrong, where, why it matters
from this side, and what the fix looks like.

**All ten were answered, on 2026-08-11.** The reply is
[`api-change-requests-response.md`](../schoenstatt.link/docs/api-change-requests-response.md)
in the application's own repository, and it is the authority on outcomes — read it before this
file. Nine were fixed and one (§6) **corrected the request's premise**, which is recorded
inline below rather than quietly edited away. `fix/phrase-table-hygiene` is merged
(schoenstatt.link#59); the capsule already serves it and production is deploying.

Ordered by severity. The first one is a credential leak and should not wait.

| # | what | severity | where | outcome |
|---|---|---|---|---|
| 1 | A JWT is stored in the phrase table | **security** | `juser/user/api-tokens` | fixed; 4 rows still to delete, 4 `jti`s to revoke — **ours** |
| 2 | The email validator stores whatever address was typed | privacy / growth | `zfcuser/register` | fixed; placeholders now survive into the key |
| 3 | Concatenated translate() keys grow without bound | data growth | `SionController.php:358` and others | fixed, reusably |
| 4 | Breadcrumbs are never translated | user-visible bug | `partial/breadcrumbs.phtml` | fixed on both front controllers |
| 5 | The site re-translates its own output | data growth | `zfcuser/register` | fixed (`headTitle()` was the cause) |
| 6 | Association record content goes through translate() | correctness | association views | **premise wrong**; `PublicNotes` is translated on purpose |
| 7 | The text corpus puts filenames and citations in the phrase table | noise | `text` / `texts` routes | fixed; 309 rows retired |
| 8 | Two rows differ only by a line ending | noise | assignment/person delete warnings | fixed, plus a CRLF catalog key |
| 9 | Several source strings contain errors | polish | various | 4 fixed, 3 retired, **6 are ours** |
| 10 | Translations have no revision history | resilience | `trans_translations` | built, with an API and `_note` |
| 11 | The schema now contradicts the controller about deletion | **data loss risk** | `ApiSchemaController` | filed 2026-08-11 |
| 12 | Publication and composition titles reach the phrase table | **61% of the table** | publication / composition show pages | filed 2026-08-11 |
| 13 | Three renamed phrases kept their old English row | user-visible | `database/db7.3.sql` | **fixed from here** 2026-08-11 |

They also fixed something nobody asked about that probably affected the Italian pass:
**phrase discovery was dead on every Symfony-served route**, because `TranslationsTable::flush()`
runs on a laminas `EVENT_FINISH` that a Symfony route never reaches. Discovered phrases were
queued and thrown away, silently, since a queued-but-unwritten phrase renders exactly like a
written one. One smoke run now records **170 phrases** that were being discarded. Expect the
corpus to grow, and roughly to double its arrival rate on ported pages — the Twig layer records
both the domain lookup and the `default` fallback, and the second row arrives pre-translated.

---

## 1. A JWT is stored in the phrase table — twice per token

**Severity: security. Fix this first.**

`/en/users/:id/api-tokens` builds its success message by appending the freshly minted
token, and the translator listener captures the *finished* string. So the token becomes a
phrase key, and is copied again into the English row.

Four rows in the capsule, all created 2026-08-10, all on route `juser/user/api-tokens`:
**13013, 12940, 12978, 12996**. Each holds two copies of a real JWT.

> **Verified 2026-08-11, after the merge.** The fix works: the capsule now also holds row
> **13086**, `Token issued. Copy it now — it is not shown again and we do not store it: %s` —
> the template, with the token as a `%s` that never reaches `translate()`. That row is
> ordinary translation work and **its placeholder must survive translation**.
>
> **Production holds no rows of this shape at all** (`?search=Token issued` → `total: 0`), so
> there is nothing live to revoke. Worth knowing *why*, because it was not the fix: production
> tokens were minted through the same screen, so a row should exist. It does not because phrase
> discovery was dead on Symfony-served routes — the bug the reply describes as unasked-for.
> One defect concealed another, and both were repaired in the same merge, so the window is
> closed rather than merely quiet.
>
> The four capsule rows still exist and are **not retired**. Deleting them needs something
> other than this API — v3 has no delete, and retirement is explicitly not enough, since the
> requirement is that the strings cease to exist.
>
> This also broke `tools/classify.py`, which matched the message prefix and so classified the
> *fixed* template as a leaked secret. It now matches the JWT shape itself — three base64url
> segments beginning `eyJ` — so a leak is detected by being a token rather than by the sentence
> it arrived in, and the fixed row classifies as work. The match is never printed or logged.

Why this is worse than the other concatenation bugs:

- The phrase table is readable by **any** account holding `sch_api_translator` — a role
  whose entire purpose is that it reaches nothing sensitive. A token here defeats the
  role separation that CLAUDE.md calls "the whole point".
- The catalog exporter writes to disk, so the token also lands in
  `language/JUser/*.lang.php`.
- The screen's own copy says "we do not store it". This row is the site storing it.

The four known rows are capsule tokens and the capsule database is disposable, so nothing
live is exposed *by them*. That is luck. The same code path on production writes a
production token into a production table.

**Fix:** translate the template, interpolate after.

```php
sprintf($this->translate('Token issued. Copy it now — it is not shown again and we do not store it: %s'), $jwt)
```

**Also needed:** revoke the four `jti`s these rows contain and delete the rows. Retiring
is not enough — `jtranslate:retire` leaves the row and its translations in place, and the
requirement here is that the string cease to exist.

**Worth a general sweep** for `translate(` or `addMessage(` receiving a concatenation
that includes a secret, a token, a password reset link, or a session identifier.

## 2. The email validator stores whatever address was typed

Six rows of the shape `'gmail.com ' is not a valid hostname for the email address` —
note the trailing space inside the quotes, which is the actual typo the user made.
Observed: `gmail.com`, `hotmail.com`, `miuandes.cl`, `uc.cl`, `yahoo.com.br`, `yahoo.de`.

Two problems. It is unbounded — every distinct bad hostname anyone ever types becomes a
permanent row. And it is a mild privacy smell: the phrase table accumulates fragments of
what real people typed into a registration form.

**Fix:** same shape as #1 — translate `'%s' is not a valid hostname for the email
address` and interpolate. This is Laminas' own validator message, so the fix is in how
its messages are passed to `translate()`, not in the validator.

## 3. Concatenated keys grow without bound

Already documented in [`phrase-table-noise.md`](phrase-table-noise.md) §1; restated here
because it is the family that #1 and #2 belong to and it is still open.

`module/SionModel/src/Controller/SionController.php:358`:

```php
'Error in form submission, please review: ' . implode(', ', array_keys($messages))
```

Every distinct combination of failing field names becomes its own permanent row. Also
`The following book id's are invalid: …` (ten rows), `File not imported due to duplicate
withinLibraryIds: …`, and `Assignment Id: 148` / `157` / `158` / `178` in the change log.

Beyond the growth, these are **not translatable as written** — nobody can render
`security, mainShowDisplay, view` into Italian.

**Fix:** `translate('Error in form submission, please review: %s')` with the field list
as an argument. One row instead of one per combination.

## 4. Breadcrumbs are never translated

**User-visible, and no translation can fix it.**

`module/Application/view/partial/breadcrumbs.phtml` renders `$page->getLabel()` with no
`translate()` call. The result: on an Italian shrine page the navigation menu says
`Santuari` and the breadcrumb directly below it says `Shrines` — the same word, from the
same config, one translated and one not.

Visible right now on <https://schoenstatt.link/it/shrines> (`Shrines World`) and
`/it/wayside-shrines` (`Shrines Wayside shrines`).

**Fix:** wrap the label in `$this->translate(...)` in both branches of the partial, and
check `breadcrumbs-list.phtml` for the same omission.

This one matters disproportionately: it makes a fully translated page look half-finished.

## 5. The site re-translates its own output

Two phrases whose **keys are already translated text**:

- capsule 13032, key `Registrati` (Italian), English row also `Registrati`
- production 12832, key `Registrar` (Spanish), English row also `Registrar`

Both on route `zfcuser/register`. The page rendered an already-translated string and
passed it through `translate()` again, so the listener captured the output as a new
phrase. Left untranslated deliberately — writing Italian here would legitimise rows that
should not exist.

**Fix:** find the double call on the register page. Likely a label that is translated
when built and translated again when rendered.

## 6. Association record content goes through translate()

> **This request was wrong, and the correction is important. Do not act on the version
> below.** The maintainers' reply
> ([`api-change-requests-response.md`](../schoenstatt.link/docs/api-change-requests-response.md) §6)
> establishes that `sch_associations.PublicNotes` is run through the translator **on
> purpose**, once per locale, so that an Italian-speaking pilgrim gets a shrine's
> directions in Italian. **60 live phrase rows are exactly a `PublicNotes` value.** Acting
> on the fix proposed here would have deleted a feature the movement wants.
>
> The 37-row list was also mixed. Of it:
> - `openingHoursHuman` and `eventsHuman` are **never** translated — the form's own help
>   text says so. Rows for them are leftovers.
> - The opening-hours JSON blobs and `Turn right at the first driveway…` are the form's
>   `placeholder` **examples**: interface text, and translatable. They sit in `default`
>   rather than `Schoenstatt` only because JTranslate's dispatch listener sets a text
>   domain on `formText` but not on `formTextarea`.
> - The remainder is genuinely `PublicNotes`, and should stay translatable.
>
> So the line is **not** "interface vs content". It is `PublicNotes` and the names on one
> side, everything else on the other — and both sides of that line are work rather than
> noise. `tools/classify.py`'s `skip-record-content` bucket is built on the wrong premise
> and needs rebuilding; the rows it excluded are mostly translatable.
>
> The staleness worry was also misdiagnosed, and the reply is worth reading in full: a
> phrase's identity *is* its text, so editing a description does not make its translations
> wrong — the new description is a different phrase that renders as itself until
> translated. **Nothing on the site was ever stale.** What went stale was the *worklist*:
> the superseded string stayed a live row with four good translations that nothing renders.
> Editing a description now retires the superseded phrase automatically, reversibly, with a
> history note naming the association. Consequence for this repo: **a phrase that vanishes
> from the queue may have been superseded, and `GET /api/v3/phrases/{id}/history` will say
> so.**

The original request, kept because the reply is a correction to it and half of it stands:

Association fields are rendered through a translating view helper, so a moderator's free
text becomes a phrase: opening-hours JSON, JSON-LD blobs, driving directions, notes about
one shrine's history, and `Se agradece Capital de gracias por este Santuario / …`.

37 such rows were identified and left untranslated. The reason is not squeamishness: a
translation written against record content is **stale the moment a moderator edits the
record**, and there is no mechanism to notice.

**Fix, in preference order:** stop routing `sch_associations` free-text fields through
`translate()` at all; or retire the existing rows and accept that this content is
monolingual. The underlying question — whether shrine descriptions should be translatable
— is a movement decision, not a technical one.

Note the related trap: **the form's own help text lives on the same routes and is the
same length**, so anything automated here must distinguish `Be as descriptive as
possible, including closing days…` (interface) from `Turn right at the first driveway…`
(content). `tools/classify.py` needs a hand-maintained exemption list for exactly this
reason. *(This part stands — the reply confirms the exemption list is still needed. Only
the premise about what to exempt was wrong.)*

## 7. The text corpus puts filenames and citations in the phrase table

> **Correction:** this said "the `text` and `texts` routes" as though both were live. Only
> `text` was. The 90 rows on `texts` stopped arriving in 2019, so that route is dead and its
> rows are historical. Fixed by the maintainers in one line — `books/texts/show.phtml` handed
> `headTitle()` the corpus title, and `headTitle` translates what it holds; every other show
> page already had `setTranslatorEnabled(false)`. **309 rows retired**, 219 on `text` and 90
> on `texts`, after checking that no interface string was caught.

220 rows on the `text` and `texts` routes that are not language in any language:

- **65 markdown filenames** — `1963-0118t029.md`, `1964-GEDEN337.md`. The corpus is
  indexed by these names; a "translation" would change a lookup string.
- **155 bibliographic citations** — `in: KENTENICH, Josef, Die Vision vom Berge Sion,
  Berg Sion ²1975, 49-93`, and physical descriptions in German shorthand
  (`verv.W, A 5 quer, 185 S.`, `o.O., o.J.`, `masch.`).

**Fix:** these fields should not pass through `translate()`. Retiring the rows is the
cheap version and is reversible.

## 8. Two rows differ only by a line ending

`Only delete an assignment if it was created by mistake! …` exists twice, once with `\n`
and once with `\r\n`. Same for `Only delete a person if he/she was created by mistake! …`.

The `UNIQUE (project, text_domain, phrase_hash)` constraint cannot collapse them — the
strings genuinely differ, and the hash is doing its job correctly.

**Fix:** normalise newlines in the templates that emit these; or normalise before
hashing, which would collapse the existing pairs as well as preventing new ones.

## 9. Source strings that contain errors

Each of these was translated from the corrected sense rather than reproduced faithfully,
which means **the Italian is now better than the English key**. Better to fix the key.

| where | problem |
|---|---|
| `This is the name that would be that will be shown to most users…` | `that would be that will be` — the English row already has it corrected |
| `Frau Dokto` | German typo for `Frau Doktor` |
| `Tags regarding the content of the content, form or liturgical use…` | `the content of the content` |
| `Hey! Welcome to Schoenstatt Link! … clicking on the this link` | `on the this link` |
| `Please type the following text` | the key lacks the trailing colon that all four other languages have |
| `Until 2019-10-18, this page will be oriented towards data-maintainers…` | stale content about a 2019 deadline; **and es, pt and de all render the date as 10 October while the key says the 18th** |
| `The form submitted did not originate from the expected site` | the English and Spanish rows say the form *expired*; pt and de agree with the key. Two of the five rows describe a different error |
| `Show editions separately?` | the Spanish row says `¿Mostrar ediciones obsoletas?` — *obsolete* editions, which is not what the key asks |
| `Sun-Sat 9-11am, 12-8pm, except first Tuesdays of the month` | the Spanish row says `Sábado-Domingo` (Sat–Sun) and drops the second time range |
| `Ladies of Schoenstatt` | the Spanish row is `Inst. Nuestra Señora de Schoenstatt` — *Our Lady*, a different body from *the Ladies* |
| `Madrugadores of %s` | the English row reads `Centinels of %s`, apparently a misspelling of *Sentinels* |
| `xxi+133` | a real page-count value sitting in the phrase table |

The last three are wrong *translations* rather than wrong keys, and they are Spanish and
English rather than Italian — worth a pass by whoever owns those languages.

## 10. Translations have no revision history

> **Built, and beyond what was asked.** `trans_translations_history` exists, append-only,
> with no foreign key in either direction so that neither a retraction nor a phrase deletion
> can erase it. `GET /api/v3/phrases/{phraseId}/history` serves it — opt-in, linked from
> `meta.history` on the phrase document rather than inlined, with `?language=` narrowing to
> one thread and `operation` one of `update` / `retract` / `retire`. The second option in the
> fix below was taken; `sch_changes` integration was declined, on the reasonable ground that
> the append-only table gives the recoverability at a fraction of the coupling.
>
> One entry per *event*, never per write: **filling an empty language writes nothing**, so an
> empty history means "nothing was lost here" rather than "no records kept". The thread is
> keyed on `(project, phrase hash, locale)` and therefore survives id changes and spans every
> text domain the string appears in — the same English string in `Schoenstatt` and in
> `default` is one translation problem.
>
> A PATCH may carry a reserved `_note` (≤255 chars, trimmed not refused, non-string is a 422;
> batch entries take it too). It lands on the history rows the write produces — **one per
> translation destroyed, none if the write only fills gaps** — and it is rendered to humans on
> the phrase edit screen, not only to agents. The maintainers ask for it on every overwrite,
> and the reason is good: read in order, the notes are a conversation, so the third agent to
> arrive learns that the obvious rendering was already tried and abandoned. It is not yet
> advertised in the schema — see §11.
>
> Caveat that limits the win: **the table does not backfill**, so nothing written before the
> deploy is recoverable.

`trans_translations` has no `sch_changes` equivalent, so a write destroys the previous
text with no record. Association writes are revertible; translation writes are not.

This shapes everything on this side: it is why a 100-item review queue exists *before*
production rather than after, why the tooling dry-runs by default, and why "fill gaps,
never overwrite" is a hard rule rather than a preference.

**Fix, if it is ever worth the cost:** record translation writes in `sch_changes` the way
association writes already are. Even an append-only `trans_translations_history` with
`(translation_id, old_text, modified_by, modified_on)` would turn an unrecoverable
mistake into a recoverable one, and would make it safe to correct a bad translation
rather than having to be sure first.

---

## 11. The phrase schema now contradicts the phrase controller about deletion

**Filed 2026-08-11, after reading the reply and the merged `fix/phrase-table-hygiene`.**
This is the one thing in the merge that could cost somebody data, and it is a documentation
defect rather than a code one.

`PhrasesV3Controller::apply()` as shipped treats an explicit JSON `null` as a **retraction**:

```php
$retractions = array_filter($patch, static fn (mixed $v): bool => null === $v);
```

It is deliberate, it is careful about the `''`/`null` asymmetry, and `representHistory()`
exposes the resulting `operation: retract`. The reply documents it too. But
`ApiSchemaController` still tells every caller the opposite, in the note it has always
carried:

> An empty string means "leave this language alone", not "blank it" — the web form behaves
> the same way, and **there is no way to remove a translation through either surface.**

Both statements are live in the same deployment. That matters more here than an ordinary doc
lag, because this API's whole design asks callers to **read the schema at request time and
validate against it rather than discovering rules by rejection** — advice this repo follows
and recommends in its own contract. A client built exactly as instructed now believes
retraction is impossible, and gets no warning that a stray `null` destroys a translation and
files a `retract` in its history.

That failure is easy to reach by accident and hard to see. A serializer emitting `null` for
an absent optional field, a dictionary comprehension over a language list where one lookup
misses, `json.dumps` of a Python `None` — none of these look like a deletion at the call
site, and all of them now are one. The `''` case was safe against exactly this class of
accident, which is presumably why it was chosen; `null` is not.

**Requested, in order:**

1. **Correct the schema note.** Say that `''` leaves a language alone and an explicit `null`
   retracts it, and that a retraction is recorded and recoverable through `.../history`.
   One string, and it removes the contradiction.
2. **Advertise `_note` in the schema.** It is a reserved PATCH key with a length bound and a
   422 on a non-string — precisely the kind of rule the schema exists to publish. Nothing in
   `GET /api/v3/schema/phrase` mentions it, so a caller following the documented discovery
   path cannot find the field the reply asks us all to send on every overwrite.
3. **Consider requiring something more explicit than `null` to retract** — a reserved
   `_retract: ["de"]`, or `null` accepted only on the single-phrase endpoint. A destructive
   operation reachable by a serializer's default value has no confirmation step in it. This
   is a design opinion and the maintainers may reasonably decline it; 1 and 2 stand either
   way.

Two smaller notes from the same read, neither a problem:

- `'0'` is now writable and honestly reported as changed, where it used to be discarded by a
  falsy test. Correct, and worth knowing if any tool here ever compares counts across the
  change.
- **The history table does not backfill.** `GET /api/v3/phrases/7229/history` answers `200`
  with an empty list in the capsule although that row was overwritten on 2026-08-10 — the
  overwrite went to production, and nothing before the migration has entries either way. So
  recoverability begins at the deploy: the 1,041 rows written and 22 corrected on 2026-08-10
  are still unrecoverable, and the review queues built for them keep their original weight.

---

## 12. Publication and composition titles now reach the phrase table

**Filed 2026-08-11.** §7 was this defect on the text corpus and its fix was one line. Two
show pages were missed, and the discovery repair has made them visible in bulk.

> **FIXED 2026-08-11, and this section's diagnosis was wrong in two ways worth keeping on the
> record.** See `api-change-requests-response.md` §12 and `database/db7.6.sql`.
>
> **The mechanism was not `headTitle()`.** It was already `setTranslatorEnabled(false)` on
> `books/publications/show.phtml` and had been since 2019, and `books/compositions/show.phtml`
> never calls `headTitle()` at all — so the fix suggested at the end of this section was aimed
> at code that was already correct. The path was `Application\Module::onBootstrap()`, which
> builds one navigation page per database row labelled with that row's own name, plus §4's
> breadcrumb fix translating those labels. Which explains the two things this section could not:
> why the rows arrived the day *after* a deploy, and why they arrived in `Application` **and**
> `default` rather than in the page's own domain.
>
> **And the signature below is not exact.** `TranslationsTable::writeMissingPhrasesToDb()`
> copies translations onto a newly discovered phrase from any same-text row in another text
> domain, so a colliding name arrives pre-translated in four languages and then passes the
> "nobody has translated it" test. Six rows survived `db7.4` that way and needed `db7.6`.
> The durable signal is `origin_route` + `text_domain`, and `tools/classify.py` was rebuilt on
> it — see the note on `is_title_artefact()`.
>
> ~4,100 rows have left the worklist. The corpus is 1,599 live phrases and the Italian gap is
> 138, so every count in this section is now historical.

`headTitle()` translates whatever it holds. The publication and composition show pages hand
it the record's own title, so the title misses the catalog, is filed as a phrase, and the
English row is auto-filled with a verbatim copy of it.

**Escalated the same day. This is now the largest thing in the phrase table.** Counted twice
on 2026-08-11, a few hours apart:

| | `publication` rows | `composition` rows | whole corpus |
|---|---|---|---|
| early afternoon | 436 | 87 | 2,281 |
| later the same day | **3,086** | 269 | **5,020** |

**3,071 of those 3,086 rows match the title signature, and they are 61% of the entire phrase
table.** It has essentially reached its ceiling rather than still running away: 1,536 distinct
titles, each filed **twice** — 1,538 rows in `Application` and 1,538 in `default` — which is
exactly the double arrival the reply predicted, the Twig layer recording both the domain lookup
and the `default` fallback. So the defect has now captured the library's whole catalogue, about
one publication per two rows, and will grow only as the library does.

That is the urgency: not that it is accelerating, but that **every one of those 3,000 rows will
appear in every language's untranslated gap, for ever, until they are retired.** They already
outnumber the real interface strings two to one, and any count of "how much is left to
translate" taken from the API is now dominated by them.

They are not translatable in any language. `Apologia pro vita mea`,
`Das Ehe-Ideal`, `A házaspárok útján`, `Svatynka pramen zivota` — a work's title is the title
of that work, and rendering it in Portuguese would invent an edition that does not exist.
Where a real translated edition *does* exist, its title belongs on that publication's own
record, which is where every other title already lives.

**These were invisible until today.** Phrase discovery was dead on Symfony-served routes, so
they were being queued and discarded; with discovery repaired they arrive in bulk. This is
the first concrete cost of that fix and it is worth naming as such — the repair was right, and
it uncovered a second defect underneath it, exactly as the JWT rows did in §1.

The signature is exact, which is what makes it safe to act on: the English row is a verbatim
copy of the key **and** no other language has ever translated it. On `publication` the nine
rows that fail the second test are precisely the nine real interface strings — `Data source`,
`Date published`, `Leave a comment`, `Total views`, `Copy into main corpus` and the rest. No
approximation involved.

**Fix:** `setTranslatorEnabled(false)` on the publication and composition show pages' calls to
`headTitle()`, as `books/texts/show.phtml` now has, and retire the 509 rows. `tools/classify.py`
excludes them in the meantime as `skip-publication-title`.

While you are there: the same `headTitle()` treatment is worth checking on every remaining
show page. §7 found one, this finds two more, and the pattern is now three for three.

---

## 13. Three phrases the migration renamed kept their old English row

**Found and fixed from this side on 2026-08-11.** Recorded because the mechanism will recur on
the next rename, and because it was invisible to everyone except a caller comparing each key
against its own English row.

§9's fix renamed three phrases in place with `database/db7.3.sql`, deliberately, so that
existing translations would follow the corrected text rather than being orphaned. That worked.
But the **English row is itself a translation**, and it held a copy of the *old* text — so the
key was corrected while `en` went on saying the thing the rename existed to remove. English
pages render the `en` row, so English readers still saw every typo that had supposedly been
fixed:

| id | key, after the rename | `en` row, before this fix |
|---|---|---|
| 7268 | `Tags regarding the content, form or liturgical use of the song.` | `…the content of the content, form…` |
| 12943, 7000 | `…any apps or websites which wish to receive…` | `…any apps or websites who which to receive…` |

Set to the corrected key verbatim, with `_note`. A fourth renamed row, 6750, already matched.

**For the next rename:** when `phrase` is corrected in place, the `en` row needs the same
update in the same migration, or English keeps rendering the old string. The other four
languages are unaffected — their translations were of the *meaning*, which did not change.

---

## 14. Please expose retirement on the API

**Filed 2026-08-11**, after reading `api-change-requests-response.md`. This is the one request
in this file that asks for a new capability rather than a fix, and it comes from the maintainer
of this repository rather than from a defect.

> **SHIPPED 2026-08-11, the same day, with every ask granted and two things we did not think to
> request.** `POST /api/v3/phrases/{id}/retire` and `/unretire`, `_note` required and enforced,
> `?onlyRetired=1` and `?includeRetired=1`, `meta.retiredOn` on the document, and the whole
> contract published under `retirement` in the phrase schema — so it is discoverable the
> documented way rather than only here.
>
> The two we did not ask for and would not have thought of:
>
> - **Idempotence with no second history entry.** Retiring an already-retired phrase is a `200`
>   with `changed: false` and writes nothing. So a retry cannot forge a second judgement, which
>   matters because a retirement's note *is* the judgement.
> - **Self-healing writes no history**, which turns the absence of an `unretire` entry into the
>   signal: a row that is live again with a `retire` and nothing after it came back by itself, so
>   the retirement was wrong. That is a better audit design than the `?retired=true` flag we
>   asked for, and it is what made a mechanical resurrection check possible.
>
> Also adopted: `writable.retract.notRetirement` and `retirement.notRetraction` now warn about
> the confusion this section spent a paragraph on, from both directions. Verified end to end on
> production — the required-note 422, the idempotent retry, the filters, and two real retirements.

**The direction.** The maintainer, 2026-08-11: retire any phrase we judge was added by mistake, with a
note saying why; if it comes back from retirement the note documents what was believed, and the
bug can be addressed at that moment. The accepted cost is one request's translation miss. The
goal is to bring the phrase counts to zero in the short term rather than carrying a permanent
tail of rows nobody can translate.

**Why this is a reasonable thing for an agent to be allowed to do**, in your own terms: a
retirement destroys nothing, `retired_on` is a statement about the translator's worklist rather
than about what the site renders, and it **self-heals** — a phrase the application still looks up
un-retires itself on the next miss. That is a stronger guarantee than the one you extended to
overwrites in §10. An overwrite is recoverable only if a reviewer notices; a wrong retirement
repairs itself the next time the page renders. So the risk profile is *better* than the one that
justified relaxing "fill gaps, never overwrite", and the audit trail is the same table.

**What is missing is only the surface.** `operation: retire` already exists in
`trans_translations_history`, already appears in every language's thread, and is already
published in `history.operations`. `PhrasesV3Controller` has five actions — `index`, `show`,
`history`, `patch`, `patchCollection` — and "retire" appears in none of them. Today the only
paths are `jtranslate:retire`, a migration, or the application superseding a description itself,
none of which an agent working through the API can reach.

Any of these would serve; the first is our preference because it cannot be a typo in a write:

```jsonc
POST /api/v3/phrases/{id}/retire   { "_note": "why" }      // and a companion un-retire
PATCH /api/v3/phrases/{id}         { "_retire": true, "_note": "why" }
PATCH /api/v3/phrases              { "retire": [13661, 13662], "_note": "why" }   // batch
```

Three things we would ask for in the contract, all of them for the same reason — that a
retirement is a judgement and the note is the only record of it:

- **Make `_note` mandatory here**, unlike on a write. A write's note explains a replacement that
  is visible in the history anyway; a retirement's note is the *entire* record of why a row left
  the worklist, and it is what the next agent reads when the row comes back.
- **A collection filter for retired rows** — `?retired=true`. Right now a retired phrase is
  invisible to us except by id, so we cannot audit our own retirements, cannot tell "retired" from
  "deleted", and cannot notice a row that un-retired itself. That last one is the feedback signal
  this whole strategy depends on.
- **Keep it reversible from the API too.** If we can retire, we should be able to un-retire what
  we got wrong without waiting for a page render.

We are not asking for phrase *deletion*. §1's four JWT rows need it and it is a production task
for a human; nothing about routine worklist hygiene does. (The shipped schema says the same thing
back to us under `retirement.notDeletion`, which is the right place for it.)

`tools/classify.py` accumulates candidates under a `retire-` bucket prefix with the reason
already phrased to serve as the `_note`, and excludes them from the worklist so nothing offers
them as work. `docs/retire-queue.md` is the log.

## 15. One breadcrumb residual db7.4 and db7.6 did not reach

**Filed 2026-08-11**, found while verifying §12's fix against production rather than trusting it.

Two live rows on production:

| id | domain | route | phrase | `added_on` | translations |
|---|---|---|---|---|---|
| 13661 | `Application` | `composition` | `Meu menino pequenino` | 2026-08-11 01:38 | en, pt |
| 13662 | `default` | `composition` | `Meu menino pequenino` | 2026-08-11 01:38 | en, pt |

This is exactly the §12 signature: a record's own name, filed twice by the breadcrumb's two-domain
lookup, at 01:38 UTC — before that morning's 09:00 deploy, so while the defect was still live. It
is a composition name, and the `pt` row is a verbatim copy of the key written two minutes after
discovery, i.e. the inheritance copy `db7.6.sql`'s header describes.

**Why the migrations missed it.** `db7.6.sql` statement 2 is scoped
`origin_route = 'publication'` and requires
`EXISTS (SELECT 1 FROM sch_publications r WHERE r.Title = p.phrase)`. A composition name matches
neither condition. `db7.4.sql` retired 302 composition names, so the bulk was caught — these two
appear to have arrived after it ran, or to have failed its own translation guard for the same
inheritance reason the six publication rows did.

**The check that would have caught it** is statement 4 of `db7.6.sql` generalized off
`sch_publications`: group live rows by `origin_route` and `text_domain`, and treat route
`composition` in `Application` or `default` the same way as route `publication`. Suggest joining
against whatever table backs composition names, with `EXISTS` rather than a join for the reason
your own header gives.

**Both retired through the new endpoint on 2026-08-11 at 11:45 UTC**, with a note naming this
section, so the evidence is in the database rather than only here. Production went from 1,581
live phrases to 1,579. Reported anyway because a migration's scope missing a whole route is worth
knowing, and because the check that would catch the next one does not exist yet.

To be precise about one thing this section could have implied: both rows were filed at 01:38 UTC,
**before** the 09:00 deploy, so they are residue and **not** evidence that the fix regressed. The
fix appears to be holding.

One thing this pair is good for: it is the test case that proves the corrected signature works.
The old "no other language has translated it" test passed it as ordinary translatable work — our
classifier was offering a Portuguese song title for translation into German, Spanish and Italian.

---

## 16. A rendered-but-untranslatable string cannot leave the worklist

**The gap:** retirement self-heals on lookup, which is the right behaviour and is what makes it
safe. The consequence is that a string the site **renders** and that **no language can ever
translate** cannot be taken off a translator's worklist by any means available to us. Retire it
and the next render un-retires it.

This is not hypothetical and it is not a complaint about `retired_on`. On 2026-08-11 we retired
eleven such rows and two were live again within five minutes — `7231` (an opening-hours JSON
placeholder) because somebody opened `associations/create`, and `7469` (a lone non-breaking space)
because a `publication` page rendered. Both carry a `retire` entry with no `unretire`, exactly as
`retirement.selfHealing` says they should. The mechanism worked; the strings are simply in the
wrong place.

The rows, all long-standing:

| what | example | route |
|---|---|---|
| call-number format templates | `%1$s%2$-8s%3$04d%4$03d%5$03d`, `$2`, `:short_category` | `libraries/library/edit` |
| a JSON-LD event skeleton | `{"@context": "http://schema.org/", "@type": "Event", …}` | `associations/association/edit` |
| an opening-hours blob | `{"friday":["09:00-12:00","13:00-18:00"], …}` | `associations/create` |
| bare data | `1`, `2007`, a non-breaking space | `publication-edit`, `publication` |
| corpus filenames | `1963-0118t029.md` | the `text` routes |

**What we think the fix is, and it is on your side of the line.** None of these should reach
`translate()`. A `placeholder` that the application itself parses is not interface text — it is
sample data, and translating `"friday"` would break the thing the example exists to be copied
into. The same call sites that were fixed in §2/§3/§5 by passing a `TranslatableMessage` or by
turning the translator off are the shape of it: `setTranslatorEnabled(false)` on those fields, or
pass the example as data rather than as a translatable label.

That is strictly better than anything we could do from here, because it stops the row being
filed at all rather than removing it afterwards.

**If that is more work than it is worth**, the alternative we would find useful is a way to say
*this string is not translatable* that survives a lookup — a flag distinct from `retired_on`, or
a `retired_on` variant the discovery path does not clear. We are **not** asking for that first:
a flag would let a consumer permanently hide a row that a maintainer might want translated, which
is a worse failure than the current one. The self-healing behaviour is correct and we would rather
you did not weaken it.

**No action needed on the two live rows.** They are back on the worklist and we have left them
there deliberately, because the absence of an `unretire` after their `retire` is the signal, and
calling un-retire by hand would replace it with a false account. Nine more of the eleven are still
retired and will return on their next render; that is expected and is not a bug report.

**What we changed on our side, so this does not recur:** `tools/classify.py` now buckets on
*does anything look this string up* rather than on *is this string translatable*, so these five
categories are `skip-` again and nothing will offer to retire them. The two categories where
nothing renders the string — the dead Laminas welcome page, and the site's own retranslated
output — stayed retired without trouble, all fifteen of them.

---

## Not a request: what is already fine

Recorded so nobody "fixes" these.

- **`GET /api/v3/schema/{entity}` is genuinely load-bearing** and worked exactly as
  advertised. Reading `writable.languages` at request time is what let one tool write to
  two environments without a code change.
- **The batch endpoint's per-id result map** is the right shape. A batch's interesting
  outcome is the partial one, and `summary.applied` is what a caller should trust.
- **The uninformative 401** is correct, and the checklist in CLAUDE.md is what makes it
  workable. It cost one re-mint, not an investigation.
- **`retired_on` and self-un-retiring** behave as documented — and §16 is the write-up of us
  learning that the hard way rather than a complaint about it. Two rows we should not have retired
  came back on their own within five minutes, with no history written, which is exactly what the
  schema promises. **Do not weaken this to accommodate §16.** It is the only mechanism in the
  phrase API that corrects one of our mistakes without a human noticing first.
- **The shared retirement thread** (schoenstatt.link#71) is right, and it changed how we work
  rather than merely being documented: we retired in sibling pairs because of it, and the first
  pair we tried confirmed every claim in it against production. Retiring one row of a pair would
  have left three languages 19 rows short with nothing to explain why.
