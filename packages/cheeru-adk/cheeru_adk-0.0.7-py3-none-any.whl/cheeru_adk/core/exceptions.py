"""Custom exceptions for CheerU-ADK.

Provides structured error handling with clear error messages.
"""

from typing import Optional


class CheerUError(Exception):
    """Base exception for CheerU-ADK."""
    
    def __init__(self, message: str, hint: Optional[str] = None):
        self.message = message
        self.hint = hint
        super().__init__(message)
    
    def __str__(self) -> str:
        if self.hint:
            return f"{self.message}\n💡 힌트: {self.hint}"
        return self.message


class ProjectNotFoundError(CheerUError):
    """Raised when CheerU-ADK project is not initialized."""
    
    def __init__(self, path: str = "."):
        super().__init__(
            message=f"CheerU-ADK 프로젝트가 아닙니다: {path}",
            hint="cheeru-adk init 명령으로 프로젝트를 초기화하세요."
        )


class PlanNotFoundError(CheerUError):
    """Raised when plan.json doesn't exist."""
    
    def __init__(self):
        super().__init__(
            message="plan.json을 찾을 수 없습니다.",
            hint="cheeru-adk plan generate 명령으로 계획을 생성하세요."
        )


class TaskNotFoundError(CheerUError):
    """Raised when a task is not found."""
    
    def __init__(self, task_id: str):
        super().__init__(
            message=f"태스크를 찾을 수 없습니다: {task_id}",
            hint="cheeru-adk task list 명령으로 태스크 목록을 확인하세요."
        )


class ConfigKeyError(CheerUError):
    """Raised when a configuration key is invalid."""
    
    def __init__(self, key: str):
        super().__init__(
            message=f"유효하지 않은 설정 키: {key}",
            hint="cheeru-adk config list 명령으로 설정 목록을 확인하세요."
        )


class GitNotAvailableError(CheerUError):
    """Raised when git is not available."""
    
    def __init__(self):
        super().__init__(
            message="Git을 사용할 수 없습니다.",
            hint="Git이 설치되어 있고 현재 폴더가 Git 저장소인지 확인하세요."
        )


class GitHubCLIError(CheerUError):
    """Raised when gh CLI is not available or fails."""
    
    def __init__(self, detail: str = ""):
        super().__init__(
            message=f"GitHub CLI 오류: {detail}" if detail else "GitHub CLI를 사용할 수 없습니다.",
            hint="gh auth login 명령으로 GitHub CLI를 인증하세요."
        )


class ValidationError(CheerUError):
    """Raised when validation fails."""
    
    def __init__(self, field: str, reason: str):
        super().__init__(
            message=f"유효성 검사 실패 [{field}]: {reason}"
        )
