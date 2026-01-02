
---

# Claude Contributor Guide

## Folder Structure

```
guidelines/claude/
├── agents/          → Personas (NOUN)
├── commands/        → Actions (VERB, imperative)
└── skills/          → Knowledge domains (NOUN)
    └── {domain}/
        ├── SKILL.md
        └── references/  (optional)
```

## Core Concepts

| Folder | Concept | Grammar | Example |
|--------|---------|---------|---------|
| `agents/` | WHO performs tasks | NOUN | `planner.md` |
| `commands/` | WHAT is executed | VERB (imperative) | `plan.md` |
| `skills/` | WHAT expertise applies | NOUN | `backend-development/` |

## Global Rules

- **kebab-case** required for all names
- **No gerunds** allowed
- **No overlap** between agents, commands, and skills
- **One concept per file**
- **YAML frontmatter required** for all files

## YAML Frontmatter Requirements

### Required Fields

All agents, commands, and skills must include:

```yaml
---
name: string
description: string
---
```

### Agents Example

```yaml
---
name: planner
description: AI agent that creates project plans
---
```

### Commands Example

```yaml
---
name: plan
description: Researches and outlines multi-step plans
---
```

### Skills Example

```yaml
---
name: backend-development
description: Expert knowledge in backend API design and implementation
---
```

## Folder-Specific Rules

### Agents

- Must be **nouns** describing roles or personas
- Filename format: `{role-name}.md`
- **YAML frontmatter required** with `name` and `description`

### Commands

- Must be **verbs** in imperative form
- Filename format: `{action}.md`
- Use base verb form (`plan`, not `planning` or `plans`)
- **YAML frontmatter required** with `name` and `description`

### Skills

- Must be **nouns** describing knowledge domains
- Each skill is a **folder** containing:
  - `SKILL.md` (uppercase, required)
  - `references/` (lowercase, optional)
- References must be **nouns**
- Reference filename format: `{domain}-{topic}.md`
- **YAML frontmatter required** in `SKILL.md` with `name` and `description`
- References may optionally include frontmatter

## Grammar Matrix

| Folder | Valid | Invalid |
|--------|-------|---------|
| `agents/` | `database-admin` | `administering-database` ❌ |
| `commands/` | `review-code` | `code-reviewing` ❌ |
| `commands/` | `plan` | `planner` ❌ (noun) |
| `skills/` | `backend-development` | `develop-backend` ❌ (verb) |
| `skills/{domain}/references/` | `backend-testing` | `test-backend` ❌ (verb) |

## Invalid Patterns

```
agents/planning.md                    ❌ gerund
commands/planner.md                   ❌ noun instead of verb
skills/backend-development.md         ❌ file instead of folder
skills/backend-development/skill.md   ❌ lowercase
skills/backend-development/Skill.md   ❌ PascalCase
agents/database_admin.md              ❌ snake_case
```

## Pre-PR Checklist

- [ ] Agent files are nouns with YAML frontmatter
- [ ] Agent frontmatter includes `name` and `description`
- [ ] Command files are imperative verbs with YAML frontmatter
- [ ] Command frontmatter includes `name` and `description`
- [ ] Skill folders contain uppercase `SKILL.md`
- [ ] `SKILL.md` has YAML frontmatter with `name` and `description`
- [ ] References are nouns if present
- [ ] No gerunds in any filename
- [ ] All names use kebab-case
- [ ] No concept appears in multiple folders
