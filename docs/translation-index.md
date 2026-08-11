# Translation index — which page shows which untranslated phrase

The hard part of this work is not translating; it is seeing the phrase in place.
This index maps the untranslated Italian backlog onto concrete pages, so it can be
worked through one page at a time instead of one database row at a time.

Snapshot of the **capsule** on 2026-08-10, rebuilt after the deduplication and the
blog cleanup. Every URL below was re-fetched and checked against the route its own
footer reports; all 109 still stand. Regenerate rather than trust the counts after a
writing session — the queries are at the bottom.

## How to use it

1. Open the URL. It already carries the `/it/` prefix, and **an untranslated phrase
   renders as its source string** — so the Italian page is itself the worklist:
   whatever still reads as English (or German, or Spanish) is what is missing.
2. Open the same path under `/en/`, `/es/`, `/de/` or `/pt/` to see how the other
   languages rendered those strings. That is a better guide to register and house
   convention than translating cold — it is how the `(Schoenstatt Shrines)`
   parenthetical and the informal *tu* register were discovered.
3. `phrase_search` with `origin_route` and `untranslated_in: "it"` gives the ids;
   `phrase_batch_patch` writes them in one call.

A worked example — `/it/SL100458A/schoenstatt-shrine-mont-sion-gikungu` renders
`Accedi`, `8 anni fa` and `23 ottobre 1994` in Italian, while `Contact Info`,
`Foundation date:`, `Country:` and `Parent organization:` are still English. Those
four are the work, and they are visible without consulting anything.

### One capsule page lies to you

`language/Books/it_IT.lang.php` in the application checkout is a **leftover
benchmark fixture**: 157 entries whose every value reads `prova di misurazione 6388`
and so on. There are no Italian Books translations in the database at all. The
exporter overwrites catalogs but never deletes them, so the file survives every
rebuild and the site keeps serving it.

So on a Books page under `/it/`, a string rendering as plausible-looking Italian may
be that fixture rather than a translation. **Trust the API, not the page, for what is
already translated.** `phrase_search(untranslated_in="it")` reads the database and is
not fooled. This is a capsule artefact; it is worth deleting the file, which is a
change for a session working on the application.

## Superseded in part by the 2026-08-10 translation pass

**Every count below is the state before that pass.** The capsule now holds **1,420
phrases with Italian and 396 without**, and the 396 are deliberate — see
[`it-skipped.md`](it-skipped.md). The 109 URLs still stand and are still the right way
to see a phrase in place; it is the numbers that have moved.

Three corrections that came out of actually opening the pages:

**1. The `n` column undercounts what a screen shows, badly.** `n` is *distinct
untranslated phrases first seen on that route* — which attributes each shared template
string to exactly one route. A shrine detail page is listed at `n = 12`; it actually
rendered **48 to 60** untranslated strings, because `Country`, `Website`, `Phone`,
`Admin notes` and the rest were each credited to whichever route happened to trigger
them first. Use [`tools/screens.py`](../tools/screens.py) for what a page really shows:
it fetches the page and finds each backlog phrase in the markup, with the enclosing
element.

**2. Most of the backlog is not on any public page.** Of 1,745 phrases, **399 were
visible on at least one** of the 109 URLs. The other 1,346 are on sign-in-gated screens,
on edit forms, or on no page at all. "Open the Italian page and translate what looks
English" is a good way to work through a *quarter* of it.

**3. Some English on the Italian page cannot be translated at all.** The breadcrumb
partial renders its labels without calling `translate()`, so a shrine page shows
`Shrines` in the breadcrumb and `Santuari` in the navigation — the same word, one
translated and one not. Do not chase it; it is an application fix. See
[`phrase-table-noise.md`](phrase-table-noise.md) section 8.

**4. The element a string sits in decides the Italian**, and the index cannot tell you
that. `Search` in a `<button>` wants the imperative `Cerca`; the same word as a column
header would want a noun. `tools/screens.py` records the enclosing tag for exactly this
reason, and it is what settled several dozen of the short labels.

## Read this before trusting any count

| | |
|---|---|
| Phrases for this project, not retired | **1,815** |
| …with no usable Italian | **1,795** |
| …whose source string is **not** English | **164** |
| Phrases that have Italian | 20 |

