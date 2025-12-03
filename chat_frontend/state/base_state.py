"""Base state with API request handling and token refresh logic."""

import reflex as rx
import httpx
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8020")


class BaseState(rx.State):
    """Base state with centralized API request handling."""
    
    # Auth tokens
    access_token: str = rx.Cookie("")
    refresh_token: str = rx.Cookie("")
    
    # Current user
    current_user: Optional[Dict] = None
    is_authenticated: bool = False
    
    # UI states
    is_loading: bool = False
    error_message: Optional[str] = None
    success_message: Optional[str] = None
    
    def clear_messages(self):
        """Clear notification messages."""
        self.error_message = None
        self.success_message = None
    
    def set_error(self, message: str):
        """Set error message."""
        self.error_message = message
        self.is_loading = False
    
    def set_success(self, message: str):
        """Set success message."""
        self.success_message = message
        self.is_loading = False
    
    async def api_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        files: Optional[Dict] = None,
        retry_on_401: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Centralized API request handler with automatic token refresh.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., "/users/me")
            json_data: JSON body
            params: Query parameters
            files: Files to upload
            retry_on_401: Whether to retry with refreshed token on 401
            
        Returns:
            Response JSON or None on error
        """
        url = f"{API_URL}{endpoint}"
        headers = {}
        
        # Add auth header if token exists
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                if files:
                    # Multipart upload
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        files=files,
                        data=json_data,
                        params=params,
                    )
                else:
                    # JSON request
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        json=json_data,
                        params=params,
                    )
                
                # Handle 401 Unauthorized - Try token refresh
                if response.status_code == 401 and retry_on_401 and self.refresh_token:
                    print("Token expired, attempting refresh...")
                    refreshed = await self._refresh_access_token()
                    
                    if refreshed:
                        # Retry the original request
                        return await self.api_request(
                            method=method,
                            endpoint=endpoint,
                            json_data=json_data,
                            params=params,
                            files=files,
                            retry_on_401=False,  # Don't retry again
                        )
                    else:
                        # Refresh failed, logout
                        await self.handle_logout()
                        return None
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text
                try:
                    error_json = e.response.json()
                    error_detail = error_json.get("detail", error_detail)
                except:
                    pass
                self.set_error(f"Error: {error_detail}")
                return None
                
            except httpx.RequestError as e:
                self.set_error(f"Connection error: {str(e)}")
                return None
                
            except Exception as e:
                self.set_error(f"Unexpected error: {str(e)}")
                return None
    
    async def _refresh_access_token(self) -> bool:
        """
        Refresh the access token using refresh token.
        
        Returns:
            True if refresh succeeded, False otherwise
        """
        url = f"{API_URL}/auth/refresh"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    url,
                    json={"refresh_token": self.refresh_token}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data.get("access_token", "")
                    # Update refresh token if provided
                    if "refresh_token" in data:
                        self.refresh_token = data["refresh_token"]
                    print("Token refreshed successfully")
                    return True
                else:
                    print("Token refresh failed")
                    return False
                    
            except Exception as e:
                print(f"Token refresh error: {e}")
                return False
    
    async def check_auth(self):
        """Check if user is authenticated and load profile."""
        if not self.access_token:
            self.is_authenticated = False
            # Use JavaScript redirect for compatibility
            return rx.redirect("/login")
        
        # Try to load current user
        user_data = await self.api_request("GET", "/users/me")
        
        if user_data:
            self.current_user = user_data
            self.is_authenticated = True
        else:
            self.is_authenticated = False
            return rx.redirect("/login")
    
    async def handle_logout(self):
        """Logout and clear all state."""
        self.access_token = ""
        self.refresh_token = ""
        self.current_user = None
        self.is_authenticated = False
        return rx.redirect("/login")