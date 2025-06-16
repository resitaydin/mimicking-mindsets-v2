import React from 'react';

const ChatMessage = ({ message, type, timestamp }) => {
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
      <div className="message-content">
        {message}
      </div>
      {timestamp && (
        <div className="message-timestamp text-small text-muted">
          {formatTimestamp(timestamp)}
        </div>
      )}
    </div>
  );
};

export default ChatMessage; 