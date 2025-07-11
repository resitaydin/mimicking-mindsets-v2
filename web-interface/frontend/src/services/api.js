import axios from 'axios';

// Backend API base URL
const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout for AI responses
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service for chatbot communication
export const chatAPI = {
  /**
   * Send a message to the multi-agent orchestrator
   * @param {string} userQuery - The user's message
   * @param {Array} chatHistory - Previous conversation history
   * @param {string} threadId - Optional thread ID for conversation continuity
   * @returns {Promise} - API response with synthesized answer and agent responses
   */
  async sendMessage(userQuery, chatHistory = [], threadId = null) {
    try {
      const payload = {
        user_query: userQuery,
        chat_history: chatHistory,
        ...(threadId && { thread_id: threadId })
      };

      const response = await apiClient.post('/chat', payload);
      
      return {
        success: true,
        data: response.data
      };
      
    } catch (error) {
      console.error('API request failed:', error.message);
      
      // Handle different types of errors
      if (error.response) {
        // Server responded with error status
        return {
          success: false,
          error: `Server error: ${error.response.status} - ${error.response.data?.detail || error.response.statusText}`,
          status: error.response.status
        };
      } else if (error.request) {
        // Request was made but no response received
        return {
          success: false,
          error: 'Backend sunucusuna bağlanılamadı. Lütfen sunucunun çalıştığından emin olun.',
          status: 'connection_error'
        };
      } else {
        // Something else happened
        return {
          success: false,
          error: `Beklenmeyen hata: ${error.message}`,
          status: 'unknown_error'
        };
      }
    }
  },

  /**
   * Send a message with streaming response
   * @param {string} userQuery - The user's message
   * @param {Array} chatHistory - Previous conversation history
   * @param {string} threadId - Optional thread ID for conversation continuity
   * @param {Function} onChunk - Callback for each streaming chunk
   * @returns {Promise} - Streaming response
   */
  async sendMessageStream(userQuery, chatHistory = [], threadId = null, onChunk = null) {
    try {
      const payload = {
        user_query: userQuery,
        chat_history: chatHistory,
        ...(threadId && { thread_id: threadId })
      };

      const response = await fetch(`${API_BASE_URL}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let buffer = '';
      let finalResult = null;

      try {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) {
            break;
          }

          // Decode the chunk
          const chunk = decoder.decode(value, { stream: true });
          buffer += chunk;

          // Process complete lines
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep incomplete line in buffer

          for (const line of lines) {
            if (line.trim() === '') continue;
            
            // Parse Server-Sent Events format
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                // Call the chunk callback if provided
                if (onChunk) {
                  onChunk(data);
                }

                // Store final result
                if (data.type === 'complete') {
                  finalResult = data;
                }
              } catch (parseError) {
                console.error('Failed to parse streaming data:', parseError);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }

      return {
        success: true,
        data: finalResult
      };

    } catch (error) {
      console.error('Streaming request failed:', error.message);
      
      return {
        success: false,
        error: error.message || 'Streaming request failed',
        status: 'streaming_error'
      };
    }
  },

  /**
   * Health check endpoint to verify backend is running
   * @returns {Promise} - Health status
   */
  async healthCheck() {
    try {
      const response = await apiClient.get('/health');
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: 'Backend server is not responding'
      };
    }
  },

  /**
   * Get current agent tracing status
   * @returns {Promise} - Current tracing status
   */
  async getTracingStatus() {
    try {
      const response = await apiClient.get('/tracing/status');
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error fetching tracing status:', error.message);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  },

  /**
   * Export traces for a session
   * @param {string} sessionId - Session ID to export traces for
   * @returns {Promise} - Exported traces
   */
  async exportTraces(sessionId) {
    try {
      const response = await apiClient.get(`/tracing/export/${sessionId}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error exporting traces:', error.message);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }
};

export default chatAPI; 