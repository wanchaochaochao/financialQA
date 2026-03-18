"""
Configuration Management
========================

Manages API keys, model configurations, and system paths.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the financial QA system"""

    # ==================== Paths ====================
    # All data directories are now inside ai_agent module
    BASE_DIR = Path(__file__).parent  # /Users/wanchao/financialQA/ai_agent
    KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
    FAISS_INDEX_DIR = BASE_DIR / "faiss_index"

    # ==================== OpenAI API Configuration ====================
    OPENAI_API_KEY: str = os.getenv(
        "OPENAI_API_KEY",
        "sk-BNB9wtkenpzSeZM04qY8L9Je5tLqbBlnOnqocqv84K3NoLR3"
    )
    OPENAI_BASE_URL: str = os.getenv(
        "OPENAI_BASE_URL",
        "https://api.openai-proxy.org/v1"
    )

    # Set environment variable for OpenAI
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

    # ==================== LLM Model Configuration ====================
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4.1-mini")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0"))

    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")

    # ==================== RAG Configuration ====================
    # Document splitting
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))

    # Vector retrieval
    RETRIEVAL_TOP_K: int = int(os.getenv("RETRIEVAL_TOP_K", "3"))

    # ==================== Agent Configuration ====================
    AGENT_MAX_ITERATIONS: int = int(os.getenv("AGENT_MAX_ITERATIONS", "15"))
    AGENT_MAX_EXECUTION_TIME: int = int(os.getenv("AGENT_MAX_EXECUTION_TIME", "60"))  # seconds
    AGENT_VERBOSE: bool = os.getenv("AGENT_VERBOSE", "true").lower() == "true"

    # ==================== Data API Configuration ====================
    # Yahoo Finance settings
    YFINANCE_CACHE_DIR = BASE_DIR / ".yfinance_cache"

    # Alpha Vantage API (optional, for alternative data source)
    ALPHA_VANTAGE_API_KEY: Optional[str] = os.getenv("ALPHA_VANTAGE_API_KEY")

    # ==================== Web Search Configuration ====================
    # For news and market analysis
    USE_WEB_SEARCH: bool = os.getenv("USE_WEB_SEARCH", "false").lower() == "true"

    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        cls.KNOWLEDGE_BASE_DIR.mkdir(exist_ok=True)
        cls.FAISS_INDEX_DIR.mkdir(exist_ok=True)
        cls.YFINANCE_CACHE_DIR.mkdir(exist_ok=True)

    @classmethod
    def get_openai_config(cls) -> dict:
        """Get OpenAI configuration as a dictionary"""
        return {
            "api_key": cls.OPENAI_API_KEY,
            "base_url": cls.OPENAI_BASE_URL,
            "model": cls.LLM_MODEL,
            "temperature": cls.LLM_TEMPERATURE,
        }

    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        if not cls.OPENAI_API_KEY or cls.OPENAI_API_KEY.startswith("sk-your"):
            raise ValueError(
                "Please set OPENAI_API_KEY in environment variables or .env file"
            )
        return True


# Initialize directories on module import
Config.ensure_directories()
