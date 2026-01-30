"""
RAG Pipeline - Retrieval-Augmented Generation
Combines vector retrieval with LLM generation for question answering
"""

import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
from retriever import VectorRetriever

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class RAGPipeline:
    """RAG pipeline for question answering"""
    
    def __init__(self, retriever: VectorRetriever):
        """
        Initialize RAG pipeline
        
        Args:
            retriever: Vector retriever instance
        """
        self.retriever = retriever
        
        # Determine which LLM to use
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.mistral_key = os.getenv("MISTRAL_API_KEY")
        
        # Initialize LLM client
        if self.openai_key:
            self._init_openai()
        elif self.gemini_key:
            self._init_gemini()
        elif self.mistral_key:
            self._init_mistral()
        else:
            logger.warning("No LLM API key found. Using template-based responses.")
            self.llm_type = "template"
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        try:
            from openai import AsyncOpenAI
            self.llm_client = AsyncOpenAI(api_key=self.openai_key)
            self.llm_type = "openai"
            self.model_name = "gpt-3.5-turbo"
            logger.info("Initialized OpenAI client")
        except ImportError:
            logger.error("OpenAI package not installed. Run: pip install openai")
            self.llm_type = "template"
    
    def _init_gemini(self):
        """Initialize Google Gemini client"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_key)
            self.llm_client = genai.GenerativeModel('gemini-pro')
            self.llm_type = "gemini"
            logger.info("Initialized Gemini client")
        except ImportError:
            logger.error("Google Generative AI package not installed. Run: pip install google-generativeai")
            self.llm_type = "template"
    
    def _init_mistral(self):
        """Initialize Mistral client"""
        try:
            from mistralai.client import MistralClient
            self.llm_client = MistralClient(api_key=self.mistral_key)
            self.llm_type = "mistral"
            self.model_name = "mistral-small"
            logger.info("Initialized Mistral client")
        except ImportError:
            logger.error("Mistral AI package not installed. Run: pip install mistralai")
            self.llm_type = "template"
    
    async def generate_answer(
        self,
        question: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Generate answer using RAG pipeline
        
        Args:
            question: User question
            top_k: Number of documents to retrieve
            
        Returns:
            Dictionary with answer and sources
        """
        try:
            logger.info(f"Generating answer for: {question}")
            
            # Step 1: Retrieve relevant documents
            retrieved_docs = await self.retriever.retrieve(question, top_k=top_k)
            
            if not retrieved_docs:
                return {
                    "answer": "I don't have enough information to answer this question. Please upload relevant documents first.",
                    "sources": []
                }
            
            # Step 2: Prepare context from retrieved documents
            context = self._prepare_context(retrieved_docs)
            
            # Step 3: Generate answer using LLM
            answer = await self._generate_llm_response(question, context)
            
            # Step 4: Format sources
            sources = [
                {
                    "text": doc["text"],
                    "metadata": doc.get("metadata", {})
                }
                for doc in retrieved_docs
            ]
            
            logger.info("Answer generated successfully")
            
            return {
                "answer": answer,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise
    
    def _prepare_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Prepare context from retrieved documents
        
        Args:
            documents: Retrieved documents
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            text = doc.get("text", "")
            metadata = doc.get("metadata", {})
            source = metadata.get("source", "Unknown")
            page = metadata.get("page", "Unknown")
            
            context_parts.append(
                f"[Source {i} - {source}, Page {page}]\n{text}"
            )
        
        return "\n\n".join(context_parts)
    
    async def _generate_llm_response(self, question: str, context: str) -> str:
        """
        Generate response using LLM
        
        Args:
            question: User question
            context: Retrieved context
            
        Returns:
            Generated answer
        """
        if self.llm_type == "openai":
            return await self._generate_openai_response(question, context)
        elif self.llm_type == "gemini":
            return await self._generate_gemini_response(question, context)
        elif self.llm_type == "mistral":
            return await self._generate_mistral_response(question, context)
        else:
            return self._generate_template_response(question, context)
    
    async def _generate_openai_response(self, question: str, context: str) -> str:
        """Generate response using OpenAI"""
        try:
            prompt = self._create_prompt(question, context)
            
            response = await self.llm_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on the provided context. "
                                   "If the context doesn't contain enough information, say so."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error with OpenAI: {e}")
            return self._generate_template_response(question, context)
    
    async def _generate_gemini_response(self, question: str, context: str) -> str:
        """Generate response using Gemini"""
        try:
            prompt = self._create_prompt(question, context)
            response = await self.llm_client.generate_content_async(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error with Gemini: {e}")
            return self._generate_template_response(question, context)
    
    async def _generate_mistral_response(self, question: str, context: str) -> str:
        """Generate response using Mistral"""
        try:
            prompt = self._create_prompt(question, context)
            
            response = self.llm_client.chat(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on the provided context."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error with Mistral: {e}")
            return self._generate_template_response(question, context)
    
    def _generate_template_response(self, question: str, context: str) -> str:
        """Generate template-based response (fallback)"""
        # Extract key sentences from context
        sentences = context.split('.')[:3]
        summary = '. '.join(sentences).strip()
        
        return (
            f"Based on the retrieved documents: {summary}. "
            f"This is a template response. Configure an LLM API key for better answers."
        )
    
    def _create_prompt(self, question: str, context: str) -> str:
        """Create prompt for LLM"""
        return f"""Answer the following question based on the provided context. 
If the context doesn't contain enough information to answer the question, say so clearly.

Context:
{context}

Question: {question}

Answer:"""
