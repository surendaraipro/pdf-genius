"""
PDF.co API service for PDF processing
Free tier with 100 credits/month
"""

import os
import json
import base64
from typing import Dict, List, Optional, BinaryIO
import httpx
from datetime import datetime

from ..core.config import settings

class PDFCoService:
    """PDF.co API service for PDF processing"""
    
    def __init__(self):
        self.api_key = os.getenv("PDF_CO_API_KEY", "")
        self.base_url = "https://api.pdf.co/v1"
        
        if not self.api_key:
            print("⚠️  PDF_CO_API_KEY not set. PDF processing will use local fallback.")
    
    async def convert_pdf(
        self,
        pdf_content: bytes,
        output_format: str,
        filename: str = "document.pdf"
    ) -> Dict[str, any]:
        """Convert PDF to another format using PDF.co"""
        if not self.api_key:
            return await self._local_fallback(pdf_content, output_format, filename)
        
        # Supported formats by PDF.co
        supported_formats = {
            "docx": "Docx",
            "doc": "Doc",
            "xlsx": "Xlsx",
            "xls": "Xls",
            "pptx": "Pptx",
            "ppt": "Ppt",
            "html": "Html",
            "txt": "Txt",
            "rtf": "Rtf",
            "jpg": "Jpeg",
            "jpeg": "Jpeg",
            "png": "Png",
            "tiff": "Tiff"
        }
        
        if output_format.lower() not in supported_formats:
            raise ValueError(f"Unsupported format: {output_format}")
        
        # Convert PDF to base64
        pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
        
        payload = {
            "async": False,
            "name": filename,
            "url": f"data:application/pdf;base64,{pdf_base64}",
            "outputType": supported_formats[output_format.lower()],
            "inline": True
        }
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/pdf/convert/to/{output_format.lower()}",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("error", False):
                        raise Exception(f"PDF.co error: {result.get('message')}")
                    
                    # Download converted file
                    if result.get("url"):
                        file_response = await client.get(result["url"])
                        if file_response.status_code == 200:
                            return {
                                "content": file_response.content,
                                "filename": f"{filename.rsplit('.', 1)[0]}.{output_format}",
                                "format": output_format,
                                "size": len(file_response.content),
                                "pages": result.get("pages", 1),
                                "provider": "pdf.co"
                            }
                    
                    raise Exception("No converted file URL returned")
                else:
                    print(f"PDF.co API error: {response.status_code} - {response.text}")
                    return await self._local_fallback(pdf_content, output_format, filename)
                    
        except Exception as e:
            print(f"PDF.co API request failed: {str(e)}")
            return await self._local_fallback(pdf_content, output_format, filename)
    
    async def merge_pdfs(
        self,
        pdf_contents: List[bytes],
        output_filename: str = "merged.pdf"
    ) -> Dict[str, any]:
        """Merge multiple PDFs using PDF.co"""
        if not self.api_key:
            return await self._local_merge_fallback(pdf_contents, output_filename)
        
        # Upload files and get URLs
        file_urls = []
        for i, content in enumerate(pdf_contents):
            upload_result = await self._upload_file(content, f"file_{i}.pdf")
            if upload_result.get("url"):
                file_urls.append(upload_result["url"])
        
        if len(file_urls) < 2:
            raise ValueError("At least 2 PDFs required for merging")
        
        payload = {
            "async": False,
            "name": output_filename,
            "url": file_urls,
            "inline": True
        }
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/pdf/merge",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("error", False):
                        raise Exception(f"PDF.co error: {result.get('message')}")
                    
                    # Download merged file
                    if result.get("url"):
                        file_response = await client.get(result["url"])
                        if file_response.status_code == 200:
                            return {
                                "content": file_response.content,
                                "filename": output_filename,
                                "size": len(file_response.content),
                                "pages": result.get("pages", len(pdf_contents)),
                                "provider": "pdf.co"
                            }
                    
                    raise Exception("No merged file URL returned")
                else:
                    print(f"PDF.co merge error: {response.status_code} - {response.text}")
                    return await self._local_merge_fallback(pdf_contents, output_filename)
                    
        except Exception as e:
            print(f"PDF.co merge failed: {str(e)}")
            return await self._local_merge_fallback(pdf_contents, output_filename)
    
    async def compress_pdf(
        self,
        pdf_content: bytes,
        quality: str = "medium",
        filename: str = "document.pdf"
    ) -> Dict[str, any]:
        """Compress PDF using PDF.co"""
        if not self.api_key:
            return await self._local_compress_fallback(pdf_content, quality, filename)
        
        # Quality mapping
        quality_map = {
            "high": "Maximum",    # Smallest size
            "medium": "Recommended",  # Balanced
            "low": "Minimum"      # Less compression
        }
        
        compression_level = quality_map.get(quality.lower(), "Recommended")
        
        # Convert PDF to base64
        pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
        
        payload = {
            "async": False,
            "name": filename,
            "url": f"data:application/pdf;base64,{pdf_base64}",
            "compressionLevel": compression_level,
            "inline": True
        }
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/pdf/optimize",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("error", False):
                        raise Exception(f"PDF.co error: {result.get('message')}")
                    
                    # Download compressed file
                    if result.get("url"):
                        file_response = await client.get(result["url"])
                        if file_response.status_code == 200:
                            original_size = len(pdf_content)
                            compressed_size = len(file_response.content)
                            savings = ((original_size - compressed_size) / original_size) * 100
                            
                            return {
                                "content": file_response.content,
                                "filename": f"compressed_{filename}",
                                "original_size": original_size,
                                "compressed_size": compressed_size,
                                "savings_percentage": round(savings, 2),
                                "quality": quality,
                                "provider": "pdf.co"
                            }
                    
                    raise Exception("No compressed file URL returned")
                else:
                    print(f"PDF.co compress error: {response.status_code} - {response.text}")
                    return await self._local_compress_fallback(pdf_content, quality, filename)
                    
        except Exception as e:
            print(f"PDF.co compress failed: {str(e)}")
            return await self._local_compress_fallback(pdf_content, quality, filename)
    
    async def extract_text(
        self,
        pdf_content: bytes,
        filename: str = "document.pdf"
    ) -> Dict[str, any]:
        """Extract text from PDF using PDF.co"""
        if not self.api_key:
            return await self._local_extract_fallback(pdf_content, filename)
        
        # Convert PDF to base64
        pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
        
        payload = {
            "async": False,
            "name": filename,
            "url": f"data:application/pdf;base64,{pdf_base64}",
            "inline": True,
            "outputFormat": "Txt"
        }
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/pdf/convert/to/text",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("error", False):
                        raise Exception(f"PDF.co error: {result.get('message')}")
                    
                    # Get text content
                    if result.get("url"):
                        text_response = await client.get(result["url"])
                        if text_response.status_code == 200:
                            text = text_response.text
                            
                            return {
                                "text": text,
                                "filename": filename,
                                "pages": result.get("pages", 1),
                                "character_count": len(text),
                                "word_count": len(text.split()),
                                "provider": "pdf.co"
                            }
                    
                    raise Exception("No text URL returned")
                else:
                    print(f"PDF.co extract error: {response.status_code} - {response.text}")
                    return await self._local_extract_fallback(pdf_content, filename)
                    
        except Exception as e:
            print(f"PDF.co extract failed: {str(e)}")
            return await self._local_extract_fallback(pdf_content, filename)
    
    # Helper methods
    async def _upload_file(self, content: bytes, filename: str) -> Dict[str, any]:
        """Upload file to PDF.co and get URL"""
        pdf_base64 = base64.b64encode(content).decode('utf-8')
        
        payload = {
            "name": filename,
            "url": f"data:application/pdf;base64,{pdf_base64}"
        }
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/file/upload",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Upload failed: {response.status_code}")
    
    async def _local_fallback(
        self,
        pdf_content: bytes,
        output_format: str,
        filename: str
    ) -> Dict[str, any]:
        """Local fallback for PDF conversion"""
        from .pdf_processor import PDFProcessor
        
        processor = PDFProcessor()
        
        # Save to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(pdf_content)
            temp_pdf = f.name
        
        try:
            output_path = processor.convert(temp_pdf, output_format)
            
            with open(output_path, "rb") as f:
                content = f.read()
            
            return {
                "content": content,
                "filename": f"{filename.rsplit('.', 1)[0]}.{output_format}",
                "format": output_format,
                "size": len(content),
                "pages": 1,
                "provider": "local"
            }
        finally:
            import os
            if os.path.exists(temp_pdf):
                os.remove(temp_pdf)
            if 'output_path' in locals() and os.path.exists(output_path):
                os.remove(output_path)
    
    async def _local_merge_fallback(
        self,
        pdf_contents: List[bytes],
        output_filename: str
    ) -> Dict[str, any]:
        """Local fallback for PDF merging"""
        from .pdf_processor import PDFProcessor
        
        processor = PDFProcessor()
        
        # Save to temp files
        import tempfile
        import os
        temp_paths = []
        
        try:
            for i, content in enumerate(pdf_contents):
                temp_path = f"/tmp/merge_{i}_{datetime.now().timestamp()}.pdf"
                with open(temp_path, "wb") as f:
                    f.write(content)
                temp_paths.append(temp_path)
            
            merged_path = processor.merge(temp_paths)
            
            with open(merged_path, "rb") as f:
                content = f.read()
            
            return {
                "content": content,
                "filename": output_filename,
                "size": len(content),
                "pages": len(pdf_contents),
                "provider": "local"
            }
        finally:
            for path in temp_paths:
                if os.path.exists(path):
                    os.remove(path)
            if 'merged_path' in locals() and os.path.exists(merged_path):
                os.remove(merged_path)
    
    async def _local_compress_fallback(
        self,
        pdf_content: bytes,
        quality: str,
        filename: str
    ) -> Dict[str, any]:
        """Local fallback for PDF compression"""
        from .pdf_processor import PDFProcessor
        
        processor = PDFProcessor()
        
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(pdf_content)
            temp_pdf = f.name
        
        try:
            compressed_path = processor.compress(temp_pdf, quality)
            
            with open(compressed_path, "rb") as f:
                content = f.read()
            
            original_size = len(pdf_content)
            compressed_size = len(content)
            savings = ((original_size - compressed_size) / original_size) * 100
            
            return {
                "content": content,
                "filename": f"compressed_{filename}",
                "original_size": original_size,
                "compressed_size": compressed_size,
                "savings_percentage": round(savings, 2),
                "quality": quality,
                "provider": "local"
            }
        finally:
            if os.path.exists(temp_pdf):
                os.remove(temp_pdf)
            if 'compressed_path' in locals() and os.path.exists(compressed_path):
                os.remove(compressed_path)
    
    async def _local_extract_fallback(
        self,
        pdf_content: bytes,
        filename: str
    ) -> Dict[str, any]:
        """Local fallback for text extraction"""
        from .pdf_processor import PDFProcessor
        
        processor = PDFProcessor()
        
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(pdf_content)
            temp_pdf = f.name
        
        try:
            text = processor.extract_text(temp_pdf)
            
            return {
                "text": text,
                "filename": filename,
                "pages": 1,
                "character_count": len(text),
                "word_count": len(text.split()),
                "provider": "local"
            }
        finally:
            if os.path.exists(temp_pdf):
                os.remove(temp_pdf)
    
    def get_usage_info(self) -> Dict[str, any]:
        """Get PDF.co usage information"""
        # PDF.co free tier: 100 credits/month
        # Each operation uses 1 credit
        return {
            "provider": "PDF.co",
            "free_tier": True,
            "monthly_credits": 100,
            "credits_used": 0,  # Would need to track
            "credits_remaining": 100,
            "operations_per_credit": 1,
            "reset_date": datetime.now().replace(day=1).isoformat()  # Monthly reset
        }