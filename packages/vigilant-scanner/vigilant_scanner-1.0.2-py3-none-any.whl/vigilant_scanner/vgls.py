import typer
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.spinner import Spinner
from contextlib import contextmanager
from .scanner.scanner import Scanner
from .scanner.db_manager import DatabaseManager
from .log_analyzer.log_analyzer import LogAnalyzer
import os

app = typer.Typer()
console = Console()


@contextmanager
def spinning_message(message):
    """
    Display a spinner with a message while executing a block of code.
    """
    spinner = Spinner("dots", text=message)
    with console.status(spinner):
        yield


@app.command("integrity-init")
@app.command("i-i", hidden=True)
def init(directory: str):
    """
    Create a snapshot of the directory for the current state - scan directory, initialize the database, and store metadata.
    """
    if not os.path.isdir(directory):
        console.print(Panel(f"[red]Directory does not exist:[/red] {directory}", title="Initialization", style="bold"))
        return

    console.print(Text(f"Initialization for directory: {directory}", style="bold"))
    scanner = Scanner(directory)

    with spinning_message("Scanning and hashing..."):
        metadata_list, errors = scanner.scan_directory()

    db = DatabaseManager(directory)
    db.reset_db()
    db.update_or_insert_metadata(metadata_list)
    if errors:
        console.print(Panel("\n".join(errors), title="Warnings", style="bold yellow"))
    console.print(Panel(f"[green]Initialization completed![/green]\n"
                        f"Target: {directory}\n"
                        f"Stored: {db.db_path}", style="bold"))


@app.command("integrity-scan")
@app.command("i-s", hidden=True)
def scan(directory: str):
    """
    Scan the target directory and compare results with the last scan stored in the database.
    """
    if not os.path.isdir(directory):
        console.print(Panel(f"[red]Directory does not exist:[/red] {directory}", title="Scanning", style="bold"))
        return

    db_path = DatabaseManager(directory).db_path
    if not os.path.exists(db_path):
        console.print(Panel(
            "[red]Snapshot not found. Please run 'integrity-init' first to initialize.[/red]\n Execute: [green]vgls integrity-init <directory>[/green]",
            title="Scanning", style="bold"))
        return

    console.print(Text(f"Scanning directory: {directory}", style="bold"))
    scanner = Scanner(directory)

    with spinning_message("Comparing with snapshot..."):
        results, errors = scanner.compare_with_database()

    if not results:
        console.print(Panel("[green]No changes detected.[/green]", title="Scanning", style="bold"))
    else:
        table = Table(title="Scan Results", style="bold")
        table.add_column("Change Type", style="bold white")
        table.add_column("File Path", style="dim")

        for change_type, file_path in results:
            if change_type == "Modified":
                style = "yellow"
            elif change_type == "New":
                style = "bright_red"
            elif change_type == "Deleted":
                style = "red"
            else:
                style = "white"

            table.add_row(f"[{style}]{change_type}[/{style}]", file_path)

        console.print(table)
    if errors:
        console.print(Panel("\n".join(errors), title="Warnings", style="bold yellow"))


@app.command("integrity-update")
@app.command("i-u", hidden=True)
def update(directory: str):
    """
    Update the database with the current file state (when authorized changes were made).
    """
    if not os.path.isdir(directory):
        console.print(Panel(f"[red]Directory does not exist:[/red] {directory}", title="Update", style="bold"))
        return

    console.print(Text(f"Updating snapshot for directory: {directory}", style="bold"))
    scanner = Scanner(directory)
    db_manager = DatabaseManager(directory)
    if not os.path.exists(db_manager.db_path):
        console.print(Panel(
            "[red]Snapshot not found. Please run 'integrity-init' first to initialize.[/red]\n Execute: [green]vgls integrity-init <directory>[/green]",
            title="Update", style="bold"))
        return

    with spinning_message("Updating database with current state..."):
        current_metadata_list, errors = scanner.scan_directory()
        current_files = {metadata.path for metadata in current_metadata_list}

        db_manager.update_or_insert_metadata(current_metadata_list)
        db_manager.delete_removed_files(current_files)

    console.print(Panel(f"[green]Snapshot updated![/green]\n"
                        f"Target: {directory}\n"
                        f"Stored: {db_manager.db_path}", style="bold"))
    if errors:
        console.print(Panel("\n".join(errors), title="Warnings", style="bold yellow"))


@app.command("log-scan")
@app.command("l-s", hidden=True)
def logs_scan(directory: str):
    """
    Scan all .log files in the provided directory for malicious activity.
    """
    console.print(Text(f"Scanning all .log files in directory: {directory}", style="bold"))
    with spinning_message("Analyzing logs..."):
        analyzer = LogAnalyzer(directory)
        results = analyzer.conduct_logs_analysis()

        # Handle errors or informational messages
        if "error" in results:
            console.print(Panel(results["error"], style="bold red"))
            return
        if "info" in results:
            console.print(Panel(results["info"], style="bold yellow"))
            return

        # Display results in a table
        table = Table(title="Log Analysis Results", style="bold")
        table.add_column("Log File", style="bold magenta", overflow="fold")
        table.add_column("Pattern", style="bold cyan")
        table.add_column("Line Number", style="bold white")
        table.add_column("Content", style="dim", overflow="fold")

        for log_file, detections in results.items():
            for pattern, occurrences in detections.items():
                for line, content in occurrences:
                    table.add_row(str(log_file), pattern, str(line), content)

        console.print(table)


@app.command("full-scan")
@app.command("f-s", hidden=True)
def full_scan(directory: str):
    """
    Perform a full scan of the directory: integrity checking and log analysis.
    """
    console.print(Text("Performing Integrity Scan", style="bold"))
    scan(directory)

    console.print(Text("Performing Log Analysis", style="bold"))
    logs_scan(directory)


if __name__ == "__main__":
    app()
