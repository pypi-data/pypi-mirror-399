import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import pickle
import re
from collections import Counter

@dataclass
class TrainingExample:
    error_text: str
    error_type: str
    language: str
    features: Optional[np.ndarray] = None
    embedding: Optional[np.ndarray] = None

class NeuralNetwork:

    def __init__(self, input_size: int, hidden_sizes: List[int], output_size: int, learning_rate: float = 0.01):
        self.lr = learning_rate
        self.layers = []

        layer_sizes = [input_size] + hidden_sizes + [output_size]
        for i in range(len(layer_sizes) - 1):
            w = np.random.randn(layer_sizes[i], layer_sizes[i+1]) * np.sqrt(2.0 / layer_sizes[i])
            b = np.zeros((1, layer_sizes[i+1]))
            self.layers.append({'w': w, 'b': b, 'cache': {}})

    def relu(self, x: np.ndarray) -> np.ndarray:
        return np.maximum(0, x)

    def relu_derivative(self, x: np.ndarray) -> np.ndarray:
        return (x > 0).astype(float)

    def softmax(self, x: np.ndarray) -> np.ndarray:
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)

    def forward(self, X: np.ndarray) -> np.ndarray:
        current = X

        for i, layer in enumerate(self.layers[:-1]):
            z = np.dot(current, layer['w']) + layer['b']
            current = self.relu(z)
            layer['cache'] = {'input': current, 'z': z}

        z = np.dot(current, self.layers[-1]['w']) + self.layers[-1]['b']
        output = self.softmax(z)
        self.layers[-1]['cache'] = {'input': current, 'z': z, 'output': output}

        return output

    def backward(self, X: np.ndarray, y: np.ndarray, output: np.ndarray):
        m = X.shape[0]

        dz = output - y
        dw = np.dot(self.layers[-1]['cache']['input'].T, dz) / m
        db = np.sum(dz, axis=0, keepdims=True) / m
        self.layers[-1]['w'] -= self.lr * dw
        self.layers[-1]['b'] -= self.lr * db

        da = np.dot(dz, self.layers[-1]['w'].T)
        for i in range(len(self.layers) - 2, -1, -1):
            dz = da * self.relu_derivative(self.layers[i]['cache']['z'])
            prev_activation = X if i == 0 else self.layers[i-1]['cache']['input']
            dw = np.dot(prev_activation.T, dz) / m
            db = np.sum(dz, axis=0, keepdims=True) / m

            self.layers[i]['w'] -= self.lr * dw
            self.layers[i]['b'] -= self.lr * db

            if i > 0:
                da = np.dot(dz, self.layers[i]['w'].T)

    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 100, batch_size: int = 32):
        n_samples = X.shape[0]
        losses = []

        for epoch in range(epochs):
            indices = np.random.permutation(n_samples)
            epoch_loss = 0

            for start in range(0, n_samples, batch_size):
                end = min(start + batch_size, n_samples)
                batch_indices = indices[start:end]
                X_batch = X[batch_indices]
                y_batch = y[batch_indices]

                output = self.forward(X_batch)
                self.backward(X_batch, y_batch, output)

                batch_loss = -np.sum(y_batch * np.log(output + 1e-8)) / len(X_batch)
                epoch_loss += batch_loss

            avg_loss = epoch_loss / (n_samples / batch_size)
            losses.append(avg_loss)

            if epoch % 10 == 0:
                print(f"Epoch {epoch}/{epochs}, Loss: {avg_loss:.4f}")

        return losses

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.forward(X)

