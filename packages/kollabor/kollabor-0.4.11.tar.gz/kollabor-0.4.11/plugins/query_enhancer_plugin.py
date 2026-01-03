"""Query Enhancement Plugin for Kollabor CLI.

Uses a fast model to enhance user queries before sending to the main model,
dramatically improving response quality especially with "dumb" models.
"""

import logging
import time
from typing import Any, Dict, List
import aiohttp

from core.events.models import Event, EventType, Hook, HookPriority
from core.io.visual_effects import AgnosterSegment

logger = logging.getLogger(__name__)


class QueryEnhancerPlugin:
    """Plugin that enhances user queries using a fast model before main processing."""
    
    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Get default configuration for the query enhancer plugin."""
        config = {
            "plugins": {
                "query_enhancer": {
                "enabled": False,
                "show_status": True,
                "fast_model": {
                    "api_url": "http://localhost:1234",
                    "model": "qwen3-0.6b",
                    "temperature": 0.3,
                    "timeout": 5
                },
                "enhancement_prompt": """You are a query enhancement specialist. Your job is to improve user queries to get better responses from AI assistants.

Take this user query and enhance it by:
1. Making it more specific and detailed
2. Adding relevant context
3. Clarifying any ambiguity
4. Keeping the original intent

Return ONLY the enhanced query, nothing else.

Original query: {query}

