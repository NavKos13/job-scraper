import os
from google import genai
from pydantic import BaseModel, Field

from dotenv import load_dotenv
load_dotenv()

class JobEvaluation(BaseModel):
    is_relevant: bool = Field(description="True if the post is a relevant software/tech job matching criteria.")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    job_title: str = Field(description="Extracted or inferred job title")
    company_name: str = Field(description="Extracted company name, or 'Unknown'")
    reason: str = Field(description="Brief explanation of why it fits or does not fit")

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

CANDIDATE_PROFILE = """
Candidate Context:
- Current 3rd-year Software Engineering undergraduate student at Ben-Gurion University.
- Former Lead Missile Systems Technician (naval electronics/hardware diagnostics).

Acceptance Criteria:
- Experience Level: Student / Intern / Junior / Graduate (0-1 years required experience, or positions accepting current B.Sc. students).
- Primary Tech & Domain (Highest Priority): Low-level, Embedded, Firmware, Systems Programming, or Chip Simulation / Hardware-Software Integration using Rust, C++, or Python.
- Secondary Domain (Accepted): Full Stack, Backend, or Consumer/Desktop/Mobile Application Development (using Rust, Python, C++, C#/.NET, Flutter/Dart, or TypeScript).
- Locations: Be'er Sheva, Southern District (e.g., Ashdod, Omer, Kiryat Gat), Remote, or Hybrid within direct train access from Be'er Sheva (e.g., Rehovot, Tel Aviv).

Strict Rejection Criteria (is_relevant = False):
- Roles requiring 2+ years of professional industry experience (e.g., "3+ years required", Mid-level, Senior, Tech Lead, Staff).
- Roles requiring a degree that does not include Computer Science/Software Engineering
- Positions that explicitly state "Full-time only with degree already completed" when student/part-time flexibility is not offered.
- Non-developer roles (Technical Support, IT Helpdesk, Sales Engineering, Manual QA with no automation/scripting, HR).
- Tech stacks limited entirely to enterprise legacy stacks outside target domains (e.g., pure legacy COBOL, PHP/WordPress).
"""


def evaluate_job_post(post_text: str) -> JobEvaluation:
    prompt = f"""
    Analyze the following Linkedin job post (which may be in Hebrew or English) based on the candidate's profile.

    Candidate Profile:
    {CANDIDATE_PROFILE}

    Post Content:
    {post_text}
    """

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": JobEvaluation,
            "temperature": 0.1,
        },
    )
    
    return JobEvaluation.model_validate_json(response.text)