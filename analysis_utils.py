import base64
import json
import mimetypes
import re
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage


model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")


def _encode_file(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")




def safe_json_parse(obj):
    if isinstance(obj, str):
        return json.loads(obj)
    elif isinstance(obj, dict):
        return obj  # already parsed
    else:
        raise TypeError(f"Expected JSON string or dict, got {type(obj)}")



def extract_json(response: str) -> dict:
    # Match inside ```json ... ```
    match = re.search(r"```(?:json)?\s*({.*?})\s*```", response, re.DOTALL)
    
    if match:
        json_str = match.group(1)
    else:
        # Fallback if no code block
        json_str = response.strip()
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        return {"error": "Failed to parse JSON", "raw": response, "details": str(e)}



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