"""
Email Query App with LangChain - Main Streamlit Application
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os

# Import custom modules
from auth import get_authenticated_session
from email_fetcher import EmailFetcher
from simple_email_search import SimpleEmailStore, SimpleEmailQA
from config import OPENAI_API_KEY


def main():
    """Main application function"""
    
    # Set page configuration
    st.set_page_config(
        page_title="Email Query App with LangChain",
        page_icon="📧",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Main title
    st.title("📧 Email Query App with LangChain")
    st.markdown("---")
    
    # Check if OpenAI API key is configured
    if not OPENAI_API_KEY:
        st.error("⚠️ OpenAI API key not configured. Please set OPENAI_API_KEY in your .env file.")
        st.stop()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Authentication status
        st.subheader("🔐 Authentication")
        access_token = get_authenticated_session()
        
        if access_token:
            if st.session_state.user_info:
                st.success(f"✅ Authenticated as {st.session_state.user_info.get('displayName', 'User')}")
                st.write(f"Email: {st.session_state.user_info.get('mail', st.session_state.user_info.get('userPrincipalName', 'N/A'))}")
            
            # Logout button
            if st.button("🚪 Logout"):
                st.session_state.access_token = None
                st.session_state.user_info = None
                st.rerun()
        else:
            st.warning("Please authenticate to continue")
            return
        
        st.markdown("---")
        
        # Date selection
        st.subheader("📅 Date Selection")
        selected_date = st.date_input(
            "Select date to fetch emails from:",
            value=date.today() - timedelta(days=1),  # Default to yesterday
            max_value=date.today()
        )
        
        # Fetch emails button
        fetch_emails = st.button("📥 Fetch Emails", type="primary")
        
        # Clear email database button
        if st.button("🗑️ Clear Email Database"):
            if 'email_store' in st.session_state:
                st.session_state.email_store.clear_emails()
            if 'emails' in st.session_state:
                del st.session_state['emails']
            if 'qa_system' in st.session_state:
                del st.session_state['qa_system']
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📊 Email Summary")
        
        # Initialize session state
        if 'emails' not in st.session_state:
            st.session_state.emails = []
        if 'email_store' not in st.session_state:
            st.session_state.email_store = SimpleEmailStore()
        if 'qa_system' not in st.session_state:
            st.session_state.qa_system = None
        
        # Fetch emails when button is clicked
        if fetch_emails:
            with st.spinner("Fetching emails..."):
                try:
                    # Create email fetcher
                    email_fetcher = EmailFetcher(access_token)
                    
                    # Convert date to datetime
                    target_datetime = datetime.combine(selected_date, datetime.min.time())
                    
                    # Fetch emails
                    emails = email_fetcher.fetch_emails_by_date(target_datetime)
                    
                    if emails:
                        st.session_state.emails = emails
                        
                        # Store emails in simple email store
                        with st.spinner("Processing emails for search..."):
                            if st.session_state.email_store.store_emails(emails):
                                # Create QA system
                                st.session_state.qa_system = SimpleEmailQA(st.session_state.email_store)
                                st.success(f"Successfully processed {len(emails)} emails!")
                            else:
                                st.error("Failed to process emails")
                    else:
                        st.warning(f"No emails found for {selected_date}")
                        
                except Exception as e:
                    st.error(f"Error fetching emails: {str(e)}")
        
        # Display email summary
        if st.session_state.emails:
            emails = st.session_state.emails
            
            # Get email summary
            email_fetcher = EmailFetcher(access_token)
            summary = email_fetcher.get_email_summary(emails)
            
            # Display metrics
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Total Emails", summary['total_emails'])
            with col_b:
                st.metric("Unique Senders", len(summary['senders']))
            with col_c:
                high_importance = summary['importance_breakdown'].get('high', 0)
                st.metric("High Priority", high_importance)
            
            # Top senders
            if summary['senders']:
                st.subheader("📤 Top Senders")
                sender_df = pd.DataFrame(summary['senders'], columns=['Email', 'Count'])
                st.dataframe(sender_df, use_container_width=True)
            
            # Recent subjects
            if summary['subjects']:
                st.subheader("📝 Recent Email Subjects")
                for i, subject in enumerate(summary['subjects'][:10], 1):
                    st.write(f"{i}. {subject}")
        
        else:
            st.info("👆 Select a date and click 'Fetch Emails' to get started")
    
    with col2:
        st.header("🤖 Ask Questions About Your Emails")
        
        if st.session_state.qa_system and st.session_state.emails:
            # Question input
            question = st.text_area(
                "Ask a question about your emails:",
                placeholder="e.g., What are the most important emails I received? Who sent me the most emails? What meetings do I have scheduled?",
                height=100
            )
            
            # Ask question button
            if st.button("🔍 Ask Question") and question.strip():
                with st.spinner("Analyzing emails..."):
                    try:
                        # Get answer from QA system
                        result = st.session_state.qa_system.ask_question(question)
                        
                        # Display answer
                        st.subheader("💡 Answer")
                        st.write(result['answer'])
                        
                        # Display sources
                        if result['sources']:
                            st.subheader("📎 Source Emails")
                            for i, source in enumerate(result['sources'], 1):
                                with st.expander(f"Email {i}: {source['subject']}"):
                                    st.write(f"**From:** {source['sender']}")
                                    st.write(f"**Date:** {source['received_date']}")
                                    st.write(f"**Preview:** {source['content_preview']}")
                        
                    except Exception as e:
                        st.error(f"Error processing question: {str(e)}")
            
            # Sample questions
            st.subheader("💡 Sample Questions")
            sample_questions = [
                "What are the most important emails I received?",
                "Who sent me the most emails today?",
                "Are there any meeting invitations?",
                "What emails require my immediate attention?",
                "Summarize the main topics discussed in my emails",
                "Are there any urgent requests or deadlines mentioned?",
                "What emails are from my manager or colleagues?",
                "Are there any emails about projects or tasks?"
            ]
            
            for question in sample_questions:
                if st.button(f"📝 {question}", key=f"sample_{hash(question)}"):
                    with st.spinner("Analyzing emails..."):
                        try:
                            result = st.session_state.qa_system.ask_question(question)
                            
                            st.subheader("💡 Answer")
                            st.write(result['answer'])
                            
                            if result['sources']:
                                st.subheader("📎 Source Emails")
                                for i, source in enumerate(result['sources'], 1):
                                    with st.expander(f"Email {i}: {source['subject']}"):
                                        st.write(f"**From:** {source['sender']}")
                                        st.write(f"**Date:** {source['received_date']}")
                                        st.write(f"**Preview:** {source['content_preview']}")
                        
                        except Exception as e:
                            st.error(f"Error processing question: {str(e)}")
        
        else:
            st.info("📥 Please fetch emails first to start asking questions")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>Email Query App with LangChain | Built with Streamlit, Microsoft Graph API, and OpenAI</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
