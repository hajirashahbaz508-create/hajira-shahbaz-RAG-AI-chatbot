import pickle
import numpy as np
import ollama
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity

EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3.2:1b"
FALLBACK = "I don't have information about this. You can tell me the information, and I'll remember it during this conversation."

# Page Setup
st.set_page_config(
    page_title="Python RAG Chatbot",
    page_icon="⚡",
    layout="wide"
)

# Light Theme Glassmorphism & Modern Styling
st.markdown("""
<style>
    /* Full Page Gradient Background (Light & Modern) */
    .stApp {
        background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 50%, #e0f2fe 100%) !important;
        color: #1e293b !important;
    }

    /* Glassmorphism Header */
    .glass-header {
        background: rgba(255, 255, 255, 0.65) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.8);
        border-radius: 20px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.1);
        margin-bottom: 25px;
        animation: fadeIn 0.8s ease-in-out;
    }

    .glass-header h1 {
        background: linear-gradient(90deg, #4f46e5, #7c3aed, #0284c7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-bottom: 5px;
    }

    /* Chat Messages Glass Containers */
    div[data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.75) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.9) !important;
        border-radius: 18px !important;
        padding: 14px 20px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 4px 15px rgba(148, 163, 184, 0.15) !important;
        color: #0f172a !important;
        animation: slideUp 0.3s ease-out forwards;
    }

    /* Glass Chat Input Box */
    .stChatInputContainer {
        border-radius: 20px !important;
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 1) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.12) !important;
    }

    /* Sidebar Glassmorphism */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.45) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.6) !important;
    }

    /* Keyframe Animations */
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(12px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# Load database with caching
@st.cache_resource
def load_rag_data():
    with open("retrieval_data.pkl", "rb") as f:
        vectors, chunks = pickle.load(f)
    return vectors, chunks

vectors, chunks = load_rag_data()

# Initialize session memory
if "memory" not in st.session_state:
    st.session_state.memory = {}

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your offline Python assistant. How can I help you today?"}
    ]

# Sidebar Controls
with st.sidebar:
    st.markdown("### ⚙️ System Status")
    st.success("🟢 Ollama Engine: Connected")
    st.info("📚 Vector Store: Loaded")
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Chat history cleared. Feel free to ask a new question!"}
        ]
        st.rerun()

# Glass Header Component
st.markdown("""
<div class="glass-header">
    <h1>Python RAG Assistant</h1>
    <p style="color: #475569; margin: 0; font-weight: 500;">Offline Intelligent Document QA Engine</p>
</div>
""", unsafe_allow_html=True)


def retrieve(question, top_k=2):
    response = ollama.embeddings(model=EMBEDDING_MODEL, prompt=question)
    query_vector = np.array(response["embedding"]).reshape(1, -1)
    scores = cosine_similarity(query_vector, vectors)[0]
    top_indices = np.argsort(scores)[-top_k:][::-1]
    return [(chunks[i], scores[i]) for i in top_indices]


def ask_chatbot(question):
    q_clean = question.lower().strip()

    # 1. Memory handling
    if q_clean.startswith("my name is "):
        name = question[11:].strip()
        st.session_state.memory["name"] = name
        return f"Nice to meet you, {name}! I'll remember your name during this session."

    if "what is my name" in q_clean:
        if "name" in st.session_state.memory:
            return f"Your name is {st.session_state.memory['name']}."
        return FALLBACK

    # 2. Vector retrieval
    results = retrieve(question)
    top_chunk, top_score = results[0]

    if top_score < 0.40:
        return FALLBACK

    context = "\n\n".join([chunk for chunk, score in results if score >= 0.35])

    prompt = f"""Context:
{context}

Question: {question}

Instructions:
- Provide a clear, direct answer to the question using the context.
- Keep the answer under 3 sentences.
- Do NOT mention words like "context" or "notes". Just answer directly.
- If the context does not answer the question, reply ONLY with:
{FALLBACK}

Answer:"""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response["message"]["content"].strip()

    if "context" in answer.lower() or "provided" in answer.lower():
        if top_score < 0.45:
            return FALLBACK

    return answer


# Render Chat History
for msg in st.session_state.messages:
    avatar = "🤖" if msg["role"] == "assistant" else "👤"
    st.chat_message(msg["role"], avatar=avatar).write(msg["content"])

# User Chat Input
if prompt := st.chat_input("Ask a Python question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="👤").write(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Searching Python notes..."):
            response_text = ask_chatbot(prompt)
            st.write(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})