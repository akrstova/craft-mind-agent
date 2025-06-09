CUSTOM_CSS = """
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