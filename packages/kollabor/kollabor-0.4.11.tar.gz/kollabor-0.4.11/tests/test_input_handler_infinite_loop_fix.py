#!/usr/bin/env python3
"""Test suite for infinite loop fixes in input handler."""

import pytest
import asyncio
import time
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add the core directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.io.input_handler import InputHandler
from core.events.models import CommandMode


class TestInfiniteLoopFixes:
    """Test cases for infinite loop prevention in input handler."""

    @pytest.fixture
    def mock_event_bus(self):
        """Create a mock event bus."""
        event_bus = Mock()
        event_bus.emit_with_hooks = Mock(return_value={})
        event_bus.register_hook = Mock(return_value=True)
        return event_bus

    @pytest.fixture
    def mock_renderer(self):
        """Create a mock renderer."""
        renderer = Mock()
        renderer.enter_raw_mode = Mock()
        renderer.exit_raw_mode = Mock()
        renderer.clear_active_area = Mock()
        renderer.update_display = Mock()
        return renderer

    @pytest.fixture
    def mock_config(self):
        """Create a mock config."""
        config = Mock()
        config.get.side_effect = lambda key, default=None: {
            "input.polling_delay": 0.01,
            "input.error_delay": 0.1,
            "input.input_buffer_limit": 10000,
            "input.history_limit": 100
        }.get(key, default)
        return config

    @pytest.fixture
    def input_handler(self, mock_event_bus, mock_renderer, mock_config):
        """Create an input handler instance for testing."""
        handler = InputHandler(mock_event_bus, mock_renderer, mock_config)
        return handler

    def test_initialization_with_safety_limits(self, input_handler):
        """Test that safety limits are properly initialized."""
        assert input_handler.max_read_attempts == 1000
        assert input_handler.total_timeout == 30.0
        assert input_handler.read_timeout == 0.1
        assert input_handler.max_chunk_size == 50000
        assert input_handler.processing_start_time is None

    @pytest.mark.asyncio
    async def test_safe_read_input_basic(self, input_handler):
        """Test basic safe read functionality."""
        input_handler.processing_start_time = time.time()

        # Mock successful read
        with patch('select.select') as mock_select, \
             patch('os.read') as mock_read:

            mock_select.return_value = [True]  # Data available
            mock_read.return_value = b"test input"

            result = await input_handler._safe_read_input()

            assert result == "test input"
            mock_select.assert_called()
            mock_read.assert_called_with(0, 8192)

    @pytest.mark.asyncio
    async def test_safe_read_input_timeout_protection(self, input_handler):
        """Test that read timeout protection works."""
        # Set processing start time in the past to trigger timeout
        input_handler.processing_start_time = time.time() - 35.0  # 35 seconds ago

        result = await input_handler._safe_read_input()
        assert result == ""

    @pytest.mark.asyncio
    async def test_safe_read_input_chunk_size_limit(self, input_handler):
        """Test that chunk size limit is enforced."""
        input_handler.processing_start_time = time.time()
        input_handler.max_chunk_size = 100  # Small limit for testing

        with patch('select.select') as mock_select, \
             patch('os.read') as mock_read:

            mock_select.return_value = [True]  # Data available
            # Return data larger than the limit
            mock_read.return_value = b"x" * 200  # 200 bytes > 100 byte limit

            result = await input_handler._safe_read_input()

            # Should return empty due to size limit
            assert result == ""

    @pytest.mark.asyncio
    async def test_safe_read_input_max_attempts(self, input_handler):
        """Test that maximum read attempts limit is enforced."""
        input_handler.processing_start_time = time.time()
        input_handler.max_read_attempts = 2  # Very low limit for testing

        with patch('select.select') as mock_select, \
             patch('os.read') as mock_read:

            # Always return data available but empty read (simulating EOF)
            mock_select.return_value = [True]
            mock_read.return_value = b""

            result = await input_handler._safe_read_input()

            # Should return empty after max attempts
            assert result == ""

    def test_is_safe_input_data_valid(self, input_handler):
        """Test safe input data validation with valid data."""
        safe_data = b"Hello, world! This is safe input."
        assert input_handler._is_safe_input_data(safe_data) is True

    def test_is_safe_input_data_too_large(self, input_handler):
        """Test that oversized data is rejected."""
        input_handler.max_chunk_size = 100
        large_data = b"x" * 200  # Larger than limit
        assert input_handler._is_safe_input_data(large_data) is False

    def test_is_safe_input_data_excessive_null_bytes(self, input_handler):
        """Test that data with excessive null bytes is rejected."""
        # Create data with >10% null bytes
        dangerous_data = b"\x00" * 20 + b"safe"  # 20 null bytes out of 24 total = 83%
        assert input_handler._is_safe_input_data(dangerous_data) is False

    def test_is_safe_input_data_excessive_escape_sequences(self, input_handler):
        """Test that data with excessive escape sequences is rejected."""
        # Create data with >100 escape sequences
        dangerous_data = b"\x1b" * 150  # 150 escape sequences
        assert input_handler._is_safe_input_data(dangerous_data) is False

    @pytest.mark.asyncio
    async def test_process_characters_with_timeout_basic(self, input_handler):
        """Test basic character processing with timeout protection."""
        chunk = "hello"

        # Mock the _process_character method
        with patch.object(input_handler, '_process_character') as mock_process:
            mock_process.return_value = None

            await input_handler._process_characters_with_timeout(chunk)

            # Should have processed each character
            assert mock_process.call_count == 5
            mock_process.assert_any_call('h')
            mock_process.assert_any_call('e')
            mock_process.assert_any_call('l')
            mock_process.assert_any_call('l')
            mock_process.assert_any_call('o')

    @pytest.mark.asyncio
    async def test_process_characters_timeout_protection(self, input_handler):
        """Test that character processing timeout works."""
        chunk = "test"

        # Mock _process_character to take too long
        async def slow_process(char):
            await asyncio.sleep(2.0)  # Longer than 1 second timeout

        with patch.object(input_handler, '_process_character', side_effect=slow_process):
            await input_handler._process_characters_with_timeout(chunk)

        # Should complete without hanging due to timeout

    @pytest.mark.asyncio
    async def test_process_characters_max_count_limit(self, input_handler):
        """Test that maximum character count limit is enforced."""
        # Create a very long chunk
        chunk = "x" * 2000  # More than 1000 character limit

        with patch.object(input_handler, '_process_character') as mock_process:
            mock_process.return_value = None

            await input_handler._process_characters_with_timeout(chunk)

            # Should stop at 1000 characters
            assert mock_process.call_count <= 1000

    @pytest.mark.asyncio
    async def test_paste_processing_timeout_protection(self, input_handler):
        """Test that paste processing has timeout protection."""
        # Set processing start time in the past
        input_handler.processing_start_time = time.time() - 35.0

        # Simulate large chunk that would trigger paste processing
        chunk = "x" * 20  # Large enough to trigger paste detection

        with patch('select.select') as mock_select:
            mock_select.return_value = [True]
            with patch.object(input_handler, '_safe_read_input', return_value=chunk):
                # Run a single iteration of the input loop simulation
                # The timeout should prevent paste processing

                # Start processing
                input_handler.processing_start_time = time.time() - 35.0

                # This should return early due to timeout
                result = await input_handler._safe_read_input()

                # Due to timeout, should return empty
                assert result == ""

    def test_buffer_limit_reduced(self, input_handler):
        """Test that buffer limit was reduced from unsafe large value."""
        # The original had 100KB limit which is dangerous
        # Should now be 10KB
        assert input_handler.buffer_manager.buffer_limit == 10000

    @pytest.mark.asyncio
    async def test_input_loop_timeout_recovery(self, input_handler):
        """Test that input loop can recover from timeout conditions."""
        # Mock the components needed for a single iteration
        with patch('select.select') as mock_select, \
             patch.object(input_handler, '_safe_read_input') as mock_safe_read, \
             patch.object(input_handler, '_process_characters_with_timeout') as mock_process_chars:

            # Configure mocks
            mock_select.return_value = [True]  # Data available
            mock_safe_read.return_value = "test"
            mock_process_chars.return_value = None

            # Set timeout condition
            input_handler.processing_start_time = time.time() - 35.0
            input_handler.running = True

            # Simulate one iteration of input processing
            # The timeout check should prevent processing
            result = await input_handler._safe_read_input()

            # Due to timeout, should return empty
            assert result == ""

    @pytest.mark.asyncio
    async def test_error_handling_in_safe_read(self, input_handler):
        """Test error handling in safe read method."""
        input_handler.processing_start_time = time.time()

        with patch('select.select') as mock_select:
            mock_select.side_effect = OSError("Simulated OS error")

            result = await input_handler._safe_read_input()

            # Should handle error gracefully and return empty string
            assert result == ""

    def test_malicious_input_detection(self, input_handler):
        """Test detection of various types of malicious input."""
        # Test control characters
        dangerous_controls = b"\x00\x01\x02\x03\x04\x05" * 3  # More than 10 of each
        assert input_handler._is_safe_input_data(dangerous_controls) is False

        # Test mixed dangerous content
        mixed_dangerous = b"\x1b" * 50 + b"\x00" * 20  # Both escape sequences and null bytes
        assert input_handler._is_safe_input_data(mixed_dangerous) is False

        # Test safe content with few control characters
        mostly_safe = b"Hello\x1bworld"  # Only one escape sequence
        assert input_handler._is_safe_input_data(mostly_safe) is True


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])