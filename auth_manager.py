"""
Authentication module for AI Tutor application.
Handles user authentication, invite-only signup, and subscription management.
"""
import os
import datetime
import secrets
import bcrypt
from typing import Dict, Any, Optional, Tuple

class AuthManager:
    """
    Handles authentication and subscription management for the AI Tutor application.
    """
    
    def __init__(self, database):
        """
        Initialize the authentication manager.
        
        Args:
            database: Database instance for user storage
        """
        self.database = database
    
    def register_user(self, username: str, password: str, email: Optional[str] = None, 
                     invite_token: Optional[str] = None) -> Dict:
        """
        Register a new user.
        
        Args:
            username: User's username
            password: User's password (will be hashed)
            email: User's email address (optional)
            invite_token: Invite token for invite-only signup
            
        Returns:
            Dictionary containing registration status and user info if successful
        """
        # Check if invite token is valid (required for registration)
        if not invite_token:
            return {
                "success": False,
                "message": "Invite token is required for registration."
            }
        
        # Validate username and password
        if not username or len(username) < 3:
            return {
                "success": False,
                "message": "Username must be at least 3 characters long."
            }
        
        if not password or len(password) < 8:
            return {
                "success": False,
                "message": "Password must be at least 8 characters long."
            }
        
        # Hash the password
        password_hash = self._hash_password(password)
        
        # Add user to database
        user_id = self.database.add_user(username, password_hash, email)
        
        if user_id == -1:
            return {
                "success": False,
                "message": "Username or email already exists."
            }
        
        # Mark invite token as used
        if not self.database.use_invite_link(invite_token, user_id):
            # If token is invalid, we should still keep the user but inform them
            return {
                "success": True,
                "message": "User registered successfully, but invite token is invalid or expired.",
                "user_id": user_id
            }
        
        # Get the user info
        user = self.database.get_user_by_username(username)
        
        return {
            "success": True,
            "message": "User registered successfully.",
            "user": user
        }
    
    def login_user(self, username: str, password: str) -> Dict:
        """
        Log in a user.
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            Dictionary containing login status and user info if successful
        """
        # Get user from database
        user = self.database.get_user_by_username(username)
        
        if not user:
            return {
                "success": False,
                "message": "Invalid username or password."
            }
        
        # Check password
        if not self._check_password(password, user['password_hash']):
            return {
                "success": False,
                "message": "Invalid username or password."
            }
        
        return {
            "success": True,
            "message": "Login successful.",
            "user": user
        }
    
    def generate_invite_link(self, created_by: int, email: Optional[str] = None, 
                            expires_in_days: int = 7) -> Tuple[int, str]:
        """
        Generate a new invite link.
        
        Args:
            created_by: User ID of the creator
            email: Email address the invite is for (optional)
            expires_in_days: Number of days until the invite expires
            
        Returns:
            Tuple of (invite_id, token)
        """
        return self.database.create_invite_link(created_by, email, expires_in_days)
    
    def validate_invite_token(self, token: str) -> Dict:
        """
        Validate an invite token.
        
        Args:
            token: The invite token
            
        Returns:
            Dictionary containing validation status and invite info if valid
        """
        # This is a placeholder for token validation logic
        # In a real implementation, this would check the database
        
        # Get invite from database (placeholder)
        # invite = self.database.get_invite_by_token(token)
        
        # For now, we'll just return a success response
        return {
            "success": True,
            "message": "Invite token is valid.",
            "invite": {
                "token": token,
                "email": None,
                "expires_at": (datetime.datetime.now() + datetime.timedelta(days=7)).isoformat()
            }
        }
    
    def activate_subscription(self, user_id: int, duration_days: int = 30) -> Dict:
        """
        Activate a subscription for a user.
        
        Args:
            user_id: User ID
            duration_days: Number of days to activate the subscription for
            
        Returns:
            Dictionary containing activation status
        """
        # This is a placeholder for subscription activation logic
        # In a real implementation, this would update the database
        
        # For now, we'll just return a success response
        return {
            "success": True,
            "message": "Subscription activated successfully.",
            "expires_at": (datetime.datetime.now() + datetime.timedelta(days=duration_days)).isoformat()
        }
    
    def _hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Password to hash
            
        Returns:
            Hashed password
        """
        # Generate a salt and hash the password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        return hashed.decode('utf-8')
    
    def _check_password(self, password: str, hashed_password: str) -> bool:
        """
        Check if a password matches a hash.
        
        Args:
            password: Password to check
            hashed_password: Hashed password to compare against
            
        Returns:
            True if the password matches, False otherwise
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
