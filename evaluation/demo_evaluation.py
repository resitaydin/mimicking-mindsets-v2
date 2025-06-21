#!/usr/bin/env python3
"""
Demo script for the Multi-Agent Persona System Evaluation Pipeline.

This script demonstrates the evaluation pipeline with a single test query,
showing all the evaluation steps and metrics in action.
"""

import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from evaluation_pipeline import EvaluationPipeline, EvaluationConfig

def run_demo():
    """Run a demonstration of the evaluation pipeline."""
    
    print("🎭 Multi-Agent Persona System Evaluation Demo")
    print("=" * 60)
    print("This demo will evaluate the system with a single test query")
    print("and show all evaluation metrics in action.")
    print()
    
    # Check environment
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY environment variable not set!")
        print("Please set your Google API key before running the demo.")
        print("\nExample:")
        print("export GOOGLE_API_KEY='your-api-key-here'")
        return False
    
    # Demo query
    demo_query = "Türk kültürel kimliği ve modernleşme arasındaki ilişki nasıl değerlendirilmelidir?"
    
    print(f"🎯 Demo Query: {demo_query}")
    print()
    
    try:
        # Create evaluation configuration
        config = EvaluationConfig(
            test_queries=[demo_query],
            output_dir="demo_evaluation_results",
            save_detailed_results=True,
            save_summary_table=True,
            enable_ragas=True,
            enable_coherence=True
        )
        
        print("🔧 Creating evaluation pipeline...")
        pipeline = EvaluationPipeline(config)
        
        print("🚀 Starting evaluation...")
        print("-" * 60)
        
        # Run evaluation
        results = pipeline.run_evaluation()
        
        print("-" * 60)
        print("💾 Saving results...")
        pipeline.save_results()
        
        # Display demo summary
        if results:
            result = results[0]
            print(f"\n🎉 Demo Evaluation Completed Successfully!")
            print("=" * 60)
            
            print(f"📝 Query: {result.query}")
            print(f"⏰ Timestamp: {result.timestamp}")
            print()
            
            print("📊 EVALUATION METRICS:")
            print("-" * 30)
            
            if result.faithfulness_score is not None:
                print(f"  🎯 Faithfulness: {result.faithfulness_score:.3f}")
            else:
                print(f"  🎯 Faithfulness: N/A")
                
            if result.answer_relevancy_score is not None:
                print(f"  🎯 Answer Relevancy: {result.answer_relevancy_score:.3f}")
            else:
                print(f"  🎯 Answer Relevancy: N/A")
                
            if result.context_precision_score is not None:
                print(f"  🎯 Context Precision: {result.context_precision_score:.3f}")
            else:
                print(f"  🎯 Context Precision: N/A")
                
            if result.context_recall_score is not None:
                print(f"  🎯 Context Recall: {result.context_recall_score:.3f}")
            else:
                print(f"  🎯 Context Recall: N/A")
                
            if result.coherence_score is not None:
                print(f"  🧠 Coherence: {result.coherence_score:.3f}")
            else:
                print(f"  🧠 Coherence: N/A")
            
            print()
            print("📁 SYSTEM RESPONSES:")
            print("-" * 30)
            print(f"  📚 Sources Found: {len(result.sources)}")
            print(f"  🎭 Erol Güngör Response: {len(result.erol_response)} characters")
            print(f"  🎭 Cemil Meriç Response: {len(result.cemil_response)} characters")
            print(f"  🤝 Synthesized Response: {len(result.synthesized_response)} characters")
            
            if result.errors:
                print()
                print("⚠️ ERRORS:")
                print("-" * 30)
                for error in result.errors:
                    print(f"  ❌ {error}")
            else:
                print()
                print("✅ No errors encountered!")
            
            print()
            print(f"📂 Results saved to: {config.output_dir}/")
            print("   - detailed_results.json (complete evaluation data)")
            print("   - summary_table.csv (metrics summary)")
            
            print()
            print("🔍 SAMPLE RESPONSES:")
            print("-" * 30)
            
            # Show truncated responses
            erol_preview = result.erol_response[:200] + "..." if len(result.erol_response) > 200 else result.erol_response
            cemil_preview = result.cemil_response[:200] + "..." if len(result.cemil_response) > 200 else result.cemil_response
            synth_preview = result.synthesized_response[:200] + "..." if len(result.synthesized_response) > 200 else result.synthesized_response
            
            print(f"📖 Erol Güngör: {erol_preview}")
            print()
            print(f"📖 Cemil Meriç: {cemil_preview}")
            print()
            print(f"🤝 Synthesized: {synth_preview}")
            
        print()
        print("🎊 Demo completed! Check the output directory for detailed results.")
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        print("Please check your setup and try again.")
        return False

def show_demo_info():
    """Show information about what the demo does."""
    
    print("📋 DEMO INFORMATION")
    print("=" * 60)
    print("This demo will:")
    print("  1. 🎯 Send a test query to the multi-agent system")
    print("  2. 🤖 Run both Erol Güngör and Cemil Meriç agents")
    print("  3. 🤝 Generate a synthesized response")
    print("  4. 📊 Evaluate using RAGAS metrics:")
    print("     - Faithfulness (groundedness in sources)")
    print("     - Answer Relevancy (relevance to query)")
    print("     - Context Precision (quality of retrieved context)")
    print("     - Context Recall (completeness of context)")
    print("  5. 🧠 Evaluate coherence using LangChain evaluator")
    print("  6. 💾 Save detailed results and summary table")
    print("  7. 📊 Display formatted results")
    print()
    print("Expected runtime: 2-5 minutes")
    print("Required: GOOGLE_API_KEY environment variable")
    print()

def main():
    """Main function for the demo."""
    
    print("🎭 Multi-Agent Persona Evaluation Demo")
    print("=" * 50)
    
    # Show demo info
    show_demo_info()
    
    # Ask for confirmation
    response = input("Do you want to run the demo? (y/n): ").strip().lower()
    
    if response in ['y', 'yes']:
        print("\n🚀 Starting demo...")
        success = run_demo()
        
        if success:
            print("\n✨ Demo completed successfully!")
            print("You can now examine the results in the demo_evaluation_results/ directory.")
        else:
            print("\n💥 Demo failed. Please check the error messages above.")
            
    else:
        print("\n👋 Demo cancelled. Run again when you're ready!")

if __name__ == "__main__":
    main() 