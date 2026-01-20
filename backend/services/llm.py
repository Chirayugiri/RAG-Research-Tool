"""
LLM service using Groq for answer generation.
"""

import requests
from typing import List, Dict, Any


class LLMService:
    """Service for generating answers using Groq LLM."""
    
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize LLM service.
        
        Args:
            api_key: Groq API key
            model: Model name (default: llama-3.3-70b-versatile)
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
    
    def generate_answer(self, question: str, context_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate answer to question using context documents.
        
        Args:
            question: User's question
            context_docs: List of relevant document chunks
            
        Returns:
            Dictionary with answer and sources
        """
        if not context_docs:
            return {
                "success": False,
                "answer": "No relevant documents found. Please process some news articles first.",
                "sources": []
            }
        
        # Prepare context
        context = "\n\n".join([
            f"Source {i+1}: {doc['text']}"
            for i, doc in enumerate(context_docs)
        ])
        
        # Prepare prompt
        prompt = f"""You are a helpful AI assistant that answers questions based on provided news articles.

Context from news articles:
{context}

Question: {question}

Instructions:
1. Answer the question using ONLY the information from the context above
2. Be concise and accurate
3. If the context doesn't contain enough information, say so
4. Do NOT include source citations in your answer - they will be displayed separately

Answer:"""
        
        try:
            # Call Groq API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            answer = result['choices'][0]['message']['content'].strip()
            
            # Remove any source references from the answer
            # Remove patterns like "(Source 1, Source 2, ...)" or "Source 1 and Source 2"
            import re
            answer = re.sub(r'\(Source\s+\d+(?:,?\s+(?:and\s+)?Source\s+\d+)*\)', '', answer)
            answer = re.sub(r'Source\s+\d+(?:\s+and\s+Source\s+\d+)*\.?', '', answer)
            
            # Remove sentences that mention using sources
            lines = answer.split('\n')
            filtered_lines = []
            for line in lines:
                if not re.search(r'(I used|using|from|contain) Source', line, re.IGNORECASE):
                    filtered_lines.append(line)
            answer = '\n'.join(filtered_lines).strip()
            
            # Extract unique sources
            sources = []
            seen_sources = set()
            for doc in context_docs:
                source_url = doc.get('source', '')
                if source_url and source_url not in seen_sources:
                    sources.append({
                        'url': source_url,
                        'text': doc.get('text', '')[:200] + '...'
                    })
                    seen_sources.add(source_url)
            
            return {
                "success": True,
                "answer": answer,
                "sources": sources
            }
        except Exception as e:
            return {
                "success": False,
                "answer": f"Error generating answer: {str(e)}",
                "sources": []
            }
