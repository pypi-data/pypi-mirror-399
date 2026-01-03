"""
FastAPI Server for Meitei Senter.

Provides a REST API for sentence boundary detection in Meitei Mayek text.

Usage:
    # Run with uvicorn
    uvicorn meitei_senter.server:app --reload
    
    # Or run directly
    python -m meitei_senter.server
    
    # Or use the CLI
    meitei-senter-server --port 8000
"""

import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import __version__
from .model import MeiteiSentenceSplitter


# Initialize FastAPI app
app = FastAPI(
    title="Meitei Senter API",
    description="""
## Sentence Boundary Detection for Meitei Mayek (Manipuri)

A lightweight, context-aware sentence splitter API.

### Features:
- 🚀 Fast sentence splitting
- 🎯 94.7% F-Score accuracy
- ⚡ SentencePiece tokenization
- 🔧 Multiple splitting modes
    """,
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global splitter instance
_splitter: Optional[MeiteiSentenceSplitter] = None


def get_splitter() -> MeiteiSentenceSplitter:
    """Get or create the sentence splitter instance."""
    global _splitter
    if _splitter is None:
        model_dir = os.path.dirname(__file__)
        _splitter = MeiteiSentenceSplitter(
            pth_path=os.path.join(model_dir, "meitei_senter.pth"),
            spm_path=os.path.join(model_dir, "meitei_tokenizer.model"),
            config_path=os.path.join(model_dir, "meitei_senter.json"),
            use_neural=False  # Default to delimiter-based (faster)
        )
    return _splitter


# Request/Response models
class SplitRequest(BaseModel):
    """Request model for sentence splitting."""
    text: str = Field(..., description="Text to split into sentences", min_length=1)
    use_neural: bool = Field(False, description="Use neural network model (slower but more accurate for complex cases)")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "ꯆꯦꯔꯣꯀꯤ ꯑꯁꯤ ꯑꯣꯀ꯭ꯂꯥꯍꯣꯃꯥꯒꯤ ꯁꯍꯔꯅꯤ ꯫ ꯃꯁꯤ ꯌꯥꯝꯅ ꯆꯥꯎꯏ ꯫",
                "use_neural": False
            }
        }


class SplitResponse(BaseModel):
    """Response model for sentence splitting."""
    sentences: List[str] = Field(..., description="List of extracted sentences")
    count: int = Field(..., description="Number of sentences found")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sentences": ["ꯆꯦꯔꯣꯀꯤ ꯑꯁꯤ ꯑꯣꯀ꯭ꯂꯥꯍꯣꯃꯥꯒꯤ ꯁꯍꯔꯅꯤ꯫", "ꯃꯁꯤ ꯌꯥꯝꯅ ꯆꯥꯎꯏ꯫"],
                "count": 2
            }
        }


class TokenizeRequest(BaseModel):
    """Request model for tokenization."""
    text: str = Field(..., description="Text to tokenize", min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "ꯆꯦꯔꯣꯀꯤ ꯑꯁꯤ"
            }
        }


class TokenizeResponse(BaseModel):
    """Response model for tokenization."""
    tokens: List[str] = Field(..., description="List of subword tokens")
    token_ids: List[int] = Field(..., description="List of token IDs")
    count: int = Field(..., description="Number of tokens")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str
    model_loaded: bool


# API Endpoints
@app.post("/", tags=["Info"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Meitei Senter API",
        "version": __version__,
        "description": "Sentence boundary detection for Meitei Mayek",
        "docs": "/docs",
        "endpoints": {
            "split": "POST /split - Split text into sentences",
            "tokenize": "POST /tokenize - Tokenize text",
            "health": "POST /health - Health check"
        }
    }


@app.post("/health", response_model=HealthResponse, tags=["Info"])
async def health_check():
    """Health check endpoint."""
    splitter = get_splitter()
    return {
        "status": "ok",
        "version": __version__,
        "model_loaded": splitter is not None
    }


@app.post("/split", response_model=SplitResponse, tags=["Sentence Splitting"])
async def split_sentences(request: SplitRequest):
    """
    Split text into sentences.
    
    - **text**: The Meitei Mayek text to split
    - **use_neural**: Use neural network (default: False for faster processing)
    """
    try:
        splitter = get_splitter()
        
        if request.use_neural:
            # Create a new splitter with neural mode
            model_dir = os.path.dirname(__file__)
            neural_splitter = MeiteiSentenceSplitter(
                pth_path=os.path.join(model_dir, "meitei_senter.pth"),
                spm_path=os.path.join(model_dir, "meitei_tokenizer.model"),
                config_path=os.path.join(model_dir, "meitei_senter.json"),
                use_neural=True
            )
            sentences = neural_splitter.split_sentences(request.text)
        else:
            sentences = splitter.split_sentences(request.text)
        
        return {
            "sentences": sentences,
            "count": len(sentences)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tokenize", response_model=TokenizeResponse, tags=["Tokenization"])
async def tokenize_text(request: TokenizeRequest):
    """
    Tokenize text into subword tokens using SentencePiece.
    
    - **text**: The text to tokenize
    """
    try:
        splitter = get_splitter()
        tokens, token_ids = splitter.tokenize(request.text)
        
        return {
            "tokens": tokens,
            "token_ids": token_ids,
            "count": len(tokens)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the FastAPI server."""
    import uvicorn
    uvicorn.run(
        "meitei_senter.server:app",
        host=host,
        port=port,
        reload=reload
    )


def main():
    """CLI entry point for the server."""
    import argparse
    
    parser = argparse.ArgumentParser(
        prog="meitei-senter-server",
        description="Run the Meitei Senter API server"
    )
    parser.add_argument(
        "--host", "-H",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload", "-r",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    args = parser.parse_args()
    run_server(args.host, args.port, args.reload)


if __name__ == "__main__":
    main()
