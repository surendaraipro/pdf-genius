"""
AI Chat service for interacting with PDFs
"""

import os
from typing import Dict, List, Optional
import json
from datetime import datetime

from ..core.config import settings

class AIChatService:
    """Handle AI interactions with PDF content"""
    
    def __init__(self):
        self.use_local_llm = settings.use_local_llm
        self.local_model_name = settings.local_llm_model
        self.openai_api_key = settings.openai_api_key
        
        # Initialize appropriate AI backend
        if self.use_local_llm:
            self.ai_backend = self._init_local_llm()
        else:
            self.ai_backend = self._init_openai()
    
    async def ask_about_pdf(self, pdf_path: str, question: str) -> Dict:
        """Ask a question about PDF content"""
        try:
            # Extract text from PDF
            from .pdf_processor import PDFProcessor
            processor = PDFProcessor()
            text = processor.extract_text(pdf_path)
            
            # Limit context size (for performance)
            max_context = 8000  # characters
            if len(text) > max_context:
                text = text[:max_context] + "... [truncated]"
            
            # Prepare prompt
            prompt = self._create_question_prompt(text, question)
            
            # Get AI response
            response = await self._get_ai_response(prompt)
            
            # Extract sources/citations
            sources = self._extract_sources(text, response, question)
            
            return {
                "answer": response,
                "sources": sources,
                "confidence": 0.95,  # Placeholder
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"Failed to process AI question: {str(e)}")
    
    async def summarize_pdf(self, pdf_path: str, length: str = "medium") -> Dict:
        """Summarize PDF content"""
        try:
            from .pdf_processor import PDFProcessor
            processor = PDFProcessor()
            text = processor.extract_text(pdf_path)
            
            # Limit context
            max_context = 12000
            if len(text) > max_context:
                text = text[:max_context] + "... [truncated]"
            
            # Prepare summarization prompt
            prompt = self._create_summary_prompt(text, length)
            
            # Get AI summary
            summary = await self._get_ai_response(prompt)
            
            # Extract key points
            key_points = self._extract_key_points(summary)
            
            return {
                "text": summary,
                "length": length,
                "key_points": key_points,
                "word_count": len(summary.split()),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"Failed to summarize PDF: {str(e)}")
    
    async def extract_data(self, pdf_path: str, data_type: str) -> Dict:
        """Extract specific data from PDF"""
        data_types = {
            "dates": "Extract all dates mentioned in the document",
            "names": "Extract all person names mentioned",
            "emails": "Extract all email addresses",
            "phone_numbers": "Extract all phone numbers",
            "amounts": "Extract all monetary amounts",
            "addresses": "Extract all addresses",
            "urls": "Extract all website URLs",
        }
        
        if data_type not in data_types:
            raise ValueError(f"Unsupported data type: {data_type}")
        
        try:
            from .pdf_processor import PDFProcessor
            processor = PDFProcessor()
            text = processor.extract_text(pdf_path)
            
            prompt = f"""
            {data_types[data_type]}.
            
            Document text:
            {text[:6000]}
            
            Return ONLY a JSON array of the extracted items. No explanations.
            Example: ["item1", "item2", "item3"]
            """
            
            response = await self._get_ai_response(prompt)
            
            # Parse JSON response
            try:
                items = json.loads(response)
            except:
                # Fallback: extract items from text response
                items = self._parse_extracted_items(response)
            
            return {
                "data_type": data_type,
                "items": items,
                "count": len(items),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"Failed to extract {data_type}: {str(e)}")
    
    async def find_contradictions(self, pdf_path: str) -> Dict:
        """Find contradictions or inconsistencies in PDF"""
        try:
            from .pdf_processor import PDFProcessor
            processor = PDFProcessor()
            text = processor.extract_text(pdf_path)
            
            prompt = f"""
            Analyze this document for contradictions, inconsistencies, or conflicting information.
            
            Document text:
            {text[:8000]}
            
            Return a JSON object with:
            1. "contradictions": array of contradictions found
            2. "confidence": how confident you are (0-1)
            3. "summary": brief summary of findings
            
            Format:
            {{
                "contradictions": [
                    {{
                        "issue": "description of contradiction",
                        "location": "where it appears",
                        "severity": "high/medium/low"
                    }}
                ],
                "confidence": 0.85,
                "summary": "Brief summary"
            }}
            """
            
            response = await self._get_ai_response(prompt)
            
            try:
                result = json.loads(response)
            except:
                result = {
                    "contradictions": [],
                    "confidence": 0.0,
                    "summary": "Could not parse analysis"
                }
            
            return result
        except Exception as e:
            raise Exception(f"Failed to analyze contradictions: {str(e)}")
    
    async def translate_pdf(self, pdf_path: str, target_language: str) -> Dict:
        """Translate PDF content to another language"""
        try:
            from .pdf_processor import PDFProcessor
            processor = PDFProcessor()
            text = processor.extract_text(pdf_path)
            
            # Take first 4000 chars for translation (for performance)
            sample_text = text[:4000]
            if len(text) > 4000:
                sample_text += "... [document continues]"
            
            prompt = f"""
            Translate the following text to {target_language}.
            Maintain the original formatting and meaning.
            
            Text to translate:
            {sample_text}
            
            Return ONLY the translation. No explanations.
            """
            
            translation = await self._get_ai_response(prompt)
            
            return {
                "original_language": "auto-detected",
                "target_language": target_language,
                "translation": translation,
                "is_complete": len(text) <= 4000,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"Failed to translate PDF: {str(e)}")
    
    # Private methods
    def _init_local_llm(self):
        """Initialize local LLM (simplified for MVP)"""
        # Note: In production, load actual model
        print(f"Initializing local LLM: {self.local_model_name}")
        
        class MockLocalLLM:
            async def generate(self, prompt: str) -> str:
                # Mock response for MVP
                return f"Mock response to: {prompt[:50]}..."
        
        return MockLocalLLM()
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key required when use_local_llm is False")
        
        try:
            from openai import AsyncOpenAI
            return AsyncOpenAI(api_key=self.openai_api_key)
        except ImportError:
            raise ImportError("OpenAI package not installed")
    
    async def _get_ai_response(self, prompt: str) -> str:
        """Get response from AI backend"""
        if self.use_local_llm:
            # Local LLM
            return await self.ai_backend.generate(prompt)
        else:
            # OpenAI
            try:
                response = await self.ai_backend.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that analyzes PDF documents."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.3
                )
                return response.choices[0].message.content
            except Exception as e:
                raise Exception(f"OpenAI API error: {str(e)}")
    
    def _create_question_prompt(self, text: str, question: str) -> str:
        """Create prompt for Q&A about PDF"""
        return f"""
        Based on the following document text, answer the question.
        
        DOCUMENT TEXT:
        {text}
        
        QUESTION:
        {question}
        
        INSTRUCTIONS:
        1. Answer based ONLY on the document text above
        2. If the answer isn't in the document, say "The document doesn't contain this information"
        3. Be concise but complete
        4. Cite relevant parts of the document if possible
        
        ANSWER:
        """
    
    def _create_summary_prompt(self, text: str, length: str) -> str:
        """Create prompt for summarization"""
        length_instructions = {
            "short": "Create a 2-3 sentence summary",
            "medium": "Create a paragraph summary (5-7 sentences)",
            "long": "Create a detailed summary with key points",
            "bullet": "Create bullet point summary"
        }
        
        instruction = length_instructions.get(length, length_instructions["medium"])
        
        return f"""
        {instruction} of the following document:
        
        {text}
        
        Focus on:
        1. Main topic/purpose
        2. Key findings/conclusions
        3. Important recommendations
        4. Critical data points
        
        SUMMARY:
        """
    
    def _extract_sources(self, text: str, answer: str, question: str) -> List[Dict]:
        """Extract source citations from text (simplified)"""
        # This is a simplified version
        # In production, use more sophisticated citation extraction
        sources = []
        
        # Look for sentences in answer that might match text
        answer_sentences = answer.split('. ')
        for sentence in answer_sentences[:3]:  # Check first 3 sentences
            if len(sentence) > 20:  # Reasonable length
                # Find similar text in original
                # Simplified: just return placeholder
                sources.append({
                    "text": sentence[:100] + "...",
                    "page": 1,  # Placeholder
                    "confidence": 0.7
                })
        
        return sources[:3]  # Return top 3
    
    def _extract_key_points(self, summary: str) -> List[str]:
        """Extract key points from summary"""
        # Simple extraction: split by sentences and take important ones
        sentences = summary.split('. ')
        key_points = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 20:  # Reasonable length
                # Check for importance indicators
                important_words = ['key', 'important', 'critical', 'main', 'primary', 'essential']
                if any(word in sentence.lower() for word in important_words):
                    key_points.append(sentence)
                elif len(key_points) < 5:  # Limit to 5 key points
                    key_points.append(sentence)
        
        return key_points[:5]
    
    def _parse_extracted_items(self, response: str) -> List[str]:
        """Parse extracted items from text response"""
        # Try to extract items from various formats
        items = []
        
        # Look for list items
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            # Remove bullets, numbers, etc.
            if line.startswith('- '):
                items.append(line[2:])
            elif line.startswith('* '):
                items.append(line[2:])
            elif line and not line.startswith('[') and not line.startswith('{'):
                # Check if it looks like an item
                if 2 < len(line) < 100:  # Reasonable length
                    items.append(line)
        
        return items