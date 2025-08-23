# brain/cognitive_pipeline/utils/llm_utils.py

import os
import json
import requests
from typing import Optional

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
