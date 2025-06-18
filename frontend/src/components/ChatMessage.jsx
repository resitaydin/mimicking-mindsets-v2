import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Book, Globe } from 'lucide-react';

const ChatMessage = ({ message, type, timestamp, sources }) => {
  const [showSources, setShowSources] = useState(false);

  const formatMessage = (text) => {
    if (!text) return text;
    
    // Convert **text** to <strong>text</strong>
    return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  };
  const getMessageClass = () => {
    switch (type) {
      case 'user':
        return 'message user';
      case 'ai':
        return 'message ai';
      case 'system':
        return 'message system';
      default:
        return 'message ai';
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    
    if (isToday) {
      return date.toLocaleTimeString('tr-TR', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } else {
      return date.toLocaleString('tr-TR', { 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    }
  };

  return (
    <div className={getMessageClass()}>
      <div 
        className="message-content"
        dangerouslySetInnerHTML={{ __html: formatMessage(message) }}
      />
      {timestamp && (
        <div className="message-timestamp text-small text-muted">
          {formatTimestamp(timestamp)}
        </div>
      )}
      {sources && sources.length > 0 && type === 'ai' && (
        <div className="sources-section">
          <button 
            className="sources-toggle-btn"
            onClick={() => setShowSources(!showSources)}
          >
            <span>Kaynakları Göster</span>
            {showSources ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
          {showSources && (
            <div className="sources-list">
              {sources.map((source, index) => (
                <div key={index} className="source-item">
                  <div className="source-icon">
                    {source.type === 'vector_db' ? <Book size={16} /> : <Globe size={16} />}
                  </div>
                  <div className="source-info">
                    <div className="source-name">{source.name}</div>
                    {source.type === 'vector_db' && (
                      <div className="source-type">(Vektör Veritabanı)</div>
                    )}
                    {source.type === 'web_search' && (
                      <div className="source-type">(Web Araması)</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ChatMessage; 