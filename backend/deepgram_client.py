"""
Deepgram Client for Real-Time Speech-to-Text

Handles WebSocket connection to Deepgram's streaming API.
Optimized for real-time interview transcription.
"""

import asyncio
import json
import logging
from typing import AsyncIterator, Optional
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
)

logger = logging.getLogger(__name__)


class DeepgramTranscriber:
    """
    Wrapper for Deepgram streaming transcription
    
    Configuration:
    - Language: English (en-US)
    - Model: Nova-2 (latest and most accurate)
    - Smart formatting: Enabled (adds punctuation)
    - Interim results: Enabled (get partial transcripts)
    - Utterance end: 1000ms (detect when speaker finishes)
    """
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Deepgram API key is required")
        
        self.api_key = api_key
        
        # Initialize Deepgram client
        config = DeepgramClientOptions(
            options={"keepalive": "true"}
        )
        self.client = DeepgramClient(api_key, config)
        
        # Queue for transcription results
        self.transcription_queue = asyncio.Queue()
    
    async def start_transcription(self):
        """
        Start a new Deepgram streaming session
        
        Returns connection object for sending audio
        """
        try:
            # Configure streaming options
            options = LiveOptions(
                model="nova-2",
                language="en-US",
                smart_format=True,  # Automatic punctuation and formatting
                interim_results=True,  # Get partial results
                utterance_end_ms=1000,  # Detect end of utterance after 1s
                punctuate=True,
                encoding="opus",  # Match WebM/Opus from extension
                sample_rate=16000,  # 16kHz for optimal performance
            )
            
            # Create live transcription connection
            # Using API version 1 (stable) - see Deepgram docs for versioning
            DEEPGRAM_API_VERSION = "1"
            connection = self.client.listen.asyncwebsocket.v(DEEPGRAM_API_VERSION)
            
            # Set up event handlers
            async def on_message(self_inner, result, **kwargs):
                """Handle transcription results"""
                try:
                    sentence = result.channel.alternatives[0].transcript
                    
                    if len(sentence) == 0:
                        return
                    
                    # Check if this is a final result
                    is_final = result.is_final
                    
                    if is_final:
                        logger.info(f"Final transcript: {sentence}")
                        await self.transcription_queue.put(sentence)
                    else:
                        logger.debug(f"Interim transcript: {sentence}")
                        # Optionally handle interim results
                        # await self.transcription_queue.put(f"[interim] {sentence}")
                
                except Exception as e:
                    logger.error(f"Error processing transcription: {e}")
            
            async def on_error(self_inner, error, **kwargs):
                """Handle errors"""
                logger.error(f"Deepgram error: {error}")
            
            async def on_close(self_inner, close_event, **kwargs):
                """Handle connection close"""
                logger.info("Deepgram connection closed")
            
            # Register event handlers
            connection.on(LiveTranscriptionEvents.Transcript, on_message)
            connection.on(LiveTranscriptionEvents.Error, on_error)
            connection.on(LiveTranscriptionEvents.Close, on_close)
            
            # Start the connection
            if await connection.start(options):
                logger.info("Deepgram connection started successfully")
                return connection
            else:
                raise Exception("Failed to start Deepgram connection")
        
        except Exception as e:
            logger.error(f"Error starting Deepgram transcription: {e}")
            raise
    
    async def send_audio(self, connection, audio_data: bytes):
        """
        Send audio chunk to Deepgram
        
        Args:
            connection: Deepgram connection object
            audio_data: Raw audio bytes (webm/opus format)
        """
        try:
            await connection.send(audio_data)
        except Exception as e:
            logger.error(f"Error sending audio to Deepgram: {e}")
            raise
    
    async def get_transcriptions(self, connection) -> AsyncIterator[str]:
        """
        Async generator yielding transcription results
        
        Yields:
            Transcribed text strings
        """
        try:
            while True:
                # Get transcription from queue
                transcription = await self.transcription_queue.get()
                yield transcription
        except asyncio.CancelledError:
            logger.info("Transcription generator cancelled")
        except Exception as e:
            logger.error(f"Error in transcription generator: {e}")
    
    async def close(self, connection):
        """Close the Deepgram connection"""
        try:
            await connection.finish()
            logger.info("Deepgram connection closed")
        except Exception as e:
            logger.error(f"Error closing Deepgram connection: {e}")
