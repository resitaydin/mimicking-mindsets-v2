# Multi-Agent Persona System Evaluation Pipeline

Bu değerlendirme pipeline'ı, çok-ajanlı persona sisteminin performansını kapsamlı bir şekilde analiz etmek için tasarlanmıştır. RAGAS framework'ü ve LangChain değerlendiricilerini kullanarak sistem çıktılarını objektif metriklerle değerlendirir.

## 🎯 Değerlendirme Kriterleri

### 1. Faithfulness (Sadakat) - RAGAS
- **Amaç**: Yanıtların kaynak metinlere ne kadar sadık kaldığını ölçer
- **Metrik**: RAGAS Faithfulness Score (0-1 arası)
- **Önemli**: Persona ajanlarının kendi bilgi tabanlarındaki kaynaklara ne kadar bağlı kaldığını gösterir

### 2. Answer Relevancy (Yanıt İlgililiği) - RAGAS  
- **Amaç**: Yanıtların kullanıcı sorusuna ne kadar uygun olduğunu ölçer
- **Metrik**: RAGAS Answer Relevancy Score (0-1 arası)
- **Önemli**: Ajanların soruyu doğru anlayıp ilgili yanıt verip vermediğini gösterir

### 3. Context Precision (Bağlam Hassasiyeti) - RAGAS
- **Amaç**: Alınan kaynak metinlerin ne kadar hassas/ilgili olduğunu ölçer
- **Metrik**: RAGAS Context Precision Score (0-1 arası)
- **Önemli**: RAG sisteminin doğru kaynaklardan bilgi çekip çekmediğini gösterir

### 4. Context Recall (Bağlam Geri Çağırma) - RAGAS
- **Amaç**: İlgili tüm kaynak bilgilerinin ne kadarının alındığını ölçer
- **Metrik**: RAGAS Context Recall Score (0-1 arası)
- **Önemli**: Sistemin kapsamlı bilgi toplama becerisini gösterir

### 5. Coherence (Tutarlılık) - LangChain
- **Amaç**: Yanıtların mantıksal tutarlılığını ve akıcılığını ölçer
- **Metrik**: LangChain Coherence Score (0-1 arası)
- **Önemli**: Sentezlenmiş yanıtların ne kadar tutarlı olduğunu gösterir

## 🏗️ Pipeline Mimarisi

### Evaluation Pipeline Adımları

```
1. Sistem Sorgusu
   ├─ Multi-agent orchestrator çalıştırılır
   ├─ Her iki persona ajanı paralel çalışır
   └─ Yanıtlar sentezlenir

2. RAGAS Değerlendirmesi
   ├─ Faithfulness hesaplanır
   ├─ Answer Relevancy hesaplanır
   ├─ Context Precision hesaplanır
   └─ Context Recall hesaplanır

3. Coherence Değerlendirmesi
   ├─ LangChain evaluator kullanılır
   └─ Mantıksal tutarlılık ölçülür

4. Sonuç Kaydetme
   ├─ Detaylı JSON raporu
   ├─ Özet CSV tablosu
   └─ Konsol çıktısı
```

## 📦 Kurulum

### Gerekli Bağımlılıklar

```bash
# Temel bağımlılıklar zaten requirements.txt'de mevcut
pip install -r requirements.txt

# Ek değerlendirme bağımlılıkları (otomatik yüklenecek)
# - ragas>=0.2.0
# - datasets>=2.14.0  
# - pandas>=2.0.0
# - tabulate>=0.9.0
# - langchain-experimental>=0.0.50
```

### Ortam Değişkenleri

```bash
# Google API anahtarı (Gemini için gerekli)
export GOOGLE_API_KEY="your-gemini-api-key"
```

## 🚀 Kullanım

### 1. Basit Değerlendirme

```python
from evaluation_pipeline import EvaluationPipeline, EvaluationConfig

# Yapılandırma oluştur
config = EvaluationConfig(
    test_queries=[
        "Türk kültürel kimliği hakkında ne düşünüyorsunuz?",
        "Modernleşme ve gelenek arasındaki denge nedir?"
    ]
)

# Pipeline çalıştır
pipeline = EvaluationPipeline(config)
results = pipeline.run_evaluation()
pipeline.save_results()
```

### 2. İnteraktif Menü

```bash
python run_evaluation.py
```

