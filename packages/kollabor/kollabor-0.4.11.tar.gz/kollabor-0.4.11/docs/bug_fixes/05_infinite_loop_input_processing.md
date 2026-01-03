# Bug Fix #5: Infinite Loop in Input Processing

## 🚨 **CRITICAL BUG** - UI FREEZE

**Location:** `core/io/input_handler.py:146-228`
**Severity:** Critical
**Impact:** UI can freeze indefinitely during paste operations

## 📋 **Bug Description**

The input processing loop can become infinite when handling large pastes or malformed input, causing the terminal UI to freeze completely and requiring the user to kill the process.

### Current Problematic Code
```python
# core/io/input_handler.py:146-228 (approximate)
class InputHandler:
    async def read_input(self):
        """Read user input from terminal."""
        buffer = []

        while True:  # ← Infinite loop with no escape!
            try:
                char = await self._read_char()

                if char == '\x03':  # Ctrl+C
                    break
                elif char == '\x0a':  # Enter
                    break
                elif char == '\x7f':  # Backspace
                    if buffer:
                        buffer.pop()
                else:
                    buffer.append(char)  # ← Can grow indefinitely!

            except KeyboardInterrupt:
                break
            except Exception as e:
                # Continue processing even on errors!
                continue  # ← Never exits on error!

        return ''.join(buffer)

    async def _read_char(self):
        """Read single character from terminal."""
        # This can block indefinitely without timeout!
        while True:
            char = sys.stdin.read(1)
            if char:
                return char
            # ← No sleep, no timeout, infinite busy loop!
```

### The Issue
- **Infinite loops** with no timeout or escape conditions
- **Unbounded buffer growth** during paste operations
- **No iteration limits** or protection against malformed input
- **CPU exhaustion** from busy-wait loops
- **UI freeze** requiring process kill

## 🔧 **Fix Strategy**

### 1. Add Input Buffer Limits and Protection
```python
import asyncio
import sys
from typing import Optional

class InputHandler:
    def __init__(self, max_buffer_size=10000, max_read_attempts=1000):
        self.max_buffer_size = max_buffer_size
        self.max_read_attempts = max_read_attempts
        self.read_timeout = 0.1  # seconds between reads
        self.total_timeout = 30.0  # seconds for entire input

    async def read_input(self, prompt: str = "") -> Optional[str]:
        """Read user input with proper protection against infinite loops."""
        buffer = []
        read_attempts = 0
        start_time = asyncio.get_event_loop().time()

        try:
            while read_attempts < self.max_read_attempts:
                # Check total timeout
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > self.total_timeout:
                    logger.warning(f"Input timeout after {elapsed:.1f}s")
                    return None

                # Check buffer size
                if len(buffer) >= self.max_buffer_size:
                    logger.warning(f"Input buffer limit reached ({self.max_buffer_size})")
                    return ''.join(buffer)

                # Read character with timeout
                try:
                    char = await asyncio.wait_for(
                        self._read_char_safe(),
                        timeout=self.read_timeout
                    )

                    if char is None:  # No input available
                        read_attempts += 1
                        continue

                    # Reset read attempts on successful read
                    read_attempts = 0

                    # Handle special characters
                    if char == '\x03':  # Ctrl+C
                        logger.info("Input cancelled by user")
                        return None
                    elif char == '\x0a' or char == '\x0d':  # Enter/Return
                        return ''.join(buffer)
                    elif char == '\x7f':  # Backspace
                        if buffer:
                            buffer.pop()
                            await self._handle_backspace()
                    elif char == '\x1b':  # Escape sequences
                        await self._handle_escape_sequence()
                    elif self._is_printable(char):
                        buffer.append(char)
                        await self._echo_char(char)

                except asyncio.TimeoutError:
                    read_attempts += 1
                    continue
                except KeyboardInterrupt:
                    logger.info("Input interrupted")
                    return None
                except Exception as e:
                    logger.error(f"Error reading input: {e}")
                    read_attempts += 1
                    if read_attempts > 10:  # Too many consecutive errors
                        logger.warning("Too many read errors, giving up")
                        return None

        except Exception as e:
            logger.error(f"Critical error in input processing: {e}")
            return None

        # Return what we have if we hit max attempts
        if buffer:
            logger.warning(f"Returning partial input after {read_attempts} attempts")
            return ''.join(buffer)

        return None
```

### 2. Implement Safe Character Reading
```python
async def _read_char_safe(self) -> Optional[str]:
    """Safely read a single character with proper error handling."""
    try:
        # Use asyncio to read without blocking
        loop = asyncio.get_event_loop()

        # Check if stdin has data available
        if sys.stdin in loop.selectors or hasattr(sys.stdin, 'peek'):
            # Non-blocking read
            char = sys.stdin.read(1)
            return char if char else None
        else:
            # Fallback to async read
            char = await loop.run_in_executor(None, sys.stdin.read, 1)
            return char if char else None

    except Exception as e:
        logger.debug(f"Error reading character: {e}")
        return None

def _is_printable(self, char: str) -> bool:
    """Check if character is printable and should be added to buffer."""
    if not char or len(char) != 1:
        return False

    # Basic printable ASCII check
    return (char.isprintable() and
            char not in ('\x00', '\x01', '\x02', '\x03', '\x04', '\x05'))

async def _handle_backspace(self):
    """Handle backspace character."""
    # Send backspace sequence to terminal
    sys.stdout.write('\x08 \x08')  # Backspace, space, backspace
    sys.stdout.flush()

async def _echo_char(self, char: str):
    """Echo character to terminal."""
    sys.stdout.write(char)
    sys.stdout.flush()

async def _handle_escape_sequence(self):
    """Handle escape sequences (arrows, function keys, etc.)."""
    try:
        # Read next two characters quickly
        next_chars = []
        for _ in range(2):
            char = await asyncio.wait_for(
                self._read_char_safe(),
                timeout=0.01  # Very short timeout for escape sequences
            )
            if char:
                next_chars.append(char)

        # Handle common escape sequences
        if len(next_chars) >= 2:
            if next_chars[0] == '[':
                if next_chars[1] == 'A':  # Up arrow
                    # Handle up arrow (history navigation)
                    pass
                elif next_chars[1] == 'B':  # Down arrow
                    # Handle down arrow
                    pass
                elif next_chars[1] == 'C':  # Right arrow
                    # Handle right arrow
                    pass
                elif next_chars[1] == 'D':  # Left arrow
                    # Handle left arrow
                    pass

    except asyncio.TimeoutError:
        # Not an escape sequence, just a single ESC key
        pass
```

