"""SPEC management for CheerU-ADK.

Implements SPEC-First development with EARS format:
- Environment: Project context
- Assumptions: Development prerequisites
- Requirements: What to build (WHEN...THEN, IF...THEN)
- Specifications: How to build

Based on MoAI-ADK patterns for Gemini CLI integration.
"""

import json
import re
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

from cheeru_adk.core.state import ContextManager


# ============================================================
# SPEC Status Enum
# ============================================================

class SPECStatus(str, Enum):
    """SPEC lifecycle status."""
    DRAFT = "draft"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# ============================================================
# EARS Template
# ============================================================

EARS_TEMPLATE = """---
id: {spec_id}
title: {title}
version: 1.0.0
status: draft
created: {created}
author: cheeru-adk
category: FEATURE
priority: MEDIUM
tags: [{tags}]
---

# {title}

## Environment

- **Project**: {project_name}
- **Language**: {language}
- **Framework**: {framework}
- **Platform**: {platform}

## Assumptions

1. 개발 환경이 정상적으로 설정되어 있음
2. 필수 의존성이 설치되어 있음
3. 테스트 환경이 구성되어 있음

## Requirements

### Ubiquitous Requirements
- 시스템은 항상 로그를 기록해야 함
- 시스템은 에러를 적절히 처리해야 함

### Event-driven Requirements (WHEN...THEN)
{event_requirements}

### State-driven Requirements (IF...THEN)
{state_requirements}

### Constraints
{constraints}

## Success Criteria

- [ ] 모든 테스트 통과
- [ ] 코드 커버리지 >= 85%
- [ ] 문서화 완료

## Test Scenarios

### TC-001: 정상 동작 테스트
- Input: 유효한 입력
- Expected: 정상 처리

### TC-002: 예외 처리 테스트
- Input: 잘못된 입력
- Expected: 적절한 에러 메시지
"""


# ============================================================
# SPEC Manager
# ============================================================

