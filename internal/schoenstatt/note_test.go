package schoenstatt

import (
	"encoding/json"
	"strings"
	"testing"
)

// The reason this test exists rather than a comment: a JSON null keyed by a
// language was the retraction until 2026-08-11 and is a 422 after it, and the
// ways to emit one by accident all look like ordinary code. `patchBody` keeps
// translations as a map[string]string precisely so the type system refuses, and a
// later refactor to map[string]any would silently remove that guarantee while
// every other test still passed.
func TestPatchBodyCannotEmitANullTranslation(t *testing.T) {
	// The three shapes that produce a null elsewhere: an absent language, one
	// explicitly set to empty, and a whole absent note.
	body := patchBody(map[string]string{"it": "Santuario", "de": ""}, "_note", "")

	raw, err := json.Marshal(body)
	if err != nil {
		t.Fatalf("marshalling the body: %v", err)
	}
	if strings.Contains(string(raw), "null") {
		t.Fatalf("a patch body marshalled a null: %s", raw)
	}

	var round map[string]any
	if err := json.Unmarshal(raw, &round); err != nil {
		t.Fatalf("unmarshalling: %v", err)
	}
	for code, v := range round {
		if _, ok := v.(string); !ok {
			t.Errorf("%s marshalled as %T, want string — only a string can be sent as a translation", code, v)
		}
	}
}

// An empty note must not appear at all. A present-but-empty `_note` is a
// different request from one that omits it, and the server has to decide what an
// empty justification means; not sending one is unambiguous.
func TestPatchBodyOmitsAnEmptyNote(t *testing.T) {
	raw, _ := json.Marshal(patchBody(map[string]string{"it": "Santuario"}, "_note", ""))
	if strings.Contains(string(raw), "_note") {
		t.Errorf("an empty note reached the wire: %s", raw)
	}

	raw, _ = json.Marshal(patchBody(map[string]string{"it": "Santuario"}, "_note", "because"))
	var got map[string]any
	if err := json.Unmarshal(raw, &got); err != nil {
		t.Fatal(err)
	}
	if got["_note"] != "because" {
		t.Errorf("_note = %v, want \"because\"", got["_note"])
	}
	if got["it"] != "Santuario" {
		t.Errorf("the translation did not survive alongside the note: %s", raw)
	}
}

// The note key comes from the schema rather than from a constant here, so a site
// that renames it is followed rather than silently written to under the old name.
func TestPatchBodyUsesTheSchemasNoteKey(t *testing.T) {
	raw, _ := json.Marshal(patchBody(map[string]string{"it": "x"}, "_reason", "why"))
	if !strings.Contains(string(raw), "_reason") {
		t.Errorf("the schema's note key was not used: %s", raw)
	}
}

// `_note` and `_retract` were added to the schema in schoenstatt.link#61. A site
// deployed before that publishes neither, and this client has to keep working
// against it — so the accessors fall back to the documented values rather than
// returning a zero that would send `""` as a key or trim every note to nothing.
func TestNoteAccessorsFallBackOnAnOlderSchema(t *testing.T) {
	var old PhraseSchema
	if err := json.Unmarshal([]byte(`{"writable":{"languages":["it"],"maxLength":2000}}`), &old); err != nil {
		t.Fatal(err)
	}
	if got := old.NoteKey(); got != "_note" {
		t.Errorf("NoteKey() on a pre-#61 schema = %q, want %q", got, "_note")
	}
	if got := old.NoteLimit(); got != 255 {
		t.Errorf("NoteLimit() on a pre-#61 schema = %d, want 255", got)
	}
}

