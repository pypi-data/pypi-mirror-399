from typing import Callable, Optional

from langgraph_enterprise_sdk.api.state import State


class ExecutionLifecycle:
    """
    Execution lifecycle hooks.

    Hooks must be side-effect safe (ZAD).
    """

    def __init__(
        self,
        on_start: Optional[Callable[[State], None]] = None,
        on_step: Optional[Callable[[str, State], None]] = None,
        on_complete: Optional[Callable[[State], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
    ):
        self.on_start = on_start
        self.on_step = on_step
        self.on_complete = on_complete
        self.on_error = on_error
