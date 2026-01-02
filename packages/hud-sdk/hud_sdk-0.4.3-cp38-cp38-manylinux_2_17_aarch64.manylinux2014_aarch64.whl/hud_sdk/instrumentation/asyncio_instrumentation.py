import contextvars
import sys
from functools import wraps
from typing import Any

from ..config import config
from ..native import copy_shadowstack, get_shadowstack_contextvar
from .base_instrumentation import BaseInstrumentation


class AsyncioInstrumentation(BaseInstrumentation):
    def __init__(self) -> None:
        super().__init__("asyncio.base_events", "asyncio", "0.0.0", None)
        self.supports_context_kw = sys.version_info >= (3, 11)

    def is_enabled(self) -> bool:
        return config.instrument_asyncio

    def is_supported(self) -> bool:
        # We override this because version detection doesn't work on asyncio.
        return True

    def _instrument(self) -> None:
        import asyncio.base_events

        original_create_task = asyncio.base_events.BaseEventLoop.create_task

        @wraps(original_create_task)
        def create_task(
            loop_self: Any,
            coro: Any,
            *args: Any,
            **kwargs: Any,
        ) -> Any:
            context = kwargs.pop("context", None)
            new_context = contextvars.copy_context() if context is None else context

            try:
                shadowstack_var = get_shadowstack_contextvar()
                try:
                    original_shadowstack = shadowstack_var.get()
                except LookupError:
                    original_shadowstack = None

                try:
                    new_shadowstack = copy_shadowstack(original_shadowstack)
                except Exception:
                    new_shadowstack = None

                def set_shadowstack() -> None:
                    if new_shadowstack is not None:
                        shadowstack_var.set(new_shadowstack)

                new_context.run(set_shadowstack)
            except Exception:
                pass

            if self.supports_context_kw:
                kwargs["context"] = new_context
                return original_create_task(loop_self, coro, *args, **kwargs)
            else:
                return new_context.run(
                    original_create_task, loop_self, coro, *args, **kwargs
                )

        asyncio.base_events.BaseEventLoop.create_task = create_task  # type: ignore