class ErrorEmbedding:

    def __init__(self, embedding_dim: int = 128, window_size: int = 3):
        self.embedding_dim = embedding_dim
        self.window_size = window_size
        self.word_to_idx = {}
        self.idx_to_word = {}
        self.embeddings = None
        self.vocab_size = 0

    def tokenize(self, text: str) -> List[str]:
        text = text.lower()
        tokens = re.findall(r'\b\w+\b|[^\w\s]', text)
        return tokens

    def build_vocab(self, texts: List[str]):
        all_tokens = []
        for text in texts:
            all_tokens.extend(self.tokenize(text))

        token_counts = Counter(all_tokens)
        vocab = [token for token, _ in token_counts.most_common(5000)]

        self.word_to_idx = {word: idx for idx, word in enumerate(vocab)}
        self.idx_to_word = {idx: word for word, idx in self.word_to_idx.items()}
        self.vocab_size = len(vocab)

        self.embeddings = np.random.randn(self.vocab_size, self.embedding_dim) * 0.01

    def generate_training_pairs(self, text: str) -> List[Tuple[int, int]]:
        tokens = self.tokenize(text)
        pairs = []

        for i, target in enumerate(tokens):
            if target not in self.word_to_idx:
                continue

            target_idx = self.word_to_idx[target]

            start = max(0, i - self.window_size)
            end = min(len(tokens), i + self.window_size + 1)

            for j in range(start, end):
                if i != j and tokens[j] in self.word_to_idx:
                    context_idx = self.word_to_idx[tokens[j]]
                    pairs.append((target_idx, context_idx))

        return pairs

    def train(self, texts: List[str], epochs: int = 10, lr: float = 0.025):
        print(f"Building vocabulary from {len(texts)} texts...")
        self.build_vocab(texts)

        all_pairs = []
        for text in texts:
            all_pairs.extend(self.generate_training_pairs(text))

        print(f"Training on {len(all_pairs)} word pairs...")

        for epoch in range(epochs):
            np.random.shuffle(all_pairs)
            total_loss = 0

            for target_idx, context_idx in all_pairs:
                target_vec = self.embeddings[target_idx]
                context_vec = self.embeddings[context_idx]

                score = np.dot(target_vec, context_vec)
                prob = 1 / (1 + np.exp(-score))

                grad = (prob - 1) * lr
                self.embeddings[target_idx] -= grad * context_vec
                self.embeddings[context_idx] -= grad * target_vec

                total_loss += -np.log(prob + 1e-8)

            if epoch % 2 == 0:
                avg_loss = total_loss / len(all_pairs)
                print(f"Epoch {epoch}/{epochs}, Loss: {avg_loss:.4f}")

    def embed(self, text: str) -> np.ndarray:
        tokens = self.tokenize(text)
        embeddings = []

        for token in tokens:
            if token in self.word_to_idx:
                idx = self.word_to_idx[token]
                embeddings.append(self.embeddings[idx])

        if not embeddings:
            return np.zeros(self.embedding_dim)

        return np.mean(embeddings, axis=0)

class FeatureExtractor:

    def __init__(self):
        self.error_keywords = [
            'error', 'exception', 'failed', 'undefined', 'null', 'invalid',
            'syntax', 'type', 'reference', 'import', 'module', 'attribute',
            'index', 'key', 'value', 'name', 'timeout', 'permission'
        ]

        self.language_indicators = {
            'python': ['traceback', 'py', 'python', 'import'],
            'javascript': ['js', 'javascript', 'node', 'referenceerror'],
            'typescript': ['ts', 'typescript', 'interface', 'generic'],
            'c': ['gcc', 'segfault', 'undefined reference'],
            'php': ['php', 'parse error', 'fatal error']
        }

    def extract(self, error_text: str, language: str = None) -> np.ndarray:
        features = []
        text_lower = error_text.lower()

        features.append(len(error_text))
        features.append(len(error_text.split()))
        features.append(error_text.count('\n'))
        features.append(len(re.findall(r'[A-Z]', error_text)))

        for keyword in self.error_keywords:
            features.append(1 if keyword in text_lower else 0)

        for lang, indicators in self.language_indicators.items():
            score = sum(1 for ind in indicators if ind in text_lower)
            features.append(score)

        features.append(error_text.count('('))
        features.append(error_text.count(')'))
        features.append(error_text.count('['))
        features.append(error_text.count(']'))
        features.append(error_text.count('{'))
        features.append(error_text.count('}'))
        features.append(error_text.count(':'))
        features.append(error_text.count(';'))

        features.append(1 if 'error' in text_lower else 0)
        features.append(1 if 'warning' in text_lower else 0)
        features.append(1 if 'exception' in text_lower else 0)

        return np.array(features, dtype=float)

