import requests
import os
from typing import Dict, Any
from services.audit_logger import AuditLogger
from config import Config

class LLMService:
    """Service for generating responses using LLM providers"""
    
    def __init__(self, audit_logger: AuditLogger = None):
        self.provider = Config.LLM_PROVIDER
        self.hf_token = Config.HF_API_TOKEN
        self.hf_model = Config.HF_MODEL
        self.openai_api_key = Config.OPENAI_API_KEY
        self.audit_logger = audit_logger or AuditLogger()
        
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
        if self.provider == "huggingface":
            return self._generate_huggingface(prompt, max_tokens)
        elif self.provider == "openai":
            return self._generate_openai(prompt, max_tokens)
        else:
            self.audit_logger.log_error("LLM Provider Error", f"Unknown provider: {self.provider}")
            return {
                "error": "Unknown LLM provider",
                "response": "LLM service is not properly configured."
            }
    
    def _generate_huggingface(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Generate using HuggingFace Inference API"""
        if not self.hf_token:
            self.audit_logger.log_error("HuggingFace Error", "API token not configured")
            return {
                "error": "HuggingFace API token not configured",
                "response": "Please configure HF_API_TOKEN environment variable."
            }
        
        api_url = f"https://api-inference.huggingface.co/models/{self.hf_model}"
        
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": 0.7,
                "top_p": 0.95,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                else:
                    generated_text = result.get("generated_text", "")
                
                self.audit_logger.log_info(f"LLM response generated: {len(generated_text)} chars")
                
                return {
                    "response": generated_text.strip(),
                    "model": self.hf_model,
                    "provider": "huggingface"
                }
            
            elif response.status_code == 503:
                self.audit_logger.log_warning("HuggingFace model loading")
                return {
                    "error": "Model is loading",
                    "response": "The model is currently loading. Please try again in a few moments."
                }
            
            else:
                error_msg = f"API error: {response.status_code}"
                self.audit_logger.log_error("HuggingFace API Error", error_msg)
                return {
                    "error": error_msg,
                    "response": "Sorry, I'm having trouble generating a response right now."
                }
        
        except requests.exceptions.Timeout:
            self.audit_logger.log_error("HuggingFace Timeout", "Request timed out")
            return {
                "error": "Request timeout",
                "response": "The request took too long. Please try again."
            }
        
        except Exception as e:
            self.audit_logger.log_error("HuggingFace Exception", str(e))
            return {
                "error": str(e),
                "response": "Sorry, I encountered an error while generating a response."
            }
    
    def _generate_openai(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Generate using OpenAI API"""
        if not self.openai_api_key:
            self.audit_logger.log_error("OpenAI Error", "API key not configured")
            return {
                "error": "OpenAI API key not configured",
                "response": "Please configure OPENAI_API_KEY environment variable."
            }
        
        try:
            import openai
            
            openai.api_key = self.openai_api_key
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            generated_text = response.choices[0].message.content
            
            self.audit_logger.log_info(f"OpenAI response generated: {len(generated_text)} chars")
            
            return {
                "response": generated_text.strip(),
                "model": "gpt-3.5-turbo",
                "provider": "openai"
            }
        
        except ImportError:
            self.audit_logger.log_error("OpenAI Error", "openai package not installed")
            return {
                "error": "OpenAI package not installed",
                "response": "Please install: pip install openai"
            }
        
        except Exception as e:
            self.audit_logger.log_error("OpenAI Exception", str(e))
            return {
                "error": str(e),
                "response": "Sorry, I encountered an error with OpenAI API."
            }