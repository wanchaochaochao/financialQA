#!/usr/bin/env python
"""
API Service Startup Script
===========================

Cross-platform Python script to start the FastAPI service.

Usage:
    python start_api.py              # Start in production mode
    python start_api.py --dev        # Start in development mode (auto-reload)
    python start_api.py --port 8080  # Custom port
"""

import sys
import subprocess
import argparse
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e.name}")
        print("\nPlease install dependencies:")
        print("  pip install -r requirements.txt")
        return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Financial QA System API Service Startup Script"
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Enable development mode with auto-reload"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (production only)"
    )

    args = parser.parse_args()

    # Print header
    print("=" * 70)
    print("🏦 Financial Asset QA System - API Service")
    print("=" * 70)
    print()

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    print("✅ Dependencies OK")
    print()

    # Print configuration
    print("📍 Configuration:")
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    mode = "Development (auto-reload)" if args.dev else "Production"
    if not args.dev and args.workers > 1:
        mode += f" ({args.workers} workers)"
    print(f"   Mode: {mode}")
    print()

    print("🚀 Starting API server...")
    print()
    print(f"📖 API Documentation: http://localhost:{args.port}/docs")
    print(f"📚 ReDoc: http://localhost:{args.port}/redoc")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()

    # Build uvicorn command
    cmd = [
        "uvicorn",
        "ai_agent.api:app",
        "--host", args.host,
        "--port", str(args.port),
        "--log-level", "info"
    ]

    if args.dev:
        cmd.append("--reload")
    elif args.workers > 1:
        cmd.extend(["--workers", str(args.workers)])

    # Start server
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
