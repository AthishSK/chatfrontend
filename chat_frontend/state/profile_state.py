"""Profile management state - FIXED with explicit setters for v0.8."""

import reflex as rx
from typing import Optional
from .base_state import BaseState


class ProfileState(BaseState):
    """Manage user profile updates."""
    
    # Edit fields
    edit_bio: str = ""
    new_password: str = ""
    confirm_password: str = ""
    
    # Avatar upload
    upload_files: list[rx.UploadFile] = []
    
    # EXPLICIT SETTERS (Fix deprecation warnings)
    def set_edit_bio(self, value: str):
        """Set edit bio value."""
        self.edit_bio = value
    
    def set_new_password(self, value: str):
        """Set new password value."""
        self.new_password = value
    
    def set_confirm_password(self, value: str):
        """Set confirm password value."""
        self.confirm_password = value
    
    def open_profile_modal(self):
        """Open profile modal and load current data."""
        if self.current_user:
            self.edit_bio = self.current_user.get("bio", "")
    
    async def update_bio(self):
        """Update user bio."""
        if not self.edit_bio.strip():
            self.set_error("Bio cannot be empty")
            return
        
        response = await self.api_request(
            "PUT",
            "/users/me",
            json_data={"bio": self.edit_bio}
        )
        
        if response:
            self.current_user = response
            self.set_success("Bio updated successfully!")
    
    async def update_password(self):
        """Update user password."""
        if not self.new_password or not self.confirm_password:
            self.set_error("Please fill in all password fields")
            return
        
        if self.new_password != self.confirm_password:
            self.set_error("Passwords do not match")
            return
        
        if len(self.new_password) < 6:
            self.set_error("Password must be at least 6 characters")
            return
        
        response = await self.api_request(
            "PUT",
            "/users/me",
            json_data={"password": self.new_password}
        )
        
        if response:
            self.new_password = ""
            self.confirm_password = ""
            self.set_success("Password updated successfully!")
    
    async def handle_upload(self, files: list[rx.UploadFile]):
        """Handle avatar file upload."""
        if not files:
            return
        
        file = files[0]
        
        # Read file data
        file_data = await file.read()
        
        # Upload avatar
        response = await self.api_request(
            "POST",
            "/users/me/avatar",
            files={"file": (file.filename, file_data, file.content_type)}
        )
        
        if response:
            self.current_user = response
            self.set_success("Avatar updated successfully!")