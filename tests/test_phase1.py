"""
Comprehensive test script for both persona agents with debug output.

This script tests both Erol Güngör and Cemil Meriç agents with various query types
to demonstrate their natural research behavior and expertise areas.
"""

import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from agents.persona_agents import initialize_components, create_persona_agent
from agents.persona_prompts import list_available_personas, get_persona_info

def test_both_personas():
    """Test both persona agents with comprehensive scenarios."""
    
    load_dotenv()
    
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ GOOGLE_API_KEY ortam değişkeni ayarlanmamış!")
        print("Lütfen Google API anahtarınızı ayarlayın:")
        print("export GOOGLE_API_KEY='your-api-key-here'")
        print("veya .env dosyası oluşturup GOOGLE_API_KEY=your-api-key-here yazın")
        return

    print("🚀 Faz 1 Testini Başlatıyor: RAG ve Araçlarla Bireysel Persona Ajanları")
    print("=" * 80)
    
    # Initialize components
    qdrant_client, embedding_model, llm = initialize_components()
    if not all([qdrant_client, embedding_model, llm]):
        print("Bileşenler başlatılamadı. Testten çıkılıyor.")
        return
    
    # Get available personas
    available_personas = list_available_personas()
    print(f"\n📋 DEBUG: Available personas: {available_personas}")
    
    # Create agents for all available personas
    agents = {}
    for persona_key in available_personas:
        try:
            persona_info = get_persona_info(persona_key)
            agent = create_persona_agent(persona_key, qdrant_client, embedding_model, llm)
            agents[persona_key] = {
                "agent": agent,
                "info": persona_info
            }
            print(f"✓ {persona_info['name']} ajanı oluşturuldu")
        except Exception as e:
            print(f"✗ {persona_key} ajan oluşturma hatası: {e}")
            return
    
    # Test cases
    test_cases = [
        {
            "name": "RAG Testi - Kültürel Analiz",
            "query": "Türk kültürel kimliği ve Batı etkisi hakkındaki düşünceleriniz nelerdir?",
            "description": "Bu dahili bilgi tabanından yanıtlanabilir olmalı"
        },
        {
            "name": "Web Arama Testi - Güncel AI",
            "query": "2024 yılında yapay zeka araştırmalarının mevcut durumu nedir?",
            "description": "Bu güncel bilgi gerektirir, bilgi tabanında olmayan bilgiler"
        },
        {
            "name": "Hibrit Test - Tarihsel ve Güncel Analiz",
            "query": "2011'de Suriye'de çıkan iç savaş sonrası Türkiye'deki kültürel ve siyasi değişimleri nasıl yorumlarsınız?",
            "description": "Bu hem dahili bilgi (kültürel analiz) hem de güncel web araması (Suriye savaşı sonrası gelişmeler) gerektirir"
        }
    ]
    
    # Test each persona with each test case
    for persona_key, persona_data in agents.items():
        agent = persona_data["agent"]
        persona_info = persona_data["info"]
        
        print(f"\n{'='*20} TESTING {persona_info['name'].upper()} {'='*20}")
        
        for test_case in test_cases:
            print(f"\n--- {test_case['name']} ---")
            print(f"Sorgu: {test_case['query']}")
            print(f"Açıklama: {test_case['description']}")
            print("\nYanıt:")
            print("-" * 50)
            
            try:
                print(f"\n🎯 DEBUG: Starting agent invocation for {persona_info['name']}")
                print(f"💬 DEBUG: Query: '{test_case['query']}'")
                
                # Run the agent
                messages = [HumanMessage(content=test_case['query'])]
                result = agent.invoke({"messages": messages})
                
                # Extract the final response
                if result and 'messages' in result:
                    print(f"📋 DEBUG: Agent returned {len(result['messages'])} messages")
                    final_message = result['messages'][-1]
                    print(f"📝 DEBUG: Final response length: {len(final_message.content)} characters")
                    print("\n" + "="*50)
                    print("PERSONA YANITI:")
                    print("="*50)
                    print(final_message.content)
                else:
                    print("❌ DEBUG: No messages in result")
                    print("Yanıt üretilmedi")
                    
            except Exception as e:
                print(f"❌ DEBUG: Exception during agent invocation: {e}")
                print(f"Test çalıştırma hatası: {e}")
            
            print("-" * 50)
            
            # Pause between tests for readability
            input(f"\n⏸️  {persona_info['name']} için sonraki teste geçmek için Enter'a basın...")
    
    print("\n" + "=" * 80)
    print("✅ Faz 1 testi tamamlandı!")
    print("\n🎯 Test Özeti:")
    print("- Her iki persona da test edildi")
    print("- RAG, web arama ve hibrit senaryolar denendi") 
    print("- Debug çıktıları ile süreç izlendi")
    print("- Doğal araştırma davranışları gözlemlendi")

if __name__ == "__main__":
    test_both_personas() 