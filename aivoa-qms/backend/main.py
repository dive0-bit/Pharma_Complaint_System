from fastapi import FastAPI, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal
from ai_agent import run_agent
import pdfplumber
import io

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AIVOA QMS Copilot API")

# --- CORS SETUP (Yeh React ko connect karne dega) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- DB Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ChatRequest(BaseModel):
    message: str


class ComplaintForm(BaseModel):
    product_name: str
    batch_number: str
    originating_site: str
    impacted_npm: str
    complaint_category: str
    product_defect: str
    complaint_description: str
    severity: str
    suggested_next_action: str
    initial_risk_assessment: str


@app.get("/")
def read_root():
    return {"status": "success", "message": "AIVOA Backend is up and running!"}


@app.post("/api/chat")
def chat_with_copilot(request: ChatRequest):
    try:
        ai_reply = run_agent(request.message)
        return {"status": "success", "ai_response": ai_reply}
    except Exception as e:
        return {"status": "error", "exact_error_message": str(e)}


# Tool 3: Document Extraction Tool (PDF upload)
@app.post("/api/upload_document")
async def upload_document(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        text = ""
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

        if not text.strip():
            return {"status": "error", "exact_error_message": "Could not extract text from PDF."}

        ai_reply = run_agent(text)
        return {"status": "success", "ai_response": ai_reply}
    except Exception as e:
        return {"status": "error", "exact_error_message": str(e)}


@app.post("/api/save_complaint")
def save_complaint(complaint: ComplaintForm, db: Session = Depends(get_db)):
    try:
        # Bonus: Duplicate Complaint Detection
        existing = db.query(models.Complaint).filter(
            models.Complaint.batch_number == complaint.batch_number,
            models.Complaint.batch_number != ""
        ).first()
        duplicate_warning = None
        if existing:
            duplicate_warning = f"⚠️ Duplicate batch number found! Existing complaint ID: {existing.id}"

        new_complaint = models.Complaint(
            product_name=complaint.product_name,
            batch_number=complaint.batch_number,
            originating_site=complaint.originating_site,
            impacted_npm=complaint.impacted_npm,
            complaint_category=complaint.complaint_category,
            product_defect=complaint.product_defect,
            complaint_description=complaint.complaint_description,
            severity=complaint.severity,
            suggested_next_action=complaint.suggested_next_action,
            initial_risk_assessment=complaint.initial_risk_assessment
        )
        db.add(new_complaint)
        db.commit()
        db.refresh(new_complaint)

        response = {"status": "success", "message": "Data saved to MySQL successfully!", "id": new_complaint.id}
        if duplicate_warning:
            response["duplicate_warning"] = duplicate_warning

        return response
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}