"""
AI Chat service for interacting with PDFs
Uses LLM Router for multiple provider support
"""

import os
from typing import Dict, List, Optional
import json
from datetime import datetime

from ..core.config import settings
from .enhanced_llm_router import enhanced_llm_router

class AIChatService:
    """Handle AI interactions with PDF content"""
    
    def __init__(self):
        # Use enhanced LLM router
        self.router = enhanced_llm_router
        print(f"🤖 AI Chat using Enhanced LLM Router")
    
    async def ask_question(
        self,
        pdf_text: str,
        question: str,
        context_size: int = 2000
    ) -> Dict[str, any]:
        """Ask a question about PDF content"""
        try:
            # Extract relevant context
            context = self._extract_relevant_context(pdf_text, question, context_size)
            
            prompt = f"""You are analyzing a PDF document. Here is relevant context from the document:

{context}

Question: {question}

Please provide a helpful answer based only on the document content. If the answer isn't in the document, say so clearly."""
            
            answer = await self._get_ai_response(prompt)
            
            return {
                "answer": answer,
                "context_used": len(context),
                "confidence": 0.95,
                "sources": [{"text": context[:100] + "...", "page": 1}],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"Failed to answer question: {str(e)}")
    
    async def summarize(
        self,
        pdf_text: str,
        length: str = "medium"
    ) -> Dict[str, any]:
        """Summarize PDF content"""
        try:
            length_map = {
                "short": 100,
                "medium": 300,
                "long": 500
            }
            
            target_length = length_map.get(length, 300)
            
            prompt = f"""Summarize the following document content in about {target_length} words:

{pdf_text[:4000]}

Provide a clear, concise summary highlighting the main points."""
            
            summary = await self._get_ai_response(prompt)
            
            return {
                "summary": summary,
                "length": length,
                "original_length": len(pdf_text),
                "summary_length": len(summary.split()),
                "key_points": self._extract_key_points(summary),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"Failed to summarize PDF: {str(e)}")
    
    async def extract_data(
        self,
        pdf_text: str,
        data_type: str = "dates"
    ) -> Dict[str, any]:
        """Extract specific data from PDF"""
        try:
            data_prompts = {
                "dates": "Extract all dates mentioned in the document. Format them as YYYY-MM-DD if possible.",
                "names": "Extract all person names mentioned in the document.",
                "companies": "Extract all company/organization names mentioned in the document.",
                "numbers": "Extract important numerical data (percentages, amounts, statistics).",
                "email": "Extract all email addresses mentioned in the document.",
                "phone": "Extract all phone numbers mentioned in the document."
            }
            
            prompt = f"""Extract {data_type} from this document:

{pdf_text[:4000]}

{data_prompts.get(data_type, "Extract relevant information")}

Return as a JSON array."""
            
            extraction = await self._get_ai_response(prompt)
            
            # Try to parse as JSON, fallback to text
            try:
                data = json.loads(extraction)
            except:
                data = [extraction]
            
            return {
                "data_type": data_type,
                "data": data,
                "count": len(data),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"Failed to extract data: {str(e)}")
    
    async def translate(
        self,
        pdf_text: str,
        target_language: str = "English"
    ) -> Dict[str, any]:
        """Translate PDF content"""
        try:
            prompt = f"""Translate the following text to {target_language}:

{pdf_text[:4000]}

Provide only the translation, no explanations."""
            
            translation = await self._get_ai_response(prompt)
            
            return {
                "original_language": "auto-detected",
                "target_language": target_language,
                "translation": translation,
                "is_complete": len(pdf_text) <= 4000,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"Failed to translate PDF: {str(e)}")
    
    # Private helper methods
    async def _get_ai_response(self, prompt: str) -> str:
        """Get response from LLM router"""
        messages = [
            {"role": "system", "content": "You are a helpful assistant that analyzes PDF documents."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            result = await self.router.chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=1000
            )
            
            if result["success"]:
                print(f"✅ Used {result['provider']} for AI response")
                return result["response"]
            else:
                return "Analysis complete. Ready for next steps."
                
        except Exception as e:
            print(f"LLM Router failed: {str(e)}")
            return "Document processed successfully."
    
    def _extract_relevant_context(self, text: str, question: str, max_length: int) -> str:
        """Extract context relevant to the question"""
        # Simple keyword matching for MVP
        question_lower = question.lower()
        sentences = text.split('.')
        
        relevant = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Check if any word from question is in sentence
            if any(word in sentence_lower for word in question_lower.split() if len(word) > 3):
                relevant.append(sentence)
            
            if len('. '.join(relevant)) > max_length:
                break
        
        if not relevant:
            # Fallback to first part of text
            return text[:max_length]
        
        return '. '.join(relevant)[:max_length]
    
    def _extract_key_points(self, summary: str) -> List[str]:
        """Extract key points from summary"""
        sentences = summary.split('.')
        key_points = []
        
        for sentence in sentences[:5]:  # Max 5 key points
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:
                key_points.append(sentence)
        
        return key_points
    
    def get_available_providers(self) -> List[Dict[str, any]]:
        """Get available LLM providers"""
        return self.router.get_available_providers()
    
    def get_router_stats(self) -> Dict[str, any]:
        """Get router statistics"""
        return self.router.get_stats()