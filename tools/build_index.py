import json
import collections
import os
import sys

if len(sys.argv) < 2:
    sys.exit(f"usage: python3 {sys.argv[0]} <scratch-dir>")
SC = sys.argv[1]

# The index lands in this repository, wherever it happens to be checked out — so derive
# the root from this file rather than from the working directory.
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f"{REPO}/docs/translation-index.md"

verified = json.load(open(f"{SC}/verified.json"))
rows = json.load(open(f"{SC}/final_urls2.json"))

counts, nonen = {}, {}
for path, target in [("route_counts2.tsv", counts), ("nonenglish2.tsv", nonen)]:
    for line in open(f"{SC}/{path}"):
        p = line.rstrip("\n").split("\t")
        if len(p) == 2 and p[1].isdigit():
            target[p[0]] = int(p[1])

gated = [c for c in verified if c["note"] == "sign-in required"]

order = {"listing": 0, "association": 1, "publication": 2, "text": 3}
rows.sort(key=lambda c: (order.get(c["kind"], 9), -counts.get(c["route"], 0), c["url"]))

by_kind = collections.Counter(c["kind"] for c in rows)
gated_by_route = collections.Counter(c["route"] for c in gated)

w = open(OUT, "w").write

w("# Translation index — which page shows which untranslated phrase\n\n")
w("The hard part of this work is not translating; it is seeing the phrase in place.\n")
w("This index maps the untranslated Italian backlog onto concrete pages, so it can be\n")
w("worked through one page at a time instead of one database row at a time.\n\n")
w("Snapshot of the **capsule** on 2026-08-10, rebuilt after the deduplication and the\n")
w("blog cleanup. Every URL below was re-fetched and checked against the route its own\n")
w("footer reports; all 109 still stand. Regenerate rather than trust the counts after a\n")
w("writing session — the queries are at the bottom.\n\n")

w("## How to use it\n\n")
w("1. Open the URL. It already carries the `/it/` prefix, and **an untranslated phrase\n")
w("   renders as its source string** — so the Italian page is itself the worklist:\n")
w("   whatever still reads as English (or German, or Spanish) is what is missing.\n")
w("2. Open the same path under `/en/`, `/es/`, `/de/` or `/pt/` to see how the other\n")
w("   languages rendered those strings. That is a better guide to register and house\n")
w("   convention than translating cold — it is how the `(Schoenstatt Shrines)`\n")
w("   parenthetical and the informal *tu* register were discovered.\n")
w("3. `phrase_search` with `origin_route` and `untranslated_in: \"it\"` gives the ids;\n")
w("   `phrase_batch_patch` writes them in one call.\n\n")
w("A worked example — `/it/SL100458A/schoenstatt-shrine-mont-sion-gikungu` renders\n")
w("`Accedi`, `8 anni fa` and `23 ottobre 1994` in Italian, while `Contact Info`,\n")
w("`Foundation date:`, `Country:` and `Parent organization:` are still English. Those\n")
w("four are the work, and they are visible without consulting anything.\n\n")

w("### One capsule page lies to you\n\n")
w("`language/Books/it_IT.lang.php` in the application checkout is a **leftover\n")
w("benchmark fixture**: 157 entries whose every value reads `prova di misurazione 6388`\n")
w("and so on. There are no Italian Books translations in the database at all. The\n")
w("exporter overwrites catalogs but never deletes them, so the file survives every\n")
w("rebuild and the site keeps serving it.\n\n")
w("So on a Books page under `/it/`, a string rendering as plausible-looking Italian may\n")
w("be that fixture rather than a translation. **Trust the API, not the page, for what is\n")
w("already translated.** `phrase_search(untranslated_in=\"it\")` reads the database and is\n")
w("not fooled. This is a capsule artefact; it is worth deleting the file, which is a\n")
w("change for a session working on the application.\n\n")

