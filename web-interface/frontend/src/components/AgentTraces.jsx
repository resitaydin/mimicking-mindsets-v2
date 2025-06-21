import React from 'react';
import { Clock, CheckCircle, Loader, Cog, AlertCircle, Activity } from 'lucide-react';

const AgentTraces = ({ agentStatuses, isLoading }) => {
  if (!isLoading && Object.keys(agentStatuses).length === 0) {
    return null;
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'thinking':
        return <Loader size={14} className="spinning" />;
      case 'working':
        return <Cog size={14} className="spinning" />;
      case 'completed':
        return <CheckCircle size={14} />;
      case 'error':
        return <AlertCircle size={14} />;
      default:
        return <Activity size={14} className="spinning" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'thinking':
        return 'var(--accent-2)';
      case 'working':
        return 'var(--accent-2)';
      case 'completed':
        return 'var(--success)';
      case 'error':
        return 'var(--error)';
      default:
        return 'var(--text-secondary)';
    }
  };

  const formatDuration = (durationMs) => {
    if (!durationMs) return '';
    if (durationMs < 1000) return `${Math.round(durationMs)}ms`;
    return `${(durationMs / 1000).toFixed(1)}s`;
  };

  return (
    <div className="agent-traces">
      <h4 className="agent-traces-title">
        <Activity size={16} style={{ marginRight: '0.5rem' }} />
        Ajan İzleme Sistemi
      </h4>
      <div className="agent-traces-list">
        {Object.entries(agentStatuses).map(([agentName, status]) => (
          <div key={agentName} className="agent-trace-item">
            <div className="agent-trace-icon">
              <div style={{ color: getStatusColor(status.status) }}>
                {getStatusIcon(status.status)}
              </div>
            </div>
            <div className="agent-trace-content">
              <div className="agent-trace-header">
                <span className="agent-trace-name">{agentName}</span>
                {status.tool_calls > 0 && (
                  <span className="agent-trace-tools">
                    {status.tool_calls} araç
                  </span>
                )}
                {status.duration && (
                  <span className="agent-trace-duration">
                    {formatDuration(status.duration)}
                  </span>
                )}
              </div>
              <span className="agent-trace-message">{status.message}</span>
              {status.start_time && (
                <span className="agent-trace-timestamp">
                  {new Date(status.start_time).toLocaleTimeString()}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
      
      {/* LangSmith Integration Status */}
      <div className="langsmith-status">
        <div className="langsmith-indicator">
          <div className="langsmith-dot"></div>
          <span className="langsmith-text">LangSmith Tracing Aktif</span>
        </div>
      </div>
    </div>
  );
};

export default AgentTraces; 