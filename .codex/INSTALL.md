# Installing multi-agent-collab-skill for Codex

Codex CLI discovers skills by scanning `~/.agents/skills/` at startup and reading each
skill folder’s `SKILL.md` frontmatter (`name`, `description`).

This repo contains the most complete skill copies under:

- `plugins/collab-setup/skills/collab-setup/` (includes `references/` and `scripts/`)
- `plugins/collab-protocol/skills/collab-protocol/`

This installer clones the repo to `~/.codex/` and then links those two skill folders into
`~/.agents/skills/` so Codex can discover them.

## Prerequisites

- Git

## Installation

### macOS / Linux

1. Clone the repo:

```bash
git clone https://github.com/Skylier07/multi-agent-collab-skill.git ~/.codex/multi-agent-collab-skill
```

2. Link skills into Codex discovery:

```bash
mkdir -p ~/.agents/skills
ln -s ~/.codex/multi-agent-collab-skill/plugins/collab-setup/skills/collab-setup ~/.agents/skills/collab-setup
ln -s ~/.codex/multi-agent-collab-skill/plugins/collab-protocol/skills/collab-protocol ~/.agents/skills/collab-protocol
```

3. Restart Codex (quit and relaunch) to discover the skills.

### Windows (PowerShell)

Junctions work without Developer Mode.

1. Clone the repo:

```powershell
git clone https://github.com/Skylier07/multi-agent-collab-skill.git "$env:USERPROFILE\.codex\multi-agent-collab-skill"
```

2. Create junctions into Codex discovery:

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills" | Out-Null

cmd /c mklink /J "$env:USERPROFILE\.agents\skills\collab-setup" "$env:USERPROFILE\.codex\multi-agent-collab-skill\plugins\collab-setup\skills\collab-setup"
cmd /c mklink /J "$env:USERPROFILE\.agents\skills\collab-protocol" "$env:USERPROFILE\.codex\multi-agent-collab-skill\plugins\collab-protocol\skills\collab-protocol"
```

3. Restart Codex.

## Verify

```bash
ls -la ~/.agents/skills/collab-setup
ls -la ~/.agents/skills/collab-protocol
```

On Windows, you can check the folders exist in:

`%USERPROFILE%\.agents\skills\`

## Updating

```bash
cd ~/.codex/multi-agent-collab-skill && git pull
```

The skills update immediately through the links.

## Uninstalling

Remove the linked skill folders:

```bash
rm ~/.agents/skills/collab-setup
rm ~/.agents/skills/collab-protocol
```

Windows:

```powershell
Remove-Item "$env:USERPROFILE\.agents\skills\collab-setup"
Remove-Item "$env:USERPROFILE\.agents\skills\collab-protocol"
```

Optionally delete the clone:

```bash
rm -rf ~/.codex/multi-agent-collab-skill
```

