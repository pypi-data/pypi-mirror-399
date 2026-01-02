#!/usr/bin/env python3
import json
from importlib.metadata import version

import typer
from rich.console import Console
from rich.table import Table

from .mcp import DEFAULT_MAX_TOKENS, MIN_MAX_TOKENS
from .mcp import app as mcp_app
from .mcp import get_steps as mcp_get_steps
from .mcp import group_steps as mcp_group_steps
from .mcp import save_step as mcp_save_step
from .mcp import task_list as mcp_list_tasks
from .services import Timeline


def version_callback(value: bool) -> None:
    if value:
        console = Console()
        console.print(f"tliner version {version('tliner')}")
        raise typer.Exit


cli_app = typer.Typer()
console = Console()


@cli_app.callback(invoke_without_command=True)
def main(version_flag: bool = typer.Option(False, "--version", "-v", help="Show version and exit", callback=version_callback, is_eager=True)) -> None:
    """🌟 Timeliner CLI - AI's diary. Tracking AI's work with markdown log"""


@cli_app.command(name="version")
def version_cmd() -> None:
    """Show version information"""
    console.print(f"tliner version {version('tliner')}")


@cli_app.command()
def serve() -> None:
    """Run Timeliner as MCP server"""
    console.print("[green]Starting Timeliner MCP server...[/green]")
    mcp_app.run()


@cli_app.command()
def task_list() -> None:
    """List all tasks in the system"""
    result = mcp_list_tasks.fn()
    tasks = result.get("tasks", [])
    if not tasks:
        console.print("[yellow]No tasks found[/yellow]")
        return

    table = Table(title="Tasks")
    table.add_column("Task ID", style="cyan")
    table.add_column("Description")
    table.add_column("Steps", justify="right", style="green")

    for task in tasks:
        task_id = task["task_id"]
        title = task.get("title") or "[dim]No title[/dim]"
        steps = Timeline().get_steps_by_task_id(task_id)
        step_count = str(len(steps))

        table.add_row(task_id, title, step_count)

    console.print(table)


@cli_app.command(name="save-step")
def save_step_cmd(
    task_id: str,
    title: str,
    outcomes: str,
    tags: list[str] | None = typer.Option(None, "--tag", "-t", help="Tags for the step"),  # noqa: B008
    metadata_json: str | None = typer.Option(None, "--metadata", "-M", help='JSON object for metadata (e.g., \'{"github_issue": "https://..."}\')'),
) -> None:
    """Save a step for a task"""
    metadata = json.loads(metadata_json) if metadata_json else None
    result = mcp_save_step.fn(task_id=task_id, title=title, outcomes=outcomes, tags=tags or [], metadata=metadata)
    step_id = result.get("step_id", "N/A")
    console.print(f"[green]✓[/green] Saved step {step_id} for task {task_id}")


@cli_app.command(name="get-steps")
def get_steps_cmd(
    since: str = typer.Option("", "--since", "-s", help="Filter steps since timestamp (include) (ISO format, e.g., 2025-01-01T00:00:00Z)"),
    until: str = typer.Option("", "--until", "-u", help="Filter steps until timestamp (exclude) (ISO format, e.g., 2025-01-01T00:00:00Z)"),
    ids: list[str] | None = typer.Option(None, "--id", "-i", help="Filter by task ID(s) or step ID(s)"),  # noqa: B008
    page: int = typer.Option(1, "--page", "-p", help="Page number (1-indexed)"),
    max_tokens: int = typer.Option(DEFAULT_MAX_TOKENS, "--max-tokens", "-m", help=f"Max tokens per page (default: {DEFAULT_MAX_TOKENS} tokens, min: {MIN_MAX_TOKENS} tokens)"),
) -> None:
    """Get all steps with optional time, ID, and pagination filters"""
    result = mcp_get_steps.fn(since=since, until=until, ids=ids, page=page, max_tokens=max_tokens)
    steps = result.get("steps", [])
    pagination = result.get("pagination", {})

    if not steps:
        console.print("[yellow]No steps found[/yellow]")
        return

    title_parts = ["Steps"]
    if since and until:
        title_parts.append(f"since {since} until {until}")
    elif since:
        title_parts.append(f"since {since}")
    elif until:
        title_parts.append(f"until {until}")
    if ids:
        title_parts.append(f"ids: {', '.join(ids)}")
    title = title_parts[0] + (f" ({', '.join(title_parts[1:])})" if len(title_parts) > 1 else "")
    table = Table(title=title)
    table.add_column("Timestamp", style="green")
    table.add_column("Task ID", style="cyan")
    table.add_column("Outcomes")
    table.add_column("Tags", style="dim")

    for step in steps:
        timestamp = step["timestamp"]
        task_id = step["task_id"]
        outcomes = step["outcomes"][:80] + "..." if len(step["outcomes"]) > 80 else step["outcomes"]  # noqa: PLR2004
        tags = ", ".join(step.get("tags", []))

        table.add_row(timestamp, task_id, outcomes, tags)

    console.print(table)
    console.print(f"\n[dim]Page {pagination.get('page', 1)} of {pagination.get('total_pages', 1)} | {len(steps)} steps[/dim]")


@cli_app.command(name="group")
def group_cmd(instructions_json: str = typer.Argument(..., help='JSON mapping: {"step_id": "target_task_id", ...}')) -> None:
    """Group steps by moving them to target tasks"""
    try:
        instructions = json.loads(instructions_json)
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON:[/red] {e}")
        raise typer.Exit(code=1) from e

    if not isinstance(instructions, dict):
        console.print("[red]Instructions must be a JSON object[/red]")
        raise typer.Exit(code=1)

    result = mcp_group_steps.fn(instructions)
    moved = result.get("moved", [])
    skipped = result.get("skipped", [])
    deleted_tasks = result.get("deleted_tasks", [])

    console.print(f"[green]✓[/green] Moved {len(moved)} steps")
    if skipped:
        console.print(f"[yellow]⊘[/yellow] Skipped {len(skipped)} steps (groupable: false)")
    if deleted_tasks:
        console.print(f"[dim]✗[/dim] Deleted {len(deleted_tasks)} empty task files")


app = cli_app

if __name__ == "__main__":
    cli_app()
