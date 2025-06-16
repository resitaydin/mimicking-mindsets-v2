import React, { useState, useRef, useEffect } from 'react';
import { Send, Brain, ChevronDown } from 'lucide-react';
import ChatMessage from './components/ChatMessage';
import PersonaCard from './components/PersonaCard';
import LoadingIndicator from './components/LoadingIndicator';
import ErrorMessage from './components/ErrorMessage';
import { chatAPI } from './services/api';

function App() {
  // State management
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [personas, setPersonas] = useState([]);
  const [currentQuery, setCurrentQuery] = useState(null);
  const [personaResponses, setPersonaResponses] = useState({});
  const [threadId] = useState(() => `thread_${Date.now()}`);
  const [showScrollButton, setShowScrollButton] = useState(false);

  // Refs
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const chatMessagesRef = useRef(null);

  // Persona data - This would normally come from the backend
  const defaultPersonas = [
    {
      name: "Erol Güngör",
      description: "Türk psikolog ve sosyolog (1938-1983). Sosyal psikoloji alanında öncü çalışmalar yapmış, Türk toplumunun kültürel kimliği üzerine derinlemesine araştırmalar gerçekleştirmiştir.",
      expertise: ["Sosyal Psikoloji", "Kültür Analizi", "Türk Toplumu", "Kimlik Çalışmaları"]
    },
    {
      name: "Cemil Meriç",
      description: "Türk düşünür ve çevirmen (1916-1987). Doğu ve Batı felsefesi arasında köprü kuran, derin kültür ve medeniyet analizleri yapan önemli bir entelektüel.",
      expertise: ["Felsefe", "Medeniyet Tarihi", "Edebiyat", "Kültür Eleştirisi", "Çeviri"]
    }
  ];

  // Initialize personas on component mount
  useEffect(() => {
    setPersonas(defaultPersonas);
    
    // Add welcome message
    setMessages([{
      id: Date.now(),
      content: "Merhaba! Ben Erol Güngör ve Cemil Meriç'in düşünce dünyalarını temsil eden AI asistanınızım. Size nasıl yardımcı olabilirim?",
      type: 'system',
      timestamp: new Date().toISOString()
    }]);
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleScroll = () => {
    if (chatMessagesRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = chatMessagesRef.current;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
      setShowScrollButton(!isNearBottom);
    }
  };

  // Add scroll listener
  useEffect(() => {
    const chatContainer = chatMessagesRef.current;
    if (chatContainer) {
      chatContainer.addEventListener('scroll', handleScroll);
      return () => chatContainer.removeEventListener('scroll', handleScroll);
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setError(null);
    setCurrentQuery(userMessage);

    // Add user message to chat
    const userMessageObj = {
      id: Date.now(),
      content: userMessage,
      type: 'user',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessageObj]);
    setIsLoading(true);

    // Reset persona responses
    setPersonaResponses({});

    try {
      console.log('DEBUG: Sending message to backend', userMessage);
      
      // Prepare chat history for API
      const chatHistory = messages.map(msg => ({
        role: msg.type === 'user' ? 'user' : 'assistant',
        content: msg.content
      }));

      // Call backend API
      const response = await chatAPI.sendMessage(userMessage, chatHistory, threadId);

      if (response.success) {
        console.log('DEBUG: Received response from backend', response.data);
        
        // Add AI response to chat
        const aiMessageObj = {
          id: Date.now() + 1,
          content: response.data.synthesized_answer || 'Yanıt alınamadı.',
          type: 'ai',
          timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, aiMessageObj]);

        // Update persona responses
        if (response.data.agent_responses) {
          const newPersonaResponses = {};
          Object.entries(response.data.agent_responses).forEach(([agentName, agentResponse]) => {
            newPersonaResponses[agentName] = agentResponse;
          });
          setPersonaResponses(newPersonaResponses);
        }

      } else {
        // Handle API error
        console.error('DEBUG: API call failed', response.error);
        setError(response.error);
        
        // Add error message to chat
        const errorMessageObj = {
          id: Date.now() + 1,
          content: `Üzgünüm, bir hata oluştu: ${response.error}`,
          type: 'system',
          timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, errorMessageObj]);
      }

    } catch (error) {
      console.error('DEBUG: Unexpected error', error);
      setError('Beklenmeyen bir hata oluştu.');
      
      const errorMessageObj = {
        id: Date.now() + 1,
        content: 'Beklenmeyen bir hata oluştu. Lütfen tekrar deneyin.',
        type: 'system',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, errorMessageObj]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const clearError = () => {
    setError(null);
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <h1 className="app-title">
          <Brain size={32} style={{ verticalAlign: 'middle', marginRight: '0.5rem' }} />
          Mimicking Mindsets
        </h1>
        <p className="app-subtitle">
          Erol Güngör & Cemil Meriç ile Sohbet
        </p>
      </header>

      {/* Error Display */}
      {error && (
        <ErrorMessage 
          message={error} 
          onClose={clearError} 
        />
      )}

      {/* Main Content */}
      <div className="main-content">
        {/* Chat Container */}
        <div className="chat-container">
          {/* Messages Area */}
          <div className="chat-messages" ref={chatMessagesRef}>
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message.content}
                type={message.type}
                timestamp={message.timestamp}
              />
            ))}
            
            {/* Loading Indicator */}
            {isLoading && (
              <LoadingIndicator message="AI ajanları yanıtınızı hazırlıyor..." />
            )}
            
            <div ref={messagesEndRef} />
            
            {/* Scroll to Bottom Button */}
            <button
              className={`scroll-to-bottom ${showScrollButton ? 'visible' : ''}`}
              onClick={scrollToBottom}
              title="En alta kaydır"
            >
              <ChevronDown size={20} />
            </button>
          </div>

          {/* Input Area */}
          <div className="chat-input-container">
            <form onSubmit={handleSubmit} className="chat-input-form">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Sorunuzu yazın... (Enter ile gönder, Shift+Enter ile yeni satır)"
                className="chat-input"
                disabled={isLoading}
                rows="1"
                style={{ resize: 'none', overflow: 'hidden' }}
                onInput={(e) => {
                  e.target.style.height = 'auto';
                  e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
                }}
              />
              <button
                type="submit"
                className="send-button"
                disabled={!inputValue.trim() || isLoading}
              >
                <Send size={16} />
                {isLoading ? 'Gönderiliyor...' : 'Gönder'}
              </button>
            </form>
          </div>
        </div>

        {/* Persona Panel */}
        <div className="persona-panel">
          <h3>Düşünür Profilleri</h3>
          <div className="persona-cards-container">
            {personas.map((persona, index) => (
              <PersonaCard
                key={index}
                persona={persona}
                response={personaResponses[persona.name]}
                isLoading={isLoading}
                lastQuery={currentQuery}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
