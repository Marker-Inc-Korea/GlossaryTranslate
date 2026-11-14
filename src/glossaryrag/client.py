from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol


class ChatClient(Protocol):
    model: str

    def complete(self, messages: Sequence[Mapping[str, str]]) -> str: ...


@dataclass(slots=True)
class OpenAICompatibleClient:
    """Minimal client for local vLLM/TGI/OpenAI-compatible chat endpoints."""

    base_url: str
    model: str
    api_key: str = ""
    temperature: float = 0.0
    max_tokens: int = 1_024
    timeout_seconds: float = 300.0
    extra_body: Mapping[str, Any] = field(default_factory=dict)

    @property
    def endpoint(self) -> str:
        base = self.base_url.rstrip("/")
        if base.endswith("/v1"):
            return base + "/chat/completions"
        return base + "/v1/chat/completions"

    def complete(self, messages: Sequence[Mapping[str, str]]) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": list(messages),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **dict(self.extra_body),
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"model endpoint returned HTTP {exc.code}: {detail}") from exc
        choices = body.get("choices") or []
        if not choices:
            raise RuntimeError(f"model endpoint returned no choices: {body}")
        content = choices[0].get("message", {}).get("content")
        if not isinstance(content, str):
            raise RuntimeError(f"model endpoint returned invalid content: {body}")
        return content.strip()


@dataclass(slots=True)
class StaticClient:
    """Deterministic client used by examples and tests."""

    response: str
    model: str = "static-test-client"

    def complete(self, messages: Sequence[Mapping[str, str]]) -> str:
        del messages
        return self.response
