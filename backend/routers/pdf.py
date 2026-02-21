"""
PDF processing router
"""

import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.user import User, PDFFile
from ..schemas.user import UsageStats
from ..services.auth import AuthService
from ..services.pdf_processor import PDFProcessor
from ..services.storage import StorageService
from ..services.usage import UsageService

router = APIRouter(prefix="/pdf", tags=["pdf"])

pdf_processor = PDFProcessor()
storage_service = StorageService()
usage_service = UsageService()

@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a PDF file"""
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="File must be a PDF"
        )
    
    # Check file size limit based on subscription
    limits = current_user.get_limits()
    file_size = await _get_file_size(file)
    
    if file_size > limits["max_file_size_mb"] * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds limit of {limits['max_file_size_mb']}MB"
        )
    
    # Save file to storage
    file_info = storage_service.save_file(file, current_user.id)
    
    # Extract metadata
    temp_path = None
    try:
        # Save temporarily for processing
        temp_path = f"/tmp/{file_info['file_id']}.pdf"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        metadata = pdf_processor.get_metadata(temp_path)
        
        # Create database record
        pdf_file = PDFFile(
            id=file_info['file_id'],
            filename=file_info['file_id'],
            original_filename=file_info['original_filename'],
            file_size=file_info['size'],
            page_count=metadata.get('pages', 0),
            storage_path=file_info['storage_path'],
            user_id=current_user.id,
            title=metadata.get('title'),
            author=metadata.get('author'),
            subject=metadata.get('subject')
        )
        
        db.add(pdf_file)
        db.commit()
        db.refresh(pdf_file)
        
        # Extract text in background
        background_tasks = BackgroundTasks()
        background_tasks.add_task(
            _extract_text_background,
            pdf_file.id,
            temp_path,
            db
        )
        
        return {
            "file_id": pdf_file.id,
            "filename": pdf_file.original_filename,
            "size": pdf_file.file_size,
            "pages": pdf_file.page_count,
            "uploaded_at": pdf_file.uploaded_at.isoformat(),
            "message": "PDF uploaded successfully"
        }
        
    except Exception as e:
        # Clean up on error
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        storage_service.delete_file(file_info['storage_path'])
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload PDF: {str(e)}"
        )
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/convert/{file_id}")
async def convert_pdf(
    file_id: str,
    format: str,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """Convert PDF to another format"""
    # Check usage limits
    if not usage_service.can_perform_conversion(current_user):
        raise HTTPException(
            status_code=402,
            detail="Conversion limit reached. Please upgrade your plan."
        )
    
    # Get file from database
    pdf_file = db.query(PDFFile).filter(
        PDFFile.id == file_id,
        PDFFile.user_id == current_user.id
    ).first()
    
    if not pdf_file:
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    # Get file from storage
    file_stream = storage_service.get_file(pdf_file.storage_path)
    if not file_stream:
        raise HTTPException(status_code=404, detail="File not found in storage")
    
    try:
        # Save to temp file for processing
        temp_input = f"/tmp/{file_id}_input.pdf"
        with open(temp_input, "wb") as f:
            f.write(file_stream.read())
        
        # Convert PDF
        output_path = pdf_processor.convert(temp_input, format)
        
        # Read converted file
        with open(output_path, "rb") as f:
            converted_content = f.read()
        
        # Track usage
        usage_service.track_conversion(current_user, db)
        
        # Clean up temp files
        os.remove(temp_input)
        os.remove(output_path)
        
        return {
            "filename": f"{pdf_file.original_filename.rsplit('.', 1)[0]}.{format}",
            "content": converted_content,
            "format": format,
            "size": len(converted_content)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Conversion failed: {str(e)}"
        )

@router.post("/merge")
async def merge_pdfs(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """Merge multiple PDFs"""
    if len(files) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 PDFs required"
        )
    
    # Check usage limits
    if not usage_service.can_perform_conversion(current_user):
        raise HTTPException(
            status_code=402,
            detail="Conversion limit reached. Please upgrade your plan."
        )
    
    temp_paths = []
    try:
        # Save uploaded files temporarily
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400,
                    detail="All files must be PDFs"
                )
            
            temp_path = f"/tmp/{uuid.uuid4()}.pdf"
            with open(temp_path, "wb") as f:
                content = await file.read()
                f.write(content)
            temp_paths.append(temp_path)
        
        # Merge PDFs
        merged_path = pdf_processor.merge(temp_paths)
        
        # Read merged file
        with open(merged_path, "rb") as f:
            merged_content = f.read()
        
        # Track usage
        usage_service.track_conversion(current_user, db)
        
        return {
            "filename": "merged.pdf",
            "content": merged_content,
            "size": len(merged_content),
            "page_count": len(temp_paths)  # Approximate
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Merge failed: {str(e)}"
        )
    finally:
        # Clean up temp files
        for path in temp_paths:
            if os.path.exists(path):
                os.remove(path)
        if 'merged_path' in locals() and os.path.exists(merged_path):
            os.remove(merged_path)

@router.post("/compress/{file_id}")
async def compress_pdf(
    file_id: str,
    quality: str = "medium",
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """Compress PDF file"""
    # Check usage limits
    if not usage_service.can_perform_conversion(current_user):
        raise HTTPException(
            status_code=402,
            detail="Conversion limit reached. Please upgrade your plan."
        )
    
    # Get file from database
    pdf_file = db.query(PDFFile).filter(
        PDFFile.id == file_id,
        PDFFile.user_id == current_user.id
    ).first()
    
    if not pdf_file:
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    # Get file from storage
    file_stream = storage_service.get_file(pdf_file.storage_path)
    if not file_stream:
        raise HTTPException(status_code=404, detail="File not found in storage")
    
    try:
        # Save to temp file
        temp_input = f"/tmp/{file_id}_input.pdf"
        with open(temp_input, "wb") as f:
            f.write(file_stream.read())
        
        # Compress PDF
        compressed_path = pdf_processor.compress(temp_input, quality)
        
        # Read compressed file
        with open(compressed_path, "rb") as f:
            compressed_content = f.read()
        
        original_size = os.path.getsize(temp_input)
        compressed_size = len(compressed_content)
        savings = ((original_size - compressed_size) / original_size) * 100
        
        # Track usage
        usage_service.track_conversion(current_user, db)
        
        # Clean up
        os.remove(temp_input)
        os.remove(compressed_path)
        
        return {
            "filename": f"compressed_{pdf_file.original_filename}",
            "content": compressed_content,
            "original_size": original_size,
            "compressed_size": compressed_size,
            "savings_percentage": round(savings, 2),
            "quality": quality
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Compression failed: {str(e)}"
        )

@router.get("/files")
async def list_files(
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """List user's PDF files"""
    files = db.query(PDFFile).filter(
        PDFFile.user_id == current_user.id
    ).order_by(PDFFile.uploaded_at.desc()).all()
    
    return [
        {
            "id": file.id,
            "filename": file.original_filename,
            "size": file.file_size,
            "pages": file.page_count,
            "uploaded_at": file.uploaded_at.isoformat(),
            "processed": file.processed_at is not None
        }
        for file in files
    ]

