import requests
from typing import Dict, Any
from services.audit_logger import AuditLogger
from config import Config

class LLMService:
    """Service for generating responses using LLM providers"""
    
    def __init__(self, audit_logger: AuditLogger = None):
        self.provider = Config.LLM_PROVIDER
        self.api_url = Config.OLLAMA_API_URL
        self.ollama_model = Config.OLLAMA_MODEL
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
        if self.provider == "ollama":
            return self._generate_mistral_ollama(prompt, max_tokens)
        else:
            self.audit_logger.log_error("LLM Provider Error", f"Unknown provider: {self.provider}")
            return {
                "error": "Unknown LLM provider",
                "response": "LLM service is not properly configured."
            }
    def _generate_mistral_ollama(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """
        Generate response using self-hosted Mistral via Ollama.
        Requires: ollama running locally.
        """

        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": min(max_tokens, 256),
                        "temperature": 0.3
                    }
                },
                timeout=120
            )

            if response.status_code != 200:
                self.audit_logger.log_error(
                    "Ollama API Error",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return {
                    "error": f"Ollama HTTP {response.status_code}",
                    "response": "Local Mistral service returned an error."
                }

            data = response.json()
            generated_text = data.get("response", "")

            self.audit_logger.log_info(
                f"Mistral (Ollama) response generated ({len(generated_text)} chars)"
            )

            return {
                "response": generated_text.strip(),
                "model": "mistral (ollama)",
                "provider": "ollama"
            }

        except requests.exceptions.ConnectionError:
            self.audit_logger.log_error(
                "Ollama Connection Error",
                "Ollama server not reachable"
            )
            return {
                "error": "Ollama not running",
                "response": "Local Mistral server is not running."
            }

        except requests.exceptions.Timeout:
            self.audit_logger.log_error(
                "Ollama Timeout",
                "Request timed out"
            )
            return {
                "error": "Request timeout",
                "response": "Local Mistral generation timed out."
            }

        except Exception as e:
            self.audit_logger.log_error("Ollama Exception", str(e))
            return {
                "error": str(e),
                "response": "Local Mistral generation failed."
            }