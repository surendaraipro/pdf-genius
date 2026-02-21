"""
PDF Genius Backend - Simplified for Deployment
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import uuid
from datetime import datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    print("🚀 Starting PDF Genius backend...")
    yield
    print("🛑 Shutting down PDF Genius backend...")

app = FastAPI(
    title="PDF Genius API",
    description="Process PDFs like a pro, chat with them like a human",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/")
async def root():
    return {"message": "PDF Genius API", "status": "running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "pdf-genius", "timestamp": datetime.utcnow().isoformat()}

# Auth endpoints
@app.post("/auth/register")
async def register(email: str, password: str, username: str):
    return {
        "message": "Registration successful",
        "user": {
            "id": str(uuid.uuid4()),
            "email": email,
            "username": username,
            "subscription_tier": "free"
        },
        "access_token": "mock-token-" + str(uuid.uuid4())
    }

@app.post("/auth/login")
async def login(username: str, password: str):
    return {
        "access_token": "mock-token-" + str(uuid.uuid4()),
        "token_type": "bearer",
        "user_id": 1,
        "email": username if "@" in username else f"{username}@example.com",
        "subscription_tier": "free"
    }

# PDF endpoints
@app.post("/pdf/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    content = await file.read()
    
    return {
        "file_id": str(uuid.uuid4()),
        "filename": file.filename,
        "size": len(content),
        "pages": 1,  # Mock
        "message": "PDF uploaded successfully"
    }

@app.post("/pdf/convert/{file_id}")
async def convert_pdf(file_id: str, format: str = "docx"):
    return {
        "filename": f"converted.{format}",
        "format": format,
        "size": 1024,  # Mock
        "message": f"PDF converted to {format}"
    }

@app.post("/pdf/merge")
async def merge_pdfs(files: list[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="At least 2 PDFs required")
    
    return {
        "filename": "merged.pdf",
        "size": 2048,  # Mock
        "page_count": len(files),
        "message": "PDFs merged successfully"
    }

# AI Chat endpoints
@app.post("/chat/ask")
async def chat_with_pdf(pdf_id: str = None, question: str = "", file: UploadFile = File(None)):
    responses = [
        "Based on the document, the main findings suggest implementing AI tools can increase productivity by 20-30%.",
        "The key recommendations are: 1) Increase marketing budget, 2) Expand to new markets, 3) Reduce operational costs.",
        "I found important dates: January 15, 2024; March 30, 2024; and December 1, 2024.",
        "The document discusses three main points: market analysis, implementation strategy, and expected outcomes.",
        "According to the analysis, the projected ROI is 150% within the first year of implementation."
    ]
    
    import random
    answer = random.choice(responses)
    
    return {
        "answer": answer,
        "sources": [{"text": answer[:50] + "...", "page": 1, "confidence": 0.9}],
        "confidence": 0.95,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/chat/summarize")
async def summarize_pdf(file: UploadFile = File(...), length: str = "medium"):
    summary = "This document provides a comprehensive analysis of current market trends and recommends strategic initiatives for growth. Key findings include increased demand for AI solutions, opportunities in emerging markets, and the importance of digital transformation."
    
    return {
        "summary": summary,
        "length": length,
        "key_points": [
            "Increased demand for AI solutions",
            "Opportunities in emerging markets",
            "Importance of digital transformation"
        ],
        "word_count": len(summary.split()),
        "timestamp": datetime.utcnow().isoformat()
    }

# Usage tracking
@app.get("/usage")
async def get_usage():
    return {
        "conversions_used": 5,
        "conversions_limit": 10,
        "ai_questions_used": 3,
        "ai_questions_limit": 5,
        "subscription_tier": "free",
        "reset_date": datetime.utcnow().isoformat()
    }

# List files
@app.get("/pdf/files")
async def list_files():
    return [
        {
            "id": str(uuid.uuid4()),
            "filename": "sample_report.pdf",
            "size": 1024000,
            "pages": 15,
            "uploaded_at": datetime.utcnow().isoformat(),
            "processed": True
        }
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)