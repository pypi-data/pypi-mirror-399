import ast

class SimpleChecker(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.defined = set()
        self.used = set()
        self.imports = set()
        self.import_lines = {}
        self.undefined_locations = {}
        self.builtins = {
            'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes', 'callable',
            'chr', 'classmethod', 'compile', 'complex', 'delattr', 'dict', 'dir', 'divmod',
            'enumerate', 'eval', 'exec', 'filter', 'float', 'format', 'frozenset', 'getattr',
            'globals', 'hasattr', 'hash', 'help', 'hex', 'id', 'input', 'int', 'isinstance',
            'issubclass', 'iter', 'len', 'list', 'locals', 'map', 'max', 'memoryview', 'min',
            'next', 'object', 'oct', 'open', 'ord', 'pow', 'print', 'property', 'range',
            'repr', 'reversed', 'round', 'set', 'setattr', 'slice', 'sorted', 'staticmethod',
            'str', 'sum', 'super', 'tuple', 'type', 'vars', 'zip', '__import__',
            'False', 'None', 'True'
        }

    def visit_Import(self, node):
        for alias in node.names:
            name = alias.name.split('.')[0]
            self.imports.add(name)
            if name not in self.import_lines:
                self.import_lines[name] = node.lineno
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            if alias.name != '*':
                name = alias.asname or alias.name
                self.imports.add(name)
                if name not in self.import_lines:
                    self.import_lines[name] = node.lineno
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.defined.add(node.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.defined.add(node.name)
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.defined.add(target.id)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used.add(node.id)
            if node.id not in self.defined and node.id not in self.imports and node.id not in self.builtins:
                if node.id not in self.undefined_locations:
                    self.undefined_locations[node.id] = set()
                self.undefined_locations[node.id].add(node.lineno)
        self.generic_visit(node)

    def get_errors(self):
        errors = []
        for name, lines in self.undefined_locations.items():
            for line in sorted(lines):
                error_msg = f"NameError: name '{name}' is not defined\n  File \"{self.filename}\", line {line}"
                errors.append(error_msg)
        for name in self.imports:
            if name not in self.used:
                line = self.import_lines.get(name, 1)
                error_msg = f"Unused import: '{name}' imported but unused\n  File \"{self.filename}\", line {line}"
                errors.append(error_msg)
        return errors