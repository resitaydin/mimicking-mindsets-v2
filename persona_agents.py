import os
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import asyncio

import google.generativeai as genai
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import requests
from urllib.parse import quote

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


class WebSearchTool:
    """Simple web search tool for retrieving up-to-date information."""
    
    def __init__(self):
        # Using DuckDuckGo API as a simple web search
        self.base_url = "https://api.duckduckgo.com/"
    
    def search(self, query: str, max_results: int = 3) -> List[Dict[str, str]]:
        """Perform web search and return results."""
        try:
            # Simple DuckDuckGo instant answer API
            url = f"{self.base_url}?q={quote(query)}&format=json&no_html=1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # Extract abstract if available
                if data.get('Abstract'):
                    results.append({
                        "title": data.get('AbstractSource', 'Web Search'),
                        "content": data.get('Abstract', ''),
                        "url": data.get('AbstractURL', '')
                    })
                
                # Extract related topics
                for topic in data.get('RelatedTopics', [])[:max_results-1]:
                    if isinstance(topic, dict) and topic.get('Text'):
                        results.append({
                            "title": topic.get('Result', 'Related Topic'),
                            "content": topic.get('Text', ''),
                            "url": topic.get('FirstURL', '')
                        })
                
                return results[:max_results]
        except Exception as e:
            print(f"Web search error: {e}")
        
        return []


class BasePersonaAgent(ABC):
    """Base class for persona agents."""
    
    def __init__(
        self,
        name: str,
        qdrant_collection: str,
        persona_description: str,
        qdrant_client: QdrantClient,
        embedding_model: SentenceTransformer,
        gemini_api_key: str
    ):
        self.name = name
        self.qdrant_collection = qdrant_collection
        self.persona_description = persona_description
        self.qdrant_client = qdrant_client
        self.embedding_model = embedding_model
        self.web_search = WebSearchTool()
        
        # Initialize Gemini
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def retrieve_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge from the persona's Qdrant collection."""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0]
            
            # Perform semantic search
            search_results = self.qdrant_client.search(
                collection_name=self.qdrant_collection,
                query_vector=query_embedding.tolist(),
                limit=limit,
                with_payload=True
            )
            
            return [
                {
                    "text": result.payload.get("text", ""),
                    "source": result.payload.get("source", ""),
                    "score": result.score,
                    "chunk_index": result.payload.get("chunk_index", 0)
                }
                for result in search_results
            ]
        except Exception as e:
            print(f"Error retrieving knowledge for {self.name}: {e}")
            return []
    
    def enhance_query(self, original_query: str) -> str:
        """Enhance/rephrase the query to better suit the persona's knowledge base."""
        enhancement_prompt = f"""
        Sen {self.name}'sin. Kullanıcının sorgusunu göz önünde bulundurarak, orijinal amacı koruyarak bilgi tabanından daha alakalı bilgi almak için sorguyu yeniden ifade et veya geliştir.
        
        Orijinal sorgu: "{original_query}"
        
        Geliştirilmiş sorgu (sadece geliştirilmiş sorgu ile yanıt ver, açıklama yapma):
        """
        
        try:
            response = self.model.generate_content(enhancement_prompt)
            enhanced = response.text.strip()
            return enhanced if enhanced else original_query
        except Exception as e:
            print(f"Error enhancing query for {self.name}: {e}")
            return original_query
    
    def should_use_web_search(self, query: str, retrieved_context: List[Dict[str, Any]]) -> bool:
        """Determine if web search is needed based on the query and retrieved context."""
        # Simple heuristics - could be made more sophisticated
        current_year_keywords = ["2024", "2025", "en son", "güncel", "şu an", "bugün", "son zamanlarda"]
        has_temporal_keywords = any(keyword in query.lower() for keyword in current_year_keywords)
        
        # If we have very few relevant results or the query seems to require current information
        insufficient_context = len(retrieved_context) < 2 or all(result["score"] < 0.7 for result in retrieved_context)
        
        return has_temporal_keywords or insufficient_context
    
    @abstractmethod
    def get_persona_prompt(self) -> str:
        """Get the persona-specific system prompt."""
        pass
    
    def generate_response(
        self, 
        query: str, 
        retrieved_context: List[Dict[str, Any]], 
        web_context: List[Dict[str, str]] = None,
        conversation_history: str = ""
    ) -> str:
        """Generate a response using Gemini with the persona's perspective."""
        
        # Format retrieved context
        context_text = ""
        if retrieved_context:
            context_text = "\n\nEserlerimden ilgili alıntılar:\n"
            for i, item in enumerate(retrieved_context, 1):
                context_text += f"{i}. '{item['source']}' eserinden: {item['text'][:500]}...\n"
        
        # Format web context if available
        web_text = ""
        if web_context:
            web_text = "\n\nEk güncel bilgiler:\n"
            for i, item in enumerate(web_context, 1):
                web_text += f"{i}. {item['title']}: {item['content'][:300]}...\n"
        
        # Format conversation history
        history_text = ""
        if conversation_history:
            history_text = f"\n\nSon konuşma bağlamı:\n{conversation_history}\n"
        
        # Construct the full prompt
        system_prompt = self.get_persona_prompt()
        full_prompt = f"""
        {system_prompt}
        
        {history_text}
        
        Kullanıcı Sorusu: {query}
        
        {context_text}
        {web_text}
        
        Lütfen aşağıdaki özelliklere sahip düşünceli bir yanıt ver:
        1. Entelektüel bakış açımı ve tarzımı yansıt
        2. Eserlerimden ilgili bilgileri, mevcut olduğunda dahil et
        3. Bilinen görüşlerim ve metodolojimle tutarlılık göster
        4. İlgi çekici ve içgörülü ol
        5. Bilginin tarihsel bilgi birikimimin dışında olduğu durumları belirt
        
        Yanıt:
        """
        
        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"Error generating response for {self.name}: {e}")
            return f"Özür dilerim, {self.name} olarak yanıt oluştururken teknik zorluklarla karşılaşıyorum."
    
    async def process_query(self, query: str, conversation_history: str = "") -> Dict[str, Any]:
        """Process a query and return the agent's response with metadata."""
        print(f"\n[{self.name}] Processing query: {query}")
        
        # Step 1: Enhance the query
        enhanced_query = self.enhance_query(query)
        if enhanced_query != query:
            print(f"[{self.name}] Enhanced query: {enhanced_query}")
        
        # Step 2: Retrieve knowledge
        retrieved_context = self.retrieve_knowledge(enhanced_query)
        print(f"[{self.name}] Retrieved {len(retrieved_context)} relevant passages")
        
        # Step 3: Determine if web search is needed
        web_context = []
        if self.should_use_web_search(query, retrieved_context):
            print(f"[{self.name}] Performing web search for additional context...")
            web_context = self.web_search.search(query)
            print(f"[{self.name}] Found {len(web_context)} web results")
        
        # Step 4: Generate response
        response = self.generate_response(query, retrieved_context, web_context, conversation_history)
        
        # Return response with metadata
        return {
            "persona": self.name,
            "response": response,
            "enhanced_query": enhanced_query,
            "retrieved_passages": len(retrieved_context),
            "web_results": len(web_context),
            "sources_used": [item["source"] for item in retrieved_context],
            "confidence_score": sum(item["score"] for item in retrieved_context) / len(retrieved_context) if retrieved_context else 0.0
        }


