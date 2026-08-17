---
name: autonomous-ai-agents
description: Umbrella skill for autonomous AI coding agents (Claude, Codex, Hermes Agent, OpenCode). Provides unified access to agent-specific tools and guides.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [autonomous-ai-agents, ai-agent, coding, claude, codex, hermes-agent, opencode]
---

# Autonomous AI Agents

This skill provides a unified interface for working with various autonomous AI coding agents integrated with Hermes: Claude AI, OpenAI Codex, Hermes Agent itself, and OpenCode. Each agent has its own subskill with detailed usage instructions, references, and scripts.

## Subskills

- **Claude AI** (`claude`) – Tools and guides for working with Claude AI (coding, design, etc.). See `references/claude.md`.
- **OpenAI Codex** (`codex`) – Delegate coding tasks to the OpenAI Codex CLI. See `references/codex.md`.
- **Hermes Agent** (`hermes-agent`) – Configure, extend, or contribute to Hermes Agent. See `references/hermes-agent.md`.
- **OpenCode** (`opencode`) – Delegate coding to the OpenCode CLI. See `references/opencode.md`.

## Usage

To load a specific agent's subskill within a Hermes session, use:

```
/skill claude
```

or

```
hermes -s claude chat -q "Explain how to build a REST API with FastAPI"
```

You can also enable the whole umbrella skill to make all agent‑related tools available:

```
hermes skills enable autonomous-ai-agents
```

## References

Detailed guides for each agent are stored in the `references/` directory:

- `claude.md` – Claude AI usage guide
- `codex.md` – OpenAI Codex CLI guide
- `hermes-agent.md` – Hermes Agent configuration and extension guide
- `opencode.md` – OpenCode CLI usage guide

Any associated template or script files are located in the `templates/` and `scripts/` subdirectories.

## Related Skills

- `delegate_task` – For spawning subagents to work on tasks in isolated contexts.
- `cronjob` – For scheduling periodic agent tasks.
- `kanban` – For multi‑agent collaboration boards.