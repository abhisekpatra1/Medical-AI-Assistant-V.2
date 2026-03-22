## To Run this:
Update the GOOGLE_API_KEY=API-KEY

python -m backend.main

streamlit run app.py


## To Run this:
# Update the .env file to:
GOOGLE_API_KEY=API-KEY
GOOGLE_MODEL='gemini-2.5-flash'
GOOGLE_EMBEDDING_MODEL='models/embedding-001'#not used in this project
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
