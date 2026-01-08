import requests
from typing import Dict, Any
from services.audit_logger import AuditLogger
from config import Config
from transformers import pipeline
from huggingface_hub import InferenceClient

class LLMService:
    """Service for generating responses using LLM providers"""
    
    def __init__(self, audit_logger):
        self.provider = Config.LLM_PROVIDER
        self.HF_API_TOKEN = Config.HF_API_TOKEN
        self.api_url = Config.OLLAMA_API_URL
        self.llm_model = Config.LLM_MODEL
        self.audit_logger = audit_logger or AuditLogger()

        self._local_pipeline = None
        self._hf_client = None

        self.audit_logger.log_component_init("LLM Service", self.provider)
    
    def generate_response(self, prompt: str, max_tokens: int = 500) -> Dict[str, Any]:
        """
        Generate response using configured LLM provider
        """
        if self.provider == "huggingface":
            return self._generate_flan_t5(prompt, max_tokens)

        if self.provider == "ollama":
            return self._generate_mistral_ollama(prompt, max_tokens)

        if self.provider == "hf_mistral":
            return self._generate_mistral_hf(prompt, max_tokens)

        self.audit_logger.log_error(
            "LLM Provider Error",
            f"Unknown provider: {self.provider}"
        )
        return {
            "error": "Unknown LLM provider",
            "response": "LLM service is not properly configured."
        }
    
    def _generate_flan_t5(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Generate using local FLAN-T5 (NO API CALLS)"""
        try:
            if self._local_pipeline is None:
                self.audit_logger.log_info(
                    f"Loading local FLAN-T5 model: {self.llm_model}"
                )
                self._local_pipeline = pipeline(
                    task="text2text-generation",
                    model=self.llm_model
                )

            result = self._local_pipeline(
                prompt,
                max_new_tokens=max_tokens,
                do_sample=False,
                temperature=0.3
            )

            generated_text = result[0]["generated_text"]

            self.audit_logger.log_info(
                f"FLAN-T5 response generated ({len(generated_text)} chars)"
            )

            return {
                "response": generated_text.strip(),
                "model": self.llm_model,
                "provider": self.provider
            }

        except Exception as e:
            self.audit_logger.log_error("FLAN-T5 Exception", str(e))
            return {
                "error": str(e),
                "response": "Error generating response using FLAN-T5."
            }

    def _generate_mistral_hf(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Generate using HuggingFace InferenceClient (Mistral chat)"""
        try:
            if self._hf_client is None:
                self.audit_logger.log_info(
                    "Initializing HuggingFace InferenceClient for Mistral"
                )
                self._hf_client = InferenceClient(
                    model=self.llm_model,
                    token=self.HF_API_TOKEN
                )

            response = self._hf_client.chat_completion(
                messages=[
                    {"role": "system", "content": prompt[:433]},
                    {"role": "user", "content": prompt[433:]}
                ],
                max_tokens=min(max_tokens, 512),
                temperature=0.2
            )

            generated_text = response.choices[0].message.content

            self.audit_logger.log_info(
                f"HF Mistral response generated ({len(generated_text)} chars)"
            )

            return {
                "response": generated_text.strip(),
                "model": self.llm_model,
                "provider": self.provider
            }

        except Exception as e:
            self.audit_logger.log_error("HF Mistral Exception", str(e))
            return {
                "error": str(e),
                "response": "Error generating response using HuggingFace Mistral."
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
                    "model": self.llm_model,
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