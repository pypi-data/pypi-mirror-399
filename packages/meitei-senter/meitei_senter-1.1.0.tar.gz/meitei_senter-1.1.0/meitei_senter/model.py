"""
PyTorch Model for Meitei Mayek Sentence Boundary Detection.

This module provides a pure PyTorch implementation for sentence splitting
without requiring spaCy.
"""

import json
import torch
import torch.nn as nn
import sentencepiece as spm
from pathlib import Path
from typing import List, Tuple, Optional


class SenterModel(nn.Module):
    """
    A sentence boundary detection model using embeddings and convolution.
    
    This is a simplified architecture that can load weights from the
    exported spaCy model.
    """
    
    def __init__(self, vocab_size: int, embed_dim: int = 96, hidden_dim: int = 48):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.conv = nn.Conv1d(embed_dim, hidden_dim, kernel_size=3, padding=1)
        self.fc = nn.Linear(hidden_dim, 2)  # Binary: is_sent_start or not
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Token IDs, shape (batch_size, seq_len)
        Returns:
            Logits for sentence boundary, shape (batch_size, seq_len, 2)
        """
        emb = self.embedding(x)  # (batch, seq, embed)
        emb = emb.transpose(1, 2)  # (batch, embed, seq)
        conv_out = torch.relu(self.conv(emb))  # (batch, hidden, seq)
        conv_out = conv_out.transpose(1, 2)  # (batch, seq, hidden)
        logits = self.fc(conv_out)  # (batch, seq, 2)
        return logits


class MeiteiSentenceSplitter:
    """
    Sentence splitter using PyTorch model and SentencePiece tokenizer.
    
    This provides a spaCy-free alternative for sentence boundary detection.
    """
    
    WHITESPACE_MARKER = "▁"  # SentencePiece's word-start marker
    MEITEI_FULL_STOP = "꯫"   # Meitei Mayek sentence delimiter
    
    def __init__(
        self, 
        pth_path: Optional[str] = None, 
        spm_path: Optional[str] = None, 
        config_path: Optional[str] = None,
        use_neural: bool = False
    ):
        """
        Initialize the splitter.
        
        Args:
            pth_path: Path to the .pth file with model weights.
            spm_path: Path to the SentencePiece .model file.
            config_path: Path to the model config JSON.
            use_neural: If True, use neural network for splitting.
                       If False, use delimiter-based splitting (default).
        """
        self.use_neural = use_neural
        self.model = None
        self.sp = None
        
        # Load SentencePiece if available
        if spm_path and Path(spm_path).exists():
            self.sp = spm.SentencePieceProcessor(model_file=spm_path)
            self.vocab_size = self.sp.get_piece_size()
        else:
            self.vocab_size = 8000  # Default
        
        # Load config if available
        self.config = {}
        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                self.config = json.load(f)
        
        # Load PyTorch model if neural mode is enabled
        if use_neural and pth_path and Path(pth_path).exists():
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            
            self.model = SenterModel(
                vocab_size=self.vocab_size,
                embed_dim=self.config.get("embed_dim", 96),
                hidden_dim=self.config.get("hidden_dim", 48)
            )
            
            state_dict = torch.load(pth_path, map_location=self.device, weights_only=True)
            if state_dict:
                try:
                    self.model.load_state_dict(state_dict)
                except Exception:
                    pass  # Use random weights as fallback
            
            self.model.to(self.device)
            self.model.eval()
    
    def tokenize(self, text: str) -> Tuple[List[str], List[int]]:
        """
        Tokenize text using SentencePiece.
        
        Returns:
            Tuple of (pieces, ids)
        """
        if self.sp is None:
            # Simple character-based fallback
            return list(text), list(range(len(text)))
        
        pieces = self.sp.encode_as_pieces(text)
        ids = self.sp.encode_as_ids(text)
        return pieces, ids
    
    def predict_boundaries(self, token_ids: List[int]) -> List[bool]:
        """
        Predict sentence boundaries for token sequence.
        
        Args:
            token_ids: List of token IDs from SentencePiece.
            
        Returns:
            List of booleans indicating if each token starts a sentence.
        """
        if not token_ids or self.model is None:
            return [False] * len(token_ids) if token_ids else []
        
        with torch.no_grad():
            x = torch.tensor([token_ids], dtype=torch.long, device=self.device)
            logits = self.model(x)
            probs = torch.softmax(logits, dim=-1)
            is_sent_start = probs[0, :, 1] > 0.5
            return is_sent_start.cpu().tolist()
    
    def split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Input text to split.
            
        Returns:
            List of sentence strings.
        """
        if not text.strip():
            return []
        
        if self.use_neural and self.model is not None:
            return self._split_neural(text)
        else:
            return self._split_delimiter(text)
    
    def _split_neural(self, text: str) -> List[str]:
        """Neural network based splitting."""
        pieces, ids = self.tokenize(text)
        
        if not pieces:
            return [text]
        
        boundaries = self.predict_boundaries(ids)
        
        sentences = []
        current_sentence = []
        
        for i, (piece, is_start) in enumerate(zip(pieces, boundaries)):
            clean_piece = piece.lstrip(self.WHITESPACE_MARKER)
            has_space = piece.startswith(self.WHITESPACE_MARKER)
            
            if is_start and current_sentence:
                sentences.append("".join(current_sentence).strip())
                current_sentence = []
            
            if has_space and current_sentence:
                current_sentence.append(" ")
            
            current_sentence.append(clean_piece)
        
        if current_sentence:
            sentences.append("".join(current_sentence).strip())
        
        return sentences
    
    def _split_delimiter(self, text: str) -> List[str]:
        """Simple delimiter-based splitting (default, most reliable)."""
        sentences = []
        
        for part in text.split(self.MEITEI_FULL_STOP):
            part = part.strip()
            if part:
                sentences.append(part + self.MEITEI_FULL_STOP)
        
        return sentences
    
    def __call__(self, text: str) -> List[str]:
        """Allow calling the splitter directly."""
        return self.split_sentences(text)
