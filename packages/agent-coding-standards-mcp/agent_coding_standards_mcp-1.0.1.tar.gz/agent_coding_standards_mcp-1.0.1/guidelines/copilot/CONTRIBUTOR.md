# Copilot Contributor Guide

## Folder Structure

```
guidelines/copilot/
├── agents/          → Personas (NOUN)
├── instructions/    → Standards (NOUN)
└── prompts/         → Actions (VERB, imperative)
```

## Core Concepts

| Folder | Concept | Grammar | Extension | Example |
|--------|---------|---------|-----------|---------|
| `agents/` | WHO performs tasks | NOUN | `.agent.md` | `planner.agent.md` |
| `instructions/` | WHAT standards apply | NOUN | `.instructions.md` | `comment-rules.instructions.md` |
| `prompts/` | WHAT actions to execute | VERB | `.prompt.md` | `write-document.prompt.md` |

## Global Rules

- **kebab-case** required for all names
- **No gerunds** allowed
- **Mandatory file extensions** in filename
- **Dot separator** (`.`) between name and type
- **No overlap** between agents, instructions, and prompts
- **One concept per file**
- **YAML frontmatter required** for agents and prompts

## YAML Frontmatter Requirements

### Required Fields

Agents and prompts must include at minimum:

```yaml
---
name: string
description: string
---
```

### Optional Fields

```yaml
---
name: string
description: string
argument-hint: string
tools: [array]
handoffs: [array]
---
```

### Agents Example

```yaml
---
name: planner
description: AI agent that creates project plans
tools: ['search', 'edit']
---
```

### Prompts Example

```yaml
---
name: write-document
description: Generalize discussion into reusable prompt
tools: ['edit', 'search']
---
```

### Instructions

Instructions files typically do not require YAML frontmatter, but may include it for metadata purposes.

## Extension Format

All files **must** follow this pattern:

```
{name}.{type}.md
```

Where `{type}` is exactly:
- `agent`
- `instructions`
- `prompt`

## Folder-Specific Rules

### Agents

- Must be **nouns** describing roles or personas
- Filename format: `{role-name}.agent.md`
- Extension `.agent.md` is **mandatory**
- **YAML frontmatter required** with `name` and `description`

### Instructions

- Must be **nouns** describing standards or constraints
- Filename format: `{standard-name}.instructions.md`
- Extension `.instructions.md` is **mandatory**
- YAML frontmatter optional

### Prompts

- Must be **verbs** in imperative form
- Filename format: `{action}.prompt.md`
- Extension `.prompt.md` is **mandatory**
- Use base verb form (`plan`, not `planning` or `plans`)
- **YAML frontmatter required** with `name` and `description`

## Grammar Matrix

| Folder | Valid | Invalid |
|--------|-------|---------|
| `agents/` | `planner.agent.md` | `planning.agent.md` ❌ |
| `agents/` | `reviewer.agent.md` | `review.agent.md` ❌ (verb) |
| `instructions/` | `comment-rules.instructions.md` | `commenting.instructions.md` ❌ |
| `prompts/` | `write-document.prompt.md` | `document-writer.prompt.md` ❌ (noun) |

## Invalid Patterns

```
agents/planner.md                           ❌ missing extension
agents/planner-agent.md                     ❌ hyphen instead of dot
agents/planner.Agent.md                     ❌ capitalized extension
instructions/comment-rules.md               ❌ missing extension
prompts/write_document.prompt.md            ❌ snake_case
prompts/writing-document.prompt.md          ❌ gerund
agents/reviewer.instruction.md              ❌ wrong extension
```

## Extension Validation

Files without correct extensions are **invalid** and will not be loaded:

| Filename | Status | Reason |
|----------|--------|--------|
| `planner.agent.md` | ✓ Valid | Correct format |
| `planner.md` | ✗ Invalid | Missing `.agent` |
| `planner-agent.md` | ✗ Invalid | Hyphen instead of dot |
| `planner.agents.md` | ✗ Invalid | Wrong extension |

## Pre-PR Checklist

- [ ] Agent files are nouns with `.agent.md` extension
- [ ] Agent files have YAML frontmatter with `name` and `description`
- [ ] Instruction files are nouns with `.instructions.md` extension
- [ ] Prompt files are imperative verbs with `.prompt.md` extension
- [ ] Prompt files have YAML frontmatter with `name` and `description`
- [ ] Extensions use dot separator (`.`), not hyphen (`-`)
- [ ] No gerunds in any filename
- [ ] All names use kebab-case
- [ ] No concept appears in multiple folders
