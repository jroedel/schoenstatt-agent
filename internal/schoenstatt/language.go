package schoenstatt

import (
	"fmt"
	"sort"
	"strings"
)

// LanguageMap translates between the simple language codes this tooling speaks
// ("en", "it") and whatever codes the API actually reports.
//
// The two are not the same thing today: the API reports "en_US", "it_IT" and
// so on, while schoenstatt.link is moving toward presenting simple language
// codes and hiding the internal regional ones. Everything an agent sees from
// this server is the simple form, and every request to the API is sent in the
// form the API reported. When the API completes its move to simple codes the
// mapping becomes the identity and nothing here needs to change.
//
// This is why the language list is never hardcoded. It is read from
// GET /api/v3/schema/phrase at runtime, which the schema itself describes as
// "read from the merged configuration at request time".
type LanguageMap struct {
	// apiCodes is the list exactly as the API reported it, order preserved.
	apiCodes []string
	// publicOf maps an API code to the code agents use.
	publicOf map[string]string
	// apiOf maps every accepted spelling to the API code.
	apiOf map[string]string
}

// NewLanguageMap builds the mapping from the codes the API reported.
//
// A simple alias is created only where it is unambiguous. If the API ever
// reports both "pt_BR" and "pt_PT", "pt" names neither of them and the full
// code is required — silently picking one would write a translation into the
// wrong language, which is not recoverable.
func NewLanguageMap(apiCodes []string) (*LanguageMap, error) {
	if len(apiCodes) == 0 {
		return nil, fmt.Errorf("the API reported no writable languages")
	}

	byShort := map[string][]string{}
	for _, code := range apiCodes {
		short := strings.ToLower(code)
		if i := strings.IndexAny(short, "_-"); i > 0 {
			short = short[:i]
		}
		byShort[short] = append(byShort[short], code)
	}

	m := &LanguageMap{
		apiCodes: append([]string(nil), apiCodes...),
		publicOf: make(map[string]string, len(apiCodes)),
		apiOf:    make(map[string]string, len(apiCodes)*2),
	}
	for _, code := range apiCodes {
		// The API's own spelling is always accepted as input, so a caller
		// working from the raw schema is never wrong.
		m.apiOf[strings.ToLower(code)] = code
		m.publicOf[code] = code
	}
	for short, codes := range byShort {
		if len(codes) != 1 {
			continue // ambiguous — no alias, full code required
		}
		m.apiOf[short] = codes[0]
		m.publicOf[codes[0]] = short
	}
	return m, nil
}

// Public returns the code agents see for an API code.
func (m *LanguageMap) Public(apiCode string) string {
	if p, ok := m.publicOf[apiCode]; ok {
		return p
	}
	return apiCode
}

// API resolves anything a caller might reasonably write into the code the API
// expects. The error names the accepted values, because an agent that guesses
// a language and gets a bare rejection will guess again.
func (m *LanguageMap) API(input string) (string, error) {
	if code, ok := m.apiOf[strings.ToLower(strings.TrimSpace(input))]; ok {
		return code, nil
	}
	return "", fmt.Errorf("unknown language %q; this site writes %s",
		input, strings.Join(m.PublicCodes(), ", "))
}

// PublicCodes lists the languages in the form agents use, sorted for stable output.
func (m *LanguageMap) PublicCodes() []string {
	out := make([]string, 0, len(m.apiCodes))
	for _, code := range m.apiCodes {
		out = append(out, m.Public(code))
	}
	sort.Strings(out)
	return out
}

// APICodes lists the languages exactly as the API reported them.
func (m *LanguageMap) APICodes() []string {
	return append([]string(nil), m.apiCodes...)
}
