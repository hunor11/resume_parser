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

4. **Process initial data (optional)**

   ```sh
   make process_data
   ```

## Running the Application

- **Start the backend server**
  
  ```sh
  make run_server
  ```

- **Start the frontend**
  
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