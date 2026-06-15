from __future__ import annotations

import os
from typing import Any

_LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

try:
    from langfuse import Langfuse, observe

    _client = Langfuse(host=_LANGFUSE_HOST)

    def get_client() -> Langfuse:
        return _client

    def flush() -> None:
        _client.flush()

except Exception:  # pragma: no cover

    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

    def get_client() -> None:  # type: ignore[return]
        return None

    def flush() -> None:
        pass


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
