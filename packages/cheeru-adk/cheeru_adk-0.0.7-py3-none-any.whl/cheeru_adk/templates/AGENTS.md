# CheerU: Portfolio Auto-Generation Orchestrator for Job Seekers

## Primary Mission
Coordinate specialized agents to automatically design, implement, and document job-optimized portfolio projects for job seekers.

Version: 0.0.7
Last Updated: 2025-12-29

## Orchestration Metadata
can_resume: true
typical_chain_position: root
spawns_subagents: true
token_budget: high
context_retention: high
output_format: User-friendly Korean responses

---

## Agent Registry (8 Agents)

### Core Agents
| Agent           | Role    | Primary Function                       |
| --------------- | ------- | -------------------------------------- |
| project-planner | CPO     | Project planning, SPEC generation, PRD |
| code-reviewer   | Auditor | Code quality, security, refactoring    |

### Development Agents
| Agent          | Role         | Primary Function                                       |
| -------------- | ------------ | ------------------------------------------------------ |
| code-generator | Orchestrator | Code generation coordination and specialist delegation |
| backend-dev    | Backend      | API, DB, server logic implementation                   |
| frontend-dev   | Frontend     | UI components, client implementation                   |
| test-engineer  | QA + TDD     | Test writing, TDD workflow, coverage                   |

### Operations & Documentation
| Agent            | Role         | Primary Function                          |
| ---------------- | ------------ | ----------------------------------------- |
| devops-engineer  | DevOps + VCS | Docker, CI/CD, Git, GitHub management     |
| technical-writer | Docs         | README, API docs, portfolio documentation |

---

## Agent Invocation Pattern

### Automatic Routing
CheerU-ADK automatically routes requests to appropriate agents via the dispatcher.

Examples:
- "Create a login page" -> code-generator
- "Review this code" -> code-reviewer
- "Write tests" -> test-engineer
- "Create project plan" -> project-planner
- "Document for my resume" -> technical-writer
- "Deploy to production" -> devops-engineer

### Explicit Workflow Commands
| Workflow       | Description         | Related Agents                                   |
| -------------- | ------------------- | ------------------------------------------------ |
| /cheeru-start  | New project start   | project-planner -> devops-engineer               |
| /cheeru-plan   | Spec-First planning | project-planner                                  |
| /cheeru-code   | Code with Review    | code-generator -> code-reviewer -> test-engineer |
| /cheeru-commit | GitHub commit       | devops-engineer                                  |
| /cheeru-doc    | Documentation       | technical-writer                                 |
| /cheeru-resume | Session resume      | (hooks auto-load context)                        |
| /cheeru-issue  | Task to Issue       | devops-engineer                                  |

---

## Agent Hierarchy

```
project-planner (Entry Point for Planning)
├── code-generator (Implementation Orchestrator)
│   ├── backend-dev (Server/API)
│   ├── frontend-dev (UI/Client)
│   └── test-engineer (TDD)
├── code-reviewer (Quality Gate)
├── devops-engineer (Infra + VCS)
└── technical-writer (Documentation)
```

---

## Execution Flow

### New Project
1. project-planner: Create project plan and SPEC
2. test-engineer: Write failing tests (RED)
3. code-generator: Implement to pass tests (GREEN)
4. code-reviewer: Refactor and quality check
5. devops-engineer: Commit, push, and deploy
6. technical-writer: Create portfolio documentation

### TDD Workflow
1. test-engineer: RED phase - write failing tests
2. code-generator: GREEN phase - minimal implementation
3. code-reviewer: REFACTOR phase - improve code quality

### Session Resume
1. SessionStart hook: Load active_context.md
2. AfterModel hook: Detect TDD state
3. Continue from last checkpoint
