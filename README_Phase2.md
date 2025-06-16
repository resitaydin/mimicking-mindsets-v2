# Phase 2: Multi-Agent Orchestration with LangGraph

Bu faz, Türk entelektüelleri Erol Güngör ve Cemil Meriç'i simüle eden iki persona ajanının paralel çalışmasını koordine eden çok-ajanli orkestrasyon sistemini içerir.

## 🎯 Hedefler

- **Paralel Agent Çalıştırma**: İki persona ajanının aynı anda çalışması
- **Yanıt Sentezi**: Ajanların çıktılarının tutarlı bir yanıtta birleştirilmesi  
- **Sohbet Geçmişi Yönetimi**: Konuşma akışının takip edilmesi
- **Tool Node Desteği**: Ajanların araç kullanımının orchestration içinde yönetilmesi

## 🏗️ Sistem Mimarisi

### Graph State (`GraphState`)
```python
class GraphState(TypedDict):
    user_query: str                                    # Kullanıcı sorusu
    erol_gungor_agent_output: Optional[Dict[str, Any]] # Erol Güngör çıktısı
    cemil_meric_agent_output: Optional[Dict[str, Any]] # Cemil Meriç çıktısı
    synthesized_answer: Optional[str]                  # Sentezlenmiş yanıt
    chat_history: Annotated[List[BaseMessage], add_messages]  # Sohbet geçmişi
```

### Node'lar

#### 1. Persona Agent Node'ları
- **`erol_gungor_agent_node`**: Erol Güngör ajanını çalıştırır
- **`cemil_meric_agent_node`**: Cemil Meriç ajanını çalıştırır

Her node:
- Phase 1'den create_react_agent instance'ını kullanır
- Tool çağrıları dahil tam agent çıktısını döndürür
- Hata durumlarını graceful şekilde handle eder

#### 2. Join Node
- **`join_agents_node`**: İki ajanın tamamlanmasını bekleyen ara node
- Paralel çalışan ajanları senkronize eder

#### 3. Synthesis Node  
- **`synthesize_response_node`**: İki ajanın yanıtlarını birleştirir
- Gemini 2.0 Flash kullanarak intelligent synthesis yapar
- Tekrarları önler, perspektifleri harmanlıyor

#### 4. Memory Node
- **`update_history_node`**: Sohbet geçmişini günceller
- User query ve synthesized answer'ı history'e ekler

### Workflow Akışı

```
START
  ├─> erol_gungor_agent ──┐
  └─> cemil_meric_agent ──┴─> join_agents ─> synthesize_response ─> update_history ─> END
```

## 🔧 Kullanım

### Temel Kullanım

```python
from multi_agent_orchestrator import create_orchestrator

# Orchestrator oluştur
orchestrator = create_orchestrator()

# Sorgu gönder
result = orchestrator.invoke("Türk kültürel kimliği hakkında ne düşünüyorsunuz?")

# Sentezlenmiş yanıt
print(result["synthesized_answer"])
```

### Kolaylık Fonksiyonu

```python
from multi_agent_orchestrator import run_multi_agent_query

# Tek seferlik sorgu
result = run_multi_agent_query("Modernleşme ve gelenek arasındaki gerilim nedir?")
print(result["synthesized_answer"])
```

### Thread-based Sohbet

```python
# Aynı thread'de birden fazla sorgu
orchestrator = create_orchestrator()

result1 = orchestrator.invoke("İlk sorum...", thread_id="session_1")
result2 = orchestrator.invoke("İkinci sorum...", thread_id="session_1")  # Aynı geçmiş

# Farklı thread
result3 = orchestrator.invoke("Bağımsız soru...", thread_id="session_2")  # Yeni geçmiş
```

## 📊 Çıktı Formatı

```python
{
    "user_query": "Kullanıcının sorusu",
    "erol_gungor_agent_output": {
        "messages": [HumanMessage(...), AIMessage(...)],
        # Agent'ın tam çıktısı (tool calls dahil)
    },
    "cemil_meric_agent_output": {
        "messages": [HumanMessage(...), AIMessage(...)],
        # Agent'ın tam çıktısı (tool calls dahil)  
    },
    "synthesized_answer": "Her iki perspektifi harmanlayan final yanıt",
    "chat_history": [
        HumanMessage(content="user_query"),
        AIMessage(content="synthesized_answer")
    ]
}
```

## 🧪 Test Etme

### Ana Test Dosyası
```bash
python test_phase2.py
```

Test senaryoları:
1. **Kültürel Kimlik Analizi**: Her iki ajanın uzmanlık alanı
2. **Güncel Teknoloji ve Toplum**: Web araması + kültürel analiz
3. **Felsefe ve Modernite**: Karmaşık felsefi analiz

### Test Çıktısı Açıklaması

- **Individual Agent Contributions**: Her ajanın katkısı gösterilir
- **Synthesized Answer**: Birleştirilmiş final yanıt
- **Debug Output**: Süreç izleme bilgileri (İngilizce)
- **Chat History**: Sohbet geçmişi durumu

## 🔍 Debug Sistemi

Tüm debug çıktıları İngilizce ve detaylıdır:

```
🎯 DEBUG: Starting Erol Güngör agent node
🔍 DEBUG: User query: [sorgu]
💬 DEBUG: Invoking Erol Güngör agent
✅ DEBUG: Erol Güngör agent completed successfully
📊 DEBUG: Agent returned X messages
```

## ⚙️ Yapılandırma

### Gerekli Ortam Değişkenleri
```bash
export GOOGLE_API_KEY="your-gemini-api-key"
```

### Bağımlılıklar
- **LangGraph**: Multi-agent orchestration
- **LangChain**: Agent framework  
- **Gemini 2.0 Flash**: Synthesis LLM
- **Phase 1 bileşenleri**: Persona agents, RAG, tools

## 🚀 Gelişmiş Özellikler

### Memory Management
- LangGraph MemorySaver ile otomatik checkpoint
- Thread-based sohbet geçmişi
- Persistent conversation state

### Error Handling  
- Graceful degradation
- Partial results döndürme
- Detaylı hata raporlama

### Synthesis Intelligence
- Perspective harmonization
- Redundancy elimination  
- Context-aware combination
- Turkish intellectual tradition awareness

## 📈 Performans

### Paralel Çalıştırma
- İki agent aynı anda çalışır
- I/O bound operations optimize edilir
- Tool calls parallel processing

### Synthesis Optimization
- Minimal token usage
- Focused prompts
- Efficient content combination

## 🔄 Phase 1 ile Entegrasyon

Phase 2, Phase 1'in tüm özelliklerini korur:
- ✅ Persona-specific RAG systems
- ✅ Web search capabilities  
- ✅ Natural research behavior
- ✅ Turkish language support
- ✅ Debug monitoring

Ve üzerine ekler:
- ➕ Multi-agent coordination
- ➕ Response synthesis
- ➕ Conversation memory
- ➕ LangGraph workflow management

## 🔧 Genişletme Noktaları

Phase 3 için hazır yapı:
- Web interface integration points
- Additional persona support
- Advanced conversation management
- Real-time collaboration features 