# Italian review queue — 100 translations worth a second opinion

Every entry here is **live on schoenstatt.link** and in the test capsule. They are
collected because each involved a judgement call that a native Italian speaker —
ideally one who knows Schoenstatt — can settle in a way this repository cannot.

**How to use it.** For each entry: if the proposed Italian is right, say so and
nothing more needs doing. If it is wrong, the replacement goes in as an ordinary
translation write against the phrase id. **Note that the phrase ids below are the
production ones**, and that the capsule uses a different id for some of the same
phrases.

A translation write **cannot be undone** — there is no history on
`trans_translations`, so the previous text is simply gone. Nothing here is
blocking: the site reads better in Italian now than it did in English. But a
correction is a fresh write, not a revert.

The `es` / `pt` / `de` columns are what the site already shows in those languages.
They are evidence of house convention, not of correct Italian, and in several
entries below they disagree with each other — which is exactly why the entry is here.

| tier | what it covers | entries |
|---|---|---|
| 1 | Charism vocabulary | 29 |
| 2 | Library and bibliographic terms | 19 |
| 3 | High-visibility interface text | 18 |
| 4 | Register, gender and address forms | 17 |
| 5 | Source-string problems worth fixing at source | 12 |
| 6 | Other judgement calls | 5 |


## 1. Charism vocabulary

Terms belonging to the charism. A wrong answer here is wrong everywhere the term appears, and these are the ones no amount of comparing the other languages can settle.

### 1. `Sister`

**Proposed Italian:** **Sorella**

*phrase id 5537 · text domain Schoenstatt · visible on 8 pages · in a `<a>`*

- **es**: Hermana
- **pt**: Irmã
- **de**: Schwester

`Sorella`, chosen to agree with the glossary's `Sorelle di Maria`. As a title immediately before a name Italian normally uses `Suor` (Suor Maria) or the abbreviation `Sr.` — which is a separate phrase here. A native speaker should say which the person-title field wants.

### 2. `Sr.`

**Proposed Italian:** **Sr.**

*phrase id 5159, 5695, 6206 · text domain JUser/Schoenstatt/SionModel · visible on 5 pages · in a `<td>`*

- **es**: Hna.
- **pt**: Ir.
- **de**: Schw.

Left as `Sr.`, which in Italian reads as *Signor* (Mr.) far more naturally than as *Suora*. es `Hna.`, pt `Ir.`, de `Schw.` all abbreviate *sister*. The Italian abbreviation for a sister is `Sr.` too, so this is ambiguous in Italian in a way it is not in the other three languages — worth a native check.

### 3. `Berg Sion`

**Proposed Italian:** **Monte Sion**

*phrase id 6956 · text domain Schoenstatt · visible on 3 pages · in a `<a>`*

- **es**: Monte Sion
- **pt**: Monte Sião
- **de**: Berg Sion

`Monte Sion`, following es `Monte Sion` and pt `Monte Sião`. German keeps `Berg Sion`. This is the name of a Schoenstatt house in Germany, so translating it is a choice — es and pt made it, de did not.

### 4. `Adoration Sisters of Mary`

**Proposed Italian:** **Sorelle dell'Adorazione**

*phrase id 6957 · text domain Schoenstatt · visible on 2 pages · in a `<a>`*

- **es**: Hermanas de la adoración
- **pt**: Irmãs da Adoração
- **de**: Anbetungsschwestern

`Sorelle dell'Adorazione`, built from the glossary's `Sorelle di Maria`. The siblings drop *of Mary* as well (es `Hermanas de la adoración`, de `Anbetungsschwestern`), so the omission follows house convention — but this is a distinct institute and may have its own Italian name.

### 5. `Cenáculo de Bellavista`

**Proposed Italian:** **Santuario Cenacolo di Bellavista**

*phrase id 6941 · text domain Schoenstatt · visible on 1 page · in a `<li>`*

- **en** (the English row, which differs from the key): Cenacle of Bellavista
- **es**: Santuario Cenáculo de Bellavista
- **pt**: Santuário Cenáculo de Bellavista
- **de**: Coenaculumsheiligtum Bellavista

`Santuario Cenacolo di Bellavista`. The key is Spanish and names no shrine; es, pt and de all prepend their word for shrine, so I did too. If the label appears in a list already headed by the shrine kind, the prefix is redundant.

### 6. `Heiligtum der Internationale`

**Proposed Italian:** **Santuario dell'Internazionalità**

*phrase id 6810 · text domain Schoenstatt · visible on 1 page · in a `<p>`*

- **en** (the English row, which differs from the key): Internationality Shrine
- **es**: Santuario de la Internacional
- **pt**: Santuário da Internacional
- **de**: Heiligtum der Internationale

`Santuario dell'Internazionalità`, following the English row `Internationality Shrine`. The German `der Internationale` and the Spanish `de la Internacional` are both nouns that read oddly in their own languages; the English is the clearest statement of what is meant.

### 7. `Heiligtum der sieghaften Kindlichkeit`

**Proposed Italian:** **Santuario della filialità vittoriosa**

*phrase id 6825 · text domain Schoenstatt · visible on 1 page · in a `<p>`*

- **en** (the English row, which differs from the key): Shrine of victorious childlikeness
- **es**: Santuario de la filialidad victoriosa
- **pt**: Santuário da filialidade vitoriosa
- **de**: Heiligtum der sieghaften Kindlichkeit

`Santuario della filialità vittoriosa`, following es `filialidad victoriosa` and pt `filialidade vitoriosa`. `Kindlichkeit` is childlikeness rather than filiation; the Romance siblings all chose filiation, and Schoenstatt's Italian vocabulary may prefer `infanzia spirituale`.

### 8. `Institute of Families`

**Proposed Italian:** **Istituto di Famiglia**

*phrase id 6742 · text domain Books · visible on 1 page · in a `<td>`*

- **es**: Instituto de Familias

`Istituto di Famiglia`, kept consistent with the glossary's singular form from the movement's Italian index. es pluralizes. Same open question as `Schoenstatt Institute of Families`.

### 9. `Ostheiligtum`

**Proposed Italian:** **Santuario dell'Est**

*phrase id 6852 · text domain Schoenstatt · visible on 1 page · in a `<p>`*

- **en** (the English row, which differs from the key): Shrine of the East
- **es**: Santuario del Este
- **pt**: Santuário do Leste
- **de**: Ostheiligtum

`Santuario dell'Est` for the Friedrichroda shrine, following es `Santuario del Este`. `Santuario dell'Oriente` is the other reading — the German means the geographic east (former East Germany), not the liturgical Orient, so I chose `Est`.

### 10. `Providentia Shrine`

**Proposed Italian:** **Santuario della Provvidenza**

*phrase id 6820 · text domain Schoenstatt · visible on 1 page · in a `<p>`*

- **es**: Santuario de la Providencia
- **pt**: Santuário da Providência
- **de**: Heiligtum Providentia

`Santuario della Provvidenza`, following es `Santuario de la Providencia`. de keeps the Latin (`Heiligtum Providentia`). Same Latin-or-not question as `Victoria Patris`.

