import os

import click
from rich.console import Console
from rich.markup import escape
from rich.table import Table

from .cleaner import remove_junk
from .scanner import scan_junk

console = Console(width=1000)


@click.group()
def main():
    """macOS Junk Cleaner - Clean up macOS specific junk files."""
    pass


@main.command()
@click.argument("path", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option(
    "--recursive/--no-recursive", default=True, help="Scan subdirectories recursively."
)
def scan(path, recursive):
    """Scan a directory for macOS junk files."""
    path = os.path.abspath(path)
    scan_detail = " (recursively)" if recursive else ""
    console.print(f"Scanning [bold cyan]{escape(path)}[/bold cyan]{scan_detail}...")

    junk_files = scan_junk(path, recursive=recursive)

    if not junk_files:
        console.print("[green]No junk files found![/green]")
        return

    if os.environ.get("TESTING") == "1":
        for junk in junk_files:
            console.print(junk)
        return

    table = Table(title=f"Junk Files Found ({len(junk_files)})")
    table.add_column("Path", style="cyan", no_wrap=True)
    table.add_column("Type", style="green")

    for junk in junk_files:
        jtype = "Dir" if os.path.isdir(junk) else "File"
        # We use escape and highlight=False to ensure paths look consistent
        table.add_row(escape(junk), jtype)

    console.print(table)


@main.command()
@click.argument("path", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option(
    "--recursive/--no-recursive", default=True, help="Scan subdirectories recursively."
)
@click.option("--force", is_flag=True, help="Actually delete the files.")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt.")
def clean(path, recursive, force, yes):
    """Scan and remove macOS junk files."""
    path = os.path.abspath(path)
    scan_detail = " (recursively)" if recursive else ""
    console.print(f"Scanning [bold cyan]{escape(path)}[/bold cyan]{scan_detail}...")

    junk_files = scan_junk(path, recursive=recursive)

    if not junk_files:
        console.print("[green]No junk files found to clean![/green]")
        return

    # Determine if we should show the list of files
    show_list = not force

    if show_list:
        console.print(f"[yellow]Found {len(junk_files)} items to clean:[/yellow]")
        for f in junk_files:
            # highlight=False prevents numbers in paths from being colored differently
            console.print(
                f"  [bright_black]- {escape(f)}[/bright_black]", highlight=False
            )

    # Check if we need confirmation
    if not (yes or force):
        if not click.confirm("\nDo you want to delete these items?"):
            console.print("[yellow]Aborted.[/yellow]")
            return
    elif yes and not force:
        console.print("\n[yellow]Proceeding with deletion (--yes)...[/yellow]")
    elif force:
        console.print(
            f"[yellow]Forcing deletion of {len(junk_files)} items...[/yellow]",
            highlight=False,
        )

    removed, errors = remove_junk(junk_files, dry_run=False)

    for r in removed:
        console.print(
            f"[green]Removed:[/green] [bright_black]{escape(r)}[/bright_black]",
            highlight=False,
        )

    for path, err in errors:
        console.print(
            f"[red]Error removing {escape(path)}:[/red] {escape(str(err))}",
            highlight=False,
        )

    console.print(
        f"\n[bold green]Clean up complete![/bold green] Removed {len(removed)} items."
    )


if __name__ == "__main__":
    main()
