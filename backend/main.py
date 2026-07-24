from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm_service import analyze_resume_jd, analyze_answer, calculate_ats_score, generate_prep_guide
import pdfplumber
import docx
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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


class AnalyzeRequest(BaseModel):
    resume_text: str
    jd_text: str


@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    result = analyze_resume_jd(request.resume_text, request.jd_text)
    return result


class AnswerRequest(BaseModel):
    question: str
    answer: str


@app.post("/answer")
async def answer(request: AnswerRequest):
    result = analyze_answer(request.question, request.answer)
    return result


@app.post("/ats-score")
async def ats_score(request: AnalyzeRequest):
    result = calculate_ats_score(request.resume_text, request.jd_text)
    return result


@app.post("/prep-guide")
async def prep_guide(request: AnalyzeRequest):
    result = generate_prep_guide(request.resume_text, request.jd_text)
    return result


@app.get("/")
def root():
    return {"message": "AI Interview Coach backend is running"}