### 11. `Schoenstatt Institute of Families`

**Proposed Italian:** **Istituto di Famiglia di Schoenstatt**

*phrase id 5151 · text domain Schoenstatt · visible on 1 page · in a `<td>`*

- **es**: Schoenstatt Instituto de Familias

`Istituto di Famiglia di Schoenstatt` reads awkwardly. It follows the glossary, which takes the singular `Istituto di Famiglia` from the movement's Italian index; `Istituto delle Famiglie di Schoenstatt` is the more natural Italian and matches es `Instituto de Familias`.

### 12. `Ver Sacrum Marianum Shrine`

**Proposed Italian:** **Santuario della sacra primavera mariana**

*phrase id 6821 · text domain Schoenstatt · visible on 1 page · in a `<p>`*

- **es**: Santuario de la primavera mariana sagrada
- **pt**: Santuário da Primavera Mariana Sagrada
- **de**: Heiligtum des marianischen heiligen Frühlings

`Santuario della sacra primavera mariana`, translating the Latin as es, pt and de all do. See the `Victoria Patris` note — the site is inconsistent about whether Latin shrine names are translated, and Italian now inherits that inconsistency.

### 13. `Victoria Patris Shrine`

**Proposed Italian:** **Santuario della Vittoria del Padre**

*phrase id 6817 · text domain Schoenstatt · visible on 1 page · in a `<p>`*

- **es**: Santuario de la Victoria del Padre
- **pt**: Santuário Vitória do Pai
- **de**: Heiligtum Sieg des Vaters

`Santuario della Vittoria del Padre` — I translated the Latin, as es and de both did. Keeping `Santuario Victoria Patris` is the alternative and would match how `Lumen Patris` and `Cor Unum in Patre` are left in Latin elsewhere in the same list. **These two are inconsistent with each other and a native speaker should pick one policy.**

### 14. `Coordinating Sister`

**Proposed Italian:** **Sorella coordinatrice**

*phrase id 5396 · text domain Schoenstatt · not on a public page*

- **es**: Hermana coordinadora
- **pt**: Irmã coordenadora
- **de**: Koordinierende Schwester

`Sorella coordinatrice`, using the glossary's `Sorelle di Maria` choice. If the site's person titles settle on `Suor`, this should follow them.

### 15. `Ermida Tabor da Acolhida`

**Proposed Italian:** **Edicola Tabor dell'Accoglienza**

*phrase id 6808 · text domain Schoenstatt · not on a public page*

- **en** (the English row, which differs from the key): Welcoming Tabor wayside shrine
- **es**: Ermita Tabor de la Acogida
- **pt**: Ermida Tabor da Acolhida
- **de**: Bildstock Tabor der  Beheimatung

`Edicola Tabor dell'Accoglienza`, applying the glossary's `edicola` for a wayside shrine — confirmed here by the English row, which calls it a `Welcoming Tabor wayside shrine`, and by de `Bildstock`. This and `Edicola del Reincontro` are the first two wayside-shrine proper names to get Italian.

### 16. `Familia Patris Heiligtum, Berg Sion, Horw`

**Proposed Italian:** **Santuario Famiglia del Padre, Berg Sion, Horw**

*phrase id 7179 · text domain Schoenstatt · not on a public page*

- **en** (the English row, which differs from the key): Family of the Father Shrine, Berg Sion, Horw
- **es**: Santuario Familia del Padre, Berg Sion, Horw

Kept `Berg Sion` inside this name while the standalone `Berg Sion` phrase was translated to `Monte Sion`, following es, which does exactly the same thing. **The two are inconsistent with each other** and a reviewer should decide whether the house translates this house's name or not.

### 17. `Heiligtum der Verbundenheit`

**Proposed Italian:** **Santuario dei Legami**

*phrase id 6816 · text domain Schoenstatt · not on a public page*

- **en** (the English row, which differs from the key): Shrine of Attachments
- **es**: Santuario de la Vinculación
- **pt**: Santuário da Vinculação
- **de**: Heiligtum der Verbundenheit

**One of the most uncertain in this whole set.** `Verbundenheit` is a Schoenstatt term of art — the *attachments* or bonds at the centre of Kentenich's pedagogy. es and pt both coined `Vinculación`/`Vinculação`; the Italian cognate `Vincolazione` is not real Italian, so I used `Santuario dei Legami`. Italian Schoenstatt pedagogy will have its own settled word (`legami`, `vincoli`, `attaccamenti`) and this shrine's name should use it.

### 18. `Heiligtum der Werktagsheiligkeit`

**Proposed Italian:** **Santuario della Santità quotidiana**

*phrase id 6797 · text domain Schoenstatt · not on a public page*

- **en** (the English row, which differs from the key): Everyday Sanctity Shrine
- **es**: Santuario de la Santidad de todos los días
- **pt**: Santuário da Santidade da Vida Diária
- **de**: Heiligtum der Werktagsheiligkeit

`Santuario della Santità quotidiana`. `Werktagsheiligkeit` is another term of art — sanctity of the working day. es spells it out as `Santidad de todos los días` and pt as `Santidade da Vida Diária`. Italian Schoenstatt may say `santità del quotidiano` or `santità del giorno feriale`; the shrine's name should match whichever is used.

### 19. `Launch of new "Schoenstatt Shrines" app for Android!`

**Proposed Italian:** **Lancio della nuova app "Santuari di Schoenstatt" (Schoenstatt Shrines) per Android!**

*phrase id 7074, 7082 · text domain Application/SionModel · not on a public page*

- **es**: Publicación de la nueva app "Santuarios de Schoenstatt" (Schoenstatt Shrines) para Android!
- **pt**: Lançamento da nova app "Santuários de Schoenstatt" (Schoenstatt Shrines) para Android!
- **de**: Veröffentlichung der neuen App "Schönstatt-Heiligtümer" (Schoenstatt Shrines) für Android!

This resolves an open glossary question. es, pt and de all translate the app's name and then repeat the English in parentheses, so Italian follows: `"Santuari di Schoenstatt" (Schoenstatt Shrines)`. **The app's own Italian store listing is still the real authority** and has not been checked. A second copy of this string in the Application domain is deliberately left untranslated as dead welcome-page copy.

### 20. `Madrugadores of %s`

**Proposed Italian:** **Madrugadores di %s**

*phrase id 6251 · text domain Schoenstatt · not on a public page*

- **en** (the English row, which differs from the key): Centinels of %s
- **es**: Madrugadores of %s

Kept the Spanish `Madrugadores`. The English row calls them `Centinels of %s` — presumably *Sentinels* — and Spanish keeps `Madrugadores` even inside its own translation. Nobody has settled what this branch is called outside Spanish, so Italian keeps the Spanish name too.

### 21. `Moderator`

**Proposed Italian:** **Moderatore**

*phrase id 5865, 6223 · text domain Schoenstatt/SionModel · not on a public page*

- **es**: Asesor

