#!/usr/bin/env python3
"""Key reader utility for debugging terminal input sequences.

This tool helps debug what actual key sequences are sent by the terminal
when pressing various key combinations. Useful for implementing new
keyboard shortcuts and understanding terminal behavior.

Usage:
    python core/utils/key_reader.py

Press keys to see their sequences, Ctrl+C to exit.
"""

import sys
import signal

# Platform-specific imports
IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    import msvcrt
else:
    import tty
    import termios
    import select


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print('\n\nExiting key reader...')
    sys.exit(0)


def main_unix():
    """Main key reader loop for Unix systems."""
    print("Key Reader (Unix) - Press keys to see their sequences (Ctrl+C to exit)")
    print("=" * 60)

    # Set up signal handler for graceful exit
    signal.signal(signal.SIGINT, signal_handler)

    # Save terminal settings
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        # Set terminal to raw mode
        tty.setraw(sys.stdin.fileno())

        key_count = 0

        while True:
            # Read one character
            char = sys.stdin.read(1)
            key_count += 1

            # Get character info
            ascii_code = ord(char)
            hex_code = hex(ascii_code)

            # Determine key name
            if ascii_code == 3:  # Ctrl+C
                print(f"\n\r[{key_count:03d}] Key: 'CTRL+C' | ASCII: {ascii_code} | Hex: {hex_code} | Raw: {repr(char)}")
                break
            elif ascii_code == 27:  # ESC or start of escape sequence
                key_name = "ESC"
                # Try to read more characters for escape sequences
                try:
                    # Set a short timeout to see if more chars follow
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        sequence = char
                        while select.select([sys.stdin], [], [], 0.05)[0]:
                            next_char = sys.stdin.read(1)
                            sequence += next_char
                            if len(sequence) > 10:  # Prevent infinite sequences
                                break

                        # Update display info
                        char = sequence
                        ascii_code = f"ESC sequence"
                        hex_code = " ".join(hex(ord(c)) for c in sequence)
                        key_name = f"ESC_SEQ({sequence[1:]})" if len(sequence) > 1 else "ESC"
                except:
                    pass
            elif 1 <= ascii_code <= 26:  # Ctrl+A through Ctrl+Z
                key_name = f"CTRL+{chr(ascii_code + 64)}"
            elif ascii_code == 127:
                key_name = "BACKSPACE"
            elif 32 <= ascii_code <= 126:
                key_name = f"'{char}'"
            else:
                key_name = f"SPECIAL({ascii_code})"

            # Display the key info
            print(f"\r[{key_count:03d}] Key: {key_name} | ASCII: {ascii_code} | Hex: {hex_code} | Raw: {repr(char)}")

    finally:
        # Restore terminal settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def main_windows():
    """Main key reader loop for Windows systems."""
    print("Key Reader (Windows) - Press keys to see their sequences (Ctrl+C to exit)")
    print("=" * 60)

    key_count = 0

    try:
        while True:
            if msvcrt.kbhit():
                # Read a key
                char = msvcrt.getch()
                key_count += 1

                # Get character info
                ascii_code = char[0] if isinstance(char, bytes) else ord(char)
                hex_code = hex(ascii_code)

                # Handle special keys (arrow keys, function keys, etc.)
                if ascii_code in (0, 224):  # Extended key prefix
                    # Read the actual key code
                    ext_char = msvcrt.getch()
                    ext_code = ext_char[0] if isinstance(ext_char, bytes) else ord(ext_char)
                    key_name = f"EXTENDED({ext_code})"
                    # Map common extended keys
                    ext_key_map = {
                        72: "ArrowUp", 80: "ArrowDown",
                        75: "ArrowLeft", 77: "ArrowRight",
                        71: "Home", 79: "End",
                        73: "PageUp", 81: "PageDown",
                        82: "Insert", 83: "Delete",
                        59: "F1", 60: "F2", 61: "F3", 62: "F4",
                        63: "F5", 64: "F6", 65: "F7", 66: "F8",
                        67: "F9", 68: "F10", 133: "F11", 134: "F12",
                    }
                    if ext_code in ext_key_map:
                        key_name = ext_key_map[ext_code]
                    print(f"[{key_count:03d}] Key: {key_name} | Code: {ascii_code},{ext_code} | Hex: {hex_code},{hex(ext_code)}")
                elif ascii_code == 3:  # Ctrl+C
                    print(f"[{key_count:03d}] Key: 'CTRL+C' | ASCII: {ascii_code} | Hex: {hex_code}")
                    break
                elif ascii_code == 27:  # ESC
                    print(f"[{key_count:03d}] Key: 'ESC' | ASCII: {ascii_code} | Hex: {hex_code}")
                elif 1 <= ascii_code <= 26:  # Ctrl+A through Ctrl+Z
                    key_name = f"CTRL+{chr(ascii_code + 64)}"
                    print(f"[{key_count:03d}] Key: {key_name} | ASCII: {ascii_code} | Hex: {hex_code}")
                elif ascii_code == 8:
                    print(f"[{key_count:03d}] Key: BACKSPACE | ASCII: {ascii_code} | Hex: {hex_code}")
                elif ascii_code == 13:
                    print(f"[{key_count:03d}] Key: ENTER | ASCII: {ascii_code} | Hex: {hex_code}")
                elif 32 <= ascii_code <= 126:
                    char_str = chr(ascii_code)
                    print(f"[{key_count:03d}] Key: '{char_str}' | ASCII: {ascii_code} | Hex: {hex_code}")
                else:
                    print(f"[{key_count:03d}] Key: SPECIAL({ascii_code}) | Hex: {hex_code}")

    except KeyboardInterrupt:
        print('\n\nExiting key reader...')


def main():
    """Main entry point - selects platform-specific implementation."""
    if IS_WINDOWS:
        main_windows()
    else:
        main_unix()


if __name__ == "__main__":
    main()