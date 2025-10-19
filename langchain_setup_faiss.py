"""
LangChain Setup Module with FAISS Vector Database
"""
import os
import pickle
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from typing import List, Dict
import streamlit as st
from config import OPENAI_API_KEY


class EmailVectorStore:
    """Manages email documents in FAISS vector store"""
    
    def __init__(self):
        # Set OpenAI API key
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings()
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Initialize vector store
        self.vector_store = None
        self.faiss_index_path = "./faiss_index"
        self.faiss_pkl_path = "./faiss_index.pkl"
    
    def create_documents_from_emails(self, emails: List[Dict]) -> List[Document]:
        """
        Convert email data to LangChain Document objects
        
        Args:
            emails: List of email dictionaries
            
        Returns:
            List of Document objects
        """
        documents = []
        
        for i, email in enumerate(emails):
            # Create document content
            content = self._format_email_content(email)
            
            # Create metadata
            metadata = {
                'email_id': email.get('id', f'email_{i}'),
                'subject': email.get('subject', 'No Subject'),
                'sender_name': email.get('sender_name', 'Unknown'),
                'sender_email': email.get('sender_email', 'Unknown'),
                'received_datetime': email.get('received_datetime', ''),
                'importance': email.get('importance', 'normal'),
                'has_attachments': email.get('has_attachments', False),
                'to_recipients_count': len(email.get('to_recipients', [])),
                'cc_recipients_count': len(email.get('cc_recipients', []))
            }
            
            # Create document
            document = Document(
                page_content=content,
                metadata=metadata
            )
            
            documents.append(document)
        
        return documents
    
    def _format_email_content(self, email: Dict) -> str:
        """
        Format email data into a readable text format for embedding
        
        Args:
            email: Email dictionary
            
        Returns:
            Formatted email content string
        """
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
        
        cc_recipients = email.get('cc_recipients', [])
        if cc_recipients:
            cc_list = [f"{r.get('name', 'Unknown')} <{r.get('email', 'Unknown')}>" for r in cc_recipients]
            content_parts.append(f"CC: {'; '.join(cc_list)}")
        
        # Add received date
        received_date = email.get('received_datetime', '')
        if received_date:
            content_parts.append(f"Received: {received_date}")
        
        # Add importance
        importance = email.get('importance', 'normal')
        if importance != 'normal':
            content_parts.append(f"Importance: {importance}")
        
        # Add body content
        body_content = email.get('body_content', '')
        if body_content:
            content_parts.append(f"Content: {body_content}")
        else:
            # Fallback to body preview
            body_preview = email.get('body_preview', '')
            if body_preview:
                content_parts.append(f"Content: {body_preview}")
        
        return "\n\n".join(content_parts)
    
    def create_vector_store(self, emails: List[Dict]) -> bool:
        """
        Create and populate vector store with email documents
        
        Args:
            emails: List of email dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not emails:
                st.warning("No emails to process")
                return False
            
            # Create documents from emails
            documents = self.create_documents_from_emails(emails)
            
            # Split documents into chunks
            split_documents = self.text_splitter.split_documents(documents)
            
            # Create FAISS vector store
            self.vector_store = FAISS.from_documents(
                documents=split_documents,
                embedding=self.embeddings
            )
            
            # Save the vector store
            self.vector_store.save_local(self.faiss_index_path)
            
            st.success(f"Successfully created vector store with {len(split_documents)} document chunks")
            return True
            
        except Exception as e:
            st.error(f"Error creating vector store: {str(e)}")
            return False
    
    def load_existing_vector_store(self) -> bool:
        """
        Load existing vector store from disk
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if vector store exists
            if not os.path.exists(f"{self.faiss_index_path}.faiss"):
                return False
            
            # Load existing vector store
            self.vector_store = FAISS.load_local(
                self.faiss_index_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            
            return True
            
        except Exception as e:
            print(f"Error loading existing vector store: {str(e)}")
            return False
    
    def get_vector_store(self):
        """Get the vector store instance"""
        return self.vector_store
    
    def clear_vector_store(self):
        """Clear the vector store"""
        try:
            # Remove FAISS index files
            if os.path.exists(f"{self.faiss_index_path}.faiss"):
                os.remove(f"{self.faiss_index_path}.faiss")
            if os.path.exists(f"{self.faiss_index_path}.pkl"):
                os.remove(f"{self.faiss_index_path}.pkl")
            
            self.vector_store = None
            st.success("Vector store cleared successfully")
        except Exception as e:
            st.error(f"Error clearing vector store: {str(e)}")


class EmailQASystem:
    """Question-Answering system for emails using LangChain"""
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
        
        # Initialize LLM
        self.llm = OpenAI(
            temperature=0.7,
            openai_api_key=OPENAI_API_KEY
        )
        
        # Create custom prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are an AI assistant helping to analyze emails. Use the following email content to answer the question.

Email Content:
{context}

Question: {question}

Please provide a helpful and accurate answer based on the email content. If the information is not available in the emails, please say so clearly.

Answer:"""
        )
        
        # Create RetrievalQA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            ),
            chain_type_kwargs={"prompt": self.prompt_template},
            return_source_documents=True
        )
    
    def ask_question(self, question: str) -> Dict:
        """
        Ask a question about the emails
        
        Args:
            question: Natural language question
            
        Returns:
            Dictionary with answer and source documents
        """
        try:
            # Get answer from QA chain
            result = self.qa_chain({"query": question})
            
            # Extract answer and source documents
            answer = result.get("result", "I couldn't find an answer to your question.")
            source_docs = result.get("source_documents", [])
            
            # Process source documents
            sources = []
            for doc in source_docs:
                metadata = doc.metadata
                sources.append({
                    'subject': metadata.get('subject', 'No Subject'),
                    'sender': metadata.get('sender_name', 'Unknown'),
                    'received_date': metadata.get('received_datetime', ''),
                    'content_preview': doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                })
            
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
