# Corporate Chat Application - Reflex Frontend

A modern, production-ready chat application built with Reflex, featuring JWT authentication, WebSocket real-time messaging, and a corporate-grade UI.

## 🎯 Features

### Core Features
- ✅ **JWT Authentication** with automatic token refresh
- ✅ **Real-time Messaging** via WebSockets with auto-reconnect
- ✅ **Optimistic UI** - Messages appear instantly
- ✅ **Markdown Support** - Rich text formatting in messages
- ✅ **Copy to Clipboard** - One-click message copying
- ✅ **Typing Indicators** - See when others are typing
- ✅ **Read Receipts** - Track message delivery and read status
- ✅ **Direct Messages** - One-on-one conversations
- ✅ **Group Chats** - Multi-user chat rooms
- ✅ **Dark/Light Theme** - Toggle between themes
- ✅ **Profile Management** - Update bio, avatar, and password
- ✅ **Image Attachments** - Send and view images
- ✅ **Responsive Design** - Mobile-friendly layout

### Security Features
- 🔒 **Automatic Token Refresh** - Seamless session management
- 🔒 **Secure Cookie Storage** - Tokens stored in secure cookies
- 🔒 **401 Auto-Recovery** - Transparent token refresh on expiry
- 🔒 **Protected Routes** - Auth checks on all protected pages

## 📁 Project Structure

```
chat_frontend/
├── assets/
│   └── styles.css                    # Custom CSS
├── chat_frontend/
│   ├── components/
│   │   ├── sidebar.py                # Sidebar with room list
│   │   ├── chat_area.py              # Main chat interface
│   │   ├── message_bubble.py         # Message component with markdown
│   │   └── modals.py                 # New chat & profile modals
│   ├── pages/
│   │   ├── login.py                  # Login page
│   │   ├── signup.py                 # Registration page
│   │   └── chat.py                   # Main chat dashboard
│   ├── state/
│   │   ├── base_state.py             # Base state with API logic
│   │   ├── auth_state.py             # Authentication state
│   │   ├── chat_state.py             # Chat management state
│   │   ├── ws_state.py               # WebSocket state
│   │   └── profile_state.py          # Profile management state
│   └── chat_frontend.py              # App entry point
├── .env                              # Environment variables
├── rxconfig.py                       # Reflex configuration
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.9+
- FastAPI backend running on `http://127.0.0.1:8020`
- Node.js (for Reflex frontend assets)

### 2. Installation

```bash
# Clone the repository
git clone <your-repo>
cd chat_frontend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize Reflex (first time only)
reflex init
```

### 3. Configuration

Create a `.env` file in the project root:

```env
API_URL=http://127.0.0.1:8020
WS_URL=ws://127.0.0.1:8020
```

### 4. Run the Application

```bash
# Development mode (with hot reload)
reflex run

# Production mode
reflex run --env prod
```

The app will be available at:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000` (Reflex backend)

## 🏗️ Architecture

### State Management

The application uses a hierarchical state structure:

1. **BaseState** (`state/base_state.py`)
   - Central API request handler
   - Automatic token refresh logic
   - Error handling
   - User authentication

2. **AuthState** (`state/auth_state.py`)
   - Login/Signup forms
   - Token storage
   - Session management

3. **ChatState** (`state/chat_state.py`)
   - Room/message management
   - Optimistic UI updates
   - WebSocket integration

4. **WebSocketState** (`state/ws_state.py`)
   - WebSocket connection management
   - Auto-reconnect with exponential backoff
   - Message routing

5. **ProfileState** (`state/profile_state.py`)
   - Profile updates
   - Avatar upload
   - Password changes

### API Integration

#### Authentication Flow

```python
# Login
POST /auth/login
Body: {"username": "...", "password": "..."}
Response: {"access_token": "...", "refresh_token": "..."}

