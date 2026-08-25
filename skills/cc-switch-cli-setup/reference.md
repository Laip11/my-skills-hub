# CC-Switch CLI Setup — Reference

## Supported apps (verify live)

```bash
cc-switch --help
# or README “Supported apps”
```

Historically on SaladDay/cc-switch-cli:

- Supported: `claude`, `codex`, `gemini`, `opencode`, `hermes`, `openclaw`
- Not supported (yet): Grok Build / `grokbuild` — open feature requests may exist; desktop upstream may already support it

When adding a new app later, mirror the same gate: install binary → ask key/url/model → probe → `provider add/switch` → app-specific live sync / proxy.

## Install details

### cc-switch

```bash
curl -fsSL https://github.com/SaladDay/cc-switch-cli/releases/latest/download/install.sh | bash
# override dir: CC_SWITCH_INSTALL_DIR=...
# Linux musl default; glibc: CC_SWITCH_LINUX_LIBC=glibc
```

Manual: download `cc-switch-cli-linux-x64-musl.tar.gz` (or darwin/windows asset), put `cc-switch` on `PATH`.

From source:

```bash
git clone https://github.com/SaladDay/cc-switch-cli.git
cd cc-switch-cli/src-tauri && cargo build --release
# → target/release/cc-switch
```

Config root: `~/.cc-switch/` (override `CC_SWITCH_CONFIG_DIR`).

### Claude Code

Preferred:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

If installer host times out:

```bash
# GitHub release (version pin as needed)
VER=2.1.245
curl -fL -o /tmp/claude.tgz \
  "https://github.com/anthropics/claude-code/releases/download/v${VER}/claude-linux-x64.tar.gz"
mkdir -p ~/.local/share/claude/versions ~/.local/bin
tar -xzf /tmp/claude.tgz -C /tmp/claude-extract
install -m 755 /tmp/claude-extract/claude ~/.local/share/claude/versions/$VER
ln -sfn ~/.local/share/claude/versions/$VER ~/.local/bin/claude
```

Or copy a known-good local ELF to the same versioned path + symlink.

Ensure `~/.local/bin` is on `PATH`.

### Codex

Use the user’s existing Codex install. Confirm with `codex --version` and `cc-switch env tools`.

## Provider add flags (cheat sheet)

```bash
cc-switch --app <claude|codex|...> provider add --help
```

Useful flags:

| Flag | Purpose |
|------|---------|
| `--name` / `--id` | Display name / stable id |
| `--base-url` | API root (include `/v1` when required) |
| `--api-key` | Secret |
| `--model` | Default model |
| `--api-format` | Claude: `anthropic\|openai_chat\|openai_responses\|gemini_native`; Codex: `responses\|chat\|anthropic` |
| `--api-key-field` | Claude: `auth-token` (default) or `api-key` |
| `--haiku-model` / `--sonnet-model` / `--opus-model` / `--subagent-model` | Claude role mapping |
| `--notes` | Free text |

List / switch / inspect:

```bash
cc-switch --app claude provider list
cc-switch --app claude provider current
cc-switch --app claude provider switch <id>
```

## Claude proxy deep dive

### Why

Claude Code speaks Anthropic Messages. Many relays only expose OpenAI Chat/Responses. cc-switch local proxy adapts:

- Client → `http://127.0.0.1:15721/v1/messages`
- Proxy → upstream `.../v1/chat/completions` or `.../v1/responses` with real key

### Healthy state

```bash
cc-switch --app claude proxy show
# Running: yes ; Claude route enabled ; port 15721
```

`~/.claude/settings.json` env (conceptual):

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:15721",
    "ANTHROPIC_API_KEY": "PROXY_MANAGED",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-4-6",
    "ANTHROPIC_DEFAULT_SONNET_MODEL_NAME": "<user-model>",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }
}
```

Proxy remaps official Claude role model ids → `*_MODEL_NAME`.

### Broken: Invalid token via proxy

Cause: `proxy_live_backup` captured a placeholder instead of the real key.

Fix:

```bash
cc-switch --app claude proxy disable
cc-switch --app claude provider switch <id>   # rewrites live settings with real key
# confirm settings.json shows real sk-… BEFORE enable
cc-switch --app claude proxy enable
```

Or delete + re-add provider, then enable proxy only after live key is real.

### Broken: Unable to connect to api.anthropic.com

Cause: first-run onboarding / nonessential traffic to Anthropic.

Fix:

```bash
# ~/.claude.json
{ "hasCompletedOnboarding": true, ... }

# settings env
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
```

Then ensure proxy is up and `ANTHROPIC_BASE_URL` points at `127.0.0.1:15721`.

### Port busy

```bash
cc-switch proxy show
lsof -nP -iTCP:15721 -sTCP:LISTEN
cc-switch daemon stop
# kill only clear cc-switch proxy/daemon PIDs if needed
```

## Codex custom model metadata (optional)

Warning:

`Model metadata for <model> not found. Defaulting to fallback metadata`

Optional mitigation — `~/.codex/config.toml`:

```toml
model_catalog_json = "/home/<user>/.codex/model_catalog.json"
```

`model_catalog.json` must include a `models[]` entry whose `slug` **exactly** matches `model`. Use protocol-valid enums (`visibility`, `shell_type`, `truncation_policy.mode`, …). Catalog may replace rather than merge bundled models — include needed entries.

## Expected live files

| App | Files |
|-----|--------|
| cc-switch | `~/.cc-switch/cc-switch.db`, `settings.json` |
| Codex | `~/.codex/config.toml`, `~/.codex/auth.json` |
| Claude | `~/.claude/settings.json`, `~/.claude.json` |

## Quick verification matrix

| Check | Command / expectation |
|-------|------------------------|
| Tools present | `cc-switch env tools` → Claude/Codex ok |
| Provider current | `cc-switch --app <app> provider current` |
| Upstream OpenAI | `curl` chat/responses 200 with user model |
| Claude proxy | POST `127.0.0.1:15721/v1/messages` → 200, `model` = user model |
| Claude CLI | `claude -p 'reply with exactly: ok' --output-format text` → `ok` |
| Codex live | `config.toml` model + base_url correct |

## Future: Grok Build

When cc-switch-cli gains support:

1. Confirm `--app` label and live config path (`~/.grok/config.toml` is common upstream).
2. Extend this skill’s app table and probe matrix.
3. Reuse the same ask-gate: key / url / model after install.
4. Until then, refuse silent fake configuration; point users at desktop cc-switch or wait for CLI issue parity.
