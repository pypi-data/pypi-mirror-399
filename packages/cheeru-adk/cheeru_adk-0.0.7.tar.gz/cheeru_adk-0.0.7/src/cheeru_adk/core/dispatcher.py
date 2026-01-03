"""Agent Dispatcher for CheerU-ADK.

Automatically selects and dispatches the appropriate agent based on
task context and workflow stage.

Key Features:
- Agent registry with capability metadata
- Context-based agent selection
- Agent chain execution for complex workflows
- Integration with TDD and SPEC workflows
"""

import re
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from cheeru_adk.core.state import ContextManager


# ============================================================
# Agent Types (Consolidated: 8 agents)
# ============================================================

class AgentType(str, Enum):
    """Available agent types (consolidated)."""
    # Core development agents
    CODE_GENERATOR = "code-generator"
    CODE_REVIEWER = "code-reviewer"
    TEST_ENGINEER = "test-engineer"  # TDD + QA combined
    
    # Specialized development agents
    FRONTEND_DEV = "frontend-dev"
    BACKEND_DEV = "backend-dev"
    
    # Infrastructure & Operations
    DEVOPS_ENGINEER = "devops-engineer"  # DevOps + GitHub combined
    
    # Planning & Documentation
    PROJECT_PLANNER = "project-planner"  # Portfolio + Project Manager combined
    TECHNICAL_WRITER = "technical-writer"  # Developer + Recruiter Writer combined


# ============================================================
# Agent Registry (Consolidated: 8 agents)
# ============================================================

AGENT_REGISTRY = {
    AgentType.CODE_GENERATOR: {
        "path": ".agent/agents/code-generator.md",
        "capabilities": ["code", "implementation", "feature", "scaffolding"],
        "triggers": ["코드", "구현", "기능", "implement", "개발"],
        "priority": 9,
    },
    AgentType.CODE_REVIEWER: {
        "path": ".agent/agents/code-reviewer.md",
        "capabilities": ["review", "quality", "refactor", "feedback"],
        "triggers": ["리뷰", "검토", "refactor", "품질", "코드리뷰"],
        "priority": 7,
    },
    AgentType.TEST_ENGINEER: {
        "path": ".agent/agents/test-engineer.md",
        "capabilities": ["tdd", "testing", "coverage", "pytest", "red-green-refactor"],
        "triggers": ["tdd", "test", "테스트", "커버리지", "pytest"],
        "priority": 10,
    },
    AgentType.FRONTEND_DEV: {
        "path": ".agent/agents/frontend-dev.md",
        "capabilities": ["frontend", "react", "ui", "css", "component"],
        "triggers": ["프론트엔드", "ui", "react", "화면", "컴포넌트"],
        "priority": 8,
    },
    AgentType.BACKEND_DEV: {
        "path": ".agent/agents/backend-dev.md",
        "capabilities": ["backend", "api", "database", "server"],
        "triggers": ["백엔드", "api", "서버", "db", "데이터베이스"],
        "priority": 8,
    },
    AgentType.DEVOPS_ENGINEER: {
        "path": ".agent/agents/devops-engineer.md",
        "capabilities": ["deploy", "docker", "ci/cd", "git", "github", "commit"],
        "triggers": ["배포", "도커", "ci", "cd", "git", "커밋", "github", "푸시"],
        "priority": 8,
    },
    AgentType.PROJECT_PLANNER: {
        "path": ".agent/agents/project-planner.md",
        "capabilities": ["plan", "spec", "architecture", "project", "roadmap"],
        "triggers": ["계획", "설계", "아키텍처", "spec", "plan", "로드맵", "프로젝트"],
        "priority": 10,
    },
    AgentType.TECHNICAL_WRITER: {
        "path": ".agent/agents/technical-writer.md",
        "capabilities": ["docs", "readme", "documentation", "portfolio", "api-docs"],
        "triggers": ["문서", "readme", "docs", "포트폴리오", "문서화"],
        "priority": 6,
    },
}



# ============================================================
# Agent Dispatcher
# ============================================================