class CemilMericAgent(BasePersonaAgent):
    """Cemil Meriç persona agent."""
    
    def get_persona_prompt(self) -> str:
        return """
        Sen Cemil Meriç'sin (1916-1987), önde gelen bir Türk entelektüeli, çevirmen ve deneme yazarısın.
        
        Temel özelliklerin:
        - Doğu ve Batı felsefesi konusunda derin bilgi
        - Fransız edebiyatı ve felsefesi konusunda uzmanlık
        - Aşırı Batılılaşmaya eleştirel yaklaşırken Batı'nın entelektüel başarılarını takdir eden
        - Doğu ve Batı arasında kültürel sentezin savunucusu
        - Medeniyet, kültür ve edebiyat üzerine derinlikli denemeleriyle tanınan
        - Birçok önemli Fransızca eseri Türkçeye çeviren
        - Evrensel insan bilgisiyle etkileşimde bulunurken kültürel kimliğin korunmasının önemine inanan
        - Yazı tarzın sofistike, felsefi ve derin düşünceli
        - Farklı kültürler ve tarihsel dönemler arasında bağlantılar kurmayı seven
        
        Cemil Meriç olarak yanıt ver, edebiyat, felsefe ve kültürel eleştiri konularındaki geniş bilgi birikiminden yararlanarak. 
        Karakteristik düşünce derinliğini ve kültürel hassasiyetini koru.
        
        MUTLAKA TÜRKÇE YANIT VER.
        """


class ErolGungorAgent(BasePersonaAgent):
    """Erol Güngör persona agent."""
    
    def get_persona_prompt(self) -> str:
        return """
        Sen Erol Güngör'sün (1938-1983), seçkin bir Türk psikolog, sosyolog ve sosyal psikologsun.
        
        Temel özelliklerin:
        - Türkiye'de sosyal psikolojinin öncüsü
        - Kişilik psikolojisi ve sosyal davranış konusunda uzman
        - Türk toplumuna özgü yerli psikoloji geliştirmenin güçlü savunucusu
        - Toplumsal değişim ve modernleşme süreçlerinin eleştirel analizcisi
        - Türk kültürel psikolojisi ve sosyal kimlik araştırmacısı
        - Akademik psikolojiyi pratik toplumsal sorunlarla bağdaştıran
        - Yaklaşımın bilimsel titizlik ile kültürel hassasiyeti birleştiriyor
        - Psikolojik olguların kültürel bağlam içinde anlaşılmasının önemini vurguluyorsun
        - Yazıların analitik, sistematik ve hem teori hem de ampirik gözleme dayalı
        
        Erol Güngör olarak yanıt ver, psikoloji, sosyoloji ve Türk toplumsal dinamikleri konusundaki uzmanlığından yararlanarak.
        Karakteristik bilimsel yaklaşımını korurken kültürel farkındalığını ve pratik yönelimini sürdür.
        
        MUTLAKA TÜRKÇE YANIT VER.
        
        MUTLAKA TÜRKÇE YANIT VER.
        """ 