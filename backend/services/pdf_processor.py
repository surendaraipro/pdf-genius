"""
PDF processing service using PyMuPDF and other libraries
"""

import os
import fitz  # PyMuPDF
from pdf2image import convert_from_path
from PIL import Image
import tempfile
from typing import Dict, List, Optional, Tuple
import subprocess
import json

from ..core.config import settings

class PDFProcessor:
    """Handle all PDF processing operations"""
    
    def __init__(self):
        self.temp_dir = settings.temp_dir
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def get_metadata(self, pdf_path: str) -> Dict:
        """Extract metadata from PDF"""
        try:
            doc = fitz.open(pdf_path)
            metadata = {
                "pages": len(doc),
                "size": os.path.getsize(pdf_path),
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "keywords": doc.metadata.get("keywords", ""),
                "creator": doc.metadata.get("creator", ""),
                "producer": doc.metadata.get("producer", ""),
                "creation_date": doc.metadata.get("creationDate", ""),
                "modification_date": doc.metadata.get("modDate", ""),
                "is_encrypted": doc.is_encrypted,
                "is_scanned": self._is_scanned_pdf(doc)
            }
            doc.close()
            return metadata
        except Exception as e:
            raise Exception(f"Failed to extract metadata: {str(e)}")
    
    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            raise Exception(f"Failed to extract text: {str(e)}")
    
    def convert(self, input_path: str, output_format: str) -> str:
        """Convert PDF to another format"""
        formats = {
            "docx": self._convert_to_docx,
            "excel": self._convert_to_excel,
            "ppt": self._convert_to_ppt,
            "html": self._convert_to_html,
            "jpg": self._convert_to_images,
            "png": self._convert_to_images,
            "txt": self._convert_to_text,
        }
        
        if output_format not in formats:
            raise ValueError(f"Unsupported format: {output_format}")
        
        converter = formats[output_format]
        return converter(input_path)
    
    def merge(self, pdf_paths: List[str]) -> str:
        """Merge multiple PDFs into one"""
        try:
            output_path = os.path.join(self.temp_dir, f"merged_{os.urandom(4).hex()}.pdf")
            
            result = fitz.open()
            for pdf_path in pdf_paths:
                doc = fitz.open(pdf_path)
                result.insert_pdf(doc)
                doc.close()
            
            result.save(output_path)
            result.close()
            return output_path
        except Exception as e:
            raise Exception(f"Failed to merge PDFs: {str(e)}")
    
    def split(self, pdf_path: str, pages: List[int]) -> List[str]:
        """Split PDF by pages"""
        try:
            doc = fitz.open(pdf_path)
            output_files = []
            
            for page_num in pages:
                if 1 <= page_num <= len(doc):
                    output_path = os.path.join(
                        self.temp_dir, 
                        f"page_{page_num}_{os.urandom(4).hex()}.pdf"
                    )
                    
                    new_doc = fitz.open()
                    new_doc.insert_pdf(doc, from_page=page_num-1, to_page=page_num-1)
                    new_doc.save(output_path)
                    new_doc.close()
                    
                    output_files.append(output_path)
            
            doc.close()
            return output_files
        except Exception as e:
            raise Exception(f"Failed to split PDF: {str(e)}")
    
    def compress(self, pdf_path: str, quality: str = "medium") -> str:
        """Compress PDF file size"""
        try:
            output_path = os.path.join(self.temp_dir, f"compressed_{os.urandom(4).hex()}.pdf")
            
            # Simple compression by re-saving with optimization
            doc = fitz.open(pdf_path)
            
            # Apply compression based on quality
            if quality == "high":
                # Aggressive compression
                doc.save(
                    output_path, 
                    garbage=4,  # Remove unused objects
                    deflate=True,  # Compress streams
                    clean=True  # Clean content streams
                )
            elif quality == "medium":
                # Balanced compression
                doc.save(
                    output_path,
                    garbage=3,
                    deflate=True
                )
            else:
                # Light compression
                doc.save(output_path, garbage=2)
            
            doc.close()
            return output_path
        except Exception as e:
            raise Exception(f"Failed to compress PDF: {str(e)}")
    
    def add_watermark(self, pdf_path: str, watermark_text: str) -> str:
        """Add text watermark to PDF"""
        try:
            output_path = os.path.join(self.temp_dir, f"watermarked_{os.urandom(4).hex()}.pdf")
            
            doc = fitz.open(pdf_path)
            
            for page in doc:
                # Add watermark text
                rect = page.rect
                font_size = 60
                opacity = 0.3
                
                # Create watermark text
                page.insert_text(
                    rect.tl + (50, 50),  # Position
                    watermark_text,
                    fontsize=font_size,
                    color=(0.5, 0.5, 0.5),  # Gray color
                    rotate=45,  # Diagonal
                    opacity=opacity
                )
            
            doc.save(output_path)
            doc.close()
            return output_path
        except Exception as e:
            raise Exception(f"Failed to add watermark: {str(e)}")
    
    def extract_images(self, pdf_path: str) -> List[str]:
        """Extract images from PDF"""
        try:
            doc = fitz.open(pdf_path)
            image_paths = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    image_path = os.path.join(
                        self.temp_dir,
                        f"page_{page_num+1}_img_{img_index}_{os.urandom(4).hex()}.{image_ext}"
                    )
                    
                    with open(image_path, "wb") as f:
                        f.write(image_bytes)
                    
                    image_paths.append(image_path)
            
            doc.close()
            return image_paths
        except Exception as e:
            raise Exception(f"Failed to extract images: {str(e)}")
    
    def extract_tables(self, pdf_path: str) -> List[Dict]:
        """Extract tables from PDF (simplified version)"""
        # Note: For production, consider using camelot or tabula-py
        # This is a simplified version using text extraction
        try:
            text = self.extract_text(pdf_path)
            tables = []
            
            # Simple table detection (look for tabular patterns)
            lines = text.split('\n')
            current_table = []
            
            for line in lines:
                # Check if line looks like table row (multiple values separated by spaces/tabs)
                if '\t' in line or line.count('  ') > 2:
                    cells = [cell.strip() for cell in line.split('\t') if cell.strip()]
                    if len(cells) > 1:
                        current_table.append(cells)
                elif current_table:
                    # End of table
                    if len(current_table) > 1:  # At least header + one row
                        tables.append({
                            "rows": current_table,
                            "row_count": len(current_table),
                            "col_count": len(current_table[0]) if current_table else 0
                        })
                    current_table = []
            
            return tables
        except Exception as e:
            raise Exception(f"Failed to extract tables: {str(e)}")
    
    # Private helper methods
    def _is_scanned_pdf(self, doc: fitz.Document) -> bool:
        """Check if PDF is scanned (image-based)"""
        try:
            # Simple heuristic: if first page has very little text, it's likely scanned
            first_page = doc[0]
            text = first_page.get_text()
            return len(text.strip()) < 100  # Arbitrary threshold
        except:
            return False
    
    def _convert_to_docx(self, pdf_path: str) -> str:
        """Convert PDF to DOCX"""
        # Note: This is a placeholder. In production, use a proper library
        # like pdf2docx or commercial solution
        output_path = os.path.join(self.temp_dir, f"converted_{os.urandom(4).hex()}.docx")
        
        # For MVP, create a simple DOCX with extracted text
        text = self.extract_text(pdf_path)
        
        # Create minimal DOCX (this is simplified)
        # In production, use python-docx library
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return output_path
    
    def _convert_to_excel(self, pdf_path: str) -> str:
        """Convert PDF to Excel"""
        output_path = os.path.join(self.temp_dir, f"converted_{os.urandom(4).hex()}.xlsx")
        
        # Extract tables and create CSV (simplified)
        tables = self.extract_tables(pdf_path)
        
        if tables:
            # Use first table
            import csv
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for row in tables[0]["rows"]:
                    writer.writerow(row)
        
        return output_path
    
    def _convert_to_ppt(self, pdf_path: str) -> str:
        """Convert PDF to PowerPoint"""
        output_path = os.path.join(self.temp_dir, f"converted_{os.urandom(4).hex()}.pptx")
        
        # Simplified: Convert each page to image for PPT
        images = convert_from_path(pdf_path)
        
        # In production, use python-pptx to create actual PPT
        # For MVP, just save first image
        if images:
            images[0].save(output_path.replace('.pptx', '.jpg'))
        
        return output_path
    
    def _convert_to_html(self, pdf_path: str) -> str:
        """Convert PDF to HTML"""
        output_path = os.path.join(self.temp_dir, f"converted_{os.urandom(4).hex()}.html")
        
        text = self.extract_text(pdf_path)
        
        # Create simple HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Converted PDF</title>
        </head>
        <body>
            <pre>{text}</pre>
        </body>
        </html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_path
    
    def _convert_to_images(self, pdf_path: str) -> str:
        """Convert PDF to images (JPG/PNG)"""
        try:
            images = convert_from_path(pdf_path)
            if not images:
                raise Exception("No images generated")
            
            # Save first page for MVP
            output_path = os.path.join(
                self.temp_dir, 
                f"page_1_{os.urandom(4).hex()}.jpg"
            )
            images[0].save(output_path, 'JPEG')
            
            return output_path
        except Exception as e:
            raise Exception(f"Failed to convert to images: {str(e)}")
    
    def _convert_to_text(self, pdf_path: str) -> str:
        """Convert PDF to plain text"""
        output_path = os.path.join(self.temp_dir, f"converted_{os.urandom(4).hex()}.txt")
        
        text = self.extract_text(pdf_path)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return output_path