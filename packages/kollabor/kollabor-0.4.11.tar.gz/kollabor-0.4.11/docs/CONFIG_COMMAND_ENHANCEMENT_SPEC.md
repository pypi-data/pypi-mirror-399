# `/config` Command Enhancement Specification

**Status:** Draft
**Created:** 2025-11-07
**Author:** Claude Code
**Priority:** High

---

## Executive Summary

Transform the `/config` slash command from a display-only modal to a fully functional configuration management interface with real-time editing, validation, persistence, and rollback capabilities.

**Current State:** Modal displays widgets but doesn't persist changes
**Target State:** Full CRUD operations on config with atomic transactions and event integration

---

## 1. Current System Analysis

### Slash Command Architecture

**Data Flow:**
```
User types "/config"
  ↓
SlashCommandParser.parse_command() (parser.py:40)
  ↓
SlashCommandExecutor.execute_command() (executor.py:29)
  ↓
SystemCommandsPlugin.handle_config() (system_commands.py:142)
  ↓
Returns CommandResult with modal UI config
  ↓
Executor triggers modal via MODAL_TRIGGER event (executor.py:214)
```

**Key Components:**
- **Parser** (`core/commands/parser.py:13`) - Detects `/` commands, uses `shlex` for arg parsing
- **Registry** (`core/commands/registry.py:11`) - Stores command definitions, handles aliases + categories
- **Executor** (`core/commands/executor.py:13`) - Runs command handlers, emits events, triggers modals
- **ConfigManager** (`core/config/manager.py:14`) - Loads/saves JSON config with dot notation access
- **Modal System** (`core/ui/modal_interaction_handler.py`) - Handles modal rendering and navigation
- **Widgets** (`core/ui/widgets/`) - Checkbox, Slider, Dropdown, TextInput components

### Current `/config` Implementation

**Location:** `core/commands/system_commands.py:142`

**What Works:**
- Modal opens with defined widgets
- Navigation between widgets (↑↓)
- Widget value display from config
- ESC to close modal

**What's Missing:**
- Save functionality (Ctrl+S does nothing)
- Value persistence to config file
- Validation before save
- Event emission on config change
- Rollback on cancel
- User feedback (success/error messages)

---

## 2. Enhancement Objectives

### Primary Goals

1. **Persistence:** Save widget values to config file via `ConfigManager.set()`
2. **Validation:** Type and range validation before persisting
3. **Atomicity:** All changes save or none (transaction-style)
4. **Feedback:** Success/error messages to user
5. **Events:** Emit `CONFIG_UPDATED` for plugin hooks
6. **Rollback:** Restore original values on cancel or save failure

### Non-Goals (Future Enhancements)

- Config profiles (save/load named sets)
- Config diff view before save
- Config export/import
- Undo/redo history
- Real-time preview of terminal changes

---

## 3. Architecture Design

### 3.1 Component Interactions

```
┌─────────────────────────────────────────────────────────────┐
│                    User Actions                             │
│  - Edit widget values                                       │
│  - Press Ctrl+S (save)                                      │
│  - Press ESC (cancel)                                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│        ModalInteractionHandler                              │
│  - Detect save key                                          │
│  - Collect widget values via get_config_value()            │
│  - Validate all values                                      │
│  - Call ConfigManager.set_batch()                          │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│           ConfigManager                                     │
│  - Validate each value (type, range)                       │
│  - Backup current config                                    │
│  - Apply all changes atomically                            │
│  - Persist to .kollabor-cli/config.json                        │
│  - Rollback on any failure                                 │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              Event Bus                                      │
│  - Emit CONFIG_UPDATED event                               │
│  - Trigger plugin hooks                                     │
│  - Update status views                                      │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Save Operation Flow

```python
# 1. User presses Ctrl+S
ModalInteractionHandler.handle_keypress("Ctrl+S")

# 2. Collect all widget values
widget_values = {}
for widget in self.widgets:
    config_path, value = widget.get_config_value()
    widget_values[config_path] = value

# Example: {
#   "core.llm.temperature": 0.7,
#   "terminal.render_fps": 30,
#   "input.ctrl_c_exit": True
# }

