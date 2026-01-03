"""Main CLI for CheerU-ADK."""

import click
from rich.console import Console
from rich.panel import Panel

from cheeru_adk import __version__

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="cheeru-adk")
def cli():
    """🎉 CheerU-ADK: 취업준비생을 위한 AI 포트폴리오 자동 구축 프레임워크."""
    pass


@cli.command()
@click.argument("path", default=".", type=click.Path())
@click.option("--force", "-f", is_flag=True, help="기존 설정 덮어쓰기")
@click.option("--interactive", "-i", is_flag=True, help="인터랙티브 모드로 설정")
def init(path: str, force: bool, interactive: bool):
    """프로젝트에 CheerU-ADK를 설정합니다.
    
    PATH: 설정할 프로젝트 경로 (기본값: 현재 디렉토리)
    """
    from cheeru_adk.core.project import initialize_project
    from cheeru_adk.core.state import ContextManager
    import questionary
    
    project_path = path
    
    # Interactive mode
    if interactive:
        console.print(Panel.fit(
            "[bold cyan]CheerU-ADK 인터랙티브 설정[/bold cyan]",
            border_style="cyan"
        ))
        console.print()
        
        # Project path
        project_path = questionary.path(
            "프로젝트 경로를 선택하세요:",
            default=path
        ).ask()
        
        if not project_path:
            raise click.Abort()
        
        # Confirm
        if not questionary.confirm(f"'{project_path}'에 CheerU-ADK를 설정하시겠습니까?").ask():
            raise click.Abort()
    
    try:
        result = initialize_project(project_path, force=force)
        
        console.print(Panel.fit(
            "[bold green]✅ CheerU-ADK 설정 완료![/bold green]\n\n"
            "[bold]생성된 파일:[/bold]\n"
            + "\n".join(f"  • {f}" for f in result["created_files"][:10])
            + (f"\n  ... 외 {len(result['created_files']) - 10}개" 
               if len(result["created_files"]) > 10 else ""),
            title="🎉 CheerU-ADK",
            border_style="green",
        ))
        
        # Initialize context
        ctx = ContextManager(project_path)
        ctx.add_action("Initialized CheerU-ADK project", "init")
        
        console.print("\n[bold]다음 단계:[/bold]")
        console.print("  1. [cyan]cheeru-adk plan generate[/cyan] - 프로젝트 계획 생성")
        console.print("  2. [cyan]cheeru-adk status[/cyan] - 진행 상태 확인")
        console.print("  3. Gemini CLI에서 [cyan]/cheeru-start[/cyan] 명령 실행\n")
        
    except FileExistsError as e:
        console.print(f"[yellow]⚠️ {e}[/yellow]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]❌ 오류: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.argument("path", default=".", type=click.Path())
def update(path: str):
    """템플릿을 최신 버전으로 업데이트합니다."""
    from cheeru_adk.core.project import update_templates
    
    try:
        result = update_templates(path)
        console.print(f"[green]✅ {len(result['updated_files'])}개 파일 업데이트 완료![/green]")
    except Exception as e:
        console.print(f"[red]❌ 오류: {e}[/red]")
        raise click.Abort()


@cli.command()
def info():
    """현재 프로젝트의 CheerU-ADK 설정 정보를 표시합니다."""
    from pathlib import Path
    import json
    
    config_path = Path(".cheeru/config.json")
    
    if not config_path.exists():
        console.print("[yellow]⚠️ CheerU-ADK가 설정되지 않은 프로젝트입니다.[/yellow]")
        console.print("  [cyan]cheeru-adk init[/cyan] 명령으로 설정하세요.")
        return
    
    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)
    
    console.print(Panel.fit(
        f"[bold]프로젝트:[/bold] {config.get('project_name', 'N/A')}\n"
        f"[bold]버전:[/bold] {config.get('cheeru_version', 'N/A')}\n"
        f"[bold]생성일:[/bold] {config.get('created_at', 'N/A')}",
        title="🎉 CheerU-ADK 정보",
        border_style="blue",
    ))


@cli.command()
def status():
    """현재 프로젝트 상태를 표시합니다."""
    from rich.table import Table
    from rich.progress import Progress, BarColumn, TextColumn
    from cheeru_adk.core.state import ContextManager
    
    ctx = ContextManager()
    
    # Check if CheerU-ADK is initialized
    if not ctx.cheeru_dir.exists():
        console.print("[yellow]⚠️ CheerU-ADK가 설정되지 않은 프로젝트입니다.[/yellow]")
        console.print("  [cyan]cheeru-adk init[/cyan] 명령으로 설정하세요.")
        return
    
    status_data = ctx.get_status()
    progress = status_data.get("progress", {})
    
    # Header
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]{status_data.get('project_name', 'Unknown Project')}[/bold cyan]",
        title="📊 프로젝트 상태",
        border_style="cyan",
    ))
    
    # Progress
    total = progress.get("total_tasks", 0)
    completed = progress.get("completed_tasks", 0)
    percentage = progress.get("percentage", 0)
    
    console.print(f"\n[bold]📈 진행률:[/bold] {completed}/{total} ({percentage}%)")
    
    if total > 0:
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
            transient=True,
        ) as prog:
            task = prog.add_task("Progress", total=100)
            prog.update(task, completed=percentage)
    
    # Current Phase
    if status_data.get("current_phase"):
        console.print(f"\n[bold]🎯 현재 Phase:[/bold] {status_data['current_phase']}")
    
    # Recent Actions
    recent = status_data.get("recent_actions", [])[:5]
    if recent:
        console.print("\n[bold]📝 최근 작업:[/bold]")
        table = Table(show_header=True, header_style="bold magenta", box=None)
        table.add_column("시간", style="dim", width=20)
        table.add_column("작업", style="white")
        
        for action in recent:
            timestamp = action.get("timestamp", "")[:16].replace("T", " ")
            table.add_row(timestamp, action.get("action", ""))
        
        console.print(table)
    
    # Blockers
    blockers = [b for b in status_data.get("blockers", []) if not b.get("resolved")]
    if blockers:
        console.print("\n[bold red]🚧 Blockers:[/bold red]")
        for i, blocker in enumerate(blockers):
            console.print(f"  {i+1}. {blocker.get('description', '')}")
    
    # Session info
    session = status_data.get("session_count", 0)
    console.print(f"\n[dim]세션 #{session} | 마지막 업데이트: {status_data.get('last_updated', 'N/A')[:16].replace('T', ' ')}[/dim]")
    console.print()


