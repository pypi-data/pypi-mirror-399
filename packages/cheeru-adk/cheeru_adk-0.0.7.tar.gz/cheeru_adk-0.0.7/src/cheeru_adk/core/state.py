"""Unified state management for CheerU-ADK.

Consolidates TaskManager, ConfigManager, and ContextManager into a single module
for simpler imports and maintenance. This is the core state management for
Gemini CLI ADK projects.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Optional, List


# ============================================================
# Default Configuration
# ============================================================

DEFAULT_CONFIG = {
    "github": {
        "auto_commit": False,
        "default_labels": ["cheeru-adk"],
    },
    "notion": {
        "api_key": "",
        "database_id": "",
    },
    "cli": {
        "verbose": False,
        "color": True,
        "language": "ko",
    },
    "project": {
        "default_difficulty": "intermediate",
        "auto_save_context": True,
    }
}


# ============================================================
# Base Storage
# ============================================================

class JsonStorage:
    """Base class for JSON file storage operations."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
    
    def exists(self) -> bool:
        return self.file_path.exists()
    
    def load(self) -> Optional[dict]:
        if not self.exists():
            return None
        try:
            return json.loads(self.file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            return None
    
    def save(self, data: dict) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )


# ============================================================
# Task Manager
# ============================================================

class TaskManager:
    """Manages tasks in plan.json for Gemini CLI ADK projects."""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self._storage = JsonStorage(self.project_path / ".cheeru" / "plan.json")
    
    def list_tasks(self, status_filter: Optional[str] = None) -> List[dict]:
        """List all tasks with global index."""
        plan = self._storage.load()
        if not plan:
            return []
        
        tasks = []
        global_index = 1
        
        for phase in plan.get("phases", []):
            phase_title = phase.get("title", "Unknown Phase")
            
            for task in phase.get("tasks", []):
                task_status = task.get("status", "pending")
                
                if status_filter and task_status != status_filter:
                    global_index += 1
                    continue
                
                tasks.append({
                    "index": global_index,
                    "id": task.get("id", f"task-{global_index}"),
                    "title": task.get("title", "Untitled"),
                    "status": task_status,
                    "phase": phase_title,
                    "description": task.get("description", ""),
                })
                global_index += 1
        
        return tasks
    
    def get_task(self, index_or_id: str) -> Optional[dict]:
        """Get task by index number or ID."""
        for task in self.list_tasks():
            if str(task["index"]) == str(index_or_id) or task["id"] == index_or_id:
                return task
        return None
    
    def update_task_status(self, index_or_id: str, status: str) -> bool:
        """Update task status."""
        plan = self._storage.load()
        if not plan:
            return False
        
        global_index = 1
        for phase in plan.get("phases", []):
            for task in phase.get("tasks", []):
                task_id = task.get("id", f"task-{global_index}")
                
                if str(global_index) == str(index_or_id) or task_id == index_or_id:
                    task["status"] = status
                    if status == "in_progress":
                        task["started_at"] = datetime.now().isoformat()
                    elif status == "completed":
                        task["completed_at"] = datetime.now().isoformat()
                    
                    plan["updated_at"] = datetime.now().isoformat()
                    self._storage.save(plan)
                    return True
                
                global_index += 1
        
        return False
    
    def start_task(self, index_or_id: str) -> bool:
        return self.update_task_status(index_or_id, "in_progress")
    
    def complete_task(self, index_or_id: str) -> bool:
        return self.update_task_status(index_or_id, "completed")
    
    def reset_task(self, index_or_id: str) -> bool:
        return self.update_task_status(index_or_id, "pending")
    
    def get_progress(self) -> dict:
        """Get progress statistics."""
        tasks = self.list_tasks()
        total = len(tasks)
        completed = sum(1 for t in tasks if t["status"] == "completed")
        in_progress = sum(1 for t in tasks if t["status"] == "in_progress")
        pending = sum(1 for t in tasks if t["status"] == "pending")
        
        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "percentage": round(completed / total * 100, 1) if total > 0 else 0
        }


# ============================================================
# Config Manager
# ============================================================

