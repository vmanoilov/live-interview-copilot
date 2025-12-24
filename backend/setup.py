"""
Automated Backend Setup Module

Handles automatic setup of the Live Interview Copilot backend,
including dependency installation, environment configuration, and validation.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Tuple, List
import logging

logger = logging.getLogger(__name__)


class BackendSetup:
    """Manages automated backend setup and configuration"""
    
    def __init__(self, backend_dir: Path = None):
        """
        Initialize setup manager
        
        Args:
            backend_dir: Path to backend directory (defaults to current file's directory)
        """
        self.backend_dir = backend_dir or Path(__file__).parent
        self.setup_flag_file = self.backend_dir / '.setup_complete'
        self.env_file = self.backend_dir / '.env'
        self.env_example = self.backend_dir / '.env.example'
        self.requirements_file = self.backend_dir / 'requirements.txt'
        self.venv_dir = self.backend_dir / 'venv'
    
    def is_setup_complete(self) -> bool:
        """
        Check if backend setup is already complete
        
        Returns:
            True if setup is complete, False otherwise
        """
        # Check for setup completion flag
        if not self.setup_flag_file.exists():
            logger.info("Setup flag file not found")
            return False
        
        # Check if .env file exists
        if not self.env_file.exists():
            logger.info(".env file not found")
            return False
        
        # Check if requirements are met (basic check)
        try:
            import fastapi
            import uvicorn
            import deepgram
            import groq
            logger.info("All required packages appear to be installed")
            return True
        except ImportError as e:
            logger.info(f"Missing required package: {e}")
            return False
    
    def check_python_version(self) -> bool:
        """
        Verify Python version meets requirements (3.9+)
        
        Returns:
            True if version is acceptable
        """
        version_info = sys.version_info
        if version_info >= (3, 9):
            logger.info(f"Python version {version_info.major}.{version_info.minor}.{version_info.micro} OK")
            return True
        else:
            logger.error(f"Python 3.9+ required, found {version_info.major}.{version_info.minor}.{version_info.micro}")
            return False
    
    def install_dependencies(self) -> bool:
        """
        Install required Python packages
        
        Returns:
            True if installation successful
        """
        if not self.requirements_file.exists():
            logger.error(f"Requirements file not found: {self.requirements_file}")
            return False
        
        try:
            logger.info("Installing dependencies from requirements.txt...")
            # Use pip to install requirements
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '-q',
                '-r', str(self.requirements_file)
            ])
            logger.info("Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False
    
    def setup_env_file(self) -> bool:
        """
        Create .env file from .env.example if it doesn't exist
        
        Returns:
            True if .env file is ready
        """
        if self.env_file.exists():
            logger.info(".env file already exists")
            return True
        
        if not self.env_example.exists():
            logger.warning(f".env.example not found at {self.env_example}")
            # Create a basic .env file
            self._create_default_env()
            return True
        
        try:
            # Copy .env.example to .env
            shutil.copy(self.env_example, self.env_file)
            logger.info(f"Created .env file from .env.example")
            logger.warning("⚠️  Please edit .env file and add your API keys:")
            logger.warning("   - DEEPGRAM_API_KEY")
            logger.warning("   - GROQ_API_KEY")
            return True
        except Exception as e:
            logger.error(f"Failed to create .env file: {e}")
            return False
    
    def _create_default_env(self):
        """Create a default .env file with placeholder values"""
        default_content = """# Deepgram API Key
# Get your API key from: https://console.deepgram.com/
DEEPGRAM_API_KEY=your_deepgram_api_key_here

# Groq API Key
# Get your API key from: https://console.groq.com/
GROQ_API_KEY=your_groq_api_key_here

# Optional: Server Configuration
# HOST=0.0.0.0
# PORT=8000

# Optional: LLM Configuration
# LLM_MODEL=llama3-70b-8192
# LLM_TEMPERATURE=0.7
# LLM_MAX_TOKENS=150
"""
        with open(self.env_file, 'w') as f:
            f.write(default_content)
        logger.info("Created default .env file")
    
    def validate_configuration(self) -> Tuple[bool, List[str]]:
        """
        Validate that required configuration is set
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Try to load environment variables
        try:
            from dotenv import load_dotenv
            load_dotenv(dotenv_path=self.env_file)
        except ImportError:
            # dotenv not installed yet, skip validation
            logger.warning("python-dotenv not available, skipping configuration validation")
            return True, []
        
        # Check required API keys
        deepgram_key = os.getenv('DEEPGRAM_API_KEY', '')
        groq_key = os.getenv('GROQ_API_KEY', '')
        
        if not deepgram_key or deepgram_key == 'your_deepgram_api_key_here':
            errors.append("DEEPGRAM_API_KEY not configured in .env file")
        
        if not groq_key or groq_key == 'your_groq_api_key_here':
            errors.append("GROQ_API_KEY not configured in .env file")
        
        return len(errors) == 0, errors
    
    def mark_setup_complete(self):
        """Mark setup as complete by creating flag file"""
        try:
            with open(self.setup_flag_file, 'w') as f:
                f.write(f"Setup completed at: {self.backend_dir}\n")
            logger.info("Setup marked as complete")
        except Exception as e:
            logger.error(f"Failed to create setup flag file: {e}")
    
    def perform_setup(self) -> bool:
        """
        Perform complete backend setup
        
        Returns:
            True if setup completed successfully
        """
        logger.info("=" * 60)
        logger.info("Starting automated backend setup...")
        logger.info("=" * 60)
        
        # Step 1: Check Python version
        logger.info("\n[1/4] Checking Python version...")
        if not self.check_python_version():
            return False
        
        # Step 2: Install dependencies
        logger.info("\n[2/4] Installing dependencies...")
        if not self.install_dependencies():
            return False
        
        # Step 3: Setup .env file
        logger.info("\n[3/4] Setting up environment configuration...")
        if not self.setup_env_file():
            return False
        
        # Step 4: Validate configuration
        logger.info("\n[4/4] Validating configuration...")
        is_valid, errors = self.validate_configuration()
        
        if not is_valid:
            logger.warning("\n⚠️  Configuration warnings:")
            for error in errors:
                logger.warning(f"   - {error}")
            logger.warning("\nSetup completed, but please configure API keys before starting the server.")
        else:
            logger.info("\n✓ Configuration validated successfully")
        
        # Mark setup as complete
        self.mark_setup_complete()
        
        logger.info("\n" + "=" * 60)
        logger.info("Backend setup completed!")
        logger.info("=" * 60)
        
        if not is_valid:
            logger.info("\nNext steps:")
            logger.info("1. Edit backend/.env file")
            logger.info("2. Add your Deepgram and Groq API keys")
            logger.info("3. Restart the server with: python main.py")
        
        return True


def perform_backend_setup() -> bool:
    """
    Convenience function to perform backend setup
    
    Returns:
        True if setup completed successfully
    """
    setup = BackendSetup()
    return setup.perform_setup()


def is_setup_done() -> bool:
    """
    Convenience function to check if setup is complete
    
    Returns:
        True if setup is complete
    """
    setup = BackendSetup()
    return setup.is_setup_complete()


if __name__ == "__main__":
    # Allow running this module directly for manual setup
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    
    setup = BackendSetup()
    
    if setup.is_setup_complete():
        print("\n✓ Backend is already set up!")
        print("\nConfiguration status:")
        is_valid, errors = setup.validate_configuration()
        if is_valid:
            print("✓ All API keys configured")
        else:
            print("⚠️  Configuration issues:")
            for error in errors:
                print(f"  - {error}")
    else:
        print("\nBackend setup required. Starting setup process...\n")
        success = setup.perform_setup()
        if success:
            print("\n✓ Setup completed successfully!")
        else:
            print("\n✗ Setup failed. Please check the errors above.")
            sys.exit(1)
