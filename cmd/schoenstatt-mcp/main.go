// Command schoenstatt-mcp exposes the schoenstatt.link translation API as MCP
// tools.
//
// It carries one credential, holding the sch_api_translator role, and therefore
// reaches one resource: phrases. The association (shrine) endpoints are a
// different role and are deliberately not implemented here — a leaked
// translator token should have nothing shrine-shaped to reach even by accident.
//
// The tools encode the parts of the contract that are easy to get wrong and
// expensive to get wrong. Two of those moved on 2026-08-11: translations now
// have a revision history, so an overwrite is recoverable, and removal is the
// explicit `_retract` key rather than a bare JSON null. Neither makes a careless
// write cheap — reverting one needs somebody to notice it, and a plausible
// mistranslation is exactly what nobody notices. So the tools still refuse an
// empty or over-long translation before sending, still do not expose removal,
// and now carry the `_note` that makes an overwrite reviewable afterwards.
// What the server can make unrepresentable, it does: translations stay a
// map[string]string all the way to the wire, so a null cannot be emitted.
package main

import (
	"context"
	"fmt"
	"log"
	"sort"
	"strings"

	"github.com/jroedel/schoenstatt-agent/internal/schoenstatt"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

const version = "0.1.0"

func main() {
	log.SetFlags(0)
	log.SetPrefix("schoenstatt-mcp: ")

	cfg, err := schoenstatt.LoadConfig()
	if err != nil {
		log.Fatal(err)
	}
	client := schoenstatt.NewClient(cfg)
	// Say which database this process will write to. Test is the default; if a
	// session is about to touch production, that should be visible in the log
	// rather than inferred from which variable was set.
	log.Printf("%s environment, %s", cfg.Env, cfg.BaseURL)

	server := mcp.NewServer(&mcp.Implementation{
		Name:    "schoenstatt-translations",
		Title:   "Schoenstatt translations",
		Version: version,
		Description: "Read and improve the translations schoenstatt.link renders. " +
			"An overwrite is recorded in the phrase's history and can be reverted, so send a " +
			"note saying why whenever you replace an existing translation. These tools cannot " +
			"remove one.",
	}, nil)

	registerTools(server, client)

	if err := server.Run(context.Background(), &mcp.StdioTransport{}); err != nil {
		log.Fatal(err)
	}
}

// --------------------------------------------------------------- languages

type languagesIn struct{}

type languagesOut struct {
	Languages []string `json:"languages"`
	Source    string   `json:"source"`
	MaxLength int      `json:"max_length"`
	Note      string   `json:"note"`
}

// ---------------------------------------------------------------- search

type searchIn struct {
	UntranslatedIn string `json:"untranslated_in,omitempty" jsonschema:"language code; return only phrases with no usable translation in it. This is the filter that finds work. An empty stored translation counts as untranslated, same as a missing one."`
	TranslatedIn   string `json:"translated_in,omitempty" jsonschema:"language code; return only phrases that already have a translation in it."`
	TextDomain     string `json:"text_domain,omitempty" jsonschema:"exact match on the phrase's text domain, e.g. Schoenstatt, Application, Books. Work one domain at a time so a batch stays reviewable."`
	OriginRoute    string `json:"origin_route,omitempty" jsonschema:"exact match on the route the phrase was first rendered on."`
	Search         string `json:"search,omitempty" jsonschema:"substring of the phrase's source string; % and _ are literal characters, not wildcards."`
	// OriginRouteLike is separate from Search rather than a flag on it because the
	// escaping differs and getting that backwards is silent: a caller expecting
	// literal % gets a wildcard match, or the reverse.
	OriginRouteLike string `json:"origin_route_like,omitempty" jsonschema:"like origin_route, but your % and _ ARE wildcards, e.g. associations/% for every association route. Unlike search, nothing is escaped for you."`
	OnlyRetired     bool   `json:"only_retired,omitempty" jsonschema:"return ONLY retired phrases — rows taken off the translator's worklist. Use this to audit retirements you made, and to notice one that came back. Retired rows are hidden from every other query."`
	IncludeRetired  bool   `json:"include_retired,omitempty" jsonschema:"return retired phrases alongside live ones. Rarely what you want: the point of retiring a row is to stop being asked to translate it."`
	Limit           int    `json:"limit,omitempty" jsonschema:"page size, default 100, maximum 500."`
	Offset          int    `json:"offset,omitempty" jsonschema:"page offset, for walking past the first page."`
}

type searchPhrase struct {
	PhraseID     int      `json:"phrase_id"`
	TextDomain   string   `json:"text_domain"`
	Phrase       string   `json:"phrase"`
	MissingIn    []string `json:"missing_in"`
	TranslatedIn []string `json:"translated_in"`
	ContextURL   string   `json:"context_url,omitempty"`
	OriginRoute  string   `json:"origin_route,omitempty"`
	// DuplicatePhraseIDs are other rows on this page holding the identical
	// source string. `trans_phrases` has no uniqueness constraint and some
	// routes have re-inserted the same string thousands of times, so a page of
	// results can be one phrase wearing twenty ids.
	DuplicatePhraseIDs []int `json:"duplicate_phrase_ids,omitempty"`
}

type searchOut struct {
	Phrases []searchPhrase `json:"phrases"`
	// Count is distinct source strings; RowsRead is rows the API returned
	// before identical strings were collapsed. They differ wherever the
	// database holds the same phrase more than once.
	Count    int    `json:"count"`
	RowsRead int    `json:"rows_read,omitempty"`
	Total    int    `json:"total,omitempty"`
	Note     string `json:"note,omitempty"`
}

// ---------------------------------------------------------------- get

type getIn struct {
	PhraseID int `json:"phrase_id" jsonschema:"the phrase id, from phrase_search."`
}

type translationView struct {
	Text       string `json:"text"`
	Present    bool   `json:"present"`
	ModifiedOn string `json:"modified_on,omitempty"`
}

type getOut struct {
	PhraseID     int                        `json:"phrase_id"`
	TextDomain   string                     `json:"text_domain"`
	Phrase       string                     `json:"phrase"`
	Translations map[string]translationView `json:"translations"`
	ContextURL   string                     `json:"context_url,omitempty"`
	OriginRoute  string                     `json:"origin_route,omitempty"`
	ETag         string                     `json:"etag"`
	Note         string                     `json:"note,omitempty"`
}

// ---------------------------------------------------------------- patch

type patchIn struct {
	PhraseID     int               `json:"phrase_id" jsonschema:"the phrase id to write."`
	Translations map[string]string `json:"translations" jsonschema:"language code to translation text, e.g. {\"it\": \"Santuario\"}. Every value must be non-empty. These tools cannot remove a translation: removal is the API's _retract key and is deliberately not exposed here."`
	Note         string            `json:"note,omitempty" jsonschema:"why you are replacing a translation. REQUIRED IN PRACTICE whenever this write overwrites an existing value: it is attached to the history row holding the text you destroyed, and it is the one thing the maintainers asked for in return for allowing overwrites at all. Read in order the notes are a conversation, so say what was wrong and what the evidence was — the next agent then learns that the obvious rendering was already tried instead of trying it again. Humans read them on the phrase edit screen too. Dropped by the server when the write only fills empty rows, so it is never noise and there is no reason to withhold it."`
	ETag         string            `json:"etag,omitempty" jsonschema:"the etag from phrase_get. Send it: it makes the write fail with 412 instead of silently overwriting a change made since you read. Omitting it is a blind write."`
}

type patchOut struct {
	PhraseID int      `json:"phrase_id"`
	Changed  []string `json:"changed"`
	Warning  string   `json:"warning,omitempty"`
	Note     string   `json:"note,omitempty"`
}

// ---------------------------------------------------------------- batch

type batchEntry struct {
	PhraseID     int               `json:"phrase_id" jsonschema:"the phrase id to write."`
	Translations map[string]string `json:"translations" jsonschema:"language code to translation text. Every value must be non-empty."`
	Note         string            `json:"note,omitempty" jsonschema:"why you are replacing a translation, per phrase. Send it on every entry that overwrites an existing value; the server attaches it to the history row holding the destroyed text and drops it when the write only fills gaps. One note per phrase, not one per batch: a batch is a set of independent writes and a shared justification would be a fiction."`
}

type batchIn struct {
	Phrases []batchEntry `json:"phrases" jsonschema:"the phrases to write, at most 200 per call."`
}

type batchOut struct {
	Applied  int                 `json:"applied"`
	Failed   int                 `json:"failed"`
	Received int                 `json:"received"`
	Failures []batchFailure      `json:"failures,omitempty"`
	Changed  map[string][]string `json:"changed,omitempty"`
	Warning  string              `json:"warning,omitempty"`
	Note     string              `json:"note,omitempty"`
}

type batchFailure struct {
	PhraseID string `json:"phrase_id"`
	Status   int    `json:"status,omitempty"`
	Message  string `json:"message,omitempty"`
}

// ---------------------------------------------------------------- wiring

func registerTools(s *mcp.Server, c *schoenstatt.Client) {
	mcp.AddTool(s, &mcp.Tool{
		Name:  "phrase_languages",
		Title: "List the writable languages",
		Description: "List the language codes this site writes translations for, read live from the " +
			"API's own schema. Call this once before your first write in a session if you are unsure " +
			"which codes are accepted — the list is site configuration and is not fixed, so never " +
			"assume it. Codes are simple language codes such as en, es, it. Note that en is a " +
			"translatable target like any other: a phrase's source string is usually English but " +
			"is not required to be, so an English translation can be genuinely missing.",
	}, func(ctx context.Context, _ *mcp.CallToolRequest, _ languagesIn) (*mcp.CallToolResult, languagesOut, error) {
		schema, languages, err := c.Schema(ctx)
		if err != nil {
			return nil, languagesOut{}, err
		}
		return nil, languagesOut{
			Languages: languages.PublicCodes(),
			Source:    "GET /api/v3/schema/phrase, read at request time from the site's merged configuration",
			MaxLength: schema.Writable.MaxLength,
			Note: "A phrase is its source string, which is usually English but not guaranteed to " +
				"be — phrases coming from the database can be in any language. Determine the " +
				"source language before translating. A translation is capped at the length above, " +
				"and cannot be removed once written.",
		}, nil
	})

	mcp.AddTool(s, &mcp.Tool{
		Name:  "phrase_search",
		Title: "Find phrases needing translation",
		Description: "Find phrases by language coverage, text domain, or source text. Call this first " +
			"in any translation task — it is how you get the phrase ids every other tool needs, and " +
			"the filters reach the database rather than being applied after paging, so " +
			"untranslated_in is a real query and not a scan. The usual opening move for filling a " +
			"gap is untranslated_in plus a text_domain. Returns each phrase's source string and " +
			"which languages it is missing in. The source string is usually English but is not " +
			"required to be, so read it before assuming what you are translating from.",
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchIn) (*mcp.CallToolResult, searchOut, error) {
		_, languages, err := c.Schema(ctx)
		if err != nil {
			return nil, searchOut{}, err
		}

		params := schoenstatt.SearchParams{
			TextDomain:      in.TextDomain,
			OriginRoute:     in.OriginRoute,
			OriginRouteLike: in.OriginRouteLike,
			Search:          in.Search,
			OnlyRetired:     in.OnlyRetired,
			IncludeRetired:  in.IncludeRetired,
			Limit:           in.Limit,
			Offset:          in.Offset,
		}
		if in.UntranslatedIn != "" {
			if params.UntranslatedIn, err = languages.API(in.UntranslatedIn); err != nil {
				return nil, searchOut{}, err
			}
		}
		if in.TranslatedIn != "" {
			if params.TranslatedIn, err = languages.API(in.TranslatedIn); err != nil {
				return nil, searchOut{}, err
			}
		}

		result, err := c.Search(ctx, params)
		if err != nil {
			return nil, searchOut{}, err
		}

		// Collapse rows holding the identical source string. `trans_phrases`
		// has no uniqueness constraint, and some routes have re-inserted the
		// same string thousands of times — a 20-row page of `blog/blog-post`
		// is two distinct phrases. Returning the rows as-is hands an agent a
		// batch that is one phrase twenty times over, and it would write
		// twenty identical translations without ever seeing the second string.
		out := searchOut{Total: result.Total}
		index := map[string]int{}
		for _, p := range result.Phrases {
			if at, seen := index[p.Phrase]; seen {
				existing := &out.Phrases[at]
				existing.DuplicatePhraseIDs = append(existing.DuplicatePhraseIDs, p.PhraseID)
				continue
			}
			view := searchPhrase{
				PhraseID:    p.PhraseID,
				TextDomain:  p.TextDomain,
				Phrase:      p.Phrase,
				OriginRoute: p.Context.OriginRoute,
			}
			if p.Context.URL != nil {
				view.ContextURL = *p.Context.URL
			}
			for apiCode, t := range p.Translations {
				public := languages.Public(apiCode)
				if t.Text == nil || strings.TrimSpace(*t.Text) == "" {
					view.MissingIn = append(view.MissingIn, public)
				} else {
					view.TranslatedIn = append(view.TranslatedIn, public)
				}
			}
			sort.Strings(view.MissingIn)
			sort.Strings(view.TranslatedIn)
			index[p.Phrase] = len(out.Phrases)
			out.Phrases = append(out.Phrases, view)
		}

		out.Count = len(out.Phrases)
		out.RowsRead = len(result.Phrases)
		if collapsed := out.RowsRead - out.Count; collapsed > 0 {
			out.Note = fmt.Sprintf(
				"%d of the %d rows read were duplicate source strings and have been collapsed; "+
					"duplicate_phrase_ids lists the rows sharing each string. They are separate "+
					"rows, so translating one does not translate the others — and paging further "+
					"will keep returning them. Prefer a narrower filter, and raise the duplication "+
					"itself rather than writing the same translation many times.",
				collapsed, out.RowsRead)
		}
		if out.Count == 0 {
			out.Note = "No phrases matched. If that is surprising, check the language code and " +
				"text domain against phrase_languages — an unknown filter value is refused, not ignored."
		}
		return nil, out, nil
	})

	mcp.AddTool(s, &mcp.Tool{
		Name:  "phrase_get",
		Title: "Read one phrase and its translations",
		Description: "Read one phrase: its source string, every language's current translation, when " +
			"each was last modified, and the etag needed to write safely. Call this before writing a " +
			"phrase whose existing translations matter — to see what is already there, to judge " +
			"whether an old translation has gone stale against an edited source, and to get the etag. " +
			"context_url, when present, is always the English page the phrase renders on; it is " +
			"null more often than not, because most routes take parameters that cannot be " +
			"reconstructed. If the source string is not itself English, that page shows the " +
			"English translation rather than the source — translate from the source string.",
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in getIn) (*mcp.CallToolResult, getOut, error) {
		_, languages, err := c.Schema(ctx)
		if err != nil {
			return nil, getOut{}, err
		}
		p, etag, err := c.Get(ctx, in.PhraseID)
		if err != nil {
			return nil, getOut{}, err
		}

		out := getOut{
			PhraseID:     p.PhraseID,
			TextDomain:   p.TextDomain,
			Phrase:       p.Phrase,
			Translations: map[string]translationView{},
			OriginRoute:  p.Context.OriginRoute,
			ETag:         etag,
		}
		// `phrase` is the source string, and nothing guarantees it is English.
		// Say so on every read: this is the assumption most likely to produce a
		// confident mistranslation, and it fails silently.
		note := "`phrase` is the source string — the key. It is usually English but is not " +
			"required to be; phrases coming from the database can be in any language. Read it " +
			"and determine its language before translating, rather than assuming."
		if p.Context.URL != nil {
			out.ContextURL = *p.Context.URL
			note += " context_url is always the English page: if the source is English you see " +
				"the key in situ, but if it is not, that page shows the English translation " +
				"rather than the source. Translate from `phrase`, not from the page."
		} else {
			note += " context_url is null: this phrase's route takes parameters, so there is no " +
				"single page to view it on."
		}
		out.Note = note
		for apiCode, t := range p.Translations {
			view := translationView{}
			if t.Text != nil {
				view.Text = *t.Text
				view.Present = strings.TrimSpace(*t.Text) != ""
			}
			if t.ModifiedOn != nil {
				view.ModifiedOn = *t.ModifiedOn
			}
			out.Translations[languages.Public(apiCode)] = view
		}
		return nil, out, nil
	})

	mcp.AddTool(s, &mcp.Tool{
		Name:  "phrase_patch",
		Title: "Write translations for one phrase",
		Description: "Write one or more languages for a single phrase. Use this for a handful of " +
			"writes or when you need the etag check; for more than a handful use phrase_batch_patch, " +
			"which recompiles the site's catalogs once instead of once per phrase. " +
			"A write that overwrites an existing translation IS recoverable, as of 2026-08-11: the " +
			"replaced text is kept in the phrase's history. That is not a reason to write loosely — " +
			"reverting needs somebody to notice, and a plausible mistranslation is exactly what nobody " +
			"notices — but it does mean correcting a translation you are reasonably certain is wrong no " +
			"longer needs to have been the assigned task. Send `note` whenever you overwrite. " +
			"Pass the etag from phrase_get so a concurrent change fails the write instead of " +
			"being silently overwritten.",
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in patchIn) (*mcp.CallToolResult, patchOut, error) {
		schema, languages, err := c.Schema(ctx)
		if err != nil {
			return nil, patchOut{}, err
		}
		body, err := resolveTranslations(in.Translations, languages, schema.Writable.MaxLength)
		if err != nil {
			return nil, patchOut{}, err
		}
		note, noteNote := resolveNote(in.Note, schema.NoteLimit())

		result, err := c.Patch(ctx, in.PhraseID, body, schema.NoteKey(), note, in.ETag)
		if err != nil {
			return nil, patchOut{}, err
		}

		out := patchOut{PhraseID: in.PhraseID, Warning: result.Warning}
		for _, apiCode := range result.Changed {
			out.Changed = append(out.Changed, languages.Public(apiCode))
		}
		sort.Strings(out.Changed)
		out.Note = strings.TrimSpace(describeWrite(len(out.Changed), result.Warning, in.ETag == "") + " " + noteNote)
		return nil, out, nil
	})

	mcp.AddTool(s, &mcp.Tool{
		Name:  "phrase_batch_patch",
		Title: "Write translations for many phrases",
		Description: "Write translations for up to 200 phrases in one call. Prefer this whenever you " +
			"have more than a handful of writes: the site's translation catalogs are recompiled once " +
			"at the end rather than once per phrase, which is several times faster. Each phrase " +
			"succeeds or fails on its own, so one bad entry does not stop the rest — read the " +
			"failures list. There is no etag check on a batch; if a specific phrase needs one, write " +
			"it with phrase_patch. Overwrites are recoverable from the phrase's history as of " +
			"2026-08-11, so send `note` on any entry that replaces an existing translation — a batch " +
			"is where an unexplained overwrite is hardest to reconstruct afterwards.",
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in batchIn) (*mcp.CallToolResult, batchOut, error) {
		schema, languages, err := c.Schema(ctx)
		if err != nil {
			return nil, batchOut{}, err
		}
		if len(in.Phrases) == 0 {
			return nil, batchOut{}, fmt.Errorf("no phrases given")
		}
		if len(in.Phrases) > schoenstatt.MaxBatchPhrases {
			return nil, batchOut{}, fmt.Errorf(
				"%d phrases exceeds the API's limit of %d per batch; split the work into "+
					"several calls so a batch cannot time out half written",
				len(in.Phrases), schoenstatt.MaxBatchPhrases)
		}

		payload := make(map[string]schoenstatt.BatchEntry, len(in.Phrases))
		trimmed := 0
		for _, entry := range in.Phrases {
			body, err := resolveTranslations(entry.Translations, languages, schema.Writable.MaxLength)
			if err != nil {
				return nil, batchOut{}, fmt.Errorf("phrase %d: %w", entry.PhraseID, err)
			}
			note, was := resolveNote(entry.Note, schema.NoteLimit())
			if was != "" {
				trimmed++
			}
			payload[fmt.Sprint(entry.PhraseID)] = schoenstatt.BatchEntry{Translations: body, Note: note}
		}

		result, err := c.BatchPatch(ctx, payload, schema.NoteKey())
		if err != nil {
			return nil, batchOut{}, err
		}

		out := batchOut{
			Applied:  result.Summary.Applied,
			Failed:   result.Summary.Failed,
			Received: result.Summary.Received,
			Warning:  result.Warning,
			Changed:  map[string][]string{},
		}
		for id, outcome := range result.Results {
			if outcome.OK {
				var changed []string
				for _, apiCode := range outcome.Changed {
					changed = append(changed, languages.Public(apiCode))
				}
				sort.Strings(changed)
				if len(changed) > 0 {
					out.Changed[id] = changed
				}
				continue
			}
			out.Failures = append(out.Failures, batchFailure{
				PhraseID: id, Status: outcome.Status, Message: outcome.Message,
			})
		}
		sort.Slice(out.Failures, func(i, j int) bool { return out.Failures[i].PhraseID < out.Failures[j].PhraseID })
		out.Note = describeWrite(out.Applied, result.Warning, false)
		if trimmed > 0 {
			out.Note += fmt.Sprintf(" %d note(s) were longer than the %d characters the site "+
				"stores and were trimmed, as the site itself would have done.", trimmed, schema.NoteLimit())
		}
		return nil, out, nil
	})

	mcp.AddTool(s, &mcp.Tool{
		Name:  "phrase_retire",
		Title: "Take a phrase off the translator's worklist",
		Description: "Retire a phrase that should not be on the worklist at all — one added by a " +
			"defect at the caller, not one that is merely untranslated. A retirement DESTROYS " +
			"NOTHING: every translation stays, the site renders exactly what it rendered before, and " +
			"the only change is that nobody is asked to translate it. It is also self-healing — a " +
			"phrase the site still renders un-retires itself on the next missed lookup — so a wrong " +
			"retirement corrects itself, which is a stronger guarantee than a wrong translation has. " +
			"That is why the bar here is lower than for correcting a translation. " +
			"`note` is REQUIRED and is the entire record of the judgement. " +
			"This is NOT the way to remove a translation: that is the API's _retract, which these " +
			"tools do not expose, and retracting every language would destroy five translations and " +
			"leave the phrase on the worklist with more gaps than before. " +
			"A row that is merely untranslated is work, not a mistake — do not retire the backlog.",
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in retireIn) (*mcp.CallToolResult, retireOut, error) {
		schema, _, err := c.Schema(ctx)
		if err != nil {
			return nil, retireOut{}, err
		}
		result, remark, err := c.Retire(ctx, in.PhraseID, schema.NoteKey(), in.Note, schema.NoteLimit())
		if err != nil {
			return nil, retireOut{}, err
		}
		return nil, retirementResult(in.PhraseID, true, result, remark), nil
	})

	mcp.AddTool(s, &mcp.Tool{
		Name:  "phrase_unretire",
		Title: "Put a retired phrase back on the worklist",
		Description: "Reverse a retirement you judge was wrong, with a reason. " +
			"Read this before using it: a phrase the site still renders comes back BY ITSELF on the " +
			"next missed lookup, and that path writes no history. So the absence of an un-retire " +
			"entry is informative — a phrase that is live again with a retirement and no un-retire " +
			"after it came back on its own, which tells the next reader the retirement was wrong. " +
			"Calling this tool writes an entry saying a human decided to put it back. Do not use it " +
			"to tidy up a note or to re-do a retirement: that replaces a true signal with a false " +
			"account of a judgement. Use it when the retirement itself was the mistake.",
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in retireIn) (*mcp.CallToolResult, retireOut, error) {
		schema, _, err := c.Schema(ctx)
		if err != nil {
			return nil, retireOut{}, err
		}
		result, remark, err := c.Unretire(ctx, in.PhraseID, schema.NoteKey(), in.Note, schema.NoteLimit())
		if err != nil {
			return nil, retireOut{}, err
		}
		return nil, retirementResult(in.PhraseID, false, result, remark), nil
	})
}

// retirementResult shapes the answer to a retire or un-retire, and explains the
// idempotent case rather than letting `changed: false` read as a failure.
func retirementResult(phraseID int, retiring bool, r *schoenstatt.RetireResult, remark string) retireOut {
	out := retireOut{
		PhraseID: phraseID,
		Retired:  retiring,
		Changed:  r.Changed,
		Warning:  r.Warning,
	}
	if r.Phrase != nil {
		out.Phrase = r.Phrase.Phrase
		if r.Phrase.Meta.RetiredOn != nil {
			out.RetiredOn = *r.Phrase.Meta.RetiredOn
		}
	}
	var notes []string
	if !r.Changed {
		state := "already retired"
		if !retiring {
			state = "already on the worklist"
		}
		notes = append(notes, "Nothing changed: the phrase was "+state+
			". No second history entry was written, so a retry cannot forge a second judgement.")
	} else if retiring {
		notes = append(notes, "The phrase is off the worklist. Nothing was destroyed — its "+
			"translations are intact and the site renders what it rendered before. If it "+
			"reappears in an untranslated query later, the retirement was wrong and your note "+
			"is what says what was believed.")
	}
	if remark != "" {
		notes = append(notes, remark)
	}
	if r.Warning != "" {
		notes = append(notes, "The row was committed but the compiled catalogs could not be "+
			"written; somebody has to fix the filesystem. Retrying writes nothing.")
	}
	out.Note = strings.Join(notes, " ")
	return out
}

// ---------------------------------------------------------------- retire

type retireIn struct {
	PhraseID int    `json:"phrase_id" jsonschema:"the phrase id to take off the worklist."`
	Note     string `json:"note" jsonschema:"REQUIRED: why this phrase should not be on the worklist. Say what the row actually is, and what it means if it comes back — that is the question this note is read to answer. A retirement destroys nothing, so this note is the entire record of the judgement."`
}

type retireOut struct {
	PhraseID  int    `json:"phrase_id"`
	Retired   bool   `json:"retired"`
	Changed   bool   `json:"changed"`
	Phrase    string `json:"phrase,omitempty"`
	RetiredOn string `json:"retired_on,omitempty"`
	Warning   string `json:"warning,omitempty"`
	Note      string `json:"note,omitempty"`
}

// resolveNote prepares the reason for a write, returning the note to send and a
// remark for the agent if anything was done to it.
//
// It TRIMS rather than refuses, which is the opposite of how this server handles
// an over-long translation, and the asymmetry is the API's own and is right:
// losing the tail of a justification is a smaller harm than refusing the
// translation it justifies. Doing it here rather than leaving it to the server
// means the agent is told, instead of believing all 400 characters of its
// reasoning were recorded.
func resolveNote(note string, limit int) (string, string) {
	note = strings.TrimSpace(note)
	if note == "" || limit <= 0 {
		return note, ""
	}
	if runes := []rune(note); len(runes) > limit {
		return strings.TrimSpace(string(runes[:limit])), fmt.Sprintf(
			"The note was %d characters and the site stores %d, so it was trimmed — the tail "+
				"of your reasoning is not in the history. Say the essential thing first.",
			len(runes), limit)
	}
	return note, ""
}

// resolveTranslations maps public language codes to the API's codes and
// enforces the two rules an agent is most likely to get wrong.
func resolveTranslations(in map[string]string, languages *schoenstatt.LanguageMap, maxLength int) (map[string]string, error) {
	if len(in) == 0 {
		return nil, fmt.Errorf("no translations given; name at least one language, e.g. {\"it\": \"…\"}")
	}
	out := make(map[string]string, len(in))
	for code, text := range in {
		apiCode, err := languages.API(code)
		if err != nil {
			return nil, err
		}
		if strings.TrimSpace(text) == "" {
			// The API skips an empty value, so it is silently a no-op rather
			// than the deletion it looks like. Refusing here is the difference
			// between "nothing happened" and knowing why.
			return nil, fmt.Errorf(
				"the translation for %q is empty. An empty value does not blank a translation — "+
					"it means \"leave this language alone\" and is skipped. Removal is the API's "+
					"_retract key, which these tools deliberately do not expose. Send text, or "+
					"leave the language out of the call entirely", code)
		}
		if maxLength > 0 && len([]rune(text)) > maxLength {
			return nil, fmt.Errorf("the translation for %q is %d characters; the column holds %d",
				code, len([]rune(text)), maxLength)
		}
		out[apiCode] = text
	}
	return out, nil
}

func describeWrite(changed int, warning string, blind bool) string {
	var notes []string
	if changed == 0 {
		notes = append(notes, "Nothing changed: the text sent was already stored. No write happened, "+
			"which is why a polling agent does not fill the change log with noise.")
	}
	if warning != "" {
		notes = append(notes, "The rows were committed but the compiled catalogs could not be written, "+
			"so the site keeps showing the old text. This is not a failure to retry — retrying writes "+
			"nothing. Somebody has to fix the filesystem.")
	}
	if blind && changed > 0 {
		notes = append(notes, "This was a blind write: no etag was sent, so a change made since you "+
			"last read the phrase would have been overwritten without warning.")
	}
	return strings.Join(notes, " ")
}
