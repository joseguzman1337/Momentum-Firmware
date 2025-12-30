# Agent Skills Configuration for Momentum Firmware

This directory contains Agent Skills for the Momentum Firmware project. Skills are loaded automatically by Codex and provide specialized capabilities for Flipper Zero development.

## Available Skills

### Core Skills
- **skill-creator**: Bootstrap new skills with proper structure
- **momentum-app-creator**: Create new Flipper Zero applications
- **flipper-debug**: Debug applications and firmware issues
- **subghz-analyzer**: Analyze and develop Sub-GHz protocols

## Usage

Skills can be invoked in two ways:

1. **Explicit**: Use `/skills` command or type `$skill-name` in prompts
2. **Implicit**: Codex automatically selects relevant skills based on context

## Skill Development

To create new skills:
1. Use `$skill-creator` to bootstrap the structure
2. Follow the Agent Skills specification
3. Test with actual Momentum Firmware development tasks
4. Document any Flipper Zero specific requirements

## Integration

Skills are automatically loaded from:
- `.codex/skills/` (repository level)
- `~/.codex/skills/` (user level)
- System level skills (bundled with Codex)

Repository skills take precedence and can override system skills.