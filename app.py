import gradio as gr
from langchain_core.messages import HumanMessage, AIMessage

from agents.planner import supervisor

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

def chat_with_agent(message, history):
    # Convert Gradio history to LangChain messages
    messages = []
    for user_msg, assistant_msg in history:
        messages.append(HumanMessage(content=user_msg))
        messages.append(AIMessage(content=assistant_msg))
    messages.append(HumanMessage(content=message))

    # Run supervisor with full message history
    response = supervisor.invoke({"messages": messages})

    # Filter out system messages and duplicates
    filtered_ai_messages = []
    for msg in response["messages"]:
        if isinstance(msg, AIMessage) and msg.content:
            # Avoid including tool/system transfer messages
            if any(skip in msg.content.lower() for skip in [
                "transferring to", "transferring back to", "invoking tool", "calling agent"
            ]):
                continue
            # Avoid duplicates from previous history
            if msg.content not in [m[1] for m in history]:
                filtered_ai_messages.append(msg.content)

    return "\n\n".join(filtered_ai_messages)


# Create the Gradio interface
demo = gr.ChatInterface(
    fn=chat_with_agent,
    title="Craft Mind Assistant",
    description="I can help you learn about crafts and find supplies! Ask me anything about crafts, and I'll help you get started.",
    theme=gr.themes.Soft(),
    examples=[
        "I want to learn how to knit",
        "What supplies do I need for origami?",
        "I want to learn Bulgarian lacework"
    ]
)

if __name__ == "__main__":
    demo.launch()
