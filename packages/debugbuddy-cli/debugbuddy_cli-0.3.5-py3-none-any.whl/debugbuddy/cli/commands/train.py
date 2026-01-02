import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.progress import Progress
from ...core.trainer import PatternTrainer
from ...storage.config import ConfigManager
from ...models.training import TrainingData

console = Console()

@click.command()
@click.option('--interactive', '-i', is_flag=True, help='Interactive training mode')
@click.option('--language', '-l', type=str, help='Programming language')
@click.option('--ml', is_flag=True, help='Train ML models')
@click.option('--from-history', is_flag=True, help='Train from error history')
def train(interactive, language, ml, from_history):
    config = ConfigManager()
    trainer = PatternTrainer(config)

    if ml:
        _train_ml_models(config)
        return

    if from_history:
        _train_from_history(trainer)
        return

    if interactive:
        _interactive_training(trainer, language)
        return

    patterns = trainer.list_custom_patterns()
    if not patterns:
        console.print("[yellow]No custom patterns yet[/yellow]")
        console.print("[dim]Use --interactive to create one[/dim]")
        console.print("[dim]Use --ml to train ML models[/dim]")
        return

    console.print("\n[bold cyan]Custom Patterns[/bold cyan]\n")
    for i, pattern in enumerate(patterns, 1):
        console.print(f"{i}. [cyan]{pattern.type}[/cyan] [{pattern.language}]")


def _interactive_training(trainer, language):
    console.print("\n[bold cyan]📚 Interactive Pattern Training[/bold cyan]\n")
    console.print("[dim]Enter error examples to create a custom pattern[/dim]\n")

    examples = []

    while True:
        error_text = Prompt.ask("Error text (or 'done' to finish)")

        if error_text.lower() == 'done':
            if len(examples) < 2:
                console.print("[yellow]⚠ Need at least 2 examples[/yellow]")
                continue
            break

        explanation = Prompt.ask("Simple explanation")
        fix = Prompt.ask("How to fix")
        lang = language or Prompt.ask("Language")

        examples.append(TrainingData(
            error_text=error_text,
            explanation=explanation,
            fix=fix,
            language=lang
        ))

        console.print(f"[green]✅ Added example {len(examples)}[/green]\n")

    pattern = trainer.train_pattern(examples)

    console.print(f"\n[green]✅ Custom pattern created![/green]")
    console.print(f"[dim]Type: {pattern.type}[/dim]")
    console.print(f"[dim]Keywords: {', '.join(pattern.keywords)}[/dim]")


def _train_ml_models(config):
    console.print("\n[bold cyan]🤖 ML Model Training[/bold cyan]\n")
    
    try:
        from ...models.ml_engine import MLEngine, TrainingExample
        from ...storage.history import HistoryManager
    except ImportError:
        console.print("[red]❌ ML dependencies not installed[/red]")
        console.print("[dim]Install with: pip install numpy[/dim]")
        return

    history = HistoryManager()
    recent = history.get_recent(limit=1000)

    if len(recent) < 10:
        console.print("[yellow]⚠ Not enough training data[/yellow]")
        console.print(f"[dim]Found {len(recent)} errors, need at least 10[/dim]")
        console.print("[dim]Use DeBugBuddy more to build up error history[/dim]")
        return

    console.print(f"[green]Found {len(recent)} errors in history[/green]")
    
    if not Confirm.ask("Train ML models with this data?"):
        return

    examples = []
    for entry in recent:
        examples.append(TrainingExample(
            error_text=entry['message'],
            error_type=entry['error_type'],
            language=entry['language']
        ))

    console.print(f"\n[cyan]Preparing {len(examples)} training examples...[/cyan]")

    engine = MLEngine()

    with Progress() as progress:
        task1 = progress.add_task("[cyan]Training classifier...", total=100)
        
        console.print("\n[cyan]Training neural network classifier...[/cyan]")
        losses = engine.train_classifier(examples, epochs=100)
        progress.update(task1, completed=100)

        task2 = progress.add_task("[cyan]Training embeddings...", total=100)
        console.print("[cyan]Training word embeddings...[/cyan]")
        engine.train_embeddings(examples, epochs=10)
        progress.update(task2, completed=100)

    console.print("\n[cyan]Saving models...[/cyan]")
    engine.save_models()

    console.print("\n[green]✅ ML models trained successfully![/green]")
    console.print(f"[dim]Final loss: {losses[-1]:.4f}[/dim]")
    console.print(f"[dim]Models saved to: {engine.model_dir}[/dim]")

    config.set('use_ml_prediction', True)
    console.print("\n[green]✅ ML prediction enabled in config[/green]")


def _train_from_history(trainer):
    from ...storage.history import HistoryManager
    
    console.print("\n[bold cyan]📚 Training from History[/bold cyan]\n")
    
    history = HistoryManager()
    recent = history.get_recent(limit=100)
    
    if not recent:
        console.print("[yellow]No error history found[/yellow]")
        return
    
    console.print(f"Found {len(recent)} errors in history")
    
    error_groups = {}
    for entry in recent:
        error_type = entry['error_type']
        if error_type not in error_groups:
            error_groups[error_type] = []
        error_groups[error_type].append(entry)
    
    console.print(f"\nError types found: {', '.join(error_groups.keys())}\n")
    
    for error_type, entries in error_groups.items():
        if len(entries) < 3:
            continue
            
        console.print(f"[cyan]Training pattern for {error_type}...[/cyan]")
        
        examples = []
        for entry in entries[:5]:
            examples.append(TrainingData(
                error_text=entry['message'],
                explanation=entry['simple'],
                fix=entry['fix'],
                language=entry['language']
            ))
        
        pattern = trainer.train_pattern(examples)
        console.print(f"[green]✅ Created pattern: {pattern.type}[/green]")
    
    console.print(f"\n[green]✅ Training complete![/green]")