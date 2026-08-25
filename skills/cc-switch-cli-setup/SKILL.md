---
name: cc-switch-cli-setup
description: >-
  Install and configure CLI coding agents (Codex, Claude Code, and future Grok Build)
  via SaladDay/cc-switch-cli providers, API keys, base URLs, models, and local proxy.
  Use when the user asks to install/configure cc-switch, Codex, Claude Code, Claude CLI,
  Grok Build, or to wire a third-party relay (WinToken / OpenAI-compatible / Anthropic-compatible)
  into these agents.
---

# CC-Switch CLI Agent Setup

Use **cc-switch** as the single control plane for provider configs across Codex / Claude Code / (future) Grok Build.

## Hard rules

1. **Install tooling first, then ask for secrets.** Never invent API keys, base URLs, or model names.
2. After installs succeed, **stop and ask the user** for all of:
   - target app(s): `codex` / `claude` / `grokbuild` (if supported)
   - API key
   - base URL (e.g. `https://example.com` or `https://example.com/v1`)
   - model id (e.g. `grok-4.6`)
   - optional provider display name / id
3. Prefer **non-interactive** `cc-switch` commands. For deletes that need TTY confirm, use `script -q -c "..." /dev/null <<<'y'`.
4. Do not print full API keys in chat after the user provides them; redact to last 4 chars in summaries.
5. Before claiming Grok Build support, verify `cc-switch --help` / README `Supported apps`. If unsupported, say so and skip.

## Workflow checklist

```
Progress:
- [ ] 1. Ensure cc-switch installed
- [ ] 2. Ensure target CLI(s) installed
- [ ] 3. ASK user: apps + api_key + base_url + model
- [ ] 4. Normalize URL + probe API format
- [ ] 5. Add/switch provider via cc-switch
- [ ] 6. Claude OpenAI-compat → enable local proxy + onboarding fix
- [ ] 7. Smoke-test and summarize
```

### 1. Ensure cc-switch

```bash
which cc-switch && cc-switch --version
cc-switch env tools
```

If missing, install (Linux/macOS):

```bash
curl -fsSL https://github.com/SaladDay/cc-switch-cli/releases/latest/download/install.sh | bash
# binary → ~/.local/bin/cc-switch ; ensure PATH includes ~/.local/bin
```

Fallback: GitHub release tarball / `cargo build --release` in `src-tauri`. Details: [reference.md](reference.md).

### 2. Ensure target CLI(s)

Only install what the user asked for.

| App | Binary | Preferred install |
|-----|--------|-------------------|
| Codex | `codex` | Official Codex install the user already uses, or their usual method |
| Claude Code | `claude` | Native installer `curl -fsSL https://claude.ai/install.sh \| bash` → `~/.local/bin/claude` |
| Grok Build | (check current docs) | Only if cc-switch lists it as a supported `--app` |

**Claude install fallbacks when `claude.ai` is unreachable:**

1. GitHub release asset `claude-linux-x64.tar.gz` from `anthropics/claude-code`
2. Existing local binary (e.g. bundled under a conda/sdk path) → install to `~/.local/share/claude/versions/<ver>` and symlink `~/.local/bin/claude`

Verify:

```bash
cc-switch env tools
codex --version   # if configuring Codex
claude --version  # if configuring Claude
```

### 3. Ask the user (mandatory gate)

After installs are OK, ask clearly (do not proceed without answers):

```text
请提供以下配置信息：
1. 要配置的应用：codex / claude / 两者（或 grokbuild，若已支持）
2. API Key
3. Base URL（可带或不带 /v1）
4. 模型名（例如 grok-4.6）
5. （可选）供应商显示名 / ID
```

If the user already pasted these in the same message, reuse them; still confirm the target app list.

### 4. Normalize URL + probe format

Normalize base URL:

- Prefer a base that works with OpenAI-style paths: `https://host/v1`
- If user gave `https://host`, probe both `https://host/v1/...` and `https://host/...`
- Never use a URL that returns HTML marketing pages for API calls

Probe (redact key in logs):

```bash
# OpenAI chat
curl -sS -o /tmp/probe_chat.json -w '%{http_code}' \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}],\"max_tokens\":8}" \
  "$BASE/chat/completions"

# OpenAI responses
curl -sS -o /tmp/probe_resp.json -w '%{http_code}' \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d "{\"model\":\"$MODEL\",\"input\":\"ping\",\"max_output_tokens\":8}" \
  "$BASE/responses"

# Anthropic messages
curl -sS -o /tmp/probe_msg.json -w '%{http_code}' \
  -H "x-api-key: $KEY" -H "Authorization: Bearer $KEY" \
  -H "anthropic-version: 2023-06-01" -H "Content-Type: application/json" \
  -d "{\"model\":\"$MODEL\",\"max_tokens\":8,\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}]}" \
  "$BASE/messages"
```

