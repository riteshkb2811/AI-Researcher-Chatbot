# ⚡ AI Research Assistant (Local ChatGPT)

An interactive, ChatGPT-like conversational assistant with **real-time web search** and **live token-by-token streaming**, built using **Streamlit**, **LangGraph**, **Groq**, and **Tavily**.

---

## ✨ Features

- **⚡ Blazing-Fast Inference:** Powered by Groq (`openai/gpt-oss-20b`) for ultra-low latency response times.
- **🌐 Real-Time Web Search:** Integrates Tavily Search API as an agent tool to answer queries with fresh, live internet data.
- **🌊 True Token Streaming:** Uses Python generators with Streamlit's `st.write_stream` to render words smoothly as they arrive (typewriter effect).
- **🧠 Multi-Turn Conversation Memory:** Built-in LangGraph `MemorySaver` checkpointing partitioned by unique session `thread_id`s.
- **🎨 Interactive Modern UI:** Custom-styled sidebar, status indicator, clickable prompt suggestions, and a quick session reset button.

---

## 🏗️ Architecture & How It Works

```
[ User Input in Streamlit ]
           │
           ▼
[ LangGraph Agent (thread_id) ] ◄──► [ MemorySaver Checkpointer ]
           │
     ┌─────┴──────────┐
     ▼                ▼
[ Groq LLM ]    [ Tavily Web Search Tool ]
     │                │
     └───────┬────────┘
             ▼
  [ Token Stream Filter ]
(metadata: node == 'model')
             │
             ▼
[ st.write_stream Live Rendering ]
```

### Memory Architecture
1. **LangGraph Checkpointer (`MemorySaver`):** Saves complete multi-turn conversational state in memory under the user's `thread_id` so the agent can reference previous questions and context.
2. **Streamlit State (`st.session_state`):** Persists chat history across script re-runs to ensure previous chat bubbles remain displayed on the page.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- A [Groq API Key](https://console.groq.com/)
- A [Tavily API Key](https://tavily.com/)

### 2. Installation

Clone the repository and set up a virtual environment:

```bash
# Clone the repository
git clone https://github.com/<your-username>/<your-repo-name>.git
cd "first ai proj"

# Create and activate virtual environment (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install required packages:

```bash
pip install streamlit langchain-groq langchain-tavily langgraph python-dotenv
```

### 3. Environment Setup

Create a `.env` file in the root directory:

```env
GroqKEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

---

## 💻 Running the App

Launch the application with Streamlit:

```bash
streamlit run apps/local_chat_gpt.py
```

Open your browser at `http://localhost:8501` to start chatting!

---

## 📂 Project Structure

```
├── apps/
│   ├── local_chat_gpt.py    # Main Streamlit app source code
│   └── README.md            # Documentation
├── .env                     # API keys (not tracked in git)
└── requirement.txt          # Python dependencies
```

---

## 📜 License
This project is open-source and available under the [MIT License](MIT License).

