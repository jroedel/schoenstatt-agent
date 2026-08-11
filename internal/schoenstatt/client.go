package schoenstatt

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"sync"
	"time"
)

// MaxBatchPhrases is the API's ceiling on one batch write. The limit exists so
// a batch cannot run into max_execution_time half written.
const MaxBatchPhrases = 200

// Client talks to /api/v3. It holds one credential and therefore reaches one
// resource: phrases. Associations are a separate role and deliberately absent.
type Client struct {
	baseURL string
	token   string
	http    *http.Client

	schemaOnce sync.Once
	schema     *PhraseSchema
	languages  *LanguageMap
	schemaErr  error
}

func NewClient(cfg Config) *Client {
	return &Client{
		baseURL: cfg.BaseURL,
		token:   cfg.Token,
		http:    &http.Client{Timeout: 60 * time.Second},
	}
}

// PhraseSchema is the part of GET /api/v3/schema/phrase this server relies on.
//
// The writable set was called `locales` and carried regional codes ("en_US")
// until 2026-08-10, when it became `languages` carrying ISO 639-1 codes
// ("en"). Both spellings are read so a client is not broken by which side of
// that change the site it is pointed at happens to be on.
type PhraseSchema struct {
	Writable struct {
		Languages []string `json:"languages"`
		Locales   []string `json:"locales"`
		MaxLength int      `json:"maxLength"`
		// Note is the reserved `_note` key: the reason for a write, attached to
		// the history rows that write destroys. Published in the schema since
		// schoenstatt.link#61; before that it existed but was undiscoverable, so
		// a zero MaxLength here means "an older site" rather than "no notes".
		Note struct {
			Key       string `json:"key"`
			MaxLength int    `json:"maxLength"`
		} `json:"note"`
		// Retract is the reserved `_retract` key, which takes a list of language
		// codes and is the only way to remove a translation. Read but never sent
		// by this server: it holds a translator credential for filling gaps, and
		// removal is not one of the five tools. Present so a caller can tell a
		// site that has retraction from one where a bare null still deleted.
		Retract struct {
			Key string `json:"key"`
		} `json:"retract"`
	} `json:"writable"`
}

// NoteKey is the reserved key carrying the reason for a write, and NoteLimit the
// length the site trims it to. Both come from the schema when the site publishes
// them, with the documented values as the fallback for a site that does not.
func (s *PhraseSchema) NoteKey() string {
	if s.Writable.Note.Key != "" {
		return s.Writable.Note.Key
	}
	return "_note"
}

func (s *PhraseSchema) NoteLimit() int {
	if s.Writable.Note.MaxLength > 0 {
		return s.Writable.Note.MaxLength
	}
	return 255
}

// WritableCodes returns the language codes the site accepts, under whichever
// key this API version reports them.
func (s *PhraseSchema) WritableCodes() []string {
	if len(s.Writable.Languages) > 0 {
		return s.Writable.Languages
	}
	return s.Writable.Locales
}

// Schema fetches the phrase contract once per process and caches it. It is
// generated from the same specification the endpoints validate with, so it
// cannot drift from what is actually enforced.
func (c *Client) Schema(ctx context.Context) (*PhraseSchema, *LanguageMap, error) {
	c.schemaOnce.Do(func() {
		var s PhraseSchema
		// The schema endpoints are public — no token, so a broken credential
		// still yields a useful error rather than a bare 401 here.
		if err := c.do(ctx, http.MethodGet, "/api/v3/schema/phrase", nil, nil, &s, nil); err != nil {
			c.schemaErr = fmt.Errorf("reading the phrase schema: %w", err)
			return
		}
		languages, err := NewLanguageMap(s.WritableCodes())
		if err != nil {
			c.schemaErr = err
			return
		}
		c.schema, c.languages = &s, languages
	})
	return c.schema, c.languages, c.schemaErr
}

