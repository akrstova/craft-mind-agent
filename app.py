import gradio as gr
from langchain_core.messages import HumanMessage, AIMessage

from agents.planner import supervisor

def chat_with_agent(message, history):
    # Convert Gradio history to LangChain messages
    messages = []

    # Each item in history is a [user, assistant] pair
    for user_msg, assistant_msg in history:
        messages.append(HumanMessage(content=user_msg))
        messages.append(AIMessage(content=assistant_msg))

    # Append the current user message
    messages.append(HumanMessage(content=message))

    # Run supervisor with full chat history
    response = supervisor.invoke({"messages": messages})

    # Extract final response
    final_response = "\n".join([msg.content for msg in response["messages"]])
    # final_response = response["messages"][-1].content

    return final_response

# Create the Gradio interface
demo = gr.ChatInterface(
    fn=chat_with_agent,
    title="Craft Mind Assistant",
    description="I can help you learn about crafts and find supplies! Ask me anything about crafts, and I'll help you get started.",
    theme=gr.themes.Soft(),
    examples=[
        "I want to learn how to knit",
        "What supplies do I need for origami?",
        "Can you help me find yarn shops in Berlin?"
    ]
)

if __name__ == "__main__":
    demo.launch()
