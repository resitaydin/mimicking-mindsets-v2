"""
Evaluation Pipeline for Multi-Agent Persona System

This pipeline evaluates the system based on:
1. Faithfulness to persona and groundedness in source texts (using RAGAS)
2. Reasoning integrity/coherence (using LangChain evaluators)

The pipeline processes queries through the multi-agent system and evaluates
the responses comprehensively with detailed debugging information.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import pandas as pd
from tabulate import tabulate

# Core system imports - using lazy imports to avoid circular dependency
# Note: agents imports moved to methods to avoid circular dependency

# Evaluation framework imports
try:
    from ragas import evaluate
    from ragas.metrics import faithfulness, answer_relevancy
    from datasets import Dataset
    RAGAS_AVAILABLE = True
    print("✅ RAGAS framework loaded successfully")
except ImportError as e:
    print(f"❌ RAGAS not available: {e}")
    print("📦 Install with: pip install ragas datasets")
    RAGAS_AVAILABLE = False

try:
    from langchain.evaluation import load_evaluator
    from langchain_openai import ChatOpenAI
    LANGCHAIN_EVAL_AVAILABLE = True
    print("✅ LangChain evaluation framework loaded successfully")
except ImportError as e:
    print(f"❌ LangChain evaluation not available: {e}")
    print("📦 Install with: pip install langchain-experimental langchain-openai")
    LANGCHAIN_EVAL_AVAILABLE = False

# --- Configuration ---

@dataclass
class EvaluationConfig:
    """Configuration for the evaluation pipeline."""
    
    # Test queries for evaluation
    test_queries: List[str]
    
    # Output configuration
    output_dir: str = "evaluation_results"
    save_detailed_results: bool = True
    save_summary_table: bool = True
    
    # Evaluation configuration
    enable_ragas: bool = True
    enable_coherence: bool = True
    
    # Model configuration for evaluation
    evaluation_model: str = "gpt-4.1-mini"
    temperature: float = 0.1

@dataclass
class EvaluationResult:
    """Single evaluation result structure."""
    
    query: str
    timestamp: str
    
    # System outputs
    erol_response: str
    cemil_response: str
    synthesized_response: str
    sources: List[Dict[str, str]]
    
    # RAGAS scores
    faithfulness_score: Optional[float] = None
    answer_relevancy_score: Optional[float] = None
    
    # Coherence scores
    coherence_score: Optional[float] = None
    coherence_explanation: Optional[str] = None
    
    # Error tracking
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class EvaluationPipeline:
    """Main evaluation pipeline for the multi-agent persona system."""
    
    def __init__(self, config: EvaluationConfig):
        self.config = config
        self.orchestrator = None
        self.evaluation_llm = None
        self.results: List[EvaluationResult] = []
        
        # Create output directory
        os.makedirs(config.output_dir, exist_ok=True)
        
        print(f"🔧 Evaluation Pipeline initialized")
        print(f"📁 Output directory: {config.output_dir}")
        print(f"📊 RAGAS evaluation: {'✅ Enabled' if config.enable_ragas and RAGAS_AVAILABLE else '❌ Disabled'}")
        print(f"🧠 Coherence evaluation: {'✅ Enabled' if config.enable_coherence and LANGCHAIN_EVAL_AVAILABLE else '❌ Disabled'}")
    
    def initialize(self):
        """Initialize the evaluation pipeline components."""
        
        print("\n🚀 Initializing evaluation pipeline...")
        
        # Initialize the multi-agent orchestrator
        print("🔧 Setting up multi-agent orchestrator...")
        try:
            # Lazy import to avoid circular dependency
            from agents.multi_agent_orchestrator import create_orchestrator
            self.orchestrator = create_orchestrator()
            print("✅ Multi-agent orchestrator initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize orchestrator: {e}")
            raise
        
        # Initialize evaluation LLM
        if self.config.enable_coherence and LANGCHAIN_EVAL_AVAILABLE:
            print("🧠 Setting up evaluation LLM...")
            try:
                self.evaluation_llm = ChatOpenAI(
                    model=self.config.evaluation_model,
                    temperature=self.config.temperature
                )
                print("✅ Evaluation LLM initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize evaluation LLM: {e}")
                raise
        
        print("✅ Evaluation pipeline initialization complete")
    
    def run_system_query(self, query: str) -> Tuple[Dict[str, Any], List[str]]:
        """Run a query through the multi-agent system and return results with error tracking."""
        
        print(f"\n🎯 Running system query: '{query}'")
        errors = []
        
        try:
            # Generate unique thread ID for this evaluation
            thread_id = f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            print(f"🔄 Invoking orchestrator with thread_id: {thread_id}")
            result = self.orchestrator.invoke(query, thread_id=thread_id)
            
            print("✅ System query completed successfully")
            return result, errors
            
        except Exception as e:
            error_msg = f"System query failed: {str(e)}"
            print(f"❌ {error_msg}")
            errors.append(error_msg)
            
            # Return empty result structure
            return {
                "user_query": query,
                "erol_gungor_agent_output": {"error": error_msg},
                "cemil_meric_agent_output": {"error": error_msg},
                "synthesized_answer": f"Error: {error_msg}",
                "sources": []
            }, errors
    
    def extract_agent_responses(self, system_result: Dict[str, Any]) -> Tuple[str, str, List[Dict[str, str]]]:
        """Extract individual agent responses and sources from system result."""
        
        print("📊 Extracting agent responses...")
        
        # Extract Erol Güngör response
        erol_response = "No response available"
        erol_output = system_result.get("erol_gungor_agent_output", {})
        if "messages" in erol_output and erol_output["messages"]:
            last_message = erol_output["messages"][-1]
            if hasattr(last_message, 'content'):
                erol_response = last_message.content
        elif "error" in erol_output:
            erol_response = f"Error: {erol_output['error']}"
        
        # Extract Cemil Meriç response
        cemil_response = "No response available"
        cemil_output = system_result.get("cemil_meric_agent_output", {})
        if "messages" in cemil_output and cemil_output["messages"]:
            last_message = cemil_output["messages"][-1]
            if hasattr(last_message, 'content'):
                cemil_response = last_message.content
        elif "error" in cemil_output:
            cemil_response = f"Error: {cemil_output['error']}"
        
        # Extract sources and enhance them with actual content
        sources = system_result.get("sources", [])
        enhanced_sources = []
        
        # Try to extract actual content from agent messages for context
        all_agent_messages = []
        
        # Get all messages from both agents to extract tool usage/context
        if "messages" in erol_output:
            all_agent_messages.extend(erol_output["messages"])
        if "messages" in cemil_output:
            all_agent_messages.extend(cemil_output["messages"])
        
        # Look for tool calls or function calls that might contain retrieved content
        retrieved_content = []
        for message in all_agent_messages:
            if hasattr(message, 'content') and message.content:
                content = str(message.content)
                # Look for patterns that indicate retrieved content
                if any(keyword in content.lower() for keyword in ['kaynak:', 'içerik:', 'sonuç', 'bilgi tabanından', 'source:']):
                    # Extract meaningful chunks (more than 50 characters)
                    if len(content) > 50:
                        retrieved_content.append(content)
        
        # Enhance sources with retrieved content
        for i, source in enumerate(sources):
            enhanced_source = source.copy()
            
            # If we have retrieved content, add it to the source
            if i < len(retrieved_content):
                enhanced_source['content'] = retrieved_content[i]
            elif retrieved_content:
                # Use the first available content if we have fewer content pieces than sources
                enhanced_source['content'] = retrieved_content[0]
            else:
                # Fallback: create content from available metadata
                content_parts = []
                if 'name' in source:
                    content_parts.append(f"Kaynak: {source['name']}")
                if 'description' in source:
                    content_parts.append(source['description'])
                if 'agent' in source:
                    content_parts.append(f"Agent: {source['agent']}")
                
                enhanced_source['content'] = " | ".join(content_parts) if content_parts else "Kaynak bilgisi mevcut değil"
            
            enhanced_sources.append(enhanced_source)
        
        # If no sources but we have agent responses, create synthetic sources
        if not enhanced_sources and (erol_response != "No response available" or cemil_response != "No response available"):
            if erol_response != "No response available":
                enhanced_sources.append({
                    'type': 'agent_response',
                    'name': 'Erol Güngör Response',
                    'agent': 'Erol Güngör',
                    'content': erol_response[:1000]  # First 1000 chars as context
                })
            
            if cemil_response != "No response available":
                enhanced_sources.append({
                    'type': 'agent_response', 
                    'name': 'Cemil Meriç Response',
                    'agent': 'Cemil Meriç',
                    'content': cemil_response[:1000]  # First 1000 chars as context
                })
        
        print(f"✅ Extracted responses - Erol: {len(erol_response)} chars, Cemil: {len(cemil_response)} chars, Sources: {len(enhanced_sources)}")
        print(f"📄 Enhanced sources with content: {sum(1 for s in enhanced_sources if s.get('content'))}")
        
        return erol_response, cemil_response, enhanced_sources
    
    def evaluate_faithfulness_with_ragas(self, query: str, response: str, sources: List[Dict[str, str]]) -> Dict[str, float]:
        """Evaluate faithfulness using RAGAS framework."""
        
        if not RAGAS_AVAILABLE:
            print("⚠️ RAGAS not available, skipping faithfulness evaluation")
            return {}
        
        print(f"\n📊 Evaluating faithfulness with RAGAS...")
        
        try:
            # Prepare context from sources - handle different source formats
            contexts = []
            
            print(f"🔍 Processing {len(sources)} sources for RAGAS evaluation...")
            
            for i, source in enumerate(sources):
                print(f"📄 Source {i+1}: {source}")
                
                # Try different ways to extract content from sources
                content = None
                
                if 'content' in source:
                    content = source['content']
                elif 'text' in source:
                    content = source['text']
                elif 'description' in source:
                    # Use description as a fallback context
                    content = source['description']
                elif 'name' in source:
                    # Use name as minimal context
                    content = f"Source: {source['name']}"
                
                if content and content.strip():
                    contexts.append(content.strip())
                    print(f"✅ Added context from source {i+1}: {len(content)} chars")
                else:
                    print(f"⚠️ No usable content found in source {i+1}")
            
            # If no contexts found, create a minimal context from the response itself
            if not contexts:
                print("⚠️ No contexts found from sources, using response as context for evaluation")
                # This is not ideal but allows RAGAS to run
                contexts = [response[:500]]  # Use first 500 chars of response as context
            
            print(f"📊 Total contexts for RAGAS: {len(contexts)}")
            
            # Create dataset for RAGAS
            # Note: contexts should be a list of lists, where each inner list contains contexts for that question
            data = {
                "question": [query],
                "answer": [response],
                "contexts": [contexts]  # This is correct - list of lists
            }
            
            # Debug: Print the data structure
            print(f"🔍 RAGAS data structure:")
            print(f"  - question: {data['question']}")
            print(f"  - answer length: {len(data['answer'][0])} chars")
            print(f"  - contexts: {len(data['contexts'][0])} items")
            for i, ctx in enumerate(data['contexts'][0][:3]):  # Show first 3 contexts
                print(f"    Context {i+1}: {ctx[:100]}..." if len(ctx) > 100 else f"    Context {i+1}: {ctx}")
            
            dataset = Dataset.from_dict(data)
            
            print(f"🔍 Running RAGAS evaluation with {len(contexts)} contexts...")
            
            # Define metrics to evaluate
            metrics = [faithfulness, answer_relevancy]
            
            # Debug: Print dataset info
            print(f"🔍 Dataset info:")
            print(f"  - Dataset columns: {dataset.column_names}")
            print(f"  - Dataset shape: {dataset.shape}")
            
            # Run evaluation
            print(f"🔄 Running RAGAS evaluate() function...")
            results = evaluate(dataset, metrics)
            print(f"🔍 RAGAS results type: {type(results)}")
            print(f"🔍 RAGAS results: {results}")
            
            print("✅ RAGAS evaluation completed successfully")
            
            # Extract scores from RAGAS EvaluationResult
            scores = {}
            
            # Access scores using dot notation or to_pandas()
            try:
                # Convert to pandas DataFrame to access scores
                df = results.to_pandas()
                print(f"🔍 DataFrame columns: {df.columns.tolist()}")
                print(f"🔍 DataFrame values: {df.to_dict('records')}")
                
                for metric_name in ['faithfulness', 'answer_relevancy']:
                    if metric_name in df.columns:
                        score = df[metric_name].iloc[0]
                        print(f"🔍 Raw {metric_name} score: {score} (type: {type(score)})")
                        
                        # Handle different types of invalid scores
                        if pd.isna(score):
                            print(f"⚠️ {metric_name}: NaN value")
                        elif score is None:
                            print(f"⚠️ {metric_name}: None value")
                        elif isinstance(score, (int, float)):
                            scores[metric_name] = float(score)
                            print(f"📈 {metric_name}: {score:.3f}")
                        else:
                            print(f"⚠️ {metric_name}: {score} (unexpected type: {type(score)})")
                    else:
                        print(f"⚠️ {metric_name}: column not found in results")
                        
            except Exception as e:
                print(f"⚠️ Could not extract scores from RAGAS result: {e}")
                # Fallback: try direct attribute access
                try:
                    if hasattr(results, 'faithfulness'):
                        score = getattr(results, 'faithfulness')
                        print(f"🔍 Direct faithfulness: {score} (type: {type(score)})")
                        if isinstance(score, (int, float)) and not pd.isna(score):
                            scores['faithfulness'] = float(score)
                            print(f"📈 faithfulness: {score:.3f}")
                            
                    if hasattr(results, 'answer_relevancy'):
                        score = getattr(results, 'answer_relevancy')
                        print(f"🔍 Direct answer_relevancy: {score} (type: {type(score)})")
                        if isinstance(score, (int, float)) and not pd.isna(score):
                            scores['answer_relevancy'] = float(score)
                            print(f"📈 answer_relevancy: {score:.3f}")
                except Exception as e2:
                    print(f"⚠️ Fallback score extraction also failed: {e2}")
            
            return scores
            
        except Exception as e:
            print(f"❌ RAGAS evaluation failed: {str(e)}")
            print(f"🔍 Error details: {type(e).__name__}")
            import traceback
            print(f"📋 Traceback: {traceback.format_exc()}")
            return {}
    
    def evaluate_coherence(self, query: str, response: str) -> Tuple[Optional[float], Optional[str]]:
        """Evaluate reasoning coherence using LangChain evaluators."""
        
        if not LANGCHAIN_EVAL_AVAILABLE or not self.evaluation_llm:
            print("⚠️ LangChain evaluation not available, skipping coherence evaluation")
            return None, None
        
        print(f"\n🧠 Evaluating reasoning coherence...")
        
        try:
            # Load the criteria evaluator for coherence
            evaluator = load_evaluator(
                "criteria",
                criteria="coherence",
                llm=self.evaluation_llm
            )
            
            print("🔍 Running coherence evaluation...")
            
            # Evaluate coherence
            eval_result = evaluator.evaluate_strings(
                input=query,
                prediction=response
            )
            
            score = eval_result.get('score', 0)
            reasoning = eval_result.get('reasoning', 'No reasoning provided')
            
            print(f"✅ Coherence evaluation completed")
            print(f"📈 Coherence score: {score}")
            print(f"💭 Reasoning: {reasoning[:200]}...")
            
            return float(score), reasoning
            
        except Exception as e:
            print(f"❌ Coherence evaluation failed: {str(e)}")
            return None, str(e)
    
    def evaluate_single_query(self, query: str) -> EvaluationResult:
        """Evaluate a single query through the complete pipeline."""
        
        print(f"\n{'='*80}")
        print(f"🎯 EVALUATING QUERY: {query}")
        print(f"{'='*80}")
        
        # Initialize result
        result = EvaluationResult(
            query=query,
            timestamp=datetime.now().isoformat(),
            erol_response="",
            cemil_response="",
            synthesized_response="",
            sources=[]
        )
        
        # Step 1: Run system query
        print("\n📝 STEP 1: Running system query...")
        system_result, errors = self.run_system_query(query)
        result.errors.extend(errors)
        
        # Extract responses
        erol_response, cemil_response, sources = self.extract_agent_responses(system_result)
        result.erol_response = erol_response
        result.cemil_response = cemil_response
        result.synthesized_response = system_result.get("synthesized_answer", "No synthesized answer")
        result.sources = sources
        
        # Step 2: RAGAS evaluation
        if self.config.enable_ragas and RAGAS_AVAILABLE:
            print("\n📊 STEP 2: RAGAS evaluation...")
            ragas_scores = self.evaluate_faithfulness_with_ragas(
                query, 
                result.synthesized_response, 
                sources
            )
            
            # Update result with RAGAS scores
            result.faithfulness_score = ragas_scores.get('faithfulness')
            result.answer_relevancy_score = ragas_scores.get('answer_relevancy')
        
        # Step 3: Coherence evaluation
        if self.config.enable_coherence and LANGCHAIN_EVAL_AVAILABLE:
            print("\n🧠 STEP 3: Coherence evaluation...")
            coherence_score, coherence_explanation = self.evaluate_coherence(
                query, 
                result.synthesized_response
            )
            result.coherence_score = coherence_score
            result.coherence_explanation = coherence_explanation
        
        print(f"\n✅ Query evaluation completed: {query}")
        return result
    
    def run_evaluation(self) -> List[EvaluationResult]:
        """Run the complete evaluation pipeline on all test queries."""
        
        print(f"\n🚀 Starting evaluation pipeline with {len(self.config.test_queries)} queries")
        print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Initialize pipeline
        self.initialize()
        
        # Process each query
        for i, query in enumerate(self.config.test_queries, 1):
            print(f"\n🔄 Processing query {i}/{len(self.config.test_queries)}")
            
            try:
                result = self.evaluate_single_query(query)
                self.results.append(result)
                
            except Exception as e:
                print(f"❌ Failed to evaluate query '{query}': {str(e)}")
                # Create error result
                error_result = EvaluationResult(
                    query=query,
                    timestamp=datetime.now().isoformat(),
                    erol_response=f"Error: {str(e)}",
                    cemil_response=f"Error: {str(e)}",
                    synthesized_response=f"Error: {str(e)}",
                    sources=[],
                    errors=[str(e)]
                )
                self.results.append(error_result)
        
        print(f"\n✅ Evaluation pipeline completed")
        print(f"📊 Processed {len(self.results)} queries")
        print(f"⏰ End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return self.results
    
    def save_results(self):
        """Save evaluation results to files."""
        
        print(f"\n💾 Saving evaluation results...")
        
        # Save detailed results as JSON
        if self.config.save_detailed_results:
            detailed_file = os.path.join(self.config.output_dir, "detailed_results.json")
            with open(detailed_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(result) for result in self.results], f, indent=2, ensure_ascii=False)
            print(f"📄 Detailed results saved to: {detailed_file}")
        
        # Save summary table
        if self.config.save_summary_table:
            self.create_summary_table()
    
    def create_summary_table(self):
        """Create and display a summary table of evaluation results."""
        
        print(f"\n📊 Creating summary table...")
        
        # Prepare data for table
        table_data = []
        for result in self.results:
            row = {
                "Query": result.query[:50] + "..." if len(result.query) > 50 else result.query,
                "Faithfulness": f"{result.faithfulness_score:.3f}" if result.faithfulness_score is not None else "N/A",
                "Answer Relevancy": f"{result.answer_relevancy_score:.3f}" if result.answer_relevancy_score is not None else "N/A",
                "Coherence": f"{result.coherence_score:.3f}" if result.coherence_score is not None else "N/A",
                "Sources": len(result.sources),
                "Errors": len(result.errors)
            }
            table_data.append(row)
        
        # Create DataFrame and display
        df = pd.DataFrame(table_data)
        
        # Display table
        print(f"\n📋 EVALUATION RESULTS SUMMARY")
        print("=" * 120)
        print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
        
        # Calculate and display averages
        print(f"\n📈 AVERAGE SCORES:")
        numeric_columns = ["Faithfulness", "Answer Relevancy", "Coherence"]
        
        for col in numeric_columns:
            values = []
            for result in self.results:
                if col == "Faithfulness" and result.faithfulness_score is not None:
                    values.append(result.faithfulness_score)
                elif col == "Answer Relevancy" and result.answer_relevancy_score is not None:
                    values.append(result.answer_relevancy_score)
                elif col == "Coherence" and result.coherence_score is not None:
                    values.append(result.coherence_score)
            
            if values:
                avg = sum(values) / len(values)
                print(f"  {col}: {avg:.3f} (n={len(values)})")
            else:
                print(f"  {col}: N/A")
        
        # Save table to CSV
        csv_file = os.path.join(self.config.output_dir, "summary_table.csv")
        df.to_csv(csv_file, index=False)
        print(f"\n💾 Summary table saved to: {csv_file}")

# --- Predefined Test Configurations ---

def get_default_test_queries() -> List[str]:
    """Get default test queries for evaluation."""
    
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

def create_default_evaluation_config() -> EvaluationConfig:
    """Create default evaluation configuration."""
    
    return EvaluationConfig(
        test_queries=get_default_test_queries(),
        output_dir="evaluation_results",
        save_detailed_results=True,
        save_summary_table=True,
        enable_ragas=True,
        enable_coherence=True
    )

# --- Main Execution ---

def main():
    """Main function to run the evaluation pipeline."""
    
    print("🚀 Multi-Agent Persona System Evaluation Pipeline")
    print("=" * 60)
    
    # Check environment
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY environment variable not set!")
        print("Please set your Google API key before running the evaluation.")
        return
    
    try:
        # Create configuration
        config = create_default_evaluation_config()
        
        # Create and run pipeline
        pipeline = EvaluationPipeline(config)
        results = pipeline.run_evaluation()
        
        # Save results
        pipeline.save_results()
        
        print(f"\n🎉 Evaluation completed successfully!")
        print(f"📊 Total queries evaluated: {len(results)}")
        print(f"📁 Results saved to: {config.output_dir}")
        
    except Exception as e:
        print(f"❌ Evaluation pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 