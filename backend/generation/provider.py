"""
One HTTP call to an OpenAI-compatible chat completions endpoint (SPEC §2,
model access). No vendor SDK; the seam for pointing at any provider,
including the planned in-country host, is the base URL.
"""

from __future__ import annotations

import ipaddress
import socket
import time
from dataclasses import dataclass, field
from urllib.parse import urlparse

import httpx
from django.conf import settings


class ProviderError(Exception):
    """A message the user can act on. Shown verbatim."""


@dataclass
class ProviderResult:
    text: str
    model: str
    usage: dict | None
    duration_ms: int
    raw: dict = field(repr=False)


def normalise_base_url(base_url: str) -> str:
    url = base_url.strip().rstrip("/")
    parts = urlparse(url)
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        raise ProviderError("Base URL must start with http:// or https:// and name a host.")
    if parts.scheme == "http" and not settings.ALLOW_PRIVATE_ENDPOINTS:
        raise ProviderError(
            "Base URL must use https:// (plain http is allowed only for local endpoints)."
        )
    return url


def check_endpoint_allowed(base_url: str) -> None:
    """Refuse loopback, private, and link-local hosts unless the operator opted in."""
    if settings.ALLOW_PRIVATE_ENDPOINTS:
        return
    host = urlparse(base_url).hostname or ""
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise ProviderError(f"Could not resolve host '{host}'.") from exc
    for info in infos:
        address = ipaddress.ip_address(info[4][0])
        if not address.is_global:
            raise ProviderError(
                f"Host '{host}' resolves to a private or local address, "
                "which this server does not call."
            )


def chat_completion(
    *,
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict],
    temperature: float = 0.0,
    max_tokens: int | None = None,
    json_object: bool = False,
    seed: int | None = None,
    timeout: float | None = None,
) -> ProviderResult:
    base_url = normalise_base_url(base_url)
    check_endpoint_allowed(base_url)

    body: dict = {"model": model, "messages": messages, "temperature": temperature}
    if max_tokens is not None:
        body["max_tokens"] = max_tokens
    if json_object:
        body["response_format"] = {"type": "json_object"}
    if seed is not None:
        body["seed"] = seed

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    started = time.monotonic()
    try:
        response = httpx.post(
            f"{base_url}/chat/completions",
            json=body,
            headers=headers,
            timeout=timeout or settings.PROVIDER_TIMEOUT_SECONDS,
        )
    except httpx.TimeoutException as exc:
        raise ProviderError("The endpoint did not answer in time.") from exc
    except httpx.HTTPError as exc:
        raise ProviderError(
            f"Could not connect to the endpoint: {exc.__class__.__name__}."
        ) from exc
    duration_ms = int((time.monotonic() - started) * 1000)

    if response.status_code == 401 or response.status_code == 403:
        raise ProviderError(f"Endpoint returned {response.status_code}: check your API key.")
    if response.status_code == 404:
        raise ProviderError("Endpoint returned 404: check the base URL and the model name.")
    if response.status_code == 429:
        raise ProviderError("Endpoint returned 429: rate limited or out of credit.")
    if response.status_code >= 400:
        detail = _error_detail(response)
        raise ProviderError(f"Endpoint returned {response.status_code}: {detail}")

    try:
        data = response.json()
        text = data["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise ProviderError("Endpoint answered, but not in the chat completions format.") from exc
    if not isinstance(text, str):
        raise ProviderError("Endpoint returned a non-text message.")

    return ProviderResult(
        text=text,
        model=str(data.get("model") or model),
        usage=data.get("usage") if isinstance(data.get("usage"), dict) else None,
        duration_ms=duration_ms,
        raw=data,
    )


def _error_detail(response: httpx.Response) -> str:
    try:
        data = response.json()
        error = data.get("error", data)
        if isinstance(error, dict):
            return str(error.get("message") or error)[:200]
        return str(error)[:200]
    except ValueError:
        return response.text[:200] or "no details"
