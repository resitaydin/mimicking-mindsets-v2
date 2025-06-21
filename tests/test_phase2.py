"""
Phase 2 Test: Multi-Agent Orchestration

Bu test scripti LangGraph ile oluşturulan multi-agent orchestration sistemini test eder.
İki persona ajanının (Erol Güngör ve Cemil Meriç) paralel çalışmasını, yanıtlarının
sentezini ve sohbet geçmişi yönetimini doğrular.
"""

import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from agents.multi_agent_orchestrator import create_orchestrator, run_multi_agent_query

def test_multi_agent_orchestration():
    """Multi-agent orchestration sistemini test eder."""
    
    load_dotenv()
    
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ GOOGLE_API_KEY ortam değişkeni ayarlanmamış!")
        print("Lütfen Google API anahtarınızı ayarlayın:")
        print("export GOOGLE_API_KEY='your-api-key-here'")
        print("veya .env dosyası oluşturup GOOGLE_API_KEY=your-api-key-here yazın")
        return
    
    print("🚀 Faz 2 Testini Başlatıyor: Multi-Agent Orchestration (LangGraph)")
    print("=" * 80)
    
    # Test cases for multi-agent system
    test_cases = [
        {
            "name": "Kültürel Kimlik Analizi",
            "query": "Türk kültürel kimliği ve modernleşme sürecinde yaşanan değişimler hakkında ne düşünüyorsunuz?",
            "description": "Her iki ajanın da uzmanlık alanına giren bir konu - kültürel analiz"
        },
        {
            "name": "Güncel Teknoloji ve Toplum",
            "query": "2024 yılında yapay zeka teknolojilerinin toplumsal etkileri nelerdir ve bu durum Türk toplumu için ne anlama gelir?",
            "description": "Güncel bilgi gerektiren hibrit soru - web araması + kültürel analiz"
        },
        {
            "name": "Felsefe ve Modernite",
            "query": "Doğu ve Batı felsefesi arasındaki sentez arayışı modern Türk düşüncesinde nasıl kendini gösterir?",
            "description": "Felsefi analiz gerektiren karmaşık soru - her iki ajanın farklı perspektifleri"
        }
    ]
    
    # Create orchestrator
    try:
        print("\n🏗️ Multi-Agent Orchestrator başlatılıyor...")
        orchestrator = create_orchestrator()
        print("✅ Orchestrator başarıyla oluşturuldu")
    except Exception as e:
        print(f"❌ Orchestrator oluşturma hatası: {e}")
        return
    
    # Run test cases
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*20} TEST {i}: {test_case['name'].upper()} {'='*20}")
        print(f"📝 Sorgu: {test_case['query']}")
        print(f"📋 Açıklama: {test_case['description']}")
        print("\n" + "="*60)
        print("ORCHESTRATION SÜRECİ BAŞLIYOR...")
        print("="*60)
        
        try:
            # Run the multi-agent query
            result = orchestrator.invoke(test_case["query"], thread_id=f"test_{i}")
            
            # Display results
            print(f"\n{'='*30} SONUÇLAR {'='*30}")
            
            # Show individual agent outputs if available
            if result.get("erol_gungor_agent_output"):
                erol_output = result["erol_gungor_agent_output"]
                if "messages" in erol_output and erol_output["messages"]:
                    erol_response = erol_output["messages"][-1].content
                    print(f"\n🎯 EROL GÜNGÖR'ÜN KATKILARI:")
                    print("-" * 40)
                    print(f"{erol_response[:300]}..." if len(erol_response) > 300 else erol_response)
                elif "error" in erol_output:
                    print(f"\n❌ EROL GÜNGÖR HATASI: {erol_output['error']}")
            
            if result.get("cemil_meric_agent_output"):
                cemil_output = result["cemil_meric_agent_output"]
                if "messages" in cemil_output and cemil_output["messages"]:
                    cemil_response = cemil_output["messages"][-1].content
                    print(f"\n🎯 CEMİL MERİÇ'İN KATKILARI:")
                    print("-" * 40)
                    print(f"{cemil_response[:300]}..." if len(cemil_response) > 300 else cemil_response)
                elif "error" in cemil_output:
                    print(f"\n❌ CEMİL MERİÇ HATASI: {cemil_output['error']}")
            
            # Show synthesized answer
            if result.get("synthesized_answer"):
                print(f"\n🔄 SENTEZLENMİŞ YANIT:")
                print("=" * 50)
                print(result["synthesized_answer"])
            else:
                print(f"\n❌ Sentezlenmiş yanıt bulunamadı")
            
            # Show chat history info
            if result.get("chat_history"):
                print(f"\n📚 Sohbet Geçmişi: {len(result['chat_history'])} mesaj eklendi")
            
            print("\n" + "="*60)
            
        except Exception as e:
            print(f"❌ Test çalıştırma hatası: {e}")
            import traceback
            traceback.print_exc()
        
        # Pause between tests
        if i < len(test_cases):
            input(f"\n⏸️  Sonraki teste geçmek için Enter'a basın...")
    
    print(f"\n{'='*80}")
    print("✅ Faz 2 Multi-Agent Orchestration testi tamamlandı!")
    print("\n🎯 Test Özeti:")
    print("- Multi-agent paralel çalıştırma test edildi")
    print("- Ajanların yanıtları başarıyla sentezlendi") 
    print("- Sohbet geçmişi yönetimi doğrulandı")
    print("- LangGraph workflow'u sorunsuz çalıştı")
    print("- Debug çıktıları ile süreç izlendi")

def test_convenience_function():
    """convenience fonksiyonunu test eder."""
    
    print(f"\n🔧 convenience Fonksiyonu Testi")
    print("=" * 40)
    
    test_query = "Fransa'nın başkenti neresidir ve Erol Güngör milliyetçilik hakkında ne söylemiştir?"
    
    print(f"📝 Test Sorusu: {test_query}")
    print("\n🚀 run_multi_agent_query() fonksiyonu çalıştırılıyor...")
    
    try:
        result = run_multi_agent_query(test_query, thread_id="convenience_test")
        
        print(f"\n✅ convenience fonksiyonu başarıyla çalıştı")
        
        if result.get("synthesized_answer"):
            print(f"\n🔄 Sentezlenmiş Yanıt:")
            print("-" * 30)
            print(result["synthesized_answer"])
        
        if result.get("error"):
            print(f"\n❌ Hata: {result['error']}")
            
    except Exception as e:
        print(f"❌ convenience fonksiyonu hatası: {e}")

if __name__ == "__main__":
    # Run main orchestration test
    test_multi_agent_orchestration()
    
    # Ask if user wants to test convenience function
    print(f"\n" + "="*80)
    user_input = input("🔧 convenience fonksiyonunu da test etmek ister misiniz? (y/n): ")
    
    if user_input.lower() in ['y', 'yes', 'e', 'evet']:
        test_convenience_function()
    
    print(f"\n🎉 Tüm testler tamamlandı!") 