**These are phrases, not rows, and the two now agree.** `trans_phrases` grew a
`UNIQUE (project, text_domain, phrase_hash)` constraint and its duplicates were
merged; the blog's phrases were deleted outright. The table went from 6,874 rows to
1,815, and none of that difference was work. An older version of this document
warned that the corpus was four times smaller than the row count suggested — that is
no longer a caveat, it is just the count.

`phrase_search` still collapses identical source strings and reports the collapsed
ids in `duplicate_phrase_ids`. It should now find nothing to collapse within a text
domain, and that is the point of leaving it in.

**Retired phrases are never in the collection.** `jtranslate:retire` takes a string
off the worklist without destroying it, and there is no parameter to ask for them
back. If a retired phrase turns out to still be rendered, the site un-retires it by
itself on the next page load — so a phrase appearing that you have not seen before is
normal and does not mean anything is wrong.

## The source string is often not English on exactly these pages

164 of the 1,795 have a non-English source, and they cluster in the pages with the
most work:

| route | non-English sources |
|---|---|
| `associations/association` | 51 |
| `publications/publication` | 37 |
| `associations/association/edit` | 31 |
| `association-edit` | 17 |
| `zfcuser/register` | 3 |
| `persons/person` | 3 |

They are mostly shrine and publication proper names — `Cenáculo de Bellavista`
(Spanish), `Coenaculum-Heiligtum` (German), `Liebesheiligtum` (German). The site
does **not** leave these alone: German renders the first as
`Coenaculumsheiligtum Bellavista`, Spanish renders the second as
`Santuario del Cenáculo`. So these are decisions about what a shrine is called in
Italian — charism vocabulary, not translation — and they are the ones to ask about
rather than guess.

Two reliable tests, neither of which needs judgement:

- **Any phrase**: compare the source string with its own English row. Identical
  means the source is English; different means the English row is itself a
  translation and the source is another language.
- **Text pages**: `texts.Language` records the source language outright, and all 60
  text pages carry `de`. They are in the signed-in section below.

## Where the work actually is

| text domain | phrases | missing Italian |
|---|---|---|
| `Books` | 802 | 802 |
| `Schoenstatt` | 698 | 691 |
| `default` | 87 | 87 |
| `JUser` | 76 | 73 |
| `SionModel` | 43 | 42 |
| `Application` | 36 | 29 |
| `ZfcUser` | 29 | 29 |
| `JTranslate` | 25 | 25 |
| `Bible` | 19 | 17 |

**`Books` is 45% of the backlog and barely appears in the URL list below** — only
`books/book` (25) is reachable, and the library pages are behind a sign-in. It is
also the domain where a wrong answer is most likely: a book with a real published
Italian edition needs that edition's title found, not a title invented. Treat it as
research, not translation, and do it last.

`Application`, `Bible` and `SionModel` are small, mostly UI, and mostly visible on
the pages below. They are the sane place to start.

## Pages you can open right now

109 URLs, each re-fetched and checked against the route its own footer
reports — a page that redirected, or rendered something other than what this index
claims, was dropped rather than listed. 33 are listing and section pages the crawl reached, 76 are shrine detail pages generated from association ids.

`n` is the distinct untranslated phrases first seen on that route. On a detail page
most of those are shared template strings that appear on every such page — so the
template is worth doing once, from any one of them — and the entity's own name is
the part unique to that page.

Publication pages here are the ones the crawl reached directly. Publication URLs
*generated* from ids were dropped: they 301 to a canonical id, and the check will
not list a URL that moves. Build them from the id the site itself links to.

