"""
AI Chat router for PDF interaction
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.user import User, PDFFile, ChatSession
from ..schemas.user import UsageStats
from ..services.auth import AuthService
from ..services.ai_chat import AIChatService
from ..services.pdf_processor import PDFProcessor
from ..services.storage import StorageService
from ..services.usage import UsageService
from ..schemas.chat import ChatRequest, ChatResponse, SummaryRequest, DataExtractionRequest

router = APIRouter(prefix="/chat", tags=["chat"])

ai_chat = AIChatService()
pdf_processor = PDFProcessor()
storage_service = StorageService()
usage_service = UsageService()

@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """Ask a question about a PDF"""
    # Check usage limits
    if not usage_service.can_ask_ai_question(current_user):
        raise HTTPException(
            status_code=402,
            detail="AI question limit reached. Please upgrade your plan."
        )
    
    pdf_file = None
    temp_path = None
    
    try:
        # Handle file upload or existing file
        if request.file:
            # Process uploaded file
            if not request.file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400,
                    detail="File must be a PDF"
                )
            
            # Save temporarily
            temp_path = f"/tmp/{uuid.uuid4()}.pdf"
            with open(temp_path, "wb") as f:
                content = await request.file.read()
                f.write(content)
            
            file_path = temp_path
            
        elif request.pdf_id:
            # Use existing file from database
            pdf_file = db.query(PDFFile).filter(
                PDFFile.id == request.pdf_id,
                PDFFile.user_id == current_user.id
            ).first()
            
            if not pdf_file:
                raise HTTPException(status_code=404, detail="PDF file not found")
            
            # Get file from storage
            file_stream = storage_service.get_file(pdf_file.storage_path)
            if not file_stream:
                raise HTTPException(status_code=404, detail="File not found in storage")
            
            # Save to temp file
            temp_path = f"/tmp/{request.pdf_id}.pdf"
            with open(temp_path, "wb") as f:
                f.write(file_stream.read())
            
            file_path = temp_path
            
        else:
            raise HTTPException(
                status_code=400,
                detail="Either file or pdf_id must be provided"
            )
        
        # Ask AI question
        response = await ai_chat.ask_about_pdf(file_path, request.question)
        
        # Track usage
        usage_service.track_ai_question(current_user, db)
        
        # Create or update chat session
        chat_session = None
        if pdf_file:
            chat_session = db.query(ChatSession).filter(
                ChatSession.pdf_file_id == pdf_file.id,
                ChatSession.user_id == current_user.id
            ).first()
            
            if not chat_session:
                chat_session = ChatSession(
                    id=str(uuid.uuid4()),
                    pdf_file_id=pdf_file.id,
                    user_id=current_user.id,
                    messages=json.dumps([{
                        "role": "user",
                        "content": request.question,
                        "timestamp": datetime.utcnow().isoformat()
                    }, {
                        "role": "assistant",
                        "content": response["answer"],
                        "timestamp": datetime.utcnow().isoformat()
                    }])
                )
                db.add(chat_session)
            else:
                # Update existing session
                messages = json.loads(chat_session.messages)
                messages.extend([{
                    "role": "user",
                    "content": request.question,
                    "timestamp": datetime.utcnow().isoformat()
                }, {
                    "role": "assistant",
                    "content": response["answer"],
                    "timestamp": datetime.utcnow().isoformat()
                }])
                chat_session.messages = json.dumps(messages)
                chat_session.updated_at = datetime.utcnow()
                chat_session.last_activity = datetime.utcnow()
            
            db.commit()
        
        return ChatResponse(
            answer=response["answer"],
            sources=response.get("sources", []),
            confidence=response.get("confidence", 0.0),
            session_id=chat_session.id if chat_session else None,
            timestamp=response.get("timestamp")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question: {str(e)}"
        )
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/summarize")
async def summarize_pdf(
    request: SummaryRequest,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """Summarize a PDF"""
    # Check usage limits
    if not usage_service.can_ask_ai_question(current_user):
        raise HTTPException(
            status_code=402,
            detail="AI question limit reached. Please upgrade your plan."
        )
    
    temp_path = None
    
    try:
        if request.file:
            # Process uploaded file
            if not request.file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400,
                    detail="File must be a PDF"
                )
            
            temp_path = f"/tmp/{uuid.uuid4()}.pdf"
            with open(temp_path, "wb") as f:
                content = await request.file.read()
                f.write(content)
            
            file_path = temp_path
            
        elif request.pdf_id:
            # Use existing file
            pdf_file = db.query(PDFFile).filter(
                PDFFile.id == request.pdf_id,
                PDFFile.user_id == current_user.id
            ).first()
            
            if not pdf_file:
                raise HTTPException(status_code=404, detail="PDF file not found")
            
            file_stream = storage_service.get_file(pdf_file.storage_path)
            if not file_stream:
                raise HTTPException(status_code=404, detail="File not found in storage")
            
            temp_path = f"/tmp/{request.pdf_id}.pdf"
            with open(temp_path, "wb") as f:
                f.write(file_stream.read())
            
            file_path = temp_path
            
        else:
            raise HTTPException(
                status_code=400,
                detail="Either file or pdf_id must be provided"
            )
        
        # Get summary
        summary = await ai_chat.summarize_pdf(file_path, request.length)
        
        # Track usage
        usage_service.track_ai_question(current_user, db)
        
        return {
            "summary": summary["text"],
            "length": summary["length"],
            "key_points": summary.get("key_points", []),
            "word_count": summary.get("word_count", 0),
            "timestamp": summary.get("timestamp")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to summarize PDF: {str(e)}"
        )
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/extract")
async def extract_data(
    request: DataExtractionRequest,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """Extract specific data from PDF"""
    # Check usage limits
    if not usage_service.can_ask_ai_question(current_user):
        raise HTTPException(
            status_code=402,
            detail="AI question limit reached. Please upgrade your plan."
        )
    
    temp_path = None
    
    try:
        if request.file:
            # Process uploaded file
            if not request.file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400,
                    detail="File must be a PDF"
                )
            
            temp_path = f"/tmp/{uuid.uuid4()}.pdf"
            with open(temp_path, "wb") as f:
                content = await request.file.read()
                f.write(content)
            
            file_path = temp_path
            
        elif request.pdf_id:
            # Use existing file
            pdf_file = db.query(PDFFile).filter(
                PDFFile.id == request.pdf_id,
                PDFFile.user_id == current_user.id
            ).first()
            
            if not pdf_file:
                raise HTTPException(status_code=404, detail="PDF file not found")
            
            file_stream = storage_service.get_file(pdf_file.storage_path)
            if not file_stream:
                raise HTTPException(status_code=404, detail="File not found in storage")
            
            temp_path = f"/tmp/{request.pdf_id}.pdf"
            with open(temp_path, "wb") as f:
                f.write(file_stream.read())
            
            file_path = temp_path
            
        else:
            raise HTTPException(
                status_code=400,
                detail="Either file or pdf_id must be provided"
            )
        
        # Extract data
        result = await ai_chat.extract_data(file_path, request.data_type)
        
        # Track usage
        usage_service.track_ai_question(current_user, db)
        
        return {
            "data_type": result["data_type"],
            "items": result["items"],
            "count": result["count"],
            "timestamp": result.get("timestamp")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract data: {str(e)}"
        )
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/translate")
async def translate_pdf(
    pdf_id: str,
    target_language: str,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """Translate PDF content"""
    # Check usage limits
    if not usage_service.can_ask_ai_question(current_user):
        raise HTTPException(
            status_code=402,
            detail="AI question limit reached. Please upgrade your plan."
        )
    
    temp_path = None
    
    try:
        # Get file from database
        pdf_file = db.query(PDFFile).filter(
            PDFFile.id == pdf_id,
            PDFFile.user_id == current_user.id
        ).first()
        
        if not pdf_file:
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        # Get file from storage
        file_stream = storage_service.get_file(pdf_file.storage_path)
        if not file_stream:
            raise HTTPException(status_code=404, detail="File not found in storage")
        
        # Save to temp file
        temp_path = f"/tmp/{pdf_id}.pdf"
        with open(temp_path, "wb") as f:
            f.write(file_stream.read())
        
        # Translate
        translation = await ai_chat.translate_pdf(temp_path, target_language)
        
        # Track usage (counts as AI question)
        usage_service.track_ai_question(current_user, db)
        
        return {
            "original_filename": pdf_file.original_filename,
            "target_language": target_language,
            "translation": translation["translation"],
            "is_complete": translation["is_complete"],
            "timestamp": translation.get("timestamp")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to translate PDF: {str(e)}"
        )
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

@router.get("/sessions")
async def list_chat_sessions(
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """List user's chat sessions"""
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.last_activity.desc()).all()
    
    return [
        {
            "id": session.id,
            "pdf_file_id": session.pdf_file_id,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "message_count": len(json.loads(session.messages)) if session.messages else 0
        }
        for session in sessions
    ]

@router.get("/sessions/{session_id}")
async def get_chat_session(
    session_id: str,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat session details"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    messages = json.loads(session.messages) if session.messages else []
    
    return {
        "id": session.id,
        "pdf_file_id": session.pdf_file_id,
        "messages": messages,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
        "summary": session.summary
    }

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat session"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    db.delete(session)
    db.commit()
    
    return {"message": "Chat session deleted successfully"}

@router.get("/usage", response_model=UsageStats)
async def get_chat_usage(
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat usage statistics"""
    limits = current_user.get_limits()
    
    return UsageStats(
        conversions_used=current_user.conversions_used,
        conversions_limit=limits["conversions"],
        ai_questions_used=current_user.ai_questions_used,
        ai_questions_limit=limits["ai_questions"],
        subscription_tier=current_user.subscription_tier,
        reset_date=current_user.last_reset_date
    )