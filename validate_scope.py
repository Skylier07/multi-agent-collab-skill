#!/usr/bin/env python3
"""
Scope Validator for Multi-Agent Collaboration Protocol

Validates that staged files fall within the agent's declared scope.
Used both as a standalone tool and as the engine behind the pre-commit hook.

Usage:
    python validate_scope.py --role backend
    python validate_scope.py --role backend --files src/backend/app.py src/frontend/index.tsx

Exit codes:
    0 = all files in scope
    1 = scope violation detected
    2 = configuration error
"""

import argparse
import fnmatch
import subprocess
import sys


def parse_config(filepath):
    """Parse config.yaml without requiring PyYAML.

    Handles our specific YAML structure: agents with scope include/exclude lists.
    Patterns can be quoted or unquoted.
    """
    with open(filepath) as f:
        lines = f.readlines()

    agents = {}
    current_agent = None
    in_agents = False
    current_list = None

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        indent = len(line) - len(line.lstrip())

        if stripped == 'agents:':
            in_agents = True
            continue

        # Top-level key that isn't agents → stop parsing agents
        if indent == 0 and stripped.endswith(':') and stripped != 'agents:':
            in_agents = False
            current_agent = None
            continue

        if in_agents and indent == 2 and stripped.endswith(':'):
            key = stripped[:-1].strip()
            if key not in ('scope', 'include', 'exclude', 'name', 'model',
                           'branch_prefix', 'machine'):
                current_agent = key
                agents[current_agent] = {'include': [], 'exclude': []}
                current_list = None
            elif key == 'include':
                current_list = 'include'
            elif key == 'exclude':
                current_list = 'exclude'
            continue

        if in_agents and indent == 6 and stripped.startswith('include:'):
            current_list = 'include'
            continue
        if in_agents and indent == 6 and stripped.startswith('exclude:'):
            current_list = 'exclude'
            continue

        if in_agents and current_agent and current_list and stripped.startswith('- '):
            pattern = stripped[2:].strip().strip('"').strip("'")
            agents[current_agent][current_list].append(pattern)
            continue

        # Reset list context on non-list lines within an agent
        if in_agents and current_agent and not stripped.startswith('-') and ':' in stripped:
            key = stripped.split(':')[0].strip()
            if key in ('include', 'exclude'):
                current_list = key
            elif key in ('name', 'model', 'branch_prefix', 'machine'):
                current_list = None

    return agents


def get_staged_files():
    """Get list of staged files from git."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR'],
            capture_output=True, text=True, check=True
        )
        return [f for f in result.stdout.strip().split('\n') if f]
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: Could not read git staged files.")
        sys.exit(2)


def check_file(filepath, include_patterns, exclude_patterns):
    """Check if a file is within scope. Returns (in_scope, reason)."""

    # .collab/ protocol files — agents can write to specific ones
    if filepath.startswith('.collab/'):
        # Per-agent status files are always writable by that agent
        if filepath.startswith('.collab/status/'):
            return True, "per-agent status file"
        # messages.md is append-only but writable
        if filepath == '.collab/messages.md':
            return True, "append-only message log"
        # decisions.md is writable by all agents
        if filepath == '.collab/decisions.md':
            return True, "architecture decisions record"
        # tasks.md is writable by all agents
        if filepath == '.collab/tasks.md':
            return True, "shared task board"
        # contracts are writable (proposal/acceptance flow)
        if filepath.startswith('.collab/contracts/'):
            return True, "contract file"
        # config.yaml is human-only
        if filepath == '.collab/config.yaml':
            return False, "config.yaml is human-only — do not modify"
        # PROTOCOL.md is human-only
        if filepath == '.collab/PROTOCOL.md':
            return False, "PROTOCOL.md is human-only — do not modify"
        # Everything else in .collab/ is allowed
        return True, "protocol file"

    # Exclude patterns take priority
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(filepath, pattern):
            return False, f"blocked by exclude pattern: {pattern}"

    # Check include patterns
    for pattern in include_patterns:
        if fnmatch.fnmatch(filepath, pattern):
            return True, f"in scope: {pattern}"

    return False, "not matched by any include pattern"


def main():
    parser = argparse.ArgumentParser(description='Validate files against agent scope')
    parser.add_argument('--role', required=True, help='Agent role ID (e.g., backend)')
    parser.add_argument('--config', default='.collab/config.yaml', help='Config file path')
    parser.add_argument('--files', nargs='*', help='Files to check (default: git staged)')
    args = parser.parse_args()

    try:
        agents = parse_config(args.config)
    except FileNotFoundError:
        print(f"ERROR: Config not found: {args.config}")
        sys.exit(2)
    except Exception as e:
        print(f"ERROR: Failed to parse config: {e}")
        sys.exit(2)

    if args.role not in agents:
        print(f"ERROR: Role '{args.role}' not in config. Available: {list(agents.keys())}")
        sys.exit(2)

    include = agents[args.role]['include']
    exclude = agents[args.role]['exclude']
    files = args.files if args.files else get_staged_files()

    if not files:
        sys.exit(0)

    violations = []
    ok = []

    for f in files:
        in_scope, reason = check_file(f, include, exclude)
        if in_scope:
            ok.append((f, reason))
        else:
            violations.append((f, reason))

    for f, reason in ok:
        print(f"  OK  {f} ({reason})")

    if violations:
        print("")
        for f, reason in violations:
            print(f"  VIOLATION  {f} — {reason}")
        print(f"\n{len(violations)} file(s) out of scope for role '{args.role}'.")
        print("Post a scope-request in .collab/messages.md to request access.")
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
