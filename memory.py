from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class ConversationTurn:
    """Represents a single turn in the conversation."""
    user_query: str
    orchestrator_response: str
    persona_responses: Dict[str, str]  # persona_name -> response
    timestamp: datetime
    context_used: List[str]  # List of contexts/sources used
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "user_query": self.user_query,
            "orchestrator_response": self.orchestrator_response,
            "persona_responses": self.persona_responses,
            "timestamp": self.timestamp.isoformat(),
            "context_used": self.context_used
        }


class ConversationMemory:
    """Manages conversation history and context continuity."""
    
    def __init__(self, max_history_length: int = 10):
        self.conversation_history: List[ConversationTurn] = []
        self.max_history_length = max_history_length
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def add_turn(
        self, 
        user_query: str, 
        orchestrator_response: str, 
        persona_responses: Dict[str, str],
        context_used: List[str] = None
    ) -> None:
        """Add a new conversation turn to memory."""
        turn = ConversationTurn(
            user_query=user_query,
            orchestrator_response=orchestrator_response,
            persona_responses=persona_responses,
            timestamp=datetime.now(),
            context_used=context_used or []
        )
        
        self.conversation_history.append(turn)
        
        # Maintain maximum history length
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history.pop(0)
    
    def get_recent_context(self, num_turns: int = 3) -> str:
        """Get recent conversation context for LLM input."""
        if not self.conversation_history:
            return ""
        
        recent_turns = self.conversation_history[-num_turns:]
        context_parts = []
        
        for i, turn in enumerate(recent_turns):
            context_parts.append(f"Turn {len(self.conversation_history) - len(recent_turns) + i + 1}:")
            context_parts.append(f"User: {turn.user_query}")
            context_parts.append(f"Assistant: {turn.orchestrator_response}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the entire conversation."""
        if not self.conversation_history:
            return "No conversation history available."
        
        total_turns = len(self.conversation_history)
        topics_discussed = set()
        
        for turn in self.conversation_history:
            # Simple topic extraction - could be enhanced with NLP
            query_words = turn.user_query.lower().split()
            topics_discussed.update([word for word in query_words if len(word) > 4])
        
        return f"Conversation Summary:\n- Total turns: {total_turns}\n- Key topics: {', '.join(list(topics_discussed)[:10])}\n- Session ID: {self.session_id}"
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def export_history(self, filepath: str) -> None:
        """Export conversation history to JSON file."""
        export_data = {
            "session_id": self.session_id,
            "total_turns": len(self.conversation_history),
            "conversation": [turn.to_dict() for turn in self.conversation_history]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False) 