import ast
from pathlib import Path

def detect_all_errors(file_path: Path):
    all_errors = []

    try:
        if not file_path.exists():
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip():
            return []

        if file_path.suffix != '.py':
            return [content]

        filename = str(file_path)
        
        try:
            ast.parse(content, filename=filename)
            return []
        except (SyntaxError, IndentationError) as e:
            error_type = type(e).__name__
            lineno = e.lineno if e.lineno else 1
            msg = e.msg if e.msg else "syntax error"
            
            # Format the error message
            error_msg = f"{error_type}: {msg}\n  File \"{filename}\", line {lineno}"
            
            if hasattr(e, 'text') and e.text:
                error_msg += f"\n    {e.text.rstrip()}"
                if hasattr(e, 'offset') and e.offset and e.offset > 0:
                    error_msg += f"\n    {' ' * (e.offset - 1)}^"
            
            all_errors.append(error_msg)
            
            lines = content.splitlines(keepends=True)
            if not lines:
                return all_errors
            
            current_lines = lines[:]
            seen_errors = {f"{error_type}:{lineno}"}
            max_iterations = 20
            
            for iteration in range(max_iterations):
                if 0 <= lineno - 1 < len(current_lines):
                    line = current_lines[lineno - 1]
                    if not line.strip().startswith('#'):
                        stripped = line.lstrip()
                        if stripped:
                            indent = line[:len(line) - len(stripped)]
                            current_lines[lineno - 1] = f"{indent}# {stripped}"
                
                current_content = ''.join(current_lines)
                
                try:
                    ast.parse(current_content, filename=filename)
                    break
                except (SyntaxError, IndentationError) as e:
                    error_type = type(e).__name__
                    lineno = e.lineno if e.lineno else 1
                    msg = e.msg if e.msg else "syntax error"
                    
                    error_id = f"{error_type}:{lineno}"
                    if error_id in seen_errors:
                        break
                    seen_errors.add(error_id)
                    
                    error_msg = f"{error_type}: {msg}\n  File \"{filename}\", line {lineno}"
                    if hasattr(e, 'text') and e.text:
                        error_msg += f"\n    {e.text.rstrip()}"
                        if hasattr(e, 'offset') and e.offset and e.offset > 0:
                            error_msg += f"\n    {' ' * (e.offset - 1)}^"
                    
                    all_errors.append(error_msg)
                except Exception:
                    break

    except Exception as e:
        pass

    return all_errors