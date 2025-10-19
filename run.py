#!/usr/bin/env python3
"""
Simple script to run the Email Query App
"""
import subprocess
import sys
import os

def check_requirements():
    """Check if all required packages are installed"""
    try:
        import streamlit
        import langchain
        import openai
        import msal
        import chromadb
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("Please create a .env file based on env_example.txt")
        print("Make sure to add your API keys and Azure app registration details")
        return False
    else:
        print("✅ .env file found")
        return True

def main():
    """Main function to run the app"""
    print("🚀 Starting Email Query App with LangChain...")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment file
    if not check_env_file():
        sys.exit(1)
    
    print("✅ All checks passed!")
    print("🌐 Starting Streamlit server...")
    print("📧 Your Email Query App will open in your browser")
    print("=" * 50)
    
    # Run Streamlit app
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
