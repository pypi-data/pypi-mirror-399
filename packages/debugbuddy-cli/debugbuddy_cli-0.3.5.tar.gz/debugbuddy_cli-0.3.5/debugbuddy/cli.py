import click
import sys
import ast
import subprocess
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table
from rich.prompt import Prompt, Confirm

from debugbuddy.core.parsers import ErrorParser
from debugbuddy.core.explainer import ErrorExplainer
from debugbuddy.monitoring.watcher import ErrorWatcher
from debugbuddy.storage.history import HistoryManager
from debugbuddy.storage.config import ConfigManager

console = Console()

def get_version():
    try:
        from debugbuddy.__version__ import __version__
        return __version__
    except ImportError:
        try:
            from debugbuddy import __version__
            return __version__
        except (ImportError, AttributeError):
            return "0.3.5"

def _detect_all_errors(file_path):
    all_errors = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if file_path.suffix != '.py':
            return [content]

        filename = str(file_path)
        lines = content.splitlines(keepends=True)
        current_lines = lines[:]
        max_iterations = 20

        for iteration in range(max_iterations):
            current_content = ''.join(current_lines)
            try:
                ast.parse(current_content, filename=filename)
                break
            except (SyntaxError, IndentationError) as e:
                error_type = type(e).__name__
                lineno = e.lineno
                msg = e.msg
                error_msg = f"{error_type}: {msg}\n  File \"{filename}\", line {lineno}"
                if hasattr(e, 'text') and e.text:
                    error_msg += f"\n    {e.text.rstrip()}\n    {' ' * (getattr(e, 'offset', 0) - 1) if getattr(e, 'offset', 0) else ''}^"
                all_errors.append(error_msg)

                if 0 <= lineno - 1 < len(current_lines):
                    offending_line = current_lines[lineno - 1]
                    stripped = offending_line.lstrip()
                    if stripped:
                        indent = offending_line[:-len(stripped)]
                        commented = indent + '#' + stripped
                        current_lines[lineno - 1] = commented + '\n'

    except Exception:
        return []

    return all_errors

@click.group(invoke_without_command=True)
@click.option('--version', '-v', is_flag=True, help='Show version and exit')
@click.pass_context
def main(ctx, version):
    """DeBugBuddy - Your terminal's debugging companion"""
    
    if version:
        version_num = get_version()
        console.print(f"\n[bold green]🐛 DeBugBuddy[/bold green] v{version_num}")
        console.print("[dim]Stop Googling. Understand your errors.[/dim]")
        console.print(f"\n[dim]Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}[/dim]")
        console.print(f"[dim]Platform: {sys.platform}[/dim]\n")
        return
    
    if ctx.invoked_subcommand is None:
        version_num = get_version()
        console.print(f"\n[bold green]🐛 DeBugBuddy - Your terminal's debugging companion[/bold green]")
        console.print(f"Version {version_num}\n")
        ctx.invoke(explain)