// Phrase is one row of trans_phrases with its translations.
//
// Translations always carry an entry per writable language, present with a null
// text when there is no row — an agent that has to distinguish "key missing"
// from "key null" to find its work will get it wrong.
type Phrase struct {
	PhraseID   int    `json:"phraseId"`
	TextDomain string `json:"textDomain"`
	Phrase     string `json:"phrase"`
	// Translations is keyed by the API's language codes; callers translate to
	// public codes at the boundary.
	Translations map[string]struct {
		Text       *string `json:"text"`
		ModifiedOn *string `json:"modifiedOn"`
		ModifiedBy *int    `json:"modifiedBy"`
	} `json:"translations"`
	Context struct {
		OriginRoute string  `json:"originRoute"`
		URL         *string `json:"url"`
	} `json:"context"`
	Meta struct {
		AddedOn string `json:"addedOn"`
		ETag    string `json:"etag"`
		URL     string `json:"url"`
		// RetiredOn is the flag: non-nil means this row is off the translator's
		// worklist. The row still exists and the site still renders it, so this
		// is not a deletion and not an absence of translations.
		RetiredOn *string `json:"retiredOn"`
	} `json:"meta"`
}

// Retired reports whether this phrase is off the translator's worklist.
func (p *Phrase) Retired() bool {
	return p.Meta.RetiredOn != nil && *p.Meta.RetiredOn != ""
}

// SearchParams are the filters the collection endpoint reaches the database
// with, rather than applying after the paging decision.
type SearchParams struct {
	TextDomain     string
	OriginRoute    string
	Search         string
	UntranslatedIn string // API language code
	TranslatedIn   string // API language code
	// OriginRouteLike is OriginRoute with the caller's % and _ treated as
	// wildcards. Search escapes those; this deliberately does not.
	OriginRouteLike string
	// OnlyRetired lists only retired phrases, IncludeRetired lists both. Retired
	// rows are hidden by default, because the point of retiring one is to stop
	// asking for work on it. OnlyRetired is how a retirement is audited
	// afterwards, and how a phrase that came back is noticed.
	OnlyRetired    bool
	IncludeRetired bool
	Limit          int
	Offset         int
}

type SearchResult struct {
	Phrases []Phrase `json:"phrases"`
	Total   int      `json:"total"`
	Limit   int      `json:"limit"`
	Offset  int      `json:"offset"`
}

func (c *Client) Search(ctx context.Context, p SearchParams) (*SearchResult, error) {
	q := url.Values{}
	set := func(k, v string) {
		if v != "" {
			q.Set(k, v)
		}
	}
	set("textDomain", p.TextDomain)
	set("originRoute", p.OriginRoute)
	set("search", p.Search)
	set("untranslatedIn", p.UntranslatedIn)
	set("translatedIn", p.TranslatedIn)
	set("originRouteLike", p.OriginRouteLike)
	if p.OnlyRetired {
		q.Set("onlyRetired", "1")
	}
	if p.IncludeRetired {
		q.Set("includeRetired", "1")
	}
	if p.Limit > 0 {
		q.Set("limit", fmt.Sprint(p.Limit))
	}
	if p.Offset > 0 {
		q.Set("offset", fmt.Sprint(p.Offset))
	}

	path := "/api/v3/phrases"
	if len(q) > 0 {
		path += "?" + q.Encode()
	}

	// The collection's envelope has varied less than its key names; decode
	// loosely so a rename upstream degrades to an empty list rather than an
	// error the agent can do nothing about.
	var raw map[string]json.RawMessage
	if err := c.do(ctx, http.MethodGet, path, nil, nil, &raw, nil); err != nil {
		return nil, err
	}
	out := &SearchResult{Limit: p.Limit, Offset: p.Offset}
	for _, key := range []string{"phrases", "data", "items"} {
		if v, ok := raw[key]; ok {
			if err := json.Unmarshal(v, &out.Phrases); err == nil {
				break
			}
		}
	}
	if v, ok := raw["total"]; ok {
		_ = json.Unmarshal(v, &out.Total)
	}
	return out, nil
}

