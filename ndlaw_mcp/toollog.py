"""Per-call tool log for the MCP server — one JSON line per `tools/call`.

Apache sees one capability URL and one opaque POST body per call, so the
access log can say how many requests arrived and from where, but not which
tool ran, how long it took, or how many conversations they belonged to. The
server sees all three. This middleware appends one line per tool call to the
file named by `NDLAW_TOOLLOG` (nothing is installed when it is unset):

    {"ts": "2026-09-16T14:06:29Z", "tool": "lookup_opinion", "ok": true,
     "ms": 12, "bytes": 4531, "session": "9f1c…", "ip": "160.79.106.160",
     "ua": "Claude-User"}

What is deliberately NOT logged: the tool's arguments and its result. A query
may name a case, a party, or a draft's text; the log answers "how much, how
fast, from which client" and nothing about content. `bytes` is the size of
the text returned, not the text.

`ip` is the first `X-Forwarded-For` hop when a reverse proxy set one (Apache's
mod_proxy does), else the peer address; `session` is the MCP session id, which
is one per client connection and so a fair proxy for "one conversation"; `ua`
is the client's User-Agent, which tells claude.ai's relay (`Claude-User`) from
Claude Code (`claude-code/…`) and other clients.

A logging failure never fails the call: every write is wrapped, and an
unwritable path is reported once on stderr and then ignored.

Read by `deploy/anti-scrape/daily-traffic-report.py` (§ 8, tool-call trend).
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext

ENV_VAR = "NDLAW_TOOLLOG"


class ToolCallLog(Middleware):
    """Append one JSON line per tool call to `path`."""

    def __init__(self, path: str | os.PathLike[str]):
        self.path = Path(path)
        self._warned = False

    # ---- what we can learn about the caller, defensively ----
    @staticmethod
    def _client(context: MiddlewareContext) -> tuple[str | None, str | None, str | None]:
        """(session id, client ip, user agent) — each None when unavailable (stdio, tests)."""
        session = ip = ua = None
        ctx = context.fastmcp_context
        if ctx is not None:
            try:
                session = ctx.session_id
            except Exception:  # noqa: BLE001 — no session outside a live connection
                session = None
        try:
            from fastmcp.server.dependencies import get_http_request
            req = get_http_request()
            xff = req.headers.get("x-forwarded-for")
            ip = xff.split(",")[0].strip() if xff else (req.client.host if req.client else None)
            ua = req.headers.get("user-agent")
        except Exception:  # noqa: BLE001 — not an HTTP transport
            pass
        return session, ip, ua

    @staticmethod
    def _size(result) -> int:
        try:
            return sum(len(getattr(c, "text", "") or "") for c in (result.content or []))
        except Exception:  # noqa: BLE001
            return 0

    def _write(self, rec: dict) -> None:
        try:
            with open(self.path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, separators=(",", ":")) + "\n")
        except OSError as exc:
            if not self._warned:
                self._warned = True
                print(f"[toollog] cannot write {self.path}: {exc}; tool-call logging disabled",
                      file=sys.stderr)

    async def on_call_tool(self, context: MiddlewareContext, call_next: CallNext):
        name = getattr(context.message, "name", None) or "?"
        session, ip, ua = self._client(context)
        t0 = time.perf_counter()
        rec = {"ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "tool": name}
        try:
            result = await call_next(context)
        except Exception as exc:
            rec.update(ok=False, error=type(exc).__name__, ms=round((time.perf_counter() - t0) * 1000),
                       bytes=0, session=session, ip=ip, ua=ua)
            self._write(rec)
            raise
        rec.update(ok=not getattr(result, "is_error", False), ms=round((time.perf_counter() - t0) * 1000),
                   bytes=self._size(result), session=session, ip=ip, ua=ua)
        self._write(rec)
        return result


def install_tool_log(mcp, path: str | os.PathLike[str] | None = None) -> ToolCallLog | None:
    """Attach the middleware when `path` (or $NDLAW_TOOLLOG) names a file; else no-op."""
    target = path or os.environ.get(ENV_VAR)
    if not target:
        return None
    mw = ToolCallLog(target)
    mcp.add_middleware(mw)
    return mw