@cli.command()
@click.option("--auto", "-a", is_flag=True, help="자동으로 커밋 메시지 생성")
@click.option("--message", "-m", default=None, help="커밋 메시지")
def commit(auto: bool, message: str):
    """스마트 커밋을 생성합니다."""
    from cheeru_adk.integrations.github import GitCommit
    from cheeru_adk.core.state import ContextManager
    
    gc = GitCommit()
    ctx = ContextManager()
    
    # Check for staged files
    staged = gc.get_staged_files()
    if not staged:
        console.print("[yellow]⚠️ 스테이징된 파일이 없습니다.[/yellow]")
        console.print("  [cyan]git add <files>[/cyan] 명령으로 파일을 추가하세요.")
        return
    
    console.print(f"[bold]📁 스테이징된 파일 ({len(staged)}개):[/bold]")
    for f in staged[:5]:
        console.print(f"  • {f}")
    if len(staged) > 5:
        console.print(f"  ... 외 {len(staged) - 5}개")
    
    # Generate or use message
    if auto or not message:
        message = gc.generate_message()
        console.print(f"\n[bold]💬 생성된 메시지:[/bold] {message}")
    
    # Confirm
    if not auto:
        if not click.confirm("\n이 메시지로 커밋하시겠습니까?"):
            raise click.Abort()
    
    # Commit
    result = gc.commit(message=message)
    
    if result["success"]:
        console.print(f"\n[green]✅ 커밋 완료![/green]")
        console.print(f"  {result['message']}")
        
        # Update context
        ctx.add_action(f"Committed: {result['message']}", "commit")
    else:
        console.print(f"\n[red]❌ 커밋 실패: {result.get('error', 'Unknown error')}[/red]")
        raise click.Abort()


@cli.group()
def plan():
    """프로젝트 계획 관련 명령어."""
    pass


@plan.command(name="sync")
def plan_sync():
    """plan.json을 GitHub Issues로 동기화합니다."""
    from cheeru_adk.integrations.github import GitHubIntegration
    from cheeru_adk.core.state import ContextManager
    from pathlib import Path
    
    ctx = ContextManager()
    plan_path = Path(".cheeru/plan.json")
    
    # Check gh CLI
    if not GitHubIntegration.is_gh_available():
        console.print("[red]❌ gh CLI가 설치되지 않았거나 인증되지 않았습니다.[/red]")
        console.print("  [cyan]gh auth login[/cyan] 명령으로 인증하세요.")
        raise click.Abort()
    
    # Check plan.json
    if not plan_path.exists():
        console.print("[yellow]⚠️ plan.json이 없습니다.[/yellow]")
        console.print("  먼저 계획을 생성해주세요.")
        return
    
    console.print("[bold]🔄 GitHub Issues 동기화 중...[/bold]\n")
    
    github = GitHubIntegration()
    result = github.sync_plan_to_issues(str(plan_path))
    
    if result["success"]:
        console.print(f"[green]✅ 동기화 완료![/green]")
        console.print(f"  • 생성됨: {len(result['created'])}개")
        console.print(f"  • 건너뜀: {len(result['skipped'])}개 (이미 존재)")
        
        for title in result["created"][:5]:
            console.print(f"    [green]+[/green] {title}")
        
        ctx.add_action(f"Synced plan to GitHub: {len(result['created'])} issues created", "sync")
    else:
        console.print(f"[red]❌ 동기화 실패: {result.get('error', 'Unknown error')}[/red]")


@plan.command(name="generate")
def plan_generate():
    """인터랙티브하게 프로젝트 계획을 생성합니다."""
    from cheeru_adk.core.plan import generate_plan_interactive, save_plan
    from cheeru_adk.core.state import ContextManager
    
    ctx = ContextManager()
    
    try:
        plan = generate_plan_interactive()
        plan_path = save_plan(plan)
        
        console.print(f"\n[green]✅ 계획이 생성되었습니다![/green]")
        console.print(f"  파일: {plan_path}")
        console.print(f"\n[bold]프로젝트:[/bold] {plan['project_name']}")
        console.print(f"[bold]목표 직무:[/bold] {plan['target_job']}")
        console.print(f"[bold]프로젝트 유형:[/bold] {plan['project_type']}")
        console.print(f"[bold]기술 스택:[/bold] {', '.join(plan['tech_stack'])}")
        console.print(f"[bold]총 Phase:[/bold] {len(plan['phases'])}개")
        
        total_tasks = sum(len(p['tasks']) for p in plan['phases'])
        console.print(f"[bold]총 Task:[/bold] {total_tasks}개")
        
        console.print("\n[bold]다음 단계:[/bold]")
        console.print("  1. [cyan]cheeru-adk plan show[/cyan] - 계획 확인")
        console.print("  2. [cyan]cheeru-adk plan sync[/cyan] - GitHub Issues로 동기화")
        
        ctx.add_action(f"Generated plan: {plan['project_name']}", "plan")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ 계획 생성이 취소되었습니다.[/yellow]")
        raise click.Abort()


