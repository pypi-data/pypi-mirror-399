from typing import List
import ast
from pathlib import Path
from ..models.prediction import Prediction
from ..storage.patterns import PatternManager
from ..monitoring.checker import SimpleChecker

class ErrorPredictor:

    def __init__(self, config_manager):
        self.config = config_manager
        self.pattern_mgr = PatternManager()
        self.ml_engine = None
        self._init_ml_engine()

    def _init_ml_engine(self):
        try:
            use_ml = self.config.get('use_ml_prediction', False)
            if use_ml:
                from ..models.ml_engine import MLEngine
                self.ml_engine = MLEngine()
                
                try:
                    self.ml_engine.load_models()
                except Exception:
                    self.ml_engine = None
        except ImportError:
            self.ml_engine = None

    def predict_file(self, file_path: Path) -> List[Prediction]:
        predictions = []
        
        static_preds = self._analyze_static(file_path)
        predictions.extend(static_preds)
        
        pattern_preds = self._analyze_patterns(file_path)
        predictions.extend(pattern_preds)
        
        if self.ml_engine:
            ml_preds = self._analyze_ml(file_path)
            predictions.extend(ml_preds)
        
        predictions = self._deduplicate_predictions(predictions)
        predictions.sort(key=lambda p: p.confidence, reverse=True)
        
        return predictions

    def _analyze_static(self, file_path: Path) -> List[Prediction]:
        predictions = []
        
        if file_path.suffix != '.py':
            return predictions
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                return predictions
            
            try:
                tree = ast.parse(content, filename=str(file_path))
                checker = SimpleChecker(str(file_path))
                checker.visit(tree)
                
                for name, lines in checker.undefined_locations.items():
                    for line in lines:
                        predictions.append(Prediction(
                            file=str(file_path),
                            line=line,
                            column=None,
                            error_type='NameError',
                            message=f"name '{name}' is not defined",
                            confidence=0.85,
                            suggestion=f"Define '{name}' before using it or import it",
                            severity='high'
                        ))
                
                for name in checker.imports:
                    if name not in checker.used:
                        line = checker.import_lines.get(name, 1)
                        predictions.append(Prediction(
                            file=str(file_path),
                            line=line,
                            column=None,
                            error_type='UnusedImport',
                            message=f"'{name}' imported but unused",
                            confidence=0.9,
                            suggestion=f"Remove unused import '{name}'",
                            severity='low'
                        ))
                        
            except (SyntaxError, IndentationError) as e:
                predictions.append(Prediction(
                    file=str(file_path),
                    line=e.lineno or 1,
                    column=e.offset,
                    error_type='SyntaxError',
                    message=e.msg or 'invalid syntax',
                    confidence=1.0,
                    suggestion="Fix the syntax error",
                    severity='critical'
                ))
                
        except Exception:
            pass
            
        return predictions

    def _analyze_patterns(self, file_path: Path) -> List[Prediction]:
        lang = file_path.suffix[1:] if file_path.suffix else 'unknown'
        patterns = self.pattern_mgr.load_patterns(lang)
        predictions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines, 1):
                line_lower = line.lower()
                
                for pattern in patterns:
                    keywords = pattern.get('keywords', [])
                    matches = sum(1 for kw in keywords if kw.lower() in line_lower)
                    
                    if matches >= 2:
                        predictions.append(Prediction(
                            file=str(file_path),
                            line=i,
                            column=None,
                            error_type=pattern.get('type', 'Unknown'),
                            message=pattern.get('simple', 'Potential issue detected'),
                            confidence=0.4 + (matches * 0.1),
                            suggestion=pattern.get('fix', 'Review this line'),
                            severity='medium'
                        ))
        except Exception:
            pass
            
        return predictions

    def _analyze_ml(self, file_path: Path) -> List[Prediction]:
        if not self.ml_engine:
            return []
            
        predictions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                if not line.strip() or line.strip().startswith('#'):
                    continue
                
                result = self.ml_engine.classify_error(line, 'python')
                
                if result and result.get('top_prediction'):
                    top = result['top_prediction']
                    
                    if top['confidence'] > 0.6:
                        predictions.append(Prediction(
                            file=str(file_path),
                            line=i,
                            column=None,
                            error_type=top['type'],
                            message=f"ML detected potential {top['type']}",
                            confidence=top['confidence'],
                            suggestion="Review this line for potential issues",
                            severity=self._confidence_to_severity(top['confidence'])
                        ))
        except Exception:
            pass
            
        return predictions

    def _deduplicate_predictions(self, predictions: List[Prediction]) -> List[Prediction]:
        seen = set()
        unique = []
        
        for pred in predictions:
            key = (pred.file, pred.line, pred.error_type)
            if key not in seen:
                seen.add(key)
                unique.append(pred)
        
        return unique

    def _confidence_to_severity(self, confidence: float) -> str:
        if confidence >= 0.9:
            return 'critical'
        elif confidence >= 0.75:
            return 'high'
        elif confidence >= 0.5:
            return 'medium'
        else:
            return 'low'