# KeyboardGat

A simple, cross-platform Python library to temporarily block and unblock keyboard input in the terminal.

This can be useful for scenarios where you want to prevent user input during a critical operation or create a more controlled command-line interface.

## How to Use

Install the package from PyPI:
```bash
pip install KeyboardGat
```

Here is a basic example of how to use `KeyboardGat`:

```python
from KeyboardGat import KeyboardGate
import time

# Initialize the gate
gate = KeyboardGate()

print("Keyboard input will be disabled for 3 seconds.")
gate.KeyboardGateDisable()
time.sleep(3)
gate.KeyboardGateEnable()
print("Keyboard input is now enabled.")

# You can also use it as a context manager
with KeyboardGate():
    print("Input is disabled inside this block.")
    time.sleep(2)
print("Input is automatically re-enabled outside the 'with' block.")

```

## How It Works

-   **On Unix-like systems (Linux, macOS):** It modifies the terminal's attributes (`termios`) to turn off `ECHO`, which prevents characters from being displayed.
-   **On Windows:** It uses the `msvcrt` module to consume any keyboard events that are waiting in the input buffer.
