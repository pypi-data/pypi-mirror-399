"""TDD workflow management for CheerU-ADK.

Implements the Test-Driven Development (TDD) cycle:
RED -> GREEN -> REFACTOR

Designed for integration with Gemini CLI agents to automate
the TDD loop when AI receives a feature request.
"""

import subprocess
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Tuple
from datetime import datetime

from cheeru_adk.core.state import ContextManager, JsonStorage


# ============================================================
# TDD Phase Enum
# ============================================================

class TDDPhase(str, Enum):
    """TDD Cycle Phases.
    
    RED: Write a failing test first
    GREEN: Write minimal code to pass the test
    REFACTOR: Improve code while keeping tests green
    """
    RED = "RED"
    GREEN = "GREEN"
    REFACTOR = "REFACTOR"


# ============================================================
# TDD Manager
# ============================================================

class TDDManager:
    """Manages the TDD workflow cycle for Gemini CLI ADK projects.
    
    Tracks the current phase (RED/GREEN/REFACTOR), runs pytest,
    and provides phase transition logic based on test results.
    
    Example:
        tm = TDDManager()
        tm.start_cycle("Login Feature")
        success, output = tm.run_test("tests/test_auth.py")
        message = tm.advance_phase()
    """
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self._ctx_manager = ContextManager(project_path)
    
    def start_cycle(self, feature_name: str) -> dict[str, Any]:
        """Start a new TDD cycle.
        
        Args:
            feature_name: Name of the feature being developed
            
        Returns:
            Initial TDD state dictionary
        """
        state = {
            "feature_name": feature_name,
            "phase": TDDPhase.RED.value,
            "test_file": None,
            "target_file": None,
            "last_run_output": "",
            "last_run_success": False,
            "started_at": datetime.now().isoformat(),
        }
        self._save_state(state)
        self._ctx_manager.add_action(f"Started TDD cycle: {feature_name}", "tdd")
        return state
    
    def get_state(self) -> Optional[dict[str, Any]]:
        """Get current TDD state from context."""
        ctx = self._ctx_manager.load()
        return ctx.get("tdd_state")
    
    def run_test(self, test_file: Optional[str] = None) -> Tuple[bool, str]:
        """Run pytest and return (success, output).
        
        Args:
            test_file: Specific test file to run. If None, uses stored test_file.
            
        Returns:
            Tuple of (test_passed, pytest_output)
        """
        state = self.get_state()
        if not test_file and state:
            test_file = state.get("test_file")
            
        if not test_file:
            return False, "No test file specified."
            
        try:
            result = subprocess.run(
                ["pytest", test_file, "-v", "--no-header", "--tb=short", "-q"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            
            output = result.stdout + result.stderr
            success = result.returncode == 0
            
            # Update state if active
            if state:
                state["last_run_output"] = output
                state["last_run_success"] = success
                self._save_state(state)
            
            return success, output
            
        except FileNotFoundError:
            return False, "pytest command not found. Please install pytest."
    
    def advance_phase(self) -> str:
        """Advance to next TDD phase if conditions are met.
        
        Returns:
            Message describing phase transition result
        """
        state = self.get_state()
        if not state:
            return "No active TDD cycle."
            
        current = TDDPhase(state.get("phase", TDDPhase.RED.value))
        last_success = state.get("last_run_success", False)
        msg = ""
        
        if current == TDDPhase.RED:
            if not last_success:
                state["phase"] = TDDPhase.GREEN.value
                msg = "🔴 Test Failed (Good!). Moving to GREEN phase."
            else:
                msg = "⚠️ Test Passed unexpectedly. Write a FAILING test first."
                
        elif current == TDDPhase.GREEN:
            if last_success:
                state["phase"] = TDDPhase.REFACTOR.value
                msg = "🟢 Test Passed! Moving to REFACTOR phase."
            else:
                msg = "⚠️ Test still failing. Keep working on GREEN phase."
                
        elif current == TDDPhase.REFACTOR:
            if last_success:
                msg = "🔵 Refactoring successful. Cycle Complete!"
            else:
                msg = "⚠️ Refactoring broke the test. Revert changes."
        
        self._save_state(state)
        return msg

    def set_files(self, test_file: str, target_file: str) -> None:
        """Set files for current cycle.
        
        Args:
            test_file: Path to test file (e.g., tests/test_auth.py)
            target_file: Path to implementation file (e.g., src/auth.py)
        """
        state = self.get_state()
        if state:
            state["test_file"] = test_file
            state["target_file"] = target_file
            self._save_state(state)

    def _save_state(self, state: dict[str, Any]) -> None:
        """Save TDD state to context.json."""
        ctx = self._ctx_manager.load()
        ctx["tdd_state"] = state
        self._ctx_manager.save(ctx)
