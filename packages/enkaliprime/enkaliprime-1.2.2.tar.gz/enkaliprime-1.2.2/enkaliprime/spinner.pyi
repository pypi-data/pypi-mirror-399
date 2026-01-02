"""
Type stubs for EnkaliPrime spinner utilities.
Provides comprehensive type information for loading animations.
"""

import threading
from typing import Any, Dict, Optional, Union
from typing_extensions import Literal

from .models import SpinnerStyle, ColorName

class Spinner:
    """
    Animated terminal spinner for loading states.

    Example:
        with Spinner("Thinking"):
            # Long operation
            time.sleep(3)
    """

    SPINNERS: Dict[str, list] = ...
    COLORS: Dict[str, str] = ...

    def __init__(
        self,
        message: str = "Loading",
        style: SpinnerStyle = "dots",
        color: ColorName = "cyan",
        speed: float = 0.1,
    ) -> None: ...

    def start(self) -> None: ...

    def stop(self, success: bool = True, final_message: Optional[str] = None) -> None: ...

    def __enter__(self) -> 'Spinner': ...

    def __exit__(
        self,
        exc_type: Any,
        exc_val: Any,
        exc_tb: Any
    ) -> None: ...

class LoadingBar:
    """
    Pulsing loading bar animation.

    Example:
        with LoadingBar("Processing"):
            time.sleep(3)
    """

    def __init__(
        self,
        message: str = "Loading",
        width: int = 20,
        color: ColorName = "cyan"
    ) -> None: ...

    def start(self) -> None: ...

    def stop(self, success: bool = True, final_message: Optional[str] = None) -> None: ...

    def __enter__(self) -> 'LoadingBar': ...

    def __exit__(
        self,
        exc_type: Any,
        exc_val: Any,
        exc_tb: Any
    ) -> None: ...

# Convenience functions
def spinner(
    message: str = "Thinking",
    style: SpinnerStyle = "dots",
    color: ColorName = "cyan"
) -> Spinner: ...

def loading_bar(
    message: str = "Loading",
    color: ColorName = "cyan"
) -> LoadingBar: ...

__all__ = [
    'Spinner',
    'LoadingBar',
    'spinner',
    'loading_bar',
]
