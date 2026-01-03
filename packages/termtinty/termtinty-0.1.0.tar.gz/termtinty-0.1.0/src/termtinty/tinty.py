from .color import Color
from typing import Self


class Tinty:
    """
    A fluent interface for coloring terminal text using ANSI escape codes.
    
    This class allows method chaining to apply colors sequentially.
    The internal state (buffer) is automatically reset when the object is converted to a string.
    
    Example:
        t = Tinty()
        print(t.RED("Error: ").YELLOW("File not found"))
    """

    def __init__(self):
        """Initialize the Tinty text buffer."""
        self.text = ""

    def BLACK(self, text: str) -> Self:
        """Append black text to the buffer."""
        self.text += Color.BLACK + text
        return self
    
    def RED(self, text: str) -> Self:
        """Append red text to the buffer."""
        self.text += Color.RED + text
        return self
    
    def GREEN(self, text: str) -> Self:
        """Append green text to the buffer."""
        self.text += Color.GREEN + text
        return self
    
    def YELLOW(self, text: str) -> Self:
        """Append yellow text to the buffer."""
        self.text += Color.YELLOW + text
        return self
    
    def BLUE(self, text: str) -> Self:
        """Append blue text to the buffer."""
        self.text += Color.BLUE + text
        return self

    def MAGENTA(self, text: str) -> Self:
        """Append magenta text to the buffer."""
        self.text += Color.MAGENTA + text
        return self

    def CYAN(self, text: str) -> Self:
        """Append cyan text to the buffer."""
        self.text += Color.CYAN + text
        return self

    def RESET(self, text: str) -> Self:
        """
        Manually append a reset code and optional text.
        Note: The buffer is automatically reset when printing, so this is rarely needed manually.
        """
        self.text += Color.RESET + text
        return self
    

    def __str__(self):
        """
        Return the colored string and reset the internal buffer.
        Automatically appends a RESET code at the end.
        """
        final = self.text + Color.RESET
        self.text = ""
        return final

    def __repr__(self):
        """Return the raw string representation of the buffer without resetting it."""
        return f"{self.text}"