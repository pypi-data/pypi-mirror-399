# Filesystem-First Mode - Implementation Guide

This document explains how the filesystem-first mode works and how to use it.

## Overview

Filesystem-first mode is a paradigm shift where tools are represented as **files in the filesystem** rather than injected into context. Agents discover tools using CLI primitives (ripgrep, ast-grep) and execute them via code.

**Key Benefits:**
- 98% context reduction (150K → 3K tokens)
- Attach 100+ MCP servers with zero context cost
- Agents discover tools on-demand
- One universal config works for any task

## Workspace Structure

When filesystem-first mode is enabled, MassGen creates this structure:

```
/massgen_workspace/                    # Shared workspace root
├── servers/                           # MCP tool files (SHARED, read-only)
│   ├── filesystem/
│   │   ├── read_file.py
│   │   ├── write_file.py
│   │   └── __init__.py
│   ├── google-drive/
│   │   ├── getDocument.py
│   │   └── __init__.py
│   └── ...
├── tools/                             # Custom tool files (SHARED, read-only)
│   ├── web/
│   │   ├── playwright_navigate.py
│   │   └── __init__.py
│   └── multimodal/
│       ├── vision_understanding.py
│       └── __init__.py
├── skills/                            # Reusable workflows
│   ├── community/                     # SHARED (read/write)
│   │   ├── README.md
│   │   ├── webapp-testing/
│   │   │   ├── SKILL.md
│   │   │   └── references/
│   │   └── skill-creator/
│   │       └── SKILL.md
│   └── agent_a/                       # Per-agent skills
│       └── my-workflow/
│           └── SKILL.md
└── agents/                            # Per-agent directories
    ├── agent_a/
    │   ├── workspace/  -> temp_workspaces/agent_a/
    │   ├── memory/                    # Persistent memory
    │   │   ├── core_memories.json
    │   │   └── task_history.json
    │   └── tasks/                     # Task planning
    └── agent_b/
        └── ...
```

## How Agents See the Workspace

From each agent's perspective (via symlinks in their workspace):

```
/workspace/                            # Agent's working directory
├── servers/ -> /massgen_workspace/servers/
├── tools/ -> /massgen_workspace/tools/
├── skills/ -> /massgen_workspace/skills/
├── memory/ -> /massgen_workspace/agents/agent_a/memory/
└── ... (agent's working files)
```

## Agent Workflow Example

### Task: "Analyze Q4 sales and send summary to #sales"

**1. Discover relevant tools using ripgrep:**

```python
# Agent code (executed in Docker container)
import subprocess

# Find sales-related tools
result = subprocess.run(
    ["rg", "sales|revenue|crm", "servers/", "-i", "-l"],
    capture_output=True,
    text=True
)
print(result.stdout)
# Output:
# servers/salesforce/query_records.py
# servers/stripe/list_charges.py
# servers/hubspot/get_deals.py

# Find messaging tools
result = subprocess.run(
    ["rg", "send|message|slack", "servers/", "-i", "-l"],
    capture_output=True,
    text=True
)
print(result.stdout)
# Output:
# servers/slack/post_message.py
```

**2. Read only the needed tool definitions:**

```python
# Agent reads just 2 files out of 200+ available
with open("servers/salesforce/query_records.py") as f:
    print(f.read())

with open("servers/slack/post_message.py") as f:
    print(f.read())
```

**3. Write code using discovered tools:**

```python
from servers.salesforce import query_records
from servers.slack import post_message

# Fetch Q4 sales data
q4_data = await query_records(
    query="SELECT Amount FROM Opportunity WHERE CloseDate >= 2024-10-01"
)

# Analyze
total_revenue = sum(record["Amount"] for record in q4_data)
summary = f"Q4 Revenue: ${total_revenue:,.2f}"

# Send to Slack
await post_message(channel="#sales", text=summary)
```

**Result:** Task completed using only 2 tools (out of 200+) with ~3K token context!

## Tool File Format

Each tool is a Python file with typed interface and runtime bridge:

```python
# servers/google-drive/getDocument.py
"""Fetch a document from Google Drive.

MCP Server: google-drive
Tool: getDocument
"""

from typing import Dict, Any

async def getDocument(documentId: str) -> Dict[str, Any]:
    """Fetch a document from Google Drive.

    Args:
        documentId: The ID of the document to fetch

    Returns:
        Tool execution result as dictionary

    Raises:
        PermissionError: If agent not authorized
        RuntimeError: If tool execution fails
    """
    from _massgen_runtime import call_mcp_tool

    result = await call_mcp_tool(
        server="google-drive",
        tool="getDocument",
        arguments={"documentId": documentId}
    )

    return result
```

## Skills System

Skills are reusable workflows saved in SKILL.md format:

