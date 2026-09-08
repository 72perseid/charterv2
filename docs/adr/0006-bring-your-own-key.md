# ADR 0006: Bring-your-own-key model access over one HTTP call

Date: 2026-09-08. Status: accepted.

Each user stores an OpenAI-compatible base URL, model name, and API key. The server makes one `POST {base_url}/chat/completions` with httpx. This removes Chart-er's cost exposure, lets a user point at OpenAI, OpenRouter, Anthropic's compatibility endpoint, a local Ollama or vLLM, or a Turkish provider later with no code change, and is the seam for the planned in-country hosting project.

Rejected: vendor SDKs; one HTTP call does not need one. Found during build: endpoints disagree on optional parameters (OpenAI's newer models want `max_completion_tokens` and refuse temperature), so the call reads a 400 that names a parameter, renames or drops it, retries at most three times, and records the adjustments on the revision.
