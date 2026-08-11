"""Turn the per-batch review notes into the native-speaker review queue.

Every translation this repository writes that involved a judgement call carries a note
saying what the call was and what the alternative is. This collects those notes, ranks
them, and writes the two artefacts a reviewer needs:

    docs/it-review-queue.md   the record, committed
    it-review-queue.html      the page to hand to a reviewer (published separately)

Ranking is by tier first — charism vocabulary before library jargon before ordinary
interface text — and by how many pages the string is visible on within a tier. The cap
is 100 because that is what a person will actually read.

    python3 tools/build_review_queue.py /path/to/scratch

Reads   review_selected.json  (produced by the selection step; see docs)
"""

import html
import json
import os
import sys
from collections import defaultdict

SCRATCH = sys.argv[1] if len(sys.argv) > 1 else "."
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TIER_BLURB = {
    1: "Terms belonging to the charism. A wrong answer here is wrong everywhere the "
       "term appears, and these are the ones no amount of comparing the other "
       "languages can settle.",
    2: "Terms of art from librarianship and bibliography. The question is usually "
       "which of two correct Italian words the catalogue should standardise on.",
    3: "Strings that appear on many pages, so a poor choice is highly visible. Mostly "
       "short labels where the surrounding screen decides the right word.",
    4: "Where Italian forces a choice English does not — grammatical gender, *tu* or "
       "*Lei*, imperative or infinitive.",
    5: "Cases where the English source string is itself wrong, stale or inconsistent "
       "with its own translations. These need a decision about the source, not only "
       "about the Italian.",
    6: "Remaining judgement calls, lower stakes.",
}


def md(rows):
    out = []
    w = out.append
    w("# Italian review queue — 100 translations worth a second opinion\n")
    w("Every entry here is **live on schoenstatt.link** and in the test capsule. They are")
    w("collected because each involved a judgement call that a native Italian speaker —")
    w("ideally one who knows Schoenstatt — can settle in a way this repository cannot.\n")
    w("**How to use it.** For each entry: if the proposed Italian is right, say so and")
    w("nothing more needs doing. If it is wrong, the replacement goes in as an ordinary")
    w("translation write against the phrase id. **Note that the phrase ids below are the")
    w("production ones**, and that the capsule uses a different id for some of the same")
    w("phrases.\n")
    w("**On reverting.** Translation writes have been recoverable since 2026-08-11:")
    w("`GET /api/v3/phrases/{id}/history` gives back the text a write replaced, and")
    w("restoring it is an ordinary write with that text. **But the history does not")
    w("backfill**, and the rows below were written on 2026-08-10 — so for these the")
    w("previous text really is gone, and a correction is a fresh write rather than a")
    w("revert. Nothing here is blocking: the site reads better in Italian now than it")
    w("did in English.\n")
    w("The `es` / `pt` / `de` columns are what the site already shows in those languages.")
    w("They are evidence of house convention, not of correct Italian, and in several")
    w("entries below they disagree with each other — which is exactly why the entry is here.\n")

    by_tier = defaultdict(list)
    for r in rows:
        by_tier[r["tier"]].append(r)

    w("| tier | what it covers | entries |")
    w("|---|---|---|")
    for t in sorted(by_tier):
        w(f"| {t} | {by_tier[t][0]['tier_name']} | {len(by_tier[t])} |")
    w("")

    n = 0
    for t in sorted(by_tier):
        w(f"\n## {t}. {by_tier[t][0]['tier_name']}\n")
        w(TIER_BLURB[t] + "\n")
        for r in by_tier[t]:
            n += 1
            src = r["src"].replace("\n", " ⏎ ")
            w(f"### {n}. `{src[:160]}`\n")
            w(f"**Proposed Italian:** **{r['it']}**\n")
            ids = ", ".join(str(i) for i in r["ids"])
            where = f"phrase id {ids} · text domain {'/'.join(r['domains'])}"
            if r["vis"]:
                where += f" · visible on {r['vis']} page{'s' if r['vis'] != 1 else ''}"
                if r["el"]:
                    where += f" · in a `<{r['el']}>`"
            else:
                where += " · not on a public page"
            w(f"*{where}*\n")
            if r["en"] and r["en"].strip() != r["src"].strip():
                w(f"- **en** (the English row, which differs from the key): {r['en']}")
            for lang in ("es", "pt", "de"):
                if r[lang]:
                    w(f"- **{lang}**: {r[lang]}")
            w("")
            w(f"{r['why']}\n")
    return "\n".join(out)


