# Skills Installation Guide

## Overview

Skills are reusable workflows that agents can discover and execute. This guide explains how to install and use skills in filesystem-first mode.

## Anthropic Official Skills

### One-Time Installation

Download official skills from the Anthropic repository once, then symlink them to your projects:

```bash
# 1. Clone the official skills repository
git clone https://github.com/anthropics/skills ~/.massgen/anthropic-skills

# 2. Skills are now available globally at:
#    ~/.massgen/anthropic-skills/
```

### Skills Structure

Each skill follows the SKILL.md format:

```
~/.massgen/anthropic-skills/
├── README.md
├── webapp-testing/
│   ├── SKILL.md          # Main skill definition
│   ├── references/       # Documentation
│   └── scripts/          # Helper scripts
├── api-client-generator/
│   ├── SKILL.md
│   └── templates/
└── data-analysis/
    ├── SKILL.md
    └── assets/
```

### Auto-Symlinking (Planned Feature)

When filesystem-first mode initializes, it will automatically symlink installed skills:

```yaml
massgen:
  execution_mode: "filesystem_first"
  skills:
    install_anthropic_skills: true
    skills_directory: "~/.massgen/anthropic-skills"
```

This creates:
```
.massgen/workspace/skills/community/
├── webapp-testing -> ~/.massgen/anthropic-skills/webapp-testing
├── api-client-generator -> ~/.massgen/anthropic-skills/api-client-generator
└── data-analysis -> ~/.massgen/anthropic-skills/data-analysis
```

## Manual Installation (Current)

Until auto-installation is implemented, manually symlink skills:

```bash
# From your project directory
mkdir -p .massgen/workspace/skills/community

# Symlink desired skills
ln -s ~/.massgen/anthropic-skills/webapp-testing \
      .massgen/workspace/skills/community/webapp-testing

ln -s ~/.massgen/anthropic-skills/api-client-generator \
      .massgen/workspace/skills/community/api-client-generator
```

## Using Skills

### Discovery

Agents can discover skills using filesystem operations:

```python
# List all community skills
import os
skills = os.listdir("skills/community/")
print(f"Available skills: {skills}")

# Search for specific skills
!rg "testing" skills/ -i -l
```

### Reading Skills

```python
# Read a skill's main definition
with open("skills/community/webapp-testing/SKILL.md") as f:
    skill_content = f.read()
    print(skill_content)

# Or use the runtime helper (when implemented)
from _massgen_runtime import read_skill
skill = read_skill("webapp-testing", location="community")
print(skill["instructions"])
```

### Creating Custom Skills

Agents can create their own skills:

```python
from _massgen_runtime import save_skill

save_skill(
    name="my-workflow",
    description="Brief description of what this skill does",
    instructions="""
# My Workflow Skill

## When to Use
Use this skill when...

## Instructions
1. First step
2. Second step

## Examples
\`\`\`python
from servers.github import list_repositories
repos = await list_repositories()
\`\`\`
    """,
    community=True  # Share with all agents
)
```

## Skill Categories

### Official Anthropic Skills

Common skills you should install:

1. **webapp-testing** - Test web applications with Playwright
2. **api-client-generator** - Generate API clients from OpenAPI specs
3. **data-analysis** - Analyze datasets and create visualizations
4. **code-refactoring** - Refactor code with best practices
5. **documentation-writer** - Generate comprehensive documentation
6. **debugging** - Debug complex issues systematically

### Agent-Specific Skills

Each agent can create private skills in `skills/{agent_id}/`:

```
.massgen/workspace/skills/
├── community/           # Shared skills (from Anthropic or agents)
├── research_agent/      # Private to research_agent
└── coding_agent/        # Private to coding_agent
```

## Best Practices

### Version Control

Keep your skill installation versioned:

```bash
# Pin to specific version
cd ~/.massgen/anthropic-skills
git checkout v1.0.0  # Or latest stable tag
```

### Updating Skills

```bash
# Update to latest
cd ~/.massgen/anthropic-skills
git pull origin main

# Note: Symlinks automatically reflect updates
```

### Sharing Custom Skills

To share a custom skill with the community:

1. Create the skill in your agent's directory:
   ```python
   save_skill("my-skill", ..., community=False)
   ```

2. Test it thoroughly

3. Promote to community:
   ```bash
   cp -r .massgen/workspace/skills/my_agent/my-skill \
         .massgen/workspace/skills/community/my-skill
   ```

4. Optional: Submit to anthropics/skills repository

## Troubleshooting

### Skills Not Appearing

Check symlinks exist:
```bash
ls -la .massgen/workspace/skills/community/
```

### Skills Not Readable

Ensure permissions:
```bash
chmod -R +r ~/.massgen/anthropic-skills
```

### Outdated Skills

Update the repository:
```bash
cd ~/.massgen/anthropic-skills && git pull
```

## Future Features (Planned)

- **Auto-installation**: Automatic cloning of anthropics/skills on first run
- **Skill marketplace**: Browse and install community skills
- **Skill versioning**: Specify skill versions in config
- **Skill dependencies**: Skills can depend on other skills
- **Skill testing**: Built-in testing framework for skills

## References

- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [SKILL.md Specification](https://docs.anthropic.com/skills/specification)
- [Filesystem-First Design Doc](../../../docs/dev_notes/filesystem_tool_discovery_design.md)
