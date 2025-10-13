# Resume Parser Setup Guide

## Prerequisites

- Python 3.12+
- Node.js 18+
- npm
- Make

## Setup Instructions

1. **Clone the repository**

   ```sh
   git clone https://github.com/hunor11/resume_parser.git
   cd resume_parser
   ```

2. **Set up the backend**

   ```sh
   make setup_server
   ```

3. **Set up the frontend**

   ```sh
   make setup_frontend
   ```

4. **Process initial dummy data (optional)**

    Unzip and process a kaggle resume dataset (data/UpdatedResumeDataset.csv.zip) for testing if needed.

   ```sh
   make process_data
   ```

## Running the Application

- **Start the backend server**
  Runs on localhost:8000

  ```sh
  make run_server
  ```

- **Start the frontend**
  Runs on localhost:3000
  
  ```sh
  make run_frontend
  ```

## Development Tools

- **Lint and format backend code**
  
  ```sh
  make lint
  make format
  ```

## Notes

- The backend runs on Uvicorn (FastAPI).
- The frontend uses Next.js (React).
- Make sure to activate the Python virtual environment if running scripts manually.

## Features

**Tech Stack:**

- **FastAPI**: Framework for backend.
- **Uvicorn**: Server for running FastAPI.
- **PostgreSQL (Aiven)**: Cloud-hosted relational database for storing chat-history, resume metadata, and parsed data.
- **LangChain**: For orchestrating LLM and embedding workflows.
- **Gemini API**: Utilized for chat.
- **Huggingface all-MiniLM-L6-v2**: Utilized for embeddings
- **PyPDF2**: For parsing and extracting text from PDF resumes.
- **NextJS**: For creating a simple UI for the chatbot
- **MaterialUI**: For creating a user friendly UI

**Available Features:**

- **Resume Upload & Storage:** Accepts .pdf/.txt resumes, stores files and metadata (in postgres vectordb)
- **Resume Parsing:** Extracts structured information from resumes with top_k similarity included
- **Embedding Generation:** Uses all-MiniLM-L6-v2 to create document ebeddings from huggingface
- **Database Integration:** Stores uploads, parsed data, and session info in PostgreSQL (Aiven).
- **Session Management:** Tracks user sessions (chat-history and resumes are stored int postrgres per session, meaning that a user can acces only resumes uploaded in a given session).
- **AI Chat:**
  - Gemini chat-model to interact with and read the stored resumes
  - Minimal promp-engineering to clarify its job

- **Frontend web-application:** A NextJs web application for interacting with the chatbot and session
