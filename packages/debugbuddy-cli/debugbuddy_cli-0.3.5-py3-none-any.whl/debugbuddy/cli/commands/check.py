import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from ...core.parsers import ErrorParser
from ...core.explainer import ErrorExplainer
from ...utils.helpers import detect_all_errors
from ...storage.config import ConfigManager

console = Console()

@click.command()
@click.argument('file_path', type=click.Path(exists=True))
def check(file_path):
    config_mgr = ConfigManager()
    parser = ErrorParser()
    explainer = ErrorExplainer()

    file_path = Path(file_path)
    console.print(f"\n[bold green]Checking {file_path.name}[/bold green]\n")

    all_errors = detect_all_errors(file_path)

    if not all_errors:
        console.print("[green]No errors found![/green]")
        return

    table = Table()
    table.add_column("Line", style="dim")
    table.add_column("Type", style="red")
    table.add_column("Explanation", style="green")

    for error_text in all_errors:
        parsed = parser.parse(error_text)
        if parsed:
            explanation = explainer.explain(parsed)
            table.add_row(
                str(parsed.get('line', '-')),
                parsed['type'],
                explanation['simple']
            )

    console.print(table)