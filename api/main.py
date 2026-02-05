"""
BookBot API - FastAPI backend for web interface.

Provides REST endpoints for text analysis, file upload, and results.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add parent directory to path for bookbot imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bookbot.analyzer import BookAnalyzer, analyze_text as analyze_text_func

app = FastAPI(
    title="BookBot API",
    description="Text analysis API for books and documents",
    version="1.0.0",
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TextAnalysisRequest(BaseModel):
    """Request body for text analysis."""
    text: str
    title: Optional[str] = "Untitled"
    include_sentiment: bool = False


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )


@app.post("/api/analyze")
async def analyze_file(
    file: UploadFile = File(...),
    include_sentiment: bool = Form(False)
):
    """
    Analyze an uploaded text file.
    
    Accepts .txt, .pdf, .epub files.
    """
    # Validate file type
    allowed_extensions = {'.txt', '.text', '.md', '.pdf', '.epub'}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Allowed: {allowed_extensions}"
        )
    
    # Save to temp file
    try:
        with tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=file_ext
        ) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Analyze
        analyzer = BookAnalyzer(tmp_path)
        result = analyzer.analyze(include_sentiment=include_sentiment)
        
        # Build response
        response = result.to_dict()
        response['filename'] = file.filename
        response['file_size'] = len(content)
        response['analyzed_at'] = datetime.now().isoformat()
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temp file
        if 'tmp_path' in locals():
            try:
                os.unlink(tmp_path)
            except:
                pass


@app.post("/api/analyze-text")
async def analyze_text(request: TextAnalysisRequest):
    """
    Analyze text content directly.
    
    Useful for pasted text or API integrations.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        result = analyze_text_func(request.text, title=request.title)
        
        # Add sentiment if requested
        if request.include_sentiment:
            try:
                from bookbot.sentiment import analyze_sentiment
                sentiment = analyze_sentiment(request.text, detailed=True)
                result.sentiment = sentiment.to_dict()
            except ImportError:
                pass
        
        response = result.to_dict()
        response['analyzed_at'] = datetime.now().isoformat()
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