// And when the site does publish them, they are what is used — the point of
// reading the schema at request time is that this file holds no contract of its
// own. The fixture is the shape production served on 2026-08-11.
func TestNoteAccessorsPreferTheSchema(t *testing.T) {
	var s PhraseSchema
	body := `{"writable":{"languages":["es","de","pt","it","en"],"maxLength":2000,
	          "note":{"key":"_note","maxLength":255},
	          "retract":{"key":"_retract","value":"a list of language codes"}}}`
	if err := json.Unmarshal([]byte(body), &s); err != nil {
		t.Fatal(err)
	}
	if got := s.NoteKey(); got != "_note" {
		t.Errorf("NoteKey() = %q", got)
	}
	if got := s.NoteLimit(); got != 255 {
		t.Errorf("NoteLimit() = %d", got)
	}
	// Read but never sent: this server holds a translator credential for filling
	// gaps, and removal is deliberately not one of its five tools. Parsing it is
	// how a caller can tell a site that has retraction from one where a bare null
	// still deleted.
	if got := s.Writable.Retract.Key; got != "_retract" {
		t.Errorf("Retract.Key = %q, want %q", got, "_retract")
	}
}

// A batch's notes are per entry, and one entry's note must not leak onto another.
// The failure this pins is a real one: building the wire map by mutating a shared
// body would attribute every write in the batch to the last reason given.
func TestBatchNotesStayWithTheirOwnPhrase(t *testing.T) {
	entries := map[string]BatchEntry{
		"1": {Translations: map[string]string{"it": "uno"}, Note: "first reason"},
		"2": {Translations: map[string]string{"it": "due"}},
	}
	wire := make(map[string]any, len(entries))
	for id, e := range entries {
		wire[id] = patchBody(e.Translations, "_note", e.Note)
	}
	raw, _ := json.Marshal(wire)
	var got map[string]map[string]any
	if err := json.Unmarshal(raw, &got); err != nil {
		t.Fatal(err)
	}
	if got["1"]["_note"] != "first reason" {
		t.Errorf("phrase 1 lost its note: %v", got["1"])
	}
	if _, ok := got["2"]["_note"]; ok {
		t.Errorf("phrase 2 was given a note it did not ask for: %v", got["2"])
	}
}

// A retirement without a reason is refused on this side as well as by the server.
// The server's 422 is correct and sufficient; this exists so the message names the
// phrase, and so a batch of retirements fails on the one that forgot rather than
// after a round trip.
func TestRetirementNeedsAReason(t *testing.T) {
	for _, note := range []string{"", "   ", "\n\t "} {
		_, _, err := prepareRetirementNote(13661, "retire", note, 255)
		if err == nil {
			t.Errorf("a blank reason %q was accepted", note)
			continue
		}
		if !strings.Contains(err.Error(), "13661") {
			t.Errorf("the error should name the phrase so a batch says which one failed; got %q", err)
		}
	}
}

// The failure this pins actually happened: a 270-character retirement note was
// sent to production by hand, and the server trimmed it at 255 mid-word — losing
// the clause that said what to do if the phrase came back, which is the part a
// retirement note exists for. The server trims silently; this must not.
func TestOverLongRetirementNoteIsReportedNotSilentlyTrimmed(t *testing.T) {
	long := strings.Repeat("a", 260) + " TAIL"
	sent, remark, err := prepareRetirementNote(1, "retire", long, 255)
	if err != nil {
		t.Fatalf("an over-long note should be trimmed, not refused: %v", err)
	}
	if remark == "" {
		t.Fatal("an over-long retirement note was trimmed without telling the caller")
	}
	if !strings.Contains(remark, "265") || !strings.Contains(remark, "255") {
		t.Errorf("the remark should name both lengths so the caller can shorten it; got %q", remark)
	}
	if len([]rune(sent)) > 255 {
		t.Errorf("the trimmed note is still %d characters", len([]rune(sent)))
	}
	// And a note inside the limit must produce no remark at all, or the warning
	// becomes noise that gets ignored.
	if _, remark, _ := prepareRetirementNote(1, "retire", "short reason", 255); remark != "" {
		t.Errorf("a note within the limit produced a remark: %q", remark)
	}
}
