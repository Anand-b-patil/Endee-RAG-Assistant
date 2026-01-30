"""
FastAPI Backend for RAG System with Endee Vector Database
Production-ready API endpoints for document upload and question answering
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from pathlib import Path
import logging
from typing import List, Dict, Any

from document_loader import DocumentLoader
from chunker import TextChunker
from embeddings import EmbeddingGenerator
from endee_client import EndeeClient
from retriever import VectorRetriever
from rag import RAGPipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Endee RAG Assistant", version="1.0.0")

# CORS configuration for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize components
embedding_generator = EmbeddingGenerator()
endee_client = EndeeClient()
text_chunker = TextChunker()
document_loader = DocumentLoader()
vector_retriever = VectorRetriever(endee_client, embedding_generator)
rag_pipeline = RAGPipeline(vector_retriever)


class QuestionRequest(BaseModel):
    """Request model for question endpoint"""
    question: str


class SourceResponse(BaseModel):
    """Source chunk response model"""
    text: str
    metadata: Dict[str, Any]


class AnswerResponse(BaseModel):
    """Answer response model"""
    answer: str
    sources: List[SourceResponse]


class UploadResponse(BaseModel):
    """Upload response model"""
    message: str
    filename: str


@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    logger.info("Starting Endee RAG Assistant backend...")
    try:
        # Initialize Endee collection
        await endee_client.initialize()
        logger.info("Endee client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Endee client: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    logger.info("Shutting down Endee RAG Assistant backend...")
    await endee_client.close()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Endee RAG Assistant"}


@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process PDF or TXT document
    
    Args:
        file: PDF or TXT file
        
    Returns:
        Upload confirmation with filename
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.pdf', '.txt']:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only PDF and TXT files are supported."
            )
        
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"File saved: {file.filename}")
        
        # Extract text from document
        text = document_loader.load(str(file_path))
        
        if not text or len(text.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the document"
            )
        
        logger.info(f"Extracted {len(text)} characters from {file.filename}")
        
        # Chunk text
        chunks = text_chunker.chunk(text)
        logger.info(f"Created {len(chunks)} chunks from document")
        
        # Generate embeddings
        embeddings = embedding_generator.generate_embeddings(
            [chunk['text'] for chunk in chunks]
        )
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        # Prepare metadata for chunks
        for i, chunk in enumerate(chunks):
            chunk['metadata']['source'] = file.filename
            if 'chunk_id' not in chunk['metadata']:
                chunk['metadata']['chunk_id'] = i
        
        # Store in Endee vector database
        await endee_client.add_documents(
            texts=[chunk['text'] for chunk in chunks],
            embeddings=embeddings,
            metadatas=[chunk['metadata'] for chunk in chunks]
        )
        
        logger.info(f"Successfully stored {len(chunks)} chunks in Endee")
        
        return UploadResponse(
            message="Document uploaded successfully",
            filename=file.filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Answer question using RAG pipeline
    
    Args:
        request: Question request
        
    Returns:
        Answer with source chunks
    """
    try:
        if not request.question or len(request.question.strip()) == 0:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        logger.info(f"Received question: {request.question}")
        
        # Execute RAG pipeline
        result = await rag_pipeline.generate_answer(request.question)
        
        # Format sources
        sources = [
            SourceResponse(
                text=source['text'],
                metadata=source['metadata']
            )
            for source in result['sources']
        ]
        
        logger.info(f"Generated answer with {len(sources)} sources")
        
        return AnswerResponse(
            answer=result['answer'],
            sources=sources
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
