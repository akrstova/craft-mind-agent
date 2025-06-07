import os
import base64
import mimetypes
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage
from langchain.tools import tool

load_dotenv()
model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")


def _encode_file(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


@tool
def analyze_media(file_path: str, craft: str, project: str) -> str:
    """
    Analyze a user's image or video and give feedback on their craft project.
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        return "⚠️ Unsupported file type."

    encoded = _encode_file(file_path)
    prompt = f"The user uploaded a {mime_type} of their craft project ({project} in {craft}). Please give clear and kind feedback."

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
        return "⚠️ Unsupported media type."

    from langchain_core.messages import HumanMessage
    return model.invoke([HumanMessage(content=content)]).content



# ✅ Final clean, non-repetitive mentor system prompt
mentor_prompt = PromptTemplate.from_template(
    """
    You are Craft Mentor. Only use tools when the user uploads a file or asks for specific help. Be concise.
"""
)

mentor_agent = create_react_agent(
    model=model,
    tools=[analyze_media],
    prompt=SystemMessage(content=mentor_prompt.format()),
    name="mentor_agent"
)
