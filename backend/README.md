# Endee RAG Assistant Backend

Production-ready backend for Retrieval-Augmented Generation (RAG) system with Endee Vector Database.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
- `ENDEE_API_KEY` - Endee vector database API key
- `OPENAI_API_KEY` - OpenAI API key (or Gemini/Mistral)

### 3. Run the Server
```bash
python app.py
```

Server runs on: `http://localhost:8000`

## API Endpoints

### Upload Document
```bash
POST /upload
Content-Type: multipart/form-data

curl -X POST "http://localhost:8000/upload" \
  -F "file=@document.pdf"
```

### Ask Question
```bash
POST /ask
Content-Type: application/json

curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?"}'
```

## Architecture

```
Document Upload → Text Extraction → Chunking → Embedding → Endee Storage
                                                                ↓
Question → Query Embedding → Vector Search ← Endee Database ← Retrieved Chunks
                                    ↓
                              LLM Generation → Answer + Sources
```

## Components

- `app.py` - FastAPI application with endpoints
- `endee_client.py` - Endee vector database client
- `embeddings.py` - Sentence transformer embeddings
- `document_loader.py` - PDF/TXT text extraction
- `chunker.py` - Text chunking with overlap
- `retriever.py` - Vector similarity search
- `rag.py` - RAG pipeline with LLM

## Features

✅ PDF and TXT support  
✅ Semantic chunking with overlap  
✅ Vector embeddings (all-MiniLM-L6-v2)  
✅ Endee vector database integration  
✅ RAG with OpenAI/Gemini/Mistral  
✅ CORS enabled for frontend  
✅ Async API endpoints  
✅ Production error handling  
✅ Comprehensive logging  

## Development

Run with auto-reload:
```bash
uvicorn app:app --reload
```

## License

MIT
