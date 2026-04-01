# multi-agent-collab-skill

A two-skill system for coordinating multiple AI coding agents (Claude Code, Gemini CLI, Cursor, Codex, etc.) on a shared codebase. Agents work in parallel without stepping on each other — scope is enforced at the git layer, communication happens through append-only files, and deadlocks are caught before they spiral.

## Skills

### `collab-setup` — Run once, by the architect agent

Sets up the collaboration from scratch. It interviews you about your project and agents, then generates a `.collab/` protocol directory with everything agents need to coordinate:

- `PROTOCOL.md` — shared rulebook every agent reads
- `config.yaml` — role registry with file scopes
- `status/` — per-agent status files (zero merge conflicts)
- `messages.md` — append-only communication log
- `tasks.md` — shared task board
- `contracts/` — interface definitions between agents
- `decisions.md` — architecture decision record
- Git pre-commit hook that blocks out-of-scope commits

Also generates copy-paste onboarding prompts for every other agent.

Only the architect agent needs this skill. All agents need `collab-protocol`.

### `collab-protocol` — Loaded by every participating agent

The day-to-day rules each agent follows on every task:

- Pull main, check messages, pick up a task
- Branch and commit with role-prefixed names
- Post messages when work affects another agent
- Negotiate interface contracts before building against them
- Escalate deadlocks to the human after 4 unresolved exchanges
- Mark tasks Done only with passing test evidence

---

## Installation

### Claude Code

This marketplace is hosted on GitHub. Add it in Claude Code:

```
/plugin marketplace add Skylier07/multi-agent-collab-skill
```

Then install the skills you need:

```
/plugin install collab-setup@collab-skills
/plugin install collab-protocol@collab-skills
```

**Who installs what:**
- The agent running initial setup needs `collab-setup`
- Every agent participating in the collaboration needs `collab-protocol`

### Cursor Plugin (same repo)

This repository now includes Cursor plugin manifests:

- Repo marketplace: `.cursor-plugin/marketplace.json`
- Plugin manifests:
  - `plugins/collab-setup/.cursor-plugin/plugin.json`
  - `plugins/collab-protocol/.cursor-plugin/plugin.json`

Local test in Cursor:

1. Symlink or copy one plugin into `~/.cursor/plugins/local/`:
   - `~/.cursor/plugins/local/collab-setup` -> `plugins/collab-setup`
   - `~/.cursor/plugins/local/collab-protocol` -> `plugins/collab-protocol`
2. Reload Cursor (`Developer: Reload Window`)
3. Verify the skills appear and can be invoked

To publish on Cursor Marketplace, submit this GitHub repo at:

- <https://cursor.com/marketplace/publish>

### Manual installation (other platforms)

| Platform    | Path                                        |
|-------------|---------------------------------------------|
| Claude Code | `.claude/skills/collab-setup/` or `~/.claude/skills/collab-setup/` |
| Gemini CLI  | `.gemini/skills/collab-setup/` or `~/.gemini/skills/collab-setup/` |
| Cursor      | `.cursor/skills/collab-setup/`              |
| Codex CLI   | `.agents/skills/collab-setup/`              |

Replace `collab-setup` with `collab-protocol` for the protocol skill. Copy the full skill directory including `references/` and `scripts/` subdirectories.

---

## Quick Start

1. Install `collab-setup` on the architect agent
2. Run `/collab-setup` — it will interview you and generate `.collab/`
3. Copy the generated onboarding prompt into each other agent
4. Every agent installs `collab-protocol` and follows it on every task

## License

MIT
