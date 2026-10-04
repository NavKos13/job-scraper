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
DELETE ME AND FILL IN YOUR PERSONAL CANDIDATE PROFILE HERE
"""


def evaluate_job_post(post_text: str) -> JobEvaluation:
    prompt = f"""
    Analyze the following Linkedin job post (which may be in Hebrew or English) based on the candidate's profile.

    Candidate Profile:
    {CANDIDATE_PROFILE}

    Post Content:
    {post_text}
    """

    # INFO: Choose the model you want to use here.
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