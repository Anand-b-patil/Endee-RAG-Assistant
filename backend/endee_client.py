"""
Endee Vector Database Client
Handles all interactions with the Endee vector database
"""

import os
import httpx
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import numpy as np
import uuid

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class EndeeClient:
    """Client for Endee Vector Database operations"""
    
    def __init__(self):
        """Initialize Endee client with API credentials"""
        self.api_key = os.getenv("ENDEE_API_KEY")
        self.base_url = os.getenv("ENDEE_URL", "https://api.endee.io")
        
        if not self.api_key:
            logger.warning("ENDEE_API_KEY not found. Using mock mode.")
            self.mock_mode = True
            self.mock_storage = []
        else:
            self.mock_mode = False
        
        self.collection_name = "rag_documents"
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
    
    async def initialize(self):
        """Initialize or create collection in Endee"""
        if self.mock_mode:
            logger.info("Running in mock mode - no actual Endee connection")
            return
        
        try:
            # Check if collection exists
            response = await self.client.get(
                f"{self.base_url}/collections/{self.collection_name}"
            )
            
            if response.status_code == 404:
                # Create collection
                await self.create_collection()
            
            logger.info(f"Collection '{self.collection_name}' ready")
            
        except Exception as e:
            logger.error(f"Error initializing Endee: {e}")
            logger.info("Falling back to mock mode")
            self.mock_mode = True
            self.mock_storage = []
    
    async def create_collection(self):
        """Create a new collection in Endee"""
        if self.mock_mode:
            return
        
        try:
            payload = {
                "name": self.collection_name,
                "dimension": 384,  # all-MiniLM-L6-v2 dimension
                "metric": "cosine"
            }
            
            response = await self.client.post(
                f"{self.base_url}/collections",
                json=payload
            )
            response.raise_for_status()
            
            logger.info(f"Created collection: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise
    
    async def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ):
        """
        Add documents with embeddings to Endee
        
        Args:
            texts: List of text chunks
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
        """
        if self.mock_mode:
            # Store in mock storage
            for text, embedding, metadata in zip(texts, embeddings, metadatas):
                self.mock_storage.append({
                    'id': str(uuid.uuid4()),
                    'text': text,
                    'embedding': embedding,
                    'metadata': metadata
                })
            logger.info(f"Added {len(texts)} documents to mock storage")
            return
        
        try:
            # Prepare documents for Endee
            documents = []
            for i, (text, embedding, metadata) in enumerate(zip(texts, embeddings, metadatas)):
                documents.append({
                    "id": str(uuid.uuid4()),
                    "vector": embedding,
                    "metadata": {
                        **metadata,
                        "text": text
                    }
                })
            
            # Batch insert to Endee
            response = await self.client.post(
                f"{self.base_url}/collections/{self.collection_name}/documents",
                json={"documents": documents}
            )
            response.raise_for_status()
            
            logger.info(f"Successfully added {len(documents)} documents to Endee")
            
        except Exception as e:
            logger.error(f"Error adding documents to Endee: {e}")
            raise
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents in Endee
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            
        Returns:
            List of similar documents with text and metadata
        """
        if self.mock_mode:
            # Mock search using cosine similarity
            if not self.mock_storage:
                return []
            
            query_vector = np.array(query_embedding)
            similarities = []
            
            for doc in self.mock_storage:
                doc_vector = np.array(doc['embedding'])
                # Cosine similarity
                similarity = np.dot(query_vector, doc_vector) / (
                    np.linalg.norm(query_vector) * np.linalg.norm(doc_vector)
                )
                similarities.append({
                    'text': doc['text'],
                    'metadata': doc['metadata'],
                    'score': float(similarity)
                })
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x['score'], reverse=True)
            results = similarities[:top_k]
            
            logger.info(f"Mock search returned {len(results)} results")
            return results
        
        try:
            # Search in Endee
            payload = {
                "vector": query_embedding,
                "top_k": top_k,
                "include_metadata": True
            }
            
            response = await self.client.post(
                f"{self.base_url}/collections/{self.collection_name}/search",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("results", []):
                metadata = item.get("metadata", {})
                text = metadata.pop("text", "")
                
                results.append({
                    "text": text,
                    "metadata": metadata,
                    "score": item.get("score", 0.0)
                })
            
            logger.info(f"Endee search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching Endee: {e}")
            raise
    
    async def delete_collection(self):
        """Delete the collection from Endee"""
        if self.mock_mode:
            self.mock_storage = []
            return
        
        try:
            response = await self.client.delete(
                f"{self.base_url}/collections/{self.collection_name}"
            )
            response.raise_for_status()
            logger.info(f"Deleted collection: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            raise
    
    async def close(self):
        """Close the HTTP client"""
        if not self.mock_mode:
            await self.client.aclose()
