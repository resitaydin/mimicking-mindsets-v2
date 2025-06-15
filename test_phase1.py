"""
Test script for Phase 1: Individual Persona Agents with RAG and Tooling

This script demonstrates the functionality of the persona agents created in Phase 1.

Before running this script, make sure:
1. Qdrant is running on localhost:6333
2. Your knowledge bases are built (run preprocess/build_kb.py)
3. Set your GOOGLE_API_KEY environment variable
4. Install dependencies: pip install -r requirements.txt
"""

import os
from dotenv import load_dotenv
from persona_agents import test_persona_agents

def main():
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ GOOGLE_API_KEY environment variable not set!")
        print("Please set your Google API key:")
        print("export GOOGLE_API_KEY='your-api-key-here'")
        print("or create a .env file with GOOGLE_API_KEY=your-api-key-here")
        return
    
    print("🚀 Starting Phase 1 Test: Individual Persona Agents with RAG and Tooling")
    print("=" * 80)
    
    # Run the test
    test_persona_agents()
    
    print("\n" + "=" * 80)
    print("✅ Phase 1 test completed!")

if __name__ == "__main__":
    main() 