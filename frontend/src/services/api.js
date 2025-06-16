import axios from 'axios';

// Backend API base URL - adjust this to match your backend server
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
      console.log('DEBUG: Sending API request', { userQuery, chatHistory, threadId });
      console.log('DEBUG: API Base URL:', API_BASE_URL);
      
      const payload = {
        user_query: userQuery,
        chat_history: chatHistory,
        ...(threadId && { thread_id: threadId })
      };

      console.log('DEBUG: Request payload:', payload);

      const response = await apiClient.post('/chat', payload);
      
      console.log('DEBUG: API response status:', response.status);
      console.log('DEBUG: API response headers:', response.headers);
      console.log('DEBUG: API response data:', response.data);
      
      return {
        success: true,
        data: response.data
      };
      
    } catch (error) {
      console.error('DEBUG: API request failed', error);
      console.error('DEBUG: Error details:', {
        message: error.message,
        response: error.response,
        request: error.request,
        config: error.config
      });
      
      // Handle different types of errors
      if (error.response) {
        // Server responded with error status
        console.error('DEBUG: Server error response:', error.response.data);
        console.error('DEBUG: Server error status:', error.response.status);
        console.error('DEBUG: Server error headers:', error.response.headers);
        
        return {
          success: false,
          error: `Server error: ${error.response.status} - ${error.response.data?.detail || error.response.statusText}`,
          status: error.response.status
        };
      } else if (error.request) {
        // Request was made but no response received
        console.error('DEBUG: No response received:', error.request);
        return {
          success: false,
          error: 'Backend sunucusuna bağlanılamadı. Lütfen sunucunun çalıştığından emin olun.',
          status: 'connection_error'
        };
      } else {
        // Something else happened
        console.error('DEBUG: Request setup error:', error.message);
        return {
          success: false,
          error: `Beklenmeyen hata: ${error.message}`,
          status: 'unknown_error'
        };
      }
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
  }
};

export default chatAPI; 