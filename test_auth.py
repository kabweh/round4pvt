"""
Test module for authentication functionality in the AI Tutor application.
Tests user authentication, invite-only signup, and subscription management.
"""
import pytest
from unittest.mock import MagicMock, patch
import bcrypt

from auth import AuthManager, AuthComponent

class TestAuthManager:
    """Tests for the AuthManager class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.database = MagicMock()
        self.auth_manager = AuthManager(self.database)
    
    def test_hash_password(self):
        """Test password hashing functionality."""
        # Hash a test password
        password = "testpassword123"
        hashed = self.auth_manager._hash_password(password)
        
        # Check that the hash is not the original password
        assert hashed != password
        
        # Check that the hash can be verified
        assert bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def test_check_password(self):
        """Test password verification functionality."""
        # Hash a test password
        password = "testpassword123"
        hashed = self.auth_manager._hash_password(password)
        
        # Check correct password
        assert self.auth_manager._check_password(password, hashed) is True
        
        # Check incorrect password
        assert self.auth_manager._check_password("wrongpassword", hashed) is False
    
    def test_register_user(self):
        """Test user registration functionality."""
        # Setup mock
        self.database.add_user.return_value = 1
        self.database.use_invite_link.return_value = True
        self.database.get_user_by_username.return_value = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com"
        }
        
        # Register a user
        result = self.auth_manager.register_user(
            "testuser",
            "testpassword123",
            "test@example.com",
            "valid_token"
        )
        
        # Check if database methods were called correctly
        self.database.add_user.assert_called_once()
        self.database.use_invite_link.assert_called_once_with("valid_token", 1)
        
        # Check result
        assert result["success"] is True
        assert result["user"]["username"] == "testuser"
        
        # Test registration without invite token
        result = self.auth_manager.register_user(
            "testuser2",
            "testpassword123",
            "test2@example.com",
            None
        )
        
        # Check result
        assert result["success"] is False
        assert "required" in result["message"]
        
        # Test registration with invalid username/password
        result = self.auth_manager.register_user(
            "",
            "short",
            "test3@example.com",
            "token"
        )
        
        # Check result
        assert result["success"] is False
    
    def test_login_user(self):
        """Test user login functionality."""
        # Setup mock
        self.database.get_user_by_username.return_value = {
            "id": 1,
            "username": "testuser",
            "password_hash": self.auth_manager._hash_password("testpassword123"),
            "email": "test@example.com"
        }
        
        # Login with correct credentials
        result = self.auth_manager.login_user("testuser", "testpassword123")
        
        # Check if database method was called correctly
        self.database.get_user_by_username.assert_called_with("testuser")
        
        # Check result
        assert result["success"] is True
        assert result["user"]["username"] == "testuser"
        
        # Login with incorrect password
        result = self.auth_manager.login_user("testuser", "wrongpassword")
        
        # Check result
        assert result["success"] is False
        assert "Invalid" in result["message"]
        
        # Login with non-existent user
        self.database.get_user_by_username.return_value = None
        result = self.auth_manager.login_user("nonexistent", "testpassword123")
        
        # Check result
        assert result["success"] is False
        assert "Invalid" in result["message"]
    
    def test_generate_invite_link(self):
        """Test invite link generation functionality."""
        # Setup mock
        self.database.create_invite_link.return_value = (1, "test_token")
        
        # Generate an invite link
        invite_id, token = self.auth_manager.generate_invite_link(1, "invite@example.com", 7)
        
        # Check if database method was called correctly
        self.database.create_invite_link.assert_called_once_with(1, "invite@example.com", 7)
        
        # Check result
        assert invite_id == 1
        assert token == "test_token"
    
    def test_validate_invite_token(self):
        """Test invite token validation functionality."""
        # Validate a token
        result = self.auth_manager.validate_invite_token("test_token")
        
        # Check result (placeholder implementation always returns success)
        assert result["success"] is True
        assert result["invite"]["token"] == "test_token"
    
    def test_activate_subscription(self):
        """Test subscription activation functionality."""
        # Activate a subscription
        result = self.auth_manager.activate_subscription(1, 30)
        
        # Check result (placeholder implementation always returns success)
        assert result["success"] is True
        assert "expires_at" in result

class TestAuthComponent:
    """Tests for the AuthComponent class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.auth_manager = MagicMock()
        self.auth_component = AuthComponent(self.auth_manager)
        
        # Save original session state and create a mock one
        self.original_session_state = getattr(self.auth_component, 'st', None)
        mock_session_state = MagicMock()
        mock_session_state.user = None
        self.auth_component.st = mock_session_state
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        # Restore original session state
        if self.original_session_state:
            self.auth_component.st = self.original_session_state
