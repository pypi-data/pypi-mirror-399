from rich.panel import Panel

def format_explanation(title, content):
    return Panel(content, title=title, expand=False)