# Modal System: Gap-Filling Implementation

## 🎯 What Actually Exists vs. What We Need

### ✅ **Rich Infrastructure Already Available**

#### Visual Effects System (`core/io/visual_effects.py`)
```python
# EXISTING - Can be leveraged immediately
class GradientRenderer:          # For modal borders and text
class BannerRenderer:            # For modal headers
class ColorPalette:              # For consistent modal colors
class EffectConfig:              # For modal animations

# Available effects we can use:
- Gradient rendering (for modal borders)
- Color palettes (DIM_CYAN, DIM_YELLOW for modal styling)
- Effect configurations (for modal entrance animations)
```

#### Terminal Renderer (`core/io/terminal_renderer.py`)
```python
# EXISTING - Ready for modal integration
def clear_active_area():         # Perfect for modal overlay clearing
def render_active_area():        # Can be extended for modal rendering
def _render_lines():             # Core rendering we can use for modals
```

#### Input Handler (`core/io/input_handler.py`)
```python
# EXISTING - Already has mode infrastructure
self.command_mode = CommandMode.NORMAL/MENU_POPUP/STATUS_TAKEOVER
# We just need to add: CommandMode.MODAL

# EXISTING - Input handling patterns we can follow
async def _handle_command_mode_keypress(key_press):  # Extend for modal
async def _handle_menu_popup_keypress(key_press):    # Template for modal input
```

#### Configuration System (`core/config/`)
```python
# EXISTING - Ready to use
def get_config_value(path):      # For reading widget values
def set_config_value(path, val): # For saving widget changes
```

### ❌ **Actual Missing Pieces (Need to Build)**

## 🔧 Gap-Filling Implementation

### Gap 1: Add MODAL CommandMode

#### Extend Existing Enum
```python
# In core/events/models.py - ADD ONE LINE
class CommandMode(Enum):
    NORMAL = "normal"
    INSTANT = "instant"
    MENU_POPUP = "menu_popup"
    STATUS_TAKEOVER = "status_takeover"
    INLINE_INPUT = "inline_input"
    MODAL = "modal"                    # ← ADD THIS
```

### Gap 2: Create Minimal ModalRenderer

#### File: `core/ui/__init__.py`
```python
"""UI components for modal system."""
```

