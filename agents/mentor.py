import ast
import json
import os
import base64
import mimetypes
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage


load_dotenv()
model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")


def _encode_file(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")




def analyze_media_structured(file_path: str) -> str:
    """
    Analyze the uploaded image or video of a craft project.

    Focus the analysis on general craft quality dimensions:
    - Structure: Alignment, balance, symmetry
    - Technique: Precision of folds, stitches, lines, etc.
    - Neatness: Clean execution, absence of wrinkles or gaps
    - Materials: Appropriate use, clarity, or consistency (if visible)
    - Areas for improvement: Clear, actionable suggestions

    Return a structured dictionary with specific observations.
    Avoid general encouragement or introductions.
    Do not refer to yourself or the tool.
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        return {"error": "Unsupported file type."}

    encoded = _encode_file(file_path)
    prompt = f"""
    You are a craft analysis assistant. The user uploaded a {mime_type} of their craft project.
    Please return your observations on the following points:

    - Structure: comment on balance, alignment, or symmetry.
    - Technique: precision of folds, stitches, or construction.
    - Neatness: how polished or clean the work appears.
    - Materials: if visible, comment on appropriateness or consistency.
    - Recommendations: a list of 2–3 actionable improvements.

    Return the comments as a string.
    """

    if mime_type.startswith("video"):
        content = [
            {"type": "text", "text": prompt},
            {"type": "media", "data": encoded, "mime_type": mime_type},
        ]
    elif mime_type.startswith("image"):
        content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": f"data:{mime_type};base64,{encoded}"},
        ]
    else:
        return {"error": "Unsupported media type."}

    response = model.invoke([HumanMessage(content=content)]).content

    try:
        return response
    except Exception:
        return "Failed to load response from media analysis"



# ✅ Final clean, non-repetitive mentor system prompt
mentor_prompt = PromptTemplate.from_template(
    """
    You are Craft Mentor and your job is to help the user understand specific craft terminology and offer guidance on a given craft project.
"""
)

mentor_agent = create_react_agent(
    model=model,
    tools=[],
    prompt=SystemMessage(content=mentor_prompt.format()),
    name="mentor_agent"
)
