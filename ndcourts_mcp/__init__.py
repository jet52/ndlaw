"""Deprecated alias for :mod:`ndlaw_mcp` (package renamed in v3.0.0).

The corpus outgrew its court-opinions origin — the package now serves all
North Dakota primary law — so ``ndcourts_mcp`` became ``ndlaw_mcp``. This
shim keeps ``from ndcourts_mcp import server``-style imports working for
one transition period; it will be removed in a later release.
"""

import importlib
import sys
import warnings

warnings.warn(
    "ndcourts_mcp was renamed to ndlaw_mcp in v3.0.0; update your imports. "
    "This compatibility alias will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from ndlaw_mcp import *  # noqa: F401,F403


def __getattr__(name):
    """Lazily alias ndcourts_mcp.<mod> to ndlaw_mcp.<mod> (PEP 562)."""
    module = importlib.import_module(f"ndlaw_mcp.{name}")
    sys.modules[f"{__name__}.{name}"] = module
    return module
