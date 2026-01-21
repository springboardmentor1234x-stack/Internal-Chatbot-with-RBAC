"""
LLM Manager - Multi-Provider LLM Interface
Supports OpenAI, HuggingFace, and Local models with automatic fallback
"""

import os
from typing import Optional, Dict, Any, List
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"
    SIMULATED = "simulated"  # Fallback for testing


class LLMManager:
    """
    Unified interface for multiple LLM providers
    Automatically selects best available provider
    """
    
    def __init__(self, provider: Optional[LLMProvider] = None):
        """
        Initialize LLM Manager
        
        Args:
            provider: Specific provider to use (None for auto-select)
        """
        self.provider = provider or self._auto_select_provider()
        self.client = None
        self._initialize_client()
        
        logger.info(f"✅ LLM Manager initialized with provider: {self.provider.value}")
    
    def _auto_select_provider(self) -> LLMProvider:
        """Automatically select best available provider"""
        
        # Check HuggingFace (preferred for this project)
        if os.getenv("HUGGINGFACE_API_KEY"):
            logger.info("🔑 HuggingFace API key found - using HuggingFace")
            return LLMProvider.HUGGINGFACE
        
        # Check OpenAI API key
        if os.getenv("OPENAI_API_KEY"):
            logger.info("🔑 OpenAI API key found - using OpenAI")
            return LLMProvider.OPENAI
        
        # Check if we want to use local model
        if os.getenv("USE_LOCAL_MODEL", "false").lower() == "true":
            logger.info("🖥️  Local model enabled - using Local")
            return LLMProvider.LOCAL
        
        # Fallback to simulated
        logger.warning("⚠️  No LLM provider configured - using simulated responses")
        return LLMProvider.SIMULATED
    
    def _initialize_client(self):
        """Initialize the LLM client based on provider"""
        
        if self.provider == LLMProvider.OPENAI:
            self._initialize_openai()
        elif self.provider == LLMProvider.HUGGINGFACE:
            self._initialize_huggingface()
        elif self.provider == LLMProvider.LOCAL:
            self._initialize_local()
        else:
            # Simulated - no client needed
            self.client = None
    
    def _initialize_openai(self):
        """Initialize OpenAI client"""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            logger.info("✅ OpenAI client initialized")
        except ImportError:
            logger.error("❌ OpenAI library not installed. Run: pip install openai")
            self.provider = LLMProvider.SIMULATED
        except Exception as e:
            logger.error(f"❌ Error initializing OpenAI: {e}")
            self.provider = LLMProvider.SIMULATED
    
    def _initialize_huggingface(self):
        """Initialize HuggingFace client"""
        try:
            from huggingface_hub import InferenceClient
            self.client = InferenceClient(token=os.getenv("HUGGINGFACE_API_KEY"))
            logger.info("✅ HuggingFace client initialized")
        except ImportError:
            logger.error("❌ HuggingFace library not installed. Run: pip install huggingface-hub")
            self.provider = LLMProvider.SIMULATED
        except Exception as e:
            logger.error(f"❌ Error initializing HuggingFace: {e}")
            self.provider = LLMProvider.SIMULATED
    
    def _initialize_local(self):
        """Initialize local model"""
        try:
            from transformers import pipeline
            model_name = os.getenv("LOCAL_MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
            logger.info(f"📥 Loading local model: {model_name} (this may take a while...)")
            self.client = pipeline(
                "text-generation",
                model=model_name,
                max_new_tokens=512,
                device_map="auto"
            )
            logger.info("✅ Local model initialized")
        except ImportError:
            logger.error("❌ Transformers library not installed. Run: pip install transformers torch")
            self.provider = LLMProvider.SIMULATED
        except Exception as e:
            logger.error(f"❌ Error initializing local model: {e}")
            self.provider = LLMProvider.SIMULATED
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """
        Generate response from LLM
        
        Args:
            system_prompt: System-level instructions
            user_prompt: User query with context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
        
        Returns:
            Generated text response
        """
        
        if self.provider == LLMProvider.OPENAI:
            return self._generate_openai(system_prompt, user_prompt, max_tokens, temperature)
        elif self.provider == LLMProvider.HUGGINGFACE:
            return self._generate_huggingface(system_prompt, user_prompt, max_tokens, temperature)
        elif self.provider == LLMProvider.LOCAL:
            return self._generate_local(system_prompt, user_prompt, max_tokens, temperature)
        else:
            return self._generate_simulated(system_prompt, user_prompt)
    
    def _generate_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"❌ OpenAI generation error: {e}")
            return self._generate_simulated(system_prompt, user_prompt)
    
    def _generate_huggingface(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using HuggingFace"""
        try:
            model = os.getenv("HUGGINGFACE_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
            
            # Format as chat messages for instruct models
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.client.chat_completion(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Extract the response text
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"❌ HuggingFace generation error: {e}")
            return self._generate_simulated(system_prompt, user_prompt)
    
    def _generate_local(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using local model"""
        try:
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            outputs = self.client(
                full_prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True
            )
            return outputs[0]['generated_text'][len(full_prompt):].strip()
        except Exception as e:
            logger.error(f"❌ Local model generation error: {e}")
            return self._generate_simulated(system_prompt, user_prompt)
    
    def _generate_simulated(self, system_prompt: str, user_prompt: str) -> str:
        """Fallback: Generate simulated response (for testing without LLM)"""
        logger.warning("⚠️  Using simulated LLM response")
        
        # Extract context if available
        if "CONTEXT DOCUMENTS:" in user_prompt:
            context_start = user_prompt.find("CONTEXT DOCUMENTS:") + len("CONTEXT DOCUMENTS:")
            context_end = user_prompt.find("USER QUESTION:")
            if context_end > context_start:
                context = user_prompt[context_start:context_end].strip()
                
                # Extract first chunk for response
                if "[chunk_" in context:
                    chunks = context.split("---")
                    if chunks:
                        first_chunk = chunks[0]
                        content_start = first_chunk.find("Content:") + len("Content:")
                        if content_start > 8:
                            content = first_chunk[content_start:].strip()
                            chunk_id = first_chunk[first_chunk.find("["):first_chunk.find("]")+1]
                            return f"Based on the available information: {content[:200]}... {chunk_id}"
        
        return "I don't have enough information in the accessible documents to answer this question. (Simulated response - no LLM configured)"
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about current provider"""
        return {
            "provider": self.provider.value,
            "is_configured": self.client is not None,
            "model": self._get_model_name()
        }
    
    def _get_model_name(self) -> str:
        """Get the model name being used"""
        if self.provider == LLMProvider.OPENAI:
            return os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        elif self.provider == LLMProvider.HUGGINGFACE:
            return os.getenv("HUGGINGFACE_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
        elif self.provider == LLMProvider.LOCAL:
            return os.getenv("LOCAL_MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
        else:
            return "simulated"


# Test function
if __name__ == "__main__":
    print("🧪 Testing LLM Manager\n")
    
    # Initialize manager
    llm = LLMManager()
    
    # Get provider info
    info = llm.get_provider_info()
    print(f"Provider: {info['provider']}")
    print(f"Configured: {info['is_configured']}")
    print(f"Model: {info['model']}\n")
    
    # Test generation
    system = "You are a helpful assistant."
    user = "What is 2+2?"
    
    print("Generating response...")
    response = llm.generate(system, user, max_tokens=50)
    print(f"\nResponse: {response}")
