# TermTinty 🎨

> **A fluid and lightweight terminal colorizer for Python.**

**TermTinty** (the package) brings you **Tinty** (the tool), a library designed to make your code as elegant as your terminal. Its philosophy is symmetry and fluidity.

```python
from termtinty import Tinty
```

## Why TermTinty?

Most libraries force you to concatenate strings or remember complex constants. **Tinty** breaks that mold by using a **Fluent Interface**. This isn't just syntactic sugar; it's a way of programming that prioritizes human readability.

- 🔗 **Fluent Chaining**: Chain methods as if you were writing a sentence.
- 🪶 **Ultralight**: No dependencies.
- 🧹 **Auto-Reset**: State is automatically cleared.
- 🧘 **Zen API**: Designed for intuition.

## Installation

```bash
pip install termtinty
```

## Usage

### The Symmetric Pattern

```python
from termtinty import Tinty

t = Tinty() # Instantiate your brush
print(t.CYAN("TermTinty").GREEN(" is ready!"))
```

## 🔗 Deep Dive: The Fluent Chain

**Method chaining** is the heart of TermTinty. Unlike traditional libraries where you sum strings (`+`), here you *transform* the flow of information.

**Why is it better?**
1.  **Readability**: Reads left-to-right, like English.
2.  **Less Noise**: Eliminates `+` operators and intermediate variables.
3.  **Context**: Logically groups related styles.

```python
# Traditional Style (Hard to read)
# print(Back.RED + Fore.WHITE + "Error:" + Style.RESET_ALL + Fore.YELLOW + " Disk full")

# TermTinty Style (Clean)
print(t.bgRED().WHITE("Error: ").YELLOW("Disk full")) 
# (Note: bgRED has not been implemented but serves as a style example for background colors)
```

## 🧠 API Philosophy: Instance vs Static

A common question during the design of this library was: *Why `t = Tinty()` instead of static methods like `Tinty.RED()`?*

### The Decision: Object-Oriented for State Management
To achieve true and safe **Chaining**, we need "memory".

*   **If Static (`Class.method()`):** There is no memory between calls. It would be hard to know when to close the color (RESET) or how to accumulate multiple segments (`.RED().BLUE()`) without returning strange objects.
*   **With Instance (`obj.method()`):** The instance `t` acts as a **smart buffer**. It accumulates your intentions and knows exactly when to clean itself (Auto-Reset) when printed.

This allows the API to be powerful yet invisible. The user doesn't manage state; `Tinty` does.

## ⚔️ Competition and Comparison

How does TermTinty stack up against the giants?

| Feature | TermTinty | Colorama | Termcolor | Rich |
| :--- | :---: | :---: | :---: | :---: |
| **Syntax** | Fluent (`.RED()`) | Constants (`Fore.RED`) | Functional (`colored()`) | Objects/Tags |
| **Chaining** | **Native & Core** | Manual (concatenation) | Nested (difficult) | Via Tags |
| **Auto-Reset** | **Yes (Automatic)** | Requires `autoreset=True` | Yes | Yes |
| **Weight** | 🪶 Feather | Light | Light | Heavy (Feature-rich) |
| **Focus** | **DX (Developer Exp)** | Win Compatibility | Functional | UI Framework |

**TermTinty** is for those who want the syntax power of *Rich* but the lightness of *Colorama*.

## 🚀 Roadmap / TODO

We are actively working on expanding TermTinty. Here is what's coming next:

- [ ] **Background Colors**: Methods like `.bgRED()`, `.bgBLUE()`, etc.
- [ ] **Text Styles**: Support for **BOLD**, *ITALIC*, <u>UNDERLINE</u>, etc.
- [ ] **Mixins & Custom Combinations**: Create your own reusable styles (e.g., `WarningStyle = t.bgYELLOW().RED().BOLD()`).
- [ ] **RGB / TrueColor**: Support for 16 million colors.

## Development

Project structure:

```text
termtinty/
├── termtinty/      # Source Code
│   ├── __init__.py
│   └── tinty.py
├── tests/          # Unit Tests
└── pyproject.toml
```

Tests:
```bash
uv add --dev pytest
uv run pytest -vv
```

---

## 🏛️ History and Naming Alternatives

During the conception phase (Branding), multiple identities were evaluated. These alternatives reflect different facets of what TermTinty came to be:

1.  **ChromaFlow**: *("The Technician")* - Emphasized the continuous "flow" of colors. Discarded for sounding too much like a video processing tool.
2.  **ChromaChain**: *("The Structural")* - Literally described the software architecture.
3.  **Iris**: *("The Mythological")* - Reference to the messenger of the gods. Discarded due to PyPI name collision.
4.  **Tinty**: *("The Chosen One")* - Captures the essence: small, friendly, and does one thing well (gives tint).