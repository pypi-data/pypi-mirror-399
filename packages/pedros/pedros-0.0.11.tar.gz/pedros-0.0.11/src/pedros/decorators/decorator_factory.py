from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from types import TracebackType
from typing import Any, Awaitable, Callable, Generic, ParamSpec, TypeVar, cast

import wrapt

__all__ = ["CallContext", "make_around_decorator"]

Params = ParamSpec("Params")
ReturnType = TypeVar("ReturnType")


@dataclass
class CallContext(Generic[Params, ReturnType]):
    wrapped: Callable[Params, ReturnType]
    instance: Any | None
    args: Params.args
    kwargs: Params.kwargs
    result: ReturnType | Awaitable[ReturnType] | None = None
    error: BaseException | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def set_result(self, value: ReturnType | Awaitable[ReturnType]) -> None:
        self.result = value

    def set_error(self, err: BaseException) -> None:
        self.error = err


BeforeHook = Callable[[CallContext[Params, ReturnType]], None]
AfterHook = Callable[[CallContext[Params, ReturnType]], None]


class _HookContext(Generic[Params, ReturnType]):
    def __init__(
        self,
            ctx: CallContext[Params, ReturnType],
            before: BeforeHook[Params, ReturnType] | None,
            after: AfterHook[Params, ReturnType] | None,
    ) -> None:
        self._ctx = ctx
        self._before = before
        self._after = after

    def __enter__(self) -> None:
        if self._before is not None:
            self._before(self._ctx)
        return None

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool | None:
        if exc is not None:
            self._ctx.set_error(exc)

        if self._after is not None:
            self._after(self._ctx)

        return None


def make_around_decorator(
    *,
        before: BeforeHook[Params, ReturnType] | None = None,
        after: AfterHook[Params, ReturnType] | None = None,
) -> Callable[[Callable[Params, ReturnType]], Callable[Params, ReturnType]]:
    @wrapt.decorator
    def _wrapper(
            wrapped: Callable[Params, ReturnType],
        instance: Any | None,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> ReturnType | Awaitable[ReturnType]:
        ctx: CallContext[Params, ReturnType] = CallContext(
            wrapped=cast(Callable[Params, ReturnType], wrapped),
            instance=instance,
            args=cast(Params.args, args),
            kwargs=cast(Params.kwargs, kwargs),
        )

        is_async = inspect.iscoroutinefunction(wrapped)

        if not is_async:
            with _HookContext(ctx, before, after):
                value = wrapped(*args, **kwargs)
                ctx.set_result(cast(ReturnType, value))
                return cast(ReturnType, value)

        async def _run_async() -> ReturnType:
            with _HookContext(ctx, before, after):
                wrapped_async = cast(Callable[..., Awaitable[ReturnType]], wrapped)
                value = await wrapped_async(*args, **kwargs)
                ctx.set_result(cast(ReturnType, value))
                return cast(ReturnType, value)

        coro = _run_async()
        ctx.set_result(coro)
        return coro

    return cast(Callable[[Callable[Params, ReturnType]], Callable[Params, ReturnType]], _wrapper)