`Moderatore` is the literal Italian, but Spanish renders this office `Asesor` — *adviser* — throughout, which suggests the movement's Spanish-speaking usage does not treat it as a moderator at all. Related to the `Assistant moderator` and `Branch moderator` notes.

### 22. `Professional's branch of %s`

**Proposed Italian:** **Ramo dei professionisti di %s**

*phrase id 5845 · text domain Schoenstatt · not on a public page*

- **es**: Forjadores de %s

`Ramo dei professionisti di %s`. Spanish uses `Forjadores de %s` — a branch name specific to Spanish-speaking Schoenstatt with no equivalent elsewhere. Italian Schoenstatt may have its own name for this branch that is not a translation of *professionals*.

### 23. `RAINHA TRÊS VEZES ADMIRÁVEL DA PARÓQUIA DE SANTO ANTÓNIO DE NOVA OEIRAS`

**Proposed Italian:** **REGINA TRE VOLTE AMMIRABILE DELLA PARROCCHIA DI SANT'ANTONIO DI NOVA OEIRAS**

*phrase id 6969 · text domain Schoenstatt · not on a public page*

- **en** (the English row, which differs from the key): Queen Mother Three Times Admirable of the Parish of San Antonio of Nova Oeiras
- **es**: Reina Tres Veces Admirable de Parroquia de San Antonio de Nova Oeiras
- **pt**: Rainha Três Vezes Admirável da Paróquia de Santo António de Nova Oeiras
- **de**: Dreimal Wunderbare Königin der Pfarrei Sankt Antonius in Nova Oeiras

Rendered `REGINA TRE VOLTE AMMIRABILE`, using the glossary's `Tre Volte Ammirabile` and *Regina* for `Rainha`. Kept the all-caps of the source, which every sibling language also kept. If the caps are an artefact of data entry rather than intentional, the whole row would be better fixed at source.

### 24. `Santuario de La Loma`

**Proposed Italian:** **Santuario di La Loma**

*phrase id 6792 · text domain Schoenstatt · not on a public page*

- **en** (the English row, which differs from the key): Shrine of La Loma
- **es**: Santuario de La Loma
- **pt**: Santuário de La Loma
- **de**: Heiligtum von La Loma

`Santuario di La Loma` — changed the Spanish `de` to Italian `di` while keeping the place name. de writes `Heiligtum von La Loma`, doing the same. `Santuario de La Loma` untouched is the alternative if the whole string is treated as a proper name.

### 25. `Santuario Terruño - Portal de la Trinidad, Jardín del Padre`

**Proposed Italian:** **Santuario della Terra Natale - Portale della Trinità, Giardino del Padre**

*phrase id 7123 · text domain Schoenstatt · not on a public page*

- **en** (the English row, which differs from the key): Homeland Shrine, Gate of the Trinity, Garden of the Father
- **es**: Santuario Terruño - Portal de la Trinidad, Jardín del Padre

`Terruño` has no single Italian word; I used `Terra Natale`, following the English row's `Homeland`. `Santuario del Terruño` keeping the Spanish is the alternative for a proper name.

### 26. `Schoenstatt Institute Brothers of Mary`

**Proposed Italian:** **Istituto Secolare Fratelli di Maria di Schoenstatt**

*phrase id 5149 · text domain Schoenstatt · not on a public page*

- **es**: Instituto Secular Hermanos de María de Schoenstatt
- **pt**: Instituto Secular Irmãos de Maria de Schoenstatt
- **de**: Schönstatt-Institut Marienbrüder

`Istituto Secolare Fratelli di Maria di Schoenstatt` — I added *Secolare*, which the English key does not have, because es, pt and de all add their equivalent. Dropping it would give `Istituto Fratelli di Maria di Schoenstatt`.

### 27. `Se agradece Capital de gracias por este Santuario / https://www.facebook.com/schoenstattsanluis`

**Proposed Italian:** **Si ringrazia per la Capitale di Grazie per questo Santuario / https://www.facebook.com/schoenstattsanluis**

*phrase id 6981 · text domain Schoenstatt · not on a public page*

- **en** (the English row, which differs from the key): We thank you for your Capitol of Grace for this Shrine / https://www.facebook.com/schoenstattsanluis
- **es**: Se agradece Capital de gracias por este Santuario / https://www.facebook.com/schoenstattsanluis

Uses the glossary's `Capitale di Grazie`. The source string contains a non-breaking space before the URL, which is preserved. This is a moderator's note on one shrine record rather than interface text, so it is a candidate for retirement.

### 28. `Secular Institute Our Lady of Schoenstatt`

**Proposed Italian:** **Istituto Secolare Nostra Signora di Schoenstatt**

*phrase id 5152 · text domain Schoenstatt · not on a public page*

- **es**: Instituto Secular Nuestra Señora de Schoenstatt
- **pt**: Instituto Secular Nª Srª de Schoenstatt
- **de**: Säkularinstitut Unserer Lieben Frau von Schönstatt

`Istituto Secolare Nostra Signora di Schoenstatt`, translating the English key. Note this institute is the one the Italian communities' index calls `Signore di Schoenstatt` — *Ladies of Schoenstatt* — so the site now has two different Italian names for what may be the same body. Deliberate: the two English keys differ and I translated each.

### 29. `Via ad Patrem Misericordem Shrine`

**Proposed Italian:** **Santuario Cammino verso il Padre Misericordioso**

*phrase id 6844 · text domain Schoenstatt · not on a public page*

- **es**: Santuario Camino al Padre Misericordioso
- **pt**: Santuário Caminho para o Pai Misericordioso
- **de**: Heiligtum Weg zum barmherzigen Vater

Translated the Latin — `Santuario Cammino verso il Padre Misericordioso` — following es and pt, which both do. Note this contradicts leaving `Cor unum in Patre` and `Dilexit Ecclesiam` in Latin in the same batch, which is also what es and pt do. **The site is inconsistent about Latin shrine names and Italian now inherits that inconsistency**; worth one decision covering all of them.


## 2. Library and bibliographic terms

Terms of art from librarianship and bibliography. The question is usually which of two correct Italian words the catalogue should standardise on.

### 30. `Paperback`

**Proposed Italian:** **Brossura**

*phrase id 5619 · text domain Books · visible on 4 pages · in a `<p>`*

- **es**: Libro de tapa blanda

`Brossura` is the correct Italian binding term; `Tascabile` is the everyday word for a paperback book. Spanish used the descriptive `Libro de tapa blanda`. Which one belongs in a bibliographic *Book format* field is a librarian's call.

### 31. `Call number`

**Proposed Italian:** **Collocazione**

*phrase id 6566 · text domain Books · visible on 1 page · in a `<label>`*

- **es**: Número localizador
- **pt**: Número de localizador
- **de**: Katalognummer

`Collocazione` is the standard Italian library term for a call number, and it is used consistently across the eight `Call number …` strings in this batch. It is not a literal translation of the English, and es (`Número localizador`) and de (`Katalognummer`) both stayed closer to *number*. A librarian should confirm `Collocazione` over `Numero di collocazione`.

