"""Extract plain text from the supplied Schoenstatt books, for terminology mining.

The point is to settle charism vocabulary from sources the movement itself published,
rather than reasoning from the site's other languages. A glossary entry backed by
`Aliança de Amor` appearing 200 times across four books is a different kind of fact from
one inferred because Spanish says `Alianza de Amor`.

## The books are copyrighted. Their text does not go in this repository.

Extraction writes to a scratch directory outside the repo. What may be committed is a
**short attestation** — the term, a count, and a clause of surrounding context, which is
what a glossary needs and no more. Do not commit the extracted files, and do not quote
paragraphs into `data/`.

    python3 tools/extract_reading_material.py /path/to/scratch [--lang pt]

## How the formats are handled

- `.docx`, `.epub` → `pandoc -t plain`, which is faithful.
- `.pdf` → `pdftotext -layout … -` (to **stdout**; without the `-` it writes a file
  next to the source and pollutes the input directory).
- `.doc` → legacy Word binary, and there is no converter installed. Text is pulled out of
  the `WordDocument` OLE stream by decoding it as CP1252 and keeping printable runs.
  **This is deliberately crude.** It recovers the words and loses the structure: no
  paragraph boundaries, occasional binary artefacts, and formatting fields interleaved.
  That is acceptable for counting how a term is written and reading a clause around it,
  and it is not acceptable for quoting a book. A proper parse needs the piece table in
  the `1Table` stream; if this repository ever needs faithful `.doc` text, install
  `antiword` rather than extending this.
"""

import glob
import os
import re
import subprocess
import sys

# Only the Portuguese titles. The same directory holds Spanish, German and English
# material which is not what this pass is for.
#
# Matched on a distinctive fragment rather than the full filename: at least one of these
# files has a corrupted byte in its name (`O MIST\x90RIO DE SHOENSTATT.doc`, where the
# \x90 should be É), so an exact-name list silently misses it. A fragment that has to
# match exactly one file is both robust and still explicit about what is being read.
BY_LANG = {
    "pt": [
        "150 PERGUNTAS",
        "VOL 20  TOMO  1",
        "VOL 20 TOMO  2",
        "VOLUME 21",
        "VOLUME 3",
        "CARTA DE SANTA MARIA",
        "DE SANTU",              # DE SANTUÁRIO A SANTUÁRIO
        "INTRODU",               # INTRODUÇÃO EM SCHOENSTATT
        "ENGLING",
        "RIO DE SHOENSTATT",     # O MISTÉRIO DE SCHOENSTATT (corrupted É in the name)
        "O QUE SIGNIFICA",
    ],
    # German. Lexikon.pdf is the prize: a dictionary of Schoenstatt terms, which means it
    # both uses and *defines* the vocabulary. The two Kentenich Reader volumes are the
    # German originals of the Spanish tomos.
    "de": [
        "Lexikon.pdf",
        "KR_BDII_",
        "KR_BDIII_",
        "DD.pdf",                # Milwaukee tertianship, German
    ],
    "es": [
        "Kentenich Reader Tomo 1",
        "Kentenich Reader Tomo 2",
        "Kentenich Reader Tomo 3",
        "haciapdr.pdf",          # Hacia el Padre — Heavenwards in Spanish
        "CHARLAS DEL MONTE",
        "La llave para entender",
        "filosof",               # Mi filosofía de la educación
        # The Milwaukee tertianship conferences, in Spanish, one file per conference. Taken
        # as a group rather than named individually — there are ~130 of them.
        "GLOB:Terciado Milwaukee*/**/*.doc*",
    ],
    "en": [
        "KReader_EN_Ende.pdf",
        "Heavenwards Ebook.docx",
    ],
}
# The books live outside this repository, in a sibling directory — `../reading-material`
# from the repository root. Derived from this file's location rather than the working
# directory, and overridable for a machine that keeps them somewhere else.
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.environ.get(
    "SCHOENSTATT_READING_MATERIAL",
    os.path.normpath(os.path.join(_REPO, os.pardir, "reading-material")),
)