// Get returns one phrase and the ETag to send back with a write.
func (c *Client) Get(ctx context.Context, phraseID int) (*Phrase, string, error) {
	var p Phrase
	var hdr http.Header
	path := fmt.Sprintf("/api/v3/phrases/%d", phraseID)
	if err := c.do(ctx, http.MethodGet, path, nil, nil, &p, &hdr); err != nil {
		return nil, "", err
	}
	etag := p.Meta.ETag
	if etag == "" {
		etag = hdr.Get("ETag")
	}
	return &p, etag, nil
}

type PatchResult struct {
	Changed []string `json:"changed"`
	Phrase  *Phrase  `json:"phrase"`
	Warning string   `json:"warning,omitempty"`
}

// patchBody assembles a wire body from translations plus an optional note.
//
// translations stays a map[string]string all the way down, which is what makes a
// JSON null structurally impossible to send: Go marshals a missing string as ""
// and never as null. That matters more than it reads. A bare null keyed by a
// language was the retraction until 2026-08-11 and is a 422 after it, and in both
// eras the ways to emit one by accident — a serializer's default for an absent
// optional field, a map lookup that missed, a nil pointer — look nothing like a
// deletion at the call site. Keeping the concrete type is the guard; there is no
// check to forget.
//
// noteKey is passed in rather than hardcoded because the schema publishes it.
func patchBody(translations map[string]string, noteKey, note string) any {
	if note == "" {
		return translations
	}
	body := make(map[string]any, len(translations)+1)
	for code, text := range translations {
		body[code] = text
	}
	body[noteKey] = note
	return body
}

// Patch writes translations for one phrase. translations is keyed by API
// language codes.
//
// note, when non-empty, is sent as the reserved `_note` key: the reason for the
// write. It attaches to the history row for each translation this write
// destroys, and is dropped by the server when the write only fills gaps — so it
// is never noise and there is no reason to withhold it.
//
// ifMatch should carry the ETag from the Get that produced the text being
// replaced. Omitting it is permitted and means a blind write.
func (c *Client) Patch(ctx context.Context, phraseID int, translations map[string]string, noteKey, note, ifMatch string) (*PatchResult, error) {
	var hdrs http.Header
	if ifMatch != "" {
		hdrs = http.Header{"If-Match": []string{ifMatch}}
	}
	var out PatchResult
	path := fmt.Sprintf("/api/v3/phrases/%d", phraseID)
	if err := c.do(ctx, http.MethodPatch, path, patchBody(translations, noteKey, note), hdrs, &out, nil); err != nil {
		return nil, err
	}
	return &out, nil
}

type BatchOutcome struct {
	OK      bool     `json:"ok"`
	Changed []string `json:"changed,omitempty"`
	Status  int      `json:"status,omitempty"`
	Message string   `json:"message,omitempty"`
}

type BatchResult struct {
	Results map[string]BatchOutcome `json:"results"`
	Summary struct {
		Received int `json:"received"`
		Applied  int `json:"applied"`
		Failed   int `json:"failed"`
	} `json:"summary"`
	Warning string `json:"warning,omitempty"`
}

// BatchEntry is one phrase's worth of a batch: its translations and, optionally,
// the reason for the write. One note per phrase, on the same terms as a single
// PATCH — the API takes it per entry, not once for the batch, because a batch is
// a set of independent writes and a shared justification would be a fiction.
type BatchEntry struct {
	Translations map[string]string
	Note         string
}