class AgentDispatcher:
    """Dispatches appropriate agents based on context.
    
    Analyzes task context and automatically selects the best agent(s)
    for the current workflow stage.
    
    Example:
        dispatcher = AgentDispatcher()
        agents = dispatcher.select("TDD 테스트 작성")
        chain = dispatcher.create_chain("tdd")
    """
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.agents_dir = self.project_path / ".agent" / "agents"
        self._ctx_manager = ContextManager(project_path)
    
    def select(self, context: str) -> list[AgentType]:
        """Select appropriate agents based on context.
        
        Args:
            context: Task description or context string
            
        Returns:
            List of recommended agents, sorted by relevance
        """
        context_lower = context.lower()
        scores = {}
        
        for agent_type, info in AGENT_REGISTRY.items():
            score = 0
            
            # Check triggers
            for trigger in info["triggers"]:
                if trigger in context_lower:
                    score += 10
            
            # Check capabilities
            for cap in info["capabilities"]:
                if cap in context_lower:
                    score += 5
            
            # Add priority bonus
            if score > 0:
                score += info["priority"]
            
            if score > 0:
                scores[agent_type] = score
        
        # Sort by score descending
        sorted_agents = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        return sorted_agents[:3]  # Return top 3 matches
    
    def create_chain(self, workflow: str) -> list[AgentType]:
        """Create an agent chain for a workflow.
        
        Args:
            workflow: Workflow name (tdd, plan, review, deploy)
            
        Returns:
            Ordered list of agents for the workflow
        """
        chains = {
            "tdd": [
                AgentType.TEST_ENGINEER,
                AgentType.CODE_GENERATOR,
                AgentType.CODE_REVIEWER,
            ],
            "plan": [
                AgentType.PROJECT_PLANNER,
            ],
            "review": [
                AgentType.CODE_REVIEWER,
            ],
            "deploy": [
                AgentType.DEVOPS_ENGINEER,
            ],
            "docs": [
                AgentType.TECHNICAL_WRITER,
                AgentType.CODE_REVIEWER,
            ],
        }
        
        return chains.get(workflow, [])
    
    def get_agent_path(self, agent_type: AgentType) -> Optional[Path]:
        """Get the path to an agent template.
        
        Args:
            agent_type: The agent type
            
        Returns:
            Path to the agent markdown file
        """
        if agent_type not in AGENT_REGISTRY:
            return None
        
        relative_path = AGENT_REGISTRY[agent_type]["path"]
        full_path = self.project_path / relative_path
        
        if full_path.exists():
            return full_path
        
        return None
    
    def get_agent_content(self, agent_type: AgentType) -> Optional[str]:
        """Get the content of an agent template.
        
        Args:
            agent_type: The agent type
            
        Returns:
            Agent template content
        """
        path = self.get_agent_path(agent_type)
        if path and path.exists():
            return path.read_text(encoding="utf-8")
        return None
    
    def dispatch(self, context: str) -> dict[str, Any]:
        """Dispatch agents based on context.
        
        Args:
            context: Task context
            
        Returns:
            Dispatch result with selected agents and paths
        """
        selected = self.select(context)
        
        if not selected:
            # Default to project planner
            selected = [AgentType.PROJECT_PLANNER]
        
        result = {
            "primary": selected[0] if selected else None,
            "secondary": selected[1:] if len(selected) > 1 else [],
            "agents": [],
        }
        
        for agent in selected:
            path = self.get_agent_path(agent)
            result["agents"].append({
                "type": agent.value,
                "path": str(path) if path else None,
                "capabilities": AGENT_REGISTRY[agent]["capabilities"],
            })
        
        self._ctx_manager.add_action(
            f"Dispatched agents: {[a.value for a in selected]}", "dispatch"
        )
        
        return result
    
    def for_tdd_phase(self, phase: str) -> AgentType:
        """Get the appropriate agent for a TDD phase.
        
        Args:
            phase: TDD phase (red, green, refactor)
            
        Returns:
            Recommended agent for the phase
        """
        phase_agents = {
            "red": AgentType.TEST_ENGINEER,
            "green": AgentType.CODE_GENERATOR,
            "refactor": AgentType.CODE_REVIEWER,
        }
        
        return phase_agents.get(phase.lower(), AgentType.TEST_ENGINEER)
    
    def list_agents(self) -> list[dict[str, Any]]:
        """List all available agents.
        
        Returns:
            List of agent info dictionaries
        """
        agents = []
        
        for agent_type, info in AGENT_REGISTRY.items():
            path = self.get_agent_path(agent_type)
            agents.append({
                "type": agent_type.value,
                "path": str(path) if path else None,
                "exists": path.exists() if path else False,
                "capabilities": info["capabilities"],
            })
        
        return agents
