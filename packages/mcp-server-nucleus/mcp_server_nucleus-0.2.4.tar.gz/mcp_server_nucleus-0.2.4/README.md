# 🧠 Nucleus MCP Server

[![PyPI version](https://badge.fury.io/py/mcp-server-nucleus.svg)](https://badge.fury.io/py/mcp-server-nucleus)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **The Core of Your AI Agents** — Multi-agent orchestration MCP server

`mcp-server-nucleus` connects your local "Nuclear Brain" agentic system with MCP-compatible clients like Claude Desktop, Cursor, and more.

## ✨ Features

- **10 MCP Tools** for agent orchestration
- **3 MCP Resources** for subscribable state
- **2 MCP Prompts** for pre-built orchestration
- **Local Intelligence** — Directly manipulates your `.brain/` directory
- **Event-Driven** — Emit and listen to system events
- **Zero-Knowledge Default** — Your data stays local

## 🚀 Quick Start

### Installation

```bash
# Requires Python 3.10+ (use python3.11 if your default python3 is older)
python3.11 -m pip install mcp-server-nucleus

# Or with pip directly
pip3.11 install mcp-server-nucleus
```

> **Note:** If you get "No matching distribution found", your Python version is too old. Check with `python3 --version` and install Python 3.10+ if needed.

### Initialize Your Brain (Smart Init!)

```bash
# Create a new .brain/ directory — auto-configures Claude Desktop!
nucleus-init
```

> **v0.2.2+**: Smart Init automatically detects Claude Desktop and adds the config for you!

### Configuration (Claude Desktop)

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "nucleus": {
      "command": "python3",
      "args": ["-m", "mcp_server_nucleus"],
      "env": {
        "NUCLEAR_BRAIN_PATH": "/path/to/your/.brain"
      }
    }
  }
}
```

Restart Claude Desktop and try: *"What's my current sprint focus?"*

## 🛠 Available Tools

| Tool | Description |
|------|-------------|
| `brain_emit_event` | Emit a new event to the ledger |
| `brain_read_events` | Read recent events |
| `brain_get_state` | Get current brain state |
| `brain_update_state` | Update brain state |
| `brain_read_artifact` | Read an artifact file |
| `brain_write_artifact` | Write to an artifact file |
| `brain_list_artifacts` | List all artifacts |
| `brain_trigger_agent` | Trigger an agent with a task |
| `brain_get_triggers` | Get all neural triggers |
| `brain_evaluate_triggers` | Evaluate trigger activation |

## 📡 MCP Resources

| Resource | Description |
|----------|-------------|
| `brain://state` | Live state.json content |
| `brain://events` | Recent events stream |
| `brain://triggers` | Trigger definitions |
| `brain://context` | **Full context for cold start** — click in sidebar for instant context |

## 💬 MCP Prompts

| Prompt | Description |
|--------|-------------|
| `cold_start` | **Get instant context** — sprint, events, artifacts, workflows |
| `activate_synthesizer` | Orchestrate current sprint |
| `start_sprint` | Initialize a new sprint |

## 🚀 Cold Start (New in v0.2.4)

Start every new session with full context:

```
> Use the cold_start prompt from nucleus
```

Or click `brain://context` in Claude Desktop's sidebar.

**What you get:**
- Current sprint name, focus, and status
- Recent events and artifacts
- Workflow detection (e.g., `lead_agent_model.md`)
- Lead Agent role assignment

## 📁 Expected `.brain/` Structure

```
.brain/
├── ledger/
│   ├── events.jsonl
│   ├── state.json
│   └── triggers.json
├── artifacts/
│   ├── research/
│   ├── strategy/
│   └── ...
└── agents/
    └── *.md
```

## 📜 License

MIT © Nucleus Team