| # | URL | route | n | this page's own untranslated string |
|---|---|---|---|---|
| 1 | `/it/literature` | `publications` | 75 |  |
| 2 | `/it/` | `welcome` | 33 |  |
| 3 | `/it/shrines` | `shrines` | 23 |  |
| 4 | `/it/user/register` | `zfcuser/register` | 23 |  |
| 5 | `/it/libraries/1` | `libraries/library` | 21 |  |
| 6 | `/it/libraries/3` | `libraries/library` | 21 |  |
| 7 | `/it/libraries/6` | `libraries/library` | 21 |  |
| 8 | `/it/libraries/7` | `libraries/library` | 21 |  |
| 9 | `/it/literature/de` | `publications/index` | 21 |  |
| 10 | `/it/literature/en` | `publications/index` | 21 |  |
| 11 | `/it/literature/es` | `publications/index` | 21 |  |
| 12 | `/it/literature/fr` | `publications/index` | 21 |  |
| 13 | `/it/SL100359A/schoenstatt-shrine-isingiro` | `association` | 12 |  |
| 14 | `/it/SL100361A/schoenstatt-shrine-mutumba` | `association` | 12 |  |
| 15 | `/it/SL100458A/schoenstatt-shrine-mont-sion-gikungu` | `association` | 12 |  |
| 16 | `/it/SL100504A/schoenstatt-shrine-ibadan` | `association` | 12 |  |
| 17 | `/it/SL202139L/la-croix-de-l-unite` | `publication` | 9 |  |
| 18 | `/it/SL202154L/les-annees-cachees-pere-joseph-kentenich-enfance-e` | `publication` | 9 |  |
| 19 | `/it/SL202157L/les-documents-de-fondation` | `publication` | 9 |  |
| 20 | `/it/SL202158L/bienheureux-karl-leisner-jusqu-au-bout-de-l-amour` | `publication` | 9 |  |
| 21 | `/it/SL500240C/my-queen-my-mother` | `composition` | 4 |  |
| 22 | `/it/SL500320C/kyrie-eleison` | `composition` | 4 |  |
| 23 | `/it/SL500369C/lord-i-need-you` | `composition` | 4 |  |
| 24 | `/it/SL500372C/website-with-many-schoenstatt-songs` | `composition` | 4 |  |
| 25 | `/it/dictionary` | `dictionary` | 4 |  |
| 26 | `/it/libraries/create` | `libraries/create` | 2 |  |
| 27 | `/it/developers` | `developers` | 1 |  |
| 28 | `/it/dictionary/es` | `dictionary/inLanguage` | 1 |  |
| 29 | `/it/dictionary/pt` | `dictionary/inLanguage` | 1 |  |
| 30 | `/it/shrines/submitting-photos` | `shrines/submitting-photos` | 1 |  |
| 31 | `/it/wayside-shrines` | `wayside-shrines` | 1 |  |
| 32 | `/it/literature/150-preguntas-sobre-schoenstatt` | `publications/one-fifty-preguntas` | 0 |  |
| 33 | `/it/music` | `music` | 0 |  |
| 34 | `/it/SL100319A/original-schoenstatt-shrine` | `association` | 12 | Original Schoenstatt Shrine |
| 35 | `/it/SL100320A/schoenstatt-shrine-nueva-helvecia` | `association` | 12 | Nueva Helvecia |
| 36 | `/it/SL100321A/schoenstatt-shrine-santa-maria` | `association` | 12 | Santa Maria |
| 37 | `/it/SL100322A/cenacle-of-bellavista` | `association` | 12 | Cenáculo de Bellavista ⚠️ non-English |
| 38 | `/it/SL100323A/schoenstatt-shrine-mission-for-africa` | `association` | 12 | Mission for Africa |
| 39 | `/it/SL100324A/schoenstatt-shrine-londrina` | `association` | 12 | Londrina |
| 40 | `/it/SL100325A/schoenstatt-shrine-euskirchen` | `association` | 12 | Euskirchen |
| 41 | `/it/SL100326A/schoenstatt-shrine-st-gallen` | `association` | 12 | St. Gallen |
| 42 | `/it/SL100327A/schoenstatt-shrine-koblenz-metternich` | `association` | 12 | Koblenz-Metternich |
| 43 | `/it/SL100328A/schoenstatt-shrine-bocholt` | `association` | 12 | Bocholt |
| 44 | `/it/SL100329A/schoenstatt-shrine-kreuzland-kapellchen` | `association` | 12 | Kreuzland-Kapellchen |
| 45 | `/it/SL100330A/national-schoenstatt-shrine-florencio-varela` | `association` | 12 | Santuario de Schoenstatt Nacional, Florencio Varela ⚠️ non-English |
| 46 | `/it/SL100331A/schoenstatt-shrine-bahia-blanca-buenos-aires` | `association` | 12 | Bahía Blanca, Buenos Aires |
| 47 | `/it/SL100332A/schoenstatt-shrine-mitgruenderheiligtum` | `association` | 12 | Mitgründerheiligtum |
| 48 | `/it/SL100333A/schoenstatt-shrine-melbourne` | `association` | 12 | Melbourne |
| 49 | `/it/SL100334A/schoenstatt-shrine-ver-sacrum` | `association` | 12 | Ver Sacrum |
| 50 | `/it/SL100335A/schoenstatt-shrine-madison-wisconsin` | `association` | 12 | Madison, Wisconsin |
| 51 | `/it/SL100336A/schoenstatt-shrine-triumphatrix` | `association` | 12 | Triumphatrix |
| 52 | `/it/SL100337A/schoenstatt-shrine-mariengartenheiligtum` | `association` | 12 | Mariengartenheiligtum |
| 53 | `/it/SL100338A/schoenstatt-shrine-fribourg` | `association` | 12 | Fribourg |
| 54 | `/it/SL100339A/schoenstatt-shrine-milwaukee-wisconsin` | `association` | 12 | Milwaukee, Wisconsin |
| 55 | `/it/SL100340A/schoenstatt-shrine-friedrichroda` | `association` | 12 | Friedrichroda |
| 56 | `/it/SL100341A/schoenstatt-shrine-mannheim` | `association` | 12 | Mannheim |
| 57 | `/it/SL100342A/schoenstatt-shrine-quarten` | `association` | 12 | Quarten |
| 58 | `/it/SL100343A/schoenstatt-shrine-meppen` | `association` | 12 | Meppen |
| 59 | `/it/SL100344A/schoenstatt-shrine-dortmund-frohlinde` | `association` | 12 | Dortmund-Frohlinde |
| 60 | `/it/SL100345A/schoenstatt-shrine-obera-misiones` | `association` | 12 | Oberá, Misiones |
| 61 | `/it/SL100346A/schoenstatt-shrine-dietershausen-fulda` | `association` | 12 | Dietershausen (Fulda) |
| 62 | `/it/SL100347A/schoenstatt-shrine-muenster` | `association` | 12 | Münster |
| 63 | `/it/SL100348A/schoenstatt-shrine-muenchen-klein-schoenstatt` | `association` | 12 | München, Klein-Schönstatt |
| 64 | `/it/SL100349A/schoenstatt-shrine-oberkirch` | `association` | 12 | Oberkirch |
| 65 | `/it/SL100350A/schoenstatt-shrine-lamar-texas` | `association` | 12 | Lamar, Texas |
| 66 | `/it/SL100351A/schoenstatt-shrine-solidarity-in-the-covenant-of-l` | `association` | 12 | Solidarity in the Covenant of Love |
| 67 | `/it/SL100352A/schoenstatt-shrine-borken` | `association` | 12 | Borken |
| 68 | `/it/SL100353A/schoenstatt-shrine-gelsenkirchen-horst` | `association` | 12 | Gelsenkirchen-Horst |
| 69 | `/it/SL100354A/schoenstatt-shrine-gossau` | `association` | 12 | Gossau |
| 70 | `/it/SL100355A/schoenstatt-shrine-wuerzburg` | `association` | 12 | Würzburg |
| 71 | `/it/SL100356A/schoenstatt-shrine-haus-regina` | `association` | 12 | Haus Regina |
| 72 | `/it/SL100357A/schoenstatt-shrine-belgrano-buenos-aires` | `association` | 12 | Belgrano, Buenos Aires |
| 73 | `/it/SL100358A/schoenstatt-shrine-koeln` | `association` | 12 | Köln |
| 74 | `/it/SL100360A/schoenstatt-shrine-waukesha-wisconsin` | `association` | 12 | Waukesha, Wisconsin |
| 75 | `/it/SL100362A/schoenstatt-shrine-la-plata` | `association` | 12 | La Plata |
| 76 | `/it/SL100363A/schoenstatt-shrine-cambrai` | `association` | 12 | Cambrai |
| 77 | `/it/SL100364A/schoenstatt-shrine-haus-mariengart-frauenbund` | `association` | 12 | Haus Mariengart (Frauenbund) |
| 78 | `/it/SL100365A/schoenstatt-shrine-memhoelz` | `association` | 12 | Memhölz |
| 79 | `/it/SL100366A/schoenstatt-shrine-mulgoa` | `association` | 12 | Mulgoa |
| 80 | `/it/SL100367A/schoenstatt-shrine-herxheim` | `association` | 12 | Herxheim |
| 81 | `/it/SL100368A/schoenstatt-shrine-villa-warcalde-cordoba` | `association` | 12 | Villa Warcalde, Córdoba |
| 82 | `/it/SL100369A/schoenstatt-shrine-ayinrehue` | `association` | 12 | Ayinrehue |
| 83 | `/it/SL100370A/schoenstatt-shrine-koesching-canisiushof` | `association` | 12 | Kösching (Canisiushof) |
| 84 | `/it/SL100371A/schoenstatt-shrine-jaragua` | `association` | 12 | Jaraguá |
| 85 | `/it/SL100372A/schoenstatt-shrine-stuttgart-freiberg` | `association` | 12 | Stuttgart-Freiberg |
| 86 | `/it/SL100373A/schoenstatt-shrine-madrid-pozuelo` | `association` | 12 | Madrid Pozuelo |
| 87 | `/it/SL100374A/schoenstatt-shrine-agua-santa` | `association` | 12 | Agua Santa |
| 88 | `/it/SL100375A/schoenstatt-shrine-aloor-kerala` | `association` | 12 | Aloor, Kerala |
| 89 | `/it/SL100376A/schoenstatt-shrine-berlin-frohnau` | `association` | 12 | Berlin-Frohnau |
| 90 | `/it/SL100377A/schoenstatt-shrine-vila-mariana` | `association` | 12 | Vila Mariana |
| 91 | `/it/SL100378A/schoenstatt-shrine-berg-sion` | `association` | 12 | Berg Sion |
| 92 | `/it/SL100379A/schoenstatt-shrine-wuenschberg` | `association` | 12 | Wünschberg |
| 93 | `/it/SL100380A/schoenstatt-shrine-endel-oldenburg` | `association` | 12 | Endel (Oldenburg) |
| 94 | `/it/SL100381A/schoenstatt-shrine-puffendorf` | `association` | 12 | Puffendorf |
| 95 | `/it/SL100382A/schoenstatt-shrine-concepcion` | `association` | 12 | Concepción |
| 96 | `/it/SL100383A/schoenstatt-shrine-wiesbaden-freudenberg` | `association` | 12 | Wiesbaden-Freudenberg |
| 97 | `/it/SL100384A/schoenstatt-shrine-family-institute` | `association` | 12 | Family Institute |
| 98 | `/it/SL100385A/schoenstatt-shrine-essen-kray` | `association` | 12 | Essen-Kray |
| 99 | `/it/SL100397A/schoenstatt-shrine-adoration-sisters-of-mary` | `association` | 12 | Adoration Sisters of Mary |
| 100 | `/it/SL100435A/schoenstatt-shrine-bangalore-schoenstatt-sisters-o` | `association` | 12 | Bangalore, Schoenstatt Sisters of Mary |
| 101 | `/it/SL100461A/schoenstatt-shrine-brothers-of-mary` | `association` | 12 | Brothers of Mary |
| 102 | `/it/SL100466A/schoenstatt-shrine-sion-of-the-trinity` | `association` | 12 | Sión de la Trinidad ⚠️ non-English |
| 103 | `/it/SL100467A/santuario-de-schoenstatt-asuncion` | `association` | 12 | Santuario de Schoenstatt Asunción |
| 104 | `/it/SL100491A/schoenstatt-shrine-cordoba-fr-kentenich-center-cpk` | `association` | 12 | Córdoba, Centro Padre José Kentenich ⚠️ non-English |
| 105 | `/it/SL100501A/schoenstatt-shrine-bangalore-schoenstatt-fathers` | `association` | 12 | Bangalore, Schoenstatt Fathers |
| 106 | `/it/SL100503A/schoenstatt-shrine-hatillo-monastery` | `association` | 12 | Hatillo (Monastery) |
| 107 | `/it/SL100506A/schoenstatt-shrine-quito-santuario-ciudad` | `association` | 12 | Quito, Santuario Ciudad ⚠️ non-English |
| 108 | `/it/SL100524A/future-shrine-of-san-luis` | `association` | 12 | Futuro Santuario San Luis ⚠️ non-English |
| 109 | `/it/SL100567A/schoenstatt-wayside-shrine-la-castille-diocese-of` | `association` | 12 | La Castille (Diocèse de Fréjus-Toulon) ⚠️ non-English |

