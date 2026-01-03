"""GitHub integration using gh CLI."""

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class GitHubConfig:
    """GitHub configuration."""
    owner: str = ""
    repo: str = ""
    
    @classmethod
    def from_remote(cls) -> "GitHubConfig":
        """Auto-detect from git remote."""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True, text=True, check=True
            )
            url = result.stdout.strip()
            
            # Parse GitHub URL
            # https://github.com/owner/repo.git or git@github.com:owner/repo.git
            if "github.com" in url:
                if url.startswith("git@"):
                    # git@github.com:owner/repo.git
                    parts = url.split(":")[-1].replace(".git", "").split("/")
                else:
                    # https://github.com/owner/repo.git
                    parts = url.replace(".git", "").split("/")[-2:]
                
                if len(parts) >= 2:
                    return cls(owner=parts[0], repo=parts[1])
        except subprocess.CalledProcessError:
            pass
        
        return cls()


class GitHubIntegration:
    """GitHub operations using gh CLI."""
    
    def __init__(self, config: Optional[GitHubConfig] = None):
        self.config = config or GitHubConfig.from_remote()
    
    @staticmethod
    def is_gh_available() -> bool:
        """Check if gh CLI is installed and authenticated."""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True, text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def create_issue(
        self,
        title: str,
        body: str = "",
        labels: Optional[list[str]] = None,
        milestone: Optional[str] = None
    ) -> dict:
        """Create a GitHub issue."""
        cmd = ["gh", "issue", "create", "--title", title]
        
        if body:
            cmd.extend(["--body", body])
        if labels:
            cmd.extend(["--label", ",".join(labels)])
        if milestone:
            cmd.extend(["--milestone", milestone])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return {
                "success": True,
                "url": result.stdout.strip(),
                "message": f"Issue created: {title}"
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": e.stderr,
                "message": f"Failed to create issue: {title}"
            }
    
    def list_issues(self, state: str = "open", labels: Optional[list[str]] = None) -> list[dict]:
        """List GitHub issues."""
        cmd = ["gh", "issue", "list", "--state", state, "--json", "number,title,state,labels,url"]
        
        if labels:
            for label in labels:
                cmd.extend(["--label", label])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout) if result.stdout else []
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return []
    
    def close_issue(self, issue_number: int, comment: Optional[str] = None) -> dict:
        """Close an issue."""
        cmd = ["gh", "issue", "close", str(issue_number)]
        
        if comment:
            cmd.extend(["--comment", comment])
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            return {"success": True, "message": f"Issue #{issue_number} closed"}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": e.stderr}
    
    def sync_plan_to_issues(self, plan_path: str) -> dict:
        """Sync plan.json tasks to GitHub issues."""
        plan_file = Path(plan_path)
        
        if not plan_file.exists():
            return {"success": False, "error": "plan.json not found"}
        
        plan = json.loads(plan_file.read_text(encoding="utf-8"))
        existing_issues = self.list_issues(state="all")
        existing_titles = {issue["title"] for issue in existing_issues}
        
        created = []
        skipped = []
        
        for phase in plan.get("phases", []):
            phase_title = phase.get("title", "Unknown Phase")
            
            for task in phase.get("tasks", []):
                if isinstance(task, dict):
                    task_title = task.get("title", "")
                    task_desc = task.get("description", "")
                else:
                    task_title = str(task)
                    task_desc = ""
                
                # Format issue title
                issue_title = f"[{phase_title}] {task_title}"
                
                if issue_title in existing_titles:
                    skipped.append(issue_title)
                    continue
                
                # Create issue
                body = f"## Phase: {phase_title}\n\n{task_desc}" if task_desc else f"## Phase: {phase_title}"
                result = self.create_issue(
                    title=issue_title,
                    body=body,
                    labels=["cheeru-adk", "auto-generated"]
                )
                
                if result["success"]:
                    created.append(issue_title)
        
        return {
            "success": True,
            "created": created,
            "skipped": skipped,
            "message": f"Created {len(created)} issues, skipped {len(skipped)} existing"
        }


class GitCommit:
    """Smart git commit operations."""
    
    @staticmethod
    def get_staged_files() -> list[str]:
        """Get list of staged files."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True, text=True, check=True
            )
            return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        except subprocess.CalledProcessError:
            return []
    
    @staticmethod
    def get_diff_summary() -> str:
        """Get summary of staged changes."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--stat"],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return ""
    
    @classmethod
    def generate_message(cls, context: Optional[dict] = None) -> str:
        """Generate conventional commit message based on staged files."""
        files = cls.get_staged_files()
        
        if not files:
            return "chore: update"
        
        # Analyze file types
        types = {
            "feat": [],
            "fix": [],
            "docs": [],
            "style": [],
            "refactor": [],
            "test": [],
            "chore": []
        }
        
        for f in files:
            lower = f.lower()
            if "test" in lower or f.startswith("tests/"):
                types["test"].append(f)
            elif lower.endswith(".md") or "docs/" in lower:
                types["docs"].append(f)
            elif "fix" in lower:
                types["fix"].append(f)
            elif any(x in lower for x in [".gitignore", "config", "requirements", "pyproject"]):
                types["chore"].append(f)
            else:
                types["feat"].append(f)
        
        # Determine primary type
        primary = "chore"
        for t in ["feat", "fix", "docs", "test", "refactor", "style", "chore"]:
            if types[t]:
                primary = t
                break
        
        # Generate scope from first file
        scope = ""
        if files:
            first_file = Path(files[0])
            if first_file.parent.name not in (".", "src"):
                scope = f"({first_file.parent.name})"
        
        # Generate description
        if len(files) == 1:
            desc = Path(files[0]).stem
        else:
            desc = f"update {len(files)} files"
        
        return f"{primary}{scope}: {desc}"
    
    @classmethod
    def commit(cls, message: Optional[str] = None, auto: bool = False) -> dict:
        """Create a git commit."""
        if auto:
            message = cls.generate_message()
        
        if not message:
            return {"success": False, "error": "No commit message provided"}
        
        try:
            result = subprocess.run(
                ["git", "commit", "-m", message],
                capture_output=True, text=True, check=True
            )
            return {
                "success": True,
                "message": message,
                "output": result.stdout.strip()
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": e.stderr,
                "message": message
            }
