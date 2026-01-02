"""Async/sync compatibility utilities."""

from __future__ import annotations

import asyncio
import concurrent.futures
from typing import Any, Coroutine, TypeVar

T = TypeVar("T")


def run_sync(coro: Coroutine[Any, Any, T]) -> T:
    """Run async coroutine synchronously with Jupyter/IPython compatibility.

    This function detects whether it's running inside an async context
    (like Jupyter/IPython) and handles it appropriately.

    Args:
        coro: Async coroutine to run.

    Returns:
        Result of the coroutine.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is not None:
        # We're in an async context (Jupyter/IPython)
        # Try nest_asyncio first for best compatibility
        try:
            import nest_asyncio

            nest_asyncio.apply()
            return asyncio.run(coro)
        except ImportError:
            # nest_asyncio not available, use thread executor as fallback
            def _run_in_new_loop() -> T:
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(coro)
                finally:
                    new_loop.close()

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(_run_in_new_loop)
                return future.result()
    else:
        # No event loop running (regular Python script)
        return asyncio.run(coro)
