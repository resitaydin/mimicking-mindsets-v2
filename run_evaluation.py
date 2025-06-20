#!/usr/bin/env python3
"""
Simple script to run the evaluation pipeline for the Multi-Agent Persona System.

This script demonstrates how to use the evaluation pipeline with custom configurations
and provides an easy way to run evaluations with different test scenarios.
"""

import os
import sys
from typing import List

# Add current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from evaluation_pipeline import EvaluationPipeline, EvaluationConfig

# --- Test Scenarios ---

def get_cultural_identity_queries() -> List[str]:
    """Queries focused on cultural identity analysis."""
    return [
        "Türk kültürel kimliği nasıl şekillenmiştir?",
        "Doğu ve Batı sentezi Türk düşüncesinde nasıl gerçekleşmiştir?",
        "Kültürel değişim ve süreklilik arasındaki denge nasıl kurulmalıdır?"
    ]

def get_modernization_queries() -> List[str]:
    """Queries focused on modernization and tradition."""
    return [
        "Modernleşme sürecinde hangi değerler korunmalıdır?",
        "Teknolojik ilerleme ve manevi değerler arasındaki ilişki nedir?",
        "Batılılaşma ile Batıcılık arasındaki fark nedir?"
    ]

def get_intellectual_responsibility_queries() -> List[str]:
    """Queries focused on intellectual responsibility."""
    return [
        "Aydının toplum karşısındaki sorumluluğu nedir?",
        "Entelektüel özgürlük ve toplumsal sorumluluk nasıl dengelenmelidir?",
        "Düşünce dünyasının toplumsal dönüşümdeki rolü nedir?"
    ]

def get_comprehensive_queries() -> List[str]:
    """Comprehensive set covering all major themes."""
    return (
        get_cultural_identity_queries() + 
        get_modernization_queries() + 
        get_intellectual_responsibility_queries()
    )

# --- Evaluation Configurations ---

def create_quick_evaluation_config() -> EvaluationConfig:
    """Quick evaluation with fewer queries for testing."""
    return EvaluationConfig(
        test_queries=[
            "Türk kültürel kimliği hakkında ne düşünüyorsunuz?",
            "Modernleşme ve gelenek arasındaki denge nasıl kurulmalıdır?"
        ],
        output_dir="evaluation_results_quick",
        enable_ragas=True,
        enable_coherence=True
    )

def create_cultural_focus_config() -> EvaluationConfig:
    """Evaluation focused on cultural identity themes."""
    return EvaluationConfig(
        test_queries=get_cultural_identity_queries(),
        output_dir="evaluation_results_cultural",
        enable_ragas=True,
        enable_coherence=True
    )

def create_comprehensive_config() -> EvaluationConfig:
    """Comprehensive evaluation with all test categories."""
    return EvaluationConfig(
        test_queries=get_comprehensive_queries(),
        output_dir="evaluation_results_comprehensive",
        enable_ragas=True,
        enable_coherence=True
    )

def create_ragas_only_config() -> EvaluationConfig:
    """Evaluation using only RAGAS metrics (faster)."""
    return EvaluationConfig(
        test_queries=get_comprehensive_queries(),
        output_dir="evaluation_results_ragas_only",
        enable_ragas=True,
        enable_coherence=False  # Disable coherence evaluation for speed
    )

# --- Main Execution Functions ---

def run_quick_evaluation():
    """Run a quick evaluation for testing purposes."""
    print("🚀 Running Quick Evaluation (2 queries)")
    print("=" * 50)
    
    config = create_quick_evaluation_config()
    pipeline = EvaluationPipeline(config)
    
    results = pipeline.run_evaluation()
    pipeline.save_results()
    
    print(f"\n✅ Quick evaluation completed!")
    print(f"📊 Results saved to: {config.output_dir}")

def run_cultural_evaluation():
    """Run evaluation focused on cultural identity themes."""
    print("🏛️ Running Cultural Identity Evaluation")
    print("=" * 50)
    
    config = create_cultural_focus_config()
    pipeline = EvaluationPipeline(config)
    
    results = pipeline.run_evaluation()
    pipeline.save_results()
    
    print(f"\n✅ Cultural evaluation completed!")
    print(f"📊 Results saved to: {config.output_dir}")