class ConfigManager:
    """Manages CheerU-ADK configuration with dot-notation keys."""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self._storage = JsonStorage(self.project_path / ".cheeru" / "config.json")
    
    def load(self) -> dict[str, Any]:
        user_config = self._storage.load()
        if user_config:
            return self._merge_config(DEFAULT_CONFIG, user_config)
        return DEFAULT_CONFIG.copy()
    
    def save(self, config: dict[str, Any]) -> None:
        self._storage.save(config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value by dot-notation key (e.g., 'github.auto_commit')."""
        config = self.load()
        keys = key.split(".")
        
        value = config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """Set value by dot-notation key."""
        config = self.load()
        keys = key.split(".")
        
        current = config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Type conversion
        if isinstance(value, str):
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif value.isdigit():
                value = int(value)
        
        current[keys[-1]] = value
        self.save(config)
        return True
    
    def list_all(self) -> dict[str, Any]:
        """List all config as flat dict."""
        return self._flatten(self.load())
    
    def _merge_config(self, default: dict, user: dict) -> dict:
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def _flatten(self, d: dict, parent_key: str = "") -> dict:
        items = {}
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(self._flatten(v, new_key))
            else:
                items[new_key] = v
        return items


# ============================================================
# Context Manager
# ============================================================

class ContextManager:
    """Manages project context and session state for Gemini CLI."""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self._storage = JsonStorage(self.project_path / ".cheeru" / "context.json")
        self._plan_storage = JsonStorage(self.project_path / ".cheeru" / "plan.json")
    
    def load(self) -> dict[str, Any]:
        context = self._storage.load()
        if context:
            return context
        return self._create_default()
    
    def save(self, context: dict[str, Any]) -> None:
        context["last_updated"] = datetime.now().isoformat()
        self._storage.save(context)
    
    def _create_default(self) -> dict[str, Any]:
        return {
            "project_name": self.project_path.name,
            "current_phase": None,
            "current_task": None,
            "progress": {"total_tasks": 0, "completed_tasks": 0, "percentage": 0},
            "recent_actions": [],
            "blockers": [],
            "last_updated": datetime.now().isoformat(),
            "session_count": 0
        }
    
    def get_status(self) -> dict[str, Any]:
        """Get current project status with calculated progress."""
        context = self.load()
        plan = self._plan_storage.load()
        
        if plan:
            total = completed = 0
            current_phase = None
            
            for phase in plan.get("phases", []):
                for task in phase.get("tasks", []):
                    total += 1
                    if isinstance(task, dict):
                        if task.get("status") == "completed":
                            completed += 1
                        elif task.get("status") == "in_progress":
                            current_phase = phase.get("title")
            
            context["progress"] = {
                "total_tasks": total,
                "completed_tasks": completed,
                "percentage": round(completed / total * 100, 1) if total > 0 else 0
            }
            if current_phase:
                context["current_phase"] = current_phase
        
        return context
    
    def add_action(self, action: str, action_type: str = "general") -> None:
        """Add action to recent actions log."""
        context = self.load()
        
        context["recent_actions"].insert(0, {
            "action": action,
            "type": action_type,
            "timestamp": datetime.now().isoformat()
        })
        context["recent_actions"] = context["recent_actions"][:20]
        
        self.save(context)
    
    def add_blocker(self, description: str) -> None:
        """Add a blocker."""
        context = self.load()
        context["blockers"].append({
            "description": description,
            "added_at": datetime.now().isoformat(),
            "resolved": False
        })
        self.save(context)
    
    def resolve_blocker(self, index: int) -> None:
        """Mark blocker as resolved."""
        context = self.load()
        if 0 <= index < len(context["blockers"]):
            context["blockers"][index]["resolved"] = True
            context["blockers"][index]["resolved_at"] = datetime.now().isoformat()
        self.save(context)
    
    def start_session(self) -> dict[str, Any]:
        """Start new session and return summary."""
        context = self.load()
        context["session_count"] = context.get("session_count", 0) + 1
        context["session_started"] = datetime.now().isoformat()
        self.save(context)
        
        return {
            "session_number": context["session_count"],
            "current_phase": context.get("current_phase"),
            "progress": context.get("progress", {}),
            "recent_actions": context.get("recent_actions", [])[:5],
            "blockers": [b for b in context.get("blockers", []) if not b.get("resolved")]
        }
