import React from 'react';
import { AlertCircle, X } from 'lucide-react';

const ErrorMessage = ({ message, onClose, type = 'error' }) => {
  const getIconAndColor = () => {
    switch (type) {
      case 'warning':
        return { icon: <AlertCircle size={16} />, color: 'var(--warning)' };
      case 'info':
        return { icon: <AlertCircle size={16} />, color: 'var(--loading)' };
      default:
        return { icon: <AlertCircle size={16} />, color: 'var(--error)' };
    }
  };

  const { icon, color } = getIconAndColor();

  return (
    <div className="error-message" style={{ backgroundColor: color }}>
      {icon}
      <span>{message}</span>
      {onClose && (
        <button 
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            color: 'white',
            cursor: 'pointer',
            padding: '0',
            marginLeft: 'auto'
          }}
        >
          <X size={16} />
        </button>
      )}
    </div>
  );
};

export default ErrorMessage; 