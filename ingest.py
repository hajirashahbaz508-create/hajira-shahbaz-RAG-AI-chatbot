import pickle
import numpy as np
import ollama
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

PDF_FILE = "python notes.pdf"
EMBEDDING_MODEL = "nomic-embed-text"

# 1. Extract text from PDF
reader = PdfReader(PDF_FILE)
text = ""
for page in reader.pages:
    extracted = page.extract_text()
    if extracted:
        text += extracted + "\n"

# 2. Split text into manageable chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)
chunks = splitter.split_text(text)

print("Generating offline vector embeddings...")

# 3. Create dense semantic embeddings using Ollama
vectors = []
for i, chunk in enumerate(chunks):
    response = ollama.embeddings(model=EMBEDDING_MODEL, prompt=chunk)
    vectors.append(response["embedding"])

vectors = np.array(vectors)

# 4. Save vectors and chunks
with open("retrieval_data.pkl", "wb") as f:
    pickle.dump((vectors, chunks), f)

print("Ingestion complete! Database ready.")