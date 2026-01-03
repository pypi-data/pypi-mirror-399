from rich.console import Console
from rich.table import Table
from rich import box
from typing import List, Dict, Any, Optional

console = Console()

def print_table(title: str, headers: List[str], rows: List[List[str]]):
    """
    Prints a rich table to the console.
    """
    table = Table(title=title, box=box.ROUNDED)
    for header in headers:
        table.add_column(header)
    
    for row in rows:
        table.add_row(*row)
    
    console.print(table)

def print_json(data: Any):
    """
    Prints data as pretty-printed JSON.
    """
    import json
    console.print_json(json.dumps(data, default=str))

def print_error(message: str):
    """
    Prints an error message.
    """
    console.print(f"[bold red]Error:[/bold red] {message}")

def print_success(message: str):
    """
    Prints a success message.
    """
    console.print(f"[bold green]Success:[/bold green] {message}")

def print_info(message: str):
    """
    Prints an info message.
    """
    console.print(f"[bold blue]Info:[/bold blue] {message}")
