
import os
import json
import time
import uuid
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
import sys

# Configure FastMCP to disable banner and use stderr for logging to avoid breaking MCP protocol
os.environ["FASTMCP_SHOW_CLI_BANNER"] = "False"
os.environ["FASTMCP_LOG_LEVEL"] = "WARNING"

from fastmcp import FastMCP

# Setup logging
# logging.basicConfig(level=logging.INFO) # Removing to prevent overriding FastMCP settings
logger = logging.getLogger("nucleus")
logger.setLevel(logging.WARNING)

# Initialize FastMCP Server
mcp = FastMCP("Nucleus Brain")

# Configuration
BRAIN_PATH = os.environ.get("NUCLEAR_BRAIN_PATH")

def get_brain_path() -> Path:
    if not BRAIN_PATH:
        raise ValueError("NUCLEAR_BRAIN_PATH environment variable not set")
    path = Path(BRAIN_PATH)
    if not path.exists():
         raise ValueError(f"Brain path does not exist: {BRAIN_PATH}")
    return path

# ============================================================
# CORE LOGIC (Testable, plain functions)
# ============================================================

def _emit_event(event_type: str, emitter: str, data: Dict[str, Any], description: str = "") -> str:
    """Core logic for emitting an event."""
    try:
        brain = get_brain_path()
        events_path = brain / "ledger" / "events.jsonl"
        
        event_id = f"evt-{int(time.time())}-{str(uuid.uuid4())[:8]}"
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        
        event = {
            "event_id": event_id,
            "timestamp": timestamp,
            "type": event_type,
            "emitter": emitter,
            "data": data,
            "description": description
        }
        
        with open(events_path, "a") as f:
            f.write(json.dumps(event) + "\n")
            
        return event_id
    except Exception as e:
        return f"Error emitting event: {str(e)}"

def _read_events(limit: int = 10) -> List[Dict]:
    """Core logic for reading events."""
    try:
        brain = get_brain_path()
        events_path = brain / "ledger" / "events.jsonl"
        
        if not events_path.exists():
            return []
            
        events = []
        with open(events_path, "r") as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))
        
        return events[-limit:]
    except Exception as e:
        logger.error(f"Error reading events: {e}")
        return []

def _get_state(path: Optional[str] = None) -> Dict:
    """Core logic for getting state."""
    try:
        brain = get_brain_path()
        state_path = brain / "ledger" / "state.json"
        
        if not state_path.exists():
            return {}
            
        with open(state_path, "r") as f:
            state = json.load(f)
            
        if path:
            keys = path.split('.')
            val = state
            for k in keys:
                val = val.get(k, {})
            return val
            
        return state
    except Exception as e:
        logger.error(f"Error reading state: {e}")
        return {}

def _update_state(updates: Dict[str, Any]) -> str:
    """Core logic for updating state."""
    try:
        brain = get_brain_path()
        state_path = brain / "ledger" / "state.json"
        
        current_state = {}
        if state_path.exists():
            with open(state_path, "r") as f:
                current_state = json.load(f)
        
        current_state.update(updates)
        
        with open(state_path, "w") as f:
            json.dump(current_state, f, indent=2)
            
        return "State updated successfully"
    except Exception as e:
        return f"Error updating state: {str(e)}"

def _read_artifact(path: str) -> str:
    """Core logic for reading an artifact."""
    try:
        brain = get_brain_path()
        target = brain / "artifacts" / path
        
        if not str(target.resolve()).startswith(str((brain / "artifacts").resolve())):
             return "Error: Access denied (path traversal)"

        if not target.exists():
            return f"Error: File not found: {path}"
            
        return target.read_text()
    except Exception as e:
        return f"Error reading artifact: {str(e)}"

def _write_artifact(path: str, content: str) -> str:
    """Core logic for writing an artifact."""
    try:
        brain = get_brain_path()
        target = brain / "artifacts" / path
        
        if not str(target.resolve()).startswith(str((brain / "artifacts").resolve())):
             return "Error: Access denied (path traversal)"
             
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing artifact: {str(e)}"

def _list_artifacts(folder: Optional[str] = None) -> List[str]:
    """Core logic for listing artifacts."""
    try:
        brain = get_brain_path()
        root = brain / "artifacts"
        if folder:
            root = root / folder
            
        if not root.exists():
            return []
            
        files = []
        for p in root.rglob("*"):
            if p.is_file():
                files.append(str(p.relative_to(brain / "artifacts")))
        return files[:50]
    except Exception as e:
        return []

def _trigger_agent(agent: str, task_description: str, context_files: List[str] = None) -> str:
    """Core logic for triggering an agent."""
    data = {
        "task_id": f"task-{int(time.time())}",
        "target_agent": agent,
        "description": task_description,
        "context_files": context_files or [],
        "status": "pending"
    }
    
    event_id = _emit_event(
        event_type="task_assigned",
        emitter="nucleus_mcp",
        data=data,
        description=f"Manual trigger for {agent}"
    )
    
    return f"Triggered {agent} with event {event_id}"