// BatchPatch writes many phrases in one request, recompiling the catalogs once
// at the end rather than once per phrase.
//
// phrases is keyed by phrase id as a string.
func (c *Client) BatchPatch(ctx context.Context, phrases map[string]BatchEntry, noteKey string) (*BatchResult, error) {
	if len(phrases) > MaxBatchPhrases {
		return nil, fmt.Errorf("%d phrases exceeds the API's limit of %d per batch; split the work",
			len(phrases), MaxBatchPhrases)
	}
	wire := make(map[string]any, len(phrases))
	for id, entry := range phrases {
		wire[id] = patchBody(entry.Translations, noteKey, entry.Note)
	}
	body := map[string]any{"phrases": wire}
	var out BatchResult
	if err := c.do(ctx, http.MethodPatch, "/api/v3/phrases", body, nil, &out, nil); err != nil {
		return nil, err
	}
	return &out, nil
}

// RetireResult is the answer to a retire or un-retire. changed is false when the
// phrase was already in the state asked for, which is a 200 and not an error: the
// endpoint is idempotent and writes no second history entry, so a retry cannot
// forge a second judgement.
type RetireResult struct {
	Changed bool    `json:"changed"`
	Phrase  *Phrase `json:"phrase"`
	Warning string  `json:"warning,omitempty"`
}

// Retire takes a phrase off the translator's worklist. It destroys nothing: every
// translation stays, the compiled catalogs still carry it, and the site renders
// exactly what it rendered before.
//
// note is REQUIRED — a 422 without it, unlike on a write, and the asymmetry is
// right. A write's note explains a replacement the history records anyway; a
// retirement's note is the entire record of a judgement, read at the one moment
// it matters: when the phrase is back on the worklist and somebody has to work
// out whether the retirement was wrong or the code that files the phrase is.
//
// It is refused here as well as by the server so the caller is told which phrase
// it forgot a reason for, and trimmed here so an over-long note is reported
// rather than silently losing its tail — which is the more important half, since
// the tail of a retirement note is usually the part that says what to do if the
// phrase comes back.
func (c *Client) Retire(ctx context.Context, phraseID int, noteKey, note string, noteLimit int) (*RetireResult, string, error) {
	return c.setRetired(ctx, phraseID, "retire", noteKey, note, noteLimit)
}

// Unretire puts a phrase back on the worklist by hand. Same body, and the same
// requirement to say why.
//
// It writes an `unretire` history entry, and that entry's ABSENCE is what carries
// information: a phrase that is live again with a `retire` and no `unretire`
// after it came back because a render missed on it, which means the retirement
// was wrong. So do not un-retire a row in order to tidy up a note — it overwrites
// that signal with a false account of a judgement.
func (c *Client) Unretire(ctx context.Context, phraseID int, noteKey, note string, noteLimit int) (*RetireResult, string, error) {
	return c.setRetired(ctx, phraseID, "unretire", noteKey, note, noteLimit)
}

// prepareRetirementNote validates and bounds the reason for a retirement,
// returning the text to send and a remark for the caller if anything was done to
// it. Pure, so the rules can be tested without a server — which is the point:
// these two rules are the ones that were got wrong by hand.
func prepareRetirementNote(phraseID int, action, note string, noteLimit int) (string, string, error) {
	note = strings.TrimSpace(note)
	if note == "" {
		return "", "", fmt.Errorf(
			"phrase %d: a %s needs a reason. It is the only record of this judgement, and it is "+
				"read when the phrase is back on the worklist and somebody has to tell a wrong "+
				"retirement from a bug in the code that files the phrase", phraseID, action)
	}
	if noteLimit > 0 {
		if runes := []rune(note); len(runes) > noteLimit {
			return strings.TrimSpace(string(runes[:noteLimit])), fmt.Sprintf(
				"the reason was %d characters and the site stores %d, so it was trimmed. Put the "+
					"essential thing first: what this row is, and what it means if it comes back",
				len(runes), noteLimit), nil
		}
	}
	return note, "", nil
}