## Pages that need a signed-in human

64 of the URLs checked redirect to `/it/user/login`. **The API bot
account cannot open any of them** — it holds `sch_api_translator`, which by design
opens no web page at all. They are still real work; they just cannot be seen in
context without a session.

| route | pages gated | n untranslated |
|---|---|---|
| `text` | 60 | 219 |
| `zfcuser/login` | 4 | 21 |

The whole of `text` is in here: 219 untranslated phrases, all with German source
strings (Kentenich conference material — `**2. Vortrag**`,
`10. Oktober 1934, vormittags`). It is the single largest route in the backlog and
the least accessible. Worth deciding deliberately whether it should be translated
at all before anyone starts.

## Routes with work and no URL here

Mostly edit forms, admin screens and moderator tools, reachable only when signed
in. Translate these from `phrase_search` output and the wording of the surrounding
screen.

| route | n | non-EN |
|---|---|---|
| `associations/association` | 151 | 51 |
| `associations/association/edit` | 149 | 31 |
| `publications/publication` | 125 | 37 |
| `texts` | 90 | 1 |
| `publications/create` | 57 | 1 |
| `libraries/library/edit` | 47 | 1 |
| `persons/create` | 46 |  |
| `publications/publication/edit` | 39 |  |
| `sion-model/view-changes` | 38 | 2 |
| `libraries/library/admin` | 37 |  |
| `association-edit` | 37 | 17 |
| `associations` | 36 |  |
| `books/book` | 25 | 1 |
| `juser/user/api-tokens` | 25 |  |
| `music/create-composition` | 21 |  |
| `libraries/library/checkout` | 20 | 1 |
| `(none)` | 19 |  |
| `home` | 17 | 1 |
| `libraries` | 17 | 1 |
| `juser/create` | 17 |  |
| `assignments` | 16 | 1 |
| `admin` | 15 | 1 |
| `associations/do-work` | 14 | 1 |
| `libraries/library/send-book-notices` | 14 |  |
| `persons/person` | 13 | 3 |
| `juser` | 13 |  |
| `library-imports/library` | 10 |  |
| `composition-edit` | 10 |  |
| `associations/create` | 9 | 1 |
| `persons/person/edit` | 9 | 2 |
| `library-imports/library-import/edit` | 8 |  |
| `roles` | 8 |  |
| `libraries/library/label-management` | 8 |  |
| `library-imports/library/create` | 7 |  |
| `assignments/create` | 7 |  |
| `schoenstatt` | 7 |  |
| `publications/search` | 7 |  |
| `books/book/edit` | 7 |  |
| `assignments/assignment/edit` | 7 | 1 |
| `borrowers/borrower` | 7 |  |
| `bible/create-greek-reference` | 6 |  |
| `roles/role/edit` | 6 |  |
| `jtranslate` | 6 |  |
| `admin/import-father` | 5 |  |
| `bible/greek/root/edit` | 5 |  |
| `publication-edit` | 5 |  |
| `collections/collection/edit` | 5 |  |
| `sion-model/data-problems` | 5 | 1 |
| `texts/create` | 5 |  |

