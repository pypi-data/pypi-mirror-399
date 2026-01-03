"""
Meitei Senter - Sentence Boundary Detection for Meitei Mayek (Manipuri).

A lightweight, context-aware sentence splitter using SentencePiece tokenization
and a neural network for boundary detection.
"""

__version__ = "1.1.1"
__author__ = "Okram Jimmy"
__email__ = "okramjimmy@gmail.com"

from .tokenizer import MeiteiTokenizer, create_nlp
from .model import SenterModel, MeiteiSentenceSplitter

__all__ = [
    "MeiteiTokenizer",
    "create_nlp", 
    "SenterModel",
    "MeiteiSentenceSplitter",
    "__version__",
]


def get_model_path():
    """Get the path to the bundled model files."""
    import os
    return os.path.dirname(__file__)


def load_splitter(use_spacy: bool = False):
    """
    Load the sentence splitter.
    
    Args:
        use_spacy: If True, use spaCy backend (more accurate).
                   If False, use pure PyTorch backend (no spaCy dependency).
    
    Returns:
        A sentence splitter object with a `split_sentences(text)` method.
    """
    import os
    model_dir = os.path.dirname(__file__)
    
    if use_spacy:
        import spacy
        model_path = os.path.join(model_dir, "spacy_model")
        spm_path = os.path.join(model_dir, "meitei_tokenizer.model")
        
        nlp = spacy.load(model_path)
        nlp.tokenizer = MeiteiTokenizer(spm_path, nlp.vocab)
        
        class SpacySplitter:
            def __init__(self, nlp):
                self.nlp = nlp
            
            def split_sentences(self, text):
                doc = self.nlp(text)
                return [sent.text for sent in doc.sents]
        
        return SpacySplitter(nlp)
    else:
        pth_path = os.path.join(model_dir, "meitei_senter.pth")
        spm_path = os.path.join(model_dir, "meitei_tokenizer.model")
        config_path = os.path.join(model_dir, "meitei_senter.json")
        
        return MeiteiSentenceSplitter(pth_path, spm_path, config_path)