### 3. Add Paste Operation Handling
```python
async def read_input_with_paste_detection(self, prompt: str = "") -> Optional[str]:
    """Read input with special handling for paste operations."""
    buffer = []
    read_attempts = 0
    paste_mode = False
    consecutive_chars = 0
    start_time = asyncio.get_event_loop().time()

    while read_attempts < self.max_read_attempts:
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed > self.total_timeout:
            return None

        if len(buffer) >= self.max_buffer_size:
            return ''.join(buffer)

        try:
            char = await asyncio.wait_for(
                self._read_char_safe(),
                timeout=0.05 if not paste_mode else 0.01  # Faster timeout in paste mode
            )

            if char is None:
                # Check if we should enter paste mode
                if consecutive_chars > 5:
                    paste_mode = True
                    logger.debug("Entering paste mode")

                consecutive_chars = 0
                read_attempts += 1
                continue

            # Reset counters on successful read
            read_attempts = 0
            consecutive_chars += 1

            # Handle the character
            if char == '\x03':  # Ctrl+C
                return None
            elif char == '\x0a' or char == '\x0d':  # Enter
                if paste_mode:
                    logger.debug("Exiting paste mode")
                    paste_mode = False
                return ''.join(buffer)
            elif char == '\x7f':  # Backspace
                if buffer:
                    buffer.pop()
                    await self._handle_backspace()
                paste_mode = False  # Exit paste mode on backspace
            elif self._is_printable(char):
                buffer.append(char)
                await self._echo_char(char)

        except asyncio.TimeoutError:
            read_attempts += 1
            consecutive_chars = 0
            continue
        except KeyboardInterrupt:
            return None
        except Exception as e:
            logger.error(f"Error in input processing: {e}")
            read_attempts += 1
            if read_attempts > 10:
                return None

    return ''.join(buffer) if buffer else None
```

### 4. Add Configuration Options
```python
# core/config/input_config.py
class InputConfig:
    max_buffer_size: int = 10000
    max_read_attempts: int = 1000
    read_timeout: float = 0.1
    total_timeout: float = 30.0
    paste_detection_threshold: int = 5
    enable_paste_mode: bool = True
```

### 5. Add Input Validation and Safety
```python
def _validate_input_state(self, buffer: list) -> bool:
    """Validate input state for safety."""
    if len(buffer) > self.max_buffer_size:
        return False

    # Check for potential malicious input patterns
    if len(buffer) > 100:
        # Look for suspicious patterns (repeated escape sequences, etc.)
        escape_count = sum(1 for char in buffer[-100:] if char == '\x1b')
        if escape_count > 50:  # Too many escape sequences
            logger.warning("Suspicious input pattern detected")
            return False

    return True

async def _safety_check(self):
    """Perform periodic safety checks."""
    # This can be called from a background task
    # to ensure the input handler doesn't get stuck
    pass
```

## ✅ **Implementation Steps**

1. **Add buffer size limits** and protection against unbounded growth
2. **Implement timeouts** for character reading and total input time
3. **Add iteration limits** to prevent infinite loops
4. **Implement paste detection** and special handling
5. **Add comprehensive error handling** with recovery mechanisms
6. **Create configuration options** for input behavior

## 🧪 **Testing Strategy**

1. **Test infinite input** - verify timeouts work
2. **Test large paste operations** - verify buffer limits
3. **Test escape sequences** - verify proper handling
4. **Test timeout scenarios** - verify graceful degradation
5. **Test error recovery** - verify system remains responsive
6. **Test paste detection** - verify mode switching works

## 🚀 **Files to Modify**

- `core/io/input_handler.py` - Main fix location
- `core/config/input_config.py` - Add input configuration
- `tests/test_input_handler.py` - Add input safety tests

## 📊 **Success Criteria**

- ✅ Input processing has proper timeouts and limits
- ✅ Infinite loops are prevented with iteration limits
- ✅ Buffer growth is bounded by configurable limits
- ✅ Paste operations are detected and handled efficiently
- ✅ System remains responsive during input processing
- ✅ Graceful degradation on errors and timeouts

## 💡 **Why This Fixes the Issue**

This fix prevents UI freezes by:
- **Adding timeout protection** to prevent infinite waits
- **Limiting buffer size** to prevent memory exhaustion
- **Implementing iteration limits** to prevent infinite loops
- **Adding paste detection** for efficient bulk input handling
- **Providing error recovery** and graceful degradation
- **Ensuring responsive behavior** even with malformed input

The infinite loop is eliminated because every potential blocking operation has a timeout, and the input processing logic includes multiple escape mechanisms and safety checks to prevent the UI from freezing.