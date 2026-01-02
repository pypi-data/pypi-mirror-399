# TerminalNexus: Advanced Terminal Styling

A high-performance terminal styling engine for Python, designed for advanced UI/UX in command-line interfaces. TerminalNexus provides seamless integration of HEX color codes into your terminal applications, enabling you to create visually stunning and professional command-line interfaces.

## 🚀 Features

- **High-Performance HEX Color Processing**: Efficiently convert and apply HEX color codes to terminal text
- **Lightweight & Fast**: Minimal overhead, maximum performance
- **Easy to Use**: Simple, intuitive API for styling terminal output
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Python 3.6+ Compatible**: Supports all modern Python versions

## 📥 Installation

Install TerminalNexus using pip:

```bash
pip install terminalnexus
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/NexusDev-Labs/TerminalNexus.git
```

## 🎨 Quick Start

Get started with TerminalNexus in just a few lines of code:

```python
import terminalnexus

# Print colored text
print(terminalnexus.set("#ff0000") + "Hello, World!" + terminalnexus.reset())

# Use in input prompts
user_input = input(terminalnexus.set("#00ff00") + "Enter your name: " + terminalnexus.set("#0000ff"))
```

## 📖 Usage Examples

### Basic Text Styling

```python
import terminalnexus

# Red text
print(terminalnexus.set("#ff0000") + "This is red text" + terminalnexus.reset())

# Green text
print(terminalnexus.set("#00ff00") + "This is green text" + terminalnexus.reset())

# Blue text
print(terminalnexus.set("#0000ff") + "This is blue text" + terminalnexus.reset())
```

### Interactive Prompts

```python
import terminalnexus

name = input(
    terminalnexus.set("#00ff00") + 
    "What's your name? " + 
    terminalnexus.set("#ffff00")
)
print(terminalnexus.set("#ff00ff") + f"Hello, {name}!" + terminalnexus.reset())
```

### Combining Colors

```python
import terminalnexus

# Create colorful output
message = (
    terminalnexus.set("#ff5733") + "Welcome" +
    terminalnexus.reset() + " to " +
    terminalnexus.set("#33c3f0") + "TerminalNexus" +
    terminalnexus.reset()
)
print(message)
```

## 🔧 API Reference

### `terminalnexus.set(hex)`

Sets the terminal color to the specified HEX code.

**Parameters:**
- `hex` (str): A HEX color code in the format `#RRGGBB` (e.g., `#ff0000` for red)

**Returns:**
- `str`: ANSI escape sequence for the specified color

**Example:**
```python
color_code = terminalnexus.set("#ff5733")
```

### `terminalnexus.reset()`

Resets the terminal color to default.

**Returns:**
- `str`: ANSI escape sequence to reset terminal formatting

**Example:**
```python
reset_code = terminalnexus.reset()
```

## 📋 Requirements

- Python 3.6 or higher
- A terminal that supports ANSI color codes (most modern terminals)

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request.

## 📜 License

TerminalNexus is open-source software released under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🌐 Links

- **GitHub**: [https://github.com/NexusDev-Labs/TerminalNexus](https://github.com/NexusDev-Labs/TerminalNexus)
- **Issues**: [https://github.com/NexusDev-Labs/TerminalNexus/issues](https://github.com/NexusDev-Labs/TerminalNexus/issues)

## 💡 Acknowledgments

Thank you for using TerminalNexus! We hope this library helps you create beautiful and engaging command-line interfaces.
