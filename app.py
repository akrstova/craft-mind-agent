import json
import base64
import mimetypes
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import gradio as gr
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import Runnable
from langchain.prompts import PromptTemplate
from langchain.chat_models import init_chat_model

from utils.analysis import analyze_media_structured, extract_json
from agents.planner import supervisor
from utils.custom_css import CUSTOM_CSS
from utils.search import search_youtube
from utils.state import CraftState

load_dotenv()

model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")

app = FastAPI()
app.mount("/static", StaticFiles(directory="resources"), name="static")


# Store uploaded file path persistently
uploaded_file_path = {"path": None}
state = {
    "uploaded_file": None, 
    "media_processed": False, 
    "analysis_result": None, 
}


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
    state.query = experience["query"]
    state = detect_video_request_llm(state, model)
    
    return state


def detect_video_request_llm(state: CraftState, model: Runnable) -> CraftState:
    prompt = video_intent_prompt.format(message=state.user_message)
    result = model.invoke([HumanMessage(content=prompt)]).content.lower().strip()
    state.asked_for_video = result.startswith("yes")
    return state


def fetch_youtube_video(state: CraftState) -> CraftState:
    query = state.project + " " + state.craft + " "  + state.experience_level + " " + state.query
    # Deduplicate query for duplicate words
    words = query.split()
    seen = set()
    deduped_words = []
    for word in words:
        lw = word.lower()
        if lw not in seen:
            deduped_words.append(word)
            seen.add(lw)
    query = " ".join(deduped_words)
    video_url = search_youtube(query)
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
4. query - this refers to what the user is actually looking for, it can be the project itself (e.g. knitting) or a specific technique related to it (e.g. how to cast on). Return the query as 3 words max.
Return ONLY a JSON object with these keys: "project", "craft", "experience_level", "query".

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
    main_state = detect_video_request(main_state, model, messages)
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
with gr.Blocks(title="Craftwise", css=CUSTOM_CSS, theme=gr.themes.Soft()) as demo:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("""
            <div class="title-container">
                <h1 style="font-family: 'Lobster'; color: black; font-size: 3.5em;">Craftwise</h1><br>
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
