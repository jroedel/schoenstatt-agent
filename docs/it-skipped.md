# The phrases left untranslated on purpose

The Italian backlog was 1,745 phrases in the capsule. **1,349 were translated; 396 were not, and
that is a decision rather than a gap.** This document says which and why, so nobody
re-derives it and nobody mistakes it for unfinished work.

Regenerate with `python3 tools/classify.py <scratch>`, which is where these buckets
and their reasons live. A phrase lands in exactly one bucket; the first matching rule
wins, so the buckets are ordered most-specific-first in the code.

**On production the same rules leave 394.** The two sites do not hold an identical
corpus — 17 phrases exist only on production and 38 only in the capsule — so the
counts differ by a handful while the buckets and the reasoning are the same. The
phrase ids below are the **capsule's**; production uses a different id for some of
the same phrases, which is why nothing downstream should carry an id between sites.

Read alongside [`phrase-table-noise.md`](phrase-table-noise.md), which explains how
most of this got into the phrase table in the first place.

| bucket | phrases | one-line reason |
|---|---|---|
| `skip-bibliographic-citation` | 155 | a citation is the same in every language |
| `skip-german-source-material` | 81 | no language has systematically translated the corpus |
| `skip-german-source-precedent` | 2 | has precedent, but the corpus is one decision not 300 |
| `skip-filename` | 65 | the corpus is indexed by these names |
| `skip-record-content` | 37 | stale the moment a moderator edits the record |
| `skip-concatenated-key` | 28 | the variable part is baked into the key |
| `skip-leaked-secret` | 4 | translating it would make a third copy of a token |
| `skip-dead-page` | 12 | the page it belonged to no longer exists |
| `skip-nothing-to-translate` | 8 | digits, punctuation or whitespace only |
| `skip-format-template` | 4 | the placeholders are the whole string |
| `skip-retranslated-output` | 1 | the key is already Italian |
| | **397** | |


## Bibliographic citations from the Kentenich corpus — 155

`skip-bibliographic-citation`

A bibliographic citation for the Kentenich text corpus — volume, place and page range. A citation is the same in every language and translating it would make it wrong.

Text domains: Books (155).  
Routes: text (112), texts (43).

Examples:

- `D, A 5, 119 S.` — phrase 8757
- `verv., A 4, 95 S.` — phrase 7367
- `Nr.: 1948\datensac` — phrase 8815
- `o.O., o.J., 94-124` — phrase 8217
- `verv. o.J., 223 S.` — phrase 7369
- `verv., A 5, 223 S.` — phrase 7381
- `masch., A 4, 137 S.` — phrase 7368
- `verv.W, A 5 q, 188 S.` — phrase 8152


## German source material from the Kentenich corpus — 81

`skip-german-source-material`

German source material from the Kentenich text corpus, not interface text. No language has systematically translated these: of the 67 date-shaped strings only 2 have Spanish, and English copies the German verbatim. Whether the corpus should be translated at all is a decision for the movement, not a gap to fill.

Text domains: Books (81).  
Routes: text (49), texts (32).

Examples:

- `1950, Juli` — phrase 7354
- `1962, Juli` — phrase 7366
- `1962, Juni` — phrase 7370
- `1944, Sommer` — phrase 10060
- `1923, Oktober` — phrase 7534
- `1930, 7. Juni` — phrase 10369
- `1945, 17. Mai` — phrase 7384
- `1945, 18. Mai` — phrase 7385

Whether the Kentenich corpus should be translated at all is a decision for
the movement, not a gap for an agent to fill. It is **219 phrases on the
`text` route alone**, all with German source strings, and the pages that
render them need a signed-in session.


## German source material that does have an English rendering — 2

`skip-german-source-precedent`

German source material that does have an English rendering, so this one string has precedent — but the corpus should be decided as a whole, not string by string. Listed separately so the precedent is visible to whoever decides.

Text domains: Books (2).  
Routes: texts (2).

Examples:

- `1923, 16.-23. Dezember` — phrase 7392
- `131 der Ordnung hat in seine natürliche und übernatürliche Schöpfung eine wundersame Ordnung hin` … — phrase 7398


## Filenames — 65

`skip-filename`

A filename from the Kentenich text corpus, not a phrase. Translating it would change a string the corpus is indexed by.

Text domains: Books (65).  
Routes: text (53), texts (12).

Examples:

- `1966-0104-5V.md` — phrase 8243
- `1966-0104-6V.md` — phrase 10299
- `1962-0617PRED.md` — phrase 9400
- `1963-0106PRED.md` — phrase 9684
- `1963-0118t029.md` — phrase 7426
- `1963-0119t031.md` — phrase 7427
- `1963-0120FEIE.md` — phrase 7428
- `1963-0122t035.md` — phrase 9359


## Content belonging to one association record — 37

`skip-record-content`

Content of an association record that passed through translate(); it changes when a moderator edits the record, so a translation is stale immediately (docs/phrase-table-noise.md group 2).

Text domains: Schoenstatt (30), default (6), Books (1).  
Routes: associations/association/edit (14), association-edit (9), associations/association (6), associations/do-work (4), ….

