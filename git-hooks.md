# Git Hooks — Scope Enforcement

## Overview

The pre-commit hook physically prevents agents from committing files outside their
declared scope. It reads the agent's role from `.collab/scripts/.role` and validates
all staged files against `config.yaml`.

## Installation

Run these commands on each machine (include in every agent's onboarding prompt):

```bash
# Set the agent's role (run once per machine)
echo "ROLE_ID_HERE" > .collab/scripts/.role

# Install the pre-commit hook
cp .collab/scripts/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Pre-Commit Hook Script

Generate this as `.collab/scripts/pre-commit`:

```bash
#!/usr/bin/env bash
# Multi-agent scope enforcement hook
# Blocks commits containing files outside the agent's declared scope.

set -euo pipefail

ROLE_FILE=".collab/scripts/.role"
CONFIG_FILE=".collab/config.yaml"

if [ ! -f "$ROLE_FILE" ]; then
    echo "ERROR: No role file found at $ROLE_FILE"
    echo "Run: echo 'your_role' > $ROLE_FILE"
    exit 1
fi

ROLE=$(cat "$ROLE_FILE" | tr -d '[:space:]')

if [ -z "$ROLE" ]; then
    echo "ERROR: Role file is empty. Set your role:"
    echo "  echo 'backend' > $ROLE_FILE"
    exit 1
fi

# Run the Python validator against staged files
STAGED=$(git diff --cached --name-only --diff-filter=ACMR)

if [ -z "$STAGED" ]; then
    exit 0
fi

python3 .collab/scripts/validate_scope.py --role "$ROLE" --config "$CONFIG_FILE" --files $STAGED
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  COMMIT BLOCKED — scope violation detected for role: $ROLE"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "  To fix:"
    echo "  1. Unstage out-of-scope files:  git reset HEAD <file>"
    echo "  2. Post a scope-request in .collab/messages.md"
    echo "  3. Wait for a scope-grant before re-committing"
    echo ""
    exit 1
fi
```

## How It Works in Practice

1. Agent stages files and runs `git commit`
2. Hook reads agent's role from `.collab/scripts/.role`
3. Hook runs `validate_scope.py` against staged files
4. If all files are in-scope → commit proceeds normally
5. If any file is out-of-scope → commit is rejected with clear instructions

The agent sees the rejection in their terminal and is naturally prompted to:
- Remove the out-of-scope file from the commit
- Post a `scope-request` message in the protocol
- Wait for approval before retrying

This is much more reliable than asking agents to "remember" to check scope, because
the git layer enforces it mechanically.
