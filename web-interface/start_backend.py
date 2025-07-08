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
    print("Checking dependencies...")
    try:
        import fastapi
        import uvicorn
        print("✓ FastAPI and Uvicorn available")
    except ImportError as e:
        print(f"✗ FastAPI/Uvicorn import failed: {e}")
        return False
    
    try:
        from agents.multi_agent_orchestrator import run_multi_agent_query
        print("✓ Multi-agent orchestrator available")
    except ImportError as e:
        print(f"✗ Multi-agent orchestrator import failed: {e}")
        return False
    
    return True

def main():
    print("Starting Mimicking Mindsets Backend...")
    
    # Ensure we are running inside the same directory as this script (web-interface)
    script_dir = Path(__file__).resolve().parent
    print(f"Script directory: {script_dir}")
    os.chdir(script_dir)

    # Check if api_server.py exists in this directory
    if not Path("api_server.py").exists():
        print("✗ api_server.py not found in current directory")
        sys.exit(1)
    else:
        print("✓ api_server.py found")
    
    # Check dependencies
    if not check_dependencies():
        print("✗ Dependency check failed")
        sys.exit(1)
    
    print("✓ All checks passed. Starting server...")
    try:
        # Start the server
        import uvicorn
        uvicorn.run(
            "api_server:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"  # Temporarily increase log level for debugging
        )
    except KeyboardInterrupt:
        print("\n✓ Server stopped by user")
        pass
    except Exception as e:
        print(f"✗ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 