# 3. Validate all values
validation_errors = self._validate_config_updates(widget_values)
if validation_errors:
    show_error("Validation failed: ...")
    return False

# 4. Save atomically
results = await self.config_manager.set_batch(widget_values)

# 5. Check for failures
if any(not success for success in results.values()):
    show_error("Save failed: ...")
    return False

# 6. Emit event
await event_bus.emit(EventType.CONFIG_UPDATED, {
    "updated_paths": list(widget_values.keys()),
    "values": widget_values
})

# 7. Close modal
self.close_modal()
show_success("Configuration saved")
```

---

## 4. Implementation Tasks

### Phase 1: Core Functionality (MVP)

#### Task 1.1: Widget Value Extraction
**Priority:** CRITICAL
**Files:**
- `core/ui/widgets/base_widget.py`
- `core/ui/widgets/checkbox.py`
- `core/ui/widgets/slider.py`
- `core/ui/widgets/dropdown.py`
- `core/ui/widgets/text_input.py`

**Implementation:**

```python
# base_widget.py
class BaseWidget:
    def get_config_value(self) -> Tuple[str, Any]:
        """Get config path and current value for persistence.

        Returns:
            Tuple of (config_path, current_value)
        """
        return (self.config_path, self.get_value())

    def get_value(self) -> Any:
        """Get current widget value - must be implemented by subclass."""
        raise NotImplementedError("Subclass must implement get_value()")

# checkbox.py
class CheckboxWidget(BaseWidget):
    def get_value(self) -> bool:
        return self.checked

# slider.py
class SliderWidget(BaseWidget):
    def get_value(self) -> Union[int, float]:
        return self.current_value

# dropdown.py
class DropdownWidget(BaseWidget):
    def get_value(self) -> str:
        return self.options[self.selected_index]

# text_input.py
class TextInputWidget(BaseWidget):
    def get_value(self) -> str:
        return self.text
```

**Testing:**
- Unit test each widget's `get_value()` method
- Verify `get_config_value()` returns correct tuple
- Test with various widget states (empty, default, modified)

---

#### Task 1.2: Modal Save Handler
**Priority:** CRITICAL
**File:** `core/ui/modal_interaction_handler.py`

**Implementation:**

```python
async def handle_keypress(self, key: str) -> bool:
    """Handle keyboard input in modal mode."""
    # Add save key detection
    if key == "ctrl+s":
        return await self._handle_save_action()

    # ... existing key handling ...

async def _handle_save_action(self) -> bool:
    """Save all widget values to configuration.

    Returns:
        True if save successful, False otherwise
    """
    try:
        # Collect all widget values
        updates = {}
        for widget in self.widgets:
            config_path, value = widget.get_config_value()
            updates[config_path] = value

        self.logger.debug(f"Saving {len(updates)} config values")

        # Validate before saving
        validation_errors = self._validate_config_updates(updates)
        if validation_errors:
            await self._show_error(f"Validation failed: {validation_errors}")
            return False

        # Save to config manager
        results = await self.config_manager.set_batch(updates)

        # Check for failures
        failures = [path for path, success in results.items() if not success]
        if failures:
            await self._show_error(f"Failed to save: {', '.join(failures)}")
            return False

        # Emit config updated event
        await self.event_bus.emit_with_hooks(
            EventType.CONFIG_UPDATED,
            {"updated_paths": list(updates.keys()), "values": updates},
            "config"
        )

        await self._show_success("Configuration saved successfully")
        self.logger.info(f"Config saved: {len(updates)} values updated")

        # Close modal after successful save
        await self._close_modal()
        return True

    except Exception as e:
        self.logger.error(f"Error saving config: {e}")
        await self._show_error(f"Save failed: {str(e)}")
        return False

