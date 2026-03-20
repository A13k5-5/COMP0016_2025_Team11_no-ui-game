from threading import Event
from typing import Any, Callable


class GenerationCancelledError(Exception):
    """Raised when game generation is canceled by the user."""


def raise_if_cancelled(
    cancel_event: Event | None,
    progress_cb: Callable[[dict[str, Any]], None] | None = None,
    message: str = "Generation canceled by user",
) -> None:
    if cancel_event is None or not cancel_event.is_set():
        return

    if progress_cb is not None:
        progress_cb({"stage": "cancelled", "message": message})

    raise GenerationCancelledError(message)

