import pickle
import numpy as np
import ollama
from sklearn.metrics.pairwise import cosine_similarity

EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3.2:1b"
FALLBACK = "I don't have information about this. You can tell me the information, and I'll remember it during this conversation."

# Load retrieval data
with open("retrieval_data.pkl", "rb") as f:
    vectors, chunks = pickle.load(f)

# Runtime memory store
memory = {}


def retrieve(question, top_k=2):
    """Embed question and find top matching chunks from PDF."""
    response = ollama.embeddings(model=EMBEDDING_MODEL, prompt=question)
    query_vector = np.array(response["embedding"]).reshape(1, -1)
    
    scores = cosine_similarity(query_vector, vectors)[0]
    top_indices = np.argsort(scores)[-top_k:][::-1]
    return [(chunks[i], scores[i]) for i in top_indices]


def ask_chatbot(question):
    q_clean = question.lower().strip()

    # 1. QUESTION HANDLER: Check if user is sharing their name
    if q_clean.startswith("my name is "):
        name = question[11:].strip()
        memory["name"] = name
        return f"Nice to meet you, {name}! I'll remember your name during this conversation."

    # 2. QUESTION HANDLER: Check if user is asking for their name
    if "what is my name" in q_clean:
        if "name" in memory:
            return f"Your name is {memory['name']}."
        return FALLBACK

    # 3. RETRIEVAL & SCORE CHECK
    results = retrieve(question)
    top_chunk, top_score = results[0]

    # QUESTION HANDLER: Strict cutoff for irrelevant/out-of-bounds questions (tea, weather, capitals, etc.)
    if top_score < 0.40:
        return FALLBACK

    context = "\n\n".join([chunk for chunk, score in results if score >= 0.35])

    # Direct answer prompt (No meta phrases like 'according to context')
    prompt = f"""Context:
{context}

Question: {question}

Instructions:
- Provide a clear, direct answer to the question using the context.
- Keep the answer under 3 sentences.
- Do NOT mention words like "context", "notes", or "provided text". Just answer the question directly.
- If the context does not answer the question, reply ONLY with:
{FALLBACK}

Answer:"""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response["message"]["content"].strip()

    # Clean up any leftover prompt references
    if "context" in answer.lower() or "provided" in answer.lower():
        if top_score < 0.45:
            return FALLBACK

    return answer


# Main Chat Loop
print("--- Python Offline RAG Chatbot Active ---")
print("Type 'exit' to quit.\n")

while True:
    user_input = input("You: ").strip()

    if not user_input:
        continue

    if user_input.lower() == "exit":
        break

    bot_reply = ask_chatbot(user_input)
    print(f"\nBot: {bot_reply}\n")
