"""Authentication state management."""

import reflex as rx
from .base_state import BaseState


class AuthState(BaseState):
    """Handle authentication operations."""
    
    # Login form
    login_email: str = ""
    login_password: str = ""
    
    # Signup form
    signup_name: str = ""
    signup_username: str = ""
    signup_password: str = ""
    signup_confirm_password: str = ""
    
    async def handle_login(self):
        """Handle user login."""
        self.clear_messages()
        
        if not self.login_email or not self.login_password:
            self.set_error("Email and password are required")
            return
        
        self.is_loading = True
        
        # Call login API
        response = await self.api_request(
            "POST",
            "/auth/login",
            json_data={
                "username": self.login_email,
                "password": self.login_password,
            },
            retry_on_401=False,  # Don't retry login failures
        )
        
        if response:
            # Store tokens
            self.access_token = response.get("access_token", "")
            self.refresh_token = response.get("refresh_token", "")
            
            # Load user profile
            user_data = await self.api_request("GET", "/users/me")
            
            if user_data:
                self.current_user = user_data
                self.is_authenticated = True
                
                # Clear form
                self.login_email = ""
                self.login_password = ""
                self.is_loading = False
                
                # Redirect using window.location
                return rx.redirect("/chat")
        
        self.is_loading = False
    
    async def handle_signup(self):
        """Handle user registration."""
        self.clear_messages()
        
        # Validation
        if not self.signup_username or not self.signup_password:
            self.set_error("Username and password are required")
            return
        
        if self.signup_password != self.signup_confirm_password:
            self.set_error("Passwords do not match")
            return
        
        if len(self.signup_password) < 6:
            self.set_error("Password must be at least 6 characters")
            return
        
        self.is_loading = True
        
        # Call register API
        response = await self.api_request(
            "POST",
            "/auth/register",
            json_data={
                "username": self.signup_username,
                "password": self.signup_password,
            },
            retry_on_401=False,
        )
        
        if response:
            self.set_success("Registration successful! Please login.")
            
            # Clear form
            self.signup_name = ""
            self.signup_username = ""
            self.signup_password = ""
            self.signup_confirm_password = ""
            self.is_loading = False
            
            # Small delay before redirect
            return rx.redirect("/login")
        
        self.is_loading = False