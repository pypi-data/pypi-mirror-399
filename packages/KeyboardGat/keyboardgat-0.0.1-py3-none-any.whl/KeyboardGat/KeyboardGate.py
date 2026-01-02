import sys
import platform

# Pre-check OS to import correct system libraries
OS_TYPE = platform.system()

if OS_TYPE == "Windows":
    import msvcrt
else:
    import termios

class KeyboardGate:
    def __init__(self):
        self.os_type = OS_TYPE
        self.old_settings = None

    def KeyboardGateDisable(self):
        """Prevents the user from typing/seeing input."""
        if self.os_type == "Windows":
            # On Windows, we flush any keys currently waiting in the buffer
            while msvcrt.kbhit():
                msvcrt.getch()
        else:
            # On Unix, we disable the 'ECHO' attribute of the terminal
            try:
                fd = sys.stdin.fileno()
                self.old_settings = termios.tcgetattr(fd)
                new_settings = termios.tcgetattr(fd)
                new_settings[3] = new_settings[3] & ~termios.ECHO
                termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)
            except Exception:
                # Fallback for environments that don't support termios
                pass

    def KeyboardGateEnable(self):
        """Restores the ability to type."""
        if self.os_type == "Windows":
            # Final flush to ensure no 'spam' carries over to the next input
            while msvcrt.kbhit():
                msvcrt.getch()
        else:
            # Restore the original terminal settings (ECHO ON)
            if self.old_settings:
                try:
                    fd = sys.stdin.fileno()
                    termios.tcsetattr(fd, termios.TCSADRAIN, self.old_settings)
                except Exception:
                    pass

    # Safety aliases for 'with' statement usage
    def __enter__(self):
        self.KeyboardGateDisable()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.KeyboardGateEnable()
