# Cline Contributor Guide

## Folder Structure

```
guidelines/cline/
├── workflows/       → Actions (VERB, imperative)
└── rules/           → Standards (NOUN)
```

## Core Concepts

| Folder | Concept | Grammar | Example |
|--------|---------|---------|---------|
| `workflows/` | WHAT procedures to execute | VERB (imperative) | `review-code.md` |
| `rules/` | WHAT standards to follow | NOUN | `common-rules.md` |

## Global Rules

- **kebab-case** required for all names
- **No gerunds** allowed
- **No overlap** between workflows and rules
- **One concept per file**
- **YAML frontmatter required** for all files

## YAML Frontmatter Requirements

### Required Fields

All workflows and rules must include:

```yaml
---
name: string
description: string
---
```

### Workflows Example

```yaml
---
name: review-code
description: Step-by-step code review procedure
---
```

### Rules Example

```yaml
---
name: common-rules
description: Shared coding standards across all projects
---
```

## Folder-Specific Rules

### Workflows

- Must be **verbs** in imperative form
- Must describe **procedural steps**
- Filename format: `{action}.md`
- Use base verb form (`plan`, not `planning` or `plans`)
- Content must be step-by-step instructions
- **YAML frontmatter required** with `name` and `description`

### Rules

- Must be **nouns** describing standards or constraints
- Must be **declarative statements**
- Filename format: `{standard-name}.md`
- Content must define requirements, not procedures
- **YAML frontmatter required** with `name` and `description`

## Grammar Matrix

| Folder | Valid | Invalid |
|--------|-------|---------|
| `workflows/` | `write-document` | `document-writing` ❌ |
| `workflows/` | `review-code` | `code-reviewer` ❌ (noun) |
| `rules/` | `common-rules` | `apply-rules` ❌ (verb) |
| `rules/` | `coding-standards` | `standardizing-code` ❌ (gerund) |

## Invalid Patterns

```
workflows/planning.md                 ❌ gerund
workflows/document-writer.md          ❌ noun instead of verb
rules/review-code.md                  ❌ verb instead of noun
rules/applying-standards.md           ❌ gerund
workflows/Write-Document.md           ❌ PascalCase
rules/common_rules.md                 ❌ snake_case
```

## Pre-PR Checklist

- [ ] Workflow files are imperative verbs
- [ ] Workflow content is procedural
- [ ] Workflow files have YAML frontmatter with `name` and `description`
- [ ] Rule files are nouns
- [ ] Rule content is declarative
- [ ] Rule files have YAML frontmatter with `name` and `description`
- [ ] No gerunds in any filename
- [ ] All names use kebab-case
- [ ] No concept appears in both folders
