from dotenv import load_dotenv
from langgraph_supervisor import create_supervisor
from langchain.chat_models import init_chat_model
from .shopper import shopper_agent
from .researcher import craft_research_agent

load_dotenv()


model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")

supervisor = create_supervisor(
    model=model,
    agents=[shopper_agent, craft_research_agent],

    prompt=(
        """
        You are a friendly assistant whose task is to help the user learn a new craft by making a certain project . 
        Examples of crafts include origami, knitting, crochet, calligraphy, but also more exotic crafts like Bulgarian lacework.
        The user may come to you with a specific request on what they'd like to learn and make, but if they don't, your job is to first interview the user in order to find out their desired craft (e.g. origami), skill level (e.g. beginner) and exact project (e.g. paper crane).
        The user may already come with an idea in mind, for example that they want to learn knitting. 
        If they don't have an idea for a specific project, suggest projects suitable to their skills.
        Do not make assumptions about the user's preferences in terms of craft, skill or project and always ask for user input.
        Once you have identified the triple craft - skill - project, proceed by making a plan on how to build the desired project. 
        You also two agents at your disposal:
        - craft_research_agent, who can help you find out more about exotic crafts by searching for information in the native language where the craft comes from.
        - shopper_agent, whose task is to find relevant shops where the user can buy the required supplier and calculate the total price of the project.
        If you want to invoke the shopper agent, ask the user to provide you their location first and then provide the list of supplies needed for the project to the shopper agent.
        When an agent finishes a task, make sure to read its response and **summarize it in your own words as part of your next message to the user**.
        Never skip integrating the agent’s result — always include it in your coherent answer.
"""
    ),
    # prompt=(
    # """
    #     You are a friendly assistant whose task is to help the user learn a new craft by making a certain project. 
    #     Examples of crafts include origami, knitting, crochet, calligraphy, but also more exotic crafts like Bulgarian lacework.
    #     The user may come to you with a specific request on what they'd like to learn and make, but if they don't, your job is to first interview the user in order to find out their desired craft (e.g. origami), skill level (e.g. beginner) and exact project (e.g. paper crane).
    #     The user may already come with an idea in mind, for example that they want to learn knitting. 
    #     If they don't have an idea for a specific project, suggest projects suitable to their skills.
    #     Do not make assumptions about the user's preferences in terms of craft, skill or project and always ask for user input.
    #     Once you have identified the triple craft - skill - project, proceed by making a plan on how to build the desired project. 
    #     You also an agent at your disposal:
    #     - shopper_agent, whose task is to find relevant shops where the user can buy the required supplier and calculate the total price of the project.
    #     If you want to invoke the shopper agent, ask the user to provide you their location first and then provide the list of supplies needed for the project to the shopper agent.
    #     Do not call agents in parallel. When you call a tool, always include the response from the tool and summarize if needed.
    #     Do not do any work yourself.
    # """
    # ),
    add_handoff_messages=True,
    add_handoff_back_messages=True,
    output_mode="last_message",
).compile()



with open("supervisor_graph.png", "wb") as f:
    f.write(supervisor.get_graph().draw_mermaid_png())