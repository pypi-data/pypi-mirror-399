import click
from rich.console import Console
from ...core.explainer import ErrorExplainer

console = Console()

@click.command()
@click.argument('keyword')
def search(keyword):
    explainer = ErrorExplainer()

    results = explainer.search_patterns(keyword)
    if not results:
        console.print(f"[yellow]No patterns found for '{keyword}'[/yellow]")
        console.print("\n[dim]Try searching for:[/dim]")
        console.print("  • Error names: syntax, name, type")
        console.print("  • Keywords: import, undefined, indentation")
        return

    console.print(f"\n[bold green]Found {len(results)} patterns for '{keyword}':[/bold green]\n")

    for i, pattern in enumerate(results, 1):
        console.print(f"{i}. [cyan]{pattern['name']}[/cyan] [dim]({pattern['language']})[/dim]")
        console.print(f"   {pattern['description'][:100]}...")
        console.print()