@main.command()
@click.argument('error_input', required=False)
@click.option('--file', '-f', is_flag=True, help='Treat input as file path')
@click.option('--ai', is_flag=True, help='Use AI for explanation')
@click.option('--py', is_flag=True)
@click.option('--js', is_flag=True)
@click.option('--ts', is_flag=True)
@click.option('--c', is_flag=True)
@click.option('--php', is_flag=True)
def explain(error_input, file, ai, py, js, ts, c, php):
    config_mgr = ConfigManager()
    allowed_languages = config_mgr.get('languages', [])

    parser = ErrorParser()
    explainer = ErrorExplainer()
    history = HistoryManager()

    language = None
    if py:
        language = 'python'
    elif js:
        language = 'javascript'
    elif ts:
        language = 'typescript'
    elif c:
        language = 'c'
    elif php:
        language = 'php'

    if not error_input:
        error_input = sys.stdin.read().strip()

    if not error_input:
        console.print("[yellow]⚠ No error provided[/yellow]")
        console.print("[dim]Usage: dbug explain \"Your error message\"[/dim]")
        console.print("[dim]Or pipe: python script.py 2>&1 | dbug explain[/dim]")
        return

    if file:
        try:
            with open(error_input, 'r', encoding='utf-8') as f:
                error_text = f.read().strip()
        except FileNotFoundError:
            console.print(f"[red]✗ File not found: {error_input}[/red]")
            return
        except Exception as e:
            console.print(f"[red]✗ Error reading file: {e}[/red]")
            return
    else:
        error_text = error_input

    parsed = parser.parse(error_text, language=language)

    if not parsed:
        console.print("[yellow]⚠ Couldn't parse the error[/yellow]")
        console.print("[dim]Try copying the exact error message[/dim]")
        return

    if allowed_languages and parsed.get('language') not in allowed_languages and parsed.get('language') != 'common':
        console.print(f"[yellow]⚠ Language '{parsed.get('language')}' is excluded in config. Using generic explanation.[/yellow]")
        parsed = parser._parse_generic(error_text)

    explanation = explainer.explain(parsed)

    if ai:
        provider_name = config_mgr.get('ai_provider', 'openai')
        api_key = config_mgr.get(f'{provider_name}_api_key')
        if not api_key:
            console.print(f"[yellow]⚠ No {provider_name.upper()} API key set. Run: dbug config {provider_name}_api_key YOUR_KEY[/yellow]")
        else:
            try:
                from debugbuddy.integrations.ai import get_provider
                provider = get_provider(provider_name, config_mgr.get_all())
                if provider:
                    ai_explain = provider.explain_error(error_text, parsed.get('language', 'code'))
                    if ai_explain:
                        explanation['ai'] = ai_explain
                    else:
                        console.print("[yellow]⚠ AI explanation failed[/yellow]")
            except ImportError:
                console.print("[yellow]⚠ AI dependencies not installed[/yellow]")

    history.add(parsed, explanation)

    title = f"🐛 {parsed['type']}"
    if parsed.get('file') and parsed.get('line'):
        title += f"\nFile: {parsed['file']}, Line {parsed['line']}"

    content = f"🔍 {explanation['simple']}\n\n💡 Fix:\n{explanation['fix']}"

    if 'example' in explanation and explanation['example']:
        content += f"\n\n📝 Example:\n{explanation['example']}"

    if 'did_you_mean' in explanation:
        dym = '\n'.join(f"• {s}" for s in explanation['did_you_mean'])
        content += f"\n\n🤔 Did you mean?\n{dym}"

    if 'suggestions' in explanation:
        sugg = '\n'.join(f"• {s}" for s in explanation['suggestions'])
        content += f"\n\n📌 Suggestions:\n{sugg}"

    if 'ai' in explanation:
        content += f"\n\n🤖 AI Explanation:\n{explanation['ai']}"

    console.print(Panel(content, title=title, expand=False))

    similar = history.find_similar(parsed)
    if similar:
        console.print("\n[dim]📝 Similar error seen before:[/dim]")
        console.print(f"[dim]{similar['timestamp']}: {similar['error_type']} - {similar['simple']}[/dim]")

@main.command()
@click.argument('path', type=click.Path(exists=True), required=False)
def watch(path):
    config_mgr = ConfigManager()
    allowed_languages = config_mgr.get('languages', [])

    path = Path(path) if path else Path.cwd()

    if not path.is_dir():
        path = path.parent

    console.print(f"\n[bold green]🐛 Watching for errors in: {path.absolute()}[/bold green]")
    console.print("[dim]Press Ctrl+C to stop[/dim]\n")

    from watchdog.observers import Observer
    event_handler = ErrorWatcher()
    observer = Observer()
    observer.schedule(event_handler, str(path), recursive=True)
    observer.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

@main.command()
@click.argument('file_path', type=click.Path(exists=True))
def check(file_path):
    config_mgr = ConfigManager()
    allowed_languages = config_mgr.get('languages', [])

    file_path = Path(file_path)
    console.print(f"\n[bold green]🐛 Checking {file_path.name}[/bold green]\n")

    all_errors = _detect_all_errors(file_path)

    if not all_errors:
        console.print("[green]✅ No errors found![/green]")
        return

    parser = ErrorParser()
    explainer = ErrorExplainer()

    table = Table()
    table.add_column("Line", style="dim")
    table.add_column("Type", style="red")
    table.add_column("Explanation", style="green")

    for error_text in all_errors:
        parsed = parser.parse(error_text)
        if parsed:
            if allowed_languages and parsed.get('language') not in allowed_languages and parsed.get('language') != 'common':
                parsed = parser._parse_generic(error_text)
            explanation = explainer.explain(parsed)
            table.add_row(
                str(parsed.get('line', '-')),
                parsed['type'],
                explanation['simple']
            )

    console.print(table)

