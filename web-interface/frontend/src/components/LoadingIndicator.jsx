import React from 'react';
import { MessageCircle } from 'lucide-react';

const LoadingIndicator = ({ message = "AI ajanları düşünüyor..." }) => {
  return (
    <div className="loading-indicator">
      <MessageCircle size={16} />
      <span>{message}</span>
      <div className="loading-dots">
        <div className="loading-dot"></div>
        <div className="loading-dot"></div>
        <div className="loading-dot"></div>
      </div>
    </div>
  );
};

export default LoadingIndicator; 