func (c *Client) setRetired(ctx context.Context, phraseID int, action, noteKey, note string, noteLimit int) (*RetireResult, string, error) {
	note, remark, err := prepareRetirementNote(phraseID, action, note, noteLimit)
	if err != nil {
		return nil, "", err
	}
	if noteKey == "" {
		noteKey = "_note"
	}
	var out RetireResult
	path := fmt.Sprintf("/api/v3/phrases/%d/%s", phraseID, action)
	if err := c.do(ctx, http.MethodPost, path, map[string]string{noteKey: note}, nil, &out, nil); err != nil {
		return nil, remark, err
	}
	return &out, remark, nil
}

// apiError carries the API's own message so a refusal is actionable rather
// than a bare status code.
type apiError struct {
	Status  int
	Message string
	Body    string
}

func (e *apiError) Error() string {
	switch e.Status {
	case http.StatusUnauthorized:
		return "401 from the API: the token is missing, malformed, expired, revoked, " +
			"unregistered, or its account lacks sch_api_translator — every one of those " +
			"is the same answer, on purpose. Check, in order: is the capsule up, is the " +
			"token in " + CredentialsPath + ", does the account hold sch_api_translator, " +
			"has database/db6.8.sql been applied. (" + e.Message + ")"
	case http.StatusPreconditionFailed:
		return "412: the phrase moved since it was read. Re-read it and re-apply the change."
	case http.StatusNotFound:
		return "404: no phrase has that id in this project. Phrase ids are scoped to " +
			"this site; an id belonging to another project is a 404, not a leak."
	case http.StatusUnprocessableEntity:
		return "422: " + e.Message
	}
	if e.Message != "" {
		return fmt.Sprintf("%d from the API: %s", e.Status, e.Message)
	}
	return fmt.Sprintf("%d from the API: %s", e.Status, truncate(e.Body, 400))
}

func (c *Client) do(ctx context.Context, method, path string, body any, hdrs http.Header, out any, respHdr *http.Header) error {
	var reader io.Reader
	if body != nil {
		encoded, err := json.Marshal(body)
		if err != nil {
			return fmt.Errorf("encoding the request: %w", err)
		}
		reader = bytes.NewReader(encoded)
	}

	req, err := http.NewRequestWithContext(ctx, method, c.baseURL+path, reader)
	if err != nil {
		return err
	}
	if c.token != "" {
		req.Header.Set("Authorization", "Bearer "+c.token)
	}
	req.Header.Set("Accept", "application/json")
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}
	for k, vs := range hdrs {
		for _, v := range vs {
			req.Header.Add(k, v)
		}
	}

	resp, err := c.http.Do(req)
	if err != nil {
		return fmt.Errorf("reaching %s: %w (is the capsule up? `docker compose up -d` in the schoenstatt.link checkout)", c.baseURL, err)
	}
	defer resp.Body.Close()

	raw, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("reading the response: %w", err)
	}
	if respHdr != nil {
		*respHdr = resp.Header
	}

	if resp.StatusCode >= 400 {
		return &apiError{Status: resp.StatusCode, Message: extractMessage(raw), Body: string(raw)}
	}
	if out == nil || len(bytes.TrimSpace(raw)) == 0 {
		return nil
	}
	if err := json.Unmarshal(raw, out); err != nil {
		return fmt.Errorf("decoding the response from %s: %w", path, err)
	}
	return nil
}

// extractMessage pulls the API's error prose, including the per-field validator
// messages a 422 carries — those are the translator form's own messages and say
// exactly what a moderator would be told.
func extractMessage(raw []byte) string {
	var envelope struct {
		Error struct {
			Message  string                       `json:"message"`
			Messages map[string]map[string]string `json:"messages"`
		} `json:"error"`
	}
	if err := json.Unmarshal(raw, &envelope); err != nil {
		return ""
	}
	msg := envelope.Error.Message
	var details []string
	for field, validators := range envelope.Error.Messages {
		for _, text := range validators {
			details = append(details, field+": "+text)
		}
	}
	if len(details) > 0 {
		msg += " (" + strings.Join(details, "; ") + ")"
	}
	return msg
}

func truncate(s string, n int) string {
	if len(s) <= n {
		return s
	}
	return s[:n] + "…"
}