Bu komut şu seçenekleri sunar:
- **Hızlı Değerlendirme**: 2 sorgu ile test
- **Kültürel Kimlik Odaklı**: 3 kültürel sorgu
- **Kapsamlı Değerlendirme**: 9 farklı kategoride sorgu
- **Sadece RAGAS**: Daha hızlı değerlendirme
- **Özel Değerlendirme**: Kendi sorularınızla

### 3. Programatik Kullanım

```python
# Özel sorular ile değerlendirme
custom_queries = [
    "Batılılaşma sürecinin etkileri nelerdir?",
    "Entelektüel sorumluluğun sınırları nedir?"
]

pipeline = EvaluationPipeline(EvaluationConfig(
    test_queries=custom_queries,
    output_dir="my_evaluation",
    enable_ragas=True,
    enable_coherence=True
))

results = pipeline.run_evaluation()
```

## 📊 Çıktı Formatları

### 1. Konsol Çıktısı

Pipeline çalışırken detaylı debug bilgileri gösterir:

```
🎯 EVALUATING QUERY: Türk kültürel kimliği hakkında ne düşünüyorsunuz?
================================================================================

📝 STEP 1: Running system query...
🎯 Starting Erol Güngör agent node
🔍 User query: Türk kültürel kimliği hakkında ne düşünüyorsunuz?
💬 Invoking Erol Güngör agent
✅ Erol Güngör agent completed successfully

📊 STEP 2: RAGAS evaluation...
🔍 Running RAGAS evaluation with 5 contexts...
📈 faithfulness: 0.892
📈 answer_relevancy: 0.945
📈 context_precision: 0.823
📈 context_recall: 0.756

🧠 STEP 3: Coherence evaluation...
🔍 Running coherence evaluation...
📈 Coherence score: 0.867
```

### 2. Özet Tablosu

```
📋 EVALUATION RESULTS SUMMARY
════════════════════════════════════════════════════════════════
Query                    Faithfulness  Answer Relevancy  Context Precision  Context Recall  Coherence  Sources  Errors
Türk kültürel kimliği... 0.892        0.945            0.823             0.756          0.867      5        0
Modernleşme ve gelenek... 0.834        0.912            0.789             0.823          0.798      4        0
════════════════════════════════════════════════════════════════

📈 AVERAGE SCORES:
  Faithfulness: 0.863 (n=2)
  Answer Relevancy: 0.928 (n=2)
  Context Precision: 0.806 (n=2)
  Context Recall: 0.789 (n=2)
  Coherence: 0.832 (n=2)
```

### 3. Detaylı JSON Raporu

```json
[
  {
    "query": "Türk kültürel kimliği hakkında ne düşünüyorsunuz?",
    "timestamp": "2024-01-23T15:30:45",
    "erol_response": "Erol Güngör'ün yanıtı...",
    "cemil_response": "Cemil Meriç'in yanıtı...",
    "synthesized_response": "Sentezlenmiş final yanıt...",
    "sources": [
      {
        "source": "Erol Güngör - Kültür Değişmeleri",
        "content": "Kaynak metin içeriği..."
      }
    ],
    "faithfulness_score": 0.892,
    "answer_relevancy_score": 0.945,
    "context_precision_score": 0.823,
    "context_recall_score": 0.756,
    "coherence_score": 0.867,
    "coherence_explanation": "Yanıt mantıksal olarak tutarlı...",
    "errors": []
  }
]
```

## 🔧 Yapılandırma Seçenekleri

### EvaluationConfig Parametreleri

```python
@dataclass
class EvaluationConfig:
    test_queries: List[str]           # Değerlendirilecek sorular
    output_dir: str = "evaluation_results"  # Çıktı dizini
    save_detailed_results: bool = True      # Detaylı JSON kaydet
    save_summary_table: bool = True         # Özet tablo kaydet
    enable_ragas: bool = True              # RAGAS değerlendirmesi
    enable_coherence: bool = True          # Coherence değerlendirmesi
    evaluation_model: str = "gemini-2.0-flash-exp"  # Değerlendirme modeli
    temperature: float = 0.1               # Model sıcaklığı
```

### Özel Değerlendirme Senaryoları

