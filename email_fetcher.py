"""
Email Fetching Module for Microsoft Graph API
"""
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import streamlit as st
from config import GRAPH_API_ENDPOINT


class EmailFetcher:
    """Fetches emails from Microsoft Graph API"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def fetch_emails_by_date(self, target_date: datetime) -> List[Dict]:
        """
        Fetch all emails from a specific date
        
        Args:
            target_date: The date to fetch emails from
            
        Returns:
            List of email dictionaries
        """
        try:
            # Format dates for Microsoft Graph API
            start_date = target_date.strftime('%Y-%m-%dT00:00:00Z')
            end_date = (target_date + timedelta(days=1)).strftime('%Y-%m-%dT00:00:00Z')
            
            # Build the filter query
            filter_query = f"receivedDateTime ge {start_date} and receivedDateTime lt {end_date}"
            
            # API endpoint for messages
            url = f"{GRAPH_API_ENDPOINT}/me/messages"
            
            # Parameters for the request
            params = {
                '$filter': filter_query,
                '$select': 'id,subject,bodyPreview,body,from,toRecipients,ccRecipients,receivedDateTime,importance,hasAttachments',
                '$orderby': 'receivedDateTime desc',
                '$top': 999  # Maximum number of emails to fetch
            }
            
            emails = []
            
            # Handle pagination
            while url:
                response = requests.get(url, headers=self.headers, params=params if url == f"{GRAPH_API_ENDPOINT}/me/messages" else None)
                
                if response.status_code == 200:
                    data = response.json()
                    emails.extend(data.get('value', []))
                    
                    # Check for next page
                    url = data.get('@odata.nextLink')
                    params = None  # Clear params for subsequent requests
                    
                else:
                    st.error(f"Failed to fetch emails: {response.status_code} - {response.text}")
                    break
            
            # Process and clean the emails
            processed_emails = []
            for email in emails:
                processed_email = self._process_email(email)
                if processed_email:
                    processed_emails.append(processed_email)
            
            return processed_emails
            
        except Exception as e:
            st.error(f"Error fetching emails: {str(e)}")
            return []
    
    def _process_email(self, email: Dict) -> Optional[Dict]:
        """
        Process and clean individual email data
        
        Args:
            email: Raw email data from Graph API
            
        Returns:
            Processed email dictionary
        """
        try:
            # Extract sender information
            sender = email.get('from', {})
            sender_name = sender.get('emailAddress', {}).get('name', 'Unknown')
            sender_email = sender.get('emailAddress', {}).get('address', 'Unknown')
            
            # Extract recipients
            to_recipients = []
            for recipient in email.get('toRecipients', []):
                to_recipients.append({
                    'name': recipient.get('emailAddress', {}).get('name', 'Unknown'),
                    'email': recipient.get('emailAddress', {}).get('address', 'Unknown')
                })
            
            cc_recipients = []
            for recipient in email.get('ccRecipients', []):
                cc_recipients.append({
                    'name': recipient.get('emailAddress', {}).get('name', 'Unknown'),
                    'email': recipient.get('emailAddress', {}).get('address', 'Unknown')
                })
            
            # Extract body content
            body = email.get('body', {})
            body_content = body.get('content', '')
            body_type = body.get('contentType', 'text')
            
            # Clean HTML content if needed
            if body_type.lower() == 'html':
                body_content = self._clean_html_content(body_content)
            
            # Create processed email object
            processed_email = {
                'id': email.get('id', ''),
                'subject': email.get('subject', 'No Subject'),
                'body_preview': email.get('bodyPreview', ''),
                'body_content': body_content,
                'body_type': body_type,
                'sender_name': sender_name,
                'sender_email': sender_email,
                'to_recipients': to_recipients,
                'cc_recipients': cc_recipients,
                'received_datetime': email.get('receivedDateTime', ''),
                'importance': email.get('importance', 'normal'),
                'has_attachments': email.get('hasAttachments', False)
            }
            
            return processed_email
            
        except Exception as e:
            print(f"Error processing email: {str(e)}")
            return None
    
    def _clean_html_content(self, html_content: str) -> str:
        """
        Clean HTML content to extract plain text
        
        Args:
            html_content: HTML content string
            
        Returns:
            Cleaned plain text
        """
        try:
            # Simple HTML tag removal (for more robust cleaning, consider using BeautifulSoup)
            import re
            
            # Remove HTML tags
            clean_text = re.sub(r'<[^>]+>', '', html_content)
            
            # Replace HTML entities
            clean_text = clean_text.replace('&nbsp;', ' ')
            clean_text = clean_text.replace('&amp;', '&')
            clean_text = clean_text.replace('&lt;', '<')
            clean_text = clean_text.replace('&gt;', '>')
            clean_text = clean_text.replace('&quot;', '"')
            clean_text = clean_text.replace('&#39;', "'")
            
            # Clean up whitespace
            clean_text = re.sub(r'\s+', ' ', clean_text)
            clean_text = clean_text.strip()
            
            return clean_text
            
        except Exception as e:
            print(f"Error cleaning HTML content: {str(e)}")
            return html_content
    
    def get_email_summary(self, emails: List[Dict]) -> Dict:
        """
        Generate a summary of fetched emails
        
        Args:
            emails: List of email dictionaries
            
        Returns:
            Summary dictionary
        """
        if not emails:
            return {
                'total_emails': 0,
                'senders': [],
                'subjects': [],
                'importance_breakdown': {}
            }
        
        # Count emails by sender
        sender_counts = {}
        subjects = []
        importance_counts = {'low': 0, 'normal': 0, 'high': 0}
        
        for email in emails:
            sender = email.get('sender_email', 'Unknown')
            sender_counts[sender] = sender_counts.get(sender, 0) + 1
            subjects.append(email.get('subject', 'No Subject'))
            
            importance = email.get('importance', 'normal').lower()
            if importance in importance_counts:
                importance_counts[importance] += 1
        
        # Sort senders by email count
        top_senders = sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_emails': len(emails),
            'senders': top_senders,
            'subjects': subjects[:20],  # Top 20 subjects
            'importance_breakdown': importance_counts
        }
