# Email Query App with LangChain

A powerful application that connects to your Outlook mailbox, fetches emails from a selected day, and answers natural language questions about them using LangChain and OpenAI.

## 🚀 Features

- **Microsoft Graph API Integration**: Secure authentication and email fetching from Outlook
- **LangChain-Powered QA**: Natural language question answering about your emails
- **Vector Database Storage**: Efficient email storage and retrieval using ChromaDB
- **Interactive Web Interface**: User-friendly Streamlit interface
- **Date-Based Email Filtering**: Fetch emails from any specific date
- **Intelligent Email Analysis**: Get insights about senders, subjects, and content

## 📋 Requirements

- Python 3.8+
- Microsoft Azure App Registration (for Graph API access)
- OpenAI API Key
- Outlook/Office 365 account

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd email-query-app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root and add the following:
   ```env
   # Microsoft Graph API Configuration
   CLIENT_ID=your_client_id_here
   CLIENT_SECRET=your_client_secret_here
   TENANT_ID=your_tenant_id_here
   REDIRECT_URI=http://localhost:8080

   # OpenAI API Key
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## 🔧 Azure App Registration Setup

To use Microsoft Graph API, you need to register an application in Azure:

1. **Go to Azure Portal**
   - Navigate to [Azure Portal](https://portal.azure.com)
   - Go to "Azure Active Directory" > "App registrations"

2. **Create New Registration**
   - Click "New registration"
   - Name: "Email Query App"
   - Supported account types: "Accounts in this organizational directory only"
   - Redirect URI: "Web" - `http://localhost:8080`

3. **Configure API Permissions**
   - Go to "API permissions"
   - Add permissions: Microsoft Graph > Delegated permissions
   - Add: `Mail.Read` and `User.Read`
   - Grant admin consent (if required)

4. **Create Client Secret**
   - Go to "Certificates & secrets"
   - Create new client secret
   - Copy the secret value (you won't see it again!)

5. **Get Application Details**
   - Copy the Application (client) ID
   - Copy the Directory (tenant) ID
   - Add these to your `.env` file

## 🚀 Usage

1. **Start the application**
   ```bash
   streamlit run app.py
   ```

2. **Access the web interface**
   - Open your browser to `http://localhost:8501`

3. **Authenticate with Microsoft**
   - Click the authentication link
   - Sign in with your Outlook/Office 365 account
   - Grant permissions to the app

4. **Fetch emails**
   - Select a date from the sidebar
   - Click "Fetch Emails" to retrieve emails from that day

5. **Ask questions**
   - Type natural language questions about your emails
   - Use sample questions or create your own
   - Get AI-powered answers with source email references

## 💡 Sample Questions

- "What are the most important emails I received?"
- "Who sent me the most emails today?"
- "Are there any meeting invitations?"
- "What emails require my immediate attention?"
- "Summarize the main topics discussed in my emails"
- "Are there any urgent requests or deadlines mentioned?"
- "What emails are from my manager or colleagues?"

## 📁 Project Structure

```
email-query-app/
├── app.py                 # Main Streamlit application
├── auth.py               # Microsoft Graph API authentication
├── email_fetcher.py      # Email fetching from Outlook
├── langchain_setup.py    # LangChain and ChromaDB setup
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── env_example.txt       # Environment variables template
├── README.md            # This file
└── chroma_db/           # ChromaDB vector database (created automatically)
```

## 🔒 Security & Privacy

- **Local Processing**: All email data is processed locally on your machine
- **Secure Authentication**: Uses Microsoft's official MSAL library
- **No Data Storage**: Emails are only stored temporarily in the local vector database
- **API Key Protection**: Environment variables keep your API keys secure

## 🛠️ Technical Details

### Technologies Used
- **LangChain**: For document processing and question-answering chains
- **ChromaDB**: Vector database for efficient email storage and retrieval
- **OpenAI GPT**: Large language model for natural language understanding
- **Microsoft Graph API**: For secure Outlook email access
- **MSAL**: Microsoft Authentication Library for secure login
- **Streamlit**: Web interface framework

### Architecture
1. **Authentication Layer**: MSAL handles Microsoft Graph API authentication
2. **Data Fetching**: Graph API retrieves emails for the selected date
3. **Document Processing**: LangChain converts emails to searchable documents
4. **Vector Storage**: ChromaDB stores email embeddings for fast retrieval
5. **Question Answering**: RetrievalQA chain processes questions and returns answers
6. **User Interface**: Streamlit provides an interactive web interface

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check your Azure app registration settings
   - Verify CLIENT_ID, CLIENT_SECRET, and TENANT_ID in .env file
   - Ensure redirect URI matches Azure configuration

2. **No Emails Found**
   - Verify the selected date has emails
   - Check if your account has the necessary permissions
   - Try a different date range

3. **OpenAI API Errors**
   - Verify your OpenAI API key is correct
   - Check your OpenAI account has sufficient credits
   - Ensure API key has proper permissions

4. **ChromaDB Issues**
   - Delete the `chroma_db` folder and restart the app
   - Check disk space availability
   - Verify write permissions in the project directory

### Getting Help

If you encounter issues:
1. Check the Streamlit error messages in the web interface
2. Look at the console output where you ran `streamlit run app.py`
3. Verify all environment variables are set correctly
4. Ensure all dependencies are installed properly

## 📝 License

This project is for educational purposes. Please ensure compliance with your organization's email and data policies.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and enhancement requests.

---

**Note**: This application requires proper Microsoft Graph API permissions and OpenAI API access. Make sure you have the necessary credentials and permissions before running the application.
