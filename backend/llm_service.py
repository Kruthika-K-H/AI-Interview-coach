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
  "weakness_tags": ["tag1", "tag2"],
  "feedback_summary": "one paragraph overall feedback"
}}

For weakness_tags, choose from this fixed list only (pick 0-2 that genuinely apply, empty array if none apply):
["quantification", "structure", "technical_depth", "communication_clarity", "ownership_clarity", "completeness", "confidence"]
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


def analyze_coding_answer(question: str, answer: str) -> dict:
    prompt = f"""You are an expert technical interviewer evaluating a candidate's CODE submission.

CODING QUESTION:
{question}

CANDIDATE'S CODE/ANSWER:
{answer}

Evaluate strictly on:
- Correctness: Does the code actually solve the problem? Would it run without errors?
- Logic: Is the approach/algorithm sound?
- Edge cases: Does it handle them (empty input, negative numbers, etc.)?
- Time/space complexity: Is it efficient, or is there a better approach?

If the code has bugs or wouldn't compile/run, say so explicitly and explain why.
If the logic is fundamentally wrong, say so — don't be lenient just to be encouraging.

Return ONLY valid JSON, no markdown, no preamble:
{{
  "score": <integer 1-10>,
  "correctness": "correct|partially_correct|incorrect",
  "bugs_or_issues": ["issue1", "issue2"],
  "complexity_analysis": "time and space complexity, and whether it's optimal",
  "weakness_tags": ["tag1", "tag2"],
  "improvements": ["suggestion1", "suggestion2"],
  "feedback_summary": "one paragraph overall feedback"
}}

For weakness_tags, choose from this fixed list only (pick 0-2 that genuinely apply, empty array if none apply):
["correctness", "efficiency", "edge_cases", "structure", "technical_depth", "completeness"]
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
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

Generate EXACTLY 3 questions per category — coding, aptitude, hr_behavioral, and company_specific. Do not leave any category empty and do not generate fewer than 3 per category under any circumstances.

For 'coding' questions, generate general data structures/algorithms problems (arrays, strings, recursion, sorting, searching, etc.) appropriate to the seniority level — NOT tool-specific scripting tasks like "write a script to connect to X service."

For 'aptitude', generate logical/quantitative reasoning questions typical of campus placement drives.

For 'company_specific', use clues from the JD (industry, product, role focus) to generate realistic questions this specific company might ask.

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


from collections import Counter

def get_top_weaknesses(all_tags_lists: list) -> list:
    """all_tags_lists = list of comma-separated tag strings from past answers"""
    counter = Counter()
    for tags_str in all_tags_lists:
        if tags_str:
            for tag in tags_str.split(","):
                tag = tag.strip()
                if tag:
                    counter[tag] += 1
    return counter.most_common(3)