Enhanced query:""",
                "max_length": 500,
                "min_query_length": 10,
                "skip_enhancement_keywords": ["hi", "hello", "thanks", "thank you", "ok", "okay", "yes", "no"],
                "performance_tracking": True
                }
            }
        }
        return config
    
    @staticmethod
    def get_startup_info(config) -> List[str]:
        """Get plugin startup information for display."""
        enabled = config.get("plugins.query_enhancer.enabled", True)
        fast_model = config.get("plugins.query_enhancer.fast_model.model", "qwen/qwen3-1.5b")
        return [
            f"Enabled: {enabled}",
            f"Fast Model: {fast_model}",
            f"Enhancement: {'On' if enabled else 'Off'}"
        ]

    @staticmethod
    def get_config_widgets() -> Dict[str, Any]:
        """Get configuration widgets for this plugin."""
        return {
            "title": "Query Enhancer Plugin",
            "widgets": [
                {"type": "checkbox", "label": "Show Status", "config_path": "plugins.query_enhancer.show_status", "help": "Display query enhancement status"},
                {"type": "text_input", "label": "Fast Model API URL", "config_path": "plugins.query_enhancer.fast_model.api_url", "placeholder": "http://localhost:1234", "help": "API URL for fast enhancement model"},
                {"type": "text_input", "label": "Fast Model", "config_path": "plugins.query_enhancer.fast_model.model", "placeholder": "qwen3-0.6b", "help": "Model name for query enhancement"},
                {"type": "slider", "label": "Fast Model Temperature", "config_path": "plugins.query_enhancer.fast_model.temperature", "min_value": 0.0, "max_value": 1.0, "step": 0.1, "help": "Creativity level for enhancement (0.0-1.0)"},
                {"type": "slider", "label": "Fast Model Timeout", "config_path": "plugins.query_enhancer.fast_model.timeout", "min_value": 1, "max_value": 30, "step": 1, "help": "Timeout for enhancement requests (seconds)"},
                {"type": "slider", "label": "Max Query Length", "config_path": "plugins.query_enhancer.max_length", "min_value": 100, "max_value": 2000, "step": 50, "help": "Maximum enhanced query length"},
                {"type": "slider", "label": "Min Query Length", "config_path": "plugins.query_enhancer.min_query_length", "min_value": 1, "max_value": 50, "step": 1, "help": "Minimum query length to enhance"},
                {"type": "checkbox", "label": "Performance Tracking", "config_path": "plugins.query_enhancer.performance_tracking", "help": "Track enhancement performance metrics"}
            ]
        }

    def __init__(self, name: str, state_manager, event_bus, renderer, config) -> None:
        """Initialize the query enhancer plugin.
        
        Args:
            name: Plugin name.
            state_manager: State management system.
            event_bus: Event bus for hook registration.
            renderer: Terminal renderer.
            config: Configuration manager.
        """
        self.name = name
        self.state_manager = state_manager
        self.event_bus = event_bus
        self.renderer = renderer
        self.config = config
        
        # Plugin configuration
        self.enabled = config.get("plugins.query_enhancer.enabled", True)
        self.fast_model_config = config.get("plugins.query_enhancer.fast_model", {})
        self.enhancement_prompt = config.get("plugins.query_enhancer.enhancement_prompt", "")
        self.max_length = config.get("plugins.query_enhancer.max_length", 500)
        self.min_query_length = config.get("plugins.query_enhancer.min_query_length", 10)
        self.skip_keywords = config.get("plugins.query_enhancer.skip_enhancement_keywords", [])
        
        # Performance tracking
        self.stats = {
            "total_queries": 0,
            "enhanced_queries": 0,
            "enhancement_failures": 0,
            "avg_enhancement_time": 0.0,
            "total_enhancement_time": 0.0
        }
        
        # HTTP session for API calls
        self.session: aiohttp.ClientSession = None
        
        # Register hooks
        self.hooks = [
            Hook(
                name="enhance_user_query",
                plugin_name=self.name,
                event_type=EventType.USER_INPUT_PRE,
                priority=HookPriority.PREPROCESSING.value,
                callback=self._enhance_query_hook,
                timeout=config.get("plugins.query_enhancer.fast_model.timeout", 5)
            )
        ]
        
        logger.info(f"QueryEnhancer plugin '{name}' initialized with fast model: {self.fast_model_config.get('model', 'unknown')}")
    
    async def initialize(self) -> None:
        """Initialize the query enhancer plugin."""
        if self.enabled:
            timeout = aiohttp.ClientTimeout(total=self.fast_model_config.get("timeout", 5))
            self.session = aiohttp.ClientSession(timeout=timeout)
            logger.info("QueryEnhancer HTTP session initialized")

        # Register status view
        await self._register_status_view()

    async def _register_status_view(self) -> None:
        """Register query enhancer status view."""
        try:
            if (self.renderer and
                hasattr(self.renderer, 'status_renderer') and
                self.renderer.status_renderer and
                hasattr(self.renderer.status_renderer, 'status_registry') and
                self.renderer.status_renderer.status_registry):

                from core.io.status_renderer import StatusViewConfig, BlockConfig

                view = StatusViewConfig(
                    name="Query Enhancer",
                    plugin_source="query_enhancer",
                    priority=350,
                    blocks=[BlockConfig(
                        width_fraction=1.0,
                        content_provider=self._get_status_content,
                        title="Query Enhancer",
                        priority=100
                    )],
                )

                registry = self.renderer.status_renderer.status_registry
                registry.register_status_view("query_enhancer", view)
                logger.info("Registered 'Query Enhancer' status view")

        except Exception as e:
            logger.error(f"Failed to register status view: {e}")

    def _get_status_content(self) -> List[str]:
        """Get query enhancer status (agnoster style)."""
        try:
            seg = AgnosterSegment()

            show_status = self.config.get('plugins.query_enhancer.show_status', True)
            if not show_status or not self.enabled:
                seg.add_neutral("Enhancer: Off", "dark")
                return [seg.render()]

            success_rate = 0.0
            if self.stats["total_queries"] > 0:
                success_rate = (self.stats["enhanced_queries"] / self.stats["total_queries"]) * 100

            model = self.fast_model_config.get('model', 'unknown')

            seg.add_lime("Enhancer", "dark")
            seg.add_cyan(model, "dark")
            seg.add_lime(f"{self.stats['enhanced_queries']}/{self.stats['total_queries']}")
            seg.add_cyan(f"{success_rate:.0f}%")
            seg.add_neutral(f"{self.stats['avg_enhancement_time']:.2f}s", "mid")

            return [seg.render()]

        except Exception as e:
            logger.error(f"Error getting status content: {e}")
            seg = AgnosterSegment()
            seg.add_neutral("Enhancer: Error", "dark")
            return [seg.render()]
    
    async def register_hooks(self) -> None:
        """Register query enhancement hooks."""
        if self.enabled:
            for hook in self.hooks:
                await self.event_bus.register_hook(hook)
            logger.info("QueryEnhancer hooks registered")
    
    async def shutdown(self) -> None:
        """Shutdown the query enhancer plugin."""
        if self.session:
            await self.session.close()
            logger.info("QueryEnhancer session closed")
    
    async def _enhance_query_hook(self, data: Dict[str, Any], event: Event) -> Dict[str, Any]:
        """Hook to enhance user queries before main processing.
        
        Args:
            data: Event data containing the user message.
            event: The event object (used for hook system compatibility).
            
        Returns:
            Modified event data with enhanced query.
        """
        if not self.enabled:
            return data
        
        original_query = data.get("message", "").strip()
        if not original_query:
            return data
        
        self.stats["total_queries"] += 1
        
        # Skip enhancement for very short queries or common phrases
        if (len(original_query) < self.min_query_length or 
            any(keyword.lower() in original_query.lower() for keyword in self.skip_keywords)):
            logger.debug(f"Skipping enhancement for short/common query: {original_query[:50]}")
            return data
        
        start_time = time.time()
        try:
            enhanced_query = await self._enhance_query(original_query)
            enhancement_time = time.time() - start_time
            
            if enhanced_query and enhanced_query.strip() != original_query.strip():
                # Update stats
                self.stats["enhanced_queries"] += 1
                self.stats["total_enhancement_time"] += enhancement_time
                self.stats["avg_enhancement_time"] = (
                    self.stats["total_enhancement_time"] / self.stats["enhanced_queries"]
                )
                
                # Return enhanced query in expected format
                enhanced_data = data.copy()
                enhanced_data["enhanced_message"] = enhanced_query.strip()
                logger.info(f"Enhanced query ({enhancement_time:.2f}s): {original_query[:50]}... → {enhanced_query[:50]}...")
                return enhanced_data
            else:
                logger.debug("Enhancement did not improve query, using original")
            
        except Exception as e:
            self.stats["enhancement_failures"] += 1
            logger.warning(f"Query enhancement failed: {e}, using original query")
        
        return data
    
    async def _enhance_query(self, query: str) -> str:
        """Enhance a user query using the fast model.
        
        Args:
            query: The original user query.
            
        Returns:
            Enhanced query or original if enhancement fails.
        """
        if not self.session:
            raise Exception("HTTP session not initialized")
        
        # Prepare the enhancement prompt
        prompt = self.enhancement_prompt.format(query=query)
        
        # Prepare API payload
        payload = {
            "model": self.fast_model_config.get("model", "qwen3-0.6b"),
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.fast_model_config.get("temperature", 0.3),
            "max_tokens": self.max_length,
            "stream": False
        }
        
        # Call the fast model API with timeout
        api_url = self.fast_model_config.get("api_url", "http://localhost:1234")
        timeout = self.fast_model_config.get("timeout", 5)
        
        async with self.session.post(
            f"{api_url}/v1/chat/completions",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=timeout)
        ) as response:
            if response.status != 200:
                raise Exception(f"API returned status {response.status}")
            
            result = await response.json()
            raw_response = result["choices"][0]["message"]["content"].strip()
            
            # Clean up response by removing thinking tags and extracting clean content
            enhanced_query = self._clean_response(raw_response)
            
            # Basic validation of enhanced query
            if len(enhanced_query) > self.max_length * 2:  # Too long
                raise Exception("Enhanced query too long")
            
            if not enhanced_query or enhanced_query.lower() in ["none", "n/a", "null"]:
                raise Exception("Invalid enhanced query")
            
            return enhanced_query
    
    def _clean_response(self, raw_response: str) -> str:
        """Clean up model response by removing thinking tags and extracting enhanced query.
        
        Args:
            raw_response: Raw response from the fast model.
            
        Returns:
            Cleaned enhanced query.
        """
        import re
        
        # Remove thinking tags and their content
        cleaned = re.sub(r'<think>.*?</think>', '', raw_response, flags=re.DOTALL)
        cleaned = re.sub(r'<thinking>.*?</thinking>', '', cleaned, flags=re.DOTALL)
        
        # If response still starts with <think> (unclosed tag), extract everything after it
        if cleaned.startswith('<think>'):
            # Find the end of the thinking section and extract what comes after
            lines = cleaned.split('\n')
            enhanced_lines = []
            in_thinking = True
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Skip obvious thinking indicators
                if (line.startswith('<think>') or 
                    line.startswith('Okay,') or 
                    line.startswith('Let me') or
                    line.startswith('First,') or
                    line.startswith('I should') or
                    line.startswith('Maybe') or
                    line.startswith('The user')):
                    continue
                
                # Look for the actual enhanced query
                if (not in_thinking or
                    line.startswith('Enhanced query:') or
                    line.startswith('Improved query:') or
                    (len(line) > 20 and '?' in line)):  # Likely a question
                    in_thinking = False
                    if line.startswith(('Enhanced query:', 'Improved query:')):
                        line = line.split(':', 1)[1].strip()
                    if line:
                        enhanced_lines.append(line)
            
            if enhanced_lines:
                cleaned = ' '.join(enhanced_lines)
        
        # Clean up any remaining artifacts
        cleaned = cleaned.strip()
        cleaned = re.sub(r'^(Enhanced query:|Improved query:|Query:)\s*', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s+', ' ', cleaned)  # Normalize whitespace
        
        # If we still don't have a good result, try to extract the most query-like sentence
        if not cleaned or len(cleaned) < 10:
            sentences = raw_response.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 15 and ('?' in sentence or 'how' in sentence.lower()):
                    cleaned = sentence
                    break
        
        return cleaned.strip() if cleaned else raw_response.strip()