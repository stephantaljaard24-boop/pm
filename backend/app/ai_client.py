import json
import os
from typing import Any

import httpx

OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "openai/gpt-oss-120b"


class OpenRouterConfigError(Exception):
    pass


class OpenRouterRequestError(Exception):
    pass


def get_openrouter_api_key() -> str:
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise OpenRouterConfigError("OPENROUTER_API_KEY is not configured")
    return api_key


def get_openrouter_chat_completion(
    messages: list[dict[str, str]],
    response_format: dict[str, Any] | None = None,
) -> str:
    payload: dict[str, Any] = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
    }
    if response_format is not None:
        payload["response_format"] = response_format

    headers = {
        "Authorization": f"Bearer {get_openrouter_api_key()}",
        "Content-Type": "application/json",
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(OPENROUTER_CHAT_URL, headers=headers, json=payload)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise OpenRouterRequestError("OpenRouter request failed") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise OpenRouterRequestError("OpenRouter returned an unexpected response") from exc

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise OpenRouterRequestError("OpenRouter returned an unexpected response") from exc

    if not isinstance(content, str):
        raise OpenRouterRequestError("OpenRouter returned an unexpected response")

    return content


def ask_openrouter(prompt: str) -> str:
    return get_openrouter_chat_completion([{"role": "user", "content": prompt}])


def ask_openrouter_json(
    messages: list[dict[str, str]],
    response_schema: dict[str, Any],
) -> dict[str, Any]:
    content = get_openrouter_chat_completion(
        messages,
        {
            "type": "json_schema",
            "json_schema": {
                "name": "kanban_ai_response",
                "strict": True,
                "schema": response_schema,
            },
        },
    )

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise OpenRouterRequestError("OpenRouter returned invalid JSON") from exc

    if not isinstance(data, dict):
        raise OpenRouterRequestError("OpenRouter returned an unexpected response")

    return data