### 32. `Filiation`

**Proposed Italian:** **Filiale**

*phrase id 6608 · text domain Books · visible on 1 page · in a `<label>`*

- **es**: Filial
- **pt**: Filial
- **de**: Filiale

`Filiale` follows es/pt `Filial` and de `Filiale`, all of which mean a *branch* of an organization. But the English word *filiation* means descent or affiliation, not a branch office. The siblings may have mistranslated it; if the field records which shrine a shrine descends from, `Filiazione` is right.

### 33. `PUC`

**Proposed Italian:** **PUC**

*phrase id 5599, 6698 · text domain Books/SionModel · visible on 1 page · in a `<li>`*

- **en** (the English row, which differs from the key): Theological library of the Catholic University of Chile
- **es**: Biblioteca de teología de la Universidad Católica de Chile

Left as `PUC`. The English row expands it to `Theological library of the Catholic University of Chile` and Spanish to `Biblioteca de teología de la Universidad Católica de Chile`, so both siblings expanded rather than kept the abbreviation. If this is a heading rather than a code, Italian should expand too.

### 34. `AudiobookFormat`

**Proposed Italian:** **Audiolibro**

*phrase id 5616 · text domain Books · not on a public page*

- **es**: FormatoAudiolibro

`Audiolibro`. The key is a schema.org `BookFormatType` enum name, and es rendered it as the compound `FormatoAudiolibro`. **If the site ever matches this string against schema.org rather than only displaying it, translating it is wrong** — but Spanish, Portuguese and German have all translated the sibling format values (`Hardcover`, `Paperback`), so the site appears to use them as labels.

### 35. `CM PK`

**Proposed Italian:** **Colegio Mayor PK**

*phrase id 5597 · text domain Books · not on a public page*

- **es**: Colegio Mayor PK

Expanded to `Colegio Mayor PK`, following the Spanish row, rather than keeping the two-letter code. If the string is used as a compact column value the expansion will not fit.

### 36. `Delete song`

**Proposed Italian:** **Elimina canto**

*phrase id 8281 · text domain Books · not on a public page*


`Elimina canto`. `Canto` is the word for a liturgical song; `Canzone` is the general word for a song. The music module holds Schoenstatt songs, so `canto` fits — but if it also holds secular music, `Canzone` is safer.

### 37. `Due on`

**Proposed Italian:** **Da restituire il**

*phrase id 5716 · text domain Books · not on a public page*

- **es**: Fecha de devolución
- **pt**: Data de Devolução

`Da restituire il` — *to be returned on* — which is how an Italian library labels this. es `Fecha de devolución` and pt `Data de Devolução` both use the noun *return date*; `Data di restituzione` would match them more closely.

### 38. `Editor(s)`

**Proposed Italian:** **Curatore(i)**

*phrase id 6629 · text domain Books · not on a public page*

- **es**: Editor(es)
- **pt**: Editor(es)
- **de**: Herausgeber

`Curatore(i)` — the Italian bibliographic term for the editor of a volume, matching de `Herausgeber`. Spanish used `Editor(es)`, which in Italian would read as *publisher* and clashes with the separate `Publisher` field (`Editore`). This distinction matters more in Italian than in Spanish.

### 39. `GraphicNovel`

**Proposed Italian:** **Graphic novel**

*phrase id 6313 · text domain Books · not on a public page*

- **es**: NovelaGrafica

`Graphic novel`, kept as the English term Italian actually uses. es coined `NovelaGrafica`. Same schema.org caveat as `AudiobookFormat` and `Hardcover`.

### 40. `Hardcover`

**Proposed Italian:** **Copertina rigida**

*phrase id 5618 · text domain Books · not on a public page*

- **es**: TapaDura

`Copertina rigida`, the standard Italian binding term, alongside `Brossura` for `Paperback`. es used the compound `TapaDura`, matching its `FormatoAudiolibro` style. Same schema.org caveat as `AudiobookFormat`.

### 41. `Literature relating to Schoenstatt. This index has been compiled from several libraries of the Schoenstatt Fathers and will continue to grow as we review the in`

**Proposed Italian:** **Letteratura riguardante Schoenstatt. Questo catalogo è stato compilato a partire da diverse biblioteche dei Padri di Schoenstatt e continuerà a crescere man mano che rivediamo le informazioni su altri libri.**

*phrase id 6513 · text domain Books · not on a public page*

- **es**: Literatura referente a Schoenstatt. Este índice ha sido compilado de varias bibliotecas de los Padres de Schoenstatt y seguirá creciendo mientras revisamos la información de más libros.
- **pt**: Literatura relativa a Schoenstatt. Este catálogo foi compilado com a ajuda de várias bibliotecas dos Padres de Schoenstatt e continuará a crescer à medida que for possível incorporar informação de novos livros.
- **de**: Schönstattliteratur. Dieser Katalog wurde auf der Basis von mehreren Bibliotheken der Schönstattpatres erstellt und wird fortlaufend ergänzt.

Same choice: `catalogo` for the key's *index*, following es, pt and de, which all say catalogue. The site's own English uses both words for the same thing.

### 42. `Locale`

**Proposed Italian:** **Locale**

*phrase id 6606 · text domain Books · not on a public page*

- **es**: Local

Kept `Locale`, which is the Italian technical term as well as the English one. The Spanish row says `Local` — *a room or premises* — which is a mistranslation, so there is no useful precedent to follow.

### 43. `Lyricist(s)`

**Proposed Italian:** **Autore(i) del testo**

*phrase id 7267 · text domain Books · not on a public page*

- **es**: Compositor(es)

`Autore(i) del testo`. The Spanish row says `Compositor(es)` — *composer* — which is wrong, and this form has a separate `Composer(s)` field. `Paroliere` is the single-word Italian for a lyricist but belongs to popular music rather than hymnody.

### 44. `Merged into`

**Proposed Italian:** **Unito a**

*phrase id 9036 · text domain Books · not on a public page*


`Unito a`. Without seeing the screen it is unclear whether this labels a link to the surviving record (`Unito a`) or a status (`Unificato in`). No sibling rendering exists.

### 45. `Pending call number`

**Proposed Italian:** **Collocazione in attesa**

*phrase id 6646 · text domain Books · not on a public page*

- **es**: Número localizador pendiente

`Collocazione in attesa`, consistent with `Collocazione` for *call number* throughout. See that note.

### 46. `Superiors`

**Proposed Italian:** **Superiori**

*phrase id 5701 · text domain Books · not on a public page*

- **es**: Superiores
- **pt**: Superiores
- **de**: Obere

`Superiori`. In a religious-institute context this means the superiors of the community, which `Superiori` conveys. If the field instead lists a publication's *superiors* in some hierarchy of records, the word is wrong — no sibling clarifies.

### 47. `To avoid showing multiple editions of the same book in the index, please select the latest edition of this work from the list.`

**Proposed Italian:** **Per non mostrare più edizioni della stessa opera nel catalogo, seleziona dall'elenco l'edizione più recente.**

