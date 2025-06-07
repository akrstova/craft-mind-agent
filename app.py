import os
import base64
import mimetypes
import gradio as gr
from langchain_core.messages import HumanMessage, AIMessage
from agents.planner import supervisor  # your LangGraph supervisor setup

# Store uploaded file path persistently
uploaded_file_path = {"path": None}


def encode_file_to_media_message(file_path: str):
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"

    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    if mime_type.startswith("image"):
        return [
            {
                "type": "image_url",
                "image_url": f"data:{mime_type};base64,{encoded}",
            },
            {
                "type": "text",
                "text": "Please evaluate this image of my craft project.",
            },
        ]
    elif mime_type.startswith("video"):
        return [
            {
                "type": "media",
                "data": encoded,
                "mime_type": mime_type,
            },
            {
                "type": "text",
                "text": "This is a video of me working on my project. Could you give feedback?",
            },
        ]
    else:
        return [{"type": "text", "text": "Unsupported file type uploaded."}]


def chat_with_agent(message, history):
    # Convert history to LangChain messages
    messages = []
    for user_msg, assistant_msg in history:
        messages.append(HumanMessage(content=user_msg))
        messages.append(AIMessage(content=assistant_msg))
    messages.append(HumanMessage(content=message))

    # If a file is uploaded, attach it in proper format
    if uploaded_file_path["path"]:
        media_msg = encode_file_to_media_message(uploaded_file_path["path"])
        messages.append(HumanMessage(content=media_msg))
        uploaded_file_path["path"] = None  # 🔥 clear it after use

    # Call supervisor
    response = supervisor.invoke({"messages": messages})

    # Filter response
    filtered_ai_messages = []
    for msg in response["messages"]:
        if isinstance(msg, AIMessage) and msg.content:
            if any(skip in msg.content.lower() for skip in [
                "transferring to", "transferring back to", "invoking tool", "calling agent"
            ]):
                continue
            if msg.content not in [m[1] for m in history]:
                filtered_ai_messages.append(msg.content)

    return "\n\n".join(filtered_ai_messages)


def handle_file_upload(file):
    if file:
        uploaded_file_path["path"] = file.name
        return "✅ File received. It will be considered in your next message."
    else:
        uploaded_file_path["path"] = None
        return "❌ File cleared."


# Gradio UI
with gr.Blocks(title="Craft Mind Assistant") as demo:
    gr.ChatInterface(
        fn=chat_with_agent,
        title="Craft Mind Assistant",
        description="I can help you learn about crafts and find supplies! You can also upload an image or video of your work for feedback.",
        theme=gr.themes.Soft(),
        examples=[
            "Can you help me evaluate this paper crane?",
            "I’m learning how to knit. Any tips?",
            "How do I make Bulgarian lace?"
        ]
    )

    with gr.Row():
        with gr.Column(scale=0.6):
            gr.Markdown("### 📎 Upload a craft image or video (optional):")
            file_input = gr.File(label="Upload Image or Video", file_types=["image", "video"])
            file_status = gr.Textbox(label="", interactive=False)

    file_input.change(fn=handle_file_upload, inputs=file_input, outputs=file_status)

if __name__ == "__main__":
    demo.launch()