Examples:

- `{collectionAbbreviation}%1$06.2f{author}{title}%2$02d` — phrase 7955
- a moderator's administrative note on one association, about that association's standing — phrase 6976 *(not quoted; the id is enough to find it)*
- `Turn right at the first driveway after getting off the highway. ⏎  ⏎ **Confession**: By appointm` … — phrase 6954
- `Directly on the big road, do not enter in the village of Thun-Saint-Martin. Coming from Cambrai,` … — phrase 7205
- `Founded in 2015, Patris' mission is to bring the Schoenstatt spirituality of the Catholic Church` … — phrase 6967
- `Used for linking to the association's Google Place, for example, for reviews. Use the <a href="h` … — phrase 6924
- `**Cómo llegar** ⏎  ⏎ Entras por Mederos camino al panteón Guadalupe al lado esta la entrada a la` … — phrase 7090
- `**Apertura**: ⏎  ⏎  7:00 hrs - 22:00 hrs ⏎  ⏎ **Misas**:  ⏎  ⏎ Domingo: 10:00 hrs, 19:00 hrs ⏎  ` … — phrase 6980


## Keys the application built by concatenation — 28

`skip-concatenated-key`

The application built this string by concatenation, so the variable part is baked into the key; it is not translatable as written and the fix is at the caller (docs/phrase-table-noise.md group 1).

Text domains: default (18), ZfcUser (6), SionModel (4).  
Routes: libraries/library/checkout (13), zfcuser/register (6), sion-model/view-changes (4), libraries/create (2), ….

Examples:

- `Assignment Id: 148` — phrase 6243
- `Assignment Id: 157` — phrase 6242
- `Assignment Id: 158` — phrase 6241
- `Assignment Id: 178` — phrase 6348
- `Error in form submission, please review: personId` — phrase 7054
- `Error in form submission, please review: security` — phrase 6955
- `Error in form submission, please review: adminNotes` — phrase 7436
- `'uc.cl ' is not a valid hostname for the email address` — phrase 8803


## Keys containing a credential — 4

`skip-leaked-secret`

The api-tokens screen appended a freshly issued JWT to its success message, so the token is baked into the phrase key and into the English row. Never translate it — a translation makes a third copy. The token needs revoking and the caller needs fixing.

Text domains: JUser (4).  
Routes: juser/user/api-tokens (4).

Examples:

- `Token issued. Copy it now — it is not shown again and we do not store it: eyJ0eXAiOiJKV1QiLCJhbG` … — phrase 13013
- `Token issued. Copy it now — it is not shown again and we do not store it: eyJ0eXAiOiJKV1QiLCJhbG` … — phrase 12940
- `Token issued. Copy it now — it is not shown again and we do not store it: eyJ0eXAiOiJKV1QiLCJhbG` … — phrase 12978
- `Token issued. Copy it now — it is not shown again and we do not store it: eyJ0eXAiOiJKV1QiLCJhbG` … — phrase 12996

**The token itself is deliberately not quoted here or anywhere in this
repository.** See `phrase-table-noise.md` section 4 for the handling: fix the
caller, revoke the four `jti`s, delete the rows.


## Copy from the retired welcome page — 12

`skip-dead-page`

Copy from the retired Laminas welcome page; the live Symfony page says something different in English (docs/phrase-table-noise.md group 3).

Text domains: Application (12).  
Routes: welcome (12).

Examples:

- `Learn more` — phrase 6285
- `Latest blog posts` — phrase 6727
- `translation edits` — phrase 6216
- `Update on advances` — phrase 6855
- `We need your help!` — phrase 6188
- `What is Schoenstatt Link?` — phrase 7161
- `Upcoming lauch: December 18th` — phrase 6728
- `Launch of new "Schoenstatt Shrines" app for Android!` — phrase 7074


## Nothing to translate — 8

`skip-nothing-to-translate`

No words in it — digits, punctuation or whitespace only.

Text domains: Books (7), Schoenstatt (1).  
Routes: text (4), publication-edit (2), texts (1), publication (1).

Examples:

- `1` — phrase 7478
- ` ` — phrase 7469
- `1946` — phrase 7345
- `2007` — phrase 7479
- `1945-1953` — phrase 9475
- `1914, 18. 10.` — phrase 10010
- `1914, 29. 06.` — phrase 11475
- `1916, 22. 05.` — phrase 10011


## Format templates — 4

`skip-format-template`

A format template, not prose: the placeholders are the whole string and the site interpolates into it.

Text domains: Books (4).  
Routes: libraries/library/edit (4).

Examples:

- `$2` — phrase 6388
- `$3` — phrase 6390
- `:short_category` — phrase 6385
- `%1$s%2$-8s%3$04d%4$03d%5$03d` — phrase 7712


## The site re-translating its own output — 1

`skip-retranslated-output`

The key is itself Italian: the site rendered an already-translated string back through translate() and captured it as a new phrase. Writing a translation here would legitimize a row that should not exist.

Text domains: JUser (1).  
Routes: zfcuser/register (1).

Examples:

- `Registrati` — phrase 13032
