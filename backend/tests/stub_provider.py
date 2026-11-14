"""
A tiny OpenAI-compatible server for tests (SPEC §10). Behaviour is chosen by
the API key so one server covers the happy path and the failure paths:

  good-key      -> 200 with the canned reply (a Vega-Lite spec from build step 4 on)
  bad-key       -> 401
  slow-key      -> sleeps past the caller's timeout
  garbage-key   -> 200 with a non-JSON body
  text-key      -> 200 whose message content is plain prose, not JSON
  strict-key    -> 400 on max_tokens (wants max_completion_tokens) and on temperature != 1,
                   like OpenAI's reasoning models; 200 once both are fixed

GET /v1/models returns three canned ids (401 for bad-key).
"""

from __future__ import annotations

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CANNED_SPEC = {
    "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
    "mark": "bar",
    "encoding": {
        "x": {"field": "Alan", "type": "nominal"},
        "y": {"field": "Sayı", "type": "quantitative", "aggregate": "sum"},
    },
    "data": {"name": "main"},
}


# What the stub says when asked about period labels (generation/periods.py): one
# name PeriodO knows, one it does not (years only), one refusal, one label nobody asked about.
PERIOD_ANSWERS = {
    "Erken Hristiyanlık": {"name": "Early Christian", "start": 100, "end": 600},
    "Evre 7": {"name": "Kinet Phase 7", "start": -700, "end": -650},
    "Açma B": {"name": None, "start": None, "end": None},
    "Roma": {"name": "Neolithic", "start": -9000, "end": -6000},
}


class Handler(BaseHTTPRequestHandler):
    server: StubServer

    def log_message(self, *args):  # keep test output quiet
        pass

    def do_GET(self):
        key = self.headers.get("Authorization", "").removeprefix("Bearer ").strip()
        if self.path != "/v1/models":
            return self._send(404, {"error": {"message": "not found"}})
        if key == "bad-key":
            return self._send(401, {"error": {"message": "invalid api key"}})
        return self._send(
            200,
            {
                "object": "list",
                "data": [
                    {
                        "id": "stub-large",
                        "object": "model",
                        "pricing": {"prompt": "0.000001", "completion": "0.000002"},
                    },
                    {"id": "stub-small", "object": "model"},
                    {"id": "Stub-Embed", "object": "model"},
                ],
            },
        )

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        self.server.requests.append(
            {"path": self.path, "headers": dict(self.headers), "body": body}
        )
        key = self.headers.get("Authorization", "").removeprefix("Bearer ").strip()

        if self.path != "/v1/chat/completions":
            return self._send(404, {"error": {"message": "not found"}})
        if key == "bad-key":
            return self._send(401, {"error": {"message": "invalid api key"}})
        if key == "slow-key":
            time.sleep(3)
        if key == "strict-key":
            if "max_tokens" in body:
                return self._send(
                    400,
                    {
                        "error": {
                            "message": "Unsupported parameter: 'max_tokens' is not supported "
                            "with this model. Use 'max_completion_tokens' instead.",
                            "type": "invalid_request_error",
                            "param": "max_tokens",
                        }
                    },
                )
            if body.get("temperature", 1) != 1:
                return self._send(
                    400,
                    {
                        "error": {
                            "message": "Unsupported value: 'temperature' does not support 0.0 "
                            "with this model. Only the default (1) value is supported.",
                            "type": "invalid_request_error",
                            "param": "temperature",
                        }
                    },
                )
        if key == "garbage-key":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", "17")
            self.end_headers()
            self.wfile.write(b"<html>oops</html>")
            return None
        content = "Sure, here is prose." if key == "text-key" else json.dumps(CANNED_SPEC)
        asked_about_periods = "order archaeological period labels" in json.dumps(
            body.get("messages", [])
        )
        if asked_about_periods and key != "text-key":
            content = json.dumps(PERIOD_ANSWERS, ensure_ascii=False)
        if "single word: ok" in json.dumps(body.get("messages", [])):
            content = "ok"  # the connection test
        return self._send(
            200,
            {
                "id": "stub-1",
                "model": body.get("model", "stub-model"),
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": content},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 12,
                    "completion_tokens": 7,
                    "total_tokens": 19,
                    "completion_tokens_details": {"reasoning_tokens": 3},
                },
            },
        )

    def _send(self, status: int, payload: dict):
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class StubServer(ThreadingHTTPServer):
    def __init__(self):
        super().__init__(("127.0.0.1", 0), Handler)
        self.requests: list[dict] = []

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.server_port}/v1"


def start() -> StubServer:
    server = StubServer()
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server
