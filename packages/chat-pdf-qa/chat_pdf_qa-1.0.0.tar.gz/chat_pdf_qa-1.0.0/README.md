# chat-pdf

Chat with PDF documents using LangChain and OpenAI.

`chat-pdf` is a lightweight Python library that allows you to load a PDF, ask questions about its content, and optionally retrieve the source passages used to generate the answers.

The library is intentionally simple and pinned to stable LangChain versions to avoid breaking changes.

---

## Features

- Load and index PDF documents
- Ask natural language questions
- Retrieve answers with or without source documents
- Minimal, function-based API
- Stable LangChain 1.2.x compatibility
- Suitable for scripts, notebooks, and APIs

---

## Installation

```bash
pip install chat-pdf
```

---

## Requirements

- Python 3.10 or higher
- OpenAI API key

Set your API key as an environment variable or pass it directly in code:

```bash
export OPENAI_API_KEY="your-api-key"
```

---

## Quick Start

### 1. Load a PDF

```python
from chat_pdf import load_pdf

db = load_pdf(
    "document.pdf",
    api_key="OPENAI_API_KEY"
)
```

This will:
- Load the PDF file
- Split it into chunks
- Generate embeddings
- Store them in a Chroma vector database

---

### 2. Ask a Question

```python
from chat_pdf import ask_question

answer = ask_question(
    "What is this document about?",
    db=db,
    api_key="OPENAI_API_KEY"
)

print(answer)
```

---

### 3. Ask a Question with Sources (Optional)

```python
from chat_pdf import ask_question_with_sources

result = ask_question_with_sources(
    "What are the termination conditions?",
    db=db,
    api_key="OPENAI_API_KEY"
)

print("Answer:")
print(result["answer"])

print("\nSources:")
for doc in result["sources"]:
    print(doc.metadata)
```

Returned keys:
- `answer` – generated response
- `sources` – list of retrieved document chunks

---

## API Reference

### load_pdf

```python
load_pdf(
    pdf_path: str,
    api_key: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    persist_directory: str | None = None
)
```

---

### ask_question

```python
ask_question(
    question: str,
    db,
    api_key: str,
    model_name: str = "gpt-3.5-turbo",
    search_kwargs: dict | None = None,
    system_prompt: str | None = None
)
```

Returns a string answer.

---

### ask_question_with_sources

```python
ask_question_with_sources(
    question: str,
    db,
    api_key: str,
    model_name: str = "gpt-3.5-turbo",
    search_kwargs: dict | None = None,
    system_prompt: str | None = None
)
```

Returns a dictionary:

```python
{
    "answer": str,
    "sources": list
}
```

---

## Version Compatibility

This package is pinned for stability.

| chat-pdf | LangChain |
|----------|-----------|
| 1.2.0.0  | 1.2.x     |

Upgrading LangChain independently is not recommended.

---

## Design Philosophy

- Simple over clever
- Stable over experimental
- Explicit over magical

This library is designed to be easy to read, debug, and extend.

---

## License

MIT License