@plan.command(name="show")
def plan_show():
    """현재 계획을 표시합니다."""
    from cheeru_adk.core.plan import load_plan
    from rich.table import Table
    from rich.tree import Tree
    
    plan = load_plan()
    
    if not plan:
        console.print("[yellow]⚠️ plan.json이 없습니다.[/yellow]")
        console.print("  [cyan]cheeru-adk plan generate[/cyan] 명령으로 생성하세요.")
        return
    
    # Header
    console.print(Panel.fit(
        f"[bold cyan]{plan.get('project_name', 'Unknown')}[/bold cyan]\n"
        f"[dim]{plan.get('target_job', '')} | {plan.get('project_type', '')}[/dim]",
        title="📋 프로젝트 계획",
        border_style="cyan"
    ))
    
    console.print(f"\n[bold]기술 스택:[/bold] {', '.join(plan.get('tech_stack', []))}")
    console.print(f"[bold]난이도:[/bold] {plan.get('difficulty', 'N/A')}")
    
    # Phases and tasks
    tree = Tree("[bold]📁 Phases[/bold]")
    
    for phase in plan.get("phases", []):
        status_icon = "✅" if phase.get("status") == "completed" else "🔄" if phase.get("status") == "in_progress" else "⬜"
        phase_branch = tree.add(f"{status_icon} [bold]{phase.get('title', 'Unknown')}[/bold]")
        
        for task in phase.get("tasks", []):
            task_status = task.get("status", "pending")
            task_icon = "✅" if task_status == "completed" else "🔄" if task_status == "in_progress" else "⬜"
            phase_branch.add(f"{task_icon} {task.get('title', 'Unknown')}")
    
    console.print(tree)
    
    # Stats
    total_tasks = sum(len(p.get('tasks', [])) for p in plan.get('phases', []))
    completed = sum(
        1 for p in plan.get('phases', [])
        for t in p.get('tasks', [])
        if t.get('status') == 'completed'
    )
    
    console.print(f"\n[dim]진행률: {completed}/{total_tasks} ({round(completed/total_tasks*100, 1) if total_tasks > 0 else 0}%)[/dim]")


# ============================================================
# Task Commands
# ============================================================

@cli.group()
def task():
    """태스크 관리 명령어."""
    pass


@task.command(name="list")
@click.option("--status", "-s", type=click.Choice(["all", "pending", "in_progress", "completed"]), default="all")
def task_list(status: str):
    """모든 태스크를 표시합니다."""
    from cheeru_adk.core.state import TaskManager
    from rich.table import Table
    
    tm = TaskManager()
    
    status_filter = None if status == "all" else status
    tasks = tm.list_tasks(status_filter)
    
    if not tasks:
        if status_filter:
            console.print(f"[yellow]⚠️ '{status}' 상태의 태스크가 없습니다.[/yellow]")
        else:
            console.print("[yellow]⚠️ plan.json이 없거나 태스크가 없습니다.[/yellow]")
            console.print("  [cyan]cheeru-adk plan generate[/cyan] 명령으로 계획을 생성하세요.")
        return
    
    # Build table
    table = Table(title="📋 태스크 목록", show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4)
    table.add_column("상태", width=6)
    table.add_column("태스크", style="white")
    table.add_column("Phase", style="dim")
    
    status_icons = {
        "pending": "[dim]⬜[/dim]",
        "in_progress": "[yellow]🔄[/yellow]",
        "completed": "[green]✅[/green]",
    }
    
    for t in tasks:
        icon = status_icons.get(t["status"], "⬜")
        table.add_row(
            str(t["index"]),
            icon,
            t["title"],
            t["phase"].replace("Phase ", "P")
        )
    
    console.print(table)
    
    # Progress summary
    progress = tm.get_progress()
    console.print(f"\n[dim]진행률: {progress['completed']}/{progress['total']} ({progress['percentage']}%)[/dim]")


@task.command(name="start")
@click.argument("task_id")
def task_start(task_id: str):
    """태스크를 진행중으로 표시합니다."""
    from cheeru_adk.core.state import TaskManager
    from cheeru_adk.core.state import ContextManager
    
    tm = TaskManager()
    ctx = ContextManager()
    
    task_info = tm.get_task(task_id)
    if not task_info:
        console.print(f"[red]❌ 태스크 '{task_id}'를 찾을 수 없습니다.[/red]")
        console.print("  [cyan]cheeru-adk task list[/cyan] 명령으로 태스크 목록을 확인하세요.")
        return
    
    if tm.start_task(task_id):
        console.print(f"[yellow]🔄 시작: {task_info['title']}[/yellow]")
        ctx.add_action(f"Started task: {task_info['title']}", "task")
    else:
        console.print("[red]❌ 태스크 상태 업데이트 실패[/red]")


@task.command(name="complete")
@click.argument("task_id")
def task_complete(task_id: str):
    """태스크를 완료로 표시합니다."""
    from cheeru_adk.core.state import TaskManager
    from cheeru_adk.core.state import ContextManager
    
    tm = TaskManager()
    ctx = ContextManager()
    
    task_info = tm.get_task(task_id)
    if not task_info:
        console.print(f"[red]❌ 태스크 '{task_id}'를 찾을 수 없습니다.[/red]")
        return
    
    if tm.complete_task(task_id):
        console.print(f"[green]✅ 완료: {task_info['title']}[/green]")
        ctx.add_action(f"Completed task: {task_info['title']}", "task")
        
        # Show progress
        progress = tm.get_progress()
        console.print(f"[dim]진행률: {progress['completed']}/{progress['total']} ({progress['percentage']}%)[/dim]")
    else:
        console.print("[red]❌ 태스크 상태 업데이트 실패[/red]")


@task.command(name="reset")
@click.argument("task_id")
def task_reset(task_id: str):
    """태스크를 대기중으로 초기화합니다."""
    from cheeru_adk.core.state import TaskManager
    
    tm = TaskManager()
    
    task_info = tm.get_task(task_id)
    if not task_info:
        console.print(f"[red]❌ 태스크 '{task_id}'를 찾을 수 없습니다.[/red]")
        return
    
    if tm.reset_task(task_id):
        console.print(f"[dim]⬜ 초기화: {task_info['title']}[/dim]")
    else:
        console.print("[red]❌ 태스크 상태 업데이트 실패[/red]")


