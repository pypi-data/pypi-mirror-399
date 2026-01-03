"""Git Worktree CLI for parallel SPEC development.

Provides commands to manage Git worktrees for SPEC-based parallel development
without context switching. Each SPEC gets its own isolated workspace.

Based on MoAI-ADK patterns.
"""

import subprocess
from pathlib import Path
from typing import Any, Optional

from cheeru_adk.core.state import ContextManager


# ============================================================
# Worktree Manager
# ============================================================

class WorktreeManager:
    """Manages Git worktrees for parallel SPEC development.
    
    Each SPEC can have its own isolated workspace via Git worktree.
    This enables true parallel development without context switching.
    
    Example:
        wm = WorktreeManager()
        wm.create("SPEC-001")      # Create worktree
        wm.list_worktrees()        # List all
        wm.go("SPEC-001")          # Switch
        wm.merge("SPEC-001")       # Merge and remove
    """
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.worktrees_dir = self.project_path / "worktrees"
        self._ctx_manager = ContextManager(project_path)
    
    def create(self, spec_id: str, branch_name: Optional[str] = None) -> dict[str, Any]:
        """Create a new worktree for a SPEC.
        
        Args:
            spec_id: SPEC identifier (e.g., SPEC-001)
            branch_name: Branch name (default: feature/{spec_id})
            
        Returns:
            Result dictionary with path and status
        """
        if not branch_name:
            branch_name = f"feature/{spec_id.lower()}"
        
        worktree_path = self.worktrees_dir / spec_id
        
        # Create worktree with new branch
        try:
            result = subprocess.run(
                ["git", "worktree", "add", "-b", branch_name, str(worktree_path)],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            
            if result.returncode != 0:
                # Try without -b if branch exists
                result = subprocess.run(
                    ["git", "worktree", "add", str(worktree_path), branch_name],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    encoding="utf-8"
                )
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            if success:
                self._ctx_manager.add_action(f"Created worktree: {spec_id}", "worktree")
            
            return {
                "success": success,
                "spec_id": spec_id,
                "branch": branch_name,
                "path": str(worktree_path),
                "output": output,
            }
            
        except FileNotFoundError:
            return {
                "success": False,
                "error": "git command not found. Please install Git.",
            }
    
    def list_worktrees(self) -> list[dict[str, Any]]:
        """List all existing worktrees.
        
        Returns:
            List of worktree info dictionaries
        """
        try:
            result = subprocess.run(
                ["git", "worktree", "list", "--porcelain"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            
            if result.returncode != 0:
                return []
            
            worktrees = []
            current = {}
            
            for line in result.stdout.strip().split("\n"):
                if line.startswith("worktree "):
                    if current:
                        worktrees.append(current)
                    current = {"path": line.replace("worktree ", "")}
                elif line.startswith("HEAD "):
                    current["head"] = line.replace("HEAD ", "")
                elif line.startswith("branch "):
                    current["branch"] = line.replace("branch refs/heads/", "")
                elif line == "bare":
                    current["bare"] = True
                elif line == "detached":
                    current["detached"] = True
            
            if current:
                worktrees.append(current)
            
            # Add SPEC info if applicable
            for wt in worktrees:
                path = Path(wt["path"])
                if path.parent == self.worktrees_dir:
                    wt["spec_id"] = path.name
            
            return worktrees
            
        except FileNotFoundError:
            return []
    
    def go(self, spec_id: str) -> dict[str, Any]:
        """Get the path to navigate to a SPEC worktree.
        
        Args:
            spec_id: SPEC identifier
            
        Returns:
            Result with worktree path
        """
        worktree_path = self.worktrees_dir / spec_id
        
        if not worktree_path.exists():
            return {
                "success": False,
                "error": f"Worktree for {spec_id} does not exist.",
            }
        
        return {
            "success": True,
            "spec_id": spec_id,
            "path": str(worktree_path),
            "command": f"cd {worktree_path}",
        }
    
    def remove(self, spec_id: str, force: bool = False) -> dict[str, Any]:
        """Remove a worktree.
        
        Args:
            spec_id: SPEC identifier
            force: Force removal even if dirty
            
        Returns:
            Result dictionary
        """
        worktree_path = self.worktrees_dir / spec_id
        
        cmd = ["git", "worktree", "remove", str(worktree_path)]
        if force:
            cmd.append("--force")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            
            success = result.returncode == 0
            
            if success:
                self._ctx_manager.add_action(f"Removed worktree: {spec_id}", "worktree")
            
            return {
                "success": success,
                "spec_id": spec_id,
                "output": result.stdout + result.stderr,
            }
            
        except FileNotFoundError:
            return {"success": False, "error": "git command not found."}
    
    def merge(
        self,
        spec_id: str,
        base_branch: str = "main",
        min_coverage: int = 80,
        skip_lint: bool = False,
    ) -> dict[str, Any]:
        """Merge a SPEC worktree into base branch with enhanced verification.
        
        Verification steps:
        1. Run pytest with coverage check
        2. Run lint check (ruff/flake8)
        3. Verify coverage meets threshold
        4. Merge to base branch
        5. Clean up worktree
        
        Args:
            spec_id: SPEC identifier
            base_branch: Target branch to merge into
            min_coverage: Minimum coverage percentage required (default: 80)
            skip_lint: Skip lint check (not recommended)
            
        Returns:
            Result dictionary with merge status and verification results
        """
        worktree_path = self.worktrees_dir / spec_id
        
        if not worktree_path.exists():
            return {"success": False, "error": f"Worktree {spec_id} not found."}
        
        feature_branch = f"feature/{spec_id.lower()}"
        verification = {
            "tests_passed": False,
            "coverage_met": False,
            "lint_passed": skip_lint,  # Auto-pass if skipped
            "coverage_percent": 0,
        }
        
        try:
            # Step 1: Run tests with coverage
            test_result = subprocess.run(
                ["pytest", "tests/", "-v", "--tb=short", "--cov=src", "--cov-report=term-missing"],
                cwd=worktree_path,
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            
            verification["tests_passed"] = test_result.returncode == 0
            
            # Parse coverage percentage
            output = test_result.stdout + test_result.stderr
            import re
            cov_match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', output)
            if cov_match:
                verification["coverage_percent"] = int(cov_match.group(1))
                verification["coverage_met"] = verification["coverage_percent"] >= min_coverage
            
            if not verification["tests_passed"]:
                return {
                    "success": False,
                    "phase": "tests",
                    "error": "Tests failed. Fix tests before merging.",
                    "verification": verification,
                    "output": output,
                }
            
            if not verification["coverage_met"]:
                return {
                    "success": False,
                    "phase": "coverage",
                    "error": f"Coverage {verification['coverage_percent']}% < {min_coverage}%. Increase coverage before merging.",
                    "verification": verification,
                }
            
            # Step 2: Run lint check (if not skipped)
            if not skip_lint:
                lint_result = subprocess.run(
                    ["python", "-m", "ruff", "check", "."],
                    cwd=worktree_path,
                    capture_output=True,
                    text=True,
                    encoding="utf-8"
                )
                
                if lint_result.returncode != 0:
                    # Try flake8 as fallback
                    lint_result = subprocess.run(
                        ["python", "-m", "flake8", "--max-line-length=120", "."],
                        cwd=worktree_path,
                        capture_output=True,
                        text=True,
                        encoding="utf-8"
                    )
                
                verification["lint_passed"] = lint_result.returncode == 0
                
                if not verification["lint_passed"]:
                    return {
                        "success": False,
                        "phase": "lint",
                        "error": "Lint check failed. Fix lint issues before merging.",
                        "verification": verification,
                        "output": lint_result.stdout + lint_result.stderr,
                    }
            
            # Step 3: Merge to base branch
            subprocess.run(
                ["git", "checkout", base_branch],
                cwd=self.project_path,
                capture_output=True,
                text=True,
            )
            
            merge_result = subprocess.run(
                ["git", "merge", "--no-ff", feature_branch, "-m", f"feat: merge {spec_id}"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            
            if merge_result.returncode != 0:
                return {
                    "success": False,
                    "phase": "merge",
                    "error": "Merge conflict. Resolve manually.",
                    "verification": verification,
                    "output": merge_result.stdout + merge_result.stderr,
                }
            
            # Step 4: Remove worktree after successful merge
            self.remove(spec_id)
            
            self._ctx_manager.add_action(f"Merged worktree: {spec_id} → {base_branch}", "worktree")
            
            return {
                "success": True,
                "spec_id": spec_id,
                "merged_into": base_branch,
                "verification": verification,
                "output": merge_result.stdout,
            }
            
        except FileNotFoundError as e:
            return {"success": False, "error": f"Command not found: {e}"}

    
    def sync(self, spec_id: str, base_branch: str = "main") -> dict[str, Any]:
        """Sync worktree with latest base branch.
        
        Args:
            spec_id: SPEC identifier
            base_branch: Branch to sync from
            
        Returns:
            Result dictionary
        """
        worktree_path = self.worktrees_dir / spec_id
        
        if not worktree_path.exists():
            return {"success": False, "error": f"Worktree {spec_id} not found."}
        
        try:
            # Fetch latest
            subprocess.run(
                ["git", "fetch", "origin", base_branch],
                cwd=worktree_path,
                capture_output=True,
            )
            
            # Rebase on base branch
            result = subprocess.run(
                ["git", "rebase", f"origin/{base_branch}"],
                cwd=worktree_path,
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            
            success = result.returncode == 0
            
            return {
                "success": success,
                "spec_id": spec_id,
                "output": result.stdout + result.stderr,
            }
            
        except FileNotFoundError:
            return {"success": False, "error": "git command not found."}