def _get_triggers() -> List[Dict]:
    """Core logic for getting all triggers."""
    try:
        brain = get_brain_path()
        triggers_path = brain / "ledger" / "triggers.json"
        
        if not triggers_path.exists():
            return []
            
        with open(triggers_path, "r") as f:
            triggers_data = json.load(f)
        
        # Return list of trigger definitions
        return triggers_data.get("triggers", [])
    except Exception as e:
        logger.error(f"Error reading triggers: {e}")
        return []

def _evaluate_triggers(event_type: str, emitter: str) -> List[str]:
    """Core logic for evaluating which agents should activate."""
    try:
        triggers = _get_triggers()
        matching_agents = []
        
        for trigger in triggers:
            # Check if this trigger matches the event
            if trigger.get("event_type") == event_type:
                # Check emitter filter if specified
                emitter_filter = trigger.get("emitter_filter")
                if emitter_filter is None or emitter in emitter_filter:
                    matching_agents.append(trigger.get("target_agent"))
        
        return list(set(matching_agents))  # Dedupe
    except Exception as e:
        logger.error(f"Error evaluating triggers: {e}")
        return []

# ============================================================
# MCP TOOL WRAPPERS (Registration layer)
# ============================================================

@mcp.tool()
def brain_emit_event(event_type: str, emitter: str, data: Dict[str, Any], description: str = "") -> str:
    """Emit a new event to the brain ledger."""
    return _emit_event(event_type, emitter, data, description)

@mcp.tool()
def brain_read_events(limit: int = 10) -> List[Dict]:
    """Read the most recent events from the ledger."""
    return _read_events(limit)

@mcp.tool()
def brain_get_state(path: Optional[str] = None) -> Dict:
    """Get the current state of the brain."""
    return _get_state(path)

@mcp.tool()
def brain_update_state(updates: Dict[str, Any]) -> str:
    """Update the brain state with new values (shallow merge)."""
    return _update_state(updates)

@mcp.tool()
def brain_read_artifact(path: str) -> str:
    """Read contents of an artifact file (relative to .brain/artifacts)."""
    return _read_artifact(path)

@mcp.tool()
def brain_write_artifact(path: str, content: str) -> str:
    """Write contents to an artifact file."""
    return _write_artifact(path, content)

@mcp.tool()
def brain_list_artifacts(folder: Optional[str] = None) -> List[str]:
    """List artifacts in a folder."""
    return _list_artifacts(folder)

@mcp.tool()
def brain_trigger_agent(agent: str, task_description: str, context_files: List[str] = None) -> str:
    """Trigger an agent by emitting a task_assigned event."""
    return _trigger_agent(agent, task_description, context_files)

@mcp.tool()
def brain_get_triggers() -> List[Dict]:
    """Get all defined neural triggers from triggers.json."""
    return _get_triggers()

@mcp.tool()
def brain_evaluate_triggers(event_type: str, emitter: str) -> List[str]:
    """Evaluate which agents should activate for a given event type and emitter."""
    return _evaluate_triggers(event_type, emitter)

# ============================================================
# MCP RESOURCES (Subscribable data)
# ============================================================

@mcp.resource("brain://state")
def resource_state() -> str:
    """Live state.json content - subscribable."""
    state = _get_state()
    return json.dumps(state, indent=2)

@mcp.resource("brain://events")
def resource_events() -> str:
    """Recent events - subscribable."""
    events = _read_events(limit=20)
    return json.dumps(events, indent=2)

@mcp.resource("brain://triggers")
def resource_triggers() -> str:
    """Trigger definitions - subscribable."""
    triggers = _get_triggers()
    return json.dumps(triggers, indent=2)

@mcp.resource("brain://context")
def resource_context() -> str:
    """Full context for cold start - auto-visible in sidebar. Click this first in any new session."""
    try:
        brain = get_brain_path()
        state = _get_state()
        sprint = state.get("current_sprint", {})
        agents = state.get("active_agents", [])
        actions = state.get("top_3_leverage_actions", [])
        
        # Format actions
        actions_text = ""
        if actions:
            for i, action in enumerate(actions[:3], 1):
                if isinstance(action, dict):
                    actions_text += f"  {i}. {action.get('action', 'Unknown')}\n"
                else:
                    actions_text += f"  {i}. {action}\n"
        else:
            actions_text = "  (None set)"
        
        # Recent events
        events = _read_events(limit=3)
        events_text = ""
        for evt in events:
            events_text += f"  - {evt.get('type', 'unknown')}: {evt.get('description', '')[:50]}\n"
        if not events_text:
            events_text = "  (No recent events)"
        
        # Check for workflow
        workflow_hint = ""
        workflow_path = brain / "workflows" / "lead_agent_model.md"
        if workflow_path.exists():
            workflow_hint = "📋 Workflow: Read .brain/workflows/lead_agent_model.md for coordination rules"
        
        return f"""# Nucleus Brain Context

## Current Sprint
- Name: {sprint.get('name', 'No active sprint')}
- Focus: {sprint.get('focus', 'Not set')}
- Status: {sprint.get('status', 'Unknown')}

## Active Agents
{', '.join(agents) if agents else 'None'}

## Top Priorities
{actions_text}
## Recent Activity
{events_text}
{workflow_hint}

---
You are the Lead Agent. Use brain_* tools to explore and act."""
    except Exception as e:
        return f"Error loading context: {str(e)}"