```markdown
---
name: webapp-testing
description: Test web applications with Playwright
---

# Web Application Testing Skill

## Instructions
When testing a web app:
1. Navigate to the URL using playwright_navigate
2. Take screenshots
3. Check console for errors

## Examples
\`\`\`python
from tools.web import playwright_navigate
result = await playwright_navigate(url="https://example.com", screenshot=True)
\`\`\`
```

**Using skills:**

```python
# Discover skills
import os
skills = os.listdir("skills/community/")

# Read a skill
with open("skills/community/webapp-testing/SKILL.md") as f:
    instructions = f.read()

# Or use helper
from _massgen_runtime import read_skill
skill = read_skill("webapp-testing")
print(skill["instructions"])
```

**Creating skills:**

```python
from _massgen_runtime import save_skill

save_skill(
    name="my-workflow",
    description="Custom workflow for data analysis",
    instructions="""
# Data Analysis Workflow

1. Fetch data from database
2. Process with pandas
3. Generate visualizations
    """,
    community=True  # Share with other agents
)
```

## Memory System

Each agent has a persistent `memory/` directory:

```python
import json

# Read memory
with open("memory/core_memories.json") as f:
    memories = json.load(f)

# Write memory
memories["learned_patterns"].append("use ripgrep for fast search")
with open("memory/core_memories.json", "w") as f:
    json.dump(memories, f, indent=2)

# Search memory with ripgrep
import subprocess
result = subprocess.run(
    ["rg", "database optimization", "memory/", "-i"],
    capture_output=True,
    text=True
)
```

## Configuration

See `filesystem_first_basic.yaml` and `filesystem_first_universal.yaml` for examples.

**Minimal config:**

```yaml
massgen:
  execution_mode: "filesystem_first"

  in_context_tools:
    filesystem: [read_file, write_file, list_directory]
    code_execution: [execute_python, execute_bash]

  available_mcp_servers:
    - google-drive
    - github
    # ... add as many as you want!

agents:
  - id: "agent"
    backend:
      type: "openai"
      model: "gpt-4o"
      enable_mcp_command_line: true
      command_line_execution_mode: "docker"
```

## Initialization Process

When MassGen starts with `execution_mode: "filesystem_first"`:

1. **Create workspace structure** - servers/, tools/, skills/, agents/
2. **Generate MCP tool files** - Parse schemas, create Python files
3. **Generate custom tool files** - Create typed wrappers
4. **Initialize skills** - Set up community/ and per-agent directories
5. **Create agent directories** - memory/, workspace/, tasks/
6. **Create symlinks** - Link shared resources into agent workspaces
7. **Validate search tools** - Check ripgrep and ast-grep availability

## Search Tool Requirements

Filesystem-first mode requires these CLI tools in the Docker container:

- **ripgrep** (`rg`) - Fast text search (REQUIRED)
- **ast-grep** (`ast-grep` or `sg`) - Structural code search (RECOMMENDED)
- **semtools** - Semantic search (OPTIONAL, future)

Install in Dockerfile:

```dockerfile
# Install ripgrep
RUN apt-get update && apt-get install -y ripgrep

# Install ast-grep
RUN cargo install ast-grep --locked
```

## Runtime Functions

Agents have access to these runtime functions:

```python
from _massgen_runtime import (
    call_mcp_tool,        # Execute MCP tool
    call_custom_tool,     # Execute custom tool
    save_skill,           # Save workflow as skill
    read_skill,           # Read skill instructions
    list_skills,          # List available skills
    get_skill_resource,   # Access skill resources
    get_memory_path,      # Get agent's memory directory
    get_agent_id,         # Get current agent ID
)
```

## Comparison: Context-Based vs Filesystem-First

| Aspect | Context-Based | Filesystem-First |
|--------|---------------|------------------|
| Max MCP servers | 5-10 | **100+** |
| Context cost | ~150K tokens | **~3K tokens** |
| Tool discovery | Manual config | **Automatic (search)** |
| Tool composition | Chain tool calls | **Write code** |
| Scalability | Limited by context | **Unlimited** |
| Skill reuse | No | **Yes** |
| Memory | Dedicated API | **Filesystem** |

## Troubleshooting

### "execution_mode: 'filesystem_first' requires code execution"

**Solution:** Enable code execution in agent backend:

```yaml
agents:
  - backend:
      enable_mcp_command_line: true
      command_line_execution_mode: "docker"
```

### "Search tool 'ripgrep' is NOT available"

**Solution:** Update Docker image to include ripgrep:

```dockerfile
RUN apt-get update && apt-get install -y ripgrep
```

### Tools not found in filesystem

**Solution:** Check workspace initialization logs. Ensure MCP clients are connected before workspace initialization.

## Next Steps

1. Try the basic example: `massgen --config configs/examples/filesystem_first_basic.yaml`
2. Explore the universal workspace: `configs/examples/filesystem_first_universal.yaml`
3. Create your own skills and share with the community
4. Experiment with 50+ MCP servers and see the context savings!
