# Meitei Senter

A lightweight sentence boundary detector for **Meitei Mayek (Manipuri)** text.

[![PyPI version](https://badge.fury.io/py/meitei-senter.svg)](https://pypi.org/project/meitei-senter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
![Model Size](https://img.shields.io/badge/model%20size-1MB-green)
![F-Score](https://img.shields.io/badge/F--Score-94.7%25-brightgreen)

## Features

- 🚀 **Lightweight** - Only ~1MB model, minimal dependencies
- 🎯 **Accurate** - 94.7% F-Score on Meitei text
- 🔧 **Easy to use** - Simple Python API and CLI
- ⚡ **Fast** - Optimized for quick inference

---

## Installation

```bash
pip install meitei-senter
```

### Optional: spaCy Backend (for higher accuracy)
```bash
pip install meitei-senter[spacy]
```

---

## Quick Start

### Python API

```python
from meitei_senter import MeiteiSentenceSplitter

# Initialize the splitter
splitter = MeiteiSentenceSplitter()

# Split text into sentences
text = "ꯆꯦꯔꯣꯀꯤ ꯑꯁꯤ ꯑꯣꯀ꯭ꯂꯥꯍꯣꯃꯥꯒꯤ ꯁꯍꯔꯅꯤ ꯫ ꯃꯁꯤ ꯌꯥꯝꯅ ꯆꯥꯎꯏ ꯫"
sentences = splitter.split_sentences(text)

for i, sent in enumerate(sentences, 1):
    print(f"{i}. {sent}")
```

**Output:**
```
1. ꯆꯦꯔꯣꯀꯤ ꯑꯁꯤ ꯑꯣꯀ꯭ꯂꯥꯍꯣꯃꯥꯒꯤ ꯁꯍꯔꯅꯤ ꯫
2. ꯃꯁꯤ ꯌꯥꯝꯅ ꯆꯥꯎꯏ ꯫
```

### Command Line

```bash
# Interactive mode
meitei-senter --interactive

# Direct text input
meitei-senter --text "ꯆꯦꯔꯣꯀꯤ ꯑꯁꯤ ꯑꯣꯀ꯭ꯂꯥꯍꯣꯃꯥꯒꯤ ꯁꯍꯔꯅꯤ ꯫ ꯃꯁꯤ ꯌꯥꯝꯅ ꯆꯥꯎꯏ ꯫"

# Show version
meitei-senter --version
```

---

## Advanced Usage

### Using the Convenient Loader

```python
from meitei_senter import load_splitter

# Load with default (delimiter-based) backend
splitter = load_splitter()

# Or with spaCy backend (requires spacy extra)
splitter = load_splitter(use_spacy=True)

sentences = splitter.split_sentences("Your Meitei text here ꯫")
```

### Using Neural Network Mode

```python
from meitei_senter import MeiteiSentenceSplitter

# Enable neural mode for context-aware splitting
splitter = MeiteiSentenceSplitter(use_neural=True)
sentences = splitter.split_sentences(text)
```

### Direct Callable Interface

```python
from meitei_senter import MeiteiSentenceSplitter

splitter = MeiteiSentenceSplitter()

# Call splitter directly
sentences = splitter("ꯆꯦꯔꯣꯀꯤ ꯑꯁꯤ... ꯫ ꯃꯁꯤ ꯌꯥꯝꯅ ꯆꯥꯎꯏ ꯫")
```

### With spaCy (Custom Tokenizer)

```python
import spacy
import os
from meitei_senter import MeiteiTokenizer, get_model_path

# Get path to bundled model
model_path = os.path.join(get_model_path(), 'meitei_tokenizer.model')

# Create blank spaCy model with custom tokenizer
nlp = spacy.blank("xx")
nlp.tokenizer = MeiteiTokenizer(model_path, nlp.vocab)

doc = nlp("ꯆꯦꯔꯣꯀꯤ ꯑꯁꯤ ꯑꯣꯀ꯭ꯂꯥꯍꯣꯃꯥꯒꯤ ꯁꯍꯔꯅꯤ ꯫")
print([token.text for token in doc])
# Output: ['ꯆꯦ', 'ꯔꯣ', 'ꯀꯤ', 'ꯑꯁꯤ', 'ꯑꯣꯀ꯭ꯂꯥꯍꯣꯃꯥ', 'ꯒꯤ', 'ꯁꯍꯔ', 'ꯅꯤ', '꯫']
```

---

## 🌐 REST API Server

Start the FastAPI server for HTTP-based sentence splitting:

### Start Server

```bash
# Using CLI
meitei-senter-server --port 8000

# Or with uvicorn directly
uvicorn meitei_senter.server:app --host 0.0.0.0 --port 8000

# With auto-reload for development
meitei-senter-server --port 8000 --reload
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/split` | POST | Split text into sentences |
| `/split` | GET | Split text (query param) |
| `/tokenize` | POST | Tokenize text |
| `/docs` | GET | Swagger UI |
| `/redoc` | GET | ReDoc |

### Example Requests

**POST /split**
```bash
curl -X POST "http://localhost:8000/split" \
     -H "Content-Type: application/json" \
     -d '{"text": "ꯆꯦꯔꯣꯀꯤ ꯑꯁꯤ ꯑꯣꯀ꯭ꯂꯥꯍꯣꯃꯥꯒꯤ ꯁꯍꯔꯅꯤ ꯫ ꯃꯁꯤ ꯌꯥꯝꯅ ꯆꯥꯎꯏ ꯫"}'
```

**Response:**
```json
{
  "sentences": ["ꯆꯦꯔꯣꯀꯤ ꯑꯁꯤ ꯑꯣꯀ꯭ꯂꯥꯍꯣꯃꯥꯒꯤ ꯁꯍꯔꯅꯤ꯫", "ꯃꯁꯤ ꯌꯥꯝꯅ ꯆꯥꯎꯏ꯫"],
  "count": 2
}
```

**GET /split (query param)**
```bash
curl "http://localhost:8000/split?text=ꯆꯦꯔꯣꯀꯤ%20ꯑꯁꯤ...%20꯫"
```

**POST /tokenize**
```bash
curl -X POST "http://localhost:8000/tokenize" \
     -H "Content-Type: application/json" \
     -d '{"text": "ꯆꯦꯔꯣꯀꯤ ꯑꯁꯤ"}'
```

---

## 📊 Model Details

| Feature | Specification |
|---------|---------------|
| **Model Size** | ~1 MB |
| **Tokenizer** | SentencePiece (Unigram, 8K vocab) |
| **Architecture** | CNN (HashEmbedCNN) |
| **F-Score** | 94.71% |
| **Precision** | 93.94% |
| **Recall** | 95.49% |

---

## 📂 Repository Structure

```
mni_tokenizer/
├── meitei_senter/              # Main package
│   ├── __init__.py             # Package exports
│   ├── cli.py                  # Command-line interface
│   ├── model.py                # PyTorch model & splitter
│   ├── tokenizer.py            # spaCy tokenizer
│   ├── meitei_tokenizer.model  # SentencePiece model
│   ├── meitei_senter.pth       # PyTorch weights
│   └── meitei_senter.json      # Model config
├── pyproject.toml              # Build configuration
└── README.md                   # This file
```

---

## API Reference

### `MeiteiSentenceSplitter`

Main class for sentence splitting.

```python
MeiteiSentenceSplitter(
    pth_path: str = None,      # Path to PyTorch model
    spm_path: str = None,      # Path to SentencePiece model
    config_path: str = None,   # Path to config JSON
    use_neural: bool = False   # Enable neural network mode
)
```

**Methods:**
| Method | Description |
|--------|-------------|
| `split_sentences(text)` | Split text into list of sentences |
| `tokenize(text)` | Tokenize text into pieces and IDs |
| `__call__(text)` | Direct callable interface |

### `MeiteiTokenizer`

spaCy-compatible tokenizer using SentencePiece.

```python
MeiteiTokenizer(model_path: str, vocab: spacy.Vocab)
```

### `load_splitter`

Convenience function to load a pre-configured splitter.

```python
load_splitter(use_spacy: bool = False)
```

---

## 🔧 Development

```bash
# Clone repository
git clone https://github.com/Okramjimmy/mni_tokenizer.git
cd mni_tokenizer

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Build package
python -m build

# Upload to PyPI
twine upload dist/*
```

---

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 📚 Citation

If you use this in your research, please cite:

```bibtex
@software{meitei_senter,
  author = {Okram Jimmy},
  title = {Meitei Senter: Sentence Boundary Detection for Meitei Mayek},
  year = {2024},
  url = {https://github.com/Okramjimmy/mni_tokenizer}
}
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


## 📧 Contact

- **Author**: Okram Jimmy
- **Email**: okramjimmy@gmail.com
- **GitHub**: [@Okramjimmy](https://github.com/Okramjimmy)
