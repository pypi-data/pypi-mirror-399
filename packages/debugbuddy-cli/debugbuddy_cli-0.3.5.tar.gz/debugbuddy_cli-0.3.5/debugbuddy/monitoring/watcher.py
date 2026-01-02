import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console
from ..core.parsers import ErrorParser
from ..core.explainer import ErrorExplainer
from ..monitoring.checker import SimpleChecker
from ..utils.helpers import detect_all_errors

console = Console()

class ErrorWatcher:
    def __init__(self, path='.'):
        self.directory = Path(path).resolve() if Path(path).is_dir() else Path(path).parent.resolve()
        self.target_file = Path(path).resolve() if not Path(path).is_dir() else None
        self.extensions = ['.py',]
        self.exclude = ['__pycache__', '.git', '.venv']

    def start(self):
        event_handler = ErrorFileHandler()
        observer = Observer()
        observer.schedule(event_handler, str(self.directory), recursive=True)
        observer.start()

        if self.target_file and self.target_file.exists():
            event_handler._check_for_errors(self.target_file)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

class ErrorFileHandler(FileSystemEventHandler):
    def __init__(self):
        self.parser = ErrorParser()
        self.explainer = ErrorExplainer()
        self.last_check = {}

    def on_modified(self, event):
        self._handle_event(event)

    def on_created(self, event):
        self._handle_event(event)

    def _handle_event(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.suffix not in ['.py']:
            return

        now = time.time()
        if str(file_path) in self.last_check and now - self.last_check[str(file_path)] < 1.5:
            return

        self.last_check[str(file_path)] = now
        time.sleep(0.1)
        self._check_for_errors(file_path)

    def _check_for_errors(self, file_path):
        all_errors = detect_all_errors(file_path)
        if all_errors:
            timestamp = time.strftime("%H:%M:%S")
            console.print(f"\n[{timestamp}] Found {len(all_errors)} error(s) in {file_path.name}")
            for i, error_text in enumerate(all_errors, 1):
                parsed = self.parser.parse(error_text)
                if parsed:
                    explanation = self.explainer.explain(parsed)
                    line_info = f" (line {parsed['line']})" if parsed.get('line') else ""
                    console.print(f"           [{i}] [red]{parsed['type']}[/red]{line_info}")
                    console.print(f"                [dim]{explanation['simple'][:70]}...[/dim]")