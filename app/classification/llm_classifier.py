import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

CATEGORIES = ["urgent", "billing", "support", "junk"]

PROMPT_TEMPLATE = """You are a support ticket classifier. Classify the following
ticket into exactly one of these categories: {categories}.

Respond with ONLY valid JSON, no markdown formatting, no explanation, in this
exact shape:
{{"category": "<one of {categories}>", "confidence": <float between 0 and 1>}}

Subject: {subject}
Body: {body}
"""

def classify_llm(subject: str, body: str) -> dict:
    """
    Build the prompt from PROMPT_TEMPLATE, call client.interactions.create(...),
    parse interaction.output_text as JSON.
    Validate: category must be one of CATEGORIES, confidence must be a float
    between 0 and 1 — if either check fails, raise ValueError (don't silently
    accept garbage).
    Let any exception (network error, JSON parse failure, validation failure)
    propagate up — the caller (the dispatcher we build next) is responsible
    for catching it and falling back, not this function.
    """

    prompt = PROMPT_TEMPLATE.format(
        categories=CATEGORIES, 
        subject=subject, 
        body=body
    )

    response= client.interactions.create(
        model="gemini-3.5-flash-lite",
        input=prompt
    )

    output= response.output_text
    if output.startswith("```"):
        output = output.strip("`").removeprefix("json").strip()
    data= json.loads(output)


    category= data.get("category")
    confidence = data.get("confidence")
    if category not in CATEGORIES:
        raise ValueError(f" Invalid category returned: {category}")
    if not isinstance(confidence, float) or not (0 <= confidence <= 1):
        raise ValueError(f"Invalid confidence score: {confidence}. Must be a float between 0 and 1 ")

    return data




