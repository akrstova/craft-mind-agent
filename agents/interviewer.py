
import os
import googlemaps
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_tavily import TavilySearch
from langchain.chat_models import init_chat_model


load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=API_KEY)

tavily_search_tool = TavilySearch(
    max_results=5,
)

model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")


interviewer_agent = create_react_agent(
    model=model,
    tools=[],
    prompt=(
        """You are a friendly assistant that interviews the user regarding the craft they'd like to learn. 
        Examples of crafts include origami, knitting, crochet, calligraphy, but also more exotic crafts like Bulgarian lacework. 
        Your job is to interview the user in order to find out their desired craft (e.g. origami), skill level (e.g. beginner) and exact project (e.g. paper crane).
        The user may already come with an idea in mind, for example that they want to learn knitting. 
        If they don't have an idea for a specific project, suggest projects suitable to their skills.
        Do not make assumptions about the user's preferences in terms of craft, skill or project and always ask for user input.
        Your task is to find out the missing info to return a triple (craft, skill level, project) and report them back to the supervisor agent. 
        """
        
    ),
    name="interviewer_agent",
)