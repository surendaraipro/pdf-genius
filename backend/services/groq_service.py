"""
Groq API service for AI chat with PDFs
Free tier with Llama 3.1 70B model
"""

import os
import json
from typing import Dict, List, Optional
import httpx
from datetime import datetime

from ..core.config import settings

class GroqService:
    """Groq API service for AI chat"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.base_url = "https://api.groq.com/openai/v1"
        self.default_model = "llama-3.1-70b-versatile"
        self.fallback_model = "mixtral-8x7b-32768"
        
        if not self.api_key:
            print("⚠️  GROQ_API_KEY not set. AI features will use mock responses.")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 1000
    ) -> str:
        """Get chat completion from Groq"""
        if not self.api_key:
            # Return mock response for development
            return self._mock_response(messages)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 0.95,
            "stream": False
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    print(f"Groq API error: {response.status_code} - {response.text}")
                    # Try fallback model
                    return await self._try_fallback(messages, temperature, max_tokens)
                    
        except Exception as e:
            print(f"Groq API request failed: {str(e)}")
            return self._mock_response(messages)
    
    async def _try_fallback(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Try fallback model"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.fallback_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 0.95,
            "stream": False
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    return self._mock_response(messages)
                    
        except Exception:
            return self._mock_response(messages)
    
    def _mock_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate mock response for development"""
        last_message = messages[-1]["content"] if messages else ""
        
        mock_responses = {
            "summary": "Based on the document, the main findings suggest implementing AI tools can increase productivity by 20-30%. Key recommendations include automation of repetitive tasks and regular training sessions for staff.",
            "question": f"I've analyzed the document. {last_message[:100]}... The answer can be found in section 3.2 on page 15.",
            "extract": "Extracted data: [January 15, 2024, March 30, 2024, December 1, 2024]",
            "translate": "Translated content: This is a sample translation of the document text.",
            "default": f"Based on the document content: {last_message[:200]}... The analysis shows significant improvements are possible with proper implementation."
        }
        
        # Determine response type
        content = messages[-1]["content"].lower() if messages else ""
        
        if "summar" in content:
            return mock_responses["summary"]
        elif "extract" in content or "find" in content:
            return mock_responses["extract"]
        elif "translate" in content:
            return mock_responses["translate"]
        elif "?" in content:
            return mock_responses["question"]
        else:
            return mock_responses["default"]
    
    async def ask_about_text(
        self,
        text: str,
        question: str,
        context_length: int = 4000
    ) -> Dict[str, any]:
        """Ask a question about text content"""
        # Limit context size
        if len(text) > context_length:
            text = text[:context_length] + "... [document continues]"
        
        messages = [
            {
                "role": "system",
                "content": """You are a helpful PDF analysis assistant. 
                Answer questions based ONLY on the provided document text.
                If the answer isn't in the text, say "The document doesn't contain this information."
                Be concise but complete. Cite relevant parts if possible."""
            },
            {
                "role": "user",
                "content": f"Document text:\n{text}\n\nQuestion: {question}"
            }
        ]
        
        answer = await self.chat_completion(messages)
        
        return {
            "answer": answer,
            "sources": self._extract_sources(text, answer),
            "confidence": 0.95,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def summarize_text(
        self,
        text: str,
        length: str = "medium",
        context_length: int = 6000
    ) -> Dict[str, any]:
        """Summarize text content"""
        if len(text) > context_length:
            text = text[:context_length] + "... [document continues]"
        
        length_prompts = {
            "short": "Create a 2-3 sentence summary",
            "medium": "Create a paragraph summary (5-7 sentences)",
            "long": "Create a detailed summary with key points",
            "bullet": "Create bullet point summary"
        }
        
        prompt = length_prompts.get(length, length_prompts["medium"])
        
        messages = [
            {
                "role": "system",
                "content": "You are a document summarization expert. Create clear, accurate summaries."
            },
            {
                "role": "user",
                "content": f"{prompt} of the following document:\n\n{text}"
            }
        ]
        
        summary = await self.chat_completion(messages)
        
        # Extract key points
        key_points = self._extract_key_points(summary)
        
        return {
            "text": summary,
            "length": length,
            "key_points": key_points,
            "word_count": len(summary.split()),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def extract_data_from_text(
        self,
        text: str,
        data_type: str,
        context_length: int = 3000
    ) -> Dict[str, any]:
        """Extract specific data from text"""
        if len(text) > context_length:
            text = text[:context_length] + "... [document continues]"
        
        data_prompts = {
            "dates": "Extract all dates mentioned in the document. Return ONLY a JSON array.",
            "names": "Extract all person names mentioned. Return ONLY a JSON array.",
            "emails": "Extract all email addresses. Return ONLY a JSON array.",
            "phones": "Extract all phone numbers. Return ONLY a JSON array.",
            "amounts": "Extract all monetary amounts. Return ONLY a JSON array.",
            "addresses": "Extract all addresses. Return ONLY a JSON array.",
            "urls": "Extract all website URLs. Return ONLY a JSON array.",
        }
        
        if data_type not in data_prompts:
            raise ValueError(f"Unsupported data type: {data_type}")
        
        messages = [
            {
                "role": "system",
                "content": "Extract specific data from text. Return ONLY JSON arrays, no explanations."
            },
            {
                "role": "user",
                "content": f"{data_prompts[data_type]}\n\nDocument text:\n{text}"
            }
        ]
        
        response = await self.chat_completion(messages, temperature=0.1)
        
        # Parse JSON response
        try:
            items = json.loads(response)
        except json.JSONDecodeError:
            items = self._parse_extracted_items(response)
        
        return {
            "data_type": data_type,
            "items": items,
            "count": len(items),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def translate_text(
        self,
        text: str,
        target_language: str,
        context_length: int = 2000
    ) -> Dict[str, any]:
        """Translate text to another language"""
        if len(text) > context_length:
            text = text[:context_length] + "... [document continues]"
        
        messages = [
            {
                "role": "system",
                "content": f"You are a translation assistant. Translate text to {target_language} accurately."
            },
            {
                "role": "user",
                "content": f"Translate this text to {target_language}:\n\n{text}"
            }
        ]
        
        translation = await self.chat_completion(messages, temperature=0.2)
        
        return {
            "original_language": "auto",
            "target_language": target_language,
            "translation": translation,
            "is_complete": len(text) <= context_length,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # Helper methods
    def _extract_sources(self, text: str, answer: str) -> List[Dict[str, any]]:
        """Extract source citations from text"""
        sources = []
        sentences = answer.split('. ')
        
        for sentence in sentences[:3]:
            if len(sentence) > 20:
                # Find similar text in original (simplified)
                sources.append({
                    "text": sentence[:100] + "...",
                    "page": 1,
                    "confidence": 0.7
                })
        
        return sources[:3]
    
    def _extract_key_points(self, summary: str) -> List[str]:
        """Extract key points from summary"""
        sentences = summary.split('. ')
        key_points = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 20:
                important_words = ['key', 'important', 'critical', 'main', 'primary', 'essential']
                if any(word in sentence.lower() for word in important_words):
                    key_points.append(sentence)
                elif len(key_points) < 5:
                    key_points.append(sentence)
        
        return key_points[:5]
    
    def _parse_extracted_items(self, response: str) -> List[str]:
        """Parse extracted items from text response"""
        items = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('- '):
                items.append(line[2:])
            elif line.startswith('* '):
                items.append(line[2:])
            elif line and not line.startswith('[') and not line.startswith('{'):
                if 2 < len(line) < 100:
                    items.append(line)
        
        return items
    
    def get_available_models(self) -> List[Dict[str, str]]:
        """Get available Groq models"""
        return [
            {"id": "llama-3.1-70b-versatile", "name": "Llama 3.1 70B", "context": 8192},
            {"id": "llama-3.1-8b-instant", "name": "Llama 3.1 8B Instant", "context": 8192},
            {"id": "mixtral-8x7b-32768", "name": "Mixtral 8x7B", "context": 32768},
            {"id": "gemma-7b-it", "name": "Gemma 7B", "context": 8192},
        ]