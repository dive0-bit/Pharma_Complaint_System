# AIVOA QMS - AI-Powered Customer Complaint Management System

An AI-powered Customer Complaint Management System for the pharmaceutical manufacturing industry, built as part of the AIVOA AI Product Engineer internship assignment.

## Tech Stack
- **Frontend:** React + Redux (state management)
- **Backend:** Python FastAPI
- **AI Agent Framework:** LangGraph
- **LLM:** Groq (openai/gpt-oss-120b)
- **Database:** MySQL

## Features
- Chat-based AI Copilot that extracts complaint details from natural language and auto-fills the complaint form
- Smart state merging — new information updates the form without erasing previously extracted fields
- Auto-reset when a completely new/unrelated complaint is detected (different product + defect)
- Edit/correction flow via LangGraph intent routing (Log Complaint vs Edit Complaint tools)
- PDF document upload — extracts complaint details directly from uploaded pharmaceutical complaint PDFs
- Save complaint to MySQL database
- Duplicate complaint detection (by batch number)
- Downloadable PDF report of the logged complaint
- Google Inter font per assignment spec

## Project Structure

Pharma_Complaint_System/
├── aivoa-qms/
│ └── backend/ # FastAPI + LangGraph + Groq backend
│ ├── main.py
│ ├── ai_agent.py
│ ├── models.py
│ ├── database.py
│ └── .env.example
└── frontend/ # React + Redux frontend
└── src/
├── App.jsx
└── store/


## Setup Instructions

### Backend
```bash
cd aivoa-qms/backend
python -m venv venv
venv\Scripts\activate      # Windows
pip install fastapi uvicorn sqlalchemy pymysql langgraph groq python-dotenv pydantic python-multipart pdfplumber

# Copy .env.example to .env and fill in your own values
cp .env.example .env

uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm install @reduxjs/toolkit react-redux axios jspdf
npm run dev
```

### Database
Create a MySQL database named `aivoa_qms`. Tables are auto-created on backend startup.

## AI Agent Architecture (LangGraph)
The backend uses a LangGraph `StateGraph` with two nodes:
- **Log Complaint Tool** — triggered for new complaint narratives
- **Edit Complaint Tool** — triggered when correction keywords (e.g. "sorry", "actually", "wrong") are detected in the message

A conditional entry point routes user messages to the correct tool based on simple intent detection.

## Demo Videos
- Working demo: [link]
- Code walkthrough: [link]