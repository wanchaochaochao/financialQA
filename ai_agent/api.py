"""
Financial Asset QA System - FastAPI Backend Service
====================================================

RESTful API service for the financial QA system.
Wraps the AI agent functionality for web access.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from contextlib import asynccontextmanager
import logging
import time

from .agent_core import build_financial_agent, FinancialQAAgent
from .config import Config
from .logger import get_logger, log_qa_interaction
from .monitor import get_monitor

# NOTE: User authentication is now handled by Next.js backend
# Removed imports: database, models, crud, auth (SQLAlchemy-based user system)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global agent instance
agent_instance: Optional[FinancialQAAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Initializes the agent on startup and cleans up on shutdown.
    """
    global agent_instance

    logger.info("🚀 Starting Financial QA API Service...")
    logger.info(f"📍 Model: {Config.LLM_MODEL}")
    logger.info(f"📍 Base URL: {Config.OPENAI_BASE_URL}")

    try:
        # Initialize agent
        logger.info("🤖 Initializing AI Agent...")
        agent_instance = build_financial_agent(rebuild_kb=False)
        logger.info("✅ Agent initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize: {e}")
        raise

    yield

    # Cleanup on shutdown
    logger.info("👋 Shutting down Financial QA API Service...")
    agent_instance = None


# Create FastAPI application
app = FastAPI(
    title="Financial Asset QA System API",
    description="AI-powered financial question answering system with RAG and real-time market data",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for chart images
# Charts can be accessed at http://localhost:8000/charts/<filename>.png
chart_output_dir = Config.BASE_DIR / "chart_output"
chart_output_dir.mkdir(exist_ok=True)
app.mount("/charts", StaticFiles(directory=str(chart_output_dir)), name="charts")


# ==================== Request/Response Models ====================

class ChatRequest(BaseModel):
    """Chat request model"""
    question: str = Field(
        ...,
        description="User question about finance or market data",
        min_length=1,
        max_length=1000,
        example="阿里巴巴现在的股价是多少？"
    )


class ChatResponse(BaseModel):
    """Chat response model"""
    question: str = Field(..., description="Original user question")
    answer: str = Field(..., description="AI-generated answer")
    timestamp: str = Field(..., description="Response timestamp")
    model: str = Field(..., description="LLM model used")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Current timestamp")
    agent_ready: bool = Field(..., description="Whether agent is initialized")


class StatusResponse(BaseModel):
    """System status response"""
    agent_ready: bool = Field(..., description="Agent initialization status")
    model: str = Field(..., description="LLM model name")
    embedding_model: str = Field(..., description="Embedding model name")
    knowledge_base_docs: int = Field(..., description="Number of documents in knowledge base")
    config: Dict[str, Any] = Field(..., description="System configuration")


class RebuildResponse(BaseModel):
    """Knowledge base rebuild response"""
    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Status message")
    timestamp: str = Field(..., description="Operation timestamp")


# ==================== Authentication Models ====================

# NOTE: Authentication request/response models removed
# User authentication is now handled by Next.js backend (/api/auth/*)


# ==================== Helper Functions ====================

def get_agent() -> FinancialQAAgent:
    """Get the agent instance"""
    if agent_instance is None:
        raise HTTPException(
            status_code=503,
            detail="Agent not initialized. Please wait for service to start."
        )
    return agent_instance


def get_timestamp() -> str:
    """Get current timestamp as ISO format string"""
    return datetime.now().isoformat()


# NOTE: Authentication helper functions removed (get_current_user, get_optional_user)
# User authentication is handled by Next.js backend


# ==================== API Endpoints ====================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Financial Asset QA System API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "note": "Authentication endpoints (/api/auth/*) are now handled by Next.js backend",
        "endpoints": {
            "core": {
                "chat": "POST /api/chat",
                "health": "GET /api/health",
                "status": "GET /api/status",
                "rebuild": "POST /api/rebuild-kb"
            },
            "monitoring": {
                "metrics": "GET /api/metrics",
                "today_metrics": "GET /api/metrics/today",
                "trends": "GET /api/metrics/trends?days=7",
                "tool_usage": "GET /api/metrics/tools?days=7",
                "error_analysis": "GET /api/metrics/errors?days=7",
                "dashboard": "GET /api/dashboard",
                "health_report": "GET /api/health-report"
            },
            "admin": {
                "models": "GET /api/models",
                "config": "GET /api/config"
            }
        }
    }


