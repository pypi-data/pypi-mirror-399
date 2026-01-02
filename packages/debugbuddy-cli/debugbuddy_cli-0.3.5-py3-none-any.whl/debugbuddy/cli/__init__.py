import click
from rich.console import Console

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

@click.group(invoke_without_command=True)
@click.option('--version', '-v', is_flag=True, help='Show version')
@click.pass_context
def main(ctx, version):
    """DeBugBuddy - Your terminal's debugging companion"""
    
    if version:
        version_num = get_version()
        console.print(f"\n[bold green]DeBugBuddy[/bold green] v{version_num}")
        console.print("[dim]Your terminal's debugging companion[/dim]\n")
        return
    
    if ctx.invoked_subcommand is None:
        version_num = get_version()
        console.print(f"\n[bold green]DeBugBuddy - Your terminal's debugging companion[/bold green]")
        console.print(f"Version v{version_num}\n")
        console.print("Usage: [cyan]dbug [COMMAND] [OPTIONS][/cyan]\n")
        console.print("Commands:")
        console.print("  [cyan]explain[/cyan]     Explain an error message")
        console.print("  [cyan]predict[/cyan]     Predict errors in a file")
        console.print("  [cyan]watch[/cyan]       Watch files for errors")
        console.print("  [cyan]history[/cyan]     View error history")
        console.print("  [cyan]train[/cyan]       Train custom patterns or ML models")
        console.print("  [cyan]search[/cyan]      Search error patterns")
        console.print("  [cyan]config[/cyan]      Manage configuration")
        console.print("  [cyan]github[/cyan]      GitHub integration")
        console.print("\nOptions:")
        console.print("  [cyan]--version, -v[/cyan]  Show version")
        console.print("  [cyan]--help, -h[/cyan]     Show this message")
        console.print("\nExamples:")
        console.print('  [dim]dbug explain "NameError: name \'x\' is not defined"[/dim]')
        console.print('  [dim]dbug predict script.py[/dim]')
        console.print('  [dim]dbug train --ml[/dim]')
        console.print()

try:
    from .commands.explain import explain
    main.add_command(explain)
except ImportError:
    pass

try:
    from .commands.watch import watch
    main.add_command(watch)
except ImportError:
    pass

try:
    from .commands.history import history
    main.add_command(history)
except ImportError:
    pass

try:
    from .commands.search import search
    main.add_command(search)
except ImportError:
    pass

try:
    from .commands.config import config
    main.add_command(config)
except ImportError:
    pass

try:
    from .commands.predict import predict
    main.add_command(predict)
except ImportError:
    pass

try:
    from .commands.train import train
    main.add_command(train)
except ImportError:
    pass

try:
    from .commands.github import github
    main.add_command(github)
except ImportError:
    pass

if __name__ == "__main__":
    main()