#### File: `core/ui/modal_renderer.py`
```python
"""Modal rendering system leveraging existing visual effects."""

import asyncio
from typing import List, Dict, Any
from ..io.visual_effects import ColorPalette, GradientRenderer
from ..events.models import UIConfig


class ModalRenderer:
    """Modal overlay renderer using existing terminal infrastructure."""

    def __init__(self, terminal_renderer, visual_effects):
        self.terminal_renderer = terminal_renderer
        self.visual_effects = visual_effects
        self.gradient_renderer = GradientRenderer()

    async def show_modal(self, ui_config: UIConfig) -> Dict[str, Any]:
        """Show modal using existing rendering infrastructure."""

        # Use existing clear_active_area
        self.terminal_renderer.clear_active_area()

        # Render modal using existing _render_lines infrastructure
        modal_lines = self._render_modal_box(ui_config)

        # Use existing animation capabilities
        await self._animate_entrance(modal_lines)

        # Handle input using existing input patterns
        return await self._handle_modal_input(ui_config)

    def _render_modal_box(self, ui_config: UIConfig) -> List[str]:
        """Render modal box using existing visual effects."""
        width = int(ui_config.width or 80)  # 80% of terminal width
        title = ui_config.title or "Modal"

        lines = []

        # Top border using existing color palette
        border_color = ColorPalette.DIM_CYAN
        lines.append(f"{border_color}╭{'─' * (width-2)}╮{ColorPalette.RESET}")

        # Title line using existing gradient renderer
        title_line = f"│{title.center(width-2)}│"
        lines.append(f"{border_color}{title_line}{ColorPalette.RESET}")

        # Separator
        lines.append(f"{border_color}├{'─' * (width-2)}┤{ColorPalette.RESET}")

        # Content area (widgets will go here in Phase 2)
        modal_config = ui_config.modal_config or {}
        content_lines = self._render_modal_content(modal_config, width)
        lines.extend(content_lines)

        # Bottom border
        lines.append(f"{border_color}╰{'─' * (width-2)}╯{ColorPalette.RESET}")

        # Footer using existing color palette
        footer = "Enter to select • Esc to close"
        lines.append(f"{ColorPalette.DIM_YELLOW}{footer.center(width)}{ColorPalette.RESET}")

        return lines

    def _render_modal_content(self, modal_config: Dict, width: int) -> List[str]:
        """Render modal content - placeholder for widget system."""
        lines = []
        border_color = ColorPalette.DIM_CYAN

        # Phase 1: Simple content display
        sections = modal_config.get("sections", [{"title": "Configuration", "content": "Coming soon..."}])

        for section in sections:
            section_title = section.get("title", "Section")
            lines.append(f"{border_color}│{ColorPalette.BRIGHT}  {section_title}{ColorPalette.RESET}{border_color}{' ' * (width - len(section_title) - 5)}│{ColorPalette.RESET}")
            lines.append(f"{border_color}│{' ' * (width-2)}│{ColorPalette.RESET}")

            # Phase 1: Show simple content
            content = section.get("content", "No content")
            content_line = f"    {content}"
            padding = width - len(content_line) - 2
            lines.append(f"{border_color}│{content_line}{' ' * padding}│{ColorPalette.RESET}")
            lines.append(f"{border_color}│{' ' * (width-2)}│{ColorPalette.RESET}")

        return lines

    async def _animate_entrance(self, lines: List[str]):
        """Animate modal entrance using existing visual effects."""
        # Phase 1: Simple fade-in using existing dim effects
        for opacity in [0.3, 0.6, 1.0]:
            if opacity < 1.0:
                # Apply dim effect using existing ColorPalette
                dimmed_lines = [f"{ColorPalette.DIM}{line}{ColorPalette.RESET}" for line in lines]
                await self._render_modal_lines(dimmed_lines)
            else:
                await self._render_modal_lines(lines)
            await asyncio.sleep(0.1)

    async def _render_modal_lines(self, lines: List[str]):
        """Render modal lines using existing terminal infrastructure."""
        # Use existing terminal renderer method
        for line in lines:
            self.terminal_renderer._write(f"\n{line}")
        self.terminal_renderer._write("\n")

    async def _handle_modal_input(self, ui_config: UIConfig) -> Dict[str, Any]:
        """Handle modal input using existing input handler patterns."""
        # Phase 1: Simple Esc to close
        # This will be integrated with existing input_handler in next step
        return {"action": "close", "changes": {}}
```

### Gap 3: Integrate Modal Mode into Input Handler

#### Extend Existing Input Handler (`core/io/input_handler.py`)
```python
# ADD to _handle_command_mode_keypress method around line 890
elif self.command_mode == CommandMode.MODAL:
    return await self._handle_modal_keypress(key_press)

# ADD new method to input_handler.py
async def _handle_modal_keypress(self, key_press: KeyPress) -> bool:
    """Handle KeyPress during modal mode."""
    try:
        if key_press.name == "Escape":
            await self._exit_modal_mode()
            return True
        elif key_press.name == "Enter":
            # Phase 1: Just close modal
            await self._exit_modal_mode()
            return True
        # Phase 2: Add widget navigation here
        return True
    except Exception as e:
        logger.error(f"Error handling modal keypress: {e}")
        await self._exit_modal_mode()
        return False

async def _enter_modal_mode(self, ui_config: UIConfig):
    """Enter modal mode with given UI config."""
    self.command_mode = CommandMode.MODAL
    self.current_modal_config = ui_config

    # Create modal renderer using existing infrastructure
    from ..ui.modal_renderer import ModalRenderer
    modal_renderer = ModalRenderer(self.terminal_renderer, self.terminal_renderer.visual_effects)

    # Show modal
    result = await modal_renderer.show_modal(ui_config)

    # Handle result (Phase 3: Save config changes)
    if result.get("action") == "save":
        # TODO: Apply config changes
        pass

async def _exit_modal_mode(self):
    """Exit modal mode and return to normal input."""
    self.command_mode = CommandMode.NORMAL
    self.current_modal_config = None
    await self._update_display()
```

