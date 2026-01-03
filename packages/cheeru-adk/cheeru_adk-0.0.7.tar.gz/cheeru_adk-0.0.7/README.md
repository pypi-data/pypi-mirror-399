# CheerU-ADK

**AI Portfolio Auto-Generation Framework for Job Seekers (Gemini CLI)**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/badge/pypi-v0.0.7-green.svg)](https://pypi.org/project/cheeru-adk/)

---

## What is CheerU-ADK?

**CheerU-ADK** (Cheer You - Agentic Development Kit) is an AI-powered portfolio auto-generation framework for developers preparing for employment.

With simple commands in the Gemini CLI environment:
- **Project Planning**: Automatically design projects tailored to your target job
- **Code Generation**: AI writes code step by step with TDD
- **GitHub Automation**: Generate meaningful commit history
- **Portfolio Documentation**: Automatically organize in portfolio format

---

## Installation

```bash
# Install with uv (recommended)
uv tool install cheeru-adk

# Or install with pip
pip install cheeru-adk
```

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Install & Initialize

```bash
# Create your portfolio project
mkdir my-portfolio && cd my-portfolio

# Initialize CheerU-ADK
cheeru-adk init
```

### Step 2: Open Gemini CLI

```bash
# Start Gemini CLI in your project
gemini
```

### Step 3: Start Planning

In Gemini CLI, type:
```
/cheeru-plan "로그인 기능이 있는 Todo App"
```

The AI will:
1. Analyze your project requirements
2. Break down into feature-level SPECs
3. Generate development roadmap

### Step 4: Create Feature SPEC

```
cheeru-adk spec new "이메일 로그인" --worktree
```

This creates:
- SPEC document (`.cheeru/specs/SPEC-001/spec.md`)
- Worktree for parallel development (after confirmation)

### Step 5: Start TDD Development

```bash
# In Gemini CLI
/cheeru-code
```

The AI will guide you through:
- **RED**: Write failing tests
- **GREEN**: Implement minimal code
- **REFACTOR**: Improve code quality

### Step 6: Commit & Document

```
/cheeru-commit
/cheeru-doc
```

---

## Workflow Commands

| Command          | Description                   |
| ---------------- | ----------------------------- |
| `/cheeru-start`  | Start a new portfolio project |
| `/cheeru-plan`   | Create feature-level SPECs    |
| `/cheeru-code`   | Generate code with TDD        |
| `/cheeru-commit` | Commit to GitHub              |
| `/cheeru-doc`    | Generate documentation        |
| `/cheeru-resume` | Resume previous session       |
| `/cheeru-issue`  | Create GitHub Issues          |

---

## Agent System (8 Agents)

CheerU-ADK uses 8 specialized AI agents:

| Agent              | Role         | Function                          |
| ------------------ | ------------ | --------------------------------- |
| `project-planner`  | CPO          | Project planning, SPEC generation |
| `code-generator`   | Orchestrator | Code generation coordination      |
| `code-reviewer`    | Auditor      | Code quality and review           |
| `test-engineer`    | QA + TDD     | TDD workflow, testing             |
| `backend-dev`      | Backend      | API, DB, server logic             |
| `frontend-dev`     | Frontend     | UI components                     |
| `devops-engineer`  | DevOps       | CI/CD, Git, deployment            |
| `technical-writer` | Docs         | README, API docs                  |

---

## CLI Commands

```bash
# Project
cheeru-adk init              # Initialize project
cheeru-adk status            # Show project status

# SPEC Management
cheeru-adk spec new "name"   # Create SPEC
cheeru-adk spec new "name" --worktree  # Create with worktree
cheeru-adk spec list         # List all SPECs

# TDD Workflow
cheeru-adk tdd start         # Start TDD
cheeru-adk tdd status        # Check TDD status

# Worktree (Parallel Development)
cheeru-adk worktree list     # List worktrees
cheeru-adk worktree merge    # Merge completed work

# Task Management
cheeru-adk task list         # List tasks
cheeru-adk task run <name>   # Run a task
```

---

## Project Structure

After `cheeru-adk init`:

```
your-project/
├── .agent/
│   ├── agents/          # AI agent definitions
│   └── workflows/       # Workflow definitions
├── .cheeru/
│   ├── config.json      # Project settings
│   ├── active_context.md # Session state
│   ├── specs/           # SPEC documents
│   └── tasks.yaml       # Task definitions
├── .gemini/
│   ├── commands/        # Slash commands
│   └── hooks/           # Lifecycle hooks
└── AGENTS.md            # Main orchestrator
```

---

## Development

```bash
git clone https://github.com/Dalgoi/cheeru-adk
cd cheeru-adk
uv sync
uv run pytest  # 169 tests
```

---

## Contributing

We welcome contributions!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a Pull Request

---

**Questions or Issues?** Please report any bugs or feedback through the [Issue tracker](https://github.com/Dalgoi/cheeru-adk/issues).

**Made with 😊 for job seekers**

