# Mimicking Mindsets - Frontend

Modern React-based frontend for the 'Mimicking Mindsets' chatbot application, featuring AI personas of Turkish intellectuals Erol Güngör and Cemil Meriç.

## 🎨 Features

- **Modern Chat Interface**: Clean, responsive chat UI with message bubbles
- **Persona Cards**: Expandable cards showing individual persona responses
- **Real-time Communication**: WebSocket-like experience with the backend API
- **Turkish Language Support**: Full Turkish interface and content
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Loading Indicators**: Visual feedback during AI processing
- **Error Handling**: User-friendly error messages and recovery

## 🎨 Design System

### Color Palette
- **Background**: #1C2B3A (Midnight Blue)
- **Text**: #F4F4F9 (Soft White)
- **Secondary BG**: #2D3E50 (Oxford Blue)
- **Accent 1**: #D4AF37 (Soft Gold) - App title, icons
- **Accent 2**: #4CA1A3 (Muted Teal) - User message bubbles
- **Accent 3**: #C17C74 (Dusty Rose) - AI message bubbles
- **Borders**: #A0A4A8 (Cool Grey)
- **Input Fields**: #E6E8EB (Cloud Grey)

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Backend API server running on `http://localhost:8000`

### Installation

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

4. **Open in browser**:
   - URL: http://localhost:5173
   - The app will automatically reload when you make changes

### Alternative Startup Methods

**Windows**:
```cmd
start_frontend.bat
```

**Unix/Linux/macOS**:
```bash
./start_frontend.sh
```

## 🏗️ Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/        # React components
│   │   ├── ChatMessage.jsx      # Individual message component
│   │   ├── PersonaCard.jsx      # Persona information cards
│   │   ├── LoadingIndicator.jsx # Loading animation
│   │   └── ErrorMessage.jsx     # Error display component
│   ├── services/          # API communication
│   │   └── api.js              # Backend API client
│   ├── App.jsx           # Main application component
│   ├── main.jsx          # React entry point
│   └── index.css         # Global styles and design system
├── package.json          # Dependencies and scripts
├── vite.config.js        # Vite configuration
└── README_Frontend.md    # This file
```

## 🔧 Configuration

### Backend API Connection

The frontend connects to the backend API at `http://localhost:8000` by default. To change this:

1. Edit `src/services/api.js`
2. Update the `API_BASE_URL` constant:
   ```javascript
   const API_BASE_URL = 'http://your-backend-url:port';
   ```

### Environment Variables

Create a `.env` file in the frontend directory for custom configuration:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=Mimicking Mindsets
```

## 🎯 Usage

### Chat Interface

1. **Send Messages**: Type your question in Turkish and press Enter or click "Gönder"
2. **View Responses**: The synthesized answer appears in the chat area
3. **Persona Details**: Click on persona cards to see individual responses
4. **Message History**: Scroll through previous conversations
5. **Error Recovery**: If errors occur, they're displayed with retry options

### Persona Cards

- **Expandable**: Click headers to expand/collapse persona information
- **Individual Responses**: See how each persona responded to your query
- **Expertise Areas**: View each persona's areas of specialization
- **Loading States**: Visual indicators when personas are processing

### Keyboard Shortcuts

- **Enter**: Send message
- **Shift + Enter**: New line in message input
- **Escape**: Clear current input (if implemented)

## 🛠️ Development

### Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### Adding New Components

1. Create component file in `src/components/`
2. Follow the existing naming convention (PascalCase)
3. Import and use in `App.jsx` or other components
4. Add corresponding CSS classes in `index.css`

### Styling Guidelines

- Use CSS custom properties (variables) defined in `:root`
- Follow the established color palette
- Maintain responsive design principles
- Use semantic class names
- Add hover and focus states for interactive elements

## 🔌 API Integration

### Request Format

The frontend sends requests to `/chat` endpoint:

```javascript
{
  "user_query": "Kullanıcının sorusu",
  "chat_history": [
    {"role": "user", "content": "Önceki mesaj"},
    {"role": "assistant", "content": "AI yanıtı"}
  ],
  "thread_id": "thread_12345"
}
```

### Response Format

Expected response from backend:

```javascript
{
  "synthesized_answer": "Birleştirilmiş AI yanıtı",
  "agent_responses": {
    "Erol Güngör": "Erol Güngör'ün yanıtı",
    "Cemil Meriç": "Cemil Meriç'in yanıtı"
  },
  "chat_history": [...],
  "thread_id": "thread_12345",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Backend Connection Failed**:
   - Ensure backend server is running on port 8000
   - Check CORS configuration in backend
   - Verify API_BASE_URL in `api.js`

2. **Dependencies Not Installing**:
   - Clear npm cache: `npm cache clean --force`
   - Delete `node_modules` and `package-lock.json`
   - Run `npm install` again

3. **Build Errors**:
   - Check for TypeScript/JavaScript syntax errors
   - Ensure all imports are correct
   - Verify component exports

4. **Styling Issues**:
   - Check CSS custom properties are defined
   - Verify class names match CSS rules
   - Test responsive breakpoints

### Debug Mode

Enable debug logging by opening browser developer tools and checking the Console tab. The app logs API requests and responses for debugging.

## 📱 Responsive Design

The application is fully responsive with breakpoints:

- **Desktop**: > 768px (full layout with sidebar)
- **Tablet**: 768px - 480px (stacked layout)
- **Mobile**: < 480px (optimized for touch)

## 🔒 Security Considerations

- API requests include proper error handling
- No sensitive data stored in localStorage
- CORS properly configured for allowed origins
- Input sanitization handled by React

## 🚀 Production Deployment

### Build for Production

```bash
npm run build
```

### Deploy Options

1. **Static Hosting** (Netlify, Vercel, GitHub Pages):
   - Upload `dist/` folder contents
   - Configure redirects for SPA routing

2. **Docker**:
   ```dockerfile
   FROM nginx:alpine
   COPY dist/ /usr/share/nginx/html/
   EXPOSE 80
   ```

3. **CDN Integration**:
   - Build assets are optimized for CDN delivery
   - Configure proper cache headers

## 📄 License

This project is part of the Mimicking Mindsets system. See the main project README for license information.

## 🤝 Contributing

1. Follow the existing code style and conventions
2. Test your changes thoroughly
3. Update documentation as needed
4. Ensure responsive design is maintained
5. Add appropriate error handling

## 📞 Support

For issues related to the frontend:
1. Check this README and troubleshooting section
2. Review browser console for error messages
3. Verify backend API connectivity
4. Check network requests in browser dev tools 