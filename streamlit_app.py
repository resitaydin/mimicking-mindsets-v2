import streamlit as st
import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

# Add the current directory to the path to import our modules
sys.path.append(os.path.dirname(__file__))

from runtime import MimickingMindsetsRuntime

# Configure Streamlit page
st.set_page_config(
    page_title="Mimicking Mindsets",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling and mobile responsiveness
st.markdown("""
<style>
    /* Main layout */
    .main {
        padding-top: 1rem;
    }
    
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .persona-card {
            padding: 1rem !important;
            margin: 0.5rem 0 !important;
        }
        
        .persona-title {
            font-size: 1.1rem !important;
        }
        
        .orchestrator-response {
            padding: 1rem !important;
            margin: 0.5rem 0 !important;
        }
    }
    
    /* Persona cards */
    .persona-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        color: white;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .persona-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.2);
    }
    
    .persona-card-cemil {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    }
    
    .persona-card-erol {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='4'/%3E%3Ccircle cx='10' cy='10' r='4'/%3E%3Ccircle cx='50' cy='10' r='4'/%3E%3Ccircle cx='10' cy='50' r='4'/%3E%3Ccircle cx='50' cy='50' r='4'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    }
    
    .persona-title {
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    }
    
    .persona-relevance {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-bottom: 1rem;
        background-color: rgba(255, 255, 255, 0.2);
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        display: inline-block;
    }
    
    /* Orchestrator response */
    .orchestrator-response {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        color: #2c3e50;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .orchestrator-response:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.2);
    }
    
    /* Chat messages */
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        background-color: #f8f9fa;
        animation: fadeIn 0.5s ease-in;
    }
    
    .user-message {
        border-left-color: #28a745;
        background-color: #d4edda;
    }
    
    .assistant-message {
        border-left-color: #667eea;
        background-color: #e3f2fd;
    }
    
    /* Loading animations */
    .loading-container {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
    }
    
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin-right: 1rem;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    /* Sources and metadata */
    .sources-list {
        font-size: 0.8rem;
        color: #6c757d;
        margin-top: 0.5rem;
        background-color: rgba(255, 255, 255, 0.1);
        padding: 0.5rem;
        border-radius: 8px;
    }
    
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin: 0.5rem 0;
        transition: transform 0.2s ease;
    }
    
    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Status indicators */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .status-processing {
        background-color: #ffeaa7;
        color: #fdcb6e;
    }
    
    .status-ready {
        background-color: #55efc4;
        color: #00b894;
    }
    
    .status-error {
        background-color: #fab1a0;
        color: #e17055;
    }
    
    /* Custom scrollbar for sidebar */
    .css-1d391kg {
        scrollbar-width: thin;
        scrollbar-color: #667eea #f1f1f1;
    }
    
    .css-1d391kg::-webkit-scrollbar {
        width: 6px;
    }
    
    .css-1d391kg::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    .css-1d391kg::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 10px;
    }
    
    .css-1d391kg::-webkit-scrollbar-thumb:hover {
        background: #5a6fd8;
    }
    
    /* Button enhancements */
    .stButton > button {
        border-radius: 25px;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Text area improvements */
    .stTextArea > div > div > textarea {
        border-radius: 15px;
        border: 2px solid #e9ecef;
        padding: 1rem;
        font-size: 1rem;
        transition: border-color 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "runtime" not in st.session_state:
    st.session_state.runtime = None
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "system_initialized" not in st.session_state:
    st.session_state.system_initialized = False
if "processing" not in st.session_state:
    st.session_state.processing = False

async def initialize_system():
    """Initialize the runtime system."""
    if not st.session_state.system_initialized:
        # Create a progress bar for initialization
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.markdown("🔄 Starting system initialization...")
            progress_bar.progress(10)
            
            runtime = MimickingMindsetsRuntime()
            
            status_text.markdown("🔧 Validating configuration...")
            progress_bar.progress(25)
            await asyncio.sleep(0.1)  # Small delay for UI feedback
            
            status_text.markdown("🗄️ Connecting to Qdrant database...")
            progress_bar.progress(50)
            
            status_text.markdown("🤖 Loading embedding models...")
            progress_bar.progress(75)
            
            success = await runtime.initialize_system()
            
            if success:
                status_text.markdown("✅ Initializing persona agents...")
                progress_bar.progress(90)
                await asyncio.sleep(0.1)
                
                st.session_state.runtime = runtime
                st.session_state.system_initialized = True
                
                progress_bar.progress(100)
                status_text.markdown("🎉 System initialized successfully!")
                
                # Clear the progress indicators after a moment
                await asyncio.sleep(1)
                progress_bar.empty()
                status_text.empty()
                
                return True
            else:
                progress_bar.empty()
                status_text.empty()
                st.error("❌ System initialization failed. Please check your configuration.")
                return False
                
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ Error initializing system: {e}")
            return False
    return True

def display_persona_card(agent_name: str, response_data: Dict[str, Any], relevance_score: float):
    """Display a persona response card with enhanced mobile responsiveness."""
    # Determine card style based on persona
    card_class = "persona-card"
    persona_icon = "🎭"
    
    if "Cemil" in agent_name:
        card_class += " persona-card-cemil"
        persona_icon = "📚"
    elif "Erol" in agent_name:
        card_class += " persona-card-erol"
        persona_icon = "🧠"
    
    # Format the response text for better readability
    response_text = response_data.get('response', 'Cevap alınamadı')
    
    # Create relevance indicator
    relevance_percentage = int(relevance_score * 100)
    relevance_color = "#4CAF50" if relevance_score >= 0.7 else "#FF9800" if relevance_score >= 0.4 else "#F44336"
    
    # Create the card content with better mobile layout
    card_html = f"""
    <div class="{card_class}">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div class="persona-title">{persona_icon} {agent_name}</div>
            <div style="background: {relevance_color}; color: white; padding: 0.25rem 0.75rem; 
                        border-radius: 20px; font-size: 0.8rem; font-weight: bold;">
                {relevance_percentage}% İlgili
            </div>
        </div>
        <div style="line-height: 1.6; font-size: 0.95rem;">
            {response_text}
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Display sources and metadata in an expandable section
    sources = response_data.get('sources_used', [])
    retrieved_passages = response_data.get('retrieved_passages', 0)
    web_results = response_data.get('web_results', 0)
    
    if sources or retrieved_passages or web_results:
        with st.expander(f"📖 {agent_name} - Kaynak Detayları"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📚 Kullanılan Kaynak", len(sources))
            with col2:
                st.metric("📄 Alıntı Sayısı", retrieved_passages)
            with col3:
                st.metric("🌐 Web Sonucu", web_results)
            
            if sources:
                st.markdown("**Kaynak Eserler:**")
                for source in sources[:5]:  # Show first 5 sources
                    st.markdown(f"• {source}")
    
    st.markdown("<br>", unsafe_allow_html=True)

def display_orchestrator_response(response: str):
    """Display the orchestrator's synthesized response."""
    st.markdown(f"""
    <div class="orchestrator-response">
        <div style="font-size: 1.2rem; font-weight: bold; margin-bottom: 1rem;">
            🎯 Orchestrator Sentezi
        </div>
        <div>{response}</div>
    </div>
    """, unsafe_allow_html=True)

def display_conversation_history():
    """Display conversation history in the sidebar."""
    st.sidebar.markdown("## 📚 Konuşma Geçmişi")
    
    if not st.session_state.conversation_history:
        st.sidebar.info("Henüz konuşma geçmişi yok.")
        return
    
    # Reverse to show most recent first
    for i, entry in enumerate(reversed(st.session_state.conversation_history)):
        with st.sidebar.expander(f"Soru {len(st.session_state.conversation_history) - i}"):
            st.write(f"**Soru:** {entry['query'][:100]}...")
            st.write(f"**Zaman:** {entry['timestamp']}")
            if st.button(f"Detayları Göster", key=f"show_detail_{i}"):
                st.session_state.selected_conversation = entry

async def process_query(query: str):
    """Process a user query through the system."""
    if not st.session_state.runtime:
        st.error("System not initialized. Please refresh the page.")
        return
    
    # Create loading interface
    loading_container = st.empty()
    progress_container = st.empty()
    
    try:
        st.session_state.processing = True
        
        # Show animated loading indicator
        with loading_container:
            st.markdown("""
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <div style="font-size: 1.1rem; color: #667eea;">
                    🤔 Processing your query...
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Create progress tracking
        progress_bar = progress_container.progress(0)
        status_text = st.empty()
        
        # Step 1: Query analysis
        status_text.markdown("🔍 Analyzing query relevance...")
        progress_bar.progress(20)
        await asyncio.sleep(0.2)
        
        # Step 2: Agent coordination
        status_text.markdown("🎭 Coordinating persona agents...")
        progress_bar.progress(40)
        await asyncio.sleep(0.2)
        
        # Step 3: Knowledge retrieval
        status_text.markdown("📚 Retrieving knowledge from databases...")
        progress_bar.progress(60)
        await asyncio.sleep(0.2)
        
        # Step 4: Response generation
        status_text.markdown("✨ Generating responses...")
        progress_bar.progress(80)
        
        # Process through orchestrator
        result = await st.session_state.runtime.orchestrator.process_query(query)
        
        # Step 5: Synthesis
        status_text.markdown("🎯 Synthesizing final response...")
        progress_bar.progress(95)
        await asyncio.sleep(0.1)
        
        # Complete
        progress_bar.progress(100)
        status_text.markdown("✅ Response ready!")
        await asyncio.sleep(0.5)
        
        # Clear loading indicators
        loading_container.empty()
        progress_container.empty()
        status_text.empty()
        
        # Add to conversation history
        conversation_entry = {
            "query": query,
            "result": result,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.conversation_history.append(conversation_entry)
        
        st.session_state.processing = False
        return result
        
    except Exception as e:
        # Clear loading indicators
        loading_container.empty()
        progress_container.empty()
        
        st.session_state.processing = False
        st.error(f"❌ Error processing query: {e}")
        return None

def display_system_status():
    """Display system status indicator."""
    if st.session_state.system_initialized:
        st.markdown("""
        <div style="display: flex; align-items: center; justify-content: center; margin: 1rem 0;">
            <span class="status-badge status-ready">System Ready</span>
        </div>
        """, unsafe_allow_html=True)
    elif st.session_state.processing:
        st.markdown("""
        <div style="display: flex; align-items: center; justify-content: center; margin: 1rem 0;">
            <span class="status-badge status-processing pulse">Processing</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display: flex; align-items: center; justify-content: center; margin: 1rem 0;">
            <span class="status-badge status-error">System Initializing</span>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main Streamlit application."""
    # Header with enhanced styling
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <h1 style="font-size: 3rem; margin-bottom: 0.5rem; 
                   background: linear-gradient(45deg, #667eea, #764ba2);
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   background-clip: text;">
            🧠 Mimicking Mindsets v2
        </h1>
        <p style="font-size: 1.2rem; color: #666; margin-bottom: 1rem;">
            Türk düşünürlerinin entelektüel perspektifleriyle etkileşim kurun
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # System status indicator
    display_system_status()
    
    # Sidebar for conversation history and controls
    display_conversation_history()
    
    # Sidebar controls
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Kontroller")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🗑️ Temizle", use_container_width=True):
            st.session_state.conversation_history.clear()
            if st.session_state.runtime:
                st.session_state.runtime.orchestrator.clear_conversation_history()
            st.rerun()
    
    with col2:
        if st.button("🔄 Yenile", use_container_width=True):
            st.rerun()
    
    # Add system info in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Sistem Bilgisi")
    if st.session_state.system_initialized and st.session_state.runtime:
        st.sidebar.info(f"""
        **Durum:** Aktif  
        **Konuşma:** {len(st.session_state.conversation_history)} kayıt  
        **Düşünürler:** 2 aktif
        """)
    else:
        st.sidebar.warning("Sistem başlatılıyor...")
    
    # System initialization
    if not st.session_state.system_initialized:
        if asyncio.run(initialize_system()):
            st.rerun()
        else:
            st.stop()
    
    # Display available personas
    st.markdown("### 🎭 Mevcut Düşünürler")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **Cemil Meriç**  
        🔸 Türk entelektüeli, çevirmen, deneme yazarı  
        🔸 Doğu-Batı felsefesi uzmanı  
        🔸 Kültürel sentez savunucusu
        """)
    
    with col2:
        st.info("""
        **Erol Güngör**  
        🔸 Türk psikolog ve sosyolog  
        🔸 Sosyal psikoloji öncüsü  
        🔸 Türk kültürel psikolojisi araştırmacısı
        """)
    
    st.markdown("---")
    
    # Main chat interface
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0 1rem 0;">
        <h3 style="color: #667eea; margin-bottom: 0.5rem;">💭 Düşünürlerle Sohbet</h3>
        <p style="color: #666; font-size: 0.9rem;">
            Sorunuzu yazın ve farklı entelektüel perspektiflerden yanıtlar alın
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Example questions for mobile users
    st.markdown("#### 💡 Örnek Sorular")
    example_cols = st.columns(3)
    
    example_questions = [
        "Kültür ve medeniyet ilişkisi",
        "Modernleşme ve geleneksel değerler",
        "Psikolojinin toplumsal rolü"
    ]
    
    for i, (col, question) in enumerate(zip(example_cols, example_questions)):
        with col:
            if st.button(f"💬 {question}", key=f"example_{i}", use_container_width=True):
                st.session_state.query_input = question
                st.rerun()
    
    st.markdown("---")
    
    # Query input with enhanced styling
    query = st.text_area(
        "Sorunuzu buraya yazın:",
        placeholder="Örnek: Cemil Meriç'in Doğu-Batı sentezi hakkındaki düşünceleri nelerdir?",
        height=120,
        key="query_input",
        help="Düşünürlerden almak istediğiniz yanıtın konusunu net bir şekilde belirtin."
    )
    
    # Submit button with loading state
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state.processing:
            st.button("⏳ İşleniyor...", disabled=True, use_container_width=True)
        else:
            submit_button = st.button("🚀 Gönder ve Yanıt Al", type="primary", use_container_width=True)
    
    # Process query when submitted
    if not st.session_state.processing:
        if 'submit_button' in locals() and submit_button and query.strip():
            result = asyncio.run(process_query(query.strip()))
            
            if result:
                st.markdown("---")
                
                # Results header with animation
                st.markdown("""
                <div style="text-align: center; margin: 2rem 0;">
                    <h2 style="color: #667eea; animation: fadeIn 1s ease-in;">
                        📊 Yanıtlarınız Hazır!
                    </h2>
                </div>
                """, unsafe_allow_html=True)
                
                # Display persona responses
                st.markdown("### 🎭 Bireysel Düşünür Yanıtları")
                
                persona_responses = result["persona_responses"]
                relevance_scores = result["relevance_scores"]
                
                # Display in columns for better mobile layout
                for agent_name in result["active_agents"]:
                    if agent_name in persona_responses:
                        response_data = persona_responses[agent_name]
                        relevance = relevance_scores.get(agent_name, 0.0)
                        display_persona_card(agent_name, response_data, relevance)
                
                st.markdown("---")
                
                # Display orchestrator synthesis
                st.markdown("### 🎯 Sentezlenmiş Yanıt")
                display_orchestrator_response(result["synthesized_response"])
                
                # Display metrics in mobile-friendly layout
                st.markdown("### 📈 Analiz Sonuçları")
                
                # Responsive metrics layout
                metric_col1, metric_col2 = st.columns(2)
                metric_col3, metric_col4 = st.columns(2)
                
                with metric_col1:
                    st.metric("🎭 Aktif Düşünür", len(result["active_agents"]))
                
                with metric_col2:
                    total_sources = sum(len(data.get('sources_used', [])) for data in persona_responses.values())
                    st.metric("📚 Kullanılan Kaynak", total_sources)
                
                with metric_col3:
                    avg_relevance = sum(relevance_scores.values()) / len(relevance_scores) if relevance_scores else 0
                    st.metric("🎯 Ortalama İlgililik", f"{avg_relevance:.2f}")
                
                with metric_col4:
                    response_time = "~2-3 saniye"  # Placeholder
                    st.metric("⚡ İşlem Süresi", response_time)
                
                # Success message and clear input
                st.success("✅ Yanıt başarıyla oluşturuldu!")
                
                # Scroll to top button (CSS only, for better UX)
                st.markdown("""
                <div style="text-align: center; margin: 2rem 0;">
                    <p style="color: #666; font-size: 0.9rem;">
                        💡 Yeni bir soru sormak için yukarıdaki metin kutusunu kullanın
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        elif 'submit_button' in locals() and submit_button and not query.strip():
            st.warning("⚠️ Lütfen bir soru yazın.")
    
    # Processing state indicator
    if st.session_state.processing:
        st.info("🔄 Sorgunuz işleniyor, lütfen bekleyin...")
    
    # Display selected conversation details if any
    if hasattr(st.session_state, 'selected_conversation'):
        st.markdown("---")
        st.markdown("## 🔍 Seçilen Konuşma Detayları")
        
        entry = st.session_state.selected_conversation
        st.markdown(f"**Soru:** {entry['query']}")
        st.markdown(f"**Zaman:** {entry['timestamp']}")
        
        # Display the full result
        result = entry['result']
        
        # Persona responses
        st.markdown("### Düşünür Yanıtları")
        for agent_name in result["active_agents"]:
            if agent_name in result["persona_responses"]:
                response_data = result["persona_responses"][agent_name]
                relevance = result["relevance_scores"].get(agent_name, 0.0)
                display_persona_card(agent_name, response_data, relevance)
        
        # Orchestrator response
        st.markdown("### Sentezlenmiş Yanıt")
        display_orchestrator_response(result["synthesized_response"])
        
        if st.button("❌ Detayları Kapat"):
            del st.session_state.selected_conversation
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; padding: 1rem;'>"
        "🎓 AI-Driven Graduation Project • Mimicking Mindsets v2"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 