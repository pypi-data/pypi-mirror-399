# agent-coding-standards-mcp
This repository provides an MCP (Model Context Protocol) Server for managing AI coding agent guidelines, workflows, and rules.

## Table of Contents
- [agent-coding-standards-mcp](#agent-coding-standards-mcp)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Repository Structure](#repository-structure)
  - [Local Environment Setup](#local-environment-setup)
    - [Prerequisites](#prerequisites)
    - [Setup Steps](#setup-steps)
  - [Development](#development)
    - [Code Quality Management](#code-quality-management)
      - [Format](#format)
      - [Lint](#lint)
      - [Type Check](#type-check)
    - [Running Tests](#running-tests)
      - [Basic Test Execution](#basic-test-execution)
      - [Coverage Report](#coverage-report)
  - [Usage](#usage)
    - [Running the MCP Server](#running-the-mcp-server)
    - [Available Tools and Resources](#available-tools-and-resources)

## Overview
agent-coding-standards-mcp is an MCP Server that provides standardized guidelines, workflows, and rules for AI coding agents including Cline, Claude, and Copilot. It helps maintain consistent coding practices and development workflows across different AI agents.

## Repository Structure
- `guidelines/`: Contains AI agent-specific guidelines and configurations.
  - `cline/`: Guidelines and configurations for Cline AI agent.
    - `config/`: Configuration files for Cline.
    - `workflows/`: Workflow definitions for Cline.
    - `rules/`: Coding rules and standards for Cline.
  - `claude/`: Guidelines and configurations for Claude AI agent.
    - `config/`: Configuration files for Claude.
    - `workflows/`: Workflow definitions for Claude.
    - `rules/`: Coding rules and standards for Claude.
  - `copilot/`: Guidelines and configurations for GitHub Copilot.
    - `config/`: Configuration files for Copilot.
    - `workflows/`: Workflow definitions for Copilot.
    - `rules/`: Coding rules and standards for Copilot.
- `src/`: Contains all source code for the MCP server.
  - `mcp_server/`: Main MCP server package.
    - `tools/`: MCP tools implementation.
    - `services/`: Business logic and application services.
    - `models/`: Data models and schemas.
    - `utils/`: Utility functions and helpers.
- `tests/`: Contains test code for the application.
- `docs/`: Contains documentation and project plans.

## Local Environment Setup

### Prerequisites
- [mise](https://mise.jdx.dev/) must be installed
- Python 3.13+ is required

### Setup Steps
1. Clone the repository
```bash
git clone <repository-url>
cd agent-coding-standards-mcp
```

2. Set up the development environment
```bash
mise run setup
```

This command performs the following:
- Installs Python 3.13.3 and uv 0.7.18
- Creates a virtual environment
- Installs dependencies

3. Install pre-commit hooks
```bash
mise run pre-commit
```

## Development

### Code Quality Management

#### Format
```bash
mise run format
```
Uses ruff to automatically format the code.

#### Lint
```bash
mise run lint
```
Uses ruff to perform static code analysis and fix issues.

#### Type Check
```bash
mise run typecheck
```
Uses mypy to perform static type checking.

### Running Tests

#### Basic Test Execution
```bash
mise run test
```
Runs tests using pytest.

#### Coverage Report
```bash
mise run test-cov
```
Runs tests with coverage reporting and generates HTML coverage report.

## Usage

### Running the MCP Server
```bash
# Install the package
uv sync

# Run the MCP server
agent-mcp-server
```

### Available Tools and Resources
The MCP server provides tools and resources for:
- Managing AI agent coding guidelines
- Accessing workflow configurations
- Retrieving coding rules and standards
- Synchronizing agent configurations across different environments

For detailed information about available MCP tools and resources, refer to the server implementation in `src/mcp_server/`.