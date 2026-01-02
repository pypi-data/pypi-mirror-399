import click
import sys
from rich.console import Console
from rich.panel import Panel
from ...core.parsers import ErrorParser
from ...core.explainer import ErrorExplainer
from ...storage.history import HistoryManager
from ...storage.config import ConfigManager

console = Console()

@click.command()
@click.argument('error_input', required=False)
@click.option('--file', '-f', is_flag=True, help='Treat input as file path')
@click.option('--ai', is_flag=True, help='Use AI for explanation')
@click.option('--language', '-l', type=str, help='Specify language')
def explain(error_input, file, ai, language):
    config_mgr = ConfigManager()
    parser = ErrorParser()
    explainer = ErrorExplainer()
    history = HistoryManager()

    if not error_input:
        error_input = sys.stdin.read().strip()

    if not error_input:
        console.print("[yellow]No error provided[/yellow]")
        console.print("[dim]Usage: dbug explain \"Your error message\"[/dim]")
        console.print("[dim]Or pipe: python script.py 2>&1 | dbug explain[/dim]")
        return

    if file:
        try:
            with open(error_input, 'r', encoding='utf-8') as f:
                error_text = f.read().strip()
        except FileNotFoundError:
            console.print(f"[red]File not found: {error_input}[/red]")
            return
        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")
            return
    else:
        error_text = error_input

    parsed = parser.parse(error_text, language=language)

    if not parsed:
        console.print("[yellow]Couldn't parse the error[/yellow]")
        console.print("[dim]Try copying the exact error message[/dim]")
        return

    explanation = explainer.explain(parsed)

    if ai:
        try:
            from ...integrations.ai import get_provider
            provider_name = config_mgr.get('ai_provider', 'openai')
            api_key = config_mgr.get(f'{provider_name}_api_key')
            if not api_key:
                console.print(f"[yellow]No {provider_name.upper()} API key set. Run: dbug config {provider_name}_api_key YOUR_KEY[/yellow]")
            else:
                provider = get_provider(provider_name, config_mgr.get_all())
                if provider:
                    ai_explain = provider.explain_error(error_text, parsed.get('language', 'code'))
                    if ai_explain:
                        explanation['ai'] = ai_explain
                    else:
                        console.print("[yellow]AI explanation failed[/yellow]")
        except ImportError:
            console.print("[yellow]AI dependencies not installed[/yellow]")

    history.add(parsed, explanation)

    title = f"DeBugBuddy {parsed['type']}"
    if parsed.get('file') and parsed.get('line'):
        title += f"\nFile: {parsed['file']}, Line {parsed['line']}"

    content = f"Error: {explanation['simple']}\n\nFix:\n{explanation['fix']}"

    if 'example' in explanation and explanation['example']:
        content += f"\n\nExample:\n{explanation['example']}"

    if 'did_you_mean' in explanation and explanation['did_you_mean']:
        dym = '\n'.join(f"  {s}" for s in explanation['did_you_mean'])
        content += f"\n\nDid you mean?\n{dym}"

    if 'suggestions' in explanation and explanation['suggestions']:
        sugg = '\n'.join(f"  {s}" for s in explanation['suggestions'])
        content += f"\n\nSuggestions:\n{sugg}"

    if 'ai' in explanation:
        content += f"\n\nAI Explanation:\n{explanation['ai']}"

    console.print(Panel(content, title=title, expand=False))

    similar = history.find_similar(parsed)
    if similar:
        console.print("\n[dim]Similar error seen before:[/dim]")
        console.print(f"[dim]{similar['timestamp']}: {similar['error_type']} - {similar['simple']}[/dim]")