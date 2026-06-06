"""Ollama integration: health check + strict-JSON generation with retry & repair."""
from __future__ import annotations

import json
import re
from typing import Any, Optional

import httpx

from .. import config


class OllamaUnavailable(RuntimeError):
    """Raised when the local Ollama server cannot be reached."""


def is_running() -> bool:
    try:
        r = httpx.get(f"{config.OLLAMA_HOST}/api/tags", timeout=3.0)
        return r.status_code == 200
    except httpx.HTTPError:
        return False


def installed_models() -> list[str]:
    try:
        r = httpx.get(f"{config.OLLAMA_HOST}/api/tags", timeout=3.0)
        r.raise_for_status()
        return [m.get("name", "") for m in r.json().get("models", [])]
    except httpx.HTTPError:
        return []


def _extract_json(text: str) -> Optional[dict[str, Any]]:
    """Defensive JSON parse: strip fences, grab the outermost object."""
    if not text:
        return None
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = text[start : end + 1]
        try:
            return json.loads(snippet)
        except json.JSONDecodeError:
            # Last resort: remove trailing commas.
            snippet = re.sub(r",\s*([}\]])", r"\1", snippet)
            try:
                return json.loads(snippet)
            except json.JSONDecodeError:
                return None
    return None


def generate_json(
    prompt: str,
    system: str = "",
    model: Optional[str] = None,
    temperature: float = 0.7,
    retries: int = 1,
) -> dict[str, Any]:
    """Call Ollama and return a parsed JSON object. Retries once on parse failure.

    Raises OllamaUnavailable if the server is unreachable.
    """
    model = model or config.MODEL
    body = {
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "format": "json",
        "options": {"temperature": temperature},
    }
    last_text = ""
    attempt = 0
    while attempt <= retries:
        attempt += 1
        try:
            r = httpx.post(
                f"{config.OLLAMA_HOST}/api/generate",
                json=body,
                timeout=config.OLLAMA_TIMEOUT,
            )
        except httpx.ConnectError as exc:
            raise OllamaUnavailable(str(exc)) from exc
        except httpx.HTTPError as exc:
            if attempt > retries:
                raise OllamaUnavailable(str(exc)) from exc
            continue
        if r.status_code != 200:
            if attempt > retries:
                raise OllamaUnavailable(f"Ollama returned {r.status_code}")
            continue
        last_text = r.json().get("response", "")
        parsed = _extract_json(last_text)
        if parsed is not None:
            return parsed
        # Nudge the model to return valid JSON on the retry.
        body["prompt"] = prompt + "\n\nReturn ONLY a single valid JSON object. No prose."
        body["options"]["temperature"] = 0.3
    raise ValueError(f"Could not parse JSON from model output: {last_text[:200]}")
