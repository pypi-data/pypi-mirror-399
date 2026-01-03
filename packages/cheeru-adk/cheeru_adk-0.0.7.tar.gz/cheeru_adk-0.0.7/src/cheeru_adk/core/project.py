"""Project initialization and management."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from cheeru_adk import __version__


def get_templates_dir() -> Path:
    """Get the templates directory path."""
    return Path(__file__).parent.parent / "templates"


def initialize_project(path: str, force: bool = False) -> dict[str, Any]:
    """Initialize CheerU-ADK in a project directory.
    
    Args:
        path: Target project directory
        force: Overwrite existing configuration
        
    Returns:
        Dictionary with created files list
    """
    project_path = Path(path).resolve()
    
    if not project_path.exists():
        project_path.mkdir(parents=True)
    
    # Check existing configuration
    cheeru_dir = project_path / ".cheeru"
    agent_dir = project_path / ".agent"
    
    if cheeru_dir.exists() and not force:
        raise FileExistsError(
            "CheerU-ADK가 이미 설정되어 있습니다. "
            "--force 옵션으로 덮어쓰기 가능합니다."
        )
    
    created_files = []
    templates_dir = get_templates_dir()
    
    # Copy .agent directory
    agent_template = templates_dir / ".agent"
    if agent_template.exists():
        if agent_dir.exists() and force:
            shutil.rmtree(agent_dir)
        shutil.copytree(agent_template, agent_dir, dirs_exist_ok=True)
        
        for file in agent_dir.rglob("*"):
            if file.is_file():
                created_files.append(str(file.relative_to(project_path)))
    
    # Copy .gemini directory (slash commands)
    gemini_dir = project_path / ".gemini"
    gemini_template = templates_dir / ".gemini"
    if gemini_template.exists():
        if gemini_dir.exists() and force:
            shutil.rmtree(gemini_dir)
        shutil.copytree(gemini_template, gemini_dir, dirs_exist_ok=True)
        
        for file in gemini_dir.rglob("*"):
            if file.is_file():
                created_files.append(str(file.relative_to(project_path)))
    
    # Copy AGENTS.md
    agents_md_template = templates_dir / "AGENTS.md"
    agents_md_dest = project_path / "AGENTS.md"
    if agents_md_template.exists():
        shutil.copy(agents_md_template, agents_md_dest)
        created_files.append("AGENTS.md")
    
    # Create .cheeru directory and config
    cheeru_dir.mkdir(exist_ok=True)
    
    config = {
        "project_name": project_path.name,
        "cheeru_version": __version__,
        "created_at": datetime.now().isoformat(),
        "settings": {
            "github_auto_commit": True,
            "notion_auto_sync": True,
            "default_difficulty": "중급",
        }
    }
    
    config_path = cheeru_dir / "config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    created_files.append(".cheeru/config.json")
    
    return {"created_files": sorted(created_files)}


def update_templates(path: str) -> dict[str, Any]:
    """Update templates to latest version.
    
    Args:
        path: Project directory path
        
    Returns:
        Dictionary with updated files list
    """
    project_path = Path(path).resolve()
    agent_dir = project_path / ".agent"
    
    if not agent_dir.exists():
        raise FileNotFoundError("CheerU-ADK가 설정되지 않은 프로젝트입니다.")
    
    templates_dir = get_templates_dir()
    updated_files = []
    
    # Update .agent directory
    agent_template = templates_dir / ".agent"
    if agent_template.exists():
        shutil.copytree(agent_template, agent_dir, dirs_exist_ok=True)
        
        for file in agent_dir.rglob("*"):
            if file.is_file():
                updated_files.append(str(file.relative_to(project_path)))
    
    # Update AGENTS.md
    agents_md_template = templates_dir / "AGENTS.md"
    if agents_md_template.exists():
        shutil.copy(agents_md_template, project_path / "AGENTS.md")
        updated_files.append("AGENTS.md")
    
    return {"updated_files": sorted(updated_files)}
