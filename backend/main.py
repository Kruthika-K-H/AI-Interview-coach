from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from llm_service import (
    analyze_resume_jd,
    analyze_answer,
    analyze_coding_answer,
    calculate_ats_score,
    generate_prep_guide,
    get_top_weaknesses,
)
from database import get_db
from models import InterviewSession, Answer as AnswerModel
import pdfplumber
import docx
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-interview-coach-ten-psi.vercel.app",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join(para.text for para in doc.paragraphs)


@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    file_bytes = await file.read()

    if file.filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    elif file.filename.endswith(".docx"):
        text = extract_text_from_docx(file_bytes)
    else:
        return {"error": "Unsupported file type. Please upload a .pdf or .docx file."}

    return {
        "filename": file.filename,
        "text_length": len(text),
        "extracted_text": text
    }


@app.post("/create-session")
async def create_session(db: Session = Depends(get_db)):
    new_session = InterviewSession(resume_text="", jd_text="")
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {"session_id": new_session.id}


@app.get("/weakness-history")
async def weakness_history(db: Session = Depends(get_db)):
    all_answers = db.query(AnswerModel).all()
    tags_lists = [a.weakness_tags for a in all_answers]
    top = get_top_weaknesses(tags_lists)
    return {"top_weaknesses": [{"tag": t, "count": c} for t, c in top]}


class AnalyzeRequest(BaseModel):
    resume_text: str
    jd_text: str


@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    result = analyze_resume_jd(request.resume_text, request.jd_text)
    return result


@app.post("/ats-score")
async def ats_score(request: AnalyzeRequest):
    result = calculate_ats_score(request.resume_text, request.jd_text)
    return result


@app.post("/prep-guide")
async def prep_guide(request: AnalyzeRequest):
    result = generate_prep_guide(request.resume_text, request.jd_text)
    return result


class AnswerRequest(BaseModel):
    question: str
    answer: str
    session_id: Optional[int] = None


@app.post("/answer")
async def answer(request: AnswerRequest, db: Session = Depends(get_db)):
    result = analyze_answer(request.question, request.answer)
    if request.session_id and "weakness_tags" in result:
        new_answer = AnswerModel(
            session_id=request.session_id,
            answer_text=request.answer,
            score=result.get("score"),
            feedback_text=result.get("feedback_summary"),
            weakness_tags=",".join(result.get("weakness_tags", []))
        )
        db.add(new_answer)
        db.commit()
    return result


@app.post("/answer-coding")
async def answer_coding(request: AnswerRequest, db: Session = Depends(get_db)):
    result = analyze_coding_answer(request.question, request.answer)
    if request.session_id and "weakness_tags" in result:
        new_answer = AnswerModel(
            session_id=request.session_id,
            answer_text=request.answer,
            score=result.get("score"),
            feedback_text=result.get("feedback_summary"),
            weakness_tags=",".join(result.get("weakness_tags", []))
        )
        db.add(new_answer)
        db.commit()
    return result


@app.get("/")
def root():
    return {"message": "AI Interview Coach backend is running"}