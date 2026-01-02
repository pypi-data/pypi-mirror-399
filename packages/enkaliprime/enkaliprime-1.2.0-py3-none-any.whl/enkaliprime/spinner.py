"""
Terminal Spinner Animations for EnkaliPrime SDK

Provides visually appealing loading animations while waiting for AI responses.
"""

import sys
import threading
import time
from typing import Optional


class Spinner:
    """
    Animated terminal spinner for loading states.
    
    Example:
        ```python
        with Spinner("Thinking"):
            # Long operation
            time.sleep(3)
        ```
    """
    
    # Different spinner styles
    SPINNERS = {
        "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
        "line": ["-", "\\", "|", "/"],
        "dots2": ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"],
        "bounce": ["⠁", "⠂", "⠄", "⠂"],
        "pulse": ["◐", "◓", "◑", "◒"],
        "moon": ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"],
        "earth": ["🌍", "🌎", "🌏"],
        "clock": ["🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚", "🕛"],
        "brain": ["🧠", "💭", "💡", "✨"],
        "arrows": ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"],
        "bar": ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▂"],
        "simple": [".", "..", "...", ".."],
    }
    
    # Color codes for terminal
    COLORS = {
        "cyan": "\033[96m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "white": "\033[97m",
        "reset": "\033[0m",
    }

    def __init__(
        self,
        message: str = "Loading",
        style: str = "dots",
        color: str = "cyan",
        speed: float = 0.1,
    ):
        """
        Initialize the spinner.
        
        Args:
            message: Text to display alongside the spinner
            style: Animation style (dots, line, dots2, bounce, pulse, moon, etc.)
            color: Color of the spinner (cyan, green, yellow, blue, magenta, white)
            speed: Animation speed in seconds between frames
        """
        self.message = message
        self.frames = self.SPINNERS.get(style, self.SPINNERS["dots"])
        self.color_code = self.COLORS.get(color, self.COLORS["cyan"])
        self.reset_code = self.COLORS["reset"]
        self.speed = speed
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._frame_index = 0
        self._start_time: Optional[float] = None

    def _spin(self):
        """Animation loop running in a separate thread."""
        while self._running:
            frame = self.frames[self._frame_index % len(self.frames)]
            elapsed = time.time() - self._start_time if self._start_time else 0
            elapsed_str = f"{elapsed:.1f}s"
            
            # Build the output line
            output = f"\r{self.color_code}{frame}{self.reset_code} {self.message}... {elapsed_str}"
            
            sys.stdout.write(output)
            sys.stdout.flush()
            
            self._frame_index += 1
            time.sleep(self.speed)

    def start(self):
        """Start the spinner animation."""
        if self._running:
            return
        
        self._running = True
        self._start_time = time.time()
        self._frame_index = 0
        
        # Hide cursor
        sys.stdout.write("\033[?25l")
        
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def stop(self, success: bool = True, final_message: Optional[str] = None):
        """
        Stop the spinner animation.
        
        Args:
            success: Whether the operation was successful
            final_message: Optional message to display after stopping
        """
        self._running = False
        
        if self._thread:
            self._thread.join(timeout=0.5)
        
        # Clear the line
        sys.stdout.write("\r" + " " * 80 + "\r")
        
        # Show final message if provided
        if final_message:
            icon = "✓" if success else "✗"
            color = self.COLORS["green"] if success else "\033[91m"  # Red for failure
            sys.stdout.write(f"{color}{icon}{self.reset_code} {final_message}\n")
        
        # Show cursor again
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        success = exc_type is None
        self.stop(success=success)
        return False


class LoadingBar:
    """
    Pulsing loading bar animation.
    
    Example:
        ```python
        with LoadingBar("Processing"):
            time.sleep(3)
        ```
    """
    
    def __init__(self, message: str = "Loading", width: int = 20, color: str = "cyan"):
        self.message = message
        self.width = width
        self.color_code = Spinner.COLORS.get(color, Spinner.COLORS["cyan"])
        self.reset_code = Spinner.COLORS["reset"]
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._position = 0
        self._direction = 1

    def _animate(self):
        """Animation loop."""
        while self._running:
            # Create the bar with a moving highlight
            bar = ""
            for i in range(self.width):
                if abs(i - self._position) <= 2:
                    intensity = 3 - abs(i - self._position)
                    bar += "█" * intensity + "▓" * (3 - intensity)
                else:
                    bar += "░"
            
            # Trim to width
            bar = bar[:self.width]
            
            output = f"\r{self.color_code}[{bar}]{self.reset_code} {self.message}..."
            sys.stdout.write(output)
            sys.stdout.flush()
            
            # Move position
            self._position += self._direction
            if self._position >= self.width - 1 or self._position <= 0:
                self._direction *= -1
            
            time.sleep(0.05)

    def start(self):
        """Start the animation."""
        if self._running:
            return
        
        self._running = True
        self._position = 0
        self._direction = 1
        
        sys.stdout.write("\033[?25l")  # Hide cursor
        
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()

    def stop(self, success: bool = True, final_message: Optional[str] = None):
        """Stop the animation."""
        self._running = False
        
        if self._thread:
            self._thread.join(timeout=0.5)
        
        sys.stdout.write("\r" + " " * 80 + "\r")
        
        if final_message:
            icon = "✓" if success else "✗"
            color = Spinner.COLORS["green"] if success else "\033[91m"
            sys.stdout.write(f"{color}{icon}{self.reset_code} {final_message}\n")
        
        sys.stdout.write("\033[?25h")  # Show cursor
        sys.stdout.flush()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop(success=exc_type is None)
        return False


# Convenience functions
def spinner(message: str = "Thinking", style: str = "dots", color: str = "cyan") -> Spinner:
    """
    Create a spinner context manager.
    
    Args:
        message: Loading message
        style: Animation style
        color: Spinner color
        
    Returns:
        Spinner instance for use with 'with' statement
        
    Example:
        ```python
        with spinner("Generating response"):
            response = client.send_message(...)
        ```
    """
    return Spinner(message=message, style=style, color=color)


def loading_bar(message: str = "Loading", color: str = "cyan") -> LoadingBar:
    """
    Create a loading bar context manager.
    
    Args:
        message: Loading message
        color: Bar color
        
    Returns:
        LoadingBar instance for use with 'with' statement
    """
    return LoadingBar(message=message, color=color)


