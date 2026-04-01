# File Templates for .collab/ Directory

Generate these files during setup. Replace `{{PLACEHOLDERS}}` with project-specific values.

---

## config.yaml

```yaml
version: 2
project:
  name: "{{PROJECT_NAME}}"
  repo: "{{REPO_URL}}"

# Add one block per agent. Supports any number of agents.
agents:
  {{ROLE_ID_1}}:
    name: "{{AGENT_NAME_1}}"
    model: "{{MODEL_1}}"
    scope:
      include:
{{SCOPE_INCLUDE_1}}
      exclude:
{{SCOPE_EXCLUDE_1}}
    branch_prefix: "collab/{{ROLE_ID_1}}"

  {{ROLE_ID_2}}:
    name: "{{AGENT_NAME_2}}"
    model: "{{MODEL_2}}"
    scope:
      include:
{{SCOPE_INCLUDE_2}}
      exclude:
{{SCOPE_EXCLUDE_2}}
    branch_prefix: "collab/{{ROLE_ID_2}}"

  # Add more agents as needed:
  # {{ROLE_ID_N}}:
  #   name: "{{AGENT_NAME_N}}"
  #   model: "{{MODEL_N}}"
  #   scope:
  #     include:
  #       - "path/**"
  #     exclude:
  #       - "other_path/**"
  #   branch_prefix: "collab/{{ROLE_ID_N}}"

git:
  main_branch: "main"
  commit_prefix_by_role: true

sync:
  check_messages_before_task: true
  update_status_before_push: true

housekeeping:
  janitor: "{{ARCHITECT_ROLE_ID}}"  # the agent that ran collab-setup
  archive_after_resolved_threads: 10
  deadlock_threshold: 4
```

---

## status/{{ROLE_ID}}.yaml (one per agent)

```yaml
role: {{ROLE_ID}}
agent: {{AGENT_NAME}}
task: null
state: initializing
branch: null
updated: {{TIMESTAMP}}
blocker: null
```

---

## messages.md

```markdown
# Messages

_Append only. Never edit or delete existing messages._

---
### MSG-001 | {{TIMESTAMP}}
- **From:** {{ARCHITECT_ROLE_ID}}
- **To:** all
- **Type:** info
- **Priority:** normal
- **Status:** pending
- **Body:** Collaboration initialized. All agents: read `.collab/PROTOCOL.md` for rules,
  then update your status file in `status/` when ready.
```

---

## tasks.md

```markdown
# Tasks

## Backlog
{{INITIAL_TASKS_IF_ANY, or "_No tasks yet._"}}

## In Progress
_None_

## Done
_None_
```

---

## decisions.md

```markdown
# Architecture Decisions

_Key decisions are logged here so agents can catch up without reading full history._
_Add entries when contracts are accepted, disputes resolved, or conventions established._

- **{{DATE}}** — CONVENTION: Collaboration initialized with {{AGENT_SUMMARY}}.
  Scopes defined in config.yaml. (Ref: MSG-001)
```

---

## history.md

```markdown
# History

_Completed message threads and tasks are archived here by the janitor agent._
```
