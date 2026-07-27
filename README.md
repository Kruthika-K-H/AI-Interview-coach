# AI Interview Coach

An AI-powered, chatbot-style placement preparation tool that goes beyond generic Q&A. It analyzes your resume against a specific job description to generate an ATS compatibility score, skill-gap analysis, and a categorized practice guide -- then tracks your recurring weaknesses across sessions, so every practice round builds on the last instead of starting from zero.

Built as part of active campus placement preparation, using real job descriptions from companies like Celonis, Boeing, and Infosys as test cases.

## Live Demo

- **Live App:** https://ai-interview-coach-ten-psi.vercel.app
- **Live API docs:** https://ai-interview-coach-backend-qqrl.onrender.com/docs
- **GitHub Repo:** https://github.com/Kruthika-K-H/AI-Interview-coach

Note: the backend runs on Render's free tier, so if it's been idle, the first request may take 30-50 seconds while it spins back up.

---

## Why this is different

Most AI interview prep tools generate questions from a resume/JD and score your answers in isolation -- every session is a blank slate. This tool persists feedback across sessions: each answer is tagged with the specific weakness it revealed (e.g., "quantification," "technical depth," "structure"), and before your next practice session starts, the bot tells you what's been coming up repeatedly -- so you know exactly what to focus on.

It also separates coding evaluation from general answer scoring entirely. A behavioral answer and a coding answer are judged on completely different criteria (communication and structure vs. correctness, edge cases, and time/space complexity), so feedback is actually relevant to what you were asked.

---

## Features

- **Resume parsing** -- upload a PDF or DOCX, extracts clean text automatically
- **ATS Score** -- simulates applicant tracking system compatibility (0-100) with keyword match/gap breakdown
- **Skill Gap Analysis** -- compares resume against the job description, flags matched and missing skills
- **Categorized Prep Guide** -- generates practice questions across four categories: Coding, Aptitude, HR/Behavioral, and Company-Specific, plus a study plan with recommended topics and resources
- **Dedicated Coding Evaluation** -- coding answers are assessed separately on correctness, edge cases, and time/space complexity -- not generic communication feedback
- **Cross-Session Weakness Tracking** -- every answer is tagged with its weak point; recurring patterns are surfaced automatically at the start of your next session
- **Chatbot Interface** -- the entire flow happens in a single conversational UI, no page navigation

---

## Tech Stack

**Backend:** Python, FastAPI, SQLAlchemy, SQLite, Groq API (Llama 3.1 8B Instant), pdfplumber, python-docx

**Frontend:** React (Vite), Axios, plain CSS

**Deployment:** Render (backend), Vercel (frontend)

---

## Architecture

```
   React UI  ------->  FastAPI Backend  ------->  Groq LLM (Llama 3.1)
  (Chatbot)  <-------  (Python)         <-------
                            |
                            v
                      SQLite DB
                (sessions, answers,
                  weakness tags)
```

---

## Project Structure

```
ai-interview-coach/
├── backend/
│   ├── main.py            # FastAPI app, all API endpoints
│   ├── llm_service.py     # All Groq/LLM prompt logic
│   ├── models.py          # SQLAlchemy database models
│   ├── database.py        # DB session dependency
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # Main chatbot UI
│   │   └── App.css
│   └── package.json
└── README.md
```

---

## Setup & Installation (running locally)

### Prerequisites
- Python 3.10+
- Node.js 18+
- A free Groq API key from https://console.groq.com

### Backend

```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file inside `backend/`:

```
GROQ_API_KEY=your_groq_api_key_here
```

Initialize the database:

```
python -c "from models import init_db; init_db()"
```

Run the backend:

```
uvicorn main:app --reload
```

Backend runs at http://127.0.0.1:8000 -- interactive API docs at http://127.0.0.1:8000/docs

### Frontend

In a separate terminal:

```
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:5173

Note: both servers must be running simultaneously. Also update `API_BASE` in `frontend/src/App.jsx` back to `http://127.0.0.1:8000` if testing locally against a local backend.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /upload-resume | Parses PDF/DOCX resume, returns extracted text |
| POST | /create-session | Creates a new practice session |
| GET | /weakness-history | Returns top recurring weakness tags across past sessions |
| POST | /analyze | Skill-gap analysis + general interview questions |
| POST | /ats-score | ATS compatibility score with keyword breakdown |
| POST | /prep-guide | Categorized practice questions + study plan |
| POST | /answer | Scores a non-coding answer, stores feedback + weakness tags |
| POST | /answer-coding | Scores a coding answer (correctness/complexity), stores feedback + tags |

---

## How the AI-generated questions work (honesty note)

The categorized and company-specific questions are generated by an LLM reasoning over the job description and resume text -- they are not scraped from real interview databases or leaked question banks. For well-known companies, the model can often infer relevant themes (industry, tools, role focus) from the JD itself. This is the same approach used by most LLM-based prep tools; it's disclosed here for transparency rather than overclaiming accuracy.

Similarly, coding answers are evaluated through LLM reasoning about correctness and complexity -- the code is not executed in a sandboxed runtime.

---

## Known Limitations / Future Work

- No user authentication -- sessions are currently anonymous
- Voice input/output not yet implemented
- No PDF export of session reports
- Mock interview mode (adaptive multi-turn follow-ups) not yet implemented
- Backend free-tier hosting means occasional cold-start delays

---

## Author

**Kruthika K H**

B.E. Computer Science and Business Systems, Nitte Meenakshi Institute of Technology

LinkedIn: linkedin.com/in/kruthika-k-h-67650936b

GitHub: github.com/Kruthika-K-H