class MLEngine:

    def __init__(self, model_dir: Path = None):
        self.model_dir = model_dir or Path.home() / '.debugbuddy' / 'models'
        self.model_dir.mkdir(parents=True, exist_ok=True)

        self.feature_extractor = FeatureExtractor()
        self.embedding_model = None
        self.classifier = None
        self.error_types = []
        self.type_to_idx = {}
        self.trained = False

    def prepare_data(self, examples: List[TrainingExample]) -> Tuple[np.ndarray, np.ndarray]:
        X = []
        y = []

        unique_types = list(set(ex.error_type for ex in examples))
        self.error_types = unique_types
        self.type_to_idx = {t: i for i, t in enumerate(unique_types)}

        for ex in examples:
            features = self.feature_extractor.extract(ex.error_text, ex.language)

            label = np.zeros(len(unique_types))
            label[self.type_to_idx[ex.error_type]] = 1

            X.append(features)
            y.append(label)

        return np.array(X), np.array(y)

    def train_classifier(self, examples: List[TrainingExample], epochs: int = 100):
        print(f"Training classifier on {len(examples)} examples...")

        X, y = self.prepare_data(examples)

        self.feature_mean = np.mean(X, axis=0)
        self.feature_std = np.std(X, axis=0) + 1e-8
        X_norm = (X - self.feature_mean) / self.feature_std

        input_size = X.shape[1]
        output_size = len(self.error_types)
        self.classifier = NeuralNetwork(
            input_size=input_size,
            hidden_sizes=[128, 64, 32],
            output_size=output_size,
            learning_rate=0.01
        )

        losses = self.classifier.train(X_norm, y, epochs=epochs)
        self.trained = True

        print(f"Training complete. Final loss: {losses[-1]:.4f}")
        return losses

    def train_embeddings(self, examples: List[TrainingExample], epochs: int = 10):
        print(f"Training embeddings on {len(examples)} examples...")

        texts = [ex.error_text for ex in examples]
        self.embedding_model = ErrorEmbedding(embedding_dim=128)
        self.embedding_model.train(texts, epochs=epochs)

        print("Embedding training complete.")

    def classify_error(self, error_text: str, language: str = None) -> Dict:
        if not self.trained or self.classifier is None:
            return {'error': 'Model not trained'}

        features = self.feature_extractor.extract(error_text, language)
        features_norm = (features - self.feature_mean) / self.feature_std
        features_norm = features_norm.reshape(1, -1)

        probs = self.classifier.predict(features_norm)[0]

        top_indices = np.argsort(probs)[-3:][::-1]
        predictions = []
        for idx in top_indices:
            predictions.append({
                'type': self.error_types[idx],
                'confidence': float(probs[idx])
            })

        return {
            'predictions': predictions,
            'top_prediction': predictions[0] if predictions else None
        }

    def get_similar_errors(self, error_text: str, top_k: int = 5) -> List[Dict]:
        if self.embedding_model is None:
            return []

        query_embedding = self.embedding_model.embed(error_text)

        return []

    def save_models(self):
        if self.classifier:
            model_data = {
                'layers': self.classifier.layers,
                'error_types': self.error_types,
                'type_to_idx': self.type_to_idx,
                'feature_mean': self.feature_mean,
                'feature_std': self.feature_std
            }
            with open(self.model_dir / 'classifier.pkl', 'wb') as f:
                pickle.dump(model_data, f)

        if self.embedding_model:
            embedding_data = {
                'embeddings': self.embedding_model.embeddings,
                'word_to_idx': self.embedding_model.word_to_idx,
                'idx_to_word': self.embedding_model.idx_to_word,
                'embedding_dim': self.embedding_model.embedding_dim
            }
            with open(self.model_dir / 'embeddings.pkl', 'wb') as f:
                pickle.dump(embedding_data, f)

        print(f"Models saved to {self.model_dir}")

    def load_models(self):
        classifier_path = self.model_dir / 'classifier.pkl'
        if classifier_path.exists():
            with open(classifier_path, 'rb') as f:
                data = pickle.load(f)

            input_size = data['layers'][0]['w'].shape[0]
            output_size = len(data['error_types'])
            hidden_sizes = [layer['w'].shape[1] for layer in data['layers'][:-1]]

            self.classifier = NeuralNetwork(input_size, hidden_sizes, output_size)
            self.classifier.layers = data['layers']
            self.error_types = data['error_types']
            self.type_to_idx = data['type_to_idx']
            self.feature_mean = data['feature_mean']
            self.feature_std = data['feature_std']
            self.trained = True

            print("Classifier loaded successfully")

        embedding_path = self.model_dir / 'embeddings.pkl'
        if embedding_path.exists():
            with open(embedding_path, 'rb') as f:
                data = pickle.load(f)

            self.embedding_model = ErrorEmbedding(embedding_dim=data['embedding_dim'])
            self.embedding_model.embeddings = data['embeddings']
            self.embedding_model.word_to_idx = data['word_to_idx']
            self.embedding_model.idx_to_word = data['idx_to_word']
            self.embedding_model.vocab_size = len(data['word_to_idx'])

            print("Embeddings loaded successfully")

if __name__ == '__main__':
    examples = [
        TrainingExample("NameError: name 'x' is not defined", "NameError", "python"),
        TrainingExample("TypeError: cannot concatenate str and int", "TypeError", "python"),
        TrainingExample("IndentationError: unexpected indent", "IndentationError", "python"),
        TrainingExample("ReferenceError: foo is not defined", "ReferenceError", "javascript"),
        TrainingExample("TypeError: Cannot read property of undefined", "TypeError", "javascript"),
        TrainingExample("SyntaxError: Unexpected token", "SyntaxError", "javascript"),
    ]

    engine = MLEngine()
    engine.train_classifier(examples, epochs=50)
    engine.train_embeddings(examples, epochs=5)

    test_error = "NameError: name 'foo' is not defined"
    result = engine.classify_error(test_error)
    print(f"\nClassification result for: {test_error}")
    print(json.dumps(result, indent=2))

    engine.save_models()