### Gap 4: Modify Command Executor to Support Modals

#### Extend Existing Executor (`core/commands/executor.py`)
```python
# ADD to execute_command method after status_ui handling
if result.ui_config and result.ui_config.type == "modal":
    # Trigger modal mode in input handler
    await self._trigger_modal_mode(result.ui_config)

async def _trigger_modal_mode(self, ui_config: UIConfig):
    """Trigger modal mode through event bus."""
    await self.event_bus.emit_with_hooks(
        EventType.COMMAND_MODAL_OPEN,
        {"ui_config": ui_config},
        "command_executor"
    )
```

### Gap 5: Update System Commands to Use Modals

#### Modify Existing `/config` Command (`core/commands/system_commands.py`)
```python
# REPLACE existing handle_config method
async def handle_config(self, command: SlashCommand) -> CommandResult:
    """Handle /config command with modal UI."""
    try:
        return CommandResult(
            success=True,
            message="Configuration modal opened",
            ui_config=UIConfig(
                type="modal",
                title="System Configuration",
                width=80,
                height=20,
                modal_config={
                    "sections": [
                        {
                            "title": "LLM Settings",
                            "content": "Temperature, Model, API URL (widgets coming in Phase 2)"
                        },
                        {
                            "title": "Terminal Settings",
                            "content": "Colors, Effects, Status Lines (widgets coming in Phase 2)"
                        }
                    ]
                }
            ),
            display_type="modal"
        )
    except Exception as e:
        self.logger.error(f"Error in config command: {e}")
        return CommandResult(
            success=False,
            message=f"Error opening configuration: {str(e)}",
            display_type="error"
        )
```

## 🚀 Implementation Sequence

### Phase 1A: Basic Modal Infrastructure (Day 1)
1. Create `core/ui/` directory
2. Add `CommandMode.MODAL` to enum
3. Create basic `ModalRenderer` class using existing visual effects
4. Test with simple modal box

### Phase 1B: Input Integration (Day 2)
1. Add modal keypress handling to existing input handler
2. Integrate modal mode with existing command mode system
3. Test Esc key closing modal

### Phase 1C: Command Integration (Day 3)
1. Modify command executor to detect modal UI configs
2. Update `/config` command to return modal UI config
3. Test complete flow: `/config` → modal opens → Esc closes

### Phase 1D: Visual Polish (Day 4)
1. Use existing gradient renderer for modal borders
2. Add fade-in animation using existing visual effects
3. Center modal on screen using existing terminal utilities

## 🎯 Success Criteria for Phase 1

- [ ] `/config` opens a modal box instead of status takeover
- [ ] Modal uses existing visual effects (colors, gradients)
- [ ] Modal responds to Esc key (closes and returns to normal input)
- [ ] Modal is centered and 80% width
- [ ] Background chat is still visible (dimmed)

## 📁 Minimal File Structure

```
core/
├── ui/                    # NEW - minimal gap filling
│   ├── __init__.py       # NEW
│   └── modal_renderer.py # NEW - uses existing visual_effects
├── events/
│   └── models.py         # MODIFY - add CommandMode.MODAL
├── io/
│   └── input_handler.py  # MODIFY - add modal keypress handling
└── commands/
    ├── executor.py       # MODIFY - detect modal UI configs
    └── system_commands.py # MODIFY - /config returns modal UI config
```

This approach fills only the actual gaps while maximizing use of your existing rich infrastructure!