w("## Read this before trusting any count\n\n")
w("| | |\n|---|---|\n")
w("| Phrases for this project, not retired | **1,815** |\n")
w("| …with no usable Italian | **1,795** |\n")
w("| …whose source string is **not** English | **164** |\n")
w("| Phrases that have Italian | 20 |\n\n")
w("**These are phrases, not rows, and the two now agree.** `trans_phrases` grew a\n")
w("`UNIQUE (project, text_domain, phrase_hash)` constraint and its duplicates were\n")
w("merged; the blog's phrases were deleted outright. The table went from 6,874 rows to\n")
w("1,815, and none of that difference was work. An older version of this document\n")
w("warned that the corpus was four times smaller than the row count suggested — that is\n")
w("no longer a caveat, it is just the count.\n\n")
w("`phrase_search` still collapses identical source strings and reports the collapsed\n")
w("ids in `duplicate_phrase_ids`. It should now find nothing to collapse within a text\n")
w("domain, and that is the point of leaving it in.\n\n")
w("**Retired phrases are never in the collection.** `jtranslate:retire` takes a string\n")
w("off the worklist without destroying it, and there is no parameter to ask for them\n")
w("back. If a retired phrase turns out to still be rendered, the site un-retires it by\n")
w("itself on the next page load — so a phrase appearing that you have not seen before is\n")
w("normal and does not mean anything is wrong.\n\n")

w("## The source string is often not English on exactly these pages\n\n")
w("164 of the 1,795 have a non-English source, and they cluster in the pages with the\n")
w("most work:\n\n")
w("| route | non-English sources |\n|---|---|\n")
for r, n in sorted(nonen.items(), key=lambda kv: -kv[1])[:6]:
    w(f"| `{r}` | {n} |\n")
w("\nThey are mostly shrine and publication proper names — `Cenáculo de Bellavista`\n")
w("(Spanish), `Coenaculum-Heiligtum` (German), `Liebesheiligtum` (German). The site\n")
w("does **not** leave these alone: German renders the first as\n")
w("`Coenaculumsheiligtum Bellavista`, Spanish renders the second as\n")
w("`Santuario del Cenáculo`. So these are decisions about what a shrine is called in\n")
w("Italian — charism vocabulary, not translation — and they are the ones to ask about\n")
w("rather than guess.\n\n")
w("Two reliable tests, neither of which needs judgement:\n\n")
w("- **Any phrase**: compare the source string with its own English row. Identical\n")
w("  means the source is English; different means the English row is itself a\n")
w("  translation and the source is another language.\n")
w("- **Text pages**: `texts.Language` records the source language outright, and all 60\n")
w("  text pages carry `de`. They are in the signed-in section below.\n\n")

w("## Where the work actually is\n\n")
w("| text domain | phrases | missing Italian |\n|---|---|---|\n")
for dom, ph, miss in [
    ("Books", "802", "802"), ("Schoenstatt", "698", "691"), ("default", "87", "87"),
    ("JUser", "76", "73"), ("SionModel", "43", "42"), ("Application", "36", "29"),
    ("ZfcUser", "29", "29"), ("JTranslate", "25", "25"), ("Bible", "19", "17"),
]:
    w(f"| `{dom}` | {ph} | {miss} |\n")
w("\n**`Books` is 45% of the backlog and barely appears in the URL list below** — only\n")
w("`books/book` (25) is reachable, and the library pages are behind a sign-in. It is\n")
w("also the domain where a wrong answer is most likely: a book with a real published\n")
w("Italian edition needs that edition's title found, not a title invented. Treat it as\n")
w("research, not translation, and do it last.\n\n")
w("`Application`, `Bible` and `SionModel` are small, mostly UI, and mostly visible on\n")
w("the pages below. They are the sane place to start.\n\n")

w("## Pages you can open right now\n\n")
w(f"{len(rows)} URLs, each re-fetched and checked against the route its own footer\n")
w("reports — a page that redirected, or rendered something other than what this index\n")
w("claims, was dropped rather than listed. ")
w(f"{by_kind['listing']} are listing and section pages the crawl reached, "
  f"{by_kind['association']} are shrine detail pages generated from association ids.\n\n")
w("`n` is the distinct untranslated phrases first seen on that route. On a detail page\n")
w("most of those are shared template strings that appear on every such page — so the\n")
w("template is worth doing once, from any one of them — and the entity's own name is\n")
w("the part unique to that page.\n\n")
w("Publication pages here are the ones the crawl reached directly. Publication URLs\n")
w("*generated* from ids were dropped: they 301 to a canonical id, and the check will\n")
w("not list a URL that moves. Build them from the id the site itself links to.\n\n")
w("| # | URL | route | n | this page's own untranslated string |\n|---|---|---|---|---|\n")
for i, c in enumerate(rows, 1):
    own = c.get("own_phrase", "")
    if own and c.get("src") == "non-English":
        own = f"{own} ⚠️ non-English"
    elif own and c.get("src") == "de":
        own = f"{own} ⚠️ German"
    url = c.get("final") or c["url"]
    w(f"| {i} | `{url}` | `{c['route']}` | {counts.get(c['route'], 0)} | {own} |\n")

