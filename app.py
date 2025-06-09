import json
import base64
import mimetypes
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import gradio as gr
from langchain_core.messages import HumanMessage, AIMessage
from agents.planner import supervisor
from agents.mentor import search_youtube, model
from analysis_utils import analyze_media_structured, extract_json
from langchain_core.runnables import Runnable
from langchain.prompts import PromptTemplate

app = FastAPI()
app.mount("/static", StaticFiles(directory="resources"), name="static")

# Custom CSS for craft-themed styling

custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Lobster&family=Comfortaa&family=Playfair+Display&display=swap');

.gradio-container {
    font-family: 'Comfortaa', sans-serif;
    background: url('https://raw.githubusercontent.com/akrstova/craft-mind-agent/main/resources/background_craftpilot.png') no-repeat center center fixed;
    background-size: cover;
    position: relative;
    min-height: 100vh;
}

.title-container {
    background: rgba(255, 255, 255, 0.35);
    border-radius: 20px;
    padding: 15px 30px;
    margin: 20px auto;
    max-width: 50%;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(5px);
    text-align: center;
}

.upload-container {
    background: rgba(255, 255, 255, 0.35);
    border-radius: 20px;
    padding: 15px 30px;
    margin: 20px auto;
    max-width: 100%;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(5px);
    text-align: center;
}

.title-container h1 {
    display: inline-block;
    margin: 0;
    padding-right: 20px;
}

.title-container p {
    display: inline-block;
    margin: 0;
    vertical-align: middle;
}

.gradio-interface {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: 20px;
    max-width: 800px;
    margin: 0 auto;
    position: relative;
    z-index: 1;
}

.gradio-chat {
    background: #f0f7f4;
    border-radius: 12px;
    border: 1px solid #d0e8e0;
}

.gradio-chat-message {
    border-radius: 12px;
    padding: 12px;
    margin: 8px 0;
}

.gradio-chat-message.user {
    background: #e8f4f8;
    border: 1px solid #b8d8e8;
}

.gradio-chat-message.bot {
    background: #e8f4e8;
    border: 1px solid #c8e8d8;
}

.gradio-button {
    background: #2d5a4a !important;
    border: none !important;
    color: white !important;
    padding: 8px 16px !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
}

.gradio-button:hover {
    background: #1a3c32 !important;
    transform: translateY(-2px);
}

.gradio-file-upload {
    border: 2px dashed #2d5a4a !important;
    border-radius: 12px !important;
    padding: 10px !important;
    background: rgba(248, 249, 250, 0.95) !important;
    max-width: 30% !important;
    margin: 0 auto !important;
}

.gradio-file-upload:hover {
    border-color: #1a3c32 !important;
    background: rgba(240, 242, 245, 0.95) !important;
}

.gradio-markdown {
    font-family: 'Comfortaa', sans-serif;
    color: #2d5a4a;
}

.gradio-title {
    font-family: 'Playfair Display', serif;
    color: #2d5a4a;
    font-size: 2.5em !important;
    margin-bottom: 0.5em !important;
}

.gradio-description {
    font-family: 'Comfortaa', sans-serif;
    color: #2d5a4a;
    font-size: 1.1em !important;
}

.upload-section {
    max-width: 30% !important;
    margin: 0 auto !important;
}

.upload-section .gradio-markdown {
    margin: 0.5em 0 !important;
}

.upload-section h3 {
    margin: 0.5em 0 !important;
    font-size: 1.2em !important;
}

.upload-section p {
    margin: 0.3em 0 !important;
    font-size: 0.9em !important;
}

.file-status {
    max-width: 30% !important;
    margin: 0.3em auto !important;
    text-align: center !important;
    padding: 0.3em !important;
}
"""

# Store uploaded file path persistently
uploaded_file_path = {"path": None}
state = {
    "uploaded_file": None, 
    "media_processed": False, 
    "analysis_result": None, 
}



class CraftState:
    def __init__(self):
        self.user_message = ""
        self.asked_for_video = False
        self.video_url = None
        self.project = ""
        self.craft = ""
        self.experience_level = ""

main_state = CraftState()

video_intent_prompt = PromptTemplate.from_template("""
You are a helpful assistant that determines whether a user is asking for a video tutorial explicitly. 
Answer only "yes" or "no". If there's no mention of the user asking for a video tutorial, always return no.