# ============================================================
# Config Commands
# ============================================================

@cli.group()
def config():
    """설정 관리 명령어."""
    pass


@config.command(name="list")
def config_list():
    """모든 설정을 표시합니다."""
    from cheeru_adk.core.state import ConfigManager
    from rich.table import Table
    
    cm = ConfigManager()
    settings = cm.list_all()
    
    table = Table(title="⚙️ 설정", show_header=True, header_style="bold cyan")
    table.add_column("키", style="cyan")
    table.add_column("값", style="white")
    
    for key, value in sorted(settings.items()):
        table.add_row(key, str(value))
    
    console.print(table)


@config.command(name="get")
@click.argument("key")
def config_get(key: str):
    """설정 값을 조회합니다."""
    from cheeru_adk.core.state import ConfigManager
    
    cm = ConfigManager()
    value = cm.get(key)
    
    if value is None:
        console.print(f"[yellow]⚠️ 설정 '{key}'를 찾을 수 없습니다.[/yellow]")
    else:
        console.print(f"[cyan]{key}[/cyan] = [white]{value}[/white]")


@config.command(name="set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """설정 값을 변경합니다."""
    from cheeru_adk.core.state import ConfigManager
    
    cm = ConfigManager()
    
    if cm.set(key, value):
        console.print(f"[green]✅ 설정 완료: {key} = {value}[/green]")
    else:
        console.print(f"[red]❌ 설정 실패[/red]")


# ============================================================
# Portfolio Commands
# ============================================================

@cli.group()
def portfolio():
    """포트폴리오 생성 명령어."""
    pass


@portfolio.command(name="generate")
def portfolio_generate():
    """현재 프로젝트의 포트폴리오를 생성합니다."""
    from cheeru_adk.core.portfolio import generate_portfolio
    
    try:
        data = generate_portfolio()
        
        console.print(Panel.fit(
            f"[bold green]✅ 포트폴리오 생성 완료![/bold green]\n\n"
            f"[bold]프로젝트:[/bold] {data['project_name']}\n"
            f"[bold]대상 직무:[/bold] {data['target_job']}\n"
            f"[bold]완료율:[/bold] {data['stats']['completion_rate']}%\n"
            f"[bold]태스크:[/bold] {data['stats']['completed_tasks']}/{data['stats']['total_tasks']}",
            title="📋 포트폴리오",
            border_style="green"
        ))
        
        console.print("\n[bold]다음 단계:[/bold]")
        console.print("  [cyan]cheeru-adk portfolio export --format md[/cyan] - 마크다운 내보내기")
        console.print("  [cyan]cheeru-adk portfolio export --format json[/cyan] - JSON 내보내기")
        
    except FileNotFoundError as e:
        console.print(f"[yellow]⚠️ {e}[/yellow]")


@portfolio.command(name="export")
@click.option("--format", "-f", type=click.Choice(["md", "json"]), default="md", help="출력 형식")
@click.option("--output", "-o", default=None, help="출력 파일 경로")
def portfolio_export(format: str, output: str):
    """포트폴리오를 파일로 내보냅니다."""
    from cheeru_adk.core.portfolio import generate_portfolio, export_portfolio_markdown, export_portfolio_json
    from pathlib import Path
    
    try:
        data = generate_portfolio()
        
        # Determine output path
        if not output:
            output = f"PORTFOLIO.{format}"
        
        if format == "md":
            content = export_portfolio_markdown(data, output)
            console.print(f"[green]✅ 마크다운 포트폴리오 생성: {output}[/green]")
        else:
            content = export_portfolio_json(data, output)
            console.print(f"[green]✅ JSON 포트폴리오 생성: {output}[/green]")
        
        console.print(f"[dim]파일 크기: {len(content)} bytes[/dim]")
        
    except FileNotFoundError as e:
        console.print(f"[yellow]⚠️ {e}[/yellow]")


@portfolio.command(name="preview")
def portfolio_preview():
    """포트폴리오 미리보기를 표시합니다."""
    from cheeru_adk.core.portfolio import generate_portfolio, export_portfolio_markdown
    from rich.markdown import Markdown
    
    try:
        data = generate_portfolio()
        md_content = export_portfolio_markdown(data)
        
        console.print(Markdown(md_content))
        
    except FileNotFoundError as e:
        console.print(f"[yellow]⚠️ {e}[/yellow]")


# ============================================================
# TDD Commands (Test Driven Development)
# ============================================================

@cli.group()
def tdd():
    """TDD 워크플로우 관리 명령어."""
    pass


@tdd.command(name="auto")
@click.argument("feature")
def tdd_auto(feature: str):
    """[Auto-TDD] AI가 자동으로 TDD 사이클을 수행합니다."""
    console.print(Panel(
        f"[bold]🤖 Auto-TDD 시작: {feature}[/bold]\n"
        "AI가 RED-GREEN-REFACTOR 사이클을 자동으로 수행합니다.",
        title="Auto-TDD",
        border_style="magenta"
    ))
    
    # 1. Start Cycle
    from cheeru_adk.core.tdd import TDDManager
    tm = TDDManager()
    state = tm.start_cycle(feature)
    
    console.print(f"\n[bold magenta]Phase 1: RED (Failing Test)[/bold magenta]")
    console.print("AI 에이전트에게 테스트 작성을 요청합니다...")
    console.print("[dim]Hint: @tdd-expert에게 요청하세요.[/dim]")


@tdd.command(name="start")
@click.argument("feature")
def tdd_start(feature: str):
    """새로운 TDD 사이클을 시작합니다."""
    from cheeru_adk.core.tdd import TDDManager
    
    tm = TDDManager()
    tm.start_cycle(feature)
    
    console.print(f"[green]✅ TDD 사이클 시작: {feature}[/green]")
    console.print("👉 [bold]RED Phase[/bold]: 실패하는 테스트를 작성하세요.")


@tdd.command(name="run")
@click.option("--file", "-f", help="실행할 테스트 파일")
def tdd_run(file: str):
    """현재 TDD 단계의 테스트를 실행하고 상태를 업데이트합니다."""
    from cheeru_adk.core.tdd import TDDManager, TDDPhase
    
    tm = TDDManager()
    state = tm.get_state()
    
    if not state:
        console.print("[yellow]⚠️ 진행 중인 TDD 사이클이 없습니다.[/yellow]")
        console.print("  [cyan]cheeru-adk tdd start <feature>[/cyan] 명령으로 시작하세요.")
        return

    console.print(f"[bold]Running TDD Phase: {state.phase.value}[/bold]...")
    
    # Run test
    success, output = tm.run_test(file)
    
    # Print Output (Truncated)
    console.print(Panel(output[-500:] if len(output) > 500 else output, title="Pytest Output"))
    
    # Check result
    if success:
        console.print("[green]✅ 테스트 통과![/green]")
    else:
        console.print("[red]❌ 테스트 실패[/red]")
        
    # Advance phase logic
    msg = tm.advance_phase()
    console.print(f"\n[bold cyan]👉 {msg}[/bold cyan]")


@tdd.command(name="status")
def tdd_status():
    """현재 TDD 상태를 확인합니다."""
    from cheeru_adk.core.tdd import TDDManager
    
    tm = TDDManager()
    state = tm.get_state()
    
    if not state:
        console.print("[dim]진행 중인 TDD 사이클이 없습니다.[/dim]")
        return
        
    console.print(Panel(
        f"[bold]Feature:[/bold] {state.feature_name}\n"
        f"[bold]Phase:[/bold] {state.phase.value}\n"
        f"[bold]Test File:[/bold] {state.test_file or 'Not set'}\n"
        f"[bold]Started at:[/bold] {state.started_at}",
        title="🔄 TDD Status",
        border_style="cyan"
    ))


# ============================================================
# SPEC Commands (SPEC-First Development)
# ============================================================

@cli.group()
def spec():
    """SPEC 관리 명령어 (SPEC-First 개발)."""
    pass


@spec.command(name="new")
@click.argument("title")
@click.option("--lang", default="Python", help="주 프로그래밍 언어")
@click.option("--framework", default="FastAPI", help="프레임워크")
@click.option("--worktree", "-w", is_flag=True, help="SPEC 확인 후 Worktree 자동 생성")
def spec_new(title: str, lang: str, framework: str, worktree: bool):
    """새로운 SPEC 문서를 생성합니다 (EARS 포맷)."""
    from cheeru_adk.core.spec import SPECManager
    import questionary
    
    sm = SPECManager()
    spec_id = sm.create(title, language=lang, framework=framework)
    
    console.print(Panel(
        f"[bold green]✅ SPEC 생성 완료![/bold green]\n\n"
        f"[bold]ID:[/bold] {spec_id}\n"
        f"[bold]Title:[/bold] {title}\n"
        f"[bold]Path:[/bold] .cheeru/specs/{spec_id}/spec.md",
        title="📋 SPEC Created",
        border_style="green"
    ))
    
    # Worktree auto-creation with confirmation
    if worktree:
        console.print("\n[bold yellow]⏳ SPEC 문서를 먼저 편집하세요.[/bold yellow]")
        console.print(f"[dim]경로: .cheeru/specs/{spec_id}/spec.md[/dim]\n")
        
        confirm = questionary.confirm(
            "SPEC 편집이 완료되었나요? Worktree를 생성할까요?",
            default=True
        ).ask()
        
        if confirm:
            from cheeru_adk.core.worktree import WorktreeManager
            
            wm = WorktreeManager()
            result = wm.create(spec_id)
            
            if result.get("success"):
                console.print(Panel(
                    f"[bold green]✅ Worktree 생성 완료![/bold green]\n\n"
                    f"[bold]SPEC:[/bold] {spec_id}\n"
                    f"[bold]Branch:[/bold] {result.get('branch')}\n"
                    f"[bold]Path:[/bold] {result.get('path')}",
                    title="🌿 Worktree Created",
                    border_style="green"
                ))
                console.print("\n[bold]다음 단계:[/bold]")
                console.print(f"  1. [cyan]cd {result.get('path')}[/cyan]")
                console.print(f"  2. [cyan]cheeru-adk tdd start[/cyan] - TDD 시작")
            else:
                console.print(f"[red]❌ Worktree 생성 실패: {result.get('error')}[/red]")
        else:
            console.print("[dim]Worktree 생성을 건너뛰었습니다.[/dim]")
    else:
        console.print("\n[bold]다음 단계:[/bold]")
        console.print(f"  1. SPEC 문서 편집: .cheeru/specs/{spec_id}/spec.md")
        console.print(f"  2. [cyan]cheeru-adk spec new \"{title}\" --worktree[/cyan] 또는")
        console.print(f"     [cyan]cheeru-adk worktree create {spec_id}[/cyan]")


@spec.command(name="list")
def spec_list():
    """모든 SPEC 문서를 나열합니다."""
    from cheeru_adk.core.spec import SPECManager
    from rich.table import Table
    
    sm = SPECManager()
    specs = sm.list_specs()
    
    if not specs:
        console.print("[dim]생성된 SPEC이 없습니다. 'cheeru-adk spec new <title>'로 생성하세요.[/dim]")
        return
    
    table = Table(title="📋 SPEC Documents")
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Status", style="yellow")
    
    for s in specs:
        table.add_row(s.get("id", "?"), s.get("title", "?"), s.get("status", "?"))
    
    console.print(table)


@spec.command(name="show")
@click.argument("spec_id")
def spec_show(spec_id: str):
    """SPEC 문서 상세 정보를 표시합니다."""
    from cheeru_adk.core.spec import SPECManager
    
    sm = SPECManager()
    info = sm.get_spec(spec_id)
    
    if not info:
        console.print(f"[red]❌ SPEC '{spec_id}'를 찾을 수 없습니다.[/red]")
        return
    
    console.print(Panel(
        f"[bold]ID:[/bold] {info.get('id')}\n"
        f"[bold]Title:[/bold] {info.get('title')}\n"
        f"[bold]Status:[/bold] {info.get('status')}\n"
        f"[bold]Path:[/bold] {info.get('path')}",
        title=f"📋 {spec_id}",
        border_style="cyan"
    ))


@spec.command(name="auto-transition")
@click.argument("spec_id", required=False)
def spec_auto_transition(spec_id: str):
    """SPEC 상태를 자동으로 전환합니다."""
    from cheeru_adk.core.spec import SPECManager
    
    sm = SPECManager()
    
    if spec_id:
        # Single SPEC
        result = sm.auto_transition(spec_id)
        
        if result.get("transitioned"):
            console.print(Panel(
                f"[bold green]✅ 상태 전환 완료![/bold green]\n\n"
                f"[bold]SPEC:[/bold] {spec_id}\n"
                f"[bold]변경:[/bold] {result['old_status']} → {result['new_status']}",
                title="🔄 Auto Transition",
                border_style="green"
            ))
        else:
            console.print(f"[yellow]ℹ️ {spec_id}: 상태 변경 없음 (현재: {result.get('current_status', 'unknown')})[/yellow]")
    else:
        # Batch all SPECs
        console.print("[bold]🔄 전체 SPEC 상태 확인 중...[/bold]")
        result = sm.batch_auto_transition()
        
        if result["transitioned"]:
            for t in result["transitioned"]:
                console.print(f"[green]✅ {t['spec_id']}: {t['old_status']} → {t['new_status']}[/green]")
        else:
            console.print("[dim]전환된 SPEC이 없습니다.[/dim]")


@spec.command(name="check")
@click.argument("spec_id")
def spec_check(spec_id: str):
    """SPEC 완료 상태를 확인합니다."""
    from cheeru_adk.core.spec import SPECManager
    
    sm = SPECManager()
    result = sm.detect_completion(spec_id)
    
    if "error" in result:
        console.print(f"[red]❌ {result['error']}[/red]")
        return
    
    criteria = result.get("criteria", {})
    
    console.print(Panel(
        f"[bold]SPEC:[/bold] {spec_id}\n"
        f"[bold]완료 여부:[/bold] {'✅ Yes' if result['is_complete'] else '❌ No'}\n\n"
        f"[bold]체크리스트:[/bold]\n"
        f"  - 테스트 존재: {'✅' if criteria.get('tests_exist') else '❌'}\n"
        f"  - 테스트 통과: {'✅' if criteria.get('tests_pass') else '❌'}\n"
        f"  - 구현 완료: {'✅' if criteria.get('implementation_exists') else '❌'}\n"
        + ("\n[bold]이슈:[/bold]\n" + "\n".join(f"  ⚠️ {i}" for i in result.get("issues", [])) if result.get("issues") else ""),
        title="🔍 Completion Check",
        border_style="cyan"
    ))


# ============================================================
# Worktree Commands (Parallel Development)
# ============================================================

@cli.group()
def worktree():
    """Git Worktree 관리 (병렬 개발)."""
    pass


@worktree.command(name="new")
@click.argument("spec_id")
@click.option("--branch", "-b", help="브랜치 이름 (기본: feature/<spec_id>)")
def worktree_new(spec_id: str, branch: str):
    """SPEC을 위한 새 worktree를 생성합니다."""
    from cheeru_adk.core.worktree import WorktreeManager
    
    wm = WorktreeManager()
    result = wm.create(spec_id, branch)
    
    if result.get("success"):
        console.print(Panel(
            f"[bold green]✅ Worktree 생성 완료![/bold green]\n\n"
            f"[bold]SPEC:[/bold] {spec_id}\n"
            f"[bold]Branch:[/bold] {result.get('branch')}\n"
            f"[bold]Path:[/bold] {result.get('path')}",
            title="🌳 Worktree Created",
            border_style="green"
        ))
        console.print(f"\n[bold]이동:[/bold] cd {result.get('path')}")
    else:
        console.print(f"[red]❌ 오류: {result.get('error', result.get('output'))}[/red]")


@worktree.command(name="list")
def worktree_list():
    """모든 worktree를 나열합니다."""
    from cheeru_adk.core.worktree import WorktreeManager
    from rich.table import Table
    
    wm = WorktreeManager()
    worktrees = wm.list_worktrees()
    
    if not worktrees:
        console.print("[dim]생성된 worktree가 없습니다.[/dim]")
        return
    
    table = Table(title="🌳 Git Worktrees")
    table.add_column("SPEC", style="cyan")
    table.add_column("Branch", style="yellow")
    table.add_column("Path")
    
    for wt in worktrees:
        spec_id = wt.get("spec_id", "-")
        branch = wt.get("branch", "detached")
        path = wt.get("path", "?")
        table.add_row(spec_id, branch, path)
    
    console.print(table)


@worktree.command(name="go")
@click.argument("spec_id")
def worktree_go(spec_id: str):
    """SPEC worktree로 이동하는 명령을 출력합니다."""
    from cheeru_adk.core.worktree import WorktreeManager
    
    wm = WorktreeManager()
    result = wm.go(spec_id)
    
    if result.get("success"):
        console.print(f"[bold]Run:[/bold] {result.get('command')}")
    else:
        console.print(f"[red]❌ {result.get('error')}[/red]")


@worktree.command(name="merge")
@click.argument("spec_id")
@click.option("--base", default="main", help="병합 대상 브랜치")
@click.option("--min-coverage", default=80, type=int, help="최소 커버리지 % (기본: 80)")
@click.option("--skip-lint", is_flag=True, help="린트 검사 스킵")
def worktree_merge(spec_id: str, base: str, min_coverage: int, skip_lint: bool):
    """SPEC worktree를 통합 테스트 후 병합합니다 (커버리지/린트 검사 포함)."""
    from cheeru_adk.core.worktree import WorktreeManager
    
    console.print(f"[bold]🔄 {spec_id} 통합 검증 중...[/bold]")
    console.print(f"[dim]  - 최소 커버리지: {min_coverage}%")
    console.print(f"  - 린트 검사: {'☐ 스킵' if skip_lint else '☑ 활성화'}[/dim]")
    
    wm = WorktreeManager()
    result = wm.merge(spec_id, base, min_coverage=min_coverage, skip_lint=skip_lint)
    
    if result.get("success"):
        verification = result.get("verification", {})
        console.print(Panel(
            f"[bold green]✅ 병합 완료![/bold green]\n\n"
            f"[bold]SPEC:[/bold] {spec_id}\n"
            f"[bold]Merged into:[/bold] {base}\n\n"
            f"[bold]검증 결과:[/bold]\n"
            f"  - 테스트 통과: ✅\n"
            f"  - 커버리지 {verification.get('coverage_percent', 0)}%: ✅\n"
            f"  - 린트 검사: {'✅' if verification.get('lint_passed') else '⏭ 스킵'}",
            title="🎉 Integration Complete",
            border_style="green"
        ))
    else:
        phase = result.get("phase", "unknown")
        error = result.get("error", "Unknown error")
        verification = result.get("verification", {})
        console.print(f"[red]❌ {phase} 단계에서 실패: {error}[/red]")
        if verification:
            console.print(f"[dim]  - 테스트 통과: {'✅' if verification.get('tests_passed') else '❌'}")
            console.print(f"  - 커버리지 {verification.get('coverage_percent', 0)}%: {'✅' if verification.get('coverage_met') else '❌'}")
            console.print(f"  - 린트 검사: {'✅' if verification.get('lint_passed') else '❌'}[/dim]")



@worktree.command(name="remove")
@click.argument("spec_id")
@click.option("--force", "-f", is_flag=True, help="강제 삭제")
def worktree_remove(spec_id: str, force: bool):
    """SPEC worktree를 삭제합니다."""
    from cheeru_adk.core.worktree import WorktreeManager
    
    wm = WorktreeManager()
    result = wm.remove(spec_id, force=force)
    
    if result.get("success"):
        console.print(f"[green]✅ Worktree '{spec_id}' 삭제됨[/green]")
    else:
        console.print(f"[red]❌ {result.get('error', result.get('output'))}[/red]")


# ============================================================
# Sync Commands (Auto Documentation)
# ============================================================

@cli.group()
def sync():
    """자동 문서화 명령어."""
    pass


@sync.command(name="all")
def sync_all():
    """모든 문서를 동기화합니다 (README, CHANGELOG)."""
    from cheeru_adk.core.sync import DocSyncManager
    
    console.print("[bold]📝 문서 동기화 중...[/bold]")
    
    dsm = DocSyncManager()
    result = dsm.sync_all()
    
    console.print(Panel(
        f"[bold green]✅ 문서 동기화 완료![/bold green]\n\n"
        f"[bold]CHANGELOG:[/bold] {result['changelog'].get('commits_added', 0)}개 커밋 추가\n"
        f"[bold]README:[/bold] 업데이트됨",
        title="📝 Sync Complete",
        border_style="green"
    ))


@sync.command(name="changelog")
def sync_changelog():
    """CHANGELOG.md를 업데이트합니다."""
    from cheeru_adk.core.sync import DocSyncManager
    
    dsm = DocSyncManager()
    result = dsm.update_changelog()
    
    if result.get("success"):
        console.print(f"[green]✅ CHANGELOG 업데이트: {result.get('commits_added', 0)}개 커밋 추가[/green]")
    else:
        console.print(f"[yellow]ℹ️ {result.get('message', 'No changes')}[/yellow]")


@sync.command(name="readme")
def sync_readme():
    """README.md를 업데이트합니다."""
    from cheeru_adk.core.sync import DocSyncManager
    
    dsm = DocSyncManager()
    result = dsm.update_readme()
    
    if result.get("success"):
        console.print(f"[green]✅ README 업데이트: features={result.get('features')}, tests={result.get('tests')}[/green]")
    else:
        console.print(f"[red]❌ {result.get('error')}[/red]")


@sync.command(name="api")
def sync_api():
    """API 문서를 생성합니다."""
    from cheeru_adk.core.sync import DocSyncManager
    
    dsm = DocSyncManager()
    result = dsm.generate_api_docs()
    
    if result.get("success"):
        console.print(f"[green]✅ API 문서 생성: {result.get('files_generated')}개 파일[/green]")
    else:
        console.print(f"[red]❌ {result.get('error')}[/red]")


@sync.command(name="check")
def sync_check():
    """문서 최신성을 확인합니다."""
    from cheeru_adk.core.sync import DocSyncManager
    
    dsm = DocSyncManager()
    result = dsm.check_freshness()
    
    score = result.get("score", 0)
    color = "green" if score >= 80 else "yellow" if score >= 50 else "red"
    
    console.print(Panel(
        f"[bold {color}]문서 최신성: {score}%[/bold {color}]\n\n"
        + ("\n".join(f"⚠️ {issue}" for issue in result.get("issues", [])) or "✅ 모든 문서가 최신 상태입니다."),
        title="📊 Documentation Freshness",
        border_style=color
    ))


# ============================================================
# Agent Commands (Dispatcher)
# ============================================================

@cli.group()
def agent():
    """에이전트 디스패처 명령어."""
    pass


@agent.command(name="select")
@click.argument("context")
def agent_select(context: str):
    """컨텍스트에 맞는 에이전트를 자동 선택합니다."""
    from cheeru_adk.core.dispatcher import AgentDispatcher
    from rich.table import Table
    
    dispatcher = AgentDispatcher()
    result = dispatcher.dispatch(context)
    
    if not result.get("agents"):
        console.print("[yellow]일치하는 에이전트가 없습니다.[/yellow]")
        return
    
    table = Table(title=f"🤖 추천 에이전트 ('{context}')")
    table.add_column("순위", style="cyan")
    table.add_column("에이전트")
    table.add_column("역할")
    
    for i, agent in enumerate(result["agents"], 1):
        role = ", ".join(agent["capabilities"][:3])
        table.add_row(str(i), agent["type"], role)
    
    console.print(table)
    
    primary = result.get("primary")
    if primary:
        console.print(f"\n[bold]사용:[/bold] @.agent/agents/{primary.value}.md")


@agent.command(name="list")
def agent_list():
    """모든 에이전트를 나열합니다."""
    from cheeru_adk.core.dispatcher import AgentDispatcher
    from rich.table import Table
    
    dispatcher = AgentDispatcher()
    agents = dispatcher.list_agents()
    
    table = Table(title="🤖 Available Agents")
    table.add_column("에이전트", style="cyan")
    table.add_column("역할")
    table.add_column("상태", style="green")
    
    for agent in agents:
        status = "✅" if agent["exists"] else "❌"
        role = ", ".join(agent["capabilities"][:3])
        table.add_row(agent["type"], role, status)
    
    console.print(table)


@agent.command(name="chain")
@click.argument("workflow")
def agent_chain(workflow: str):
    """워크플로우에 맞는 에이전트 체인을 생성합니다."""
    from cheeru_adk.core.dispatcher import AgentDispatcher
    
    dispatcher = AgentDispatcher()
    chain = dispatcher.create_chain(workflow)
    
    if not chain:
        console.print(f"[yellow]'{workflow}' 워크플로우가 없습니다.[/yellow]")
        console.print("[dim]사용 가능: tdd, plan, review, deploy, docs[/dim]")
        return
    
    console.print(f"[bold]📋 {workflow.upper()} 워크플로우 체인:[/bold]\n")
    
    for i, agent in enumerate(chain, 1):
        console.print(f"  {i}. @.agent/agents/{agent.value}.md")


# ============================================================
# Task Commands
# ============================================================

@cli.group()
def task():
    """📋 Task 관리 명령어."""
    pass


@task.command(name="list")
def task_list():
    """모든 태스크 목록을 표시합니다."""
    from cheeru_adk.core.task import TaskManager
    from rich.table import Table
    
    manager = TaskManager()
    tasks = manager.list_tasks()
    
    if not tasks:
        console.print("[yellow]정의된 태스크가 없습니다.[/yellow]")
        console.print("[dim]`.cheeru/tasks.yaml` 파일을 확인하세요.[/dim]")
        return
    
    table = Table(title="📋 Available Tasks")
    table.add_column("태스크", style="cyan")
    table.add_column("에이전트", style="green")
    table.add_column("의존성")
    table.add_column("상태")
    
    for t in tasks:
        deps = ", ".join(t.dependencies) if t.dependencies else "-"
        status = t.status.value
        table.add_row(t.name, t.agent, deps, status)
    
    console.print(table)


@task.command(name="show")
@click.argument("task_name")
def task_show(task_name: str):
    """특정 태스크의 상세 정보를 표시합니다."""
    from cheeru_adk.core.task import TaskManager
    
    manager = TaskManager()
    t = manager.get_task(task_name)
    
    if not t:
        console.print(f"[red]태스크 '{task_name}'을 찾을 수 없습니다.[/red]")
        return
    
    console.print(Panel.fit(
        f"[bold cyan]{t.name}[/bold cyan]",
        border_style="cyan"
    ))
    console.print(f"[bold]에이전트:[/bold] {t.agent}")
    console.print(f"[bold]상태:[/bold] {t.status.value}")
    console.print()
    console.print("[bold]설명:[/bold]")
    console.print(t.description)
    console.print()
    console.print("[bold]예상 결과:[/bold]")
    console.print(t.expected_output)
    
    if t.dependencies:
        console.print()
        console.print(f"[bold]의존성:[/bold] {', '.join(t.dependencies)}")
    
    if t.context:
        console.print()
        console.print(f"[bold]컨텍스트:[/bold] {', '.join(t.context)}")


@task.command(name="run")
@click.argument("task_name")
@click.option("--input", "-i", "inputs", multiple=True, help="입력 변수 (key=value)")
def task_run(task_name: str, inputs: tuple):
    """태스크를 실행합니다."""
    from cheeru_adk.core.task import TaskManager
    
    manager = TaskManager()
    
    # Parse inputs
    input_dict = {}
    for inp in inputs:
        if "=" in inp:
            key, value = inp.split("=", 1)
            input_dict[key] = value
    
    console.print(f"[bold]🚀 태스크 실행: {task_name}[/bold]")
    
    result = manager.execute(task_name, input_dict if input_dict else None)
    
    if not result["success"]:
        console.print(f"[red]❌ 실패: {result.get('error')}[/red]")
        return
    
    console.print(f"[green]✅ 성공[/green]")
    console.print()
    console.print("[bold]에이전트:[/bold]", result["agent"])
    console.print()
    console.print("[bold]프롬프트:[/bold]")
    console.print(Panel(result["prompt"], border_style="dim"))


@task.command(name="order")
def task_order():
    """의존성에 따른 태스크 실행 순서를 표시합니다."""
    from cheeru_adk.core.task import TaskManager
    
    manager = TaskManager()
    order = manager.get_execution_order()
    
    if not order:
        console.print("[yellow]정의된 태스크가 없습니다.[/yellow]")
        return
    
    console.print("[bold]📋 태스크 실행 순서:[/bold]\n")
    
    for i, name in enumerate(order, 1):
        t = manager.get_task(name)
        agent = t.agent if t else "unknown"
        console.print(f"  {i}. [cyan]{name}[/cyan] ([dim]{agent}[/dim])")


if __name__ == "__main__":
    cli()

