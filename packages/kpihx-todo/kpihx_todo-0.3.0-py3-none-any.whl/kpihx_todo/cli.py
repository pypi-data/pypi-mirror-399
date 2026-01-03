import json
from enum import Enum
import re
from pathlib import Path
from typing import List, Optional
import typer

app = typer.Typer()
DB = Path.home() / ".todo_cli.json"

class SortOrder(str, Enum):
    """Enum for sorting order."""
    ASC = "asc"
    DESC = "desc"

def load_db():
    if not DB.exists():
        return []
    return json.loads(DB.read_text())

def save_db(tasks):
    DB.write_text(json.dumps(tasks, indent=2))

@app.command()
def add(task: str):
    tasks = load_db()
    tasks.append({"task": task, "done": False})
    save_db(tasks)
    typer.echo(f"Added: {task}")

def _list_tasks(tasks: List[dict], reverse_ids: bool = False):
    if not tasks:
        typer.echo("No tasks yet.")
        return
    display_tasks = reversed(tasks) if reverse_ids else tasks
    for i, t in enumerate(display_tasks, 1):
        status = "✓" if t["done"] else " "
        typer.echo(f"{len(tasks) - i + 1 if reverse_ids else i}. [{status}] {t['task']}")

@app.command(name="list")
def list_tasks(
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Search for tasks with a regex pattern."),
    sort_by_name: Optional[SortOrder] = typer.Option(None, "--sort-by-name", "-sn", help="Sort tasks by name."),
    sort_by_id: Optional[SortOrder] = typer.Option(None, "--sort-by-id", "-si", help="Sort tasks by ID."),
    show_done: Optional[bool] = typer.Option(False, "--done", "-d", help="Show only done tasks."),
    show_not_done: Optional[bool] = typer.Option(False, "--not-done", "-nd", help="Show only not-done tasks."),
):
    """Lists tasks with filtering and sorting options."""
    tasks = load_db()

    # Search by regex pattern
    if query:
        try:
            tasks = [t for t in tasks if re.search(query, t["task"], re.IGNORECASE)]
        except re.error as e:
            typer.echo(f"Error: Invalid regex pattern: {e}")
            raise typer.Exit(code=1)

    # Filter by status
    if show_done and show_not_done:
        typer.echo("Error: --done and --not-done options cannot be used together.")
        raise typer.Exit(code=1)
    if show_done:
        tasks = [t for t in tasks if t["done"]]
    elif show_not_done:
        tasks = [t for t in tasks if not t["done"]]

    # Sorting
    if sort_by_name and sort_by_id:
        typer.echo("Error: --sort-by-name and --sort-by-id options cannot be used together.")
        raise typer.Exit(code=1)

    reverse_ids_display = False
    if sort_by_name:
        reverse = sort_by_name == SortOrder.DESC
        tasks.sort(key=lambda t: t["task"].lower(), reverse=reverse)
    elif sort_by_id:
        reverse_ids_display = sort_by_id == SortOrder.DESC

    _list_tasks(tasks, reverse_ids=reverse_ids_display)

@app.command()
def done(id: int):
    """Marks a task as done."""
    tasks = load_db()
    if 1 <= id <= len(tasks):
        tasks[id-1]["done"] = True
        save_db(tasks)
        typer.echo(f"Marked task '{tasks[id-1]['task']}' as done.")
    else:
        typer.echo("Error: Invalid task ID.")

@app.command()
def toggle(id: int):
    """Toggles a task's status (done/not done)."""
    tasks = load_db()
    if 1 <= id <= len(tasks):
        tasks[id-1]["done"] = not tasks[id-1]["done"]
        save_db(tasks)
        status = "done" if tasks[id-1]["done"] else "not done"
        typer.echo(f"Task {id} is now marked as {status}.")
    else:
        typer.echo("Error: Invalid task ID.")

@app.command()
def delete(id: int):
    """Deletes a task by its ID."""
    tasks = load_db()
    if 1 <= id <= len(tasks):
        deleted_task = tasks.pop(id - 1)
        save_db(tasks)
        typer.echo(f"Deleted task: {deleted_task['task']}")
    else:
        typer.echo("Error: Invalid task ID.")

def main():
    app()
