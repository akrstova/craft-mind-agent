import os
import requests
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool

load_dotenv()

model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


@tool
def search_youtube(query: str) -> str:
    """
    Search YouTube for a relevant video for the given query.
    Ensures the video is embeddable, public, and available.
    Returns the URL of the top valid result.
    """
    search_url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&type=video&videoEmbeddable=true&maxResults=5"
        f"&q={query}&key={YOUTUBE_API_KEY}"
    )
    response = requests.get(search_url)
    if response.status_code != 200:
        return "YouTube search failed."

    items = response.json().get("items", [])
    if not items:
        return "No video found for this query."

    for item in items:
        video_id = item["id"].get("videoId")
        if not video_id:
            continue

        # Check video status via videos endpoint
        video_check_url = (
            f"https://www.googleapis.com/youtube/v3/videos"
            f"?part=status&id={video_id}&key={YOUTUBE_API_KEY}"
        )
        video_resp = requests.get(video_check_url)
        if video_resp.status_code != 200:
            continue

        video_data = video_resp.json().get("items", [])
        if not video_data:
            continue

        status = video_data[-1]["status"]
        if status.get("privacyStatus") == "public" and status.get("embeddable", False):
            return f"https://www.youtube.com/watch?v={video_id}"

    return "No valid public video found for this query."
                


mentor_agent = create_react_agent(
    model=model,
    tools=[search_youtube],
    prompt=(
        """
        🎓 You are Craft Mentor, a friendly and patient coach helping users learn new craft skills. You explain things clearly, answer questions, and guide them through tricky parts like buttonholes, tension, or blocking.

        Use the YouTube search tool when:

        The user asks “how do I…” or wants to see something

        A video would help explain it better

        The user prefers videos

        Choose clear, beginner-friendly videos. Describe what it shows and why it helps. Share the title and link naturally. Never change the link.

        End with a gentle nudge:
        “Want to try it?”
        “Need a video for that?”

        """
        
    ),
    name="mentor_agent",
)