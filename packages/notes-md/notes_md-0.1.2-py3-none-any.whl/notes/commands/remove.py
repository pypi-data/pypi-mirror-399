"""
Click command for removing a note.
"""
from pathlib import Path
import click
from ..config import read_config
from ..helpers import run_git_command, git_is_tracked


@click.command(name="remove")
@click.argument("note_name")
def remove_note(note_name: str):
    """
    Remove a note from the current project.

    If the note is tracked by git, it is removed using `git rm`
    so the deletion can be synced. Otherwise, the file is deleted
    directly from the filesystem.
    """
    note_name = f"{note_name}.md"
    config = read_config()
    notes_dir = Path(config["notes_dir"])
    project_dir = Path(config["notes_dir"]) / Path.cwd().name
    note_path = project_dir / note_name

    if not note_path.exists():
        click.echo(f"Note '{note_name}' does not exist.")
        raise click.Abort()

    # Confirm removal
    if not click.confirm(f"Are you sure you want to remove '{note_name}'?"):
        raise click.abort("Aborted.")

    if (notes_dir / ".git").exists() and git_is_tracked(project_dir, notes_dir):
        click.echo(f"Removing tracked note: {note_path}")
        run_git_command(["rm", str(note_path)], project_dir)
    else:
        click.echo("Note is not tracked by git; removing locally only.")
        note_path.unlink()
