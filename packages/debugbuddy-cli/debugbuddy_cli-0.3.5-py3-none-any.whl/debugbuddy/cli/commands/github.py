import click
from rich.console import Console
from rich.table import Table
from ...integrations.github.client import GitHubClient
from ...integrations.github.search import GitHubSearcher
from ...storage.config import ConfigManager

console = Console()

@click.group()
def github():

    pass

@github.command()
@click.argument('error_text')
@click.option('--language', '-l', type=str, default='python')
def search(error_text, language):

    config = ConfigManager()
    token = config.get('github_token')

    client = GitHubClient(token)
    searcher = GitHubSearcher(client)

    console.print(f"\n[bold cyan]Searching GitHub...[/bold cyan]\n")

    solutions = searcher.find_solutions(error_text, language)

    if not solutions:
        console.print("[yellow]No solutions found[/yellow]")
        return

    table = Table(title="GitHub Solutions")
    table.add_column("Title", style="cyan")
    table.add_column("State", style="green")
    table.add_column("👍", style="yellow")
    table.add_column("💬", style="blue")

    for sol in solutions:
        table.add_row(
            sol['title'][:50] + "..." if len(sol['title']) > 50 else sol['title'],
            sol['state'],
            str(sol['reactions']),
            str(sol['comments'])
        )

    console.print(table)

    console.print("\n[dim]URLs:[/dim]")
    for i, sol in enumerate(solutions, 1):
        console.print(f"  {i}. {sol['url']}")

@github.command()
@click.argument('error_text')
@click.option('--repo', '-r', type=str, required=True)
def report(error_text, repo):

    config = ConfigManager()
    token = config.get('github_token')

    if not token:
        console.print("[red]GitHub token not configured[/red]")
        console.print("[dim]Set with: dbug config github_token YOUR_TOKEN[/dim]")
        return

    client = GitHubClient(token)

    title = f"[DeBugBuddy] {error_text[:50]}"
    body = f"Error reported via DeBugBuddy:\n\n```\n{error_text}\n```"

    issue = client.create_issue(repo, title, body, labels=['bug', 'debugbuddy'])

    console.print(f"\n[green]Issue created: {issue['html_url']}[/green]")