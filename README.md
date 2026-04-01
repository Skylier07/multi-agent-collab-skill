# Multi-Agent Collaboration Skill

A two-skill system for coordinating multiple AI coding agents (Claude Code, Gemini CLI, Cursor, Codex, etc.) on a shared codebase. Agents work in parallel without stepping on each other — scope is enforced at the git layer, communication happens through append-only files, and deadlocks are caught before they spiral.

## The Problem

When you put two or more AI agents on the same project — say Claude Code on the backend and Gemini CLI on the frontend — they have no way to coordinate. They overwrite each other's files, build against APIs that don't exist yet, and have no channel to communicate decisions. The human becomes a full-time relay operator, copy-pasting context between terminals, while constantly be in the fear of merge conflicts. 

## The Solution

These skills give agents a structured collaboration protocol through files in a `.collab/` directory, synced via git. Agents communicate through append-only messages, negotiate shared interfaces through contracts, and are physically prevented from touching each other's files by a git pre-commit hook. Deadlocks are automatically detected and escalated. Task completion requires test evidence. Architectural decisions are logged so agents can recover context after a session reset.

The protocol is designed around failure modes specific to LLMs: scope violations (blocked mechanically, not by honor system), politeness loops (broken by the 4-message escalation rule), context loss (mitigated by a lightweight decision log), and the bystander effect (one agent is explicitly designated as janitor).


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

### Gemini CLI

```
gemini extensions install https://github.com/Skylier07/multi-agent-collab-skill
```
To update the skill:
```
gemini extensions update multi-agent-collab-skill
```
### Cursor (COMING SOON)
```
/add-plugin multi-agent-collab 
```

### Codex 
```
Fetch https://raw.githubusercontent.com/Skylier07/multi-agent-collab-skill/refs/heads/main/.codex/INSTALL.md and follow install instructions
```

---
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


**Who installs what:**
- The two skills are intended to be used together on the architect machine. Skills are separated to grealty reduce token usage overhead. 
- The agent running initial setup needs `collab-setup`
- Every agent participating in the collaboration needs `collab-protocol`


## Quick Start

1. Install the skills on agents of your choosing (all agents that intends to work on the project should have the skills installed)
2. Run `/collab-setup` on your architect machine — it will interview you and generate `.collab/`. It will now lead the project.
3. Copy the generated onboarding prompt into each other agent 


## How Agents Communicate

```
.collab/
├── PROTOCOL.md       # Shared rulebook every agent reads
├── config.yaml       # Who owns which files
├── status/           # Per-agent status (no merge conflicts)
├── messages.md       # Append-only message log
├── tasks.md          # Shared task board
├── contracts/        # API and interface agreements
├── decisions.md      # Lightweight architecture decision log
└── scripts/          # Scope validator + archival automation
```

Agents post structured messages, propose and accept interface contracts, and follow git conventions — all without direct communication. The human merges branches and relays urgent blockers when needed, but most coordination happens asynchronously through the protocol files.

## License

MIT
