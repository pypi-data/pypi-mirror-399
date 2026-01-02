import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm
from ...storage.config import ConfigManager

console = Console()

@click.command()
@click.argument('key', required=False)
@click.argument('value', required=False)
@click.option('--show', is_flag=True, help='Show current config')
@click.option('--reset', is_flag=True, help='Reset to defaults')
def config(key, value, show, reset):
    config_mgr = ConfigManager()

    if reset:
        if Confirm.ask("Reset all settings to defaults?"):
            config_mgr.reset()
            console.print("[green]Config reset to defaults[/green]")
        return

    if show or (not key and not value):
        cfg = config_mgr.get_all()

        console.print("\n[bold green]Current Configuration[/bold green]\n")

        table = Table()
        table.add_column("Setting", style="yellow")
        table.add_column("Value", style="green")

        for k, v in cfg.items():
            table.add_row(k, str(v))

        console.print(table)
        console.print("\n[dim]To set: dbug config key value[/dim]")
        return

    if not value:
        current = config_mgr.get(key)
        console.print(f"[yellow]{key}:[/yellow] {current}")
        return

    config_mgr.set(key, value)
    console.print(f"[green]{key} set to {value}[/green]")