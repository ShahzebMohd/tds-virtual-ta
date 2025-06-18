from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel
from PIL import Image
import pytesseract
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import io

# Load course and discourse data
with open("data/tds_chunks.json") as f:
    course_chunks = json.load(f)

with open("data/discourse_chunks.json") as f:
    discourse_chunks = json.load(f)

course_index = faiss.read_index("data/tds_faiss.index")
discourse_index = faiss.read_index("data/discourse_faiss.index")

# Load local embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Define schema for response
class Link(BaseModel):
    url: str
    text: str

class QuestionResponse(BaseModel):
    answer: str
    links: List[Link]

# OCR utility
def extract_text_from_file(uploaded_file: UploadFile):
    image = Image.open(uploaded_file.file)
    return pytesseract.image_to_string(image)

# Embedding-based search utility
def get_top_chunks(query: str, chunks: List[dict], index: faiss.IndexFlatL2, top_k: int = 5):
    query_embedding = model.encode([query])
    distances, indices = index.search(np.array(query_embedding).astype("float32"), top_k)
    return [chunks[i] for i in indices[0] if i < len(chunks)]

# Create FastAPI app
app = FastAPI()

@app.post("/api/", response_model=QuestionResponse)
async def answer_question(
    question: str = Form(...),
    image: Optional[UploadFile] = File(None)
):
    query = question.strip()

    if image:
        ocr_text = extract_text_from_file(image)
        query += " " + ocr_text.strip()

    # Search in course and discourse chunks
    course_results = get_top_chunks(query, course_chunks, course_index)
    discourse_results = get_top_chunks(query, discourse_chunks, discourse_index)

    # Construct answer from most relevant discourse post (if any), else course
    if discourse_results:
        answer = discourse_results[0]["text"].strip()
    elif course_results:
        answer = course_results[0]["text"].strip()
    else:
        answer = "Sorry, no relevant information found in course or discourse content."

    # Collect unique links from top results
    seen = set()
    links = []
    for chunk in discourse_results + course_results:
        url = chunk.get("url")
        text = chunk.get("source", "")
        if url and url not in seen:
            seen.add(url)
            links.append({"url": url, "text": text})
        if len(links) >= 4:
            break

    return {"answer": answer, "links": links}