```python
# Sadece RAGAS (daha hızlı)
config = EvaluationConfig(
    test_queries=my_queries,
    enable_coherence=False
)

# Sadece Coherence
config = EvaluationConfig(
    test_queries=my_queries,
    enable_ragas=False
)

# Özel çıktı dizini
config = EvaluationConfig(
    test_queries=my_queries,
    output_dir="my_custom_results"
)
```

## 📈 Metrik Yorumlama

### Skor Aralıkları

- **0.9 - 1.0**: Mükemmel performans
- **0.8 - 0.9**: Çok iyi performans  
- **0.7 - 0.8**: İyi performans
- **0.6 - 0.7**: Orta performans
- **0.5 - 0.6**: Zayıf performans
- **0.0 - 0.5**: Çok zayıf performans

### Metrik Bazlı Analiz

#### Faithfulness Düşükse:
- Ajanlar kaynaklarından sapıyor olabilir
- RAG sistemi yanlış bilgi çekiyor olabilir
- Persona prompts'ları güçlendirilmeli

#### Answer Relevancy Düşükse:
- Ajanlar soruyu yanlış anlıyor olabilir
- Query processing iyileştirilmeli
- Persona understanding geliştirilmeli

#### Context Precision Düşükse:
- Çok fazla irrelevant kaynak çekiliyor
- Semantic search threshold'u artırılmalı
- Embedding model kalitesi sorgulanmalı

#### Context Recall Düşükse:
- Yeterli kaynak çekilmiyor
- Knowledge base eksik olabilir
- Search limit'i artırılmalı

#### Coherence Düşükse:
- Synthesis logic'i iyileştirilmeli
- Persona integration problemi var
- Response generation prompts'ları güçlendirilmeli

## 🛠️ Troubleshooting

### Yaygın Hatalar

#### 1. RAGAS Import Hatası
```bash
pip install ragas datasets
```

#### 2. LangChain Evaluation Hatası
```bash
pip install langchain-experimental
```

#### 3. Google API Key Hatası
```bash
export GOOGLE_API_KEY="your-key-here"
```

#### 4. Qdrant Bağlantı Hatası
- Qdrant server'ın çalıştığından emin olun
- Knowledge base'lerin yüklendiğini kontrol edin

### Debug Modları

Pipeline otomatik olarak detaylı debug bilgileri gösterir:
- System query execution
- Agent responses
- RAGAS evaluation steps
- Coherence evaluation process
- Error tracking

## 🔄 Entegrasyon

### Mevcut Sistemle Entegrasyon

Pipeline, mevcut Phase 2 multi-agent orchestrator ile tam uyumludur:
- ✅ LangGraph workflow'u destekler
- ✅ LangSmith tracing ile uyumlu
- ✅ Persona agent'ları kullanır
- ✅ RAG sistemini değerlendirir
- ✅ Tool usage'ı analiz eder

### CI/CD Pipeline Entegrasyonu

```bash
# Otomatik değerlendirme scripti
python run_evaluation.py --config quick --output ci_results
```

## 📝 Örnek Kullanım Senaryoları

### 1. Geliştirme Sürecinde Kalite Kontrolü

```python
# Her major değişiklik sonrası çalıştır
config = EvaluationConfig(
    test_queries=get_comprehensive_queries(),
    output_dir=f"evaluation_{version}",
    enable_ragas=True,
    enable_coherence=True
)
```

### 2. A/B Testing

```python
# Farklı prompt versiyonlarını karşılaştır
config_v1 = EvaluationConfig(test_queries=test_set, output_dir="eval_v1")
config_v2 = EvaluationConfig(test_queries=test_set, output_dir="eval_v2")
```

### 3. Performance Monitoring

```python
# Düzenli performans izleme
config = EvaluationConfig(
    test_queries=monitoring_queries,
    output_dir=f"monitoring_{date}",
    enable_ragas=True
)
```

## 🎯 Gelecek Geliştirmeler

- [ ] Batch evaluation desteği
- [ ] Custom metric ekleme
- [ ] Grafik görselleştirme
- [ ] Automated benchmarking
- [ ] Multi-language support
- [ ] Real-time evaluation API

---

Bu evaluation pipeline, multi-agent persona sisteminizin kalitesini objektif metriklerle ölçmenizi ve sürekli iyileştirmenizi sağlar. Detaylı debug bilgileri ve kapsamlı raporlama ile sistem performansınızı derinlemesine analiz edebilirsiniz. 