CSS = """
/* Palette: a proof sheet rather than a manuscript — cool neutrals with a blue bias,
   correction-ink blue as the single accent, ochre reserved for the one tier that flags
   a broken source string. Three type roles: serif for titles, sans for reading, mono
   for the literal keys and language codes. */
:root{
  --paper:#f4f5f7; --card:#ffffff; --sunk:#eceef2;
  --ink:#14171c; --dim:#5c6470; --rule:#dcdfe5;
  --accent:#2a3f7e; --accent-wash:#e8ecf7;
  --flag:#8a5a12; --flag-wash:#f6eedf;
  --attest:#2f5d4a;
  --serif:"Charter","Bitstream Charter","Sitka Text",Cambria,Georgia,serif;
  --sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --paper:#101216; --card:#181b21; --sunk:#1f232b;
    --ink:#e6e8ec; --dim:#98a1b0; --rule:#2a2e37;
    --accent:#9db4f0; --accent-wash:#1b2130;
    --flag:#d9a95a; --flag-wash:#2a2318;
    --attest:#84c0a6;
  }
}
:root[data-theme="dark"]{
  --paper:#101216; --card:#181b21; --sunk:#1f232b;
  --ink:#e6e8ec; --dim:#98a1b0; --rule:#2a2e37;
  --accent:#9db4f0; --accent-wash:#1b2130;
  --flag:#d9a95a; --flag-wash:#2a2318;
  --attest:#84c0a6;
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
  font:400 16px/1.65 var(--sans);-webkit-text-size-adjust:100%}
.wrap{max-width:56rem;margin:0 auto;padding:3.5rem 1.25rem 7rem}
a{color:var(--accent)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:2px}

/* masthead */
.mast{display:flex;flex-direction:column;gap:.75rem;
  padding-bottom:1.75rem;border-bottom:1px solid var(--ink)}
.eyebrow{font:600 .7rem/1 var(--mono);letter-spacing:.16em;text-transform:uppercase;
  color:var(--dim);margin:0}
h1{font:400 2.5rem/1.08 var(--serif);margin:0;letter-spacing:-.015em;text-wrap:balance}
.standfirst{margin:0;max-width:36rem;color:var(--dim);font-size:1.05rem}

/* counter strip */
.tally{display:flex;flex-wrap:wrap;gap:0;margin:2rem 0 0;
  border:1px solid var(--rule);background:var(--card)}
.tally div{flex:1 1 7rem;padding:.85rem 1rem;border-right:1px solid var(--rule)}
.tally div:last-child{border-right:0}
.tally dt{font:600 .68rem/1.3 var(--mono);letter-spacing:.1em;text-transform:uppercase;
  color:var(--dim);margin:0 0 .2rem}
.tally dd{margin:0;font:400 1.5rem/1 var(--serif);font-variant-numeric:tabular-nums}

.note{margin:1.75rem 0 0;padding:1rem 1.15rem;background:var(--card);
  border:1px solid var(--rule);border-left:3px solid var(--flag)}
.note p{margin:.45rem 0} .note p:first-child{margin-top:0} .note p:last-child{margin-bottom:0}
.note strong{color:var(--flag)}

.howto{margin:2.5rem 0 0}
.howto h2{font:600 .7rem/1 var(--mono);letter-spacing:.16em;text-transform:uppercase;
  color:var(--dim);margin:0 0 .75rem}
.howto p{margin:0;max-width:40rem;color:var(--ink);font-size:.97rem}

.tw{overflow-x:auto;margin:1.25rem 0 0}
table{border-collapse:collapse;width:100%;font-size:.93rem;min-width:26rem}
caption{text-align:left;font:600 .7rem/1 var(--mono);letter-spacing:.16em;
  text-transform:uppercase;color:var(--dim);padding-bottom:.6rem}
th,td{text-align:left;padding:.5rem .7rem;border-bottom:1px solid var(--rule)}
thead th{font:600 .7rem/1.3 var(--mono);letter-spacing:.08em;text-transform:uppercase;
  color:var(--dim);border-bottom:1px solid var(--ink)}
td.n{font-variant-numeric:tabular-nums;width:3rem;color:var(--dim)}
td.c{font-variant-numeric:tabular-nums;text-align:right;width:5rem}

/* tier sections */
.tier{margin-top:4rem}
.tier-head{display:flex;gap:.9rem;align-items:baseline;
  padding-bottom:.6rem;border-bottom:1px solid var(--ink)}
.tier-n{font:400 2rem/1 var(--serif);color:var(--accent);font-variant-numeric:tabular-nums;
  flex:none;min-width:1.6rem}
.tier--flag .tier-n{color:var(--flag)}
.tier h2{font:600 1.15rem/1.3 var(--sans);margin:0;letter-spacing:-.005em;text-wrap:balance}
.tier-blurb{color:var(--dim);margin:.85rem 0 1.5rem;max-width:40rem;font-size:.97rem}

/* an entry, set as a dictionary entry: metadata rail, then headword and apparatus */
.entry{display:grid;grid-template-columns:9.5rem 1fr;gap:0 1.5rem;
  padding:1.35rem 0;border-top:1px solid var(--rule)}
.entry:first-of-type{border-top:0}
.rail{font:.72rem/1.55 var(--mono);color:var(--dim);display:flex;
  flex-direction:column;gap:.15rem}
.rail .idx{font-size:.9rem;color:var(--ink);font-weight:600;
  font-variant-numeric:tabular-nums;margin-bottom:.15rem}
.rail .seen{color:var(--accent)}
.body{min-width:0}
.headword{margin:0 0 .7rem;font:.95rem/1.55 var(--mono);
  overflow-wrap:anywhere;color:var(--ink)}
.headword .q{color:var(--dim)}
.proposal{display:flex;flex-wrap:wrap;align-items:baseline;gap:.25rem .7rem;
  margin:0 0 .8rem;padding:.6rem .8rem;background:var(--accent-wash);
  border-left:2px solid var(--accent)}
.tier--flag .proposal{background:var(--flag-wash);border-left-color:var(--flag)}
.proposal .lbl{font:600 .64rem/1.4 var(--mono);letter-spacing:.12em;text-transform:uppercase;
  color:var(--accent);flex:none}
.tier--flag .proposal .lbl{color:var(--flag)}
.proposal b{font:600 1.08rem/1.4 var(--sans);overflow-wrap:anywhere}
dl.attest{margin:0 0 .8rem;padding:0;font-size:.93rem}
dl.attest div{display:grid;grid-template-columns:2.1rem 1fr;gap:.5rem;
  padding:.22rem 0;border-bottom:1px dotted var(--rule)}
dl.attest div:last-child{border-bottom:0}
dl.attest dt{margin:0;font:600 .7rem/1.7 var(--mono);letter-spacing:.06em;
  text-transform:uppercase;color:var(--dim)}
dl.attest dt.en{color:var(--attest)}
dl.attest dd{margin:0;overflow-wrap:anywhere;color:var(--ink)}
.why{margin:0;font-size:.95rem;color:var(--ink);max-width:42rem}
code{font:.88em/1.5 var(--mono);background:var(--sunk);padding:.06rem .32rem;
  border-radius:2px;overflow-wrap:anywhere}
footer{margin-top:4.5rem;padding-top:1.25rem;border-top:1px solid var(--rule);
  color:var(--dim);font-size:.88rem}
@media (max-width:38rem){
  h1{font-size:1.9rem}
  .entry{grid-template-columns:1fr;gap:.55rem}
  .rail{flex-direction:row;flex-wrap:wrap;gap:.15rem .8rem}
}
"""


