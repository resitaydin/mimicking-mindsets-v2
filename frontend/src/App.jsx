import React, { useState, useRef, useEffect } from 'react';
import { Send, Brain, ChevronDown } from 'lucide-react';
import ChatMessage from './components/ChatMessage';
import PersonaCard from './components/PersonaCard';
import LoadingIndicator from './components/LoadingIndicator';
import ErrorMessage from './components/ErrorMessage';
import AgentTraces from './components/AgentTraces';
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
  const [streamingContent, setStreamingContent] = useState('');
  const [agentStatuses, setAgentStatuses] = useState({});

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

    // Reset states for new streaming session
    setPersonaResponses({});
    setStreamingContent('');
    setAgentStatuses({});

    // Add a placeholder message for streaming content
    const streamingMessageObj = {
      id: Date.now() + 1,
      content: '',
      type: 'ai',
      timestamp: new Date().toISOString(),
      isStreaming: true
    };
    setMessages(prev => [...prev, streamingMessageObj]);

    try {
      console.log('DEBUG: Starting streaming request', userMessage);
      
      // Prepare chat history for API
      const chatHistory = messages.map(msg => ({
        role: msg.type === 'user' ? 'user' : 'assistant',
        content: msg.content
      }));

      // Handle streaming chunks
      const handleStreamChunk = (data) => {
        console.log('DEBUG: Processing stream chunk:', data);
        
        switch (data.type) {
          case 'status':
            console.log('DEBUG: Status update:', data.message);
            break;
            
          case 'agent_start':
            setAgentStatuses(prev => ({
              ...prev,
              [data.agent]: { status: 'thinking', message: data.message }
            }));
            break;
            
          case 'agent_working':
            setAgentStatuses(prev => ({
              ...prev,
              [data.agent]: { status: 'working', message: data.message }
            }));
            break;
            
          case 'agent_response':
            setPersonaResponses(prev => ({
              ...prev,
              [data.agent]: data.response
            }));
            setAgentStatuses(prev => ({
              ...prev,
              [data.agent]: { status: 'completed', message: 'Yanıt hazır' }
            }));
            break;
            
          case 'synthesis_start':
            console.log('DEBUG: Synthesis started:', data.message);
            break;
            
          case 'synthesis_chunk':
            setStreamingContent(prev => {
              const newContent = prev + data.chunk;
              // Update the streaming message with the new content
              setMessages(prevMessages => prevMessages.map(msg => 
                msg.isStreaming ? { ...msg, content: newContent } : msg
              ));
              return newContent;
            });
            break;
            
          case 'complete':
            // Update final message
            setMessages(prev => prev.map(msg => 
              msg.isStreaming ? { 
                ...msg, 
                content: data.synthesized_answer, 
                isStreaming: false 
              } : msg
            ));
            setStreamingContent('');
            break;
            
          case 'error':
            console.error('DEBUG: Stream error:', data.message);
            setError(data.message);
            break;
            
          default:
            console.log('DEBUG: Unknown stream data type:', data.type);
        }
      };

      // Call streaming API
      const response = await chatAPI.sendMessageStream(
        userMessage, 
        chatHistory, 
        threadId, 
        handleStreamChunk
      );

      if (!response.success) {
        // Handle API error
        console.error('DEBUG: Streaming API call failed', response.error);
        setError(response.error);
        
        // Update the streaming message with error
        setMessages(prev => prev.map(msg => 
          msg.isStreaming ? {
            ...msg,
            content: `Üzgünüm, bir hata oluştu: ${response.error}`,
            type: 'system',
            isStreaming: false
          } : msg
        ));
      }

    } catch (error) {
      console.error('DEBUG: Unexpected streaming error', error);
      setError('Beklenmeyen bir hata oluştu.');
      
      // Update the streaming message with error
      setMessages(prev => prev.map(msg => 
        msg.isStreaming ? {
          ...msg,
          content: 'Beklenmeyen bir hata oluştu. Lütfen tekrar deneyin.',
          type: 'system',
          isStreaming: false
        } : msg
      ));
    } finally {
      setIsLoading(false);
      setAgentStatuses({});
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
          
          {/* Agent Traces */}
          <AgentTraces 
            agentStatuses={agentStatuses} 
            isLoading={isLoading} 
          />
          
          <div className="persona-cards-container">
            {personas.map((persona, index) => (
              <PersonaCard
                key={index}
                persona={persona}
                response={personaResponses[persona.name]}
                isLoading={isLoading}
                lastQuery={currentQuery}
                agentStatus={agentStatuses[persona.name]}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