*phrase id 6736 · text domain Books · not on a public page*

- **en** (the English row, which differs from the key): To avoid showing multiple editions of the same book in the catalog, please select the latest edition of this work from the list.
- **es**: Para no mostrar múltiples ediciones de la misma obra en el catálogo, por favor selecciona la última edición de esta obra.

The key says *index* but the English row and the Spanish both say *catalog*; I followed them and wrote `catalogo`. The key looks like the older wording.

### 48. `Vaterhaus Investigation Library`

**Proposed Italian:** **Biblioteca di ricerca Vaterhaus**

*phrase id 7487 · text domain Books · not on a public page*


`Biblioteca di ricerca Vaterhaus` — kept the German `Vaterhaus` as the house's name and translated the rest. No sibling rendering exists. If the house has an Italian name in the movement, that should be used.


## 3. High-visibility interface text

Strings that appear on many pages, so a poor choice is highly visible. Mostly short labels where the surrounding screen decides the right word.

### 49. `Chile`

**Proposed Italian:** **Cile**

*phrase id 6880 · text domain Schoenstatt · visible on 109 pages · in a `<p>`*

- **es**: Chile
- **pt**: Chile
- **de**: Chile

Rendered with the Italian exonym `Cile`, where es, pt and de all keep `Chile`. Correct Italian, but it makes Italian the only language that changes the country's name here — and this is a dropdown value that may be matched against stored data.

### 50. `Controller`

**Proposed Italian:** **Controller**

*phrase id 6775, 6859 · text domain Books/Schoenstatt · visible on 106 pages · in a `<p>`*


Kept in English as a software term, but Spanish translated it (`Controlador`). It appears in the footer's debug line on 106 pages. Italian MVC usage normally keeps `Controller`.

### 51. `Admin notes`

