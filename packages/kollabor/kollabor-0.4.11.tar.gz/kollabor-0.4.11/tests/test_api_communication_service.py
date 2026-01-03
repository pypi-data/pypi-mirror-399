"""Tests for APICommunicationService component.

Tests the pure API communication functionality extracted from
the monolithic LLM service for better separation of concerns.
"""

import asyncio
import json
import unittest
from unittest.mock import AsyncMock, MagicMock, patch, call
from pathlib import Path
from tempfile import TemporaryDirectory

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm.api_communication_service import APICommunicationService
from core.models import ConversationMessage


class TestAPICommunicationService(unittest.TestCase):
    """Test API communication service functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = MagicMock()
        self.config.get.side_effect = self._get_config_value
        
        self.temp_dir = TemporaryDirectory()
        self.raw_conversations_dir = Path(self.temp_dir.name)
        
        self.service = APICommunicationService(
            config=self.config,
            raw_conversations_dir=self.raw_conversations_dir
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def _get_config_value(self, key, default=None):
        """Mock configuration values."""
        config_map = {
            "core.llm.api_url": "http://localhost:1234",
            "core.llm.model": "test-model",
            "core.llm.temperature": 0.7,
            "core.llm.timeout": 30,
            "core.llm.enable_streaming": False,
            "core.llm.http_connector_limit": 5
        }
        return config_map.get(key, default)
    
    def test_service_initialization(self):
        """Test service initializes with correct configuration."""
        self.assertEqual(self.service.api_url, "http://localhost:1234")
        self.assertEqual(self.service.model, "test-model")
        self.assertEqual(self.service.temperature, 0.7)
        self.assertEqual(self.service.timeout, 30)
        self.assertFalse(self.service.enable_streaming)
        
        self.assertIsNone(self.service.session)
        self.assertIsNone(self.service.connector)
        self.assertFalse(self.service.cancel_requested)
    
    @patch('aiohttp.ClientSession')
    @patch('aiohttp.TCPConnector')
    def test_initialization_creates_session(self, mock_connector_class, mock_session_class):
        """Test that initialization creates HTTP session."""
        mock_connector = MagicMock()
        mock_session = AsyncMock()
        mock_connector_class.return_value = mock_connector
        mock_session_class.return_value = mock_session
        
        asyncio.run(self.service.initialize())
        
        # Should create connector with limit
        mock_connector_class.assert_called_once_with(limit=5)
        
        # Should create session with connector
        mock_session_class.assert_called_once_with(connector=mock_connector)
        
        self.assertEqual(self.service.connector, mock_connector)
        self.assertEqual(self.service.session, mock_session)
    
    def test_prepare_messages_with_objects(self):
        """Test message preparation with ConversationMessage objects."""
        # Create conversation messages
        messages = [
            ConversationMessage(role="system", content="You are helpful."),
            ConversationMessage(role="user", content="Hello!"),
            ConversationMessage(role="assistant", content="Hi there!")
        ]
        
        prepared = self.service._prepare_messages(messages, max_history=None)
        
        self.assertEqual(len(prepared), 3)
        self.assertEqual(prepared[0]["role"], "system")
        self.assertEqual(prepared[0]["content"], "You are helpful.")
        self.assertEqual(prepared[1]["role"], "user")
        self.assertEqual(prepared[1]["content"], "Hello!")
        self.assertEqual(prepared[2]["role"], "assistant")
        self.assertEqual(prepared[2]["content"], "Hi there!")
    
    def test_prepare_messages_with_dicts(self):
        """Test message preparation with dictionary messages."""
        messages = [
            {"role": "user", "content": "Test message 1"},
            {"role": "assistant", "content": "Test response 1"}
        ]
        
        prepared = self.service._prepare_messages(messages, max_history=None)
        
        self.assertEqual(len(prepared), 2)
        self.assertEqual(prepared[0]["role"], "user")
        self.assertEqual(prepared[0]["content"], "Test message 1")
    
    def test_prepare_messages_with_history_limit(self):
        """Test message preparation with history limit."""
        messages = [
            {"role": "user", "content": "Old message 1"},
            {"role": "assistant", "content": "Old response 1"},
            {"role": "user", "content": "Recent message 1"},
            {"role": "assistant", "content": "Recent response 1"},
            {"role": "user", "content": "Latest message"}
        ]
        
        prepared = self.service._prepare_messages(messages, max_history=3)
        
        # Should only include last 3 messages
        self.assertEqual(len(prepared), 3)
        self.assertEqual(prepared[0]["content"], "Recent message 1")
        self.assertEqual(prepared[1]["content"], "Recent response 1")
        self.assertEqual(prepared[2]["content"], "Latest message")
    
    @patch('aiohttp.ClientSession')
    def test_call_llm_session_not_initialized(self, mock_session_class):
        """Test error when session not initialized."""
        messages = [{"role": "user", "content": "Test"}]
        
        with self.assertRaises(RuntimeError) as context:
            asyncio.run(self.service.call_llm(messages))
        
        self.assertIn("HTTP session not initialized", str(context.exception))
    
    def test_cancel_request_functionality(self):
        """Test request cancellation."""
        # Set up mock task
        mock_task = AsyncMock()
        mock_task.done.return_value = False
        self.service.current_request_task = mock_task
        
        self.service.cancel_current_request()
        
        self.assertTrue(self.service.cancel_requested)
        mock_task.cancel.assert_called_once()
    
    def test_get_api_stats(self):
        """Test API statistics generation."""
        stats = self.service.get_api_stats()
        
        expected_stats = {
            "api_url": "http://localhost:1234",
            "model": "test-model",
            "temperature": 0.7,
            "timeout": 30,
            "streaming_enabled": False,
            "session_active": False  # Not initialized yet
        }
        
        self.assertEqual(stats, expected_stats)
    
    def test_raw_interaction_logging(self):
        """Test raw interaction logging to JSONL."""
        payload = {
            "model": "test-model",
            "messages": [{"role": "user", "content": "Test"}],
            "temperature": 0.7
        }
        
        response_data = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        
        self.service._log_raw_interaction(payload, response_data=response_data)
        
        # Check that log file was created
        log_files = list(self.raw_conversations_dir.glob("raw_llm_interactions_*.jsonl"))
        self.assertEqual(len(log_files), 1)
        
        # Read and verify log content
        with open(log_files[0], 'r') as f:
            log_entry = json.loads(f.read().strip())
        
        self.assertIn("timestamp", log_entry)
        self.assertEqual(log_entry["request"]["payload"], payload)
        self.assertEqual(log_entry["response"]["status"], "success")
        self.assertEqual(log_entry["response"]["data"], response_data)
    
    def test_raw_interaction_logging_error(self):
        """Test raw interaction logging for errors."""
        payload = {"model": "test", "messages": []}
        error = "API Error: 500 Internal Server Error"
        
        self.service._log_raw_interaction(payload, error=error)
        
        log_files = list(self.raw_conversations_dir.glob("raw_llm_interactions_*.jsonl"))
        self.assertEqual(len(log_files), 1)
        
        with open(log_files[0], 'r') as f:
            log_entry = json.loads(f.read().strip())
        
        self.assertEqual(log_entry["response"]["status"], "error")
        self.assertEqual(log_entry["response"]["error"], error)
    
    def test_raw_interaction_logging_cancelled(self):
        """Test raw interaction logging for cancellation."""
        payload = {"model": "test", "messages": []}
        
        self.service._log_raw_interaction(payload, cancelled=True)
        
        log_files = list(self.raw_conversations_dir.glob("raw_llm_interactions_*.jsonl"))
        self.assertEqual(len(log_files), 1)
        
        with open(log_files[0], 'r') as f:
            log_entry = json.loads(f.read().strip())
        
        self.assertEqual(log_entry["response"]["status"], "cancelled")
        self.assertIn("cancelled by user", log_entry["response"]["message"])


class TestAPICommunicationServiceIntegration(unittest.TestCase):
    """Integration tests for API communication service."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.config = MagicMock()
        self.config.get.side_effect = lambda key, default: {
            "core.llm.api_url": "http://test-api:1234",
            "core.llm.model": "integration-test-model",
            "core.llm.temperature": 0.5,
            "core.llm.timeout": 10,
            "core.llm.enable_streaming": False,
            "core.llm.http_connector_limit": 2
        }.get(key, default)
        
        self.temp_dir = TemporaryDirectory()
        self.service = APICommunicationService(
            config=self.config,
            raw_conversations_dir=Path(self.temp_dir.name)
        )
    
    def tearDown(self):
        """Clean up integration test fixtures."""
        asyncio.run(self.service.shutdown())
        self.temp_dir.cleanup()
    
    @patch('aiohttp.ClientSession.post')
    def test_successful_api_call_integration(self, mock_post):
        """Test complete API call flow with mocked response."""
        # Mock HTTP response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Integration test response"}}]
        }
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Set up session
        with patch('aiohttp.TCPConnector'), patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session.post = mock_post
            mock_session_class.return_value = mock_session
            
            async def run_test():
                await self.service.initialize()
                
                messages = [
                    ConversationMessage(role="user", content="Integration test message")
                ]
                
                result = await self.service.call_llm(messages)
                
                self.assertEqual(result, "Integration test response")
                
                # Verify API call was made correctly
                mock_post.assert_called_once()
                call_args = mock_post.call_args
                
                # Check URL
                self.assertEqual(call_args[0][0], "http://test-api:1234/v1/chat/completions")
                
                # Check payload
                payload = call_args[1]["json"]
                self.assertEqual(payload["model"], "integration-test-model")
                self.assertEqual(payload["temperature"], 0.5)
                self.assertEqual(len(payload["messages"]), 1)
                self.assertEqual(payload["messages"][0]["content"], "Integration test message")
            
            asyncio.run(run_test())
    
    @patch('aiohttp.ClientSession.post')
    def test_api_error_handling_integration(self, mock_post):
        """Test API error handling in complete flow."""
        # Mock HTTP error response
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text.return_value = "Internal Server Error"
        mock_post.return_value.__aenter__.return_value = mock_response
        
        with patch('aiohttp.TCPConnector'), patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session.post = mock_post
            mock_session_class.return_value = mock_session
            
            async def run_test():
                await self.service.initialize()
                
                messages = [{"role": "user", "content": "Test"}]
                
                with self.assertRaises(Exception) as context:
                    await self.service.call_llm(messages)
                
                self.assertIn("LLM API error: 500", str(context.exception))
            
            asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main(verbosity=2)