def page(rows):
    by_tier = defaultdict(list)
    for r in rows:
        by_tier[r["tier"]].append(r)
    e = html.escape
    total_flagged = len(rows)

    sec = []
    n = 0
    for t in sorted(by_tier):
        # tier 5 is the one that flags broken source strings — it gets the ochre
        klass = "tier tier--flag" if t == 5 else "tier"
        sec.append(f'<section class="{klass}">'
                   f'<div class="tier-head"><span class="tier-n">{t}</span>'
                   f'<h2>{e(by_tier[t][0]["tier_name"])}</h2></div>'
                   f'<p class="tier-blurb">{e(TIER_BLURB[t])}</p>')
        for r in by_tier[t]:
            n += 1
            src = e(r["src"].replace("\n", " ⏎ "))
            rail = [f'<span class="idx">{n}</span>',
                    f'<span>phrase {e(", ".join(str(i) for i in r["ids"]))}</span>',
                    f'<span>{e("/".join(r["domains"]))}</span>']
            if r["vis"]:
                seen = f"on {r['vis']} page" + ("s" if r["vis"] != 1 else "")
                if r["el"]:
                    seen += f" · &lt;{e(r['el'])}&gt;"
                rail.append(f'<span class="seen">{seen}</span>')
            else:
                rail.append("<span>not on a public page</span>")

            att = []
            if r["en"] and r["en"].strip() != r["src"].strip():
                att.append(f'<div><dt class="en">en</dt><dd>{e(r["en"])}</dd></div>')
            for lang in ("es", "pt", "de"):
                if r[lang]:
                    att.append(f"<div><dt>{lang}</dt><dd>{e(r[lang])}</dd></div>")

            sec.append(f"""<article class="entry" id="i{n}">
<div class="rail">{''.join(rail)}</div>
<div class="body">
<p class="headword"><span class="q">&ldquo;</span>{src}<span class="q">&rdquo;</span></p>
<div class="proposal"><span class="lbl">Italian</span><b>{e(r['it'])}</b></div>
{'<dl class="attest">' + ''.join(att) + '</dl>' if att else ''}
<p class="why">{e(r['why'])}</p>
</div>
</article>""")
        sec.append("</section>")

    tier_rows = "".join(
        f'<tr><td class="n">{t}</td><td>{e(by_tier[t][0]["tier_name"])}</td>'
        f'<td class="c">{len(by_tier[t])}</td></tr>'
        for t in sorted(by_tier))

    return f"""<title>Italian review queue — schoenstatt.link</title>
<style>{CSS}</style>
<div class="wrap">
<header class="mast">
<p class="eyebrow">schoenstatt.link · translations · it</p>
<h1>Italian review queue</h1>
<p class="standfirst">{total_flagged} translations where the choice was not obvious, with
the reasoning and the alternative, for a native speaker to settle.</p>
</header>

<dl class="tally">
<div><dt>Italian before</dt><dd>18</dd></div>
<div><dt>Italian now</dt><dd>1,401</dd></div>
<div><dt>Left untranslated on purpose</dt><dd>394</dd></div>
<div><dt>Flagged here</dt><dd>{total_flagged}</dd></div>
</dl>

<div class="note">
<p>Everything below is <strong>live on schoenstatt.link</strong> — 1,383 translations were
written to the production site on 2026-08-10, and to the test capsule before that.</p>
<p>Translation writes have been recoverable since 2026-08-11 — the site now keeps the text
each write replaced. <strong>But that history does not backfill</strong>, and these rows were
written on 2026-08-10, so for them the previous text really is gone. A correction here is a
fresh write rather than a revert, which is why each entry below says what the alternative
was. Nothing is blocking — the Italian pages read as Italian now, where they read as English
before.</p>
</div>

<div class="howto">
<h2>How to read an entry</h2>
<p>The quoted line is the phrase as the site stores it — the lookup key, usually English
but not always. <b>Italian</b> is what is written now. The <code>es</code> /
<code>pt</code> / <code>de</code> lines are what the site already shows in those
languages: evidence of what this house does, not of correct Italian, and where they
disagree with each other that is usually why the entry is here. An <code>en</code> line
appears only when the English row differs from the key — meaning the key is stale, or is
not English. If the Italian is right, say so and nothing more needs doing; if it is
wrong, the replacement goes in as an ordinary write against the phrase id on the left.</p>
</div>

<div class="tw"><table>
<caption>How the list is ordered</caption>
<thead><tr><th>Tier</th><th>What it covers</th><th>Entries</th></tr></thead>
<tbody>{tier_rows}</tbody>
</table></div>

{chr(10).join(sec)}

<footer>Generated from the translation batches by
<code>tools/build_review_queue.py</code> in the <code>schoenstatt-agent</code>
repository. Counts read from the capsule on 2026-08-10.</footer>
</div>"""


def main():
    rows = json.load(open(os.path.join(SCRATCH, "review_selected.json"), encoding="utf-8"))
    p1 = os.path.join(REPO, "docs", "it-review-queue.md")
    open(p1, "w", encoding="utf-8").write(md(rows))
    p2 = os.path.join(SCRATCH, "it-review-queue.html")
    open(p2, "w", encoding="utf-8").write(page(rows))
    print(f"wrote {p1}")
    print(f"wrote {p2}")


if __name__ == "__main__":
    main()
