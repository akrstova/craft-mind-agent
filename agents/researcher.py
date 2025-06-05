from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers.string import StrOutputParser


load_dotenv()

# Initialize model
model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")


# Prompt template
language_detection_prompt = PromptTemplate.from_template(
    """Given the name or description of a craft: "{craft}", determine which language would likely return the most useful search results online. 
Respond only with the name of the language (e.g. 'Bulgarian', 'Japanese', 'English')."""
)

# Chain using your model
language_detection_chain = LLMChain(llm=model, prompt=language_detection_prompt, output_parser=StrOutputParser())

# Tool function
@tool
def detect_search_language(craft: str) -> str:
    """Uses an LLM to decide the best language to search for information about a given craft."""
    return language_detection_chain.run({"craft": craft})


# Tool 2: Search the web using Tavily
@tool
def web_search_in_language(query: str) -> str:
    """Search the internet for a given query (in any language) and return a few relevant results."""
    search_tool = TavilySearchResults(k=5)
    return search_tool.run(query)

# Tool 3: Translate text to English
translate_prompt = PromptTemplate.from_template(
    """Translate the following text into English:

    ---
    {text}
    ---
    """
)
translate_chain = LLMChain(llm=model, prompt=translate_prompt, output_parser=StrOutputParser())

@tool
def translate_to_english(text: str) -> str:
    """Translates a given text into English.

    Args:
        text (str): input text

    Returns:
        str: English translation
    """
    return translate_chain.run({"text": text})


# Tool 4: Summarize translated content
summarize_prompt = PromptTemplate.from_template(
    """Summarize the following content as a craft introduction for beginners. Include what the craft is, materials used, and a basic starting point:

    ---
    {text}
    ---
    """
)
summarize_chain = LLMChain(llm=model, prompt=summarize_prompt, output_parser=StrOutputParser())

@tool
def summarize_craft_intro(text: str) -> str:
    """Summarizes a given text about a specific craft as a craft introduction for beginners.

    Args:
        text (str): text about a craft

    Returns:
        str: summary
    """
    return summarize_chain.run({"text": text})


# Define the agent
craft_research_agent = create_react_agent(
    model=model,
    tools=[
        detect_search_language,
        web_search_in_language,
        translate_to_english,
        summarize_craft_intro
    ],
   prompt = """
        You are a helpful craft researcher assistant.

        Your job is to research traditional or exotic crafts — such as Bulgarian lacework — using reliable online sources (in the language of origin if needed), and return a beginner-friendly summary that teaches the user what the craft is and how to get started.
        Use the available tools to find the relevant information.
        Please follow this exact structure in your response:

        === What is it? ===
        Explain what this craft is, where it comes from, and what makes it unique or culturally important.

        === Types or Styles (if relevant) ===
        Briefly describe any subtypes, styles, or traditions within the craft (if they exist).

        === Materials Needed ===
        List the essential tools or materials required to practice the craft.

        === How to Get Started ===
        Explain how a beginner can start — mention basic techniques, patterns, or entry-level projects.

        === Cultural or Historical Context (optional) ===
        Add interesting background info if available (e.g., where/when it was traditionally practiced).

        Keep the tone friendly, and informative — like you're introducing the craft to someone who’s curious but knows nothing yet.

        DO NOT add any introduction or closing lines. Just return the structured content above.
        """,
    name="craft_research_agent"
)



# Example usage
if __name__ == "__main__":
    response = craft_research_agent.invoke({"input": "I want to learn Bulgarian lacework"})
    print(response)
