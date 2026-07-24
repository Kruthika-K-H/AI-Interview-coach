import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama-3.1-8b-instant"


def analyze_resume_jd(resume_text: str, jd_text: str) -> dict:
    prompt = f"""You are an expert technical interviewer and career coach.

Given the RESUME and JOB DESCRIPTION below, do the following:
1. Identify skills in the resume that match the job description (matched_skills).
2. Identify important skills/requirements from the job description that are missing from the resume (missing_skills).
3. Generate 8 interview questions this candidate should prepare for, based on BOTH the resume and the job description. Mix of categories: technical, behavioral, role-specific.

Return ONLY valid JSON. No markdown, no code fences, no preamble. Format exactly like this:
{{
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "questions": [
    {{"text": "question text", "category": "technical"}},
    {{"text": "question text", "category": "behavioral"}},
    {{"text": "question text", "category": "role-specific"}}
  ]
}}

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    raw_output = response.choices[0].message.content.strip()
    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`")
        raw_output = raw_output.replace("json\n", "", 1).strip()
    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError:
        result = {"error": "Failed to parse LLM response as JSON", "raw_output": raw_output}
    return result


def analyze_answer(question: str, answer: str) -> dict:
    prompt = f"""You are an expert interview coach evaluating a candidate's spoken/written answer.

QUESTION:
{question}

CANDIDATE'S ANSWER:
{answer}

Evaluate the answer on: structure (clear beginning/middle/end), technical accuracy, communication clarity, and completeness.

Return ONLY valid JSON, no markdown, no preamble, in this exact format:
{{
  "score": <integer 1-10>,
  "strengths": ["point1", "point2"],
  "improvements": ["point1", "point2"],
  "feedback_summary": "one paragraph overall feedback"
}}
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    raw_output = response.choices[0].message.content.strip()
    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`")
        raw_output = raw_output.replace("json\n", "", 1).strip()
    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError:
        result = {"error": "Failed to parse LLM response as JSON", "raw_output": raw_output}
    return result


def calculate_ats_score(resume_text: str, jd_text: str) -> dict:
    prompt = f"""You are an ATS (Applicant Tracking System) simulator.

Given the RESUME and JOB DESCRIPTION below, calculate an ATS compatibility score (0-100) based on:
- Keyword overlap between resume and JD
- Presence of standard resume sections (Education, Experience, Skills, Projects)
- Formatting simplicity signals (bullet points, clear headers)

Return ONLY valid JSON, no markdown, no preamble:
{{
  "ats_score": <integer 0-100>,
  "keyword_matches": ["keyword1", "keyword2"],
  "keyword_gaps": ["keyword1", "keyword2"],
  "formatting_notes": "one sentence on formatting/structure"
}}

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    raw_output = response.choices[0].message.content.strip()
    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`")
        raw_output = raw_output.replace("json\n", "", 1).strip()
    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError:
        result = {"error": "Failed to parse LLM response as JSON", "raw_output": raw_output}
    return result


def generate_prep_guide(resume_text: str, jd_text: str) -> dict:
    prompt = f"""You are a placement preparation coach. Analyze the RESUME and JOB DESCRIPTION below.

Return ONLY valid JSON, no markdown, no preamble, in this exact format:
{{
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "prep_guide": {{
    "topics_to_study": ["topic1", "topic2"],
    "resources": ["resource1", "resource2"]
  }},
  "questions": {{
    "coding": [{{"text": "...", "difficulty": "easy|medium|hard"}}],
    "aptitude": [{{"text": "...", "difficulty": "easy|medium|hard"}}],
    "hr_behavioral": [{{"text": "..."}}],
    "company_specific": [{{"text": "..."}}]
  }}
}}

Generate 3-4 questions per category. For coding/aptitude, infer likely question style from the company/role in the JD (e.g. product-based companies favor DSA, service-based favor aptitude+basics, consulting/analytics roles favor case-study style). For company_specific, use clues from the JD (industry, product, role focus) to generate realistic questions this specific company might ask.

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    raw_output = response.choices[0].message.content.strip()
    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`")
        raw_output = raw_output.replace("json\n", "", 1).strip()
    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError:
        result = {"error": "Failed to parse LLM response as JSON", "raw_output": raw_output}
    return result