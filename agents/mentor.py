from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import tool


load_dotenv()

model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")

@tool
def search_craft_tutorials(query: str) -> str:
    """Search the Internet for written craft tutorials based on the given query and return a few relevant results."""
    search_tool = TavilySearchResults(k=5)
    return search_tool.run(query)


# ✅ Final clean, non-repetitive mentor system prompt
mentor_prompt = PromptTemplate.from_template(
    """
    You are Craft Mentor and your job is to help the user understand specific craft terminology and offer guidance on a given craft project. In addition, you can search for written tutorials on the 
    Internet to help the user or give guidance and ideas. To search the Internet for written tutorials, use the search_craft_tutorials tool.
    Do not try to make up YouTube links, only use the search tool to look for written tutorials.
"""
)

mentor_agent = create_react_agent(
    model=model,
    tools=[search_craft_tutorials],
    prompt=SystemMessage(content=mentor_prompt.format()),
    name="mentor_agent"
)
