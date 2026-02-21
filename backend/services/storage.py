"""
File storage service for PDF files
"""

import os
import uuid
from typing import Optional, BinaryIO
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

from ..core.config import settings

class StorageService:
    """Handle file storage operations"""
    
    def __init__(self):
        self.storage_type = settings.storage_type
        self.temp_dir = settings.temp_dir
        
        # Initialize S3 client if using S3
        if self.storage_type == "s3":
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.s3_access_key,
                aws_secret_access_key=settings.s3_secret_key,
                endpoint_url=settings.s3_endpoint
            )
            self.s3_bucket = settings.s3_bucket
    
    def save_file(
        self, 
        file: UploadFile, 
        user_id: int,
        prefix: str = "pdfs"
    ) -> dict:
        """Save uploaded file to storage"""
        file_id = str(uuid.uuid4())
        original_filename = file.filename
        file_extension = os.path.splitext(original_filename)[1].lower()
        
        # Generate storage path
        if self.storage_type == "s3":
            storage_path = f"{prefix}/{user_id}/{file_id}{file_extension}"
            file_url = self._save_to_s3(file, storage_path)
        else:
            # Local storage
            user_dir = os.path.join(self.temp_dir, str(user_id))
            os.makedirs(user_dir, exist_ok=True)
            
            storage_path = os.path.join(user_dir, f"{file_id}{file_extension}")
            file_url = self._save_to_local(file, storage_path)
        
        return {
            "file_id": file_id,
            "original_filename": original_filename,
            "storage_path": storage_path,
            "file_url": file_url,
            "storage_type": self.storage_type,
            "size": self._get_file_size(file)
        }
    
    def get_file(self, storage_path: str) -> Optional[BinaryIO]:
        """Retrieve file from storage"""
        try:
            if self.storage_type == "s3":
                return self._get_from_s3(storage_path)
            else:
                return self._get_from_local(storage_path)
        except Exception:
            return None
    
    def delete_file(self, storage_path: str) -> bool:
        """Delete file from storage"""
        try:
            if self.storage_type == "s3":
                return self._delete_from_s3(storage_path)
            else:
                return self._delete_from_local(storage_path)
        except Exception:
            return False
    
    def get_file_url(self, storage_path: str, expires_in: int = 3600) -> Optional[str]:
        """Get temporary URL for file access"""
        if self.storage_type == "s3":
            return self._get_s3_presigned_url(storage_path, expires_in)
        else:
            # For local storage, return file path
            return f"file://{storage_path}"
    
    def cleanup_old_files(self, older_than_hours: int = 24) -> int:
        """Clean up files older than specified hours"""
        deleted_count = 0
        
        if self.storage_type == "local":
            cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
            
            for root, dirs, files in os.walk(self.temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_time < cutoff_time:
                        try:
                            os.remove(file_path)
                            deleted_count += 1
                        except Exception:
                            pass
        
        return deleted_count
    
    # Private methods
    def _save_to_s3(self, file: UploadFile, storage_path: str) -> str:
        """Save file to S3"""
        file.file.seek(0)
        self.s3_client.upload_fileobj(
            file.file,
            self.s3_bucket,
            storage_path,
            ExtraArgs={
                'ContentType': file.content_type,
                'Metadata': {
                    'original-filename': file.filename
                }
            }
        )
        
        return f"https://{self.s3_bucket}.s3.amazonaws.com/{storage_path}"
    
    def _save_to_local(self, file: UploadFile, storage_path: str) -> str:
        """Save file to local storage"""
        with open(storage_path, "wb") as f:
            content = file.file.read()
            f.write(content)
        
        return storage_path
    
    def _get_from_s3(self, storage_path: str) -> BinaryIO:
        """Get file from S3"""
        import io
        buffer = io.BytesIO()
        
        self.s3_client.download_fileobj(
            self.s3_bucket,
            storage_path,
            buffer
        )
        
        buffer.seek(0)
        return buffer
    
    def _get_from_local(self, storage_path: str) -> BinaryIO:
        """Get file from local storage"""
        import io
        with open(storage_path, "rb") as f:
            content = f.read()
        
        buffer = io.BytesIO(content)
        buffer.seek(0)
        return buffer
    
    def _delete_from_s3(self, storage_path: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.s3_bucket,
                Key=storage_path
            )
            return True
        except ClientError:
            return False
    
    def _delete_from_local(self, storage_path: str) -> bool:
        """Delete file from local storage"""
        try:
            if os.path.exists(storage_path):
                os.remove(storage_path)
                return True
            return False
        except Exception:
            return False
    
    def _get_s3_presigned_url(self, storage_path: str, expires_in: int) -> str:
        """Generate presigned URL for S3 object"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.s3_bucket,
                    'Key': storage_path
                },
                ExpiresIn=expires_in
            )
            return url
        except ClientError:
            return ""
    
    def _get_file_size(self, file: UploadFile) -> int:
        """Get file size in bytes"""
        current_position = file.file.tell()
        file.file.seek(0, 2)  # Seek to end
        size = file.file.tell()
        file.file.seek(current_position)  # Reset position
        return size
    
    def get_storage_stats(self) -> dict:
        """Get storage statistics"""
        if self.storage_type == "local":
            total_size = 0
            file_count = 0
            
            for root, dirs, files in os.walk(self.temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
                    file_count += 1
            
            return {
                "storage_type": "local",
                "total_size_bytes": total_size,
                "total_size_mb": total_size / (1024 * 1024),
                "file_count": file_count,
                "directory": self.temp_dir
            }
        else:
            # For S3, would need to implement bucket stats
            return {
                "storage_type": "s3",
                "bucket": self.s3_bucket,
                "note": "S3 statistics not implemented"
            }