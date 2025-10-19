"""
Microsoft Graph API Authentication Module using MSAL
"""
import msal
import requests
import streamlit as st
from config import CLIENT_ID, CLIENT_SECRET, TENANT_ID, AUTHORITY, SCOPES, REDIRECT_URI


class GraphAuthenticator:
    """Handles Microsoft Graph API authentication using MSAL"""
    
    def __init__(self):
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.authority = AUTHORITY
        self.scopes = SCOPES
        self.redirect_uri = REDIRECT_URI
        
        # Create MSAL app instance
        self.app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=self.authority
        )
    
    def get_auth_url(self):
        """Generate authorization URL for user consent"""
        auth_url = self.app.get_authorization_request_url(
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        return auth_url
    
    def get_token_from_code(self, auth_code):
        """Exchange authorization code for access token"""
        try:
            result = self.app.acquire_token_by_authorization_code(
                auth_code,
                scopes=self.scopes,
                redirect_uri=self.redirect_uri
            )
            
            if "access_token" in result:
                return result["access_token"]
            else:
                st.error(f"Authentication failed: {result.get('error_description', 'Unknown error')}")
                return None
                
        except Exception as e:
            st.error(f"Error during token acquisition: {str(e)}")
            return None
    
    def get_token_silent(self, account):
        """Try to get token silently using cached credentials"""
        try:
            result = self.app.acquire_token_silent(
                scopes=self.scopes,
                account=account
            )
            
            if "access_token" in result:
                return result["access_token"]
            else:
                return None
                
        except Exception as e:
            print(f"Silent token acquisition failed: {str(e)}")
            return None
    
    def get_accounts(self):
        """Get cached accounts"""
        return self.app.get_accounts()
    
    def validate_token(self, access_token):
        """Validate access token by making a test API call"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(
                'https://graph.microsoft.com/v1.0/me',
                headers=headers
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, None
                
        except Exception as e:
            print(f"Token validation failed: {str(e)}")
            return False, None


def get_authenticated_session():
    """
    Streamlit session management for authentication
    Returns access token if authenticated, None otherwise
    """
    # Initialize session state
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    
    authenticator = GraphAuthenticator()
    
    # Check if we already have a valid token
    if st.session_state.access_token:
        is_valid, user_info = authenticator.validate_token(st.session_state.access_token)
        if is_valid:
            st.session_state.user_info = user_info
            return st.session_state.access_token
        else:
            # Token expired, clear session
            st.session_state.access_token = None
            st.session_state.user_info = None
    
    # Try silent authentication first
    accounts = authenticator.get_accounts()
    if accounts:
        token = authenticator.get_token_silent(accounts[0])
        if token:
            is_valid, user_info = authenticator.validate_token(token)
            if is_valid:
                st.session_state.access_token = token
                st.session_state.user_info = user_info
                return token
    
    # Need interactive authentication
    st.warning("Please authenticate with your Microsoft account to access your emails.")
    
    # Check for authorization code in URL parameters
    query_params = st.query_params
    if 'code' in query_params:
        auth_code = query_params['code']
        token = authenticator.get_token_from_code(auth_code)
        
        if token:
            is_valid, user_info = authenticator.validate_token(token)
            if is_valid:
                st.session_state.access_token = token
                st.session_state.user_info = user_info
                st.success(f"Successfully authenticated as {user_info.get('displayName', 'User')}")
                st.rerun()
                return token
    
    # Show authentication button
    auth_url = authenticator.get_auth_url()
    st.markdown(f"[Click here to authenticate with Microsoft]({auth_url})")
    st.info("After clicking the link above, you'll be redirected to Microsoft for authentication. "
            "Once completed, you'll be redirected back to this app.")
    
    return None
