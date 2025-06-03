import asyncio
from typing import List, Dict, Any, Set
import google.generativeai as genai
from memory import ConversationMemory
from persona_agents import BasePersonaAgent


class OrchestratorAgent:
    """Central coordination agent that manages persona agents and synthesizes responses."""
    
    def __init__(self, persona_agents: List[BasePersonaAgent], gemini_api_key: str):
        self.persona_agents = {agent.name: agent for agent in persona_agents}
        self.memory = ConversationMemory()
        
        # Initialize Gemini for orchestrator
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def analyze_query_relevance(self, query: str) -> Dict[str, float]:
        """Analyze which persona agents are most relevant for the given query."""
        
        # Create persona descriptions for analysis
        persona_descriptions = {}
        for name, agent in self.persona_agents.items():
            persona_descriptions[name] = agent.persona_description
        
        analysis_prompt = f"""
        Analyze the following user query and determine the relevance of each persona for answering it.
        
        User Query: "{query}"
        
        Available Personas:
        1. Cemil Meriç - Turkish intellectual, translator, essayist. Expert in Eastern/Western philosophy, French literature, cultural synthesis, civilization studies.
        2. Erol Güngör - Turkish psychologist, sociologist. Expert in social psychology, personality psychology, Turkish cultural psychology, social change.
        
        For each persona, provide a relevance score from 0.0 to 1.0 (where 1.0 is most relevant) based on how well their expertise matches the query.
        
        Consider:
        - The subject matter of the query
        - The intellectual perspective needed
        - The type of knowledge required
        - Historical vs contemporary aspects
        
        Respond ONLY in this exact format:
        Cemil Meriç: 0.X
        Erol Güngör: 0.X
        """
        
        try:
            response = self.model.generate_content(analysis_prompt)
            relevance_scores = {}
            
            # Parse the response
            lines = response.text.strip().split('\n')
            for line in lines:
                if ':' in line:
                    name, score_str = line.split(':', 1)
                    name = name.strip()
                    try:
                        score = float(score_str.strip())
                        relevance_scores[name] = max(0.0, min(1.0, score))  # Clamp between 0 and 1
                    except ValueError:
                        continue
            
            # Ensure all personas have scores
            for persona_name in self.persona_agents.keys():
                if persona_name not in relevance_scores:
                    relevance_scores[persona_name] = 0.5  # Default neutral score
            
            return relevance_scores
            
        except Exception as e:
            print(f"Error analyzing query relevance: {e}")
            # Default: moderate relevance for all agents
            return {name: 0.6 for name in self.persona_agents.keys()}
    
    def determine_active_agents(self, relevance_scores: Dict[str, float], threshold: float = 0.3) -> List[str]:
        """Determine which agents should process the query based on relevance scores."""
        active_agents = []
        
        # Sort by relevance score
        sorted_agents = sorted(relevance_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Always include the most relevant agent
        if sorted_agents:
            active_agents.append(sorted_agents[0][0])
        
        # Include additional agents above threshold
        for name, score in sorted_agents[1:]:
            if score >= threshold:
                active_agents.append(name)
        
        return active_agents
    
    async def coordinate_persona_responses(self, query: str, active_agent_names: List[str]) -> Dict[str, Any]:
        """Coordinate responses from multiple persona agents concurrently."""
        conversation_context = self.memory.get_recent_context()
        
        # Create tasks for concurrent execution
        tasks = []
        for agent_name in active_agent_names:
            if agent_name in self.persona_agents:
                agent = self.persona_agents[agent_name]
                task = agent.process_query(query, conversation_context)
                tasks.append((agent_name, task))
        
        # Execute all tasks concurrently
        persona_responses = {}
        if tasks:
            results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
            
            for (agent_name, _), result in zip(tasks, results):
                if isinstance(result, Exception):
                    print(f"Error from {agent_name}: {result}")
                    persona_responses[agent_name] = {
                        "persona": agent_name,
                        "response": f"I apologize, but I encountered an error while processing your query.",
                        "error": str(result)
                    }
                else:
                    persona_responses[agent_name] = result
        
        return persona_responses
    
    def synthesize_final_response(
        self, 
        query: str, 
        persona_responses: Dict[str, Any], 
        relevance_scores: Dict[str, float]
    ) -> str:
        """Synthesize a coherent final response from multiple persona responses."""
        
        if not persona_responses:
            return "I apologize, but I was unable to generate a response from any of the intellectual perspectives available."
        
        # Prepare context for synthesis
        responses_text = ""
        sources_mentioned = set()
        
        for agent_name, response_data in persona_responses.items():
            relevance = relevance_scores.get(agent_name, 0.5)
            responses_text += f"\n\n{agent_name} (Relevance: {relevance:.1f}):\n{response_data['response']}\n"
            
            # Collect sources
            if 'sources_used' in response_data:
                sources_mentioned.update(response_data['sources_used'])
        
        conversation_context = self.memory.get_recent_context()
        
        synthesis_prompt = f"""
        You are an intelligent orchestrator synthesizing insights from multiple Turkish intellectual perspectives.
        
        Original User Query: "{query}"
        
        {f"Recent Conversation Context:{conversation_context}" if conversation_context else ""}
        
        Responses from Different Perspectives:
        {responses_text}
        
        Your task is to synthesize these perspectives into a coherent, comprehensive response that:
        
        1. **Integrates complementary insights** - Combine related ideas from different thinkers
        2. **Highlights contrasting viewpoints** - Where perspectives differ, present both sides thoughtfully
        3. **Maintains intellectual authenticity** - Preserve the unique voice and approach of each thinker
        4. **Provides balanced coverage** - Give appropriate weight based on relevance to the query
        5. **Creates coherent flow** - Organize the synthesis logically and readably
        6. **Adds connecting insights** - Draw meaningful connections between different perspectives when appropriate
        7. **Acknowledges limitations** - Note when information is incomplete or perspectives are limited
        
        Structure your response to be engaging and informative, showing how these different intellectual traditions can complement each other in addressing the user's question.
        
        Begin your response directly - do not use meta-commentary about the synthesis process.
        
        Synthesized Response:
        """
        
        try:
            response = self.model.generate_content(synthesis_prompt)
            synthesized = response.text.strip()
            
            # Add source attribution if relevant sources were found
            if sources_mentioned:
                source_list = ", ".join(sorted(sources_mentioned)[:5])  # Limit to first 5 sources
                synthesized += f"\n\n*Sources referenced: {source_list}*"
            
            return synthesized
            
        except Exception as e:
            print(f"Error synthesizing response: {e}")
            # Fallback: return the most relevant single response
            if persona_responses:
                best_agent = max(relevance_scores.items(), key=lambda x: x[1])[0]
                if best_agent in persona_responses:
                    return f"Response from {best_agent}:\n\n{persona_responses[best_agent]['response']}"
            
            return "I encountered an error while synthesizing the perspectives. Please try rephrasing your question."
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Main method to process a user query through the entire orchestration pipeline."""
        print(f"\n🤔 Orchestrator: Analyzing query - '{query}'")
        
        # Step 1: Analyze query relevance
        relevance_scores = self.analyze_query_relevance(query)
        print(f"📊 Relevance scores: {relevance_scores}")
        
        # Step 2: Determine active agents
        active_agents = self.determine_active_agents(relevance_scores)
        print(f"🎯 Active agents: {active_agents}")
        
        # Step 3: Coordinate persona responses
        print(f"⚡ Coordinating responses from {len(active_agents)} agents...")
        persona_responses = await self.coordinate_persona_responses(query, active_agents)
        
        # Step 4: Synthesize final response
        print(f"🔄 Synthesizing final response...")
        final_response = self.synthesize_final_response(query, persona_responses, relevance_scores)
        
        # Step 5: Store in memory
        persona_response_texts = {name: data.get('response', '') for name, data in persona_responses.items()}
        sources_used = []
        for data in persona_responses.values():
            sources_used.extend(data.get('sources_used', []))
        
        self.memory.add_turn(
            user_query=query,
            orchestrator_response=final_response,
            persona_responses=persona_response_texts,
            context_used=list(set(sources_used))
        )
        
        print(f"✅ Response generated and stored in memory")
        
        # Return both individual responses and synthesized response
        return {
            "synthesized_response": final_response,
            "persona_responses": persona_responses,
            "relevance_scores": relevance_scores,
            "active_agents": active_agents
        }
    
    def get_conversation_summary(self) -> str:
        """Get conversation summary from memory."""
        return self.memory.get_conversation_summary()
    
    def clear_conversation_history(self) -> None:
        """Clear conversation history."""
        self.memory.clear_history()
        print("🗑️ Conversation history cleared")
    
    def export_conversation_history(self, filepath: str) -> None:
        """Export conversation history to file."""
        self.memory.export_history(filepath)
        print(f"💾 Conversation history exported to {filepath}") 