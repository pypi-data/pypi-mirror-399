"""Plan generation and management."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import questionary
from rich.console import Console
from rich.panel import Panel

console = Console()


# Predefined templates for different job targets
JOB_TEMPLATES = {
    "backend": {
        "title": "백엔드 개발자",
        "skills": ["Python", "FastAPI", "Django", "PostgreSQL", "Docker", "AWS"],
        "project_types": [
            {"name": "REST API 서버", "phases": ["설계", "구현", "테스트", "배포"]},
            {"name": "마이크로서비스", "phases": ["설계", "서비스 분리", "통신 구현", "배포"]},
            {"name": "데이터 파이프라인", "phases": ["데이터 수집", "ETL", "저장", "시각화"]},
        ]
    },
    "frontend": {
        "title": "프론트엔드 개발자",
        "skills": ["React", "TypeScript", "Next.js", "Tailwind CSS", "Vite"],
        "project_types": [
            {"name": "SPA 웹앱", "phases": ["UI 설계", "컴포넌트 개발", "상태 관리", "최적화"]},
            {"name": "대시보드", "phases": ["레이아웃", "차트 구현", "필터링", "반응형"]},
            {"name": "포트폴리오 사이트", "phases": ["디자인", "애니메이션", "SEO", "배포"]},
        ]
    },
    "fullstack": {
        "title": "풀스택 개발자",
        "skills": ["React", "Node.js", "TypeScript", "PostgreSQL", "Docker"],
        "project_types": [
            {"name": "SaaS 웹서비스", "phases": ["기획", "백엔드", "프론트엔드", "배포"]},
            {"name": "실시간 채팅앱", "phases": ["설계", "백엔드", "프론트엔드", "WebSocket"]},
            {"name": "커머스 플랫폼", "phases": ["상품 관리", "결제", "주문", "관리자"]},
        ]
    },
    "data": {
        "title": "데이터 엔지니어/사이언티스트",
        "skills": ["Python", "Pandas", "SQL", "Spark", "Airflow", "ML"],
        "project_types": [
            {"name": "ML 모델 서빙", "phases": ["데이터 수집", "모델 학습", "API 개발", "배포"]},
            {"name": "분석 대시보드", "phases": ["데이터 수집", "분석", "시각화", "인사이트"]},
            {"name": "추천 시스템", "phases": ["데이터 준비", "알고리즘", "평가", "서빙"]},
        ]
    },
    "devops": {
        "title": "DevOps/SRE 엔지니어",
        "skills": ["Docker", "Kubernetes", "Terraform", "AWS", "GitHub Actions", "Prometheus"],
        "project_types": [
            {"name": "CI/CD 파이프라인", "phases": ["설계", "빌드 자동화", "테스트 자동화", "배포 자동화"]},
            {"name": "인프라 자동화", "phases": ["IaC 설계", "Terraform 구현", "모니터링", "문서화"]},
            {"name": "컨테이너 오케스트레이션", "phases": ["Docker 구성", "K8s 클러스터", "서비스 배포", "스케일링"]},
        ]
    },
    "mobile": {
        "title": "모바일 개발자",
        "skills": ["React Native", "Flutter", "Swift", "Kotlin", "Firebase", "REST API"],
        "project_types": [
            {"name": "크로스플랫폼 앱", "phases": ["UI 설계", "네비게이션", "API 연동", "스토어 배포"]},
            {"name": "네이티브 iOS/Android", "phases": ["화면 설계", "핵심 기능", "푸시 알림", "최적화"]},
            {"name": "실시간 채팅 앱", "phases": ["UI 구현", "인증", "메시지 기능", "알림"]},
        ]
    },
    "aiml": {
        "title": "AI/ML 엔지니어",
        "skills": ["Python", "PyTorch", "TensorFlow", "Scikit-learn", "OpenAI API", "LangChain"],
        "project_types": [
            {"name": "LLM 애플리케이션", "phases": ["프롬프트 설계", "RAG 구현", "평가", "배포"]},
            {"name": "컴퓨터 비전", "phases": ["데이터 수집", "모델 학습", "추론 최적화", "서빙"]},
            {"name": "ML 파이프라인", "phases": ["데이터 전처리", "모델 훈련", "평가", "MLOps"]},
        ]
    },
    "game": {
        "title": "게임 개발자",
        "skills": ["Unity", "C#", "Unreal", "C++", "Blender", "Photoshop"],
        "project_types": [
            {"name": "2D 플랫포머", "phases": ["기획", "캐릭터 구현", "레벨 디자인", "폴리싱"]},
            {"name": "3D 액션 게임", "phases": ["프로토타입", "캐릭터/전투", "환경 구축", "최적화"]},
            {"name": "모바일 캐주얼", "phases": ["게임 디자인", "핵심 루프", "수익화", "출시"]},
        ]
    },
}


def generate_plan_interactive(project_path: str = ".") -> dict:
    """Generate plan.json through interactive prompts."""
    
    console.print(Panel.fit(
        "[bold cyan]CheerU-ADK Plan Generator[/bold cyan]\n\n"
        "몇 가지 질문에 답하면 프로젝트 계획을 자동으로 생성합니다.",
        border_style="cyan"
    ))
    console.print()
    
    # 1. Project name
    project_name = questionary.text(
        "프로젝트 이름을 입력하세요:",
        default=Path(project_path).resolve().name
    ).ask()
    
    if not project_name:
        raise KeyboardInterrupt()
    
    # 2. Target job
    job_choices = [
        questionary.Choice(f"🔧 {v['title']}", value=k)
        for k, v in JOB_TEMPLATES.items()
    ]
    
    target_job = questionary.select(
        "목표 직무를 선택하세요:",
        choices=job_choices
    ).ask()
    
    if not target_job:
        raise KeyboardInterrupt()
    
    job_template = JOB_TEMPLATES[target_job]
    
    # 3. Project type
    project_type_choices = [
        questionary.Choice(pt["name"], value=pt)
        for pt in job_template["project_types"]
    ]
    
    project_type = questionary.select(
        "프로젝트 유형을 선택하세요:",
        choices=project_type_choices
    ).ask()
    
    if not project_type:
        raise KeyboardInterrupt()
    
    # 4. Tech stack selection
    selected_skills = questionary.checkbox(
        "사용할 기술 스택을 선택하세요:",
        choices=job_template["skills"]
    ).ask()
    
    if selected_skills is None:
        raise KeyboardInterrupt()
    
    # 5. Difficulty
    difficulty = questionary.select(
        "난이도를 선택하세요:",
        choices=[
            questionary.Choice("🟢 초급 (기본 기능 구현)", value="beginner"),
            questionary.Choice("🟡 중급 (추가 기능 + 테스트)", value="intermediate"),
            questionary.Choice("🔴 고급 (CI/CD + 문서화)", value="advanced"),
        ]
    ).ask()
    
    if not difficulty:
        raise KeyboardInterrupt()
    
    # Generate phases and tasks
    phases = []
    for i, phase_name in enumerate(project_type["phases"], 1):
        tasks = generate_tasks_for_phase(phase_name, difficulty)
        phases.append({
            "id": f"phase-{i}",
            "title": f"Phase {i}: {phase_name}",
            "status": "pending",
            "tasks": tasks
        })
    
    # Build plan
    plan = {
        "project_name": project_name,
        "target_job": job_template["title"],
        "project_type": project_type["name"],
        "tech_stack": selected_skills,
        "difficulty": difficulty,
        "phases": phases,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }
    
    return plan


def generate_tasks_for_phase(phase_name: str, difficulty: str) -> list[dict]:
    """Generate tasks for a phase based on difficulty."""
    
    # Base tasks for each phase type
    task_templates = {
        "설계": ["요구사항 분석", "아키텍처 설계", "API 명세 작성"],
        "구현": ["프로젝트 셋업", "핵심 기능 구현", "에러 처리"],
        "테스트": ["단위 테스트 작성", "통합 테스트", "버그 수정"],
        "배포": ["Docker 설정", "배포 스크립트", "모니터링 설정"],
        "UI 설계": ["와이어프레임", "컴포넌트 설계", "디자인 시스템"],
        "컴포넌트 개발": ["공통 컴포넌트", "페이지 컴포넌트", "라우팅"],
        "상태 관리": ["상태 설계", "API 연동", "캐싱"],
        "최적화": ["코드 스플리팅", "이미지 최적화", "성능 측정"],
        "기획": ["시장 조사", "기능 정의", "로드맵 작성"],
        "데이터 수집": ["데이터 소스 파악", "수집 스크립트", "저장소 설정"],
        "분석": ["탐색적 분석", "통계 분석", "인사이트 도출"],
        "시각화": ["차트 설계", "대시보드 구현", "인터랙션"],
    }
    
    # Get base tasks or generate generic ones
    base_tasks = task_templates.get(phase_name, [
        f"{phase_name} 준비",
        f"{phase_name} 구현",
        f"{phase_name} 검증"
    ])
    
    tasks = []
    for i, task_name in enumerate(base_tasks, 1):
        task = {
            "id": f"{phase_name.lower().replace(' ', '-')}-{i}",
            "title": task_name,
            "status": "pending",
            "description": ""
        }
        tasks.append(task)
    
    # Add extra tasks for higher difficulty
    if difficulty in ["intermediate", "advanced"]:
        tasks.append({
            "id": f"{phase_name.lower().replace(' ', '-')}-test",
            "title": f"{phase_name} 테스트 코드 작성",
            "status": "pending",
            "description": ""
        })
    
    if difficulty == "advanced":
        tasks.append({
            "id": f"{phase_name.lower().replace(' ', '-')}-doc",
            "title": f"{phase_name} 문서화",
            "status": "pending",
            "description": ""
        })
    
    return tasks


def save_plan(plan: dict, project_path: str = ".") -> Path:
    """Save plan to .cheeru/plan.json."""
    cheeru_dir = Path(project_path) / ".cheeru"
    cheeru_dir.mkdir(exist_ok=True)
    
    plan_path = cheeru_dir / "plan.json"
    plan_path.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    return plan_path


def load_plan(project_path: str = ".") -> Optional[dict]:
    """Load plan from .cheeru/plan.json."""
    plan_path = Path(project_path) / ".cheeru" / "plan.json"
    
    if plan_path.exists():
        return json.loads(plan_path.read_text(encoding="utf-8"))
    return None
