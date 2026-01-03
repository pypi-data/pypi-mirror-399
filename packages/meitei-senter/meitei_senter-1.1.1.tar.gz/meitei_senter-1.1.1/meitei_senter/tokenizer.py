"""
Custom Tokenizer for Meitei Mayek using SentencePiece.

This module wraps a pre-trained SentencePiece model to work as a spaCy tokenizer.
It correctly handles whitespace by interpreting SentencePiece's ▁ (U+2581) marker.
"""

import spacy
from spacy.tokens import Doc
from spacy.vocab import Vocab
import sentencepiece as spm
from typing import List


class MeiteiTokenizer:
    """
    A custom spaCy tokenizer that uses SentencePiece for subword tokenization.

    SentencePiece uses the '▁' character (U+2581, LOWER ONE EIGHTH BLOCK) to
    represent the beginning of a word (i.e., a preceding space). This tokenizer
    correctly translates that into spaCy's `spaces` attribute.
    """

    WHITESPACE_MARKER = "▁"  # SentencePiece's word-start marker

    def __init__(self, model_path: str, vocab: Vocab):
        """
        Initialize the tokenizer.

        Args:
            model_path: Path to the SentencePiece .model file.
            vocab: The spaCy Vocab object to use for the Doc.
        """
        self.spp = spm.SentencePieceProcessor(model_file=model_path)
        self.vocab = vocab

    def __call__(self, text: str) -> Doc:
        """
        Tokenize the input text using SentencePiece and return a spaCy Doc.

        Args:
            text: The input string to tokenize.

        Returns:
            A spaCy Doc object with tokens and spaces correctly set.
        """
        if not text:
            return Doc(self.vocab, words=[], spaces=[])

        pieces = self.spp.encode_as_pieces(text)

        if not pieces:
            return Doc(self.vocab, words=[], spaces=[])

        words: List[str] = []
        spaces: List[bool] = []

        for i, piece in enumerate(pieces):
            # Check if this piece starts with the whitespace marker
            if piece.startswith(self.WHITESPACE_MARKER):
                # The previous token (if any) has a space after it
                if spaces:
                    spaces[-1] = True
                # Remove the marker from the token text
                word = piece[len(self.WHITESPACE_MARKER):]
            else:
                word = piece

            # Only add non-empty tokens
            if word:
                words.append(word)
                spaces.append(False)  # Default to no space after

        # Ensure lengths match
        if len(words) != len(spaces):
            spaces = [False] * len(words)

        return Doc(self.vocab, words=words, spaces=spaces)


def create_nlp(model_path: str) -> spacy.Language:
    """
    Create a blank spaCy Language object with the MeiteiTokenizer.

    Args:
        model_path: Path to the SentencePiece .model file.

    Returns:
        A spaCy Language object configured with the custom tokenizer.
    """
    nlp = spacy.blank("xx")  # 'xx' for multilingual/custom
    nlp.tokenizer = MeiteiTokenizer(model_path, nlp.vocab)
    return nlp
