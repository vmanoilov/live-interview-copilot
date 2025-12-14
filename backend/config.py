"""
Configuration for Live Interview Copilot Backend

Manages environment variables and configuration settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """Application configuration"""
    
    # API Keys
    DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY', '')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    
    # Server settings
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8000))
    
    # Resume path (optional: load from file)
    RESUME_PATH = os.getenv('RESUME_PATH', '')
    
    # Audio settings
    AUDIO_SAMPLE_RATE = 16000  # 16kHz for Deepgram
    AUDIO_CHUNK_SIZE = 250  # 250ms chunks
    
    # LLM settings
    LLM_MODEL = os.getenv('LLM_MODEL', 'llama3-70b-8192')
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', 0.7))
    LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', 150))
    
    # Transcription settings
    SENTENCE_END_PAUSE_MS = 3000  # 3 seconds
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        if not cls.DEEPGRAM_API_KEY:
            errors.append("DEEPGRAM_API_KEY not set")
        
        if not cls.GROQ_API_KEY:
            errors.append("GROQ_API_KEY not set")
        
        return errors
    
    @classmethod
    def load_resume(cls) -> str:
        """Load resume from file if path is specified"""
        if cls.RESUME_PATH and os.path.exists(cls.RESUME_PATH):
            with open(cls.RESUME_PATH, 'r') as f:
                return f.read()
        return ""


# Create a singleton instance
config = Config()