User message: {message}
""")

def detect_video_request(state: CraftState, model: Runnable, messages) -> CraftState:   
    experience = extract_project_craft_experience(messages=messages, model=model)
    state.project = experience['project'] 
    state.craft = experience['craft'] 
    state.experience_level = experience['experience_level'] 
    print("The experince values are ", experience)
    print("The statuses of the states are ", state.project, state.craft, state.experience_level)
    state = detect_video_request_llm(state, model)
    
    return state


def detect_video_request_llm(state: CraftState, model: Runnable) -> CraftState:
    prompt = video_intent_prompt.format(message=state.user_message)
    result = model.invoke([HumanMessage(content=prompt)]).content.lower().strip()
    state.asked_for_video = result.startswith("yes")
    return state


def fetch_youtube_video(state: CraftState) -> CraftState:
    query = state.project + " " + state.craft + " "  + state.experience_level
    # Replace with your working API call
    print("the query for video search is ", query)
    video_url = search_youtube(query)
    print("The found video url is ", video_url)
    state.video_url = video_url
    return state


def generate_final_response(state: CraftState) -> str:
    response = ""
    if state.video_url:
        response+= f"\nHere's a helpful video tutorial: {state.video_url}"
    return response


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



# Define prompt template
extraction_prompt = PromptTemplate.from_template("""
You are an assistant that extracts structured information from a conversation between a user and an assistant.
Extract the following fields:
1. project – what the user wants to create or work on (e.g., paper crane, knitted scarf)
2. craft – what type of craft it involves (e.g., origami, knitting, crochet)
3. experience level – the user's skill level (one of beginner, intermediate, advanced, or ""). If you cannot classify as beginner, intermediate, advanced, return empty string as a value

Return ONLY a JSON object with these keys: "project", "craft", "experience_level".

Conversation:
{conversation}
""")

# Function to extract structured data
def extract_project_craft_experience(messages: list, model: Runnable) -> dict:
    conversation = "\n".join(
        f"{'User' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}"
        for msg in messages
    )
    prompt = extraction_prompt.format(conversation=conversation)
    response = model.invoke([HumanMessage(content=prompt)]).content
    parsed = extract_json(response)
    try:
        return parsed
    except json.JSONDecodeError:
        return {
            "project": None,
            "craft": None,
            "experience_level": None
        }



def chat_with_agent(message, history):
    # Convert history to LangChain messages
    messages = []

    for user_msg, assistant_msg in history:
        messages.append(HumanMessage(content=user_msg))
        messages.append(AIMessage(content=assistant_msg))
   

    # If a file is uploaded, attach it in proper format    
    if uploaded_file_path["path"] and not state['media_processed']:
        analysis = analyze_media_structured(uploaded_file_path["path"])
        state["analysis_result"] = analysis
        state['media_processed'] = True

        # Clear uploaded file reference to avoid duplicate analysis
        uploaded_file_path["path"] = None

        return analysis
    
    
    
    
    global main_state
    if len(messages) > 0:
        print("The type of message id is ", type(messages[-1]))
    main_state.user_message = messages[-1].content + " " + message if len(messages) > 0 else message
    
    messages.append(HumanMessage(content=message))
    print("The current user_message is ", main_state.user_message)
    main_state = detect_video_request(main_state, model, messages)
    print("the main state is ", main_state.project, main_state.experience_level, main_state.craft)
    if main_state.asked_for_video:
        main_state = fetch_youtube_video(main_state)
        response = generate_final_response(main_state)
        main_state.asked_for_video = False
        main_state.video_url = None
        messages.append(AIMessage(content=response))
    
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
        state["media_processed"] = False
        state["analysis_result"] = None
        return "✅ File received. It will be considered in your next message."
    else:
        uploaded_file_path["path"] = None
        state["media_processed"] = True
        state["analysis_result"] = None
        return "❌ File cleared."


# Gradio UI
with gr.Blocks(title="Craft Pilot", css=custom_css, theme=gr.themes.Soft()) as demo:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("""
            <div class="title-container">
                <h1 style="font-family: 'Lobster'; color: black; font-size: 3.5em;">Craft Pilot</h1><br>
                <p style="font-family: 'Lobster'; color: black; font-size: 1.5em;">Your personal craft mentor and guide. Share your projects and get expert feedback!</p>
            </div>
            """)
    
    gr.ChatInterface(
        fn=chat_with_agent,
        title="",
        description="",
        theme=gr.themes.Soft(),
        examples=[
            "I'm learning how to knit. Any tips?",
            "How do I make Bulgarian lace?",
            "Can you help me evaluate this paper crane I made?",
        ]
    )

    with gr.Row():
        with gr.Column(scale=1, elem_classes="upload-section"):
            gr.Markdown("""
            <div class="upload-container">
                <h2 style="font-family: 'Lobster'; color: black; font-size: 2em; margin: 0.5em 0;">📎 Share Your Craft Project</h2>
                <p style="font-family: 'Lobster'; color: black; font-size: 1.2em !important; margin: 0.3em 0;">
                    Upload an image or video of your work to get personalized feedback
                </p>
            </div>
            """)
            file_input = gr.File(
                label="Upload Image or Video",
                file_types=["image", "video"],
                file_count="single"
            )
            file_status = gr.Textbox(
                label="",
                interactive=False,
                elem_classes="file-status"
            )

    file_input.change(fn=handle_file_upload, inputs=file_input, outputs=file_status)

if __name__ == "__main__":
    demo.launch()
