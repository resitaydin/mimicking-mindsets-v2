#!/usr/bin/env python3
"""
Startup script for the Mimicking Mindsets Backend API Server
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        print("FastAPI dependencies found")
    except ImportError as e:
        print(f"Missing dependencies: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False
    
    try:
        from agents.multi_agent_orchestrator import run_multi_agent_query
        print("Multi-agent orchestrator found")
    except ImportError as e:
        print(f"Multi-agent orchestrator not found: {e}")
        print("Please ensure agents/multi_agent_orchestrator.py is in the current directory")
        return False
    
    return True

def main():
    print("Starting Mimicking Mindsets Backend Server...")
    
    # Ensure we are running inside the same directory as this script (web-interface)
    script_dir = Path(__file__).resolve().parent
    os.chdir(script_dir)

    # Check if api_server.py exists in this directory
    if not Path("api_server.py").exists():
        print("ERROR: api_server.py not found alongside start_backend.py")
        print("Please make sure api_server.py is located in the same directory as start_backend.py")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("Server starting on http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    
    try:
        # Start the server
        import uvicorn
        uvicorn.run(
            "api_server:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 