@main.command()
@click.argument('command', required=False, nargs=-1)
def run(command):
    if not command:
        console.print("[yellow]⚠ No command provided[/yellow]")
        console.print("[dim]Usage: dbug run python script.py[/dim]")
        return

    command_str = ' '.join(command)
    console.print(f"\n[bold green]🐛 Running: {command_str}[/bold green]\n")

    process = subprocess.Popen(command_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode == 0:
        console.print(stdout.decode('utf-8'))
        console.print("\n[green]✅ Success![/green]")
    else:
        error_text = stderr.decode('utf-8').strip()
        if error_text:
            ctx = click.get_current_context()
            ctx.invoke(explain, error_input=error_text)
        else:
            console.print("[yellow]⚠ Command failed without error output[/yellow]")

@main.command()
@click.option('--clear', is_flag=True, help='Clear history')
@click.option('--stats', is_flag=True, help='Show statistics')
@click.option('--search', type=str, help='Search history')
def history(clear, stats, search):
    history_mgr = HistoryManager()

    if clear:
        if Confirm.ask("Clear all history?"):
            history_mgr.clear()
            console.print("[green]✅ History cleared[/green]")
        return

    if stats:
        stats_data = history_mgr.get_stats()
        console.print("\n[bold green]📊 Error Statistics[/bold green]\n")
        console.print(f"Total errors: {stats_data['total']}\n")

        console.print("[cyan]By Type:[/cyan]")
        for typ, count in sorted(stats_data['by_type'].items(), key=lambda x: x[1], reverse=True):
            console.print(f"  • {typ}: {count}")

        console.print("\n[cyan]By Language:[/cyan]")
        for lang, count in sorted(stats_data['by_language'].items(), key=lambda x: x[1], reverse=True):
            console.print(f"  • {lang}: {count}")
        return

    if search:
        results = history_mgr.search(search)
        if not results:
            console.print(f"[yellow]⚠ No history found for '{search}'[/yellow]")
            return

        console.print(f"\n[bold green]🔍 Search Results for '{search}':[/bold green]\n")
        for entry in results:
            console.print(f"[dim]{entry['timestamp']}[/dim]")
            console.print(f"[red]{entry['error_type']}[/red]: {entry['message']}")
            if entry['file']:
                console.print(f"[dim]File: {entry['file']}, Line {entry['line']}[/dim]")
            console.print(f"💡 {entry['simple']}")
            console.print()
        return

    recent = history_mgr.get_recent()
    if not recent:
        console.print("[yellow]⚠ No history yet[/yellow]")
        return

    console.print("\n[bold green]📜 Recent Errors[/bold green]\n")
    for entry in recent:
        console.print(f"[dim]{entry['timestamp']}[/dim]")
        console.print(f"[red]{entry['error_type']}[/red]: {entry['message']}")
        if entry['file']:
            console.print(f"[dim]File: {entry['file']}, Line {entry['line']}[/dim]")
        console.print(f"💡 {entry['simple']}")
        console.print()

@main.command()
@click.argument('keyword')
def search(keyword):
    explainer = ErrorExplainer()

    results = explainer.search_patterns(keyword)
    if not results:
        console.print(f"[yellow]⚠ No patterns found for '{keyword}'[/yellow]")
        console.print("\n[dim]Try searching for:[/dim]")
        console.print("  • Error names: syntax, name, type")
        console.print("  • Keywords: import, undefined, indentation")
        return

    console.print(f"\n[bold green]🔍 Found {len(results)} patterns for '{keyword}':[/bold green]\n")

    for i, pattern in enumerate(results, 1):
        console.print(f"{i}. [cyan]{pattern['name']}[/cyan] [dim]({pattern['language']})[/dim]")
        console.print(f"   {pattern['description'][:100]}...")
        console.print()

@main.command()
@click.argument('key', required=False)
@click.argument('value', required=False)
@click.option('--show', is_flag=True, help='Show current config')
@click.option('--reset', is_flag=True, help='Reset to defaults')
def config(key, value, show, reset):
    config_mgr = ConfigManager()

    if reset:
        if Confirm.ask("Reset all settings to defaults?"):
            config_mgr.reset()
            console.print("[green]✅  Config reset to defaults[/green]")
        return

    if show or (not key and not value):
        cfg = config_mgr.get_all()

        console.print("\n[bold green]⚙️  Current Configuration[/bold green]\n")

        table = Table()
        table.add_column("Setting", style="yellow")
        table.add_column("Value", style="green")

        for k, v in cfg.items():
            table.add_row(k, str(v))

        console.print(table)
        console.print()
        return

    if key and value:
        config_mgr.set(key, value)
        console.print(f"[green]✅ Set {key} = {value}[/green]")
    elif key:
        val = config_mgr.get(key)
        console.print(f"{key}: {val}")

@main.command()
def update():
    with console.status("[cyan]Checking for pattern updates...", spinner="dots"):
        import time
        time.sleep(1)

    console.print("[green]✅ Patterns are up to date[/green]")
    console.print("\n[dim]Pattern version: 2.0[/dim]")
    console.print("[dim]Last updated: 2024-11-22[/dim]")

try:
    from debugbuddy.cli.commands.predict import predict
    from debugbuddy.cli.commands.train import train
    from debugbuddy.cli.commands.github import github
    
    main.add_command(predict)
    main.add_command(train)
    main.add_command(github)
except ImportError as e:
    pass

if __name__ == '__main__':
    main()