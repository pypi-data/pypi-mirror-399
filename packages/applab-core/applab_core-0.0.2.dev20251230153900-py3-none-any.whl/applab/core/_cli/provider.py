from cyclopts import App
from rich.console import Console

console = Console(width=80)
print = console.print

provider_app = App(name="provider")


@provider_app.command(name="list")
def list_():
    """
    List all providers.
    """
    from rich.table import Table

    table = Table(title="Demo Table", show_lines=True)
    table.add_column("Name")
    table.add_column("Value")
    table.add_row("foo", "123")
    table.add_row("bar", "456")

    print(table)


@provider_app.command
def info(path, url):
    """Upload a file."""
    print(f"Downloading {url} to {path}.")


@provider_app.command
def login(path, url):
    """Upload a file."""
    print(f"Downloading {url} to {path}.")
