import React from 'react';
import { Plus, MessageSquare, Trash2 } from 'lucide-react';

const ChatSidebar = ({ 
  chats, 
  currentChatId, 
  onCreateNewChat, 
  onSelectChat, 
  onDeleteChat,
  isCollapsed,
  onToggleCollapse 
}) => {
  const formatChatTitle = (chat) => {
    if (chat.title) return chat.title;
    
    // Generate title from first user message
    const firstUserMessage = chat.messages.find(msg => msg.type === 'user');
    if (firstUserMessage) {
      return firstUserMessage.content.length > 30 
        ? firstUserMessage.content.substring(0, 30) + '...'
        : firstUserMessage.content;
    }
    
    return 'Yeni Sohbet';
  };

  const formatChatDate = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Bugün';
    if (diffDays === 2) return 'Dün';
    if (diffDays <= 7) return `${diffDays} gün önce`;
    
    return date.toLocaleDateString('tr-TR', { 
      day: 'numeric', 
      month: 'short' 
    });
  };

  return (
    <div className={`chat-sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <button 
          className="new-chat-btn"
          onClick={onCreateNewChat}
          title="Yeni Sohbet"
        >
          <Plus size={16} />
          {!isCollapsed && <span>Yeni Sohbet</span>}
        </button>
      </div>
      
      <div className="sidebar-content">
        <div className="chat-list">
          {chats.map((chat) => (
            <div
              key={chat.id}
              className={`chat-item ${currentChatId === chat.id ? 'active' : ''}`}
              onClick={() => onSelectChat(chat.id)}
            >
              <div className="chat-item-content">
                <MessageSquare size={16} className="chat-icon" />
                {!isCollapsed && (
                  <div className="chat-info">
                    <div className="chat-title">
                      {formatChatTitle(chat)}
                    </div>
                    <div className="chat-date">
                      {formatChatDate(chat.createdAt)}
                    </div>
                  </div>
                )}
              </div>
              
              {!isCollapsed && chats.length > 1 && (
                <button
                  className="delete-chat-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteChat(chat.id);
                  }}
                  title="Sohbeti Sil"
                >
                  <Trash2 size={14} />
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
      
      <div className="sidebar-footer">
        <button
          className="toggle-sidebar-btn"
          onClick={onToggleCollapse}
          title={isCollapsed ? 'Kenar Çubuğunu Genişlet' : 'Kenar Çubuğunu Daralt'}
        >
          <MessageSquare size={16} />
        </button>
      </div>
    </div>
  );
};

export default ChatSidebar; 