# Protocol Template for PROTOCOL.md

Generate `.collab/PROTOCOL.md` with this content, customized for the project.
This is the shared rulebook that every agent reads from the repo.

---

BEGIN TEMPLATE (everything below goes into .collab/PROTOCOL.md):

```markdown
# Collaboration Protocol

This file defines how agents work together on this project. Every agent must read this
file in full before starting work. When in doubt, re-read the relevant section.

## Agents and Scopes

See `config.yaml` for the full role registry. Key rules:
- **Never modify files outside your declared scope.**
- A pre-commit git hook enforces this — out-of-scope commits are physically blocked.
- If you need to touch an out-of-scope file, use the scope-request flow (see below).

## Workflow — Every Task

1. `git pull origin main`
2. Read your messages: scan `messages.md` for entries where `To:` matches your role
   and `Status:` is `pending`. Handle `Priority: blocking` messages first.
3. Check `tasks.md` for your next task (assigned to you, or self-assign from Backlog)
4. Check `contracts/` for interface specs you depend on — only build against `accepted`
5. Create your branch: `collab/YOUR_ROLE/task-slug`
6. Do the work
7. Before committing: the pre-commit hook validates scope automatically
8. Before pushing: update your status file in `status/YOUR_ROLE.yaml`
9. If your work affects another agent: post a message AND update/create a contract
10. Push your branch

## Status — Per-Agent Files

Each agent has its own file in `status/`. Write ONLY to your own file. Read all files
to see the full status board.

File: `status/YOUR_ROLE.yaml`
```yaml
role: backend
agent: Claude Code
task: "Implement auth middleware"
state: in-progress  # initializing | ready | in-progress | blocked | done | role-swapped
branch: collab/backend/auth-middleware
updated: 2026-03-31T14:00Z
blocker: null  # or "Waiting on auth contract acceptance (MSG-005)"
```

## Messages — How Agents Communicate

File: `messages.md` — **APPEND-ONLY.** Never edit or delete existing messages.

### Format
\```
---
### MSG-XXX | YYYY-MM-DDTHH:MMZ
- **From:** your_role
- **To:** recipient_role (or "all" or "human")
- **Type:** see types below
- **Priority:** normal | high | blocking
- **Status:** pending
- **Body:** Your message.
- **Re:** MSG-XXX (if replying)
\```

Find the highest existing MSG number and add 1.

### Message Types
| Type              | When to use                                        |
|-------------------|----------------------------------------------------|
| `info`            | FYI — no response needed                           |
| `question`        | You need an answer from the recipient               |
| `answer`          | Replying to a question (set Re: field)             |
| `contract-change` | Proposing an interface change                      |
| `contract-accept` | Accepting a proposed change                        |
| `contract-reject` | Rejecting a change (must include reason)           |
| `scope-request`   | Asking to edit files outside your scope            |
| `scope-grant`     | Approving a scope request                          |
| `scope-deny`      | Denying a scope request (must include reason)      |
| `blocker`         | You're stuck and need help                         |
| `task-complete`   | Finished a task (must include test evidence)       |
| `task-handoff`    | Delegating work to another agent                   |
| `decision`        | Recording an architectural decision to decisions.md|
| `emergency-stop`  | Forces all agents to halt and wait for human       |

## Deadlock Prevention

Agents can get stuck in unproductive loops (e.g., repeated clarification requests,
circular contract rejections, or ambiguous answers that don't resolve).

**The 4-message rule:** If any message thread (tracked by `Re:` references) reaches
4 messages without resolving to `Status: resolved`, the NEXT agent to respond MUST:
1. Change the thread's priority to `blocking`
2. Set `To: human`
3. Summarize the disagreement in 2-3 sentences
4. Propose two concrete options for the human to pick between

**Contract deadlock:** If a contract proposal is rejected twice by the same stakeholder
(after revision), the rejecting agent MUST post an `emergency-stop` message.
All agents with a stake in the contract update their status to `blocked` and wait
for the human.

**Multi-agent disputes:** When 3+ agents are involved in a contract, any two agents
that cannot agree after 2 rounds of proposal/rejection trigger the emergency-stop.
The other agents are not blocked — only the disputing parties and anyone who depends
on the contested contract.

**Emergency stop:** Any agent can post `Type: emergency-stop` at any time. When you
see an emergency-stop message (regardless of who it's addressed to), you MUST:
1. Stop your current work
2. Commit and push what you have (even if incomplete)
3. Update your status to `blocked`
4. Wait for the human to resolve and post a follow-up `info` message

## Contracts — Shared Interfaces

Files in `contracts/` define interfaces between agents (API endpoints, data models, etc.).

### Rules
- Any agent can propose a change: set `Status: proposed` in the contract file and
  post a `contract-change` message
- **Who must accept?** Every agent whose scope touches the interface ("stakeholders")
  must post `contract-accept` before the contract becomes `accepted`. The proposing
  agent lists stakeholders in the `contract-change` message `To:` field (comma-separated
  roles, or `all` if uncertain). If only two agents share an interface, one acceptance
  suffices. If three or more share it, all must accept.
- **Never build against a `proposed` contract — only `accepted` ones**
- Agents have full autonomy to accept or reject — no human approval needed
- When accepting: if possible, run a quick type-check or mock test against the contract
  before posting `contract-accept` (recommended but not required)
- A single `contract-reject` from any stakeholder blocks the change — the proposer
  must revise and re-propose

### Contract File Format
\```markdown
# Contract: [Area Name]
**Version:** 1.0
**Status:** proposed | accepted
**Modified by:** role_id
**Date:** YYYY-MM-DD
**Stakeholders:** backend, frontend  (all roles that must accept)
**Accepted by:** frontend  (roles that have accepted so far; when all stakeholders
                             are listed here, change Status to accepted)

## [Endpoint/Interface Name]
[Request/response specs, data models, event schemas, etc.]

## Changelog
- v1.0: Initial contract
\```

### After Acceptance
When a contract is accepted, the accepting agent MUST also add a one-line entry to
`decisions.md` recording the decision. Format:

```
- **[DATE]** — CONTRACT: [contract name] v[X] accepted. [One sentence summary of what
  was agreed and why.] (Ref: MSG-XXX)
