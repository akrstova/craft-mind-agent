# 🧶 Craftwise

**Craftwise** is an AI-native learning assistant for hands-on crafts including (but not limited to!) origami, knitting, and crochet, and even more exotic crafts like Balkan lacework or Kente cloth making.
It guides users through creative projects with smart project suggestions, real-time explanations, YouTube tutorial retrieval, and visual feedback on uploaded photos.

Built with a multi-agent architecture using LangGraph and powered by LLMs, Craftwise helps users learn-by-doing—just like a friendly workshop mentor.

---

## ✨ Features

- 🎨 Personalized craft project recommendations  
- 🤖 Multi-agent orchestration with LangGraph  
- 🔍 YouTube tutorial search 
- 📷 Visual feedback on uploaded craft work  
- 💬 Conversational interface via Gradio  
- 🧵 Modular agent setup for easy extension

---

## 🚀 Getting Started

### 1. **Clone the Repository**

```bash
git clone https://github.com/akrstova/craftwise.git craftwise
cd craftwise
```

### 2. **Install Dependencies with [uv](https://github.com/astral-sh/uv)**

```bash
uv venv
source .venv/bin/activate
uv sync
```

> ℹ️ Don't have `uv` installed?  
> Install via pip: `pip install uv`

---

### 3. **Configure Environment Variables**

Copy the example file and set your keys:

```bash
cp .env.example .env
```

Fill in:
- Gemini API key - for the LLM calls
- Google Maps API key - for searching local craft shops
- YouTube API key (usually the same as Google Maps API key retrieved from your Google Cloud Console)
- Tavily API key - for searching the web

---

### 4. **Run the Gradio App**

```bash
gradio app.py
```

Then open your browser at: [http://localhost:7860](http://localhost:7860)

---

## 🧭 Project Structure

```
craftwise/
├── agents/           # LangGraph agents: Planner, Mentor, Perception
├── analysis_utils.py # Media analysis logic
├── app.py            # Gradio interface
├── main.py           # LangGraph supervisor setup
├── .env.example      # Sample environment config
└── resources/        # Static images, backgrounds, styles
```

---

## 🧪 Development Notes

- 🧠 Agents are defined modularly under `agents/`
- 🧵 Media feedback handled by PerceptionAgent (`analyze_media_structured`)
- 🔎 YouTube search is integrated via API with fallback validation
- 🌐 Background and UI assets are served via FastAPI + Gradio hybrid

---

## 🧩 Ideas for Expansion

- Track user learning progress over time
- Search for online or in-presence workshops and connect to teachers who know the craft

---

## 🤝 Contributing

Pull requests and forks welcome!  
To contribute:

1. Fork the repo  
2. Create a feature branch: `git checkout -b feature/my-feature`  
3. Commit your changes: `git commit -m "Add awesome feature"`  
4. Push and open a PR

---

## 📄 License

MIT License © 2025 Alisa and Jasmin Bogatinovski 

---

> Made with code, curiosity, and a little bit of yarn. 🧶
