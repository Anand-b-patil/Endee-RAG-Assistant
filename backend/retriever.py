"""
Vector Retriever
Performs similarity search using embeddings and Endee vector database
"""

import logging
from typing import List, Dict, Any
from embeddings import EmbeddingGenerator
from endee_client import EndeeClient

logger = logging.getLogger(__name__)


class VectorRetriever:
    """Retrieve relevant documents using vector similarity search"""
    
    def __init__(
        self,
        endee_client: EndeeClient,
        embedding_generator: EmbeddingGenerator,
        top_k: int = 5
    ):
        """
        Initialize vector retriever
        
        Args:
            endee_client: Endee database client
            embedding_generator: Embedding generator
            top_k: Number of documents to retrieve
        """
        self.endee_client = endee_client
        self.embedding_generator = embedding_generator
        self.top_k = top_k
    
    async def retrieve(
        self,
        query: str,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: Query text
            top_k: Number of documents to retrieve (overrides default)
            
        Returns:
            List of retrieved documents with text and metadata
        """
        if not query or len(query.strip()) == 0:
            raise ValueError("Query cannot be empty")
        
        # Use provided top_k or default
        k = top_k if top_k is not None else self.top_k
        
        try:
            logger.info(f"Retrieving documents for query: {query[:100]}...")
            
            # Generate query embedding
            query_embedding = self.embedding_generator.generate_embedding(query)
            
            # Search in Endee vector database
            results = await self.endee_client.search(
                query_embedding=query_embedding,
                top_k=k
            )
            
            logger.info(f"Retrieved {len(results)} documents")
            
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            raise
    
    async def retrieve_with_threshold(
        self,
        query: str,
        similarity_threshold: float = 0.5,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents with similarity threshold filtering
        
        Args:
            query: Query text
            similarity_threshold: Minimum similarity score (0-1)
            max_results: Maximum number of results
            
        Returns:
            List of retrieved documents above threshold
        """
        # Retrieve more results than needed for filtering
        results = await self.retrieve(query, top_k=max_results)
        
        # Filter by threshold
        filtered_results = [
            r for r in results
            if r.get('score', 0) >= similarity_threshold
        ]
        
        logger.info(
            f"Filtered {len(results)} results to {len(filtered_results)} "
            f"above threshold {similarity_threshold}"
        )
        
        return filtered_results
