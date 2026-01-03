"""Example full-screen plugin demonstrating framework capabilities."""

import asyncio
import math
from core.fullscreen import FullScreenPlugin
from core.fullscreen.plugin import PluginMetadata
from core.fullscreen.components.drawing import DrawingPrimitives
from core.fullscreen.components.animation import AnimationFramework, EasingFunctions
from core.io.visual_effects import ColorPalette
from core.io.key_parser import KeyPress


class ExamplePlugin(FullScreenPlugin):
    """Example plugin showcasing full-screen framework features.

    This plugin demonstrates:
    - Drawing primitives (text, borders, shapes)
    - Animation framework (fade, slide, bounce)
    - Input handling
    - Multi-page layouts
    """

    def __init__(self):
        """Initialize the example plugin."""
        metadata = PluginMetadata(
            name="example",
            description="Example plugin showcasing framework features",
            version="1.0.0",
            author="Framework",
            category="demo",
            icon="🎯",
            aliases=[]
        )
        super().__init__(metadata)

        # Plugin state
        self.current_page = 0
        self.total_pages = 4
        self.animation_framework = AnimationFramework()
        self.page_transition_id = None
        self.demo_animations = {}
        self.frame_count = 0

    async def initialize(self, renderer) -> bool:
        """Initialize the example plugin."""
        print("🔍 CRITICAL: ExamplePlugin.initialize() called")
        try:
            if not await super().initialize(renderer):
                print("❌ CRITICAL: super().initialize() failed")
                return False

            # Setup initial animations
            current_time = asyncio.get_event_loop().time()
            self.demo_animations['title_fade'] = self.animation_framework.fade_in(2.0, current_time)
            self.demo_animations['bounce'] = self.animation_framework.bounce_in(1.5, current_time + 0.5)

            print("✅ CRITICAL: ExamplePlugin.initialize() completed successfully")
            return True
        except Exception as e:
            print(f"❌ CRITICAL: Exception in initialize(): {e}")
            import traceback
            traceback.print_exc()
            return False

    async def on_start(self):
        """Called when Example plugin starts."""
        await super().on_start()

    async def render_frame(self, delta_time: float) -> bool:
        """Render the example plugin frame."""
        if not self.renderer:
            return False

        # Increment frame counter for animations
        self.frame_count += 1

        # Clear screen and show content
        self.renderer.clear_screen()
        width, height = self.renderer.get_terminal_size()

        # Render current page
        if self.current_page == 0:
            self._render_welcome_page(width, height)
        elif self.current_page == 1:
            self._render_drawing_demo(width, height)
        elif self.current_page == 2:
            self._render_animation_demo(width, height)
        elif self.current_page == 3:
            self._render_final_page(width, height)

        # Show navigation instructions
        nav_text = f"Page {self.current_page + 1}/{self.total_pages} • ←→ or h/l navigate • 1-4 direct • q/ESC exit"
        nav_x = (width - len(nav_text)) // 2
        self.renderer.write_at(nav_x, height - 1, nav_text, "\033[37m")

        # Flush output
        self.renderer.flush()
        return True

    def _render_welcome_page(self, width: int, height: int):
        """Render the welcome page."""
        # Animated title
        title_alpha = self.animation_framework.get_value(self.demo_animations.get('title_fade', 0))
        if title_alpha > 0.5:  # Show when fade is mostly complete
            DrawingPrimitives.draw_text_centered(
                self.renderer, height // 4,
                "🎯 Full-Screen Framework Demo",
                ColorPalette.BRIGHT_CYAN
            )

        # Bouncing subtitle
        bounce_offset = int(self.animation_framework.get_value(self.demo_animations.get('bounce', 0)) * 3)
        DrawingPrimitives.draw_text_centered(
            self.renderer, height // 2 - bounce_offset,
            "Welcome to the Plugin Framework!",
            ColorPalette.BRIGHT_GREEN
        )

        # Static content
        DrawingPrimitives.draw_text_centered(
            self.renderer, height // 2 + 2,
            "This framework provides:",
            ColorPalette.WHITE
        )

        features = [
            "• Complete terminal takeover",
            "• Modal system integration",
            "• Drawing primitives & animations",
            "• Plugin lifecycle management",
            "• Input handling & routing"
        ]

        for i, feature in enumerate(features):
            DrawingPrimitives.draw_text_centered(
                self.renderer, height // 2 + 4 + i,
                feature,
                ColorPalette.YELLOW
            )

    def _render_drawing_demo(self, width: int, height: int):
        """Render drawing primitives demonstration."""
        DrawingPrimitives.draw_text_centered(
            self.renderer, 2,
            "Drawing Primitives Demo",
            ColorPalette.BRIGHT_MAGENTA
        )

        # Draw various shapes and elements
        center_x, center_y = width // 2, height // 2

        # Border around demo area
        DrawingPrimitives.draw_border(
            self.renderer, center_x - 20, center_y - 8, 40, 16,
            color=ColorPalette.CYAN
        )

        # Progress bar
        progress = (self.frame_count % 100) / 100.0
        DrawingPrimitives.draw_progress_bar(
            self.renderer, center_x - 15, center_y - 5, 30, progress,
            color=ColorPalette.GREEN
        )
        DrawingPrimitives.draw_text_centered(
            self.renderer, center_y - 6,
            f"Progress: {progress:.0%}",
            ColorPalette.WHITE
        )

        # Spinner
        DrawingPrimitives.draw_spinner(
            self.renderer, center_x - 2, center_y - 2, self.frame_count // 5,
            color=ColorPalette.BRIGHT_BLUE
        )
        self.renderer.write_at(center_x + 2, center_y - 2, "Loading...", ColorPalette.WHITE)

        # Circle points
        radius = 8
        DrawingPrimitives.draw_circle_points(
            self.renderer, center_x, center_y + 3, radius,
            char="●", color=ColorPalette.RED
        )

        # Wave
        wave_phase = self.frame_count * 0.1
        DrawingPrimitives.draw_wave(
            self.renderer, height - 5, 2, 0.3, wave_phase,
            char="~", color=ColorPalette.BLUE
        )

    def _render_animation_demo(self, width: int, height: int):
        """Render animation framework demonstration."""
        DrawingPrimitives.draw_text_centered(
            self.renderer, 2,
            "Animation Framework Demo",
            ColorPalette.BRIGHT_YELLOW
        )

        center_x, center_y = width // 2, height // 2

        # Create cycling animations
        current_time = asyncio.get_event_loop().time()

        # Pulsing circle
        pulse_size = 5 + int(3 * math.sin(current_time * 2))
        for r in range(1, pulse_size):
            DrawingPrimitives.draw_circle_points(
                self.renderer, center_x, center_y, r,
                char="○", color=ColorPalette.GREEN
            )

        # Sliding text
        slide_x = int(20 * math.sin(current_time))
        self.renderer.write_at(center_x + slide_x, center_y - 5, "← Sliding Text →", ColorPalette.CYAN)

        # Fading elements
        fade_alpha = (math.sin(current_time * 1.5) + 1) / 2
        if fade_alpha > 0.3:  # Only show when bright enough
            intensity = "▓" if fade_alpha > 0.7 else "░"
            fade_text = f"Fading {intensity}"
            DrawingPrimitives.draw_text_centered(
                self.renderer, center_y + 3,
                fade_text,
                ColorPalette.MAGENTA
            )

        # Bouncing ball
        bounce_y = center_y + 6 + int(3 * abs(math.sin(current_time * 3)))
        self.renderer.write_at(center_x, bounce_y, "●", ColorPalette.RED)

    def _render_final_page(self, width: int, height: int):
        """Render the final page with improved layout."""
        # Title at top
        DrawingPrimitives.draw_text_centered(
            self.renderer, 3,
            "🚀 Ready to Build Plugins!",
            ColorPalette.BRIGHT_GREEN
        )

        # Plugin template example - more compact positioning
        code_lines = [
            "class MyPlugin(FullScreenPlugin):",
            "    async def render_frame(self, delta_time):",
            "        self.renderer.clear_screen()",
            "        # Your awesome content here!",
            "        return True",
            "",
            "    async def handle_input(self, key_press):",
            "        return key_press.char == 'q'"
        ]

        # Position code in upper middle area
        start_y = 6
        for i, line in enumerate(code_lines):
            x = max(0, (width - len(line)) // 2)
            self.renderer.write_at(x, start_y + i, line, ColorPalette.YELLOW)

        # Features section positioned below code
        features_start_y = start_y + len(code_lines) + 2
        DrawingPrimitives.draw_text_centered(
            self.renderer, features_start_y,
            "Framework Features Available:",
            ColorPalette.WHITE
        )

        features = [
            "✓ Modal system integration",
            "✓ Terminal state management",
            "✓ Drawing primitives library",
            "✓ Animation framework",
            "✓ Input handling system"
        ]

        for i, feature in enumerate(features):
            DrawingPrimitives.draw_text_centered(
                self.renderer, features_start_y + 2 + i,
                feature,
                ColorPalette.BRIGHT_CYAN
            )

    def _render_navigation(self, width: int, height: int):
        """Render navigation controls."""
        nav_text = f"Page {self.current_page + 1}/{self.total_pages} • ←→ Navigate • Q/ESC Exit"
        DrawingPrimitives.draw_text_centered(
            self.renderer, height - 2,
            nav_text,
            ColorPalette.DIM_WHITE
        )

    async def handle_input(self, key_press: KeyPress) -> bool:
        """Handle input for the example plugin."""
        # Exit on 'q' or ESC
        if key_press.char in ['q', '\x1b'] or key_press.name == "Escape":
            return True

        # Navigation with multiple options
        if key_press.char == 'h' or key_press.char == 'a' or key_press.name == "ArrowLeft":
            if self.current_page > 0:
                self.current_page -= 1
                await self._start_page_transition()
        elif key_press.char == 'l' or key_press.char == 'd' or key_press.name == "ArrowRight":
            if self.current_page < self.total_pages - 1:
                self.current_page += 1
                await self._start_page_transition()
        elif key_press.char in ['1', '2', '3', '4']:  # Direct page navigation
            new_page = int(key_press.char) - 1
            if 0 <= new_page < self.total_pages:
                self.current_page = new_page
                await self._start_page_transition()

        return False

    async def _start_page_transition(self):
        """Start page transition animation."""
        current_time = asyncio.get_event_loop().time()
        # Could add page transition animations here
        # For now, just reset some demo animations
        self.demo_animations['bounce'] = self.animation_framework.bounce_in(0.5, current_time)

    async def on_stop(self):
        """Called when Example plugin stops."""
        await super().on_stop()

    async def cleanup(self):
        """Clean up example plugin resources."""
        self.animation_framework.clear_all()
        await super().cleanup()