# ==================== Authentication Endpoints ====================
# NOTE: All authentication endpoints have been moved to Next.js backend
# - POST /api/auth/register -> Next.js handles user registration
# - POST /api/auth/login -> Next.js handles user login
# - GET /api/auth/me -> Next.js handles user info retrieval
# Python backend now focuses solely on AI Q&A functionality


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns service health status.
    """
    return HealthResponse(
        status="healthy",
        timestamp=get_timestamp(),
        agent_ready=agent_instance is not None
    )


@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """
    Get system status.

    Returns detailed information about the system configuration and state.
    """
    # Count knowledge base documents
    kb_count = 0
    if Config.KNOWLEDGE_BASE_DIR.exists():
        kb_count = len(list(Config.KNOWLEDGE_BASE_DIR.glob("*.txt")))

    return StatusResponse(
        agent_ready=agent_instance is not None,
        model=Config.LLM_MODEL,
        embedding_model=Config.EMBEDDING_MODEL,
        knowledge_base_docs=kb_count,
        config={
            "chunk_size": Config.CHUNK_SIZE,
            "chunk_overlap": Config.CHUNK_OVERLAP,
            "retrieval_top_k": Config.RETRIEVAL_TOP_K,
            "agent_max_iterations": Config.AGENT_MAX_ITERATIONS,
            "agent_verbose": Config.AGENT_VERBOSE,
        }
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint - Ask a question to the AI agent.

    The agent will automatically route the question to:
    - Financial data APIs (for stock prices, market data)
    - Knowledge base (for financial concepts, company info)

    Args:
        request: Chat request containing the user's question

    Returns:
        ChatResponse with the AI-generated answer

    Example:
        ```
        POST /api/chat
        {
            "question": "阿里巴巴现在的股价是多少？"
        }
        ```
    """
    start_time = time.time()
    success = False
    answer = ""
    error_msg = None

    try:
        agent = get_agent()

        logger.info(f"📝 Question received: {request.question}")

        # Get answer from agent
        answer = agent.chat(request.question)
        success = True

        logger.info(f"✅ Answer generated: {len(answer)} characters")

        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000

        # Log QA interaction
        log_qa_interaction(
            question=request.question,
            answer=answer,
            response_time_ms=response_time_ms,
            success=True,
            tools_used=[],  # TODO: Extract tools from agent execution
            metadata={"model": Config.LLM_MODEL}
        )

        return ChatResponse(
            question=request.question,
            answer=answer,
            timestamp=get_timestamp(),
            model=Config.LLM_MODEL
        )

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Error processing question: {e}")

        # Log failed interaction
        response_time_ms = (time.time() - start_time) * 1000
        log_qa_interaction(
            question=request.question,
            answer="",
            response_time_ms=response_time_ms,
            success=False,
            error_message=error_msg
        )

        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )


@app.post("/api/rebuild-kb", response_model=RebuildResponse)
async def rebuild_knowledge_base():
    """
    Rebuild knowledge base (Admin endpoint).

    Rebuilds the vector store from scratch.
    This operation may take some time.

    Returns:
        RebuildResponse with operation status
    """
    try:
        global agent_instance

        logger.info("🔄 Rebuilding knowledge base...")

        # Rebuild agent with new knowledge base
        agent_instance = build_financial_agent(rebuild_kb=True)

        logger.info("✅ Knowledge base rebuilt successfully")

        return RebuildResponse(
            status="success",
            message="知识库重建完成",
            timestamp=get_timestamp()
        )

    except Exception as e:
        logger.error(f"❌ Error rebuilding knowledge base: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error rebuilding knowledge base: {str(e)}"
        )


# ==================== Additional Endpoints (Optional) ====================