class SPECManager:
    """Manages SPEC documents for SPEC-First TDD workflow.
    
    Creates, lists, and manages SPEC documents in EARS format.
    Integrates with Git Worktree for parallel development.
    
    Example:
        sm = SPECManager()
        spec_id = sm.create("User Login Feature")
        sm.update_status(spec_id, SPECStatus.IN_PROGRESS)
    """
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.specs_dir = self.project_path / ".cheeru" / "specs"
        self._ctx_manager = ContextManager(project_path)
    
    def create(
        self,
        title: str,
        language: str = "Python",
        framework: str = "FastAPI",
        platform: str = "Web",
        tags: list[str] = None,
    ) -> str:
        """Create a new SPEC document.
        
        Args:
            title: Feature title
            language: Primary programming language
            framework: Framework being used
            platform: Target platform
            tags: Additional tags
            
        Returns:
            Generated SPEC ID (e.g., SPEC-001)
        """
        # Generate SPEC ID
        spec_id = self._generate_spec_id()
        
        # Prepare template variables
        project_name = self.project_path.name
        created = datetime.now().strftime("%Y-%m-%d")
        tags_str = ", ".join(tags) if tags else "auto-generated"
        
        # Generate requirements placeholders
        event_requirements = self._generate_event_requirements(title)
        state_requirements = self._generate_state_requirements(title)
        constraints = self._generate_constraints(title)
        
        # Render template
        content = EARS_TEMPLATE.format(
            spec_id=spec_id,
            title=title,
            project_name=project_name,
            language=language,
            framework=framework,
            platform=platform,
            created=created,
            tags=tags_str,
            event_requirements=event_requirements,
            state_requirements=state_requirements,
            constraints=constraints,
        )
        
        # Save to file
        spec_dir = self.specs_dir / spec_id
        spec_dir.mkdir(parents=True, exist_ok=True)
        spec_file = spec_dir / "spec.md"
        spec_file.write_text(content, encoding="utf-8")
        
        # Log action
        self._ctx_manager.add_action(f"Created SPEC: {spec_id} - {title}", "spec")
        
        return spec_id
    
    def list_specs(self) -> list[dict[str, Any]]:
        """List all SPEC documents.
        
        Returns:
            List of SPEC info dictionaries
        """
        specs = []
        
        if not self.specs_dir.exists():
            return specs
            
        for spec_dir in sorted(self.specs_dir.iterdir()):
            if spec_dir.is_dir():
                spec_file = spec_dir / "spec.md"
                if spec_file.exists():
                    info = self._parse_spec_frontmatter(spec_file)
                    info["path"] = str(spec_dir)
                    specs.append(info)
        
        return specs
    
    def get_spec(self, spec_id: str) -> Optional[dict[str, Any]]:
        """Get SPEC details by ID.
        
        Args:
            spec_id: SPEC identifier (e.g., SPEC-001)
            
        Returns:
            SPEC info or None
        """
        spec_dir = self.specs_dir / spec_id
        spec_file = spec_dir / "spec.md"
        
        if not spec_file.exists():
            return None
            
        info = self._parse_spec_frontmatter(spec_file)
        info["path"] = str(spec_dir)
        info["content"] = spec_file.read_text(encoding="utf-8")
        return info
    
    def update_status(self, spec_id: str, status: SPECStatus) -> bool:
        """Update SPEC status.
        
        Args:
            spec_id: SPEC identifier
            status: New status
            
        Returns:
            True if successful
        """
        spec_dir = self.specs_dir / spec_id
        spec_file = spec_dir / "spec.md"
        
        if not spec_file.exists():
            return False
            
        content = spec_file.read_text(encoding="utf-8")
        
        # Update status in frontmatter
        updated = re.sub(
            r'status:\s*\w+',
            f'status: {status.value}',
            content
        )
        
        spec_file.write_text(updated, encoding="utf-8")
        self._ctx_manager.add_action(f"Updated SPEC {spec_id} status: {status.value}", "spec")
        
        return True
    
    def _generate_spec_id(self) -> str:
        """Generate next SPEC ID."""
        existing = list(self.specs_dir.glob("SPEC-*")) if self.specs_dir.exists() else []
        
        if not existing:
            return "SPEC-001"
            
        # Find highest number
        max_num = 0
        for spec_dir in existing:
            match = re.match(r"SPEC-(\d+)", spec_dir.name)
            if match:
                max_num = max(max_num, int(match.group(1)))
        
        return f"SPEC-{max_num + 1:03d}"
    
    def _parse_spec_frontmatter(self, spec_file: Path) -> dict[str, Any]:
        """Parse YAML frontmatter from SPEC file."""
        content = spec_file.read_text(encoding="utf-8")
        
        # Extract frontmatter
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return {"id": spec_file.parent.name, "title": "Unknown", "status": "unknown"}
            
        frontmatter = match.group(1)
        
        # Simple YAML-like parsing
        info = {}
        for line in frontmatter.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        
        return info
    
    def _generate_event_requirements(self, title: str) -> str:
        """Generate event-driven requirements template."""
        return f"""- WHEN 사용자가 {title} 기능을 요청하면
  - THEN 시스템은 해당 기능을 수행함
- WHEN 오류가 발생하면
  - THEN 시스템은 적절한 에러 메시지를 표시함"""
    
    def _generate_state_requirements(self, title: str) -> str:
        """Generate state-driven requirements template."""
        return f"""- IF 사용자가 인증된 상태라면
  - THEN {title} 기능에 접근 가능함
- IF 필수 입력이 누락된 경우
  - THEN 시스템은 입력 요청 메시지를 표시함"""
    
    def _generate_constraints(self, title: str) -> str:
        """Generate constraints template."""
        return """- 응답 시간은 500ms 이내
- 동시 요청 처리 최대 100개
- 메모리 사용량 최대 256MB"""
    
    def detect_completion(self, spec_id: str) -> dict[str, Any]:
        """Detect if a SPEC implementation is complete.
        
        Checks:
        - Test files exist
        - All tests pass
        - Implementation files exist
        - Success criteria met
        
        Args:
            spec_id: SPEC identifier
            
        Returns:
            Dict with is_complete, criteria_met, issues
        """
        import subprocess
        
        spec_info = self.get_spec(spec_id)
        if not spec_info:
            return {"is_complete": False, "error": f"SPEC {spec_id} not found"}
        
        criteria = {
            "tests_exist": False,
            "tests_pass": False,
            "implementation_exists": False,
            "coverage_ok": False,
        }
        issues = []
        
        # Check for test files
        tests_dir = self.project_path / "tests"
        spec_test_pattern = spec_id.lower().replace("-", "_")
        test_files = list(tests_dir.glob(f"*{spec_test_pattern}*")) if tests_dir.exists() else []
        criteria["tests_exist"] = len(test_files) > 0
        
        if not criteria["tests_exist"]:
            issues.append("No test files found for this SPEC")
        
        # Run tests if they exist
        if criteria["tests_exist"]:
            try:
                result = subprocess.run(
                    ["pytest", "tests/", "-v", "--tb=short", "-q"],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    encoding="utf-8"
                )
                criteria["tests_pass"] = result.returncode == 0
                
                if not criteria["tests_pass"]:
                    issues.append("Tests are failing")
            except FileNotFoundError:
                issues.append("pytest not installed")
        
        # Check implementation
        src_dir = self.project_path / "src"
        if src_dir.exists():
            py_files = list(src_dir.rglob("*.py"))
            criteria["implementation_exists"] = len(py_files) > 5  # Basic heuristic
        
        if not criteria["implementation_exists"]:
            issues.append("Implementation files may be incomplete")
        
        # Simple coverage check (basic heuristic)
        criteria["coverage_ok"] = criteria["tests_exist"] and criteria["tests_pass"]
        
        is_complete = all([
            criteria["tests_exist"],
            criteria["tests_pass"],
            criteria["implementation_exists"],
        ])
        
        return {
            "is_complete": is_complete,
            "criteria": criteria,
            "issues": issues,
            "spec_id": spec_id,
        }
    
    def auto_transition(self, spec_id: str) -> dict[str, Any]:
        """Automatically transition SPEC status based on implementation state.
        
        Transitions:
        - draft → in_progress: When worktree is created
        - in_progress → completed: When all tests pass
        
        Args:
            spec_id: SPEC identifier
            
        Returns:
            Dict with transitioned, old_status, new_status
        """
        spec_info = self.get_spec(spec_id)
        if not spec_info:
            return {"transitioned": False, "error": f"SPEC {spec_id} not found"}
        
        current_status = spec_info.get("status", "draft")
        new_status = current_status
        
        # Check completion
        completion = self.detect_completion(spec_id)
        
        if current_status == "draft":
            # Check if worktree exists → in_progress
            worktree_path = self.project_path / "worktrees" / spec_id
            if worktree_path.exists():
                new_status = SPECStatus.IN_PROGRESS.value
        
        elif current_status == "in_progress":
            # Check if implementation complete → completed
            if completion.get("is_complete"):
                new_status = SPECStatus.COMPLETED.value
        
        # Apply transition
        if new_status != current_status:
            self.update_status(spec_id, SPECStatus(new_status))
            self._ctx_manager.add_action(
                f"Auto-transitioned SPEC {spec_id}: {current_status} → {new_status}",
                "spec"
            )
            return {
                "transitioned": True,
                "old_status": current_status,
                "new_status": new_status,
                "spec_id": spec_id,
            }
        
        return {
            "transitioned": False,
            "current_status": current_status,
            "completion": completion,
            "spec_id": spec_id,
        }
    
    def batch_auto_transition(self) -> dict[str, Any]:
        """Auto-transition all SPECs that qualify.
        
        Returns:
            Dict with transitioned list and skipped list
        """
        specs = self.list_specs()
        transitioned = []
        skipped = []
        
        for spec in specs:
            spec_id = spec.get("id")
            if not spec_id:
                continue
                
            result = self.auto_transition(spec_id)
            
            if result.get("transitioned"):
                transitioned.append(result)
            else:
                skipped.append(result)
        
        return {
            "transitioned": transitioned,
            "skipped": skipped,
            "total_processed": len(specs),
        }
