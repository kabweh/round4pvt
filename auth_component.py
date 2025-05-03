"""
Streamlit component for authentication in the AI Tutor application.
Provides UI elements for login, registration, and subscription management.
"""
import streamlit as st
from typing import Dict, Any, Optional

from auth.auth_manager import AuthManager

class AuthComponent:
    """
    Streamlit component for handling authentication in the AI Tutor application.
    """
    
    def __init__(self, auth_manager: AuthManager):
        """
        Initialize the authentication component.
        
        Args:
            auth_manager: Instance of AuthManager to handle authentication
        """
        self.auth_manager = auth_manager
    
    def render_auth_forms(self) -> None:
        """
        Render the authentication forms (login and registration).
        """
        # Create tabs for login and registration
        login_tab, register_tab = st.tabs(["Login", "Sign Up"])
        
        # Login form
        with login_tab:
            with st.form("login_form"):
                st.subheader("Login")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                
                submitted = st.form_submit_button("Login")
                if submitted:
                    if not username or not password:
                        st.error("Please enter both username and password.")
                    else:
                        # Attempt login
                        result = self.auth_manager.login_user(username, password)
                        
                        if result["success"]:
                            # Store user in session state
                            st.session_state.user = result["user"]
                            st.success("Login successful!")
                            st.experimental_rerun()
                        else:
                            st.error(result["message"])
        
        # Registration form
        with register_tab:
            with st.form("register_form"):
                st.subheader("Sign Up")
                st.info("Registration requires an invite code. Please contact an administrator if you don't have one.")
                
                new_username = st.text_input("Username", key="reg_username")
                new_password = st.text_input("Password", type="password", key="reg_password")
                confirm_password = st.text_input("Confirm Password", type="password")
                email = st.text_input("Email (optional)")
                invite_token = st.text_input("Invite Code")
                
                submitted = st.form_submit_button("Sign Up")
                if submitted:
                    # Validate inputs
                    if not new_username or not new_password:
                        st.error("Please enter both username and password.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    elif not invite_token:
                        st.error("Invite code is required.")
                    else:
                        # Validate invite token
                        token_validation = self.auth_manager.validate_invite_token(invite_token)
                        
                        if not token_validation["success"]:
                            st.error(token_validation["message"])
                        else:
                            # Attempt registration
                            result = self.auth_manager.register_user(
                                new_username, 
                                new_password, 
                                email, 
                                invite_token
                            )
                            
                            if result["success"]:
                                st.success("Registration successful! You can now log in.")
                                # Switch to login tab
                                st.session_state.auth_tab = "login"
                                st.experimental_rerun()
                            else:
                                st.error(result["message"])
    
    def render_auth_status(self) -> None:
        """
        Render the authentication status in the sidebar.
        """
        if 'user' in st.session_state and st.session_state.user:
            user = st.session_state.user
            
            st.write(f"Logged in as: **{user['username']}**")
            
            # Subscription status
            if user.get('subscription_active', False):
                st.success("Subscription: Active")
                if user.get('subscription_expires'):
                    st.write(f"Expires: {user['subscription_expires']}")
            else:
                st.warning("Subscription: Inactive")
            
            # Logout button
            if st.button("Logout"):
                st.session_state.user = None
                # Clear other session state variables
                for key in list(st.session_state.keys()):
                    if key not in ['initialized', 'current_page']:
                        del st.session_state[key]
                st.experimental_rerun()
        else:
            st.info("Not logged in")
    
    def render_subscription_management(self) -> None:
        """
        Render the subscription management section.
        """
        st.header("Subscription Management")
        
        # Check if user is logged in
        if 'user' not in st.session_state or not st.session_state.user:
            st.warning("Please log in to manage your subscription.")
            return
        
        user = st.session_state.user
        
        # Display current subscription status
        if user.get('subscription_active', False):
            st.success("Your subscription is currently active.")
            if user.get('subscription_expires'):
                st.write(f"Your subscription expires on: {user['subscription_expires']}")
            
            # Renewal options (placeholder)
            st.subheader("Renew Subscription")
            st.write("Contact an administrator to renew your subscription.")
        else:
            st.warning("You don't have an active subscription.")
            
            # Subscription options (placeholder)
            st.subheader("Subscription Options")
            st.write("Contact an administrator to activate your subscription.")
            
            # In a real application, this would integrate with Stripe
            # For now, we'll just have a placeholder button
            if st.button("Subscribe (Test Mode)"):
                # Activate subscription (placeholder)
                result = self.auth_manager.activate_subscription(user['id'])
                
                if result["success"]:
                    # Update user in session state
                    user['subscription_active'] = True
                    user['subscription_expires'] = result["expires_at"]
                    st.session_state.user = user
                    
                    st.success("Subscription activated successfully!")
                    st.experimental_rerun()
                else:
                    st.error(result["message"])
