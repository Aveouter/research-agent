# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is the `~/.openclaw` configuration directory for an OpenClaw AI agent gateway. It tracks non-sensitive configuration files in git, synced to `git@github.com:ACautomata/research-agent.git`.

All changes are made via SSH to the remote server. Local clone is at `/Users/junran/Documents/research-agent/`.

## Architecture

This repo follows OpenClaw's hub-and-spoke multi-agent pattern. The main agent (颖姗) is bound to messaging channels and delegates specialized tasks to sub-agents via `sessions_spawn`.

- **openclaw.json** — Main gateway configuration. All secrets use `${ENV_VAR}` references resolved from `.env` (which is gitignored).
- **agents/main/agent/models.json** — Custom model provider definitions (currently MiniMax Anthropic-compatible endpoints).
- **canvas/index.html** — OpenClaw Canvas web UI.
- **workspace/** — Main agent (颖姗) working directory. Contains SOUL.md, AGENTS.md, IDENTITY.md, USER.md, TOOLS.md, MEMORY.md, HEARTBEAT.md, DREAMS.md. See [docs](https://docs.openclaw.ai/concepts/agent-workspace).
- **workspace-autoresearch/** — Sub-agent workspace for the Autoresearch agent. Mirrors the main workspace structure with SOUL.md, AGENTS.md, IDENTITY.md, USER.md, TOOLS.md, MEMORY.md, HEARTBEAT.md, DREAMS.md. This agent is spawned by 颖姗 for paper ingest, literature queries, cross-paper comparison, and wiki quality auditing.
- **workspace-paper-review/** — Agent workspace for paper review and validation experiment design. Contains SOUL.md, AGENTS.md, USER.md, memory/, and skills/ for the 5-stage paper analysis pipeline.
- **benchmarks/** — Developer benchmarks and evaluation datasets for testing agent capabilities.

## Key Configuration Details

- **Gateway**: loopback-bound on port 18789, token auth via `${GATEWAY_TOKEN}`.
- **Model**: Primary `minimax/MiniMax-M2.7`, fallback `minimax/MiniMax-M2.7-highspeed`. Provider auth uses `minimax-oauth` (handled by the minimax plugin).
- **Channels**: Feishu configured with WebSocket mode, pairing DM policy, allowlist group policy. Requires `${FEISHU_APP_ID}` and `${FEISHU_APP_SECRET}` in `.env`.
- **Memory**: QMD backend indexing `**/*.md` in workspace.
- **TTS**: Edge TTS with `zh-CN-XiaoxiaoNeural`.
- **Browser**: Headless Chromium at `/usr/bin/chromium`, no sandbox.
- **Session**: `dmScope: "per-peer"` — each user gets an independent DM session context.

### Gotchas

- Feishu channel: `streaming` must be boolean, not string. No `tools` property at channel level.
- Config validation errors appear in gateway logs on startup.
- `plugins.installs.*.installPath` is the resolved install directory; keep managed installs as absolute paths.
- QMD `paths[].path` entries resolve relative to the agent workspace directory; use `.` for the workspace root.
- External tools (Context7, WebReader) have weekly rate limits — use Playwright to read docs.openclaw.ai as fallback.
- `.env` uses `export VAR="value"` format (shell export syntax).

## Operations

```bash
# Restart gateway after config changes
openclaw gateway restart

# Verify config after restart
openclaw logs --tail 15

# View live logs
openclaw logs --follow

# Check version
openclaw --version

# Feishu pairing management
openclaw pairing list feishu
openclaw pairing approve feishu <CODE>
```

## Architectural Rules

### Workspace Naming

Workspace directories follow the OpenClaw convention `workspace-<agentId>`:

- **Main agent**: `workspace/` (no suffix — the default agent)
- **Sub-agents**: `workspace-<agentId>/` where `<agentId>` matches the `id` field in `openclaw.json` → `agents.list[]`

Examples: `workspace-autoresearch/`, `workspace-paper-review/`.

When adding a new agent, create the workspace directory, register it in `openclaw.json` under `agents.list` with a matching `workspace` path, and add the workspace to `.gitignore`'s runtime-state exceptions.

### Agent Design Pattern

The system uses a **main agent → main agent skills → subagent → subagent skills** delegation chain:

1. **Main agent (颖姗)** — bound to messaging channels, handles user-facing conversation, routing, and orchestration.
2. **Main agent skills** — live at `skills/<skill-name>/` (project root). These compose subagent capabilities into user-facing workflows (e.g. `idea-generate` orchestrates paper context extraction, idea scoring, and output formatting).
3. **Subagents** — each registered in `openclaw.json` under `agents.list`, spawned by the main agent via `sessions_spawn`. Each subagent owns a **single domain of responsibility**:
   - `autoresearch` — paper ingest, wiki maintenance, literature queries, cross-paper comparison.
   - `paper-review` — paper analysis pipeline (wiki entry → experiment extraction → review → validation design → codex prompt).
4. **Subagent skills** — live at `workspace-<agentId>/skills/<skill-name>/`. These handle domain-specific subtasks within the subagent's responsibility scope.

**Constraints:**

- **Single minimal function per subagent.** Each subagent implements exactly one atomic capability. If a subagent grows to handle multiple distinct functions, split it. The litmus test: can you describe what the subagent does in a single verb phrase? If not, it's too broad.
- Main agent skills orchestrate subagents. They should not reimplement logic that belongs in a subagent skill.
- Subagent skills should be self-contained and produce outputs that downstream stages or other agents can consume.
- The `agents.defaults.subagents.allowAgents` list in `openclaw.json` controls which subagents the main agent may spawn. Update it when adding new subagents.
- Main agent's AGENTS.md and TOOLS.md define how subagents are invoked. Keep orchestration logic in main agent skills (`skills/<skill-name>/`), not scattered across workspace files.

### Adding New Agents

When creating a new subagent:

1. Add an entry to `agents.list` in `openclaw.json` with `id`, `name`, and `workspace` path.
2. Create `workspace-<agentId>/` with standard workspace files (SOUL.md, AGENTS.md, USER.md, TOOLS.md, MEMORY.md, HEARTBEAT.md, DREAMS.md).
3. Add the agent ID to `agents.defaults.subagents.allowAgents`.
4. Write skills under `workspace-<agentId>/skills/` following the single-responsibility principle.
5. If the main agent needs to orchestrate this subagent, create or update a main agent skill under `skills/`.

## Gitignore Strategy

`.env` and `auth-profiles.json` contain secrets — never track them. Runtime data (`logs/`, `tasks/`, `*.sqlite`), QMD caches (`qmd/`, `agents/*/qmd/`), CLI-managed dirs (`extensions/`), and channel data (`qqbot/`) are excluded. Agent workspaces and their checked-in skills are tracked, while runtime state inside those workspaces is ignored. `openclaw.json` is tracked because all tokens are env var references.
