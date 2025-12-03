"""WebSocket state management with reconnection logic."""

import reflex as rx
import asyncio
import json
import os
from typing import Optional, Callable, Dict
from websockets import connect, ConnectionClosed
from dotenv import load_dotenv

load_dotenv()

WS_URL = os.getenv("WS_URL", "ws://127.0.0.1:8020")


class WebSocketState(rx.State):
    """Manage WebSocket connection with auto-reconnect."""
    
    is_connected: bool = False
    reconnect_attempts: int = 0
    max_reconnect_attempts: int = 10
    should_reconnect: bool = True
    
    # Internal non-state variables
    _ws = None
    _listen_task = None
    _on_message_callback = None
    
    async def connect(
        self,
        token: str,
        room_name: str,
        on_message_callback: Optional[Callable] = None
    ):
        """
        Connect to WebSocket with auto-reconnect logic.
        
        Args:
            token: JWT access token
            room_name: Room name to join
            on_message_callback: Callback for incoming messages
        """
        self.should_reconnect = True
        self.reconnect_attempts = 0
        
        # Store callback
        self._on_message_callback = on_message_callback
        
        # Build WebSocket URL
        ws_url = f"{WS_URL}/ws?token={token}&room={room_name}"
        
        await self._connect_with_retry(ws_url)
    
    async def _connect_with_retry(self, ws_url: str):
        """Connect with exponential backoff retry."""
        while self.should_reconnect and self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                print(f"Connecting to WebSocket... (Attempt {self.reconnect_attempts + 1})")
                
                self._ws = await connect(
                    ws_url,
                    ping_interval=20,
                    ping_timeout=10,
                )
                
                self.is_connected = True
                self.reconnect_attempts = 0
                print("WebSocket connected successfully")
                
                # Start listening for messages
                if self._listen_task:
                    self._listen_task.cancel()
                
                self._listen_task = asyncio.create_task(self._listen())
                break
                
            except Exception as e:
                print(f"WebSocket connection failed: {e}")
                self.is_connected = False
                self.reconnect_attempts += 1
                
                if self.reconnect_attempts < self.max_reconnect_attempts:
                    # Exponential backoff: 1s, 2s, 4s, 8s, max 30s
                    delay = min(2 ** (self.reconnect_attempts - 1), 30)
                    print(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    print("Max reconnection attempts reached")
                    break
    
    async def _listen(self):
        """Listen for incoming WebSocket messages."""
        try:
            async for message in self._ws:
                try:
                    data = json.loads(message)
                    print(f"WebSocket message received: {data.get('type')}")
                    
                    # Call the message handler
                    if self._on_message_callback:
                        await self._on_message_callback(data)
                        
                except json.JSONDecodeError as e:
                    print(f"Invalid JSON: {e}")
                except Exception as e:
                    print(f"Error handling message: {e}")
                    
        except ConnectionClosed:
            print("WebSocket connection closed")
            self.is_connected = False
            
            # Attempt reconnection if needed
            if self.should_reconnect:
                await self._connect_with_retry(self._ws.remote_address)
                
        except Exception as e:
            print(f"WebSocket error: {e}")
            self.is_connected = False
    
    async def send_message(self, data: Dict):
        """Send a message through WebSocket."""
        if self._ws and self.is_connected:
            try:
                await self._ws.send(json.dumps(data))
            except Exception as e:
                print(f"Failed to send WebSocket message: {e}")
                self.is_connected = False
    
    async def disconnect(self):
        """Disconnect WebSocket."""
        self.should_reconnect = False
        
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
        
        if self._ws:
            await self._ws.close()
        
        self.is_connected = False
        print("WebSocket disconnected")