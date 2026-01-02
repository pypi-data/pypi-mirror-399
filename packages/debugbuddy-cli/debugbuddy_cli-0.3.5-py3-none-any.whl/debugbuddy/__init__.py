__version__ = "0.3.5"

def __getattr__(name):
    if name == "ErrorParser":
        from .core.parsers import ErrorParser
        return ErrorParser
    elif name == "ErrorExplainer":
        from .core.explainer import ErrorExplainer
        return ErrorExplainer
    elif name == "ErrorPredictor":
        from .core.predictor import ErrorPredictor
        return ErrorPredictor
    elif name == "PatternTrainer":
        from .core.trainer import PatternTrainer
        return PatternTrainer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")