# Token Refresh (automatic)
POST /auth/refresh
Body: {"refresh_token": "..."}
Response: {"access_token": "...", "refresh_token": "..."}
```

#### Smart Token Refresh

The `BaseState.api_request()` method automatically:
1. Detects 401 Unauthorized responses
2. Calls `/auth/refresh` with refresh token
3. Updates stored access token
4. Retries the original request
5. Logs out if refresh fails

```python
# Example usage
response = await self.api_request(
    "GET",
    "/users/me",
    # Token refresh happens automatically if needed
)
```

### WebSocket Connection

```python
# Connection URL format
ws://127.0.0.1:8020/ws?token={access_token}&room={room_name}

# Message types
{
    "type": "message",
    "id": 123,
    "content": "Hello!",
    "user": "john",
    "user_id": 1,
    "timestamp": "2024-01-01T12:00:00Z"
}

{
    "type": "typing",
    "user": "jane"
}

{
    "type": "message_read",
    "message_id": 123
}

{
    "type": "system",
    "action": "joined",
    "user": "alice"
}
```

## 🎨 UI/UX Features

### Theme System

Toggle between light and dark themes:

```python
# Theme state stored in localStorage
theme: str = rx.LocalStorage("light")

# Toggle function
def toggle_theme(self):
    self.theme = "dark" if self.theme == "light" else "light"
```

### Optimistic UI

Messages appear instantly before server confirmation:

```python
# 1. Add message to UI with "sending" status
temp_message = {
    "id": f"temp-{len(self.messages)}",
    "content": content,
    "status": "sending",
}
self.messages.append(temp_message)

# 2. Send to backend
response = await self.api_request(...)

# 3. Replace with server response
if response:
    # Update with real message
else:
    # Mark as "failed"
```

### Markdown Support

Messages support rich formatting:

```markdown
**Bold text**
*Italic text*
`inline code`
```code block```
[Links](https://example.com)
```

### Copy to Clipboard

Every message has a copy button:

```python
async def copy_message(self, content: str):
    return rx.set_clipboard(content)
```

## 🔧 API Endpoints

### Authentication
- `POST /auth/register` - Create new account
- `POST /auth/login` - Login and get tokens
- `POST /auth/refresh` - Refresh access token

### Users
- `GET /users/me` - Get current user profile
- `GET /users/` - List all users (for DMs)
- `PUT /users/me` - Update profile (bio, password)
- `POST /users/me/avatar` - Upload avatar image

### Rooms
- `GET /rooms/mine` - Get user's rooms
- `GET /rooms/` - List public rooms
- `POST /rooms/` - Create new room
- `POST /rooms/dm/{username}` - Start/get DM
- `POST /rooms/{id}/join` - Join room
- `POST /rooms/{id}/typing` - Send typing indicator

### Messages
- `GET /messages/{room_id}` - Get message history
- `POST /messages/room` - Send message to room
- `POST /messages/direct/{username}` - Send DM
- `POST /messages/{id}/read` - Mark as read
- `GET /messages/search?query=...` - Search messages

## 🐛 Debugging

### Enable Debug Mode

```bash
# Run with debug logs
reflex run --loglevel debug
```

### Common Issues

1. **WebSocket connection fails**
   - Check backend is running on correct port
   - Verify WS_URL in .env
   - Check firewall/CORS settings

2. **Token refresh not working**
   - Ensure `/auth/refresh` endpoint exists
   - Check refresh token is being stored
   - Verify token format in cookies

3. **Messages not appearing**
   - Check WebSocket connection status
   - Verify room_id is correct
   - Check browser console for errors

## 📱 Responsive Design

The UI adapts to different screen sizes:

- **Desktop** (>768px): Sidebar + Chat area side-by-side
- **Mobile** (<768px): Collapsible sidebar, full-width chat

## 🚀 Deployment

### Production Build

```bash
# Build for production
reflex export

# The output will be in .web/_static/
```

### Environment Variables

For production, set these environment variables:

```env
API_URL=https://your-api-domain.com
WS_URL=wss://your-api-domain.com
```

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Email: support@example.com

---

Built with ❤️ using [Reflex](https://reflex.dev)#   c h a t f r o n t e n d  
 