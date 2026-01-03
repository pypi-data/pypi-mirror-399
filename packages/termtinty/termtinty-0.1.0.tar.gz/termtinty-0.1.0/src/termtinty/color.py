import enum

class Color(str, enum.Enum):
    """
    ANSI escape codes for terminal colors.
    Inherits from str to allow direct concatenation with strings.
    """
    BLACK = '\033[30m'    # Standard Black
    RED = '\033[31m'      # Standard Red
    GREEN = '\033[32m'    # Standard Green
    YELLOW = '\033[33m'   # Standard Yellow (Orange on some terminals)
    BLUE = '\033[34m'     # Standard Blue
    MAGENTA = '\033[35m'  # Standard Magenta/Purple
    CYAN = '\033[36m'     # Standard Cyan
    RESET = '\033[0m'     # Reset all attributes to default