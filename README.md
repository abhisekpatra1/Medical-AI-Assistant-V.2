# 🏥 Medical AI Assistant V.2

A comprehensive AI-powered medical document assistant that leverages advanced language models and vector databases to process, analyze, and extract insights from medical documents.

## ✨ Features

- **Document Upload & Processing**: Support for PDF, DOCX, XLSX, PNG, JPG formats
- **Intelligent Q&A**: Chat interface with document context awareness and source citations
- **Report Generation**: Automated medical report creation with customizable sections
- **Session Management**: Track and maintain conversation history across sessions
- **Vector Database**: ChromaDB integration for efficient document retrieval
- **Multi-Agent Architecture**: Specialized agents for different tasks (document loading, QA, extraction, report generation)

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Google API Key (for Gemini models)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/abhisekpatra1/Medical-AI-Assistant-V.2.git
cd Medical-AI-Assistant-V.2
```

### 2. Create Virtual Environment (Optional but Recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the root directory with the following configuration:

```env
# Google AI Configuration
GOOGLE_API_KEY=your_api_key_here
GOOGLE_MODEL=gemini-2.5-flash
GOOGLE_EMBEDDING_MODEL=models/embedding-001

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Storage Configuration
VECTOR_DB_DIR=data/chroma
SESSION_STORAGE_DIR=data/sessions
UPLOAD_DIR=uploads
REPORT_DIR=reports

# Logging
LOG_LEVEL=INFO
```

## 🎯 Quick Start

### Starting the Backend Server

Run the FastAPI backend server:

```bash
python -m backend.main
```

The backend will start on `http://localhost:8000`

### Starting the Frontend Interface

In a new terminal, run the Streamlit frontend:

```bash
streamlit run app.py
```

The frontend will be available at `http://localhost:8501`

## 📱 Usage

### 1. Upload Medical Documents
- Click "Upload medical documents" in the sidebar
- Select one or more files (PDF, DOCX, XLSX, PNG, JPG)
- Click "Process Documents" to process and index them

### 2. Chat with Your Documents
- Navigate to the "Chat" tab
- Ask questions about your uploaded documents
- View sources and citations for each answer
- Check full chunk content using the "Show Full Chunk Content" checkbox

### 3. Generate Medical Reports
- Go to the "Generate Report" tab
- Select sections to include:
  - Introduction
  - Clinical Findings
  - Patient Tables
  - Graphs & Charts
  - Summary
- Click "Generate Report" to create a PDF
- Download the generated report

## 🏗️ Project Structure

```
Medical-AI-Assistant-V.2/
├── backend/
│   ├── main.py                 # FastAPI application & endpoints
│   ├── agents/
│   │   ├── orchestrator.py     # Coordinates agent workflows
│   │   ├── document_loader.py  # Document processing agent
│   │   ├── qa_agent.py         # Q&A processing agent
│   │   ├── extraction_agent.py # Data extraction agent
│   │   └── report_agent.py     # Report generation agent
│   └── services/
│       ├── vector_store.py     # ChromaDB management
│       └── session_manager.py  # Session & conversation tracking
├── app.py                      # Streamlit frontend
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── uploads/                    # Temporary upload storage
├── reports/                    # Generated PDF reports
├── data/
│   ├── chroma/                 # Vector database
│   └── sessions/               # Session data storage
└── README.md
```

## 🔌 API Endpoints

### Health Check
- **GET** `/` - Service health check

### Document Management
- **POST** `/upload` - Upload and process documents
  - Parameters: `session_id` (query), `files` (multipart)
  
### Chat Interface
- **POST** `/chat` - Send chat message
  - Body: `{ "session_id": "string", "message": "string" }`
  - Returns: `{ "response": "string", "sources": [...], "citations": [...] }`

### Report Generation
- **POST** `/generate-report` - Generate medical report
  - Body: `{ "session_id": "string", "sections": ["string"] }`
  - Returns: `{ "report_path": "string", "session_id": "string" }`

### File Download
- **GET** `/download-report/{session_id}/{filename}` - Download PDF report

### Session Management
- **GET** `/sessions/{session_id}/history` - Retrieve chat history
- **DELETE** `/sessions/{session_id}` - Delete session and data

## 🛠️ Technologies Used

### Core Framework
- **FastAPI** - Web framework for backend API
- **Streamlit** - Frontend UI framework
- **LangChain** - LLM orchestration and utilities
- **LangGraph** - Agent workflow management

### AI & Language Models
- **Google Generative AI** - Gemini models for text generation
- **Sentence Transformers** - Embedding models
- **ChromaDB** - Vector database for semantic search

### Document Processing
- **PyPDF2** - PDF processing
- **python-docx** - Word document handling
- **openpyxl** - Excel file processing
- **Pillow** - Image processing
- **pytesseract** - OCR for images

### Data & Storage
- **SQLAlchemy** - Database ORM
- **pandas** - Data manipulation
- **reportlab** - PDF generation

### Logging & Monitoring
- **loguru** - Advanced logging
- **OpenTelemetry** - Observability

## 🔐 Security Notes

- Store your `GOOGLE_API_KEY` securely in environment variables
- Never commit `.env` file with actual credentials
- API endpoints currently allow all origins (CORS) - configure appropriately for production
- File paths are validated to prevent directory traversal attacks

## 📝 Configuration Details

### Storage Directories
The application creates the following directories automatically:
- `uploads/` - Temporary storage for uploaded files
- `reports/` - Generated PDF reports
- `data/chroma/` - Vector database files
- `data/sessions/` - Session data and conversation history

### Logging
Logging level can be configured via the `LOG_LEVEL` environment variable (INFO, DEBUG, WARNING, ERROR)

## 🐛 Troubleshooting

### Backend Connection Error
- Ensure backend server is running: `python -m backend.main`
- Check if port 8000 is available
- Verify API_HOST and API_PORT in .env file

### Document Processing Issues
- Check file format is supported (PDF, DOCX, XLSX, PNG, JPG)
- Ensure sufficient disk space in upload directory
- Check LOG_LEVEL=DEBUG for detailed error messages

### API Key Issues
- Verify GOOGLE_API_KEY is set correctly in .env
- Ensure API key has proper permissions
- Check rate limits on API usage

## 📚 Dependencies

Key packages included:
- FastAPI 0.109.0
- Streamlit 1.55.0
- LangChain 1.2.13
- ChromaDB 0.4.22
- Google Generative AI 0.3.2
- PyPDF2 3.0.1

See `requirements.txt` for complete dependency list.

## 📄 To Run this:

### Option 1: Update and Run
Update the GOOGLE_API_KEY=API-KEY

```bash
python -m backend.main
```

In another terminal:
```bash
streamlit run app.py
```

### Option 2: Using Environment File
Update the `.env` file to:
```
GOOGLE_API_KEY=API-KEY
GOOGLE_MODEL='gemini-2.5-flash'
GOOGLE_EMBEDDING_MODEL='models/embedding-001'
API_HOST=0.0.0.0
API_PORT=8000
VECTOR_DB_DIR=data/chroma
SESSION_STORAGE_DIR=data/sessions
UPLOAD_DIR=uploads
REPORT_DIR=reports
LOG_LEVEL=INFO
```

Then run:
```bash
python -m backend.main
```

And in another terminal:
```bash
streamlit run app.py
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is provided as-is for educational and research purposes.

## 📧 Support

For issues, questions, or suggestions, please open an issue on the GitHub repository.

---

**Version:** 2.0  
**Last Updated:** 2026  
🏥 Making healthcare document management smarter with AI
