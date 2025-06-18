import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load data
with open("data/tds_course_content.json", "r") as f:
    data = json.load(f)

# Initialize embedding model
print("🔄 Loading local embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Chunking settings
CHUNK_SIZE = 300  # ~300 words
CHUNK_OVERLAP = 50

# Chunk the content
chunks = []

def split_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append({
            "text": chunk,
            "source": current["title"],
            "url": current["url"]
        })
        i += chunk_size - overlap

for current in data:
    content = current["content"]
    split_text(content)

print(f"🔹 Total chunks: {len(chunks)}")

# Generate embeddings
print("🔄 Embedding chunks locally...")
texts = [chunk["text"] for chunk in chunks]
embeddings = model.encode(texts, show_progress_bar=True)

# Build FAISS index
dimension = len(embeddings[0])
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings).astype("float32"))

# Save the index and chunks
faiss.write_index(index, "data/tds_faiss.index")
with open("data/tds_chunks.json", "w") as f:
    json.dump(chunks, f, indent=2)

print("✅ Done! Local embeddings + FAISS index saved.")

