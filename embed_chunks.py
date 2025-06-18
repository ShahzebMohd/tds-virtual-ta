import json
import os
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken
import faiss
import numpy as np

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load scraped data
with open("data/tds_course_content.json", "r") as f:

    data = json.load(f)

# Settings
CHUNK_SIZE = 300  # in tokens
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "text-embedding-3-small"

# Tokenizer
tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")

# Store chunks
chunks = []

for entry in data:
    title = entry["title"]
    url = entry["url"]
    content = entry["content"]

    tokens = tokenizer.encode(content)
    for i in range(0, len(tokens), CHUNK_SIZE - CHUNK_OVERLAP):
        chunk_tokens = tokens[i:i + CHUNK_SIZE]
        chunk_text = tokenizer.decode(chunk_tokens)

        chunks.append({
            "title": title,
            "url": url,
            "text": chunk_text
        })

print(f"🔹 Total chunks: {len(chunks)}")

# Embed chunks
print("🔄 Getting embeddings from OpenAI...")
embeddings = []
batch_size = 100
for i in range(0, len(chunks), batch_size):
    texts = [c["text"] for c in chunks[i:i + batch_size]]
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts
    )
    emb = [e.embedding for e in response.data]
    embeddings.extend(emb)

print("✅ Embeddings generated!")

# Save chunks + build FAISS index
dimension = len(embeddings[0])
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings).astype("float32"))

# Save index
faiss.write_index(index, "data/tds_faiss.index")

with open("data/tds_chunks.json", "w") as f:
    json.dump(chunks, f, indent=2)


print("✅ FAISS index and metadata saved!")

