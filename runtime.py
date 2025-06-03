import os
import asyncio
import sys
from typing import Optional
import torch

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from persona_agents import CemilMericAgent, ErolGungorAgent
from orchestrator import OrchestratorAgent

# Load environment variables
load_dotenv()


class MimickingMindsetsRuntime:
    """Main runtime system for the Mimicking Mindsets multi-agent system."""
    
    def __init__(self):
        self.orchestrator: Optional[OrchestratorAgent] = None
        self.qdrant_client: Optional[QdrantClient] = None
        self.embedding_model: Optional[SentenceTransformer] = None
        
        # Configuration from environment variables or defaults
        self.config = {
            "gemini_api_key": os.getenv("GEMINI_API_KEY"),
            "qdrant_host": os.getenv("QDRANT_HOST", "localhost"),
            "qdrant_port": int(os.getenv("QDRANT_PORT", "6333")),
            "embedding_model_name": os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-m3"),
            "embedding_dimension": int(os.getenv("EMBEDDING_DIMENSION", "1024")),
            "base_works_dir": os.getenv("BASE_WORKS_DIR", "../works")
        }
        
        # Persona configurations
        self.personas = [
            {
                "name": "Cemil Meriç",
                "folder_name": "cemil-meric",
                "qdrant_collection_name": "cemil_meric_kb",
                "agent_class": CemilMericAgent,
                "description": "Turkish intellectual, translator, essayist. Expert in Eastern/Western philosophy, French literature, cultural synthesis."
            },
            {
                "name": "Erol Güngör",
                "folder_name": "erol-gungor", 
                "qdrant_collection_name": "erol_gungor_kb",
                "agent_class": ErolGungorAgent,
                "description": "Turkish psychologist, sociologist. Expert in social psychology, Turkish cultural psychology, social change."
            }
        ]
    
    def validate_configuration(self) -> bool:
        """Validate that all required configuration is present."""
        if not self.config["gemini_api_key"]:
            print("❌ Error: GEMINI_API_KEY environment variable is required.")
            print("   Please set your Gemini API key in a .env file or environment variable.")
            return False
        
        return True
    
    def initialize_qdrant(self) -> bool:
        """Initialize Qdrant client and verify connection."""
        try:
            self.qdrant_client = QdrantClient(
                host=self.config["qdrant_host"], 
                port=self.config["qdrant_port"]
            )
            
            # Test connection
            collections = self.qdrant_client.get_collections()
            print(f"✅ Connected to Qdrant at {self.config['qdrant_host']}:{self.config['qdrant_port']}")
            print(f"   Found {len(collections.collections)} collections")
            
            # Verify required collections exist
            collection_names = [col.name for col in collections.collections]
            required_collections = [persona["qdrant_collection_name"] for persona in self.personas]
            
            missing_collections = [name for name in required_collections if name not in collection_names]
            if missing_collections:
                print(f"⚠️  Warning: Missing collections: {missing_collections}")
                print("   Please run build_kb.py first to create the knowledge base.")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error connecting to Qdrant: {e}")
            print("   Please ensure Qdrant is running and accessible.")
            return False
    
    def initialize_embedding_model(self) -> bool:
        """Initialize the embedding model."""
        try:
            print(f"🔄 Loading embedding model: {self.config['embedding_model_name']}...")
            
            # Determine device
            if torch.cuda.is_available():
                device = 'cuda'
                print(f"   Using GPU: {torch.cuda.get_device_name(0)}")
            else:
                device = 'cpu'
                print("   Using CPU")
            
            self.embedding_model = SentenceTransformer(
                self.config['embedding_model_name'], 
                device=device
            )
            print("✅ Embedding model loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error loading embedding model: {e}")
            return False
    
    def initialize_persona_agents(self) -> bool:
        """Initialize persona agents."""
        try:
            persona_agents = []
            
            for persona_config in self.personas:
                agent = persona_config["agent_class"](
                    name=persona_config["name"],
                    qdrant_collection=persona_config["qdrant_collection_name"],
                    persona_description=persona_config["description"],
                    qdrant_client=self.qdrant_client,
                    embedding_model=self.embedding_model,
                    gemini_api_key=self.config["gemini_api_key"]
                )
                persona_agents.append(agent)
                print(f"✅ Initialized {persona_config['name']} agent")
            
            # Initialize orchestrator
            self.orchestrator = OrchestratorAgent(
                persona_agents=persona_agents,
                gemini_api_key=self.config["gemini_api_key"]
            )
            print("✅ Orchestrator agent initialized")
            
            return True
            
        except Exception as e:
            print(f"❌ Error initializing agents: {e}")
            return False
    
    async def initialize_system(self) -> bool:
        """Initialize the entire system."""
        print("🚀 Initializing Mimicking Mindsets Runtime System...")
        print("=" * 60)
        
        # Step 1: Validate configuration
        if not self.validate_configuration():
            return False
        
        # Step 2: Initialize Qdrant
        if not self.initialize_qdrant():
            return False
        
        # Step 3: Initialize embedding model
        if not self.initialize_embedding_model():
            return False
        
        # Step 4: Initialize persona agents and orchestrator
        if not self.initialize_persona_agents():
            return False
        
        print("=" * 60)
        print("🎉 System initialization complete!")
        print()
        return True
    
    def print_welcome_message(self):
        """Print welcome message and instructions."""
        print("Welcome to Mimicking Mindsets v2!")
        print("🧠 Interact with the intellectual perspectives of Turkish thinkers")
        print()
        print("Available personas:")
        for persona in self.personas:
            print(f"  • {persona['name']}: {persona['description']}")
        print()
        print("Commands:")
        print("  • Type your question to get insights from multiple perspectives")
        print("  • '/summary' - View conversation summary")
        print("  • '/clear' - Clear conversation history") 
        print("  • '/export <filename>' - Export conversation to file")
        print("  • '/help' - Show this help message")
        print("  • '/quit' or '/exit' - Exit the system")
        print()
        print("=" * 60)
    
    def print_help(self):
        """Print help message."""
        print("\n📖 Help - Mimicking Mindsets v2")
        print("=" * 40)
        print("This system allows you to interact with AI representations of Turkish")
        print("intellectual figures. Ask questions and receive synthesized insights")
        print("from multiple perspectives.")
        print()
        print("How it works:")
        print("1. The Orchestrator analyzes your query")
        print("2. Relevant persona agents are activated")
        print("3. Each agent searches their knowledge base")
        print("4. Responses are synthesized into a coherent answer")
        print()
        print("Example questions:")
        print("• 'What is the relationship between culture and civilization?'")
        print("• 'How does modernization affect traditional values?'")
        print("• 'What is the role of psychology in understanding society?'")
        print("=" * 40)
    
    async def handle_command(self, user_input: str) -> bool:
        """Handle special commands. Returns True if command was processed, False otherwise."""
        command = user_input.strip().lower()
        
        if command in ['/quit', '/exit']:
            return True
        elif command == '/help':
            self.print_help()
        elif command == '/summary':
            summary = self.orchestrator.get_conversation_summary()
            print(f"\n📊 {summary}\n")
        elif command == '/clear':
            self.orchestrator.clear_conversation_history()
        elif command.startswith('/export'):
            parts = command.split(' ', 1)
            if len(parts) > 1:
                filename = parts[1].strip()
                try:
                    self.orchestrator.export_conversation_history(filename)
                except Exception as e:
                    print(f"❌ Error exporting conversation: {e}")
            else:
                print("❌ Please specify a filename: /export <filename>")
        else:
            return False  # Not a command
        
        return True
    
    async def run_interactive_loop(self):
        """Run the main interactive loop."""
        self.print_welcome_message()
        
        try:
            while True:
                # Get user input
                user_input = input("💭 Your question: ").strip()
                
                if not user_input:
                    continue
                
                # Check for commands
                if await self.handle_command(user_input):
                    if user_input.lower() in ['/quit', '/exit']:
                        break
                    continue
                
                # Process query through orchestrator
                try:
                    print("\n" + "⚡" * 60)
                    result = await self.orchestrator.process_query(user_input)
                    print("⚡" * 60)
                    
                    # Display individual persona responses first
                    print(f"\n📚 Bireysel Düşünür Cevapları:\n")
                    print("=" * 80)
                    
                    persona_responses = result["persona_responses"]
                    relevance_scores = result["relevance_scores"]
                    
                    for agent_name in result["active_agents"]:
                        if agent_name in persona_responses:
                            response_data = persona_responses[agent_name]
                            relevance = relevance_scores.get(agent_name, 0.0)
                            
                            print(f"\n🎭 {agent_name} (İlgililik: {relevance:.1f}):")
                            print("-" * 50)
                            
                            # Show sources if available
                            if response_data.get('sources_used'):
                                sources = response_data['sources_used'][:3]  # Show first 3 sources
                                print(f"📖 Kullanılan kaynaklar: {', '.join(sources)}")
                                print()
                            
                            print(response_data.get('response', 'Cevap alınamadı'))
                            print("\n" + "-" * 50)
                    
                    # Display orchestrator's synthesis as analysis and summary
                    print(f"\n🎯 Orchestrator Analizi ve Sentezi:\n")
                    print("=" * 80)
                    print(result["synthesized_response"])
                    print("\n" + "=" * 60 + "\n")
                    
                except KeyboardInterrupt:
                    print("\n\n⏸️  Query interrupted by user")
                    continue
                except Exception as e:
                    print(f"\n❌ Error processing query: {e}\n")
                    continue
                    
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            sys.exit(1)
    
    async def run(self):
        """Main entry point to run the system."""
        # Initialize system
        if not await self.initialize_system():
            print("❌ System initialization failed. Exiting.")
            sys.exit(1)
        
        # Run interactive loop
        await self.run_interactive_loop()


async def main():
    """Main entry point."""
    runtime = MimickingMindsetsRuntime()
    await runtime.run()


if __name__ == "__main__":
    asyncio.run(main()) 