# What is in the phrase table that is not a phrase

Observed from outside the application on 2026-08-10, after the deduplication, the
`UNIQUE (project, text_domain, phrase_hash)` constraint and the blog cleanup had all
landed. Method: take the Italian backlog for a text domain, and for each phrase search
every `.php`, `.phtml`, `.twig` and `.html` file in the checkout for the string
literal, excluding `test/`, `language/`, `vendor/` and `data/`.

**Absence from every template is a signal, not a verdict**, and this document is
careful about the difference. `Hello %s, Click the link below to sign in…` is found by
no template and is unquestionably live — one arrived in Mailpit while this was being
written. Static extraction cannot see a string assembled at runtime, which is exactly
the false positive `retired_on` was designed to make harmless.

With that said, the misses sort cleanly into three kinds, and only one of them is
"dead code".

---

## 1. Keys built by concatenation — an unbounded growth path the constraint does not close

`module/SionModel/src/Controller/SionController.php:358`:

```php
'Error in form submission, please review: ' . implode(', ', array_keys($messages))
```

The translator listener sees the *finished* string, so every distinct combination of
failing field names becomes its own permanent row. In this database that is already:

| | |
|---|---|
| `…please review: adminNotes` | 7436 |
| `…please review: datePublishedText` | 7708 |
| `…please review: personId` | 7054 |
| `…please review: security` | 6955 |
| `…please review: security, mainShowDisplay, view…` | 10880, 10881 |
| `…please review: withinLibraryIds` | 7928 |

and the same shape appears elsewhere:

- `The following book id's are invalid: 30106 Please try again.` — **ten rows**, one per
  set of ids somebody happened to paste (30106, 31009, 31017, 43058, 43922, 43924,
  43926, 53797, `97895, 62463`, `97896, 81642`).
- `File not imported due to duplicate withinLibraryIds: 42596,41959,42578.` (6517)

**The unique constraint does not stop this.** It collapses identical strings, and these
are all genuinely distinct — a new field combination or a new book id makes a new row,
forever. It is a slower leak than the 2,000-character truncation loop that produced
2,636 copies of one blog post, but it is the same shape of leak and it is still open.

The fix is at the caller, not in JTranslate: translate a template and interpolate
after, `translate('Error in form submission, please review: %s')` with the field list
as an argument. That is one row instead of one per combination, and unlike the current
form it is actually translatable — no translator can be asked to render
`security, mainShowDisplay, view` into Italian.

Worth grepping for the general pattern (`translate(` or `addMessage(` with a `.`
concatenation) rather than fixing only the three sites above.

## 2. Database content that passed through the translator

Association records, not interface text:

- `{"@context": "http://schema.org/", "@type": "Event", "name": "Mas…` (7049) — a
  JSON-LD blob.
- `{"friday":["09:00-12:00","13:00-18:00"], …}` (7231, 6950) — opening hours, twice.
- `Covenant mass every 3rd Sunday, daily mass every Wednesday at 7am…` (6993)
- `Turn right at the first driveway after getting off the highway. **Confe…` (6954,
  6951) — the same directions text twice, and these are the pair whose first 255
  characters collide, which is why the constraint needed a hash rather than a prefix.

These are `sch_associations` fields rendered through a translating view helper. They
are real content and a translator could in principle translate them, but they belong
to a record and change when the record changes — so a translation written against them
is stale the moment a moderator edits the shrine's hours. They are candidates for
retirement, and better still for not being routed through `translate()` at all.

## 3. Copy from the retired Laminas welcome page

`/` is now a Symfony Twig content page (`App\Controller\ContentPageController`,
`templates/content/`), and the old Laminas welcome view went with the change. Its copy
is still in the table, in the `Application` domain, appearing in no template:

6188, 6189, 6193, 6196, 6198, 6216, 6285, 6727, 6728, 6855, 7074, 7161

That is `We need your help!`, the four mission paragraphs, `Learn more`,
`translation edits`, `Latest blog posts`, `Upcoming lauch: December 18th` *(sic)*,
`Update on advances`, `Launch of new "Schoenstatt Shrines" app for Android!` and
`What is Schoenstatt Link?`.

