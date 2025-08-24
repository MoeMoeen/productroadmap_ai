# brain/cognitive_pipeline/utils/llm_utils.py

import os
import requests
from typing import Optional

def llm_fn_anthropic(prompt: str, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229", max_tokens: int = 512) -> str:
    """
    Calls Anthropic Claude API and returns the raw string response.
    Expects the LLM to return a JSON string.
    """
    import requests
    api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data, timeout=60)
    resp.raise_for_status()
    result = resp.json()
    # Anthropic returns content as a list of message parts
    content = result["content"][0].get("text") if result.get("content") else None
    if not content:
        raise ValueError("Anthropic returned empty response")
    return content


def llm_fn_openai(prompt: str, api_key: Optional[str] = None, model: str = "gpt-4", max_tokens: int = 512) -> str:
    """
    Calls OpenAI API (or compatible endpoint) and returns the raw string response.
    Expects the LLM to return a JSON list of entities.
    """
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an expert business analyst."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.0
    }
    resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=60)
    resp.raise_for_status()
    result = resp.json()
    # Extract the assistant's message
    content = result["choices"][0]["message"]["content"]
    return content

def llm_fn_dummy(prompt: str, *args, **kwargs) -> str:
    """
    Returns a fixed, valid JSON list for testing.
    """
    return '[{"entity_type": "BusinessObjective", "value": "Grow revenue", "confidence": 0.95}]'