Choose format:

| Probe result | Codex `--api-format` | Claude `--api-format` |
|--------------|----------------------|------------------------|
| `/responses` 200 | `responses` | `openai_responses` (needs proxy) |
| `/chat/completions` 200 | `chat` | `openai_chat` (needs proxy) |
| `/messages` 200 | `anthropic` | `anthropic` (direct or proxy per cc-switch) |
| Anthropic fails, OpenAI works | use OpenAI row | **must** enable Claude local proxy |

### 5. Add / switch provider

Common pattern:

```bash
APP=codex   # or claude
ID=wintoken-grok
NAME="WinToken Grok"

cc-switch --app "$APP" provider add \
  --name "$NAME" \
  --id "$ID" \
  --base-url "$BASE" \
  --api-key "$KEY" \
  --model "$MODEL" \
  --api-format "$FORMAT" \
  --notes "relay $BASE model $MODEL"

# Claude role models: map all roles to the same custom model when only one model exists
#   --haiku-model --sonnet-model --opus-model --subagent-model "$MODEL"
#   --api-key-field api-key   # when using ANTHROPIC_API_KEY style

cc-switch --app "$APP" provider switch "$ID"
cc-switch --app "$APP" provider current
```

If ID exists: switch away → delete (TTY confirm) → re-add.

```bash
cc-switch --app "$APP" provider switch default        # or claude-official
script -q -c "cc-switch --app $APP provider delete $ID" /dev/null <<<'y'
```

### 6. Claude OpenAI-compatible extras

When Claude format is `openai_chat` / `openai_responses`:

1. **Enable local proxy** (translates Anthropic `/v1/messages` → upstream OpenAI):

```bash
cc-switch --app claude proxy enable
cc-switch --app claude proxy show
```

Live settings should look like:

- `ANTHROPIC_BASE_URL=http://127.0.0.1:15721`
- `ANTHROPIC_API_KEY` / `ANTHROPIC_AUTH_TOKEN=PROXY_MANAGED`
- role `*_MODEL_NAME` → user model (e.g. `grok-4.6`)

2. **Skip first-run official onboarding** (avoids `api.anthropic.com` errors):

```bash
# ~/.claude.json
hasCompletedOnboarding = true

# ~/.claude/settings.json env
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC = "1"
```

3. **Critical ordering:** switch provider with the **real key written to live settings**, then `proxy enable`. If proxy was enabled while the key was already `proxy-placeholder` / `PROXY_MANAGED`, the live backup stores a bad key → upstream `Invalid token`. Fix by: `proxy disable` → recreate/switch provider (real key) → `proxy enable` again.

4. Keep proxy running while using Claude:

```bash
cc-switch --app claude proxy enable
```

### 7. Smoke-test + user summary

**Codex**

```bash
# live config
rg -n 'model|base_url|wire_api' ~/.codex/config.toml
# optional: short non-interactive prompt if available
```

Expect: `model = "<user model>"`, `base_url` with working `/v1`, `wire_api` matching probe.

**Claude**

```bash
curl -sS --max-time 30 \
  -X POST 'http://127.0.0.1:15721/v1/messages' \
  -H 'x-api-key: PROXY_MANAGED' \
  -H 'anthropic-version: 2023-06-01' \
  -H 'Content-Type: application/json' \
  -d "{\"model\":\"claude-sonnet-4-6\",\"max_tokens\":16,\"messages\":[{\"role\":\"user\",\"content\":\"say ok\"}]}"

timeout 60 claude -p 'reply with exactly: ok' --output-format text
```

Tell the user:

- which apps configured + provider id
- base URL used (with `/v1` if normalized)
- model
- Claude proxy port if enabled
- known caveats (below)
- how to start: `codex` / `claude`

## Known caveats (tell the user briefly)

1. **Codex “Model metadata not found”** for custom models: warning only; still works. Optional fix: `model_catalog_json` — see [reference.md](reference.md).
2. **Model self-identifies as GPT-x**: Codex injects “based on GPT-5” system instructions. Trust status bar / billing model id, not the chat persona.
3. **Grok Build**: not in SaladDay/cc-switch-cli supported apps as of the skill’s last verified set (`claude`, `codex`, `gemini`, `opencode`, `hermes`, `openclaw`). Re-check before implementing; track upstream desktop `farion1231/cc-switch` for parity.
4. **`/usr/bin/cc`** on Linux is often the C compiler, not Claude Code. Claude binary must be `claude` on `PATH`.

## Security

- Prefer receiving the key in chat only for one-shot local config; remind the user to rotate if the key was exposed.
- Never commit keys, `~/.codex/auth.json`, or `~/.claude/settings.json` secrets into the repo.

## Additional resources

- Install fallbacks, proxy troubleshooting, model catalog: [reference.md](reference.md)
