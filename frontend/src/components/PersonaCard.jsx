import React, { useState } from 'react';
import { ChevronDown, ChevronRight, User } from 'lucide-react';

const PersonaCard = ({ 
  persona, 
  response, 
  isLoading = false,
  lastQuery = null 
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  const getPersonaIcon = (personaName) => {
    // You could customize icons based on persona name
    return <User size={20} />;
  };

  return (
    <div className="persona-card">
      <div className="persona-header" onClick={toggleExpanded}>
        <div className="persona-info">
          {getPersonaIcon(persona.name)}
          <span className="persona-name">{persona.name}</span>
        </div>
        <div className="expand-icon">
          {isExpanded ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
        </div>
      </div>
      
      <div className={`persona-content ${isExpanded ? 'expanded' : ''}`}>
        {/* Persona Description */}
        <div className="persona-description mb-2">
          <h4 className="text-small" style={{ color: 'var(--accent-1)', marginBottom: '0.5rem' }}>
            Kişilik Profili:
          </h4>
          <p className="text-small">{persona.description}</p>
        </div>

        {/* Last Query Response */}
        {lastQuery && (
          <div className="persona-response">
            <h4 className="text-small" style={{ color: 'var(--accent-1)', marginBottom: '0.5rem' }}>
              Son Soruya Yanıt:
            </h4>
            <div className="query-display mb-1">
              <span className="text-small text-muted">Soru: "{lastQuery}"</span>
            </div>
            
            {isLoading ? (
              <div className="persona-loading">
                <div className="loading-dots">
                  <div className="loading-dot"></div>
                  <div className="loading-dot"></div>
                  <div className="loading-dot"></div>
                </div>
                <span className="text-small text-muted">Yanıt hazırlanıyor...</span>
              </div>
            ) : response ? (
              <div className="persona-answer">
                <p className="text-small" style={{ lineHeight: '1.5' }}>
                  {response}
                </p>
              </div>
            ) : (
              <div className="persona-no-response">
                <span className="text-small text-muted">
                  Henüz yanıt verilmedi.
                </span>
              </div>
            )}
          </div>
        )}

        {/* Persona Expertise Areas */}
        {persona.expertise && (
          <div className="persona-expertise mt-2">
            <h4 className="text-small" style={{ color: 'var(--accent-1)', marginBottom: '0.5rem' }}>
              Uzmanlık Alanları:
            </h4>
            <div className="expertise-tags">
              {persona.expertise.map((area, index) => (
                <span 
                  key={index} 
                  className="expertise-tag text-small"
                  style={{
                    display: 'inline-block',
                    backgroundColor: 'var(--border-color)',
                    color: 'var(--bg-primary)',
                    padding: '0.25rem 0.5rem',
                    borderRadius: '12px',
                    marginRight: '0.5rem',
                    marginBottom: '0.25rem',
                    fontSize: '0.8rem'
                  }}
                >
                  {area}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PersonaCard; 