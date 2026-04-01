---
name: collab-setup
description: >
  Initializes multi-agent collaboration on a codebase. Interviews the user, generates
  the .collab/ protocol directory, installs git hooks for scope enforcement, and produces
  copy-paste onboarding prompts for each agent. Use this skill when the user wants to SET UP
  collaboration between AI coding agents, mentions "shared brain", asks to coordinate between
  two or more agents on a project, or wants to add/remove/swap agents in an existing collab.
  This skill handles initial setup and structural changes only — for the ongoing collaboration
  rules that agents follow during daily work, see the companion skill collab-protocol.
---

# Collab Setup — Architect

Two use cases: **initial setup** (bootstrapping a new collaboration) and **structural
changes** (adding, removing, or swapping agents in an existing one). After either,
agents use the companion `collab-protocol` skill for ongoing work.

**Platform-agnostic:** Works on Claude Code, Gemini CLI, Cursor, Codex CLI, Antigravity,
and any agent supporting the universal `SKILL.md` format.

## How It Works

This skill's directory contains:
```
collab-setup/
├── SKILL.md               ← you are here
├── references/
│   ├── protocol-template.md   # Template for .collab/PROTOCOL.md
│   ├── file-templates.md      # Templates for config.yaml, status/, messages.md, etc.
│   ├── git-hooks.md           # Pre-commit hook script and install commands
│   └── prompt-patterns.md     # Onboarding prompt templates (8–35 lines each)
└── scripts/
    ├── validate_scope.py      # Copy into .collab/scripts/ during setup
    └── archive_messages.py    # Copy into .collab/scripts/ during setup
```

Steps:
1. **Interview** — Ask the user about their project, agents, and goals
2. **Design** — Decide roles, scopes, and contracts
3. **Generate** — Create `.collab/` directory with all files
4. **Enforce** — Install git pre-commit hook for scope validation
5. **Prompt** — Generate short onboarding prompts for each other agent
6. **Activate** — Set yourself up in your assigned role

## Step 1: The Interview

Ask conversationally. Adapt to the user's technical level. Resolve in 1–2 exchanges.

### Required Information

**Project:** name, description, existing repo or fresh, tech stack
**Agents:** which platforms, what each is responsible for, which machines
**Workflow:** sync frequency, git comfort level

### Common Role Patterns

**2 agents:**

| Project Type        | Agent A              | Agent B              |
|---------------------|----------------------|----------------------|
| Full-stack web app  | Backend / API        | Frontend / UI        |
| Monorepo            | Core library / API   | Apps / integrations  |
| Data pipeline       | ETL / processing     | Dashboard / viz      |
| Mobile + API        | API server           | Mobile app           |
| Microservices       | Service A            | Service B            |

**3+ agents** — layer onto any 2-agent pattern:

| Extra Agent Role     | Scope                          |
|----------------------|--------------------------------|
| DevOps               | Infra / CI/CD / Docker         |
| Testing / QA         | E2E tests / test utilities     |
| Data                 | Database / migrations          |
| Additional service   | Another microservice           |

Ensure scopes don't overlap — each file path belongs to exactly one agent.

### Inferring Scope

- "Backend" → `src/backend/**, lib/**, database/**, server/**`
- "Frontend" → `src/frontend/**, public/**, src/components/**, src/styles/**`
- "Full-stack framework" → split by `app/api/**` vs `app/(pages)/**`
- "DevOps" → `infra/**, docker/**, .github/**, Dockerfile`

If an existing repo, examine the directory structure for precise paths.

## Step 2: Generate .collab/

Read `references/protocol-template.md` for PROTOCOL.md content.
Read `references/file-templates.md` for all other files.
Copy scripts from this skill's `scripts/` directory into `.collab/scripts/`.

```
.collab/
├── PROTOCOL.md          # Shared rulebook (all agents read this)
├── config.yaml          # Role registry with scopes (N agents)
├── status/              # Per-agent YAML files (zero merge conflicts)
├── messages.md          # Append-only message log
├── tasks.md             # Shared task queue
├── contracts/           # Interface definitions per boundary
├── decisions.md         # Architecture Decision Record
├── history.md           # Archived threads
└── scripts/
    ├── validate_scope.py
    ├── archive_messages.py
    └── pre-commit          # Git hook script
```

## Step 3: Install Git Hooks

Read `references/git-hooks.md` for the hook script and installation commands.
The hook blocks out-of-scope commits. Each machine needs it installed locally —
include the setup commands in every agent's onboarding prompt.

## Step 4: Generate Agent Prompts

Read `references/prompt-patterns.md` for the full template library.

For agents with `collab-protocol` installed, the prompt is ~8 lines.
For agents without it, use this compact pattern (~15 lines):

```
You are **[ROLE] Lead** on "[PROJECT]". Other AI agents handle other parts.
Your files: [SCOPE]  |  Don't touch: [EXCLUDED]
Branch: collab/[ROLE]/task-name  |  Commits: [ROLE] type: desc

Setup: echo "[ROLE]" > .collab/scripts/.role && cp .collab/scripts/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

Read .collab/PROTOCOL.md for all rules. Read decisions.md for context.
Before every task: pull main, check messages.md and tasks.md.
Before every push: update status/[ROLE].yaml.
Start: read .collab/, set status to ready, tell me your first task.
```

**For 3+ agents:** generate a separate prompt for each. List all other agents by role
so each understands the full topology.

## Step 5: Self-Activation

1. Write your role to `.collab/scripts/.role`
2. Install the pre-commit hook locally
3. Create your status file with state `ready`
4. Post MSG-001 in `messages.md`
5. Tell the user what you're starting on

## Structural Changes (Post-Setup)

This skill also handles role swaps, adding agents, and removing agents:
1. Update `.collab/config.yaml`
2. Post an `info` message announcing the change
3. Update `.collab/scripts/.role` if your own role changed
4. Generate re-onboarding prompts for affected agents
5. Update status files

## Installation

| Platform        | Workspace                       | Global                                       |
|-----------------|---------------------------------|----------------------------------------------|
| Claude Code     | `.claude/skills/collab-setup/`  | `~/.claude/skills/collab-setup/`             |
| Gemini CLI      | `.gemini/skills/collab-setup/`  | `~/.gemini/skills/collab-setup/`             |
| Antigravity     | `.agent/skills/collab-setup/`   | `~/.gemini/antigravity/skills/collab-setup/` |
| Cursor          | `.cursor/skills/collab-setup/`  | `~/.cursor/skills/collab-setup/`             |
| Codex CLI       | `.agents/skills/collab-setup/`  | `~/.codex/skills/collab-setup/`              |
| Cross-platform  | `.agents/skills/collab-setup/`  | `~/.agents/skills/collab-setup/`             |

Only the architect agent needs this skill. All participating agents need `collab-protocol`.