def _validate_config_updates(self, updates: Dict[str, Any]) -> List[str]:
    """Validate config updates before saving.

    Args:
        updates: Dictionary of config_path -> value

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    for path, value in updates.items():
        # Type validation
        if "temperature" in path:
            if not isinstance(value, (int, float)):
                errors.append(f"{path}: must be numeric")
            elif not 0.0 <= value <= 2.0:
                errors.append(f"{path}: must be between 0.0 and 2.0")

        elif "fps" in path or "history" in path:
            if not isinstance(value, int):
                errors.append(f"{path}: must be integer")
            elif value < 1:
                errors.append(f"{path}: must be positive")

        elif "enabled" in path or "exit" in path:
            if not isinstance(value, bool):
                errors.append(f"{path}: must be boolean")

    return errors
```

**Testing:**
- Test save with valid values
- Test save with invalid values (validation failure)
- Test save with disk write error
- Test event emission after save
- Test modal closes after save

---

#### Task 1.3: Config Manager Batch Updates
**Priority:** CRITICAL
**File:** `core/config/manager.py`

**Implementation:**

```python
def set_batch(self, updates: Dict[str, Any]) -> Dict[str, bool]:
    """Set multiple config values with atomic transaction.

    All changes are applied atomically - if any value fails validation
    or saving, all changes are rolled back.

    Args:
        updates: Dictionary mapping config paths to values

    Returns:
        Dictionary mapping config paths to success status

    Raises:
        ConfigValidationError: If validation fails
        ConfigPersistenceError: If file write fails
    """
    if not updates:
        logger.debug("No updates to apply")
        return {}

    # Backup current config for rollback
    original_config = self.config.copy()
    logger.debug(f"Starting batch update of {len(updates)} values")

    try:
        # Phase 1: Validate all updates
        for path, value in updates.items():
            if not self._validate_config_value(path, value):
                logger.error(f"Validation failed for {path}: {value}")
                self.config = original_config  # Rollback
                return {p: False for p in updates.keys()}

        # Phase 2: Apply all updates to in-memory config
        for path, value in updates.items():
            success = safe_set(self.config, path, value)
            if not success:
                logger.error(f"Failed to set {path} in config dict")
                self.config = original_config  # Rollback
                return {p: False for p in updates.keys()}

        # Phase 3: Persist to disk (all or nothing)
        if not self.save_config_file(self.config):
            logger.error("Failed to persist config to disk")
            self.config = original_config  # Rollback
            return {p: False for p in updates.keys()}

        # Success!
        logger.info(f"Batch config update successful: {len(updates)} values")
        return {p: True for p in updates.keys()}

    except Exception as e:
        logger.error(f"Batch config update exception: {e}")
        self.config = original_config  # Rollback on any exception
        return {p: False for p in updates.keys()}

def _validate_config_value(self, path: str, value: Any) -> bool:
    """Validate a config value before setting.

    Args:
        path: Config path (dot notation)
        value: Value to validate

    Returns:
        True if valid, False otherwise
    """
    # Define validators for specific config paths
    validators = {
        "core.llm.temperature": lambda v: (
            isinstance(v, (int, float)) and 0.0 <= v <= 2.0
        ),
        "core.llm.max_history": lambda v: (
            isinstance(v, int) and v > 0 and v <= 1000
        ),
        "core.llm.max_tokens": lambda v: (
            isinstance(v, int) and v > 0
        ),
        "terminal.render_fps": lambda v: (
            isinstance(v, int) and 1 <= v <= 60
        ),
        "terminal.status_lines": lambda v: (
            isinstance(v, int) and 1 <= v <= 10
        ),
        "terminal.thinking_effect": lambda v: (
            isinstance(v, str) and v in ["shimmer", "pulse", "wave", "none"]
        ),
        "input.ctrl_c_exit": lambda v: isinstance(v, bool),
        "input.backspace_enabled": lambda v: isinstance(v, bool),
        "input.history_limit": lambda v: (
            isinstance(v, int) and 10 <= v <= 1000
        ),
    }

    # Check if we have a specific validator
    validator = validators.get(path)
    if validator:
        try:
            is_valid = validator(value)
            if not is_valid:
                logger.warning(f"Validation failed for {path}={value}")
            return is_valid
        except Exception as e:
            logger.error(f"Validator error for {path}: {e}")
            return False

    # No specific validator - accept any value with warning
    logger.debug(f"No validator for {path}, accepting value")
    return True
```

**Testing:**
- Test batch update with all valid values
- Test rollback on validation failure
- Test rollback on disk write failure
- Test transaction atomicity (all or nothing)
- Test with empty updates dict
- Test with partial failures

---

#### Task 1.4: Event System Integration
**Priority:** HIGH
**Files:**
- `core/events/models.py`
- Documentation update

**Implementation:**

```python
# core/events/models.py
class EventType(Enum):
    # ... existing events ...

    # Config events (add this section)
    CONFIG_UPDATED = "config_updated"
    CONFIG_VALIDATION_FAILED = "config_validation_failed"
    CONFIG_SAVE_FAILED = "config_save_failed"
```

**Event Data Schema:**

```python
# CONFIG_UPDATED event data
{
    "updated_paths": [
        "core.llm.temperature",
        "terminal.render_fps"
    ],
    "values": {
        "core.llm.temperature": 0.7,
        "terminal.render_fps": 30
    },
    "timestamp": datetime.now(),
    "source": "modal_config"  # or "api", "cli", etc.
}

# CONFIG_VALIDATION_FAILED event data
{
    "updates": {"core.llm.temperature": 5.0},
    "errors": ["core.llm.temperature: must be between 0.0 and 2.0"],
    "timestamp": datetime.now()
}

# CONFIG_SAVE_FAILED event data
{
    "updates": {...},
    "error": "Disk write failed: Permission denied",
    "timestamp": datetime.now()
}
```

**Plugin Hook Example:**

```python
# Example plugin that reacts to config changes
class MyPlugin:
    def register_hooks(self):
        self.event_bus.register_hook(
            name="my_plugin_config_update",
            plugin_name="my_plugin",
            event_type=EventType.CONFIG_UPDATED,
            priority=100,
            callback=self.on_config_updated
        )

    async def on_config_updated(self, event_data):
        """React to config changes."""
        if "core.llm.temperature" in event_data["updated_paths"]:
            new_temp = event_data["values"]["core.llm.temperature"]
            self.update_llm_temperature(new_temp)
```

---

### Phase 2: User Experience Enhancements

#### Task 2.1: User Feedback System
**Priority:** HIGH
**File:** `core/ui/modal_interaction_handler.py`

**Implementation:**

```python
async def _show_success(self, message: str) -> None:
    """Show success message to user.

    Args:
        message: Success message to display
    """
    # Option 1: Status line message
    await self.event_bus.emit_with_hooks(
        EventType.STATUS_CONTENT_UPDATE,
        {
            "area": "notification",
            "content": f"✓ {message}",
            "style": "success",
            "duration": 3  # seconds
        },
        "notifications"
    )

    # Option 2: Inline modal message
    self.notification_message = message
    self.notification_type = "success"
    await self._refresh_modal()

async def _show_error(self, message: str) -> None:
    """Show error message to user.

    Args:
        message: Error message to display
    """
    await self.event_bus.emit_with_hooks(
        EventType.STATUS_CONTENT_UPDATE,
        {
            "area": "notification",
            "content": f"✗ {message}",
            "style": "error",
            "duration": 5  # seconds
        },
        "notifications"
    )

    self.notification_message = message
    self.notification_type = "error"
    await self._refresh_modal()
```

---

#### Task 2.2: Unsaved Changes Detection
**Priority:** MEDIUM
**File:** `core/ui/modal_interaction_handler.py`

**Implementation:**

```python
class ModalInteractionHandler:
    def __init__(self, ...):
        # ... existing init ...
        self.original_values = {}  # Store original widget values
        self.has_unsaved_changes = False

    async def open_modal(self, ...):
        """Open modal and store original values."""
        # ... existing modal open logic ...

        # Store original values for change detection
        for widget in self.widgets:
            config_path, value = widget.get_config_value()
            self.original_values[config_path] = value

        self.has_unsaved_changes = False

    async def handle_keypress(self, key: str) -> bool:
        """Handle keyboard input with change detection."""
        # Detect changes on any widget modification
        if key in ["left", "right", "space", "enter", ...]:
            await self._check_for_changes()

        # Show confirmation on ESC if changes pending
        if key == "escape":
            if self.has_unsaved_changes:
                confirmed = await self._confirm_discard_changes()
                if not confirmed:
                    return True  # Don't close modal

            await self._close_modal()
            return True

        # ... rest of key handling ...

    async def _check_for_changes(self) -> None:
        """Check if any widget values have changed."""
        current_values = {}
        for widget in self.widgets:
            config_path, value = widget.get_config_value()
            current_values[config_path] = value

        # Compare with original values
        self.has_unsaved_changes = (
            current_values != self.original_values
        )

        # Update modal title to show unsaved indicator
        if self.has_unsaved_changes:
            self.modal_title = "System Configuration *"
        else:
            self.modal_title = "System Configuration"

        await self._refresh_modal()

    async def _confirm_discard_changes(self) -> bool:
        """Ask user to confirm discarding unsaved changes.

        Returns:
            True if user confirms, False otherwise
        """
        # Show confirmation dialog
        return await self._show_confirmation_dialog(
            title="Unsaved Changes",
            message="You have unsaved changes. Discard them?",
            options=["Discard", "Cancel"]
        )
```

---

#### Task 2.3: Inline Validation Feedback
**Priority:** MEDIUM
**Files:** Widget classes in `core/ui/widgets/`

**Implementation:**

```python
# base_widget.py
class BaseWidget:
    def __init__(self, ...):
        # ... existing init ...
        self.validation_error = None  # Error message or None
        self.is_valid = True

    def validate(self) -> bool:
        """Validate current widget value.

        Returns:
            True if valid, False otherwise
        """
        # Override in subclasses
        return True

    def render(self) -> List[str]:
        """Render widget with validation state."""
        lines = self._render_content()

        # Add red border or indicator if invalid
        if not self.is_valid and self.validation_error:
            lines = self._apply_error_style(lines)
            lines.append(f"  ✗ {self.validation_error}")

        return lines

# slider.py
class SliderWidget(BaseWidget):
    def validate(self) -> bool:
        """Validate slider value is in range."""
        if hasattr(self, 'min_value') and self.current_value < self.min_value:
            self.validation_error = f"Value must be >= {self.min_value}"
            self.is_valid = False
            return False

        if hasattr(self, 'max_value') and self.current_value > self.max_value:
            self.validation_error = f"Value must be <= {self.max_value}"
            self.is_valid = False
            return False

        self.validation_error = None
        self.is_valid = True
        return True
```

---

### Phase 3: Advanced Features (Future)

#### Task 3.1: Config Profiles
**Priority:** LOW
**Scope:** Save/load named configuration sets

**Design:**
- `/config save <profile_name>` - Save current config as named profile
- `/config load <profile_name>` - Load a saved profile
- `/config list` - List available profiles
- Profiles stored in `.kollabor-cli/profiles/`

---

#### Task 3.2: Config Diff View
**Priority:** LOW
**Scope:** Show what changed before saving

**Design:**
- Before save, show diff modal:
  ```
  Configuration Changes:

  core.llm.temperature: 0.5 → 0.7
  terminal.render_fps:  20  → 30

  Save these changes? [Yes] [No]
  ```

---

#### Task 3.3: Config Export/Import
**Priority:** LOW
**Scope:** Share configs between machines

**Design:**
- `/config export <file>` - Export config to JSON file
- `/config import <file>` - Import config from JSON file
- Support for partial imports (merge vs replace)

---

## 5. Testing Strategy

### 5.1 Unit Tests

**File:** `tests/test_config_command.py`

```python
import pytest
from core.config.manager import ConfigManager
from core.ui.widgets.slider import SliderWidget

class TestConfigManagerBatch:
    def test_set_batch_all_valid(self):
        """Test batch update with all valid values."""
        config_manager = ConfigManager(Path(".kollabor-cli/test_config.json"))

        updates = {
            "core.llm.temperature": 0.7,
            "terminal.render_fps": 30
        }

        results = config_manager.set_batch(updates)

        assert all(results.values())
        assert config_manager.get("core.llm.temperature") == 0.7
        assert config_manager.get("terminal.render_fps") == 30

    def test_set_batch_validation_failure(self):
        """Test rollback on validation failure."""
        config_manager = ConfigManager(Path(".kollabor-cli/test_config.json"))

        # Store original value
        original_temp = config_manager.get("core.llm.temperature")

        updates = {
            "core.llm.temperature": 5.0,  # Invalid: > 2.0
            "terminal.render_fps": 30
        }

        results = config_manager.set_batch(updates)

        # All should fail due to atomic transaction
        assert all(not success for success in results.values())

        # Original value should be preserved
        assert config_manager.get("core.llm.temperature") == original_temp

    def test_set_batch_rollback_on_disk_error(self):
        """Test rollback when disk write fails."""
        # Mock save_config_file to fail
        # Verify config rolled back to original state

class TestWidgetValueExtraction:
    def test_checkbox_get_config_value(self):
        """Test checkbox returns correct config value."""
        widget = CheckboxWidget(
            label="Enable LLM",
            config_path="core.llm.enabled",
            checked=True
        )

        config_path, value = widget.get_config_value()

        assert config_path == "core.llm.enabled"
        assert value is True

    def test_slider_get_config_value(self):
        """Test slider returns correct config value."""
        widget = SliderWidget(
            label="Temperature",
            config_path="core.llm.temperature",
            current_value=0.7,
            min_value=0.0,
            max_value=2.0
        )

        config_path, value = widget.get_config_value()

        assert config_path == "core.llm.temperature"
        assert value == 0.7

class TestModalSaveHandler:
    async def test_save_valid_values(self):
        """Test modal save with valid widget values."""
        # Create modal with widgets
        # Modify widget values
        # Call _handle_save_action()
        # Verify config updated
        # Verify event emitted

    async def test_save_invalid_values(self):
        """Test modal save with invalid values."""
        # Create modal with widgets
        # Set invalid widget value
        # Call _handle_save_action()
        # Verify save failed
        # Verify error message shown
        # Verify config unchanged
```

---

### 5.2 Integration Tests

**File:** `tests/integration/test_config_command_integration.py`

```python
class TestConfigCommandIntegration:
    async def test_full_config_save_flow(self):
        """Test complete flow: modal → widgets → config → disk."""
        # 1. Execute /config command
        # 2. Modify widget values
        # 3. Press Ctrl+S
        # 4. Verify .kollabor-cli/config.json updated
        # 5. Verify CONFIG_UPDATED event emitted
        # 6. Verify modal closed

    async def test_config_persistence_across_restart(self):
        """Test config changes persist after app restart."""
        # 1. Change config via modal
        # 2. Save config
        # 3. Restart app (reload config from disk)
        # 4. Verify changes persisted

    async def test_config_change_event_propagation(self):
        """Test CONFIG_UPDATED event reaches plugin hooks."""
        # 1. Register plugin hook for CONFIG_UPDATED
        # 2. Change config via modal
        # 3. Save config
        # 4. Verify hook was called with correct data
```

---

### 5.3 Manual Testing Checklist

**Happy Path:**
- [ ] Open `/config`, see current values loaded
- [ ] Change slider value, see value update in widget
- [ ] Change checkbox, see checked state toggle
- [ ] Change dropdown, see selected option update
- [ ] Edit text input, see text update
- [ ] Press Ctrl+S, see success message
- [ ] Verify `.kollabor-cli/config.json` updated on disk
- [ ] Close and reopen modal, see saved values

**Validation:**
- [ ] Set temperature to 5.0, press Ctrl+S, see validation error
- [ ] Set FPS to -1, press Ctrl+S, see validation error
- [ ] Set invalid integer in text input, see validation error
- [ ] Fix validation error, press Ctrl+S, see success

**Error Handling:**
- [ ] Simulate disk full, press Ctrl+S, see error + rollback
- [ ] Simulate permission denied, see error + rollback
- [ ] Corrupt config JSON file, see graceful handling

**Unsaved Changes:**
- [ ] Change value, press ESC, see "unsaved changes" confirmation
- [ ] Confirm discard, see modal close without saving
- [ ] Change value, see `*` in modal title
- [ ] Press Ctrl+S, see `*` disappear

---

## 6. Edge Cases & Error Handling

| Scenario | Current Behavior | Required Behavior |
|----------|------------------|-------------------|
| Config file doesn't exist | Modal opens, no values | Create file on first save |
| Invalid JSON in config | App may crash | Show error, use defaults |
| Concurrent modifications | Race condition | File locking or last-write-wins |
| Widget validation fails | No validation | Show inline error, prevent save |
| Disk full during save | Partial write | Detect failure, rollback, notify |
| Invalid integer in text | String saved | Validate + reject before save |
| Config path doesn't exist | N/A | Create nested structure (safe_set) |
| Network drive disconnected | Hang or crash | Timeout + error message |
| Very large config file | Slow load | Warn if > 1MB |
| Unicode in config values | May break | Handle UTF-8 correctly |

---

## 7. File Modifications Summary

### Files to Create
- `tests/test_config_command.py` - Unit tests
- `tests/integration/test_config_command_integration.py` - Integration tests

### Files to Modify

| File | Changes | Lines Changed (est.) |
|------|---------|---------------------|
| `core/ui/widgets/base_widget.py` | Add `get_config_value()`, `get_value()` | +15 |
| `core/ui/widgets/checkbox.py` | Implement `get_value()` | +5 |
| `core/ui/widgets/slider.py` | Implement `get_value()` | +5 |
| `core/ui/widgets/dropdown.py` | Implement `get_value()` | +5 |
| `core/ui/widgets/text_input.py` | Implement `get_value()` | +5 |
| `core/ui/modal_interaction_handler.py` | Add save handler, validation, feedback | +150 |
| `core/config/manager.py` | Add `set_batch()`, validation | +100 |
| `core/events/models.py` | Add CONFIG_UPDATED event | +5 |

**Total estimated changes:** ~290 lines

---

## 8. Implementation Timeline

### Phase 1 (MVP) - 1 day
- Widget value extraction (2 hours)
- Modal save handler (3 hours)
- Config manager batch updates (2 hours)
- Basic testing (1 hour)

### Phase 2 (Polish) - 1 day
- Event integration (1 hour)
- User feedback system (2 hours)
- Unsaved changes detection (2 hours)
- Inline validation (2 hours)
- Comprehensive testing (1 hour)

### Phase 3 (Advanced) - Future
- Config profiles (TBD)
- Diff view (TBD)
- Export/import (TBD)

**Total for MVP + Polish:** 2 days

---

## 9. Success Criteria

### Functional Requirements
- [ ] Ctrl+S saves all widget values to config file
- [ ] Invalid values show validation errors
- [ ] Save failures show error messages and rollback
- [ ] CONFIG_UPDATED event emitted on successful save
- [ ] Unsaved changes show confirmation on ESC
- [ ] All config paths from widgets persist correctly

### Non-Functional Requirements
- [ ] Save operation completes in < 100ms (normal case)
- [ ] Rollback on failure is atomic (all or nothing)
- [ ] No data loss on partial failures
- [ ] Clear error messages for all failure modes
- [ ] User can recover from all error states

### Code Quality
- [ ] 90%+ test coverage for new code
- [ ] All edge cases documented and handled
- [ ] Logging for all operations (debug, info, error)
- [ ] No breaking changes to existing APIs

---

## 10. Future Enhancements

### Config Validation Schema
Define JSON schema for config validation:
```python
CONFIG_SCHEMA = {
    "core.llm.temperature": {
        "type": "float",
        "min": 0.0,
        "max": 2.0,
        "default": 0.7
    },
    "terminal.render_fps": {
        "type": "int",
        "min": 1,
        "max": 60,
        "default": 30
    },
    # ... etc
}
```

### Config Migration System
Handle config version upgrades:
- Old configs automatically migrated to new schema
- Deprecated config paths logged with warnings
- Default values for new config paths

### Real-time Config Preview
For visual changes (colors, animations):
- Show preview in status area before saving
- Allow toggle between current/preview
- "Apply" button in addition to "Save"

---

## 11. API Reference

### ConfigManager.set_batch()

```python
def set_batch(self, updates: Dict[str, Any]) -> Dict[str, bool]:
    """Set multiple config values atomically.

    All changes are applied as a transaction - if any value fails
    validation or saving, all changes are rolled back to the
    original state.

    Args:
        updates: Dictionary mapping config paths to values.
                 Example: {
                     "core.llm.temperature": 0.7,
                     "terminal.render_fps": 30
                 }

    Returns:
        Dictionary mapping config paths to success status.
        Example: {
            "core.llm.temperature": True,
            "terminal.render_fps": True
        }

        If any value fails, all values will be False.

    Raises:
        ConfigValidationError: If a value fails validation.
        ConfigPersistenceError: If writing to disk fails.

    Example:
        >>> config_manager = ConfigManager(Path(".kollabor-cli/config.json"))
        >>> results = config_manager.set_batch({
        ...     "core.llm.temperature": 0.7,
        ...     "terminal.render_fps": 30
        ... })
        >>> assert all(results.values())  # All succeeded
    """
```

### BaseWidget.get_config_value()

```python
def get_config_value(self) -> Tuple[str, Any]:
    """Get the config path and current value for persistence.

    Returns:
        Tuple of (config_path, current_value).
        Example: ("core.llm.temperature", 0.7)

    Example:
        >>> widget = SliderWidget(
        ...     label="Temperature",
        ...     config_path="core.llm.temperature",
        ...     current_value=0.7
        ... )
        >>> path, value = widget.get_config_value()
        >>> assert path == "core.llm.temperature"
        >>> assert value == 0.7
    """
```

### CONFIG_UPDATED Event

```python
EventType.CONFIG_UPDATED

Event Data Schema:
{
    "updated_paths": List[str],  # Config paths that changed
    "values": Dict[str, Any],    # New values for each path
    "timestamp": datetime,       # When change occurred
    "source": str                # Where change originated ("modal", "api", etc.)
}

Example:
{
    "updated_paths": ["core.llm.temperature", "terminal.render_fps"],
    "values": {
        "core.llm.temperature": 0.7,
        "terminal.render_fps": 30
    },
    "timestamp": datetime(2025, 11, 7, 15, 30, 0),
    "source": "modal_config"
}
```

---

## 12. References

### Related Documentation
- [Modal System Implementation Guide](modal-system-implementation-guide.md)
- [Config Widget Definitions](../core/ui/config_widgets.py)
- [Hook System SDK](reference/hook-system-sdk.md)
- [Architecture Overview](reference/architecture-overview.md)

### Related Code
- Command system: `core/commands/`
- Modal system: `core/ui/modal_*.py`
- Config management: `core/config/manager.py`
- Event system: `core/events/`
- Widget implementations: `core/ui/widgets/`

---

## Appendix A: Current Config Schema

**File:** `.kollabor-cli/config.json`

```json
{
  "core": {
    "llm": {
      "api_url": "http://localhost:1234",
      "model": "qwen/qwen3-4b",
      "temperature": 0.7,
      "max_history": 90,
      "max_tokens": 4096,
      "enabled": true
    }
  },
  "terminal": {
    "render_fps": 30,
    "status_lines": 3,
    "thinking_effect": "shimmer",
    "shimmer_speed": 5
  },
  "input": {
    "ctrl_c_exit": true,
    "backspace_enabled": true,
    "history_limit": 100
  },
  "application": {
    "name": "Kollabor CLI",
    "version": "1.0.0"
  }
}
```

---

## Appendix B: Widget-to-Config Mapping

| Widget Type | Config Path | Data Type | Validation |
|-------------|-------------|-----------|------------|
| Checkbox | `core.llm.enabled` | bool | - |
| Slider | `core.llm.temperature` | float | 0.0 - 2.0 |
| Dropdown | `core.llm.model` | str | Enum |
| TextInput | `core.llm.max_tokens` | int | > 0 |
| Slider | `terminal.render_fps` | int | 1 - 60 |
| Slider | `terminal.status_lines` | int | 1 - 10 |
| Dropdown | `terminal.thinking_effect` | str | Enum |
| Checkbox | `input.ctrl_c_exit` | bool | - |
| Slider | `input.history_limit` | int | 10 - 1000 |

---

## Document History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-11-07 | 1.0 | Claude Code | Initial specification |

---

**END OF SPECIFICATION**
