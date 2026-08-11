package schoenstatt

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// CredentialsPath is where tokens live: outside any repository, mode 600, in a
// directory that is mode 700. Nothing tracked by git ever holds a token, and no
// tool here accepts one as a command-line argument — arguments are visible in
// `ps` and land in shell history.
const CredentialsPath = "~/.config/schoenstatt/credentials.env"

// Config is what the server needs to reach the API.
type Config struct {
	BaseURL string
	Token   string
	// Env is "test" or "production", for anything that wants to say which
	// database it is about to write to.
	Env string
}

// LoadConfig reads the environment first and falls back to the credentials
// file, so the server works both when an MCP client passes an env block and
// when it is launched with nothing set.
//
// **Test is the default, and production is opt-in.** The credentials file holds
// both, one variable apart, and the difference between them is the difference
// between a disposable capsule and the live site. Translations have no
// revision history, so a write aimed at the wrong one cannot be taken back —
// which makes "which environment am I pointed at" the wrong question to answer
// by whichever variable happens to be set. Set SCHOENSTATT_ENV=production, in
// full, to reach production.
func LoadConfig() (Config, error) {
	file, err := readEnvFile(expandHome(CredentialsPath))
	if err != nil {
		return Config{}, err
	}

	pick := func(key string) string {
		if v := strings.TrimSpace(os.Getenv(key)); v != "" {
			return v
		}
		return file[key]
	}

	env := strings.ToLower(strings.TrimSpace(pick("SCHOENSTATT_ENV")))
	switch env {
	case "", "test", "capsule", "local":
		env = "test"
	case "production", "prod", "live":
		env = "production"
	default:
		return Config{}, fmt.Errorf(
			"SCHOENSTATT_ENV is %q; it must be \"test\" (the default, the local capsule) "+
				"or \"production\"", env)
	}

	suffix := "_TEST"
	if env == "production" {
		suffix = ""
	}

	cfg := Config{
		Env:     env,
		BaseURL: strings.TrimRight(pick("SCHOENSTATT_BASE_URL"+suffix), "/"),
		Token:   pick("SCHOENSTATT_TRANSLATOR_JWT" + suffix),
	}
	if cfg.BaseURL == "" {
		return Config{}, fmt.Errorf(
			"no SCHOENSTATT_BASE_URL%s for the %s environment: set it in the environment "+
				"or in %s (the capsule is http://localhost:8080)", suffix, env, CredentialsPath)
	}
	if cfg.Token == "" {
		return Config{}, fmt.Errorf(
			"no SCHOENSTATT_TRANSLATOR_JWT%s for the %s environment: issue a token for an "+
				"account holding sch_api_translator and put it in %s (it is shown once)",
			suffix, env, CredentialsPath)
	}
	return cfg, nil
}

// readEnvFile parses KEY=value lines. A missing file is not an error — the
// environment may carry everything.
func readEnvFile(path string) (map[string]string, error) {
	f, err := os.Open(path)
	if err != nil {
		if os.IsNotExist(err) {
			return map[string]string{}, nil
		}
		return nil, fmt.Errorf("reading %s: %w", path, err)
	}
	defer f.Close()

	out := map[string]string{}
	scan := bufio.NewScanner(f)
	for scan.Scan() {
		line := strings.TrimSpace(scan.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		key, value, ok := strings.Cut(line, "=")
		if !ok {
			continue
		}
		value = strings.TrimSpace(value)
		value = strings.Trim(value, `"'`)
		out[strings.TrimSpace(key)] = value
	}
	return out, scan.Err()
}

func expandHome(path string) string {
	if !strings.HasPrefix(path, "~/") {
		return path
	}
	home, err := os.UserHomeDir()
	if err != nil {
		return path
	}
	return filepath.Join(home, path[2:])
}
