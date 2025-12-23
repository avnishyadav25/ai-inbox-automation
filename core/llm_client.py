from typing import Optional, Dict, Any
from anthropic import Anthropic
from openai import OpenAI
from core.config import settings


class LLMClient:
    """Unified client for LLM providers (Anthropic/OpenAI)"""

    def __init__(self):
        self.provider = settings.ai_provider

        if self.provider == "anthropic":
            self.client = Anthropic(api_key=settings.anthropic_api_key)
            self.model = "claude-sonnet-4-20250514"
        elif self.provider == "openai":
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model = "gpt-4-turbo-preview"
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """Generate text completion from LLM"""

        if self.provider == "anthropic":
            messages = [{"role": "user", "content": prompt}]

            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt if system_prompt else "",
                messages=messages,
            )
            return response.content[0].text

        elif self.provider == "openai":
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """Generate structured JSON output"""
        import json

        json_instruction = "\n\nRespond ONLY with valid JSON. No other text."

        if self.provider == "anthropic":
            messages = [{"role": "user", "content": prompt + json_instruction}]

            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.3,
                system=system_prompt if system_prompt else "",
                messages=messages,
            )
            return json.loads(response.content[0].text)

        elif self.provider == "openai":
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt + json_instruction})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.3,
                response_format={"type": "json_object"},
            )
            return json.loads(response.choices[0].message.content)


# Global LLM client instance
llm_client = LLMClient()
