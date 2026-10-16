"""Server-wide cap on in-flight work (public deployment).

The per-IP fail2ban jails throttle individual clients, but they cannot
protect capacity: an AI provider's egress address carries many users at
once (and those ranges are exempted from the jails), and the droplet fails
on TOTAL load, wherever it comes from. Apache cannot enforce a global cap
under the prefork MPM (``ProxyPass max=`` is per child process), so the
cap lives here.

``NDLAW_MAX_INFLIGHT=N`` enables it (unset or 0 = no cap, so stdio and
local HTTP use are unchanged). Sized 2026-10-15 by a one-core load test:
throughput flattens at 4-8 concurrent tool calls and RSS grows ~20 MB per
in-flight call, crossing the unit's MemoryHigh=300M near 16.

What counts: MCP ``tools/call`` requests and web-interface pages. What
does not: the MCP handshake and bookkeeping (``initialize``,
``tools/list``, notifications, session DELETE, the GET event stream) —
they are cheap, and refusing ``initialize`` makes a client report the
whole connector as unreachable.

A counted request that finds every slot busy waits up to
``NDLAW_INFLIGHT_WAIT`` seconds (default 2), absorbing short bursts. If
it still has no slot:
- a tool call gets a normal JSON-RPC tool result with ``isError`` and a
  "retry in a few seconds" message, which an LLM client reads and acts on
  (an HTTP error mid-session tends to surface as a broken connector);
- a web page gets 503 + ``Retry-After``.
Neither status is matched by a fail2ban filter, so shedding load never
turns into a ban.
"""

from __future__ import annotations

import asyncio
import json
import os

_RETRY_AFTER = "2"
_BUSY_TEXT = (
    "ndlaw.org is at capacity right now. Wait a few seconds and retry "
    "this tool call."
)


class InflightLimit:
    """Pure ASGI middleware: at most ``limit`` counted requests at once."""

    def __init__(self, app, limit: int, wait: float = 2.0):
        self.app = app
        self.limit = limit
        self.wait = wait
        self._sem = asyncio.Semaphore(limit)
        self.shed = 0  # requests refused since start (inspected by tests)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        path = scope.get("path", "")
        is_mcp = path == "/mcp" or path.startswith("/mcp/")
        msg = None
        if is_mcp:
            if scope.get("method") != "POST":
                await self.app(scope, receive, send)
                return
            body = await _read_body(receive)
            receive = _replay(body, receive)
            msg = _parse(body)
            if not (isinstance(msg, dict) and msg.get("method") == "tools/call"):
                await self.app(scope, receive, send)
                return
        try:
            await asyncio.wait_for(self._sem.acquire(), timeout=self.wait)
        except asyncio.TimeoutError:
            self.shed += 1
            if msg is not None:
                await _send_busy_result(send, msg.get("id"))
            else:
                await _send_503(send)
            return
        try:
            await self.app(scope, receive, send)
        finally:
            self._sem.release()


async def _read_body(receive) -> bytes:
    chunks = []
    while True:
        message = await receive()
        if message["type"] != "http.request":
            break
        chunks.append(message.get("body", b""))
        if not message.get("more_body"):
            break
    return b"".join(chunks)


def _replay(body: bytes, receive):
    """Hand the consumed body back once, then defer to the real channel
    (so the app still sees ``http.disconnect`` when the client leaves)."""
    sent = False

    async def replay():
        nonlocal sent
        if not sent:
            sent = True
            return {"type": "http.request", "body": body, "more_body": False}
        return await receive()

    return replay


def _parse(body: bytes):
    try:
        return json.loads(body)
    except ValueError:
        return None  # batch arrays / junk fall through uncounted to the app


async def _send_json(send, status: int, payload: dict, extra=()) -> None:
    body = json.dumps(payload).encode()
    await send({
        "type": "http.response.start",
        "status": status,
        "headers": [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(body)).encode()),
            *extra,
        ],
    })
    await send({"type": "http.response.body", "body": body})


async def _send_busy_result(send, req_id) -> None:
    await _send_json(send, 200, {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "content": [{"type": "text", "text": _BUSY_TEXT}],
            "isError": True,
        },
    })


async def _send_503(send) -> None:
    await _send_json(
        send, 503,
        {"error": "ndlaw.org is at capacity; retry in a few seconds."},
        extra=[(b"retry-after", _RETRY_AFTER.encode())],
    )


def middleware_from_env() -> list:
    """Starlette ``Middleware`` list for ``mcp.run(middleware=...)``."""
    raw = os.environ.get("NDLAW_MAX_INFLIGHT", "").strip()
    limit = int(raw) if raw else 0
    if limit <= 0:
        return []
    wait = float(os.environ.get("NDLAW_INFLIGHT_WAIT", "2"))
    from starlette.middleware import Middleware

    return [Middleware(InflightLimit, limit=limit, wait=wait)]
