import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load Discourse posts
with open("data/tds_discourse.json", "r") as f:
    data = json.load(f)

# Load embedding model
print("🔄 Loading local embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Chunking settings
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50

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

# Split each post into chunks
for current in data:
    split_text(current["content"])

print(f"🔹 Total Discourse chunks: {len(chunks)}")

# Embed each chunk
print("🔄 Embedding chunks locally...")
texts = [chunk["text"] for chunk in chunks]
embeddings = model.encode(texts, show_progress_bar=True)

# Build FAISS index
dimension = len(embeddings[0])
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings).astype("float32"))

# Save to disk
faiss.write_index(index, "data/discourse_faiss.index")
with open("data/discourse_chunks.json", "w") as f:
    json.dump(chunks, f, indent=2)

print("✅ Discourse embeddings and index saved.")

