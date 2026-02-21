"""
PDF Genius Backend - FastAPI Application
Main entry point for the PDF processing and AI chat service
"""

import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

from .core.config import settings
from .core.database import engine, Base, get_db
from .services.pdf_processor import PDFProcessor
from .services.ai_chat import AIChatService
from .services.auth import get_current_user
from .models.user import User

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the application"""
    # Startup
    print("Starting PDF Genius backend...")
    yield
    # Shutdown
    print("Shutting down PDF Genius backend...")

app = FastAPI(
    title="PDF Genius API",
    description="Process PDFs like a pro, chat with them like a human",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
pdf_processor = PDFProcessor()
ai_chat = AIChatService()

# Models
class ChatRequest(BaseModel):
    question: str
    pdf_id: Optional[str] = None

class ConversionRequest(BaseModel):
    format: str = "docx"  # docx, excel, ppt, html, jpg, png

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "pdf-genius"}

# Auth endpoints
@app.post("/auth/register")
async def register():
    """Register new user"""
    return {"message": "Register endpoint"}

@app.post("/auth/login")
async def login():
    """Login user"""
    return {"message": "Login endpoint"}

# PDF Processing endpoints
@app.post("/pdf/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a PDF file for processing"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Save file temporarily
        file_path = f"/tmp/{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process metadata
        metadata = pdf_processor.get_metadata(file_path)
        
        return {
            "filename": file.filename,
            "size": len(content),
            "pages": metadata.get("pages", 0),
            "message": "PDF uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/pdf/convert/{pdf_id}")
async def convert_pdf(
    pdf_id: str,
    conversion: ConversionRequest,
    current_user: User = Depends(get_current_user)
):
    """Convert PDF to another format"""
    try:
        # In production: Get file path from database using pdf_id
        # For now, using a sample file
        sample_pdf = "sample.pdf"  # Replace with actual file retrieval
        
        output_path = pdf_processor.convert(
            input_path=sample_pdf,
            output_format=conversion.format
        )
        
        return FileResponse(
            path=output_path,
            filename=f"converted.{conversion.format}",
            media_type="application/octet-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

@app.post("/pdf/merge")
async def merge_pdfs(
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """Merge multiple PDFs into one"""
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="At least 2 PDFs required")
    
    try:
        file_paths = []
        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail="All files must be PDFs")
            
            file_path = f"/tmp/{file.filename}"
            with open(file_path, "wb") as f:
                f.write(await file.read())
            file_paths.append(file_path)
        
        merged_path = pdf_processor.merge(file_paths)
        
        return FileResponse(
            path=merged_path,
            filename="merged.pdf",
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Merge failed: {str(e)}")

# AI Chat endpoints
@app.post("/chat/ask")
async def chat_with_pdf(
    chat_request: ChatRequest,
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user)
):
    """Ask questions about a PDF"""
    try:
        if file:
            # Process uploaded file
            file_path = f"/tmp/{file.filename}"
            with open(file_path, "wb") as f:
                f.write(await file.read())
            
            response = await ai_chat.ask_about_pdf(
                pdf_path=file_path,
                question=chat_request.question
            )
        elif chat_request.pdf_id:
            # Use existing PDF from database
            # In production: Retrieve file path from database
            response = await ai_chat.ask_about_pdf(
                pdf_path=f"stored/{chat_request.pdf_id}.pdf",
                question=chat_request.question
            )
        else:
            raise HTTPException(status_code=400, detail="Either file or pdf_id required")
        
        return {
            "answer": response["answer"],
            "sources": response.get("sources", []),
            "confidence": response.get("confidence", 0.0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.post("/chat/summarize")
async def summarize_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Summarize a PDF document"""
    try:
        file_path = f"/tmp/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        summary = await ai_chat.summarize_pdf(file_path)
        
        return {
            "summary": summary["text"],
            "length": summary.get("length", "short"),
            "key_points": summary.get("key_points", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

# Usage tracking
@app.get("/usage")
async def get_usage(current_user: User = Depends(get_current_user)):
    """Get current user's usage statistics"""
    return {
        "conversions_used": 0,
        "conversions_limit": 10,  # Based on subscription tier
        "ai_questions_used": 0,
        "ai_questions_limit": 5,
        "subscription_tier": "free"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)