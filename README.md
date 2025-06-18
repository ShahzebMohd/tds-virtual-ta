# TDS Virtual TA

This project is the final submission for the **Tools in Data Science** course at **IIT Madras (May 2025 batch)**.

It is a virtual TA powered by embeddings, retrieval, and an LLM. It can answer any student question using course content and Discourse posts. You may optionally attach an image (e.g. screenshot) for OCR-based understanding.

---

## 🔧 Features

- 🔍 **RAG-based QA** over:
  - All official [TDS course content](https://tds.s-anand.net/)
  - All Discourse posts from the TDS category
- 🧠 Embeddings via OpenAI or local model
- 📸 Optional image input with OCR
- ⚡ FastAPI-based API endpoint
- 🧪 Testable via `curl` or `promptfoo`

---

## 📦 Usage

### API Endpoint (POST `/api/`)

Send JSON like this:

```json
{
  "question": "What model should I use for GA5 Q8?",
  "image": "<base64_encoded_image>"  // optional
}
