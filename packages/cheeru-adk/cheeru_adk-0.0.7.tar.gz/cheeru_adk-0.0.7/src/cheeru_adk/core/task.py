"""Task System for CheerU-ADK.

CrewAI-inspired Task system that separates "what to do" (Task)
from "who does it" (Agent).

Key Features:
- Task definition with description, expected_output, agent assignment
- Task dependencies and execution order
- YAML-based task configuration
- Integration with existing agents
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional
import yaml

from cheeru_adk.core.state import ContextManager


# ============================================================
# Task Status
# ============================================================

class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


# ============================================================
# Task Definition
# ============================================================

@dataclass
class Task:
    """A unit of work to be executed by an agent.
    
    Attributes:
        name: Unique task identifier
        description: What the task should accomplish
        agent: Agent type to execute this task
        expected_output: Description of expected result
        context: List of context sources (files, previous tasks)
        dependencies: List of task names that must complete first
        status: Current execution status
        result: Task execution result
    """
    name: str
    description: str
    agent: str
    expected_output: str = ""
    context: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    
    def to_dict(self) -> dict:
        """Convert task to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "agent": self.agent,
            "expected_output": self.expected_output,
            "context": self.context,
            "dependencies": self.dependencies,
            "status": self.status.value,
        }
    
    @classmethod
    def from_dict(cls, name: str, data: dict) -> "Task":
        """Create Task from dictionary."""
        return cls(
            name=name,
            description=data.get("description", ""),
            agent=data.get("agent", "code-generator"),
            expected_output=data.get("expected_output", ""),
            context=data.get("context", []),
            dependencies=data.get("dependencies", []),
        )


# ============================================================
# Task Manager
# ============================================================

class TaskManager:
    """Manages task definitions and execution.
    
    Loads tasks from YAML configuration and provides methods
    for task execution, dependency resolution, and status tracking.
    
    Example:
        manager = TaskManager()
        tasks = manager.load_tasks()
        result = manager.execute("write_tests", {"feature": "login"})
    """
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.tasks_file = self.project_path / ".cheeru" / "tasks.yaml"
        self.tasks: dict[str, Task] = {}
        self._ctx_manager = ContextManager(project_path)
    
    def load_tasks(self) -> dict[str, Task]:
        """Load tasks from YAML file.
        
        Returns:
            Dictionary of task name to Task object
        """
        if not self.tasks_file.exists():
            return {}
        
        with open(self.tasks_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        
        self.tasks = {}
        for name, task_data in data.items():
            self.tasks[name] = Task.from_dict(name, task_data)
        
        return self.tasks
    
    def get_task(self, name: str) -> Optional[Task]:
        """Get a task by name.
        
        Args:
            name: Task name
            
        Returns:
            Task object or None
        """
        if not self.tasks:
            self.load_tasks()
        return self.tasks.get(name)
    
    def list_tasks(self) -> list[Task]:
        """List all available tasks.
        
        Returns:
            List of all tasks
        """
        if not self.tasks:
            self.load_tasks()
        return list(self.tasks.values())
    
    def get_runnable_tasks(self) -> list[Task]:
        """Get tasks that can be executed (dependencies met).
        
        Returns:
            List of tasks ready to run
        """
        if not self.tasks:
            self.load_tasks()
        
        runnable = []
        for task in self.tasks.values():
            if task.status != TaskStatus.PENDING:
                continue
            
            # Check all dependencies are completed
            deps_met = all(
                self.tasks.get(dep, Task(name="", description="", agent="")).status == TaskStatus.COMPLETED
                for dep in task.dependencies
            )
            
            if deps_met:
                runnable.append(task)
        
        return runnable
    
    def execute(self, task_name: str, inputs: Optional[dict] = None) -> dict:
        """Execute a task.
        
        Args:
            task_name: Name of task to execute
            inputs: Input variables for task (e.g., feature name)
            
        Returns:
            Execution result dictionary
        """
        task = self.get_task(task_name)
        if not task:
            return {"success": False, "error": f"Task '{task_name}' not found"}
        
        # Check dependencies
        for dep in task.dependencies:
            dep_task = self.get_task(dep)
            if dep_task and dep_task.status != TaskStatus.COMPLETED:
                return {
                    "success": False,
                    "error": f"Dependency '{dep}' not completed"
                }
        
        # Update status
        task.status = TaskStatus.RUNNING
        
        # Build prompt with variable substitution
        description = task.description
        if inputs:
            for key, value in inputs.items():
                description = description.replace(f"{{{key}}}", str(value))
        
        # Log action
        self._ctx_manager.add_action(
            f"Executing task: {task_name}", "task"
        )
        
        result = {
            "success": True,
            "task": task_name,
            "agent": task.agent,
            "description": description,
            "expected_output": task.expected_output,
            "context": task.context,
            "prompt": self._build_prompt(task, description),
        }
        
        task.status = TaskStatus.COMPLETED
        task.result = result
        
        return result
    
    def _build_prompt(self, task: Task, description: str) -> str:
        """Build execution prompt for the task.
        
        Args:
            task: Task object
            description: Substituted description
            
        Returns:
            Full prompt string
        """
        prompt_parts = [
            f"## Task: {task.name}",
            "",
            f"### Description",
            description,
            "",
            f"### Expected Output",
            task.expected_output,
        ]
        
        if task.context:
            prompt_parts.extend([
                "",
                "### Context",
                "Load the following for context:",
            ])
            for ctx in task.context:
                prompt_parts.append(f"- @{ctx}")
        
        return "\n".join(prompt_parts)
    
    def reset_all(self) -> None:
        """Reset all tasks to pending status."""
        for task in self.tasks.values():
            task.status = TaskStatus.PENDING
            task.result = None
    
    def get_execution_order(self) -> list[str]:
        """Get tasks in dependency-resolved execution order.
        
        Returns:
            List of task names in execution order
        """
        if not self.tasks:
            self.load_tasks()
        
        order = []
        visited = set()
        
        def visit(name: str):
            if name in visited:
                return
            visited.add(name)
            
            task = self.tasks.get(name)
            if task:
                for dep in task.dependencies:
                    visit(dep)
                order.append(name)
        
        for name in self.tasks:
            visit(name)
        
        return order