# ============================================================
# MCP PROMPTS (Pre-built orchestration)
# ============================================================

@mcp.prompt()
def activate_synthesizer() -> str:
    """Activate Synthesizer agent to orchestrate the current sprint."""
    state = _get_state()
    sprint = state.get("current_sprint", {})
    return f"""You are the Synthesizer, the orchestrating intelligence of this Nuclear Brain.

Current Sprint: {sprint.get('name', 'Unknown')}
Focus: {sprint.get('focus', 'Unknown')}

Your job is to:
1. Review the current state and recent events
2. Determine which agents need to be activated
3. Emit appropriate task_assigned events

Use the available brain_* tools to coordinate the agents."""

@mcp.prompt()
def start_sprint(goal: str = "MVP Launch") -> str:
    """Initialize a new sprint with the given goal."""
    return f"""Initialize a new sprint with goal: {goal}

Steps:
1. Use brain_update_state to set current_sprint with name, focus, and start date
2. Use brain_emit_event to emit a sprint_started event
3. Identify top 3 leverage actions and emit task_assigned events for each

Goal: {goal}"""

@mcp.prompt()
def cold_start() -> str:
    """Get instant context when starting a new session. Call this first in any new conversation."""
    try:
        brain = get_brain_path()
        state = _get_state()
        sprint = state.get("current_sprint", {})
        agents = state.get("active_agents", [])
        actions = state.get("top_3_leverage_actions", [])
        
        # Format top actions
        actions_text = ""
        if actions:
            for i, action in enumerate(actions[:3], 1):
                if isinstance(action, dict):
                    actions_text += f"{i}. {action.get('action', 'Unknown')}\n"
                else:
                    actions_text += f"{i}. {action}\n"
        else:
            actions_text = "None set - check state.json"
        
        # Recent events
        events = _read_events(limit=5)
        events_text = ""
        for evt in events[-3:]:  # Show last 3
            evt_type = evt.get('type', 'unknown')
            evt_desc = evt.get('description', '')[:40]
            events_text += f"- {evt_type}: {evt_desc}\n"
        if not events_text:
            events_text = "(No recent events)"
        
        # Check for workflow
        workflow_hint = ""
        workflow_path = brain / "workflows" / "lead_agent_model.md"
        if workflow_path.exists():
            workflow_hint = "\n📋 **Coordination:** Read `.brain/workflows/lead_agent_model.md` for multi-tool rules."
        
        # Recent artifacts
        artifacts = _list_artifacts()[:5]
        artifacts_text = ", ".join([a.split("/")[-1] for a in artifacts]) if artifacts else "None"
        
        return f"""# Nucleus Cold Start

You are now connected to a Nucleus Brain.

## Current State
- **Sprint:** {sprint.get('name', 'No active sprint')}
- **Focus:** {sprint.get('focus', 'Not set')}
- **Status:** {sprint.get('status', 'Unknown')}
- **Active Agents:** {', '.join(agents) if agents else 'None'}

## Top Priorities
{actions_text}
## Recent Activity
{events_text}
## Recent Artifacts
{artifacts_text}
{workflow_hint}

---

## Your Role
You are now the **Lead Agent** for this session.
- No strict role restrictions - you can do code, strategy, research
- Use brain_* tools to read/write state and artifacts
- Emit events to coordinate with other agents

What would you like to work on?"""
    except Exception as e:
        return f"""# Nucleus Cold Start

⚠️ Could not load brain state: {str(e)}

Make sure NUCLEAR_BRAIN_PATH is set correctly.

You can still use brain_* tools to explore the brain manually."""

def main():
    # Helper to log to debug file
    def log_debug(msg):
        with open("/tmp/mcp_debug.log", "a") as f:
            f.write(f"{msg}\n")
    
    try:
        log_debug("Entering mcp.run()")
        mcp.run()
        log_debug("Exited mcp.run() normally")
    except Exception as e:
        log_debug(f"Exception in mcp.run(): {e}")
        import traceback
        with open("/tmp/mcp_debug.log", "a") as f:
            traceback.print_exc(file=f)
        raise

if __name__ == "__main__":
    main()
