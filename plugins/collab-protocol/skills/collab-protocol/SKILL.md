---
name: collab-protocol
description: >
  Day-to-day rules for multi-agent collaboration on a shared codebase via git. Use this
  skill whenever you are working in a repo with a .collab/ directory. Covers messages,
  contracts, scope enforcement, deadlock prevention, and task lifecycle. Companion to
  collab-setup (which handles one-time initialization — use that if no .collab/ exists).
---

# Collab Protocol — Participant Rules

This skill contains the rules for participating in a multi-agent collaboration. It is
loaded by every agent on every task — keep it lean.

The collaboration was initialized by the `collab-setup` skill, which created the `.collab/`
directory. This skill tells you how to use those files correctly.

**Recovery:** If `.collab/` exists but is missing files (e.g., no `PROTOCOL.md`, no
`config.yaml`, no `status/` directory), the setup was incomplete. Tell the user to run
`collab-setup` again — it will regenerate missing files without overwriting existing ones.

## Quick Reference — Every Task

1. `git pull origin main`
2. Read `messages.md` for messages where `To:` is your role and `Status:` is `pending`
3. Handle `Priority: blocking` messages before anything else
4. Check `tasks.md` for your next task
5. Check `contracts/` — only build against `Status: accepted`
6. Branch: `collab/YOUR_ROLE/task-slug`
7. Work. The pre-commit hook validates scope automatically.
8. Before pushing: update `status/YOUR_ROLE.yaml`
9. If your work affects another agent: post a message AND update a contract
10. Push your branch

## Key Files

| File                  | Purpose                    | Your access                    |
|-----------------------|----------------------------|--------------------------------|
| `config.yaml`         | Role registry and scopes   | Read only (human modifies)     |
| `PROTOCOL.md`         | Rules (also in this skill) | Read only                      |
| `status/YOUR_ROLE.yaml` | Your live status          | Write your own file only       |
| `messages.md`         | Communication log          | Append only — never edit/delete|
| `tasks.md`            | Task board                 | Move your own tasks only       |
| `contracts/*.md`      | Interface contracts        | Propose, accept, reject        |
| `decisions.md`        | Decision log               | Append entries                 |
| `history.md`          | Archive                    | Read only (janitor writes)     |

## Status File

Write ONLY to `status/YOUR_ROLE.yaml`. Read all files in `status/` for the full board.

```yaml
role: your_role
agent: Your Agent Name
task: "Current task description"
state: in-progress   # initializing | ready | in-progress | blocked | done | role-swapped
branch: collab/your_role/task-slug
updated: YYYY-MM-DDTHH:MMZ
blocker: null        # or "Waiting on X (MSG-NNN)"
```

## Messages

Append to `messages.md`. Find the highest MSG number and add 1.

```
---
### MSG-XXX | YYYY-MM-DDTHH:MMZ
- **From:** your_role
- **To:** recipient_role (or "all" or "human")
- **Type:** info | question | answer | contract-change | contract-accept |
            contract-reject | scope-request | scope-grant | scope-deny |
            blocker | task-complete | task-handoff | decision | emergency-stop
- **Priority:** normal | high | blocking
- **Status:** pending
- **Body:** Your message.
- **Re:** MSG-XXX (if replying)
```

## Contract Negotiation

Contracts live in `contracts/`. They define shared interfaces between agents.

**Proposing:** Set `Status: proposed` in the contract, post a `contract-change` message.
List all stakeholder roles in the `To:` field.

**Accepting/Rejecting:** Post `contract-accept` or `contract-reject`. A rejection must
include a reason. All stakeholders must accept before a contract becomes `accepted`.

**Key rules:**
- Never build against a `proposed` contract — only `accepted`
- A single reject from any stakeholder blocks the change
- After acceptance, add a one-liner to `decisions.md`

**Contract format:**
```
# Contract: [Area Name]
**Version:** 1.0  |  **Status:** proposed | accepted
**Modified by:** role  |  **Date:** YYYY-MM-DD
**Stakeholders:** role_a, role_b  |  **Accepted by:** role_b
```

## Deadlock Prevention

**4-message rule:** If a thread reaches 4 messages without resolving, the next agent
to respond MUST escalate to the human: set `Priority: blocking`, `To: human`, summarize
in 2–3 sentences, propose two concrete options.

**Contract deadlock:** If a stakeholder rejects the same contract twice (after revision),
post `emergency-stop`. Disputing parties and dependents go `blocked`.

**Emergency stop:** When you see `Type: emergency-stop` (regardless of recipient):
stop work, commit and push what you have, set status to `blocked`, wait for human.

## Task Completion

A task CANNOT move to Done and `task-complete` CANNOT be sent without evidence:
- Passing test output, OR
- Successful build output, OR
- Manual verification description (with explicit note: "No test runner available")

If a `task-handoff` references code that fails on your end, post `blocker` immediately.

## Scope Enforcement

The pre-commit hook blocks out-of-scope commits automatically.

When blocked:
1. `git reset HEAD <out-of-scope-file>`
2. Post `scope-request` with `To:` set to the file's owning role (check `config.yaml`)
3. Wait for `scope-grant`
4. Commit with: `[role] type: desc (scope-grant MSG-XXX)`

## Decisions Record

Append to `decisions.md` when: a contract is accepted, a dispute is resolved, or a
significant technical choice is made.

Format: `- **[DATE]** — CATEGORY: [Summary.] (Ref: MSG-XXX)`
Categories: `CONTRACT`, `ARCHITECTURE`, `SCOPE`, `BUGFIX`, `CONVENTION`

## Housekeeping

The janitor agent is designated in `config.yaml` → `housekeeping.janitor` (set during
`collab-setup` initialization — defaults to the architect agent). If the field is missing,
the first agent listed in `config.yaml` is the janitor. Responsibilities:
- When `messages.md` exceeds 10 resolved threads, run `.collab/scripts/archive_messages.py`
- Ensure `decisions.md` is updated after contract acceptances
- Nudge stale agents via messages if their status files are outdated

## Git Conventions

- Branch: `collab/your_role/task-slug`
- Commits: `[your_role] type: description`
- Pull main before every task
- Push your branch when done — human integrates to main

## Installation

| Platform        | Workspace                          | Global                                          |
|-----------------|------------------------------------|--------------------------------------------------|
| Claude Code     | `.claude/skills/collab-protocol/`  | `~/.claude/skills/collab-protocol/`              |
| Gemini CLI      | `.gemini/skills/collab-protocol/`  | `~/.gemini/skills/collab-protocol/`              |
| Antigravity     | `.agent/skills/collab-protocol/`   | `~/.gemini/antigravity/skills/collab-protocol/`  |
| Cursor          | `.cursor/skills/collab-protocol/`  | `~/.cursor/skills/collab-protocol/`              |
| Codex CLI       | `.agents/skills/collab-protocol/`  | `~/.codex/skills/collab-protocol/`               |
| Cross-platform  | `.agents/skills/collab-protocol/`  | `~/.agents/skills/collab-protocol/`              |

Every participating agent needs this skill. Only the architect needs `collab-setup`.
