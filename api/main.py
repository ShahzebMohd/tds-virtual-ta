# Imports
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel
from PIL import Image
import base64, io, json, faiss, numpy as np
from sentence_transformers import SentenceTransformer
import pytesseract

# FastAPI app
app = FastAPI()

# Response model
class Link(BaseModel):
    url: str
    text: str

class QuestionResponse(BaseModel):
    answer: str
    links: List[Link]

# Load everything
with open("data/tds_chunks.json") as f:
    course_chunks = json.load(f)
course_index = faiss.read_index("data/tds_faiss.index")


with open("data/discourse_chunks.json") as f:
    discourse_chunks = json.load(f)
discourse_index = faiss.read_index("data/discourse_faiss.index")


embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Embedding + search functions
def get_embedding(text, model):
    return model.encode([text])[0]

def get_top_chunks(query, chunks, index, top_k=5):
    query_vector = get_embedding(query, embedder).astype("float32")
    D, I = index.search(np.array([query_vector]), top_k)
    return [chunks[i] for i in I[0]]

# OCR utility
def extract_text_from_file(uploaded_file: UploadFile):
    image = Image.open(uploaded_file.file)
    return pytesseract.image_to_string(image)

# API route
@app.post("/api/", response_model=QuestionResponse)
async def answer_question(
    request: Request,
    question: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None)
):
    # Detect request type
    content_type = request.headers.get("content-type", "")
    is_json = "application/json" in content_type

    if is_json:
        body = await request.json()
        query = body.get("question", "").strip()
        image_b64 = body.get("image")

        if image_b64:
            try:
                image_data = base64.b64decode(image_b64)
                img = Image.open(io.BytesIO(image_data))
                ocr_text = pytesseract.image_to_string(img)
                query += " " + ocr_text.strip()
            except Exception as e:
                print(f"[OCR Error] Invalid base64 image: {e}")
    else:
        query = (question or "").strip()
        if image:
            try:
                img = Image.open(image.file)
                ocr_text = pytesseract.image_to_string(img)
                query += " " + ocr_text.strip()
            except Exception as e:
                print(f"[OCR Error] Uploaded file issue: {e}")

    course_results = get_top_chunks(query, course_chunks, course_index)
    discourse_results = get_top_chunks(query, discourse_chunks, discourse_index)

    answer = "📘 **Course Content:**\n"
    for i, chunk in enumerate(course_results):
        answer += f"{i+1}. {chunk['text'][:300].strip()}...\n\n"

    answer += "\n💬 **Discourse Posts:**\n"
    for i, chunk in enumerate(discourse_results):
        answer += f"{i+1}. {chunk['text'][:300].strip()}...\n\n"

    links = [
        {"url": chunk["url"], "text": chunk["source"]}
        for chunk in course_results + discourse_results
    ]

    return {"answer": answer.strip(), "links": links}
