"""
VERA - LLM wrappers for data augmentation
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import re


PARAPHRASE_PROMPT = """Generate {n} different paraphrases of the following question.
Each paraphrase should:
- Maintain the same meaning and intent
- Use different words and sentence structure
- Be natural and grammatically correct

Question: {question}

Return ONLY the paraphrases, one per line, numbered 1 to {n}."""


class BaseLLM(ABC):
    """Base class for LLM models"""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text from a prompt.

        Args:
            prompt: Input prompt

        Returns:
            Generated text
        """
        pass

    def paraphrase(self, text: str, n: int = 5) -> List[str]:
        """
        Generate n paraphrases of the input text.

        Args:
            text: Text to paraphrase
            n: Number of paraphrases to generate

        Returns:
            List of paraphrases
        """
        prompt = PARAPHRASE_PROMPT.format(question=text, n=n)
        response = self.generate(prompt)

        # Parse numbered list
        paraphrases = []
        lines = response.strip().split('\n')
        for line in lines:
            # Remove numbering (1., 2., etc.)
            cleaned = re.sub(r'^\d+[\.\)]\s*', '', line.strip())
            if cleaned:
                paraphrases.append(cleaned)

        # Ensure we have exactly n paraphrases
        if len(paraphrases) < n:
            # Pad with original if not enough
            paraphrases.extend([text] * (n - len(paraphrases)))
        elif len(paraphrases) > n:
            paraphrases = paraphrases[:n]

        return paraphrases


class OpenAILLM(BaseLLM):
    """OpenAI LLM wrapper"""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        Initialize OpenAI LLM.

        Args:
            api_key: OpenAI API key
            model: Model name
            base_url: Optional custom base URL
            temperature: Sampling temperature
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Please install openai: pip install openai")

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.temperature = temperature

    def generate(self, prompt: str, **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", self.temperature)
        )
        return response.choices[0].message.content


class HuggingFaceLLM(BaseLLM):
    """HuggingFace LLM wrapper"""

    def __init__(
        self,
        model: str,
        device: str = "cuda",
        max_new_tokens: int = 512,
        temperature: float = 0.7
    ):
        """
        Initialize HuggingFace LLM.

        Args:
            model: Model name or path
            device: Device to use
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        """
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
        except ImportError:
            raise ImportError("Please install transformers: pip install transformers torch")

        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.model = AutoModelForCausalLM.from_pretrained(
            model,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map=device
        )
        self.device = device
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature

    def generate(self, prompt: str, **kwargs) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=kwargs.get("max_new_tokens", self.max_new_tokens),
            temperature=kwargs.get("temperature", self.temperature),
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )

        # Decode only new tokens
        response = self.tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True
        )
        return response


class CustomLLM(BaseLLM):
    """Custom API LLM wrapper"""

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        prompt_key: str = "prompt",
        response_key: str = "response"
    ):
        """
        Initialize custom LLM.

        Args:
            base_url: API endpoint URL
            api_key: Optional API key
            headers: Optional additional headers
            prompt_key: Key in request JSON for prompt
            response_key: Key in response JSON containing generated text
        """
        self.base_url = base_url
        self.prompt_key = prompt_key
        self.response_key = response_key

        self.headers = headers or {}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        self.headers.setdefault("Content-Type", "application/json")

    def generate(self, prompt: str, **kwargs) -> str:
        import requests

        payload = {self.prompt_key: prompt}
        payload.update(kwargs)

        response = requests.post(
            self.base_url,
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()

        data = response.json()

        # Handle different response formats
        if self.response_key in data:
            return data[self.response_key]
        elif "choices" in data:
            # OpenAI-compatible format
            return data["choices"][0]["message"]["content"]

        raise ValueError(f"Could not find response in API output: {data.keys()}")


# Factory functions
def openai(
    api_key: str,
    model: str = "gpt-4o-mini",
    base_url: Optional[str] = None,
    **kwargs
) -> OpenAILLM:
    """Create an OpenAI LLM"""
    return OpenAILLM(api_key=api_key, model=model, base_url=base_url, **kwargs)


def huggingface(
    model: str,
    device: str = "cuda",
    **kwargs
) -> HuggingFaceLLM:
    """Create a HuggingFace LLM"""
    return HuggingFaceLLM(model=model, device=device, **kwargs)


def custom(
    base_url: str,
    api_key: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> CustomLLM:
    """Create a custom API LLM"""
    return CustomLLM(base_url=base_url, api_key=api_key, headers=headers, **kwargs)