```

## Test-Driven Task Completion

A task CANNOT be moved to Done in `tasks.md` and a `task-complete` message CANNOT be
sent unless the agent includes evidence that the work is functional. Evidence means
one of:
- Terminal output of passing tests (paste into the message body or commit message)
- A successful build/compile command output
- For UI work: a description of what was manually verified in the browser

If the agent cannot run tests (no test runner configured), it must explicitly state
this in the `task-complete` message body: "No test runner available — verified by
[manual method]."

The receiving agent should verify compatibility before building on top of handed-off
work. If a `task-handoff` references code that fails on the receiving end, post a
`blocker` message immediately — do not try to silently fix the other agent's code.

## Scope Enforcement

A pre-commit git hook automatically validates every commit against your declared scope.
If you attempt to commit an out-of-scope file, the commit will be rejected with an
error message listing the violations.

When the hook blocks your commit:
1. Unstage the out-of-scope files: `git reset HEAD <file>`
2. Post a `scope-request` message. Set `To:` to the role that owns the file
   (check `config.yaml` to find which agent's scope includes it)
3. Wait for a `scope-grant` response from that specific agent
4. After receiving the grant, commit with: `[role] type: desc (scope-grant MSG-XXX)`

## Architecture Decisions Record

File: `decisions.md` — A lightweight log of key decisions. Agents add entries when:
- A contract is accepted (or significantly revised)
- A complex message thread is resolved
- A significant technical choice is made

This file is the "catch-up" document — a newly onboarded agent (or one whose context
has reset) reads this instead of digging through history.

Format:
```
- **[DATE]** — CATEGORY: [One sentence summary.] (Ref: MSG-XXX)
```

Categories: `CONTRACT`, `ARCHITECTURE`, `SCOPE`, `BUGFIX`, `CONVENTION`

## Message Archival

When `messages.md` exceeds 10 resolved threads, the designated janitor agent (see
`config.yaml`) runs `.collab/scripts/archive_messages.py` to move resolved threads
to `history.md`. The script:
1. Finds message threads where all messages have `Status: resolved`
2. Moves them to `history.md` with a date header
3. Leaves a one-line tombstone in `messages.md`: `_[MSG-XXX through MSG-YYY archived]_`

## Task Board

File: `tasks.md` — Sections: Backlog, In Progress, Done.
- Self-assign from Backlog
- Move only your own tasks between sections
- Include branch name and dependencies
- Moving to Done requires test evidence (see Test-Driven Task Completion)

## Git Conventions

- Branch: `collab/your_role/task-slug`
- Commits: `[your_role] type: description`
- Always pull main before starting a task
- Push your branch when done — the human (or auto-merge) integrates to main
```

END TEMPLATE
