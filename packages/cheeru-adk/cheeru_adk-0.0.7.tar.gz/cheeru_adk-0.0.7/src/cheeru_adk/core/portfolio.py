"""Portfolio generation from completed projects."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from rich.console import Console

console = Console()


def generate_portfolio(project_path: str = ".") -> dict:
    """Generate portfolio data from plan.json and context.
    
    Returns:
        Portfolio data dictionary
    """
    cheeru_dir = Path(project_path) / ".cheeru"
    plan_path = cheeru_dir / "plan.json"
    context_path = cheeru_dir / "context.json"
    
    if not plan_path.exists():
        raise FileNotFoundError("plan.json not found. Run 'cheeru-adk plan generate' first.")
    
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    context = {}
    if context_path.exists():
        context = json.loads(context_path.read_text(encoding="utf-8"))
    
    # Calculate statistics
    total_tasks = sum(len(p.get("tasks", [])) for p in plan.get("phases", []))
    completed_tasks = sum(
        1 for p in plan.get("phases", [])
        for t in p.get("tasks", [])
        if t.get("status") == "completed"
    )
    
    # Build portfolio
    portfolio = {
        "project_name": plan.get("project_name", "Unknown"),
        "target_job": plan.get("target_job", ""),
        "project_type": plan.get("project_type", ""),
        "tech_stack": plan.get("tech_stack", []),
        "difficulty": plan.get("difficulty", ""),
        "created_at": plan.get("created_at", ""),
        "stats": {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": round(completed_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0,
            "sessions": context.get("session_count", 0),
        },
        "phases": [],
        "achievements": [],
        "learnings": [],
    }
    
    # Process phases
    for phase in plan.get("phases", []):
        phase_data = {
            "title": phase.get("title", ""),
            "status": phase.get("status", "pending"),
            "tasks": [],
        }
        
        for task in phase.get("tasks", []):
            task_data = {
                "title": task.get("title", ""),
                "status": task.get("status", "pending"),
                "completed_at": task.get("completed_at", ""),
            }
            phase_data["tasks"].append(task_data)
        
        portfolio["phases"].append(phase_data)
    
    # Extract achievements from completed tasks
    for phase in portfolio["phases"]:
        completed = [t for t in phase["tasks"] if t["status"] == "completed"]
        if len(completed) == len(phase["tasks"]) and phase["tasks"]:
            portfolio["achievements"].append(f"{phase['title']} 완료")
    
    return portfolio


def export_portfolio_markdown(portfolio: dict, output_path: Optional[str] = None) -> str:
    """Export portfolio as markdown document.
    
    Args:
        portfolio: Portfolio data dictionary
        output_path: Optional path to save markdown file
        
    Returns:
        Markdown string
    """
    lines = []
    
    # Header
    lines.append(f"# {portfolio['project_name']}")
    lines.append("")
    lines.append(f"> {portfolio['target_job']} 포트폴리오 프로젝트")
    lines.append("")
    
    # Project Info
    lines.append("## 프로젝트 정보")
    lines.append("")
    lines.append(f"- **프로젝트 유형**: {portfolio['project_type']}")
    lines.append(f"- **난이도**: {portfolio['difficulty']}")
    lines.append(f"- **시작일**: {portfolio['created_at'][:10] if portfolio['created_at'] else 'N/A'}")
    lines.append("")
    
    # Tech Stack
    lines.append("## 기술 스택")
    lines.append("")
    for tech in portfolio.get("tech_stack", []):
        lines.append(f"- {tech}")
    lines.append("")
    
    # Progress
    stats = portfolio.get("stats", {})
    lines.append("## 진행 현황")
    lines.append("")
    lines.append(f"- **완료율**: {stats.get('completion_rate', 0)}%")
    lines.append(f"- **완료 태스크**: {stats.get('completed_tasks', 0)}/{stats.get('total_tasks', 0)}")
    lines.append(f"- **세션 수**: {stats.get('sessions', 0)}")
    lines.append("")
    
    # Phases
    lines.append("## 개발 단계")
    lines.append("")
    
    for phase in portfolio.get("phases", []):
        status_emoji = "✅" if phase["status"] == "completed" else "🔄" if phase["status"] == "in_progress" else "⬜"
        lines.append(f"### {status_emoji} {phase['title']}")
        lines.append("")
        
        for task in phase.get("tasks", []):
            task_emoji = "✅" if task["status"] == "completed" else "🔄" if task["status"] == "in_progress" else "⬜"
            lines.append(f"- [{task_emoji}] {task['title']}")
        
        lines.append("")
    
    # Achievements
    if portfolio.get("achievements"):
        lines.append("## 성과")
        lines.append("")
        for achievement in portfolio["achievements"]:
            lines.append(f"- 🏆 {achievement}")
        lines.append("")
    
    # Footer
    lines.append("---")
    lines.append(f"*Generated by CheerU-ADK on {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    
    markdown = "\n".join(lines)
    
    # Save if output path provided
    if output_path:
        Path(output_path).write_text(markdown, encoding="utf-8")
    
    return markdown


def export_portfolio_json(portfolio: dict, output_path: Optional[str] = None) -> str:
    """Export portfolio as JSON.
    
    Args:
        portfolio: Portfolio data dictionary
        output_path: Optional path to save JSON file
        
    Returns:
        JSON string
    """
    json_str = json.dumps(portfolio, ensure_ascii=False, indent=2)
    
    if output_path:
        Path(output_path).write_text(json_str, encoding="utf-8")
    
    return json_str
