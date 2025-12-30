---
name: skill-creator
description: Create new Agent Skills for the Momentum Firmware project
metadata:
  short-description: Bootstrap new skills with proper structure
---

# Skill Creator

Create new Agent Skills for the Momentum Firmware project following the Agent Skills specification.

## Instructions

When creating a new skill:

1. Ask for the skill name and description
2. Create the skill directory structure in `.codex/skills/[skill-name]/`
3. Generate a proper `SKILL.md` file with:
   - YAML frontmatter with name and description
   - Clear instructions for the agent
   - Any necessary metadata
4. Create optional directories if needed:
   - `scripts/` for executable code
   - `references/` for documentation
   - `assets/` for templates and resources

## Skill Structure

```
.codex/skills/[skill-name]/
├── SKILL.md          # Required: instructions + metadata
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
└── assets/          # Optional: templates, resources
```

## SKILL.md Template

```markdown
---
name: skill-name
description: Brief description for skill selection
metadata:
  short-description: User-facing description
---

# Skill Name

Detailed instructions for the agent to follow when using this skill.

## Context
- Momentum Firmware project specifics
- Flipper Zero development environment

## Instructions
1. Step-by-step process
2. Expected outputs
3. Error handling
```

## Momentum-Specific Guidelines

- Skills should understand Flipper Zero hardware constraints
- Consider embedded C development patterns
- Reference existing project structure and conventions
- Include proper error handling for hardware operations