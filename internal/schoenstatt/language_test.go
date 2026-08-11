package schoenstatt

import (
	"strings"
	"testing"
)

// The API reports regional codes today and simple ones after the migration.
// Both must present the same surface to an agent, because the agent's prompts,
// the glossary filenames and the committed style guides all speak simple codes
// and none of them should have to change when the API flips.
func TestPublicSurfaceSurvivesTheLanguageCodeMigration(t *testing.T) {
	before := []string{"es_ES", "de_DE", "pt_BR", "it_IT", "en_US"}
	after := []string{"es", "de", "pt", "it", "en"}

	for _, codes := range [][]string{before, after} {
		m, err := NewLanguageMap(codes)
		if err != nil {
			t.Fatalf("NewLanguageMap(%v): %v", codes, err)
		}
		got := strings.Join(m.PublicCodes(), ",")
		if want := "de,en,es,it,pt"; got != want {
			t.Errorf("PublicCodes() for %v = %q, want %q", codes, got, want)
		}
	}
}

func TestAPIResolvesBothSpellings(t *testing.T) {
	m, err := NewLanguageMap([]string{"es_ES", "de_DE", "pt_BR", "it_IT", "en_US"})
	if err != nil {
		t.Fatal(err)
	}
	for input, want := range map[string]string{
		"en":    "en_US", // the code agents use
		"it":    "it_IT",
		"IT":    "it_IT", // case-insensitive
		" it ":  "it_IT", // stray whitespace
		"it_IT": "it_IT", // the API's own spelling still works
	} {
		got, err := m.API(input)
		if err != nil {
			t.Errorf("API(%q): %v", input, err)
			continue
		}
		if got != want {
			t.Errorf("API(%q) = %q, want %q", input, got, want)
		}
	}
}

func TestUnknownLanguageNamesTheValidOnes(t *testing.T) {
	m, _ := NewLanguageMap([]string{"en_US", "it_IT"})
	_, err := m.API("fr")
	if err == nil {
		t.Fatal("API(\"fr\") succeeded; an unknown language must be refused")
	}
	// An agent that guesses a locale and gets a bare rejection guesses again.
	for _, want := range []string{"en", "it"} {
		if !strings.Contains(err.Error(), want) {
			t.Errorf("error %q does not name the valid language %q", err, want)
		}
	}
}

// If the site ever serves two Portuguese variants, "pt" names neither of them.
// Guessing would write a translation into the wrong locale, and a translation
// cannot be unwritten.
func TestAmbiguousLanguageGetsNoAlias(t *testing.T) {
	m, err := NewLanguageMap([]string{"en_US", "pt_BR", "pt_PT"})
	if err != nil {
		t.Fatal(err)
	}
	if _, err := m.API("pt"); err == nil {
		t.Error("API(\"pt\") resolved despite pt_BR and pt_PT both being writable")
	}
	for _, code := range []string{"pt_BR", "pt_PT"} {
		if got, err := m.API(code); err != nil || got != code {
			t.Errorf("API(%q) = %q, %v; the full code must still resolve", code, got, err)
		}
	}
	if got := m.Public("pt_BR"); got != "pt_BR" {
		t.Errorf("Public(\"pt_BR\") = %q; an ambiguous language must show its full code", got)
	}
	if got := m.Public("en_US"); got != "en" {
		t.Errorf("Public(\"en_US\") = %q, want \"en\"; the unambiguous ones still shorten", got)
	}
}

func TestEmptyLanguageListIsAnError(t *testing.T) {
	if _, err := NewLanguageMap(nil); err == nil {
		t.Error("NewLanguageMap(nil) succeeded; there is nothing to write to")
	}
}

// The site renamed writable.locales to writable.languages on 2026-08-10 and
// changed the codes with it. A client that reads only one key silently sees no
// writable languages at all and refuses every write — which is how this was
// found. Read both.
func TestWritableCodesReadsEitherSchemaKey(t *testing.T) {
	var afterRename PhraseSchema
	afterRename.Writable.Languages = []string{"es", "de", "pt", "it", "en"}

	var beforeRename PhraseSchema
	beforeRename.Writable.Locales = []string{"es_ES", "de_DE", "pt_BR", "it_IT", "en_US"}

	for name, schema := range map[string]PhraseSchema{
		"languages": afterRename,
		"locales":   beforeRename,
	} {
		codes := schema.WritableCodes()
		if len(codes) != 5 {
			t.Fatalf("WritableCodes() with writable.%s = %v, want 5 codes", name, codes)
		}
		m, err := NewLanguageMap(codes)
		if err != nil {
			t.Fatalf("writable.%s: %v", name, err)
		}
		if got, want := strings.Join(m.PublicCodes(), ","), "de,en,es,it,pt"; got != want {
			t.Errorf("writable.%s exposes %q, want %q", name, got, want)
		}
	}
}

// Once the API reports simple codes it also refuses the regional form, so the
// server must stop offering it rather than forwarding a request it knows will
// be rejected.
func TestRegionalFormIsRefusedAfterTheRename(t *testing.T) {
	m, err := NewLanguageMap([]string{"es", "de", "pt", "it", "en"})
	if err != nil {
		t.Fatal(err)
	}
	if _, err := m.API("it_IT"); err == nil {
		t.Error(`API("it_IT") resolved; the API refuses the locale form of a listed language`)
	}
	if got, err := m.API("it"); err != nil || got != "it" {
		t.Errorf(`API("it") = %q, %v; want "it"`, got, err)
	}
}
