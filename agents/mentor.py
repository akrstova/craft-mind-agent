import base64
import mimetypes
import os
import requests
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import tool
from langchain_community.tools import YouTubeSearchTool


load_dotenv()

model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def search_youtube(query: str) -> str:
    """
    Searches YouTube for a relevant video tutorial and returns the URL of the top result.
    """
    search_url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&type=video&videoEmbeddable=true&maxResults=1"
        f"&q={requests.utils.quote(query)}&key={YOUTUBE_API_KEY}"
    )

    response = requests.get(search_url)
    if response.status_code != 200:
        return "YouTube search failed."

    items = response.json().get("items", [])
    if not items:
        return "No video found for this query."

    video_id = items[0]["id"]["videoId"]
    return f"https://www.youtube.com/watch?v={video_id}"



@tool
def find_craft_video(topic: str) -> str:
    """
    Find a beginner-friendly video tutorial for a craft technique (e.g. reverse fold, blocking, magic loop).
    Return the video title and YouTube link.
    """
    yt_tool = YouTubeSearchTool()
    raw_result = yt_tool.run(topic)
    return f"Here's a helpful video: {raw_result}"


@tool
def search_craft_tutorials(query: str) -> str:
    """Search the Internet for written craft tutorials based on the given query and return a few relevant results."""
    search_tool = TavilySearchResults(k=5)
    return search_tool.run(query)


# ✅ Final clean, non-repetitive mentor system prompt
mentor_prompt = PromptTemplate.from_template(
    """
    You are Craft Mentor and your job is to help the user understand specific craft terminology and offer guidance on a given craft project. In addition, you can search for tutorials on the 
    Internet to help the user or give guidance and ideas. To search the Internet for written tutorials, use the search_craft_tutorials tool.
"""
)

mentor_agent = create_react_agent(
    model=model,
    tools=[search_craft_tutorials],
    prompt=SystemMessage(content=mentor_prompt.format()),
    name="mentor_agent"
)
