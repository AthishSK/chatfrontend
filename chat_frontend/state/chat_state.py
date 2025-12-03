"""Chat state management with WebSocket integration."""

import reflex as rx
import asyncio
from typing import List, Dict, Optional
from .base_state import BaseState
from .ws_state import WebSocketState


class ChatState(BaseState):
    """Manage chat rooms and messages."""
    
    # Rooms and users
    rooms: List[Dict] = []
    users: List[Dict] = []
    
    # Current chat
    current_room_id: Optional[int] = None
    current_room_name: Optional[str] = None
    messages: List[Dict] = []
    
    # Message input
    message_input: str = ""
    
    # Typing indicators
    typing_users: List[str] = []
    
    # UI states
    show_new_chat_modal: bool = False
    show_profile_modal: bool = False
    show_sidebar: bool = False  # For mobile
    selected_dm_user: Optional[str] = None
    new_room_name: str = ""
    selected_members: List[str] = []  # For group creation
    
    # Search
    search_query: str = ""
    
    # Theme (using cookie instead of LocalStorage for Reflex 0.8)
    theme: str = rx.Cookie("light")
    
    def toggle_sidebar(self):
        """Toggle sidebar visibility on mobile."""
        self.show_sidebar = not self.show_sidebar
    
    def toggle_theme(self):
        """Toggle theme between light and dark."""
        self.theme = "dark" if self.theme == "light" else "light"
    
    def toggle_new_chat_modal(self):
        """Toggle new chat modal."""
        self.show_new_chat_modal = not self.show_new_chat_modal
    
    def toggle_profile_modal(self):
        """Toggle profile modal."""
        self.show_profile_modal = not self.show_profile_modal
    
    async def load_rooms(self):
        """Load user's chat rooms."""
        if not self.is_authenticated:
            return
        
        rooms_data = await self.api_request("GET", "/rooms/mine")
        if rooms_data:
            self.rooms = rooms_data
    
    async def load_users(self):
        """Load all users for DM."""
        if not self.is_authenticated:
            return
        
        users_data = await self.api_request("GET", "/users/")
        if users_data:
            # Filter out current user
            self.users = [
                u for u in users_data 
                if u["id"] != self.current_user["id"]
            ]
    
    async def select_room(self, room_id: int, room_name: str):
        """Select a chat room and load messages."""
        self.current_room_id = room_id
        self.current_room_name = room_name
        self.messages = []
        
        # Load message history
        await self.load_messages(room_id)
        
        # Connect WebSocket
        await self.connect_websocket(room_name)
    
    async def load_messages(self, room_id: int):
        """Load message history for a room."""
        messages_data = await self.api_request("GET", f"/messages/{room_id}")
        if messages_data:
            self.messages = messages_data
    
    async def connect_websocket(self, room_name: str):
        """Connect to WebSocket for real-time updates."""
        # Get WebSocket state
        ws_state = await self.get_state(WebSocketState)
        await ws_state.connect(
            token=self.access_token,
            room_name=room_name,
            on_message_callback=self.handle_ws_message
        )
    
    async def handle_ws_message(self, data: Dict):
        """Handle incoming WebSocket messages."""
        msg_type = data.get("type")
        
        if msg_type == "message":
            # New message received
            message = {
                "id": data.get("id"),
                "content": data.get("content"),
                "user": data.get("user"),
                "user_id": data.get("user_id"),
                "timestamp": data.get("timestamp"),
                "is_read": data.get("is_read", False),
                "attachment_url": data.get("attachment_url"),
                "status": "sent",
            }
            
            # Check if it's not our own message (optimistic UI)
            if message["user_id"] != self.current_user["id"]:
                self.messages.append(message)
        
        elif msg_type == "typing":
            # Typing indicator
            username = data.get("user")
            if username and username != self.current_user["username"]:
                if username not in self.typing_users:
                    self.typing_users.append(username)
                    # Remove after 3 seconds
                    asyncio.create_task(self._remove_typing_indicator(username))
        
        elif msg_type == "message_read":
            # Update read receipt
            message_id = data.get("message_id")
            self.messages = [
                {**msg, "is_read": True} if msg["id"] == message_id else msg
                for msg in self.messages
            ]
        
        elif msg_type == "system":
            # System message (user joined/left)
            action = data.get("action")
            user = data.get("user")
            # Could add system messages to chat
            print(f"System: {user} {action}")
    
    async def _remove_typing_indicator(self, username: str):
        """Remove typing indicator after 3 seconds."""
        await asyncio.sleep(3)
        self.typing_users = [u for u in self.typing_users if u != username]
    
    async def send_message(self):
        """Send a message (Optimistic UI)."""
        if not self.message_input.strip() or not self.current_room_id:
            return
        
        content = self.message_input.strip()
        self.message_input = ""  # Clear input immediately
        
        # Optimistic UI: Add message to list
        temp_id = f"temp-{len(self.messages)}"
        temp_message = {
            "id": temp_id,
            "content": content,
            "user": self.current_user["username"],
            "user_id": self.current_user["id"],
            "timestamp": "",
            "is_read": False,
            "attachment_url": None,
            "status": "sending",
        }
        self.messages.append(temp_message)
        
        # Send to backend
        response = await self.api_request(
            "POST",
            "/messages/room",
            json_data={
                "content": content,
                "room_id": self.current_room_id,
            }
        )
        
        if response:
            # Replace temp message with actual
            self.messages = [
                {**response, "status": "sent"} if msg["id"] == temp_id else msg
                for msg in self.messages
            ]
        else:
            # Mark as failed
            self.messages = [
                {**msg, "status": "failed"} if msg["id"] == temp_id else msg
                for msg in self.messages
            ]
    
    async def send_typing_indicator(self):
        """Send typing indicator to other users."""
        if self.current_room_id:
            await self.api_request(
                "POST",
                f"/rooms/{self.current_room_id}/typing"
            )
    
    def toggle_member(self, username: str):
        """Toggle member selection for group creation."""
        if username in self.selected_members:
            self.selected_members = [m for m in self.selected_members if m != username]
        else:
            self.selected_members = self.selected_members + [username]
    
    async def create_new_room(self):
        """Create a new group room with selected members."""
        if not self.new_room_name.strip():
            self.set_error("Room name is required")
            return
        
        if len(self.selected_members) == 0:
            self.set_error("Please select at least one member")
            return
        
        # Create the room first
        response = await self.api_request(
            "POST",
            "/rooms/",
            json_data={"name": self.new_room_name}
        )
        
        if response:
            room_id = response.get("id")
            
            # Add members to the room (if your backend supports this)
            # You might need to implement a backend endpoint like POST /rooms/{id}/members
            # For now, we'll just create the room
            
            self.set_success("Group created successfully!")
            self.new_room_name = ""
            self.selected_members = []
            self.show_new_chat_modal = False
            await self.load_rooms()
            
            # Select the newly created room
            room_name = response.get("name")
            await self.select_room(room_id, room_name)
    
    async def start_dm(self, username: str):
        """Start or get existing DM with a user."""
        if not username:
            self.set_error("Invalid username")
            return
            
        response = await self.api_request(
            "POST",
            f"/rooms/dm/{username}"
        )
        
        if response:
            room_id = response.get("id")
            room_name = response.get("name")
            self.show_new_chat_modal = False
            await self.load_rooms()
            await self.select_room(room_id, room_name)
    
    async def copy_message(self, content: str):
        """Copy message content to clipboard."""
        return rx.set_clipboard(content)
    
    async def delete_message(self, message_id: int):
        """Delete a message (if implemented in backend)."""
        # This would need to be implemented in your backend
        pass
    
    def get_room_display_name(self, room: Dict) -> str:
        """Get display name for a room."""
        return room.get("name", "Unknown Room")