"""
FastAPI Backend for Live Interview Copilot

Responsibilities:
1. WebSocket endpoint for receiving audio chunks from Chrome extension
2. Integrate Deepgram SDK for real-time speech-to-text
3. Process transcriptions and send to Groq LLM
4. Stream responses back to extension

Architecture:
- WebSocket: /ws/audio - Bidirectional communication with extension
- Receives: Audio chunks in webm/opus format
- Sends: Transcripts and LLM responses
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import os
from typing import Optional, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our custom clients
from deepgram_client import DeepgramTranscriber
from groq_client import GroqLLMClient

# Initialize FastAPI app
app = FastAPI(title="Live Interview Copilot Backend")

# CORS Configuration
# CRITICAL: Must allow chrome-extension:// scheme for extension communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://*",  # Allow any chrome extension
        "http://localhost:3000",  # Development
        "http://localhost:8000",  # Self
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration from environment variables
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY', '')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')

# Placeholder for resume context
# TODO: Replace with actual resume text or load from file
RESUME_TEXT = """
John Doe - Senior Software Engineer
- 5 years of experience in full-stack development
- Expert in Python, JavaScript, React, and FastAPI
- Strong background in machine learning and AI
- Previous roles at Tech Company A and Startup B
- Built scalable microservices handling millions of requests
- Led team of 4 engineers on critical projects
"""

# Initialize clients
deepgram_transcriber = DeepgramTranscriber(DEEPGRAM_API_KEY)
groq_client = GroqLLMClient(GROQ_API_KEY, RESUME_TEXT)


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_message(self, websocket: WebSocket, message: dict):
        """Send JSON message to specific client"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending message: {e}")


manager = ConnectionManager()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Live Interview Copilot Backend",
        "deepgram_configured": bool(DEEPGRAM_API_KEY),
        "groq_configured": bool(GROQ_API_KEY)
    }


@app.websocket("/ws/audio")
async def websocket_audio_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for audio streaming
    
    Flow:
    1. Accept connection from Chrome extension
    2. Receive audio chunks as binary data
    3. Stream audio to Deepgram for transcription
    4. Accumulate transcript until sentence completion
    5. Send complete sentences to Groq LLM
    6. Stream responses back to extension
    """
    await manager.connect(websocket)
    
    # Buffer for accumulating transcript
    transcript_buffer = []
    last_transcript_time = asyncio.get_event_loop().time()
    
    try:
        # Start Deepgram transcription session
        deepgram_connection = await deepgram_transcriber.start_transcription()
        
        # Create task to handle Deepgram responses
        async def handle_deepgram_responses():
            """Listen for transcription results from Deepgram"""
            nonlocal transcript_buffer, last_transcript_time
            
            async for transcription in deepgram_transcriber.get_transcriptions(deepgram_connection):
                if not transcription or not transcription.strip():
                    continue
                
                logger.info(f"Transcription: {transcription}")
                
                # Send transcript to client immediately
                await manager.send_message(websocket, {
                    "type": "transcript",
                    "text": transcription
                })
                
                # Add to buffer
                transcript_buffer.append(transcription)
                current_time = asyncio.get_event_loop().time()
                
                # Check for sentence completion
                # Conditions: ends with punctuation OR 3+ seconds pause
                is_sentence_end = (
                    transcription.rstrip().endswith(('.', '?', '!')) or
                    (current_time - last_transcript_time) > 3.0
                )
                
                last_transcript_time = current_time
                
                if is_sentence_end and transcript_buffer:
                    # Join buffered transcripts into complete question
                    complete_text = ' '.join(transcript_buffer).strip()
                    transcript_buffer = []
                    
                    logger.info(f"Complete sentence detected: {complete_text}")
                    
                    # Send to LLM for response
                    try:
                        llm_response = await groq_client.get_response(complete_text)
                        
                        logger.info(f"LLM Response: {llm_response}")
                        
                        # Send LLM response to client
                        await manager.send_message(websocket, {
                            "type": "llm_response",
                            "text": llm_response,
                            "question": complete_text
                        })
                    except Exception as e:
                        logger.error(f"Error getting LLM response: {e}")
                        await manager.send_message(websocket, {
                            "type": "error",
                            "message": f"LLM error: {str(e)}"
                        })
        
        # Start Deepgram response handler
        deepgram_task = asyncio.create_task(handle_deepgram_responses())
        
        # Main loop: receive audio from client and forward to Deepgram
        while True:
            try:
                # Receive message from client
                data = await websocket.receive()
                
                if "text" in data:
                    # JSON message (metadata)
                    message = json.loads(data["text"])
                    logger.debug(f"Received metadata: {message}")
                    
                elif "bytes" in data:
                    # Binary audio data
                    audio_chunk = data["bytes"]
                    
                    # Forward to Deepgram
                    await deepgram_transcriber.send_audio(deepgram_connection, audio_chunk)
                    
            except WebSocketDisconnect:
                logger.info("Client disconnected normally")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                break
        
        # Cleanup
        deepgram_task.cancel()
        await deepgram_transcriber.close(deepgram_connection)
        
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await manager.send_message(websocket, {
                "type": "error",
                "message": str(e)
            })
        except:
            pass
    finally:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    
    # Check for required API keys
    if not DEEPGRAM_API_KEY:
        logger.warning("DEEPGRAM_API_KEY not set! Transcription will not work.")
    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not set! LLM responses will not work.")
    
    logger.info("Starting Live Interview Copilot Backend...")
    logger.info(f"Deepgram configured: {bool(DEEPGRAM_API_KEY)}")
    logger.info(f"Groq configured: {bool(GROQ_API_KEY)}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