def run_comprehensive_evaluation():
    """Run comprehensive evaluation with all test categories."""
    print("🎯 Running Comprehensive Evaluation")
    print("=" * 50)
    
    config = create_comprehensive_config()
    pipeline = EvaluationPipeline(config)
    
    results = pipeline.run_evaluation()
    pipeline.save_results()
    
    print(f"\n✅ Comprehensive evaluation completed!")
    print(f"📊 Results saved to: {config.output_dir}")

def run_ragas_only_evaluation():
    """Run evaluation using only RAGAS metrics (faster)."""
    print("📊 Running RAGAS-Only Evaluation (Faster)")
    print("=" * 50)
    
    config = create_ragas_only_config()
    pipeline = EvaluationPipeline(config)
    
    results = pipeline.run_evaluation()
    pipeline.save_results()
    
    print(f"\n✅ RAGAS-only evaluation completed!")
    print(f"📊 Results saved to: {config.output_dir}")

def run_custom_evaluation(queries: List[str], output_dir: str = "evaluation_results_custom"):
    """Run evaluation with custom queries."""
    print(f"🔧 Running Custom Evaluation ({len(queries)} queries)")
    print("=" * 50)
    
    config = EvaluationConfig(
        test_queries=queries,
        output_dir=output_dir,
        enable_ragas=True,
        enable_coherence=True
    )
    
    pipeline = EvaluationPipeline(config)
    results = pipeline.run_evaluation()
    pipeline.save_results()
    
    print(f"\n✅ Custom evaluation completed!")
    print(f"📊 Results saved to: {output_dir}")

# --- Interactive Menu ---

def show_menu():
    """Display the evaluation options menu."""
    print("\n" + "=" * 60)
    print("🎯 Multi-Agent Persona System Evaluation Menu")
    print("=" * 60)
    print("1. Quick Evaluation (2 queries - for testing)")
    print("2. Cultural Identity Focus (3 queries)")
    print("3. Comprehensive Evaluation (9 queries)")
    print("4. RAGAS-Only Evaluation (faster, no coherence)")
    print("5. Custom Evaluation (enter your own queries)")
    print("6. Exit")
    print("=" * 60)

def get_user_choice() -> str:
    """Get user's menu choice."""
    while True:
        choice = input("\nEnter your choice (1-6): ").strip()
        if choice in ['1', '2', '3', '4', '5', '6']:
            return choice
        print("❌ Invalid choice. Please enter 1-6.")

def handle_custom_evaluation():
    """Handle custom evaluation input."""
    print("\n🔧 Custom Evaluation Setup")
    print("-" * 30)
    
    queries = []
    print("Enter your queries (press Enter twice to finish):")
    
    while True:
        query = input(f"Query {len(queries) + 1}: ").strip()
        if not query:
            if queries:
                break
            else:
                print("Please enter at least one query.")
                continue
        queries.append(query)
    
    if queries:
        output_dir = input("Output directory (default: evaluation_results_custom): ").strip()
        if not output_dir:
            output_dir = "evaluation_results_custom"
        
        run_custom_evaluation(queries, output_dir)
    else:
        print("❌ No queries provided.")

def main():
    """Main interactive function."""
    
    # Check environment
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY environment variable not set!")
        print("Please set your Google API key before running the evaluation.")
        print("\nExample:")
        print("export GOOGLE_API_KEY='your-api-key-here'")
        return
    
    print("🤖 Multi-Agent Persona System Evaluation")
    print("This tool evaluates the system using RAGAS and LangChain evaluators.")
    
    while True:
        show_menu()
        choice = get_user_choice()
        
        try:
            if choice == '1':
                run_quick_evaluation()
            elif choice == '2':
                run_cultural_evaluation()
            elif choice == '3':
                run_comprehensive_evaluation()
            elif choice == '4':
                run_ragas_only_evaluation()
            elif choice == '5':
                handle_custom_evaluation()
            elif choice == '6':
                print("\n👋 Goodbye!")
                break
                
        except KeyboardInterrupt:
            print("\n\n⚠️ Evaluation interrupted by user.")
            break
        except Exception as e:
            print(f"\n❌ Evaluation failed: {str(e)}")
            print("Please check your setup and try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 