w("\n## Pages that need a signed-in human\n\n")
w(f"{len(gated)} of the URLs checked redirect to `/it/user/login`. **The API bot\n")
w("account cannot open any of them** — it holds `sch_api_translator`, which by design\n")
w("opens no web page at all. They are still real work; they just cannot be seen in\n")
w("context without a session.\n\n")
w("| route | pages gated | n untranslated |\n|---|---|---|\n")
for r, n in gated_by_route.most_common():
    w(f"| `{r}` | {n} | {counts.get(r, 0)} |\n")
w("\nThe whole of `text` is in here: 219 untranslated phrases, all with German source\n")
w("strings (Kentenich conference material — `**2. Vortrag**`,\n")
w("`10. Oktober 1934, vormittags`). It is the single largest route in the backlog and\n")
w("the least accessible. Worth deciding deliberately whether it should be translated\n")
w("at all before anyone starts.\n\n")

w("## Routes with work and no URL here\n\n")
w("Mostly edit forms, admin screens and moderator tools, reachable only when signed\n")
w("in. Translate these from `phrase_search` output and the wording of the surrounding\n")
w("screen.\n\n")
w("| route | n | non-EN |\n|---|---|---|\n")
covered = {c["route"] for c in rows} | set(gated_by_route)
for r, n in sorted(counts.items(), key=lambda kv: -kv[1]):
    if r not in covered and n > 4:
        w(f"| `{r}` | {n} | {nonen.get(r, '') or ''} |\n")

w("\n## Regenerating this\n\n")
w("```sql\n")
w("-- phrases with no usable Italian, by route. `retired_on IS NULL` matters now:\n")
w("-- a retired phrase is off the worklist and out of the API collection.\n")
w("SELECT COALESCE(NULLIF(p.origin_route,''),'(none)') AS route, COUNT(*) AS untranslated_it\n")
w("FROM trans_phrases p\n")
w("LEFT JOIN trans_translations t\n")
w("       ON t.translation_phrase_id = p.translation_phrase_id\n")
w("      AND t.locale = 'it_IT' AND TRIM(t.translation) <> ''\n")
w("WHERE p.project = 'Schoenstatt' AND p.retired_on IS NULL AND t.translation_id IS NULL\n")
w("GROUP BY route ORDER BY untranslated_it DESC;\n\n")
w("-- phrases whose source string is not English\n")
w("SELECT p.phrase AS source_key, t_en.translation AS english_row\n")
w("FROM trans_phrases p\n")
w("JOIN trans_translations t_en\n")
w("     ON t_en.translation_phrase_id = p.translation_phrase_id\n")
w("    AND t_en.locale = 'en_US' AND TRIM(t_en.translation) <> ''\n")
w("    AND TRIM(t_en.translation) <> TRIM(p.phrase)\n")
w("WHERE p.project = 'Schoenstatt' AND p.retired_on IS NULL;\n")
w("```\n\n")
w("`COUNT(*)` is now the same as `COUNT(DISTINCT phrase)` within a text domain — the\n")
w("unique constraint guarantees it. Before the cleanup it was not, and counting rows\n")
w("gave an answer four times too large.\n\n")
w("Detail-page URLs are built from the entity id: `SL` + (offset + id) + a type\n")
w("letter, per `module/Schoenstatt/src/Validator/SchoenstattLinkIdentifier.php` —\n")
w("association 100000/`A`, publication 200000/`L`, person 300000/`P`, text 400000/`T`,\n")
w("composition 500000/`C`. Listing URLs come from crawling the capsule in Italian and\n")
w("reading each page's own route name out of its footer (`· route <name> ·`), which is\n")
w("authoritative in a way that guessing from route config is not; footer names carry a\n")
w("`.locale` suffix that `origin_route` does not.\n\n")
w("The database keys translations as `it_IT`; the API presents `it`. That is the\n")
w("internal keying the API deliberately hides — see CLAUDE.md.\n")

print(f"wrote {OUT}: {len(rows)} usable URLs, {len(gated)} gated")