def resolve(fragment):
    """Files in SRC matching `fragment`. Returns a list.

    A bare fragment must match exactly one file — ambiguity is an error, because it means
    the caller does not know what it is reading. A `GLOB:` prefix is the explicit opt-in to
    many files, used for the Milwaukee conferences where there are over a hundred and
    naming them individually would be noise.
    """
    if fragment.startswith("GLOB:"):
        pat = os.path.join(SRC, fragment[5:])
        hits = sorted(p for p in glob.glob(pat, recursive=True)
                      if os.path.isfile(p) and not os.path.basename(p).startswith("~$"))
        print(f"  {fragment[5:]!r}: {len(hits)} files")
        return hits
    hits = [p for p in sorted(glob.glob(os.path.join(SRC, "**", "*"), recursive=True))
            if fragment in os.path.basename(p) and os.path.isfile(p)
            and not os.path.basename(p).startswith("~$")]
    if len(hits) != 1:
        print(f"  {fragment!r}: matched {len(hits)} files "
              f"{[os.path.basename(h) for h in hits[:4]]} — skipped")
        return []
    return hits

# Printable Latin-1/Latin Extended plus the punctuation Word actually emits. Anything
# else in a legacy .doc stream is structure, not language.
PRINTABLE = re.compile(r"[ -~\xa0-ɏ‐-⁞]{6,}")


def from_doc(path):
    """Pull printable CP1252 runs out of the WordDocument stream. See the caveat above."""
    import olefile
    with olefile.OleFileIO(path) as o:
        if not o.exists("WordDocument"):
            return ""
        raw = o.openstream("WordDocument").read()
    runs = PRINTABLE.findall(raw.decode("cp1252", "replace"))
    # Drop runs that are mostly not letters — field codes, style names, binary noise.
    keep = [r for r in runs
            if sum(c.isalpha() or c.isspace() for c in r) / len(r) > 0.75]
    return "\n".join(keep)


def via(cmd, path, *after):
    """Run `cmd path *after` and return stdout. Never let a converter choose an output path."""
    try:
        out = subprocess.run(cmd + [path, *after], capture_output=True, timeout=600)
        return out.stdout.decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        print(f"    ! {type(e).__name__}: {e}")
        return ""


def main():
    scratch = sys.argv[1]
    lang = "pt"
    if "--lang" in sys.argv:
        lang = sys.argv[sys.argv.index("--lang") + 1]
    out_dir = os.path.join(scratch, f"{lang}_text")
    os.makedirs(out_dir, exist_ok=True)

    total = 0
    paths = []
    for fragment in BY_LANG[lang]:
        paths += resolve(fragment)
    print(f"  {len(paths)} files to extract\n")
    for path in paths:
        name = os.path.basename(path)
        ext = os.path.splitext(name)[1].lower()
        if ext == ".doc":
            text = from_doc(path)
            how = "olefile/cp1252 (crude)"
        elif ext in (".docx", ".epub"):
            text = via(["pandoc", "-t", "plain", "--wrap=none", "-o", "-"], path)
            how = "pandoc"
        elif ext == ".pdf":
            # The trailing "-" is load-bearing: without it pdftotext writes a .txt
            # NEXT TO THE SOURCE FILE, silently polluting a directory this tool is
            # only supposed to read. It did exactly that once.
            text = via(["pdftotext", "-layout", "-enc", "UTF-8"], path, "-") or ""
            how = "pdftotext"
        else:
            continue
        rel = os.path.relpath(path, SRC)
        slug = re.sub(r"[^a-z0-9]+", "-", os.path.splitext(rel)[0].lower()).strip("-")[:110]
        dest = os.path.join(out_dir, slug + ".txt")
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(text)
        total += len(text)
        print(f"  {len(text):9,} chars  {how:22}  {name[:52]}")
    print(f"\n{total:,} characters into {out_dir}")
    print("Extracted text is scratch only — the books are copyrighted and their text "
          "must not be committed.")


if __name__ == "__main__":
    main()
