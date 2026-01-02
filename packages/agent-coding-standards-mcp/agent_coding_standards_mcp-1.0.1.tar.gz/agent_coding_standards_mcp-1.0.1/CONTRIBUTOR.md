# Contributing to Agent Coding Standard Guidelines

## Repository Purpose

This repository defines **coding standards and structural guidelines** for AI agent configurations across multiple platforms.

Contributors establish **naming conventions**, **file organization rules**, and **grammar-based constraints** to ensure consistency across agent definitions.

## Core Principles

All agent configuration files follow universal rules:

- **kebab-case** for all filenames and folder names
- **One concept per file**
- **No gerunds** (`-ing` forms are forbidden)
- **Grammar-based naming**: folders define whether contents are NOUNS or VERBS

## Naming Rules

### Kebab-case Format

All names must use lowercase letters separated by hyphens:

```
valid-filename.md
multi-word-concept.md
```

### Grammar Constraints

Each folder enforces a grammatical category:

| Category | Rule | Example |
|----------|------|---------|
| NOUN | Entities, roles, domains | `database-admin`, `api-design` |
| VERB | Actions, commands, procedures | `plan`, `review-code` |

### Forbidden Patterns

```
analyzing.md          ❌ gerund
DatabaseAdmin.md      ❌ PascalCase
api_design.md         ❌ snake_case
reviewing-code.md     ❌ gerund in verb context
```

## Repository Structure

```
guidelines/
├── claude/          → Claude AI agent standards
├── cline/           → Cline agent standards
└── copilot/         → GitHub Copilot agent standards
```

## Platform-Specific Standards

Each AI platform has unique requirements for **file extensions**, **frontmatter formats**, and **folder semantics**.

Refer to platform-specific coding standards:

- [Claude coding standards](guidelines/claude/CONTRIBUTOR.md)
- [Cline coding standards](guidelines/cline/CONTRIBUTOR.md)
- [Copilot coding standards](guidelines/copilot/CONTRIBUTOR.md)

## Contribution Scope

When contributing agent configurations:

- Follow the **naming and grammar rules** defined here
- Respect **platform-specific constraints** in subdirectories
- Ensure **no concept duplication** within a platform
- Maintain **self-contained, single-purpose files**

## Validation Checklist

Before submitting:

- [ ] All filenames use kebab-case
- [ ] No gerunds in any filename
- [ ] Grammar rules match folder requirements
- [ ] No duplicate concepts across folders
- [ ] Platform-specific constraints are satisfied
