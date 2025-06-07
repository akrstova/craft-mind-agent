import os
import base64
import mimetypes
import requests
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage
from langchain.tools import tool

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
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
    prompt = f"The user is making a {project} using {craft}. Provide feedback based on this file."

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


@tool
def search_youtube_tutorial(query: str) -> str:
    """
    Search YouTube for a public, embeddable tutorial and return the first valid result.
    """
    api_key = os.getenv("YOUTUBE_API_KEY")
    search_url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&type=video&videoEmbeddable=true&videoSyndicated=true"
        f"&maxResults=5&safeSearch=strict&q={requests.utils.quote(query)}"
        f"&key={api_key}"
    )
    search_resp = requests.get(search_url)
    if search_resp.status_code != 200:
        return "⚠️ YouTube search failed."

    search_items = search_resp.json().get("items", [])
    video_ids = [item["id"]["videoId"] for item in search_items if "videoId" in item["id"]]

    # Validate video status via `/videos` endpoint
    if not video_ids:
        return "⚠️ No video candidates found."

    status_url = (
        f"https://www.googleapis.com/youtube/v3/videos"
        f"?part=status,snippet&id={','.join(video_ids)}&key={api_key}"
    )
    status_resp = requests.get(status_url)
    if status_resp.status_code != 200:
        return "⚠️ Failed to validate video status."

    status_items = status_resp.json().get("items", [])
    for item in status_items:
        status = item["status"]
        snippet = item["snippet"]
        if status.get("embeddable") and status.get("privacyStatus") == "public":
            video_id = item["id"]
            title = snippet["title"]
            channel = snippet["channelTitle"]
            return f"🎥 **{title}** by *{channel}*\nhttps://www.youtube.com/watch?v={video_id}"

    return "⚠️ No valid video found that can be embedded or viewed publicly."



# 🧠 ReAct-compatible system prompt to force tool usage
mentor_prompt = PromptTemplate.from_template(
    """
You are a helpful and kind craft mentor.

You have two tools:
- `analyze_media`: for analyzing uploaded images or videos.
- `search_youtube_tutorial`: to find real video tutorials when the user asks "how do I" or needs a visual guide.

Use this format:

Thought: Do I need to use a tool?
Action: the_tool_name
Action Input: input value

Then wait for the result.

When you receive it:

Observation: the tool result
Thought: What did I learn?
Final Answer: your reply to the user

DO NOT make up links. Only use the tool to find real videos.
Be concise, friendly, and invite them to take the next step.
"""
)

mentor_agent = create_react_agent(
    model=model,
    tools=[analyze_media, search_youtube_tutorial],
    prompt=SystemMessage(content=mentor_prompt.format()),
    name="mentor_agent"
)
