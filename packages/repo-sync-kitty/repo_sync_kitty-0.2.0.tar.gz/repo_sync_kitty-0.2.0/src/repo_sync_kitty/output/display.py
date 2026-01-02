"""Display utilities for rich terminal output."""

from rich.console import Console
from rich.table import Table

console = Console()


def create_status_table() -> Table:
    """Create a status table for repository display."""
    table = Table(title="Repository Status")
    table.add_column("Path", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Branch", style="yellow")
    table.add_column("Issues", style="red")
    return table
