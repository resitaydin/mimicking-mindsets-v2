#!/usr/bin/env python3
"""
Evaluation script for the Multi-Agent Persona System.

This script runs a comprehensive evaluation of the system using 30 test queries
covering various themes related to Turkish cultural identity, modernization,
and intellectual responsibility.
"""

import os
import sys
from typing import List

# Add current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Use absolute import to avoid circular dependency
if __name__ == "__main__":
    from evaluation_pipeline import EvaluationPipeline, EvaluationConfig
else:
    from evaluation.evaluation_pipeline import EvaluationPipeline, EvaluationConfig

def get_comprehensive_queries() -> List[str]:
    """Comprehensive set covering all major themes."""
    return [
        "Türk kültürel kimliği hakkında ne düşünüyorsunuz?",
        "Modernleşme ve gelenek arasındaki gerilim nasıl çözülebilir?",
        "Batılılaşma sürecinin Türk toplumuna etkileri nelerdir?",
        "Aydın sorumluluğu ve toplumsal değişim arasındaki ilişki nedir?",
        "Teknolojinin günümüz toplumsal yapısına etkilerini nasıl değerlendiriyorsunuz?",
        "Doğu ve Batı medeniyetleri arasında nasıl bir sentez kurulabilir?",
        "Milli kültürün korunması ve çağdaşlaşma nasıl dengelenmelidir?",
        "Entelektüel özgürlük ve toplumsal sorumluluk arasındaki ilişki nedir?",
        "Eğitim sisteminin toplumsal dönüşümdeki rolü nasıl değerlendirilmelidir?",
        "Küreselleşmenin yerel kültürler üzerindeki etkisi nedir?",
        "Sanat ve edebiyatın toplumsal bilinç oluşturmadaki işlevi nedir?",
        "Geleneksel değerlerin modern hayatta yaşatılması mümkün müdür?",
        "Bilim ve tekniğin manevi değerlerle ilişkisi nasıl kurulmalıdır?",
        "Toplumsal adaletsizliklere karşı aydının tavrı nasıl olmalıdır?",
        "Dil ve kültür arasındaki bağın önemi nedir?",
        "Felsefe ve bilim arasındaki ilişkiyi nasıl değerlendiriyorsunuz?",
        "Sosyal psikoloji ve sosyal bilimler arasındaki ilişkiyi nasıl değerlendiriyorsunuz?",
        "Psikolojinin toplumsal değişim üzerindeki etkisi nedir?",
        "Tarihsel mirasın günümüze aktarılmasında hangi yöntemler kullanılmalıdır?",
        "Bireysel özgürlük ve toplumsal düzen arasındaki denge nasıl kurulmalıdır?",
        "Medya ve iletişim araçlarının kültürel değişimdeki rolü nedir?",
        "Gençliğin toplumsal dönüşümdeki sorumluluğu nasıl tanımlanmalıdır?",
        "Çok kültürlülük ve milli kimlik arasında nasıl bir denge kurulabilir?",
        "Günümüz Türkiye'sinde var olan göçmen sorunları hakkında ne düşünüyorsunuz?",
        "Türkiye'nin dış politika stratejisi hakkında ne düşünüyorsunuz?",
        "Global küresel ısınma hakkında ne düşünüyorsunuz?",
        "Türkiye'deki mevcut eğitim sistemini nasıl değerlendiriyorsunuz?",
        "Sosyal Medya bağımlılığı hakkında ne düşünüyorsunuz?",
        "Türkiye'nin jeopolitik konumunun savaşlar üzerindeki etkisi nedir?",
        "Osmanlı İmparatorluğu'nun izlediği denge politikasının avantaj ve dezavantajları nelerdir?"
    ]

def create_evaluation_config() -> EvaluationConfig:
    """Create comprehensive evaluation configuration."""
    return EvaluationConfig(
        test_queries=get_comprehensive_queries(),
        output_dir="evaluation_results",
        enable_ragas=True,
        enable_coherence=True
    )

def run_evaluation():
    """Run comprehensive evaluation."""
    print("🎯 Running Comprehensive Evaluation (30 queries)")
    print("=" * 60)
    print("This evaluation will test the multi-agent system with 30 diverse queries")
    print("covering Turkish cultural identity, modernization, and intellectual themes.")
    print("=" * 60)
    
    config = create_evaluation_config()
    pipeline = EvaluationPipeline(config)
    
    results = pipeline.run_evaluation()
    pipeline.save_results()
    
    print(f"\n✅ Comprehensive evaluation completed!")
    print(f"📊 Results saved to: {config.output_dir}")
    print(f"📄 Check detailed_results.json and summary_table.csv for full results")

def main():
    """Main function."""
    
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key before running the evaluation.")
        print("\nExample:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return
    
    print("🤖 Multi-Agent Persona System Evaluation")
    print("This script evaluates the system using RAGAS and LangChain evaluators with GPT-4.1-mini as judge.")
    print()
    
    try:
        run_evaluation()
    except KeyboardInterrupt:
        print("\n\n⚠️ Evaluation interrupted by user.")
    except Exception as e:
        print(f"\n❌ Evaluation failed: {str(e)}")
        print("Please check your setup and try again.")

if __name__ == "__main__":
    main() 