@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a PDF file"""
    pdf_file = db.query(PDFFile).filter(
        PDFFile.id == file_id,
        PDFFile.user_id == current_user.id
    ).first()
    
    if not pdf_file:
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    # Delete from storage
    storage_service.delete_file(pdf_file.storage_path)
    
    # Delete from database
    db.delete(pdf_file)
    db.commit()
    
    return {"message": "File deleted successfully"}

@router.get("/usage", response_model=UsageStats)
async def get_usage(
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """Get current usage statistics"""
    limits = current_user.get_limits()
    
    return UsageStats(
        conversions_used=current_user.conversions_used,
        conversions_limit=limits["conversions"],
        ai_questions_used=current_user.ai_questions_used,
        ai_questions_limit=limits["ai_questions"],
        subscription_tier=current_user.subscription_tier,
        reset_date=current_user.last_reset_date
    )

# Helper functions
async def _get_file_size(file: UploadFile) -> int:
    """Get file size in bytes"""
    current_position = file.file.tell()
    file.file.seek(0, 2)  # Seek to end
    size = file.file.tell()
    file.file.seek(current_position)  # Reset position
    return size

def _extract_text_background(file_id: str, file_path: str, db: Session):
    """Extract text from PDF in background"""
    try:
        pdf_file = db.query(PDFFile).filter(PDFFile.id == file_id).first()
        if not pdf_file:
            return
        
        # Extract text
        text = pdf_processor.extract_text(file_path)
        
        # Update database
        pdf_file.processed_text = text
        pdf_file.processed_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        print(f"Failed to extract text for file {file_id}: {str(e)}")
    finally:
        # Clean up temp file
        if os.path.exists(file_path):
            os.remove(file_path)