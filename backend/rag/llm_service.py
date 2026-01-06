import requests
from transformers import pipeline
from typing import Dict, Any
from services.audit_logger import AuditLogger
from config import Config

class LLMService:
    """Service for generating responses using LLM providers"""
    
    def __init__(self, audit_logger: AuditLogger = None):
        self.provider = Config.LLM_PROVIDER
        self.hf_token = Config.HF_API_TOKEN
        self.hf_model = Config.HF_MODEL
        self.audit_logger = audit_logger or AuditLogger()
        self._local_pipeline = None

        self.audit_logger.log_component_init("LLM Service", self.provider)
    
    def generate_response(self, prompt: str, max_tokens: int = 500) -> Dict[str, Any]:
        """
        Generate response using configured LLM provider
        
        Args:
            prompt: Complete prompt with context and query
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dict with response, model info, or error
        """
        if self.hf_model == "google/flan-t5-base":
            return self._generate_flan_t5(prompt, max_tokens)
        elif self.hf_model == "mistralai/Mistral-7B-Instruct-v0.3":
            return self._generate_mistral(prompt, max_tokens)
        else:
            self.audit_logger.log_error("LLM Provider Error", f"Unknown provider: {self.provider}")
            return {
                "error": "Unknown LLM provider",
                "response": "LLM service is not properly configured."
            }
        
    def _generate_flan_t5(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Generate using local FLAN-T5-base (NO API CALLS)"""
        try:
            if self._local_pipeline is None:
                self.audit_logger.log_info(
                    f"Loading local model: {self.hf_model}"
                )
                self._local_pipeline = pipeline(
                    task="text2text-generation",
                    model=self.hf_model,
                    max_new_tokens=max_tokens
                )

            result = self._local_pipeline(prompt)
            generated_text = result[0]["generated_text"]

            self.audit_logger.log_info(
                f"FLAN-T5 response generated: {len(generated_text)} chars"
            )

            return {
                "response": generated_text.strip(),
                "model": self.hf_model,
                "provider": "huggingface"
            }

        except Exception as e:
            self.audit_logger.log_error("FLAN-T5 Exception", str(e))
            return {
                "error": str(e),
                "response": "Sorry, I encountered an error while generating a response."
            }
    
    def _generate_mistral(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Generate using Hugging Face Mistral API"""
        if not self.hf_token:
            self.audit_logger.log_error(
                "Mistral Error", "HF API token not configured"
            )
            return {
                "error": "HF API token not configured",
                "response": "Please configure HF_API_TOKEN environment variable."
            }

        api_url = f"https://api-inference.huggingface.co/models/{self.hf_model}"
        headers = {"Authorization": f"Bearer {self.hf_token}"}

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": 0.3,
                "top_p": 0.9,
                "do_sample": False,
                "return_full_text": False
            }
        }

        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()

                if isinstance(result, list) and result:
                    generated_text = result[0].get("generated_text", "")
                else:
                    generated_text = ""

                self.audit_logger.log_info(
                    f"Mistral response generated: {len(generated_text)} chars"
                )

                return {
                    "response": generated_text.strip(),
                    "model": self.hf_model,
                    "provider": self.provider
                }

            elif response.status_code == 503:
                self.audit_logger.log_warning("Mistral model loading")
                return {
                    "error": "Model is loading",
                    "response": "The model is currently loading. Please try again."
                }

            else:
                error_msg = f"API error: {response.status_code}"
                self.audit_logger.log_error("Mistral API Error", error_msg)
                return {
                    "error": error_msg,
                    "response": "Sorry, I'm having trouble generating a response."
                }

        except requests.exceptions.Timeout:
            self.audit_logger.log_error("Mistral Timeout", "Request timed out")
            return {
                "error": "Request timeout",
                "response": "The request took too long. Please try again."
            }

        except Exception as e:
            self.audit_logger.log_error("Mistral Exception", str(e))
            return {
                "error": str(e),
                "response": "Sorry, I encountered an error with Mistral API."
            }