**Proposed Italian:** **Note (solo per l'amministratore)**

*phrase id 5470, 6489 · text domain Books/Schoenstatt · visible on 81 pages · in a `<div>`*

- **es**: Notas (solamente para el administrador)
- **pt**: Notas (somente para o administrador)
- **de**: Bemerkungen (nur für den Verwalter)

Expanded to `Note (solo per l'amministratore)`, following es, pt and de, which all gloss it the same way rather than translating the two words literally.

### 52. `Links`

**Proposed Italian:** **Link**

*phrase id 6706 · text domain Schoenstatt · visible on 79 pages · in a `<strong>`*

- **es**: Enlaces
- **pt**: Links
- **de**: Links

Kept the English loanword `Link`, following pt and de. Spanish translated it (`Enlaces`). Italian does use `Link` for web links, but `Collegamenti` is the fuller form.

### 53. `Americas`

**Proposed Italian:** **Americhe**

*phrase id 6720 · text domain Schoenstatt · visible on 27 pages · in a `<p>`*

- **es**: Las Américas
- **pt**: Toda América
- **de**: Ganz Amerika

`Americhe` as a bare plural, matching the sibling region labels (Africa, Asia, Europa). es says `Las Américas` and pt `Toda América`, both with an article or qualifier; `Le Americhe` is the alternative.

### 54. `Public`

**Proposed Italian:** **Pubblica**

*phrase id 6499 · text domain Books · visible on 11 pages · in a `<p>`*

- **es**: Pública

`Pubblica` (feminine), following the Spanish `Pública`. If the label describes an access level in the abstract rather than a feminine noun, `Pubblico` would be right. Cannot tell from the markup.

### 55. `General`

**Proposed Italian:** **Collezione generale**

*phrase id 6428, 6861 · text domain Books/SionModel · visible on 9 pages · in a `<p>`*

- **en** (the English row, which differs from the key): General Collection
- **es**: Colección general

The key is `General` but the English row renders `General Collection`, so I followed English and Spanish (`Colección general`) with `Collezione generale` rather than the bare adjective. If the label sits in a column that already says `Collection`, this is redundant.

### 56. `until`

**Proposed Italian:** **fino a**

*phrase id 5401 · text domain Schoenstatt · visible on 1 page · in a `<td>`*

- **es**: hasta
- **pt**: até
- **de**: bis

`fino a`, paired with `from` → `da`. If the two appear as bare column headers on either side of a date range, `da` / `a` is the idiomatic Italian pair and `fino a` will read long.

### 57. `Account`

**Proposed Italian:** **Account**

*phrase id 12885 · text domain JUser · not on a public page*


`Account`, the ordinary Italian technical loanword. If the surrounding screen prefers Italian throughout, `Utenza` is the native term.

### 58. `Branch leader`

**Proposed Italian:** **Responsabile di ramo**

*phrase id 6222, 6253 · text domain Schoenstatt/SionModel · not on a public page*

- **es**: Jefe de rama
- **pt**: Chefe de Ramo
- **de**: Diözesanleiter / -trägerin

`Responsabile di ramo` rather than a literal `Capo di ramo` (es `Jefe de rama`), because Italian church usage says *responsabile*. de renders it as a diocesan leader entirely, which suggests the office differs by country.

### 59. `Doctor`

**Proposed Italian:** **Dottore**

*phrase id 5538 · text domain Schoenstatt · not on a public page*

- **es**: Doctor
- **pt**: Doutor
- **de**: Doktor

`Dottore` — the same Italian as the separate `Doktor` phrase, which I also rendered `Dottore`. Both are person-title values and will now be indistinguishable in Italian, as they already are in Spanish (`Doctor` for both).

### 60. `Logout`

**Proposed Italian:** **Esci**

*phrase id 12860 · text domain Application · not on a public page*

- **es**: Cerrar sesión
- **pt**: Logout
- **de**: Abmelden

`Esci` — imperative, per the style guide, and it matches the `Accedi` / `Registrati` set the Italian site chrome already used. Spanish (`Cerrar sesión`) and German (`Abmelden`) both describe the action rather than commanding it.

### 61. `Main role`

**Proposed Italian:** **Ruolo principale per i contatti**

*phrase id 5399, 7324 · text domain Schoenstatt/default · not on a public page*

- **es**: Función principal para contactos
- **pt**: Função principal para contatos
- **de**: Hauptamt für Kontakte

`Ruolo principale per i contatti`, following es and pt, which both add *for contacts* where the English key says only `Main role`. de agrees (`Hauptamt für Kontakte`). Three siblings against the key, so I followed them.

### 62. `Overdue`

**Proposed Italian:** **Scaduto**

*phrase id 6594 · text domain Books · not on a public page*

- **es**: Vencido

`Scaduto` (masculine singular). If the label heads a column of books (`libri`) it should be plural `Scaduti`; if it labels a single loan, singular is right.

### 63. `Principal`

**Proposed Italian:** **Rettore**

*phrase id 5515 · text domain Schoenstatt · not on a public page*

- **es**: Rector
- **pt**: Reitor / Diretor
- **de**: Rektor / Schulleiter

`Rettore`, following es `Rector`. The role is the head of a Schoenstatt school; modern Italian for that office is `Dirigente scolastico`, while `Rettore` is used for a university or a seminary. de hedges with `Rektor / Schulleiter`.

### 64. `Roles`

**Proposed Italian:** **Ruoli**

*phrase id 12881 · text domain JUser · not on a public page*

- **es**: Tareas
- **pt**: Cargos
- **de**: Ämter & Aufgaben

`Ruoli`. Note the sibling rows do not agree on what this field is: es `Tareas` (tasks), pt `Cargos` (offices), de `Ämter & Aufgaben` (offices & duties). The singular `Role` elsewhere in this work is also `Ruolo`, so Italian is at least internally consistent.

### 65. `Tags`

**Proposed Italian:** **Tag**

*phrase id 12867 · text domain Books · not on a public page*


`Tag` — Italian uses the English word and does not inflect it for plural, so the singular `Tag` covers both. The site's other tag fields (`Admin tags`, `Person tags`) were rendered the same way.

### 66. `Total shrine progress`

**Proposed Italian:** **Percentuale totale dei santuari elaborati**

*phrase id 7034 · text domain Schoenstatt · not on a public page*

- **es**: Porcentaje total de santuarios procesados
- **pt**: Percentagem total de santuários processados
- **de**: Prozentanteil der Informationsbearbeitung der Heiligtümer

`Percentuale totale dei santuari elaborati`, following es and pt, which both say *percentage of shrines processed* rather than translating *progress*. Long for a table header; `Avanzamento totale` is shorter but less clear.


## 4. Register, gender and address forms

Where Italian forces a choice English does not — grammatical gender, *tu* or *Lei*, imperative or infinitive.

### 67. `Checkout books`

**Proposed Italian:** **Presta libri**

*phrase id 5600 · text domain Books · visible on 3 pages · in a `<a>`*

- **es**: Prestar libros

`Presta libri` — imperative, per the style guide. Spanish used the infinitive `Prestar libros`. Italian library usage would more often label this section with the noun `Prestito libri`; whether the imperative rule should apply to a section link rather than a button is the open question.

### 68. `Pfr.`

**Proposed Italian:** **Don**

*phrase id 7311 · text domain Schoenstatt · visible on 2 pages · in a `<option>`*


**`Don` is a guess and should be checked first.** `Pfr.` is the German abbreviation for *Pfarrer*, a parish priest. Italian has no standard abbreviation for it: `Don` is the ordinary Italian address for a diocesan priest but is not an abbreviation of an office, and `Parroco` is the office spelled out. No sibling language translated this row, so there is no house convention either.

### 69. `Gift shop`

**Proposed Italian:** **Negozio di articoli religiosi**

*phrase id 7523 · text domain Schoenstatt · visible on 1 page · in a `<strong>`*


`Negozio di articoli religiosi` is descriptive and long for a contact-type label. Italian shrines often just say `Negozio`. No sibling language translated this row.

### 70. `Msgr. Dr.`

**Proposed Italian:** **Mons. Dr.**

*phrase id 5184 · text domain Schoenstatt · visible on 1 page · in a `<option>`*

- **es**: Msgr. Dr.
- **pt**: Monsenhor Dr.
- **de**: Msgr. Doktor

`Mons. Dr.` — es keeps `Msgr. Dr.`, pt spells out `Monsenhor Dr.`, de writes `Msgr. Doktor`. `Mons.` is the correct Italian abbreviation; whether the doctorate should be `Dr.` or `Dott.` is a house-style question.

### 71. `Retreat center`

**Proposed Italian:** **Casa di esercizi spirituali**

*phrase id 7524 · text domain Schoenstatt · visible on 1 page · in a `<strong>`*


`Casa di esercizi spirituali` is the standard Italian term but is long for a label; `Casa di ritiri` is shorter and also used. No sibling rendering exists to follow.

### 72. `Submitting photos`

**Proposed Italian:** **Inviare foto**

*phrase id 7140 · text domain Schoenstatt · visible on 1 page · in a `<title>`*

- **es**: Compartir fotos

`Inviare foto`. The Spanish page is titled `Compartir fotos` — *sharing* photos, not submitting them. If the page asks people to contribute photos to the database, `Inviare le foto` or `Come inviare le foto` reads better as a page title.

### 73. `Careful`

**Proposed Italian:** **Attenzione**

*phrase id 6168, 12905 · text domain JUser/Schoenstatt · not on a public page*

- **es**: Cuidado
- **pt**: Cuidado
- **de**: Vorsicht

`Attenzione`. Literally *careful* would be `Attento`, but `Attenzione` is what Italian interfaces put above a warning. es `Cuidado` and de `Vorsicht` are the same choice.

### 74. `Dear %s,`

**Proposed Italian:** **Caro %s,**

*phrase id 6603 · text domain Books · not on a public page*

- **es**: Querido %s,
- **pt**: Querido %s,
- **de**: Lieber %s,

`Caro %s,` — masculine, as es (`Querido`), pt (`Querido`) and de (`Lieber`) all are. Italian forces a gender here that English does not, and a library notice goes to men and women alike. `Gentile %s,` is gender-neutral and slightly more formal; it would also break the informal *tu* register the style guide records. Worth a decision, since this string opens every overdue-book email.

### 75. `Dear %s, ⏎  ⏎ Welcome to Schoenstatt Link! Before we get started, please confirm ⏎ your e-mail address by clicking on this link: ⏎  ⏎ %s ⏎  ⏎ If you haven't reg`

**Proposed Italian:** **Caro %s,

Benvenuto/a su Schoenstatt Link! Prima di iniziare, conferma
il tuo indirizzo email cliccando su questo link:

%s

Se non ti sei registrato/a su Schoenstatt Link, puoi ignorare
tranquillamente questo messaggio.**

*phrase id 6755 · text domain default · not on a public page*


Uses `Benvenuto/a` and `registrato/a` to avoid assuming the reader's gender, which Italian forces a choice about and English does not. The slashed form is common in Italian institutional writing but some houses prefer a rewording that avoids it entirely.

### 76. `Has lifetime membership?`

**Proposed Italian:** **Ha un'appartenenza a vita?**

*phrase id 5414 · text domain Schoenstatt · not on a public page*

- **es**: ¿Tiene pertenencia perpétua?

`Ha un'appartenenza a vita?`. Spanish uses `pertenencia perpétua` — *perpetual*. If this records a canonical status rather than a subscription, `appartenenza perpetua` is closer.

### 77. `Hey! Welcome to Schoenstatt Link! Before we get started, please confirm ⏎ your e-mail address by clicking on the this link: ⏎  ⏎ %s ⏎  ⏎ If you haven't register`

**Proposed Italian:** **Benvenuto/a su Schoenstatt Link! Prima di iniziare, conferma
il tuo indirizzo email cliccando su questo link:

%s

Se non ti sei registrato/a su Schoenstatt Link, ignora questo messaggio.
Per domande o commenti, scrivi all'assistenza: support@schoenstatt.link.**

*phrase id 6684 · text domain default · not on a public page*

- **en** (the English row, which differs from the key): Hey! Welcome to Schoenstatt Link! Before we get started, please confirm
your e-mail address by clicking on this link:

%s

If you haven't registered with Schoenstatt Link, please just ignore this message.
If you have any questions or comments, please contact support at support@schoenstatt.link.
- **es**: ¡Hola! ¡Bienvenido a Schoenstatt Link! Antes de que empezamos, por favor confirma tu dirección de mail con un clic a este link:

Dropped the `Hey!` rather than rendering it — Italian has no neutral one-word equivalent that suits an institutional email, and the Spanish row opens `¡Hola!`. Also note the key contains `on the this link`, a slip the English row corrects. Uses the same `Benvenuto/a` construction as the other registration email.

### 78. `Human check`

**Proposed Italian:** **Sei umano?**

*phrase id 6627 · text domain ZfcUser · not on a public page*

- **es**: ¿Eres humano?
- **pt**: Você é humano?
- **de**: Sind Sie ein Mensch?

`Sei umano?` — phrased as a question in the informal *tu*, following es (`¿Eres humano?`) and pt (`Você é humano?`). de uses the formal *Sie*. The English key is a noun phrase (`Human check`); if it labels a form field rather than asking the user, `Verifica umana` is the right shape.

### 79. `Is publically listed?`

**Proposed Italian:** **Compare nell'elenco pubblico?**

*phrase id 6394 · text domain Books · not on a public page*

- **es**: ¿Debe aparecer en la lista pública?

`Compare nell'elenco pubblico?` — rephrased as a question about appearing, following es (`¿Debe aparecer en la lista pública?`), rather than translating *listed* literally.

### 80. `Life community`

**Proposed Italian:** **Comunità perpetua**

*phrase id 5531 · text domain Schoenstatt · not on a public page*

- **es**: Comunidad perpétua
- **pt**: Comunidade perpétua
- **de**: Gemeinschaft auf Lebzeiten

`Comunità perpetua`, following es `Comunidad perpétua` and pt `Comunidade perpétua` rather than the English key's *life community*. de says `Gemeinschaft auf Lebzeiten` — for life. All three siblings agree the sense is permanence.

### 81. `Nope :-(`

**Proposed Italian:** **No :-(**

*phrase id 7228 · text domain Schoenstatt · not on a public page*

- **es**: No
- **de**: Nein

`No :-(` keeps the emoticon and drops the informality of *nope*, which Italian has no short equivalent for. es and de both flattened it to plain `No`/`Nein`; I kept the emoticon because the paired `Yup!` is also playful.

### 82. `Register`

**Proposed Italian:** **Registrati**

*phrase id 6673, 6674, 6678, 6681, 12820 · text domain Application/Books/JUser/ZfcUser/default · not on a public page*

- **es**: Registrar
- **pt**: Inscrever
- **de**: Anmelden

`Registrati` — imperative, per the style guide, and it matches the label the Italian site chrome already renders. es `Registrar` and de `Anmelden` are infinitives.

### 83. `Who's checking out?`

**Proposed Italian:** **Chi prende in prestito?**

*phrase id 5719 · text domain Books · not on a public page*

- **es**: ¿Quién quiere llevar el libro?
- **pt**: Quem quer pedir o livro?
- **de**: Wer möchte das Buch entleihen?

`Chi prende in prestito?`. The siblings all rephrase to *who wants to borrow the book* (es, pt, de). The shorter Italian works if the form is self-evidently about one book.


## 5. Source-string problems worth fixing at source

Cases where the English source string is itself wrong, stale or inconsistent with its own translations. These need a decision about the source, not only about the Italian.

### 84. `Show editions separately?`

**Proposed Italian:** **Mostrare le edizioni separatamente?**

*phrase id 5190 · text domain Books · visible on 5 pages · in a `<input>`*

- **es**: ¿Mostrar ediciones obsoletas?

Translated from the key. Note the Spanish row says `¿Mostrar ediciones obsoletas?` — *obsolete* editions — which does not match the key at all. One of the two is wrong and it is not the key.

### 85. `Until 2019-10-18, this page will be oriented towards data-maintainers and therefore show the columns of pertinent information.`

**Proposed Italian:** **Fino al 18 ottobre 2019 questa pagina sarà orientata ai curatori dei dati e mostrerà quindi le colonne di informazioni pertinenti.**

*phrase id 7001 · text domain Schoenstatt · visible on 2 pages · in a `<p>`*

- **es**: Hasta el 10 de octubre del 2019, esta página se orientará a los que mantienen los datos y por lo tanto mostrar columnas de información pertiente.
- **pt**: Até 10 de outubro de 2019, esta página serve prioritariamente para o trabalho de introdução de dados e mostrará por isso as colunas de informação pertinentes.
- **de**: Bis zum 10. Oktober 2019, wird die Gestaltung dieser Webseite vorrangig der Arbeit der Datenpfleger dienen. Manche Informationsspalten werden dementsprechend angezeigt. 

Translated faithfully from the key, including the past date. Worth knowing that **es, pt and de all render the date as 10 October 2019 while the key says 2019-10-18** — the three sibling translations agree with each other and disagree with the key. I followed the key. The string is also stale content about a 2019 deadline and is a candidate for retirement rather than translation.

### 86. `Frau Dokto`

**Proposed Italian:** **Signora Dottoressa**

*phrase id 7308 · text domain Schoenstatt · not on a public page*

- **en** (the English row, which differs from the key): Doctor
- **es**: Señora Doctora
- **de**: Frau Dokto

The German key is a typo for `Frau Doktor`. I translated the meaning as `Signora Dottoressa`, following the English row (`Doctor`) and es (`Señora Doctora`). The key should be corrected at source; a separate row already exists for `Frau Dr.`.

### 87. `Google Knowledge Graph`

**Proposed Italian:** **Google Knowledge Graph**

*phrase id 6191 · text domain Application · not on a public page*

- **es**: Gráfico de Conocimiento de Google
- **pt**: Google Knowledge Graph
- **de**: Google Knowledge Graph (semantische Suchfunktion von Google)

Kept in English, following pt and de (de adds a gloss). Spanish translated it to `Gráfico de Conocimiento de Google`. This resolves a standing glossary question by house majority rather than by an Italian source — the Italian Wikipedia article is itself titled `Google Knowledge Graph`, which supports keeping it.

### 88. `https://en.wikipedia.org/wiki/Knowledge_Graph`

**Proposed Italian:** **https://it.wikipedia.org/wiki/Google_Knowledge_Graph**

*phrase id 6190 · text domain Application · not on a public page*

- **es**: https://es.wikipedia.org/wiki/Gr%C3%A1fico_de_conocimiento
- **pt**: https://pt.wikipedia.org/wiki/Google_Knowledge_Graph
- **de**: https://en.wikipedia.org/wiki/Knowledge_Graph

Repointed to `https://it.wikipedia.org/wiki/Google_Knowledge_Graph`, following es and pt, which each point at their own Wikipedia. **The Italian article's existence was taken from an earlier note in the glossary and has not been re-verified in this session** — worth one click before this reaches production, since a translated URL that 404s is worse than an English one that works.

### 89. `Legacy kernel: pages now render through Laminas\Mvc\Application for you only. Check /_health — it stops answering 200 on the laminas side.`

**Proposed Italian:** **Kernel legacy: le pagine ora vengono generate tramite Laminas\Mvc\Application solo per te. Controlla /_health — smette di rispondere 200 sul lato laminas.**

*phrase id 12861 · text domain Application · not on a public page*


A developer diagnostic banner, shown only to whoever has switched kernels. Translated because it renders, but `kernel`, `/_health` and `Laminas\Mvc\Application` are left as they are — they are code, not language. Arguably this string should not go through `translate()` at all.

### 90. `Please type the following text`

**Proposed Italian:** **Digita il testo seguente**

*phrase id 6677 · text domain ZfcUser · not on a public page*

- **en** (the English row, which differs from the key): Please type the following text:
- **es**: Favor tipear el texto siguiente:
- **pt**: Por favor digite o texto seguinte:
- **de**: Bitte geben Sie den folgenden Text ein:

Note the key lacks the trailing colon that the English row and all three siblings have. I followed the key and left the colon off; the row should probably be fixed at source instead.

### 91. `Sun-Sat 9-11am, 12-8pm, except first Tuesdays of the month`

**Proposed Italian:** **Dom-Sab 9-11 e 12-20, tranne il primo martedì del mese**

*phrase id 6945, 7029 · text domain Schoenstatt/default · not on a public page*


This is placeholder example text for the opening-hours field. I converted to the 24-hour clock, which is how Italian writes opening hours. Note the Spanish row says `Sábado-Domingo` (Sat–Sun) where the key says Sun–Sat, and drops the second time range — the Spanish is wrong and I followed the key.

### 92. `The form submitted did not originate from the expected site`

**Proposed Italian:** **Il modulo inviato non proviene dal sito previsto**

*phrase id 6599, 6622, 6835, 6925, 7111 · text domain Books/JTranslate/JUser/Schoenstatt/ZfcUser · not on a public page*

- **en** (the English row, which differs from the key): The form submitted was expired, please resubmit
- **es**: Se venció el formulario, favor vuele a enviarlo

Translated from the key. **The five language rows disagree about what this message says**: the English row and the Spanish say the form *expired*, while pt and de say it did not originate as expected. I followed the key, which pt and de agree with. If the underlying check is a CSRF check, the key is right and the English row is wrong.

### 93. `The input was not found in the haystack`

**Proposed Italian:** **Il valore inserito non è tra quelli ammessi**

*phrase id 7514 · text domain Schoenstatt · not on a public page*


`Il valore inserito non è tra quelli ammessi`. This is a Laminas framework validation message whose English is itself jargon (*haystack*). I translated the meaning rather than the metaphor; Laminas' own Italian translations may have a standard wording to match.

### 94. `This is the name that would be that will be shown to most users of the page (supposing most users are Schoenstatters). This field has no name formats as the pub`

**Proposed Italian:** **Questo è il nome che verrà mostrato alla maggior parte degli utenti della pagina (supponendo che siano in maggioranza schoenstattiani). Questo campo non ha formati di nome, a differenza del campo del nome pubblico. Se il nome interno coincide con quello pubblico, lascia il campo vuoto.**

*phrase id 6750 · text domain Schoenstatt · not on a public page*

- **en** (the English row, which differs from the key): This is the name that will be shown to most users of the page (supposing most users are Schoenstatters). This field has no name formats as the public name field does. If the internal name would be the same as the public name, please leave blank.
- **pt**: Este é o nome que será visto pela maioria dos utilizadores, pressupondo que a maioria serão schoenstattianos. Este campo não tem um formato estandardizado, ao contrário do campo "Nome público". Quando o nome interno for igual ao nome público, deixe este campo em branco.
- **de**: Dies ist der Name, den die meisten Nutzer sehen werden (vorausgesetzt, die meisten Nutzer sind Schönstätter). Dieses Feld hat keine standardisierte Namensformate, im Gegensatz zu dem Feld "öffentlicher Name". Falls der interne Name derselbe ist wie der öffentliche Name, bitte dieses Feld leer lassen.

The key contains an obvious slip — `that would be that will be`. The English row has it corrected. I translated the corrected sense. Nothing to decide here, but the key should be fixed at source rather than in translation.

### 95. `xxi+133`

**Proposed Italian:** **xxi+133**

*phrase id 7331 · text domain Books · not on a public page*


Left verbatim. This is a real page-count value in the roman+arabic form the `Number of pages` help text describes, not a translatable string — arguably it should not be in the phrase table at all.


## 6. Other judgement calls

Remaining judgement calls, lower stakes.

### 96. `Compilation texts`

**Proposed Italian:** **Raccolte di testi**

*phrase id 6686 · text domain Books · visible on 4 pages · in a `<h3>`*

- **es**: Compilaciones del Padre

`Raccolte di testi`. The Spanish row is `Compilaciones del Padre` — *the Father's compilations* — which names Kentenich explicitly where the key does not. If this category means specifically compiled Kentenich texts, `Raccolte di testi del Padre` would match Spanish.

### 97. `PK`

**Proposed Italian:** **PK**

*phrase id 6429 · text domain Books · visible on 4 pages · in a `<a>`*

- **en** (the English row, which differs from the key): JK Collection
- **es**: Colección PK

Left as `PK`. The English row renders `JK Collection` and Spanish `Colección PK`, so the abbreviation itself changes by language (P. Kentenich vs J. Kentenich). Italian would say `P. Kentenich`, so `PK` is right — but only if the abbreviation is displayed rather than matched.

### 98. `live`

**Proposed Italian:** **attivo**

*phrase id 12898 · text domain JUser · visible on 3 pages · in a `<td>`*


`attivo`. This is the status column of the API-token table, where `live` means not yet revoked. `attivo` is the natural Italian for that, but if the column also shows `revoked` and `expired` the three want to read as a set.

### 99. `Regens`

**Proposed Italian:** **Rettore**

*phrase id 5183, 6612 · text domain Schoenstatt/SionModel · visible on 3 pages · in a `<a>`*

- **en** (the English row, which differs from the key): Rector
- **es**: Rector
- **pt**: Reitor
- **de**: Regens

`Rettore` for both `Regens` and `Rektor`, which are two separate phrases with the same meaning. es renders both `Rector`. If the site needs to distinguish a seminary *Regens* from a house *Rektor*, Italian collapses them here.

### 100. `Berlin-Frohnau`

**Proposed Italian:** **Berlino-Frohnau**

*phrase id 6545 · text domain Schoenstatt · visible on 2 pages · in a `<a>`*

- **es**: Berlin-Frohnau
- **pt**: Berlim-Frohnau
- **de**: Berlin-Frohnau

`Berlino-Frohnau`. Portuguese translates the city (`Berlim-Frohnau`); Spanish and German keep `Berlin`. Italian normally says Berlino, but this is a shrine's place-name label and may be better left as the German.
