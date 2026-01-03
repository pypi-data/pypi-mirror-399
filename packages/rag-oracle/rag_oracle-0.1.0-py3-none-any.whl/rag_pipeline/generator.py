"""
Step 1.5 - Generator (LLM)
Answer questions using retrieved chunks and a prompt.
"""

import os
from typing import List, Optional
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.llms import HuggingFacePipeline
from langchain_core.output_parsers import StrOutputParser

try:
    from langchain_groq import ChatGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    ChatGroq = None


class RAGGenerator:
    """Generate answers using LLM with retrieved context."""
    
    @staticmethod
    def _detect_available_api(openai_api_key: Optional[str], groq_api_key: Optional[str]) -> tuple[str, str]:
        """
        Detect which API key is available. Priority: OpenAI > Groq.
        
        Returns:
            Tuple of (model_type, model_name) for the available API
        """
        # Check OpenAI first (priority)
        openai_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if openai_key:
            return "openai", "gpt-3.5-turbo"
        
        # Fallback to Groq
        groq_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if groq_key:
            return "groq", "llama-3.3-70b-versatile"
        
        # No API key found
        raise ValueError(
            "No API key found. Please set either OPENAI_API_KEY or GROQ_API_KEY in your .env file, "
            "or pass openai_api_key/groq_api_key parameter. OpenAI has priority if both are available."
        )
    
    def __init__(
        self,
        model_type: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        openai_api_key: Optional[str] = None,
        groq_api_key: Optional[str] = None,
        system_prompt: Optional[str] = None
    ):
        """
        Initialize the generator.
        
        Args:
            model_type: "openai", "groq", "auto", or None (auto-detect). Default: None (auto-detect)
            model_name: Name of the model to use. Default: auto-selected based on available API
            temperature: Temperature for generation (0.0-1.0)
            openai_api_key: OpenAI API key (if using OpenAI)
            groq_api_key: Groq API key (if using Groq)
            system_prompt: Custom system prompt (optional)
            
        Note:
            If model_type is None or "auto", automatically detects available API keys.
            Priority: OpenAI > Groq (if both are available, OpenAI is used)
            Groq models: llama-3.3-70b-versatile, mixtral-8x7b-32768, gemma2-9b-it, etc.
        """
        # Auto-detect if model_type is None or "auto"
        if model_type is None or model_type == "auto":
            detected_type, default_model = self._detect_available_api(openai_api_key, groq_api_key)
            model_type = detected_type
            if model_name is None:
                model_name = default_model
            print(f"Auto-detected API: {model_type} (model: {model_name})")
        
        self.model_type = model_type
        self.temperature = temperature
        
        # Initialize LLM
        if model_type == "openai":
            api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var or pass openai_api_key.")
            actual_model_name = model_name or "gpt-3.5-turbo"
            print(f"Using OpenAI API with model: {actual_model_name}")
            self.llm = ChatOpenAI(
                model=actual_model_name,
                temperature=temperature,
                api_key=api_key
            )
            self.model_name = actual_model_name
        elif model_type == "groq":
            if not GROQ_AVAILABLE:
                raise ImportError(
                    "langchain-groq package is required for Groq. Install it with: pip install langchain-groq"
                )
            api_key = groq_api_key or os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("Groq API key required. Set GROQ_API_KEY env var or pass groq_api_key.")
            actual_model_name = model_name or "llama-3.3-70b-versatile"
            print(f"Using Groq API with model: {actual_model_name}")
            # Groq models: llama-3.3-70b-versatile, mixtral-8x7b-32768, gemma2-9b-it, llama-3.1-8b-instant, etc.
            # Get your API key from https://console.groq.com/keys
            try:
                self.llm = ChatGroq(
                    model=actual_model_name,
                    temperature=temperature,
                    groq_api_key=api_key
                )
            except Exception as e:
                if "API key" in str(e) or "authentication" in str(e).lower():
                    raise ValueError(
                        f"Groq API authentication failed. Please verify your GROQ_API_KEY in .env file. "
                        f"Get your API key from https://console.groq.com/keys. Error: {str(e)}"
                    ) from e
                raise
            self.model_name = actual_model_name
        elif model_type == "huggingface":
            # For HuggingFace, you would load a model here
            # This is a placeholder - actual implementation would require model loading
            raise NotImplementedError("HuggingFace models not yet implemented. Use OpenAI or Groq for now.")
        else:
            raise ValueError(f"Unsupported model type: {model_type}. Use 'openai', 'groq', 'auto', or None for auto-detect.")
        
        # Default system prompt
        self.system_prompt = system_prompt or (
            "You are a helpful assistant that answers questions based on the provided context. "
            "Use only the information from the context to answer. If the context doesn't contain "
            "enough information to answer the question, say so."
        )
        
        # Create prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "Context:\n{context}\n\nQuestion: {question}\n\nAnswer:")
        ])
        
        # Create chain
        self.chain = self.prompt_template | self.llm | StrOutputParser()
    
    def generate(
        self,
        question: str,
        retrieved_chunks: List[Document],
        custom_prompt: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Generate an answer using retrieved chunks.
        
        Args:
            question: The question to answer
            retrieved_chunks: List of retrieved Document objects
            custom_prompt: Optional custom prompt to override default
            
        Returns:
            Tuple of (answer, full_prompt_used)
        """
        # Combine retrieved chunks into context, including metadata
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks):
            meta_str = ", ".join([f"{k}: {v}" for k, v in chunk.metadata.items() if k not in ['source', 'producer', 'creator']])
            context_parts.append(f"Document {i+1} Metadata: [{meta_str}]\nContent: {chunk.page_content}")
        
        context = "\n\n".join(context_parts)
        
        # Build the full prompt string for logging
        if custom_prompt:
            user_prompt = custom_prompt.format(context=context, question=question)
            full_prompt = f"System: {self.system_prompt}\n\nHuman: {user_prompt}"
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", user_prompt)
            ])
            chain = prompt | self.llm | StrOutputParser()
            answer = chain.invoke({"context": context, "question": question})
        else:
            user_prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
            full_prompt = f"System: {self.system_prompt}\n\nHuman: {user_prompt}"
            answer = self.chain.invoke({"context": context, "question": question})
        
        return answer, full_prompt
    
    def update_temperature(self, temperature: float):
        """
        Update the temperature for generation.
        
        Args:
            temperature: New temperature value (0.0-1.0)
        """
        self.temperature = temperature
        if self.model_type in ["openai", "groq"]:
            self.llm.temperature = temperature
    
    def update_system_prompt(self, system_prompt: str):
        """
        Update the system prompt.
        
        Args:
            system_prompt: New system prompt
        """
        self.system_prompt = system_prompt
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "Context:\n{context}\n\nQuestion: {question}\n\nAnswer:")
        ])
        self.chain = self.prompt_template | self.llm | StrOutputParser()

