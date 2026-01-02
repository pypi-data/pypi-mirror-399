import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from ...core.predictor import ErrorPredictor
from ...storage.config import ConfigManager

console = Console()

@click.command()
@click.argument('path', type=click.Path(exists=True), required=False)
@click.option('--severity', type=click.Choice(['low', 'medium', 'high', 'critical']),
              help='Filter by severity level')
@click.option('--limit', type=int, default=10, help='Maximum predictions to show')
def predict(path, severity, limit):
    config = ConfigManager()
    predictor = ErrorPredictor(config)

    path = Path(path) if path else Path.cwd()

    console.print(f"\n[bold cyan]Analyzing {path.name}...[/bold cyan]\n")

    predictions = predictor.predict_file(path)

    if severity:
        predictions = [p for p in predictions if p.severity == severity]

    predictions = predictions[:limit]

    if not predictions:
        console.print("[green]No potential errors detected![/green]")
        return

    table = Table(title="Potential Errors")
    table.add_column("Line", style="yellow")
    table.add_column("Type", style="red")
    table.add_column("Confidence", style="cyan")
    table.add_column("Message", style="white")

    for pred in predictions:
        confidence = f"{pred.confidence * 100:.0f}%"
        table.add_row(
            str(pred.line),
            pred.error_type,
            confidence,
            pred.message[:60] + "..." if len(pred.message) > 60 else pred.message
        )

    console.print(table)
    console.print(f"\n[dim]Tip: Use --severity to filter by severity level[/dim]")