"""
Simple Email Search and QA System without LangChain Dependencies
"""
import os
import re
from typing import List, Dict, Tuple
from groq import Groq
import streamlit as st
from config import GROQ_API_KEY


class SimpleEmailStore:
    """Simple email storage and search without vector databases"""
    
    def __init__(self):
        # Set Groq API key
        self.groq_api_key = GROQ_API_KEY
        self.emails = []
        self.processed_emails = []
    
    def store_emails(self, emails: List[Dict]) -> bool:
        """
        Store emails in memory for searching
        
        Args:
            emails: List of email dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.emails = emails
            self.processed_emails = []
            
            for email in emails:
                processed = self._process_email_for_search(email)
                self.processed_emails.append(processed)
            
            st.success(f"Successfully stored {len(emails)} emails for searching")
            return True
            
        except Exception as e:
            st.error(f"Error storing emails: {str(e)}")
            return False
    
    def _process_email_for_search(self, email: Dict) -> Dict:
        """
        Process email for text-based searching
        
        Args:
            email: Email dictionary
            
        Returns:
            Processed email with searchable text
        """
        # Create searchable content
        content_parts = []
        
        # Add subject
        subject = email.get('subject', 'No Subject')
        content_parts.append(f"Subject: {subject}")
        
        # Add sender information
        sender_name = email.get('sender_name', 'Unknown')
        sender_email = email.get('sender_email', 'Unknown')
        content_parts.append(f"From: {sender_name} <{sender_email}>")
        
        # Add recipients
        to_recipients = email.get('to_recipients', [])
        if to_recipients:
            to_list = [f"{r.get('name', 'Unknown')} <{r.get('email', 'Unknown')}>" for r in to_recipients]
            content_parts.append(f"To: {'; '.join(to_list)}")
        
        # Add body content
        body_content = email.get('body_content', '')
        if body_content:
            content_parts.append(f"Content: {body_content}")
        else:
            body_preview = email.get('body_preview', '')
            if body_preview:
                content_parts.append(f"Content: {body_preview}")
        
        searchable_text = "\n\n".join(content_parts).lower()
        
        return {
            'original_email': email,
            'searchable_text': searchable_text,
            'subject': subject,
            'sender_name': sender_name,
            'sender_email': sender_email,
            'received_datetime': email.get('received_datetime', ''),
            'importance': email.get('importance', 'normal')
        }
    
    def search_emails(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search emails using simple text matching
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of matching emails with relevance scores
        """
        if not self.processed_emails:
            return []
        
        query_lower = query.lower()
        query_words = re.findall(r'\b\w+\b', query_lower)
        
        results = []
        
        for processed_email in self.processed_emails:
            score = self._calculate_relevance_score(
                processed_email['searchable_text'], 
                query_lower, 
                query_words
            )
            
            if score > 0:
                results.append({
                    'email': processed_email['original_email'],
                    'score': score,
                    'subject': processed_email['subject'],
                    'sender': processed_email['sender_name'],
                    'received_date': processed_email['received_datetime'],
                    'preview': processed_email['searchable_text'][:200] + "..."
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:max_results]
    
    def _calculate_relevance_score(self, text: str, query: str, query_words: List[str]) -> float:
        """
        Calculate relevance score for text matching
        
        Args:
            text: Text to search in
            query: Full query string
            query_words: List of query words
            
        Returns:
            Relevance score (higher is more relevant)
        """
        score = 0.0
        
        # Exact phrase match (highest score)
        if query in text:
            score += 10.0
        
        # Individual word matches
        for word in query_words:
            if len(word) > 2:  # Skip very short words
                word_count = text.count(word)
                score += word_count * 2.0
        
        # Bonus for matches in subject line
        if 'subject:' in text[:100]:
            subject_line = text[:100].lower()
            for word in query_words:
                if word in subject_line:
                    score += 3.0
        
        return score
    
    def clear_emails(self):
        """Clear stored emails"""
        self.emails = []
        self.processed_emails = []
        st.success("Email database cleared successfully")


class SimpleEmailQA:
    """Simple Question-Answering system for emails using Groq directly"""
    
    def __init__(self, email_store: SimpleEmailStore):
        self.email_store = email_store
        self.client = Groq(api_key=GROQ_API_KEY)
    
    def ask_question(self, question: str) -> Dict:
        """
        Answer a question about the emails
        
        Args:
            question: Natural language question
            
        Returns:
            Dictionary with answer and source emails
        """
        try:
            # Search for relevant emails
            relevant_emails = self.email_store.search_emails(question, max_results=5)
            
            if not relevant_emails:
                return {
                    'answer': "I couldn't find any relevant emails to answer your question. Try asking about different topics or check if emails are loaded.",
                    'sources': [],
                    'question': question
                }
            
            # Prepare context from relevant emails
            context_parts = []
            sources = []
            
            for i, result in enumerate(relevant_emails, 1):
                email = result['email']
                
                # Add to context
                email_context = f"Email {i}:\n"
                email_context += f"Subject: {email.get('subject', 'No Subject')}\n"
                email_context += f"From: {email.get('sender_name', 'Unknown')} <{email.get('sender_email', 'Unknown')}>\n"
                email_context += f"Date: {email.get('received_datetime', 'Unknown')}\n"
                
                body_content = email.get('body_content', '') or email.get('body_preview', '')
                if body_content:
                    # Limit content length for context
                    if len(body_content) > 500:
                        body_content = body_content[:500] + "..."
                    email_context += f"Content: {body_content}\n"
                
                context_parts.append(email_context)
                
                # Add to sources
                sources.append({
                    'subject': result['subject'],
                    'sender': result['sender'],
                    'received_date': result['received_date'],
                    'content_preview': result['preview']
                })
            
            # Create prompt
            context = "\n\n".join(context_parts)
            prompt = f"""You are an AI assistant helping to analyze emails. Use the following email content to answer the question.

Email Content:
{context}

Question: {question}

Please provide a helpful and accurate answer based on the email content. If the information is not available in the emails, please say so clearly. Be concise but informative.

Answer:"""
            
            # Get answer from Groq
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes emails and answers questions about them."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            return {
                'answer': answer,
                'sources': sources,
                'question': question
            }
            
        except Exception as e:
            return {
                'answer': f"Error processing question: {str(e)}",
                'sources': [],
                'question': question
            }
