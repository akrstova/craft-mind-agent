# instruction_graph.py
import os
import requests
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict, Literal

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-001",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

class InstructionState(TypedDict):
    craft: str
    model: str
    preference: Literal["text", "video", None]
    instruction_output: str

CraftState = Annotated[InstructionState, add_messages]

# VIDEO SEARCH TOOL
class YouTubeSearchTool:
    def __init__(self, api_key: str, max_results: int = 3):
        self.api_key = api_key
        self.max_results = max_results

    def search(self, query: str):
        search_url = (
            f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=video"
            f"&videoEmbeddable=true&maxResults={self.max_results}&q={query}&key={self.api_key}"
        )
        response = requests.get(search_url)
        if response.status_code != 200:
            return None, "YouTube search failed"

        items = response.json().get("items", [])
        for item in items:
            video_id = item["id"]["videoId"]
            # Check embeddability
            details_url = (
                f"https://www.googleapis.com/youtube/v3/videos?part=status,snippet&id={video_id}&key={self.api_key}"
            )
            details = requests.get(details_url).json()
            if not details.get("items"):
                continue
            status = details["items"][0]["status"]
            if status.get("privacyStatus") == "public" and status.get("embeddable"):
                title = details["items"][0]["snippet"]["title"]
                transcript_prompt = f"Provide a concise explanation of what this video teaches and any steps involved: {title}"
                summary = model.invoke(transcript_prompt).content.strip()
                return f"**{title}**\nhttps://www.youtube.com/embed/{video_id}\n\n{summary}", None

        return None, "No embeddable video found"

search_tool = YouTubeSearchTool(api_key=YOUTUBE_API_KEY)

# AGENTS

def ask_preference(state: CraftState):
    return {"instruction_output": "Would you like to learn this through **text instructions** or a **YouTube video**?"}

def provide_text_instructions(state: CraftState):
    prompt = f"Give step-by-step instructions to teach someone how to make a {state['model']} using {state['craft']} techniques."
    result = model.invoke(prompt).content.strip()
    return {"instruction_output": result}

def provide_video_instructions(state: CraftState):
    query = f"how to make a {state['model']} with {state['craft']}"
    video, error = search_tool.search(query)
    return {"instruction_output": video if video else error or "No video found."}

# FLOW
builder = StateGraph(InstructionState)
builder.add_node("ask_preference", ask_preference)
builder.add_node("provide_text", provide_text_instructions)
builder.add_node("provide_video", provide_video_instructions)

builder.set_entry_point("ask_preference")
builder.add_conditional_edges(
    "ask_preference",
    lambda state: state.get("preference"),
    {"text": "provide_text", "video": "provide_video"},
)
builder.add_edge("provide_text", END)
builder.add_edge("provide_video", END)

instruction_graph = builder.compile()
