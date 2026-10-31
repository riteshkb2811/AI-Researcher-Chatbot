import os
import uuid
import streamlit as st
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver

# ── 1. Page Configuration ──
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── 2. Custom CSS for Modern, Interactive UI ──
st.markdown("""
<style>
    /* Gradient Header */
    .title-banner {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.3rem;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    
    /* Subtle chat bubble styling */
    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 0.6rem;
    }
    
    /* Status indicator */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: rgba(16, 185, 129, 0.15);
        color: #10b981;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: .4; }
    }
</style>
""", unsafe_allow_html=True)

# ── 3. Load Environment Variables ──
load_dotenv()
groq_key = os.getenv("GroqKEY")
tavily_key = os.getenv("TAVILY_API_KEY")

# ── 4. Initialize Agent (Cached in Session) ──
@st.cache_resource
def get_agent():
    llm = ChatGroq(model="openai/gpt-oss-20b", groq_api_key=groq_key, streaming=True)
    tavily_search_tool = TavilySearch(
        max_results=5,
        topic="general",
        tavilly_api_key=tavily_key,
        max_tokens=2048
    )
    memory = MemorySaver()
    agent_instance = create_agent(
        model=llm,
        tools=[tavily_search_tool],
        system_prompt=(
            "You are an expert AI research assistant with live web search capabilities via Tavily. "
            "Provide accurate, comprehensive, and well-structured answers using Markdown formatting."
        ),
        checkpointer=memory
    )
    return agent_instance

# ── 5. Manage Conversation Session ──
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# ── 6. Sidebar Controls ──
with st.sidebar:
    st.markdown("### ⚙️ Session Settings")
    st.markdown('<div class="status-pill"><div class="status-dot"></div> Live Web Search Active</div>', unsafe_allow_html=True)
    st.caption(f"**Thread ID:** `{st.session_state.thread_id[:8]}...`")
    
    st.divider()
    
    st.markdown("**Powered by:**")
    st.markdown("• **LLM:** `openai/gpt-oss-20b` (Groq)")
    st.markdown("• **Search:** Tavily API")
    st.markdown("• **Agent Engine:** LangGraph")
    
    st.divider()
    
    # Quick starter suggestions
    st.markdown("**💡 Try Asking:**")
    starters = [
        "What is the latest news about SpaceX?",
        "Compare Quantum Computing vs Classic Computing",
        "What is the current stock price of Apple?"
    ]
    for prompt_hint in starters:
        if st.button(prompt_hint, key=prompt_hint, use_container_width=True):
            st.session_state.selected_prompt = prompt_hint
            
    st.divider()
    
    if st.button("🗑️ Reset Chat", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

# ── 7. Header ──
st.markdown('<div class="title-banner">⚡ AI Research Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask anything — real-time web search with token-by-token live streaming</div>', unsafe_allow_html=True)

# ── 8. Render Existing Message History ──
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ── 9. Chat Input & Live Streaming ──
chat_input_val = st.chat_input("Ask a question or search for anything...")

# Support sidebar suggestion clicks
prompt = chat_input_val or st.session_state.pop("selected_prompt", None)

if prompt:
    # 1. Store and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # 2. Stream AI response with live typewriter effect
    with st.chat_message("assistant", avatar="🤖"):
        def generate_stream():
            agent = get_agent()
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            
            for message_chunk, metadata in agent.stream(
                {"messages": [{"role": "user", "content": prompt}]},
                config,
                stream_mode="messages"
            ):
                # Stream only content generated by model node
                if message_chunk.content and metadata.get("langgraph_node") == "model":
                    yield message_chunk.content

        # st.write_stream consumes the generator and renders tokens in real time
        full_response = st.write_stream(generate_stream())

    # 3. Store assistant message in history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