@app.get("/api/models")
async def get_models():
    """Get information about the models in use"""
    return {
        "llm": {
            "model": Config.LLM_MODEL,
            "temperature": Config.LLM_TEMPERATURE,
            "base_url": Config.OPENAI_BASE_URL,
        },
        "embedding": {
            "model": Config.EMBEDDING_MODEL,
        }
    }


@app.get("/api/config")
async def get_config():
    """Get system configuration (Admin endpoint)"""
    return {
        "rag": {
            "chunk_size": Config.CHUNK_SIZE,
            "chunk_overlap": Config.CHUNK_OVERLAP,
            "retrieval_top_k": Config.RETRIEVAL_TOP_K,
        },
        "agent": {
            "max_iterations": Config.AGENT_MAX_ITERATIONS,
            "verbose": Config.AGENT_VERBOSE,
        },
        "paths": {
            "knowledge_base": str(Config.KNOWLEDGE_BASE_DIR),
            "faiss_index": str(Config.FAISS_INDEX_DIR),
        }
    }


# ==================== Monitoring Endpoints ====================

@app.get("/api/metrics")
async def get_metrics():
    """
    Get real-time metrics from current session.

    Returns:
        Real-time performance metrics
    """
    monitor = get_monitor()
    return monitor.get_realtime_metrics()


@app.get("/api/metrics/today")
async def get_today_metrics():
    """
    Get metrics for today.

    Returns:
        Today's performance statistics
    """
    monitor = get_monitor()
    return monitor.get_daily_metrics()


@app.get("/api/metrics/trends")
async def get_trends(days: int = 7):
    """
    Get performance trends over time.

    Args:
        days: Number of days to analyze (default: 7)

    Returns:
        Performance trend analysis
    """
    monitor = get_monitor()
    return monitor.get_performance_trends(days=days)


@app.get("/api/metrics/tools")
async def get_tool_usage(days: int = 7):
    """
    Get tool usage statistics.

    Args:
        days: Number of days to analyze (default: 7)

    Returns:
        Tool usage statistics
    """
    monitor = get_monitor()
    return monitor.get_tool_usage_stats(days=days)


@app.get("/api/metrics/errors")
async def get_error_analysis(days: int = 7):
    """
    Get error analysis.

    Args:
        days: Number of days to analyze (default: 7)

    Returns:
        Error analysis data
    """
    monitor = get_monitor()
    return monitor.get_error_analysis(days=days)


@app.get("/api/dashboard")
async def get_dashboard():
    """
    Get comprehensive dashboard data.

    Returns:
        All monitoring metrics for dashboard
    """
    monitor = get_monitor()
    return monitor.generate_dashboard_data()


@app.get("/api/health-report")
async def get_health_report():
    """
    Get system health report.

    Returns:
        System health status and recommendations
    """
    monitor = get_monitor()
    return monitor.generate_health_report()


# ==================== Error Handlers ====================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The endpoint {request.url.path} does not exist",
            "available_endpoints": {
                "docs": "/docs",
                "chat": "/api/chat",
                "health": "/api/health",
                "status": "/api/status"
            }
        }
    )


# ==================== Main ====================

if __name__ == "__main__":
    import uvicorn
    import os

    # Read host and port from environment variables
    HOST = os.getenv("API_HOST", "0.0.0.0")
    PORT = int(os.getenv("API_PORT", "8000"))

    print("=" * 70)
    print("🏦 Financial Asset QA System - API Service")
    print("=" * 70)
    print(f"\n📍 Starting server on http://{HOST}:{PORT}")
    print(f"📖 API Documentation: http://localhost:{PORT}/docs")
    print(f"📚 ReDoc: http://localhost:{PORT}/redoc")
    print(f"\n💡 Configure via environment variables:")
    print(f"   API_HOST={HOST}")
    print(f"   API_PORT={PORT}")
    print("\nPress Ctrl+C to stop\n")

    uvicorn.run(
        "ai_agent.api:app",
        host=HOST,
        port=PORT,
        reload=True,  # Enable auto-reload in development
        log_level="info"
    )