**This is the group `jtranslate:retire` was built for**, and the safest evidence for it
is not the grep — it is that the new page says something different in English. Two of
them prove it outright: 6189's key still ends `Please help us centralize this
information by the end of 2018!` while its English, Spanish, Portuguese and German rows
all say "on an ongoing basis", and 6193's key says "our Father and Founder" where all
four say "our Founder". The key is a lookup string the site has already moved past.

Left untranslated on purpose. Translating them would have put a 2018 deadline into
Italian and nowhere else, on a page that no longer exists.

---

## 4. A JWT in the phrase table — the concatenation bug with a credential in it

**This is group 1 again, but the variable part is a secret.**

`/en/users/:id/api-tokens` builds its success message by appending the freshly minted
token:

> `Token issued. Copy it now — it is not shown again and we do not store it: eyJ0eXAi…`

The translator listener sees the finished string, so **the whole thing became a phrase
key, token included — and was copied again into the English row.** Four such rows exist,
all added 2026-08-10, all on route `juser/user/api-tokens`:

| phrase | copies of the token in that row |
|---|---|
| 13013 | key + `en` |
| 12940 | key + `en` |
| 12978 | key + `en` |
| 12996 | key + `en` |

Why it matters more than the other concatenated keys:

- The phrase table is readable by **any** account holding `sch_api_translator`, a role
  whose whole purpose is that it reaches nothing sensitive. A token in this table
  defeats that separation.
- The exporter writes compiled catalogs to disk, so the token also lands in
  `language/JUser/*.lang.php`.
- The screen's own copy promises "we do not store it". The row is the site storing it.

**These four are capsule tokens and the capsule's database is disposable**, so nothing
live is exposed by them. That is luck, not design: the same code path on production
writes a production token into a production table.

Handling, in order:

1. **Fix the caller** — `translate('Token issued. Copy it now …')` and append the token
   after translating, never before.
2. **Revoke the four `jti`s** these rows contain, and delete the rows. Retiring is not
   enough: `jtranslate:retire` leaves the row and its translations in place, and the
   point here is that the string must not exist.
3. Do the same sweep for any other message that interpolates a secret before
   translating.

`tools/classify.py` refuses these rows by matching the message prefix — never the token
shape — so the classifier never has to recognise or handle a secret.

## 5. Filenames, citations and physical descriptions from the text corpus

The Kentenich text corpus contributes three kinds of non-phrase to the table, all on the
`text` and `texts` routes, and none of them is language:

- **65 markdown filenames** — `1963-0118t029.md`, `1964-GEDEN337.md`, `1962-0617PRED.md`.
  The corpus is indexed by these names. A "translation" would change a lookup string.
- **155 bibliographic citations** — `in: KENTENICH, Josef, Die Vision vom Berge Sion,
  Berg Sion ²1975, 49-93`. A citation is the same in every language; translating one
  makes it wrong.
- **Physical descriptions in German bibliographic shorthand** — `verv.W, A 5 quer, 185
  S.` (duplicated, A5 landscape, 185 pages), `o.O., o.J.` (no place, no year), `masch.`
  (typescript). `S.` is *Seiten* and is part of the citation, not a word to render as
  *pagine*.

These are the largest single block of apparent Italian backlog that is not work at all.

## 6. Two rows that differ only by a line ending

`Only delete an assignment if it was created by mistake! …` exists twice: once with
`\n` and once with `\r\n`. The `UNIQUE (project, text_domain, phrase_hash)` constraint
cannot collapse them, because the strings genuinely differ — the hash is doing its job.
The same shape appears for `Only delete a person if he/she was created by mistake! …`.

Whichever template emits these is being saved with mixed line endings. Normalising
newlines before hashing would collapse the pairs; normalising them in the templates
would stop new pairs appearing.

## 7. The email validator interpolates the address somebody typed

Six rows of the form `'gmail.com ' is not a valid hostname for the email address` —
note the trailing space inside the quotes, which is the actual typo the user made.
`gmail.com`, `hotmail.com`, `miuandes.cl`, `uc.cl`, `yahoo.com.br`, `yahoo.de`.

Group 1 again: every distinct bad hostname anyone ever enters becomes a permanent row.
It is also a mild privacy smell — the table accumulates fragments of what real people
typed into a form.

## 8. Not everything English on the Italian page is translatable

Worth knowing before anyone treats "whatever still reads as English" as the worklist.

`module/Application/view/partial/breadcrumbs.phtml` renders `$page->getLabel()` with
**no `translate()` call**. So the breadcrumb on a shrine page reads `Shrines` in English
while the navigation menu beside it reads `Santuari` — the same word, from the same
config, one translated and one not. No translation can fix this; the fix is a
`translate()` in the partial, which is a change for a session working on the
application.

Related: **phrase 13032's key is `Registrati`** — Italian. The register page rendered an
already-translated string back through `translate()` and the listener captured the
output as a new phrase. Its English row also reads `Registrati`. Writing an Italian
translation here would legitimise a row that should not exist.

---

## Suggested handling

1. **Fix the concatenated keys at the caller** — and start with the one that
   interpolates a JWT (section 4). This is the only family that is still getting worse,
   and one member of it leaks a credential.
2. **Retire group 3.** It is what the command is for, it is reversible, and if any of
   those strings turns out to be live elsewhere it un-retires itself on the next
   render.
3. **Leave group 2 alone until somebody decides** whether association content should go
   through `translate()` at all. Retiring it is harmless; the underlying question is
   not a translation question.
4. **Consider retiring the text-corpus filenames, citations and physical descriptions**
   (section 5). They are 220 rows that will never be translated in any language.
5. **Add the missing `translate()` to the breadcrumb partial** (section 8), so the
   Italian page stops showing English that no translator can reach.

None of this blocked the translation work: 1,349 phrases were written to the capsule
with all of it outstanding. What it changes is the count — **396 of the 1,745 phrases
that looked like Italian backlog are not translatable work**, and `tools/classify.py`
now says which and why.