## Regenerating this

```sql
-- phrases with no usable Italian, by route. `retired_on IS NULL` matters now:
-- a retired phrase is off the worklist and out of the API collection.
SELECT COALESCE(NULLIF(p.origin_route,''),'(none)') AS route, COUNT(*) AS untranslated_it
FROM trans_phrases p
LEFT JOIN trans_translations t
       ON t.translation_phrase_id = p.translation_phrase_id
      AND t.locale = 'it_IT' AND TRIM(t.translation) <> ''
WHERE p.project = 'Schoenstatt' AND p.retired_on IS NULL AND t.translation_id IS NULL
GROUP BY route ORDER BY untranslated_it DESC;

-- phrases whose source string is not English
SELECT p.phrase AS source_key, t_en.translation AS english_row
FROM trans_phrases p
JOIN trans_translations t_en
     ON t_en.translation_phrase_id = p.translation_phrase_id
    AND t_en.locale = 'en_US' AND TRIM(t_en.translation) <> ''
    AND TRIM(t_en.translation) <> TRIM(p.phrase)
WHERE p.project = 'Schoenstatt' AND p.retired_on IS NULL;
```

`COUNT(*)` is now the same as `COUNT(DISTINCT phrase)` within a text domain — the
unique constraint guarantees it. Before the cleanup it was not, and counting rows
gave an answer four times too large.

Detail-page URLs are built from the entity id: `SL` + (offset + id) + a type
letter, per `module/Schoenstatt/src/Validator/SchoenstattLinkIdentifier.php` —
association 100000/`A`, publication 200000/`L`, person 300000/`P`, text 400000/`T`,
composition 500000/`C`. Listing URLs come from crawling the capsule in Italian and
reading each page's own route name out of its footer (`· route <name> ·`), which is
authoritative in a way that guessing from route config is not; footer names carry a
`.locale` suffix that `origin_route` does not.

The database keys translations as `it_IT`; the API presents `it`. That is the
internal keying the API deliberately hides — see CLAUDE.md.
