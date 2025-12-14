"""
Groq LLM Client for Interview Assistant Responses

Uses Groq's API with Llama 3 model for generating interview assistance.
Optimized for low latency and concise responses.
"""

import asyncio
import logging
from typing import Optional
from groq import AsyncGroq

logger = logging.getLogger(__name__)


class GroqLLMClient:
    """
    Wrapper for Groq API with Llama 3
    
    Configuration:
    - Model: llama3-70b-8192 (best balance of quality and speed)
    - Temperature: 0.7 (balanced creativity)
    - Max tokens: 150 (keep responses concise)
    - Stream: Enabled (low latency)
    """
    
    def __init__(self, api_key: str, resume_text: str):
        if not api_key:
            raise ValueError("Groq API key is required")
        
        self.api_key = api_key
        self.resume_text = resume_text
        self.client = AsyncGroq(api_key=api_key)
        
        # System prompt template
        self.system_prompt = f"""You are an interview assistant helping a candidate respond effectively during a live interview.

The candidate's resume:
{resume_text}

Your role:
1. Analyze the interview question or discussion point
2. Provide a SHORT, conversational answer (2-3 sentences max)
3. Help the candidate respond naturally and confidently
4. Draw from the resume when relevant
5. Be concise - this is real-time assistance

Guidelines:
- Keep responses brief and to the point
- Use a natural, conversational tone
- Focus on key points from the resume
- Suggest specific examples when helpful
- Don't be overly formal"""
    
    async def get_response(self, question: str) -> str:
        """
        Get LLM response for interview question
        
        Args:
            question: Transcribed interview question or discussion
        
        Returns:
            AI-generated response suggestion
        """
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Create chat completion
            response = await self.client.chat.completions.create(
                model="llama3-70b-8192",  # Fast and high-quality
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"Interview question/discussion: {question}\n\nProvide a brief, helpful response suggestion:"
                    }
                ],
                temperature=0.7,  # Balanced creativity
                max_tokens=150,  # Keep responses short
                top_p=0.9,
                stream=False  # For simplicity, not streaming
            )
            
            # Extract response text
            assistant_message = response.choices[0].message.content.strip()
            
            # Calculate latency
            end_time = asyncio.get_event_loop().time()
            latency = end_time - start_time
            
            logger.info(f"LLM response generated in {latency:.2f}s")
            logger.debug(f"Token usage: {response.usage}")
            
            return assistant_message
        
        except Exception as e:
            logger.error(f"Error getting LLM response: {e}")
            raise
    
    async def get_streaming_response(self, question: str):
        """
        Get streaming LLM response (for future optimization)
        
        Args:
            question: Transcribed interview question
        
        Yields:
            Response chunks as they're generated
        """
        try:
            stream = await self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"Interview question: {question}\n\nProvide a brief response:"
                    }
                ],
                temperature=0.7,
                max_tokens=150,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            raise
