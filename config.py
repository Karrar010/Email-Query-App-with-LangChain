"""
Configuration file for the Email Query App
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Microsoft Graph API Configuration
CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
TENANT_ID = os.getenv("TENANT_ID", "")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8504")

# Microsoft Graph API Scopes
SCOPES = [
    "https://graph.microsoft.com/Mail.Read",
    "https://graph.microsoft.com/User.Read"
]

# Groq Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# FAISS Configuration
FAISS_INDEX_PATH = "./faiss_index"

# Graph API Endpoints
GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
