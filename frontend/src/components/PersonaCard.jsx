import React, { useState } from 'react';
import { ChevronDown, ChevronRight, User } from 'lucide-react';
import erolGungorImage from '../assets/erol-gungor.jpg';
import cemilMericImage from '../assets/cemil-meric.jpg';

const PersonaCard = ({ 
  persona, 
  response, 
  isLoading = false,
  lastQuery = null,
  agentStatus = null
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  const getPersonaIcon = (personaName) => {
    // Display actual profile pictures for the personas
    if (personaName === "Erol Güngör") {
      return (
        <img 
          src={erolGungorImage} 
          alt="Erol Güngör" 
          className="persona-avatar"
          style={{
            width: '50px',    
            height: '50px',
            borderRadius: '50%',
            objectFit: 'cover',
            border: '2px solid var(--border-color)'
          }}
        />
      );
    } else if (personaName === "Cemil Meriç") {
      return (
        <img 
          src={cemilMericImage} 
          alt="Cemil Meriç" 
          className="persona-avatar"
          style={{
            width: '50px',
            height: '50px',
            borderRadius: '50%',
            objectFit: 'cover',
            border: '2px solid var(--border-color)'
          }}
        />
      );
    }
    
    // Fallback to User icon for unknown personas
    return <User size={20} />;
  };

  return (
    <div className="persona-card">
      <div className="persona-header" onClick={toggleExpanded}>
        <div className="persona-info">
          {getPersonaIcon(persona.name)}
          <span className="persona-name">{persona.name}</span>
          {agentStatus && (
            <span 
              className="agent-status-indicator"
              style={{
                display: 'inline-block',
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: agentStatus.status === 'thinking' ? '#ffa500' : 
                                agentStatus.status === 'completed' ? '#00ff00' : '#ccc',
                marginLeft: '8px'
              }}
            />
          )}
        </div>
        <div className="expand-icon">
          {isExpanded ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
        </div>
      </div>
      
      <div className={`persona-content ${isExpanded ? 'expanded' : ''}`}>
        {/* Persona Description */}
        <div className="persona-description mb-2">
          <h4 className="text-small" style={{ color: 'var(--accent-1)', marginBottom: '0.5rem' }}>
            Yazar Hakkında:
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
            
            {(isLoading || agentStatus?.status === 'thinking') ? (
              <div className="persona-loading">
                <div className="loading-dots">
                  <div className="loading-dot"></div>
                  <div className="loading-dot"></div>
                  <div className="loading-dot"></div>
                </div>
                <span className="text-small text-muted">
                  {agentStatus?.message || 'Yanıt hazırlanıyor...'}
                </span>
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