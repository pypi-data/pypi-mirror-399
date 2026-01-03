"""Conversation logging system with intelligence features.

This module provides comprehensive JSONL logging for all conversations,
including message threading, session management, and intelligence features
that learn from user patterns and project context.
"""

import json
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..utils.session_naming import generate_session_name

logger = logging.getLogger(__name__)


class KollaborConversationLogger:
    """Conversation logger with intelligence features.
    
    Logs every terminal interaction as structured JSON objects with
    conversation threading, user context analysis, and learning capabilities.
    """
    
    def __init__(self, conversations_dir: Path):
        """Initialize the conversation logger.
        
        Args:
            conversations_dir: Directory to store conversation JSONL files
        """
        self.conversations_dir = conversations_dir
        self.conversations_dir.mkdir(parents=True, exist_ok=True)
        
        # Session management - use memorable session names
        self.session_id = generate_session_name()
        self.session_file = self.conversations_dir / f"{self.session_id}.jsonl"
        
        # Conversation state
        self.conversation_start_time = datetime.now()
        self.message_count = 0
        self.current_thread_uuid = None
        
        # Intelligence features
        self.user_patterns = []
        self.project_context = {}
        self.conversation_themes = []
        self.file_interactions = {}
        
        # Memory management
        self.memory_dir = self.conversations_dir.parent / "conversation_memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self._load_conversation_memory()
        
        logger.info(f"Conversation logger initialized: {self.session_id}")
    
    async def initialize(self) -> bool:
        """Initialize async resources for conversation logger."""
        # Any async initialization can happen here
        logger.debug("Conversation logger async initialization complete")
        return True
    
    async def shutdown(self):
        """Shutdown conversation logger and save state."""
        # Save any pending data
        self._save_conversation_memory()
        logger.info("Conversation logger shutdown complete")
    
    def _load_conversation_memory(self):
        """Load conversation memory from previous sessions."""
        try:
            # Load user patterns
            patterns_file = self.memory_dir / "user_patterns.json"
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    self.user_patterns = json.load(f)
            
            # Load project context
            context_file = self.memory_dir / "project_context.json"
            if context_file.exists():
                with open(context_file, 'r') as f:
                    self.project_context = json.load(f)
            
            # Load solution history
            solutions_file = self.memory_dir / "solution_history.json"
            if solutions_file.exists():
                with open(solutions_file, 'r') as f:
                    self.solution_history = json.load(f)
            else:
                self.solution_history = []
                
            logger.info("Loaded conversation memory from previous sessions")
            
        except Exception as e:
            logger.warning(f"Failed to load conversation memory: {e}")
            self.solution_history = []
    
    def _save_conversation_memory(self):
        """Save conversation memory for future sessions."""
        try:
            # Save user patterns
            patterns_file = self.memory_dir / "user_patterns.json"
            with open(patterns_file, 'w') as f:
                json.dump(self.user_patterns, f, indent=2)
            
            # Save project context
            context_file = self.memory_dir / "project_context.json"
            with open(context_file, 'w') as f:
                json.dump(self.project_context, f, indent=2)
            
            # Save solution history
            solutions_file = self.memory_dir / "solution_history.json"
            with open(solutions_file, 'w') as f:
                json.dump(self.solution_history, f, indent=2)
                
            logger.debug("Saved conversation memory for future sessions")
            
        except Exception as e:
            logger.error(f"Failed to save conversation memory: {e}")
    
    def _get_git_branch(self) -> str:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return "unknown"
    
    def _get_working_directory(self) -> str:
        """Get current working directory."""
        return str(Path.cwd())
    
    async def _append_to_jsonl(self, message: Dict[str, Any]):
        """Append message to JSONL file."""
        try:
            with open(self.session_file, 'a') as f:
                f.write(json.dumps(message) + '\n')
            self.message_count += 1
        except Exception as e:
            logger.error(f"Failed to write to JSONL: {e}")
    
    def _analyze_user_context(self, content: str) -> Dict[str, Any]:
        """Analyze user context from message content."""
        context = {
            "message_length": len(content),
            "has_code": "```" in content,
            "has_question": "?" in content,
            "has_command": any(cmd in content.lower() for cmd in ["fix", "create", "update", "delete", "implement"]),
            "detected_intent": self._detect_intent(content)
        }
        
        # Learn from patterns (deduplicated)
        new_patterns = []
        if context["has_command"]:
            new_patterns.append("prefers_direct_commands")
        if context["message_length"] > 200:
            new_patterns.append("provides_detailed_context")
        if context["has_code"]:
            new_patterns.append("shares_code_frequently")
        if context["has_question"]:
            new_patterns.append("asks_clarifying_questions")
        
        # Add new patterns (deduplicated)
        for pattern in new_patterns:
            if pattern not in self.user_patterns:
                self.user_patterns.append(pattern)
                logger.debug(f"Learned user pattern: {pattern}")
        
        # Update project context based on content
        self._update_project_context(content)
            
        return context
    
    def _update_project_context(self, content: str):
        """Update project context based on message content."""
        # Track file mentions
        import re
        file_mentions = re.findall(r'(?:core/|plugins/|tests/|\.py|\.json|\.md)\S*', content)
        for file_path in file_mentions:
            if file_path not in self.project_context:
                self.project_context[file_path] = {
                    "mentions": 0,
                    "first_mentioned": datetime.now().isoformat(),
                    "context": "user_discussion"
                }
            self.project_context[file_path]["mentions"] += 1
            self.project_context[file_path]["last_mentioned"] = datetime.now().isoformat()
        
        # Track technologies mentioned
        technologies = ["python", "async", "json", "mcp", "terminal", "llm", "hook", "plugin"]
        mentioned_tech = [tech for tech in technologies if tech in content.lower()]
        if mentioned_tech:
            if "technologies" not in self.project_context:
                self.project_context["technologies"] = {}
            for tech in mentioned_tech:
                if tech not in self.project_context["technologies"]:
                    self.project_context["technologies"][tech] = 0
                self.project_context["technologies"][tech] += 1
    
    def _analyze_assistant_response(self, content: str):
        """Analyze assistant response to learn solution patterns."""
        # Track successful solution patterns
        solution_patterns = []
        
        if "<terminal>" in content:
            solution_patterns.append("uses_terminal_commands")
        if "<tool" in content:
            solution_patterns.append("uses_mcp_tools")
        if "```" in content:
            solution_patterns.append("provides_code_examples")
        if len(content) > 500:
            solution_patterns.append("provides_detailed_explanations")
        if any(word in content.lower() for word in ["because", "therefore", "however", "first", "next", "then"]):
            solution_patterns.append("explains_reasoning")
        
        # Add to solution history
        if solution_patterns:
            solution_entry = {
                "timestamp": datetime.now().isoformat(),
                "patterns": solution_patterns,
                "content_length": len(content),
                "session_id": self.session_id
            }
            self.solution_history.append(solution_entry)
            
            # Keep only last 100 solutions
            if len(self.solution_history) > 100:
                self.solution_history = self.solution_history[-100:]
    
    def _detect_intent(self, content: str) -> str:
        """Detect user intent from message."""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["fix", "bug", "error", "broken"]):
            return "debugging"
        elif any(word in content_lower for word in ["create", "new", "add", "implement"]):
            return "feature_development"
        elif any(word in content_lower for word in ["refactor", "clean", "improve", "optimize"]):
            return "refactoring"
        elif any(word in content_lower for word in ["help", "how", "what", "explain"]):
            return "seeking_help"
        elif any(word in content_lower for word in ["test", "check", "verify"]):
            return "testing"
        else:
            return "general_conversation"
    
    def _get_session_context(self) -> Dict[str, Any]:
        """Get current session context."""
        return {
            "conversation_phase": self._determine_conversation_phase(),
            "message_count": self.message_count,
            "session_duration": (datetime.now() - self.conversation_start_time).total_seconds(),
            "recurring_themes": list(set(self.conversation_themes[-10:])) if self.conversation_themes else [],
            "active_files": list(self.file_interactions.keys())[-5:] if self.file_interactions else []
        }
    
    def _determine_conversation_phase(self) -> str:
        """Determine current phase of conversation."""
        if self.message_count < 2:
            return "initiation"
        elif self.message_count < 10:
            return "exploration"
        elif self.message_count < 30:
            return "development"
        else:
            return "deep_work"
    
    def _get_project_awareness(self) -> Dict[str, Any]:
        """Get project awareness context."""
        return {
            "project_type": self.project_context.get("type", "python_terminal_app"),
            "architecture": self.project_context.get("architecture", "plugin_based"),
            "recent_changes": self.project_context.get("recent_changes", []),
            "known_issues": self.project_context.get("known_issues", []),
            "coding_standards": self.project_context.get("coding_standards", {})
        }
    
    def _get_related_sessions(self) -> List[str]:
        """Find related previous sessions."""
        related = []
        try:
            # Look for sessions with similar themes
            for session_file in self.conversations_dir.glob("session_*.jsonl"):
                if session_file.name != self.session_file.name:
                    # Simple heuristic: sessions from same day
                    if session_file.name[:10] == self.session_file.name[:10]:
                        related.append(session_file.stem)
                    if len(related) >= 3:
                        break
        except Exception as e:
            logger.warning(f"Failed to find related sessions: {e}")
        return related
    
    def log_message(self, role: str, content: str, parent_uuid: Optional[str] = None,
                    metadata: Optional[Dict] = None) -> None:
        """Generic message logging - routes to appropriate role-specific method.

        This is a synchronous wrapper that schedules the async logging.

        Args:
            role: Message role (user, assistant, system)
            content: Message content
            parent_uuid: Optional parent message UUID
            metadata: Optional additional metadata
        """
        import asyncio

        async def _log():
            if role == "user":
                await self.log_user_message(content, parent_uuid, metadata)
            elif role == "assistant":
                await self.log_assistant_message(content, parent_uuid or "", metadata)
            elif role == "system":
                await self.log_system_message(content, parent_uuid or "", metadata)
            else:
                logger.warning(f"Unknown role for logging: {role}")

        # Try to get running loop and schedule, otherwise log synchronously
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(_log())
        except RuntimeError:
            # No running loop - skip async logging
            logger.debug(f"Skipping async log for {role} message (no event loop)")

    async def log_conversation_start(self):
        """Log conversation root structure with metadata."""
        root_message = {
            "type": "conversation_metadata",
            "sessionId": self.session_id,
            "startTime": self.conversation_start_time.isoformat() + "Z",
            "endTime": None,
            "uuid": str(uuid4()),
            "timestamp": datetime.now().isoformat() + "Z",
            "cwd": self._get_working_directory(),
            "gitBranch": self._get_git_branch(),
            "version": "1.0.0",
            "conversation_context": {
                "project_type": "python_terminal_app",
                "active_plugins": ["llm_service", "hook_system", "conversation_logger"],
                "user_profile": {
                    "expertise_level": "advanced",
                    "preferred_communication": "direct",
                    "coding_style": "pythonic"
                },
                "session_goals": [],
                "conversation_summary": ""
            },
            "kollabor_intelligence": {
                "conversation_memory": {
                    "related_sessions": self._get_related_sessions(),
                    "recurring_themes": [],
                    "user_patterns": self.user_patterns[:10] if self.user_patterns else []
                }
            }
        }
        
        await self._append_to_jsonl(root_message)
        logger.info(f"Logged conversation start: {self.session_id}")
    
    async def log_user_message(self, content: str, parent_uuid: Optional[str] = None, 
                              user_context: Optional[Dict] = None) -> str:
        """Log user message with intelligence features."""
        message_uuid = str(uuid4())
        
        message = {
            "parentUuid": parent_uuid,
            "isSidechain": False,
            "userType": "external",
            "cwd": self._get_working_directory(),
            "sessionId": self.session_id,
            "version": "1.0.0",
            "gitBranch": self._get_git_branch(),
            "type": "user",
            "message": {
                "role": "user",
                "content": content
            },
            "uuid": message_uuid,
            "timestamp": datetime.now().isoformat() + "Z",
            "kollabor_intelligence": {
                "user_context": user_context or self._analyze_user_context(content),
                "session_context": self._get_session_context(),
                "project_awareness": self._get_project_awareness()
            }
        }
        
        await self._append_to_jsonl(message)
        
        # Update conversation themes
        intent = message["kollabor_intelligence"]["user_context"].get("detected_intent")
        if intent:
            self.conversation_themes.append(intent)
        
        # Save updated conversation memory
        self._save_conversation_memory()
        
        return message_uuid
    
    async def log_assistant_message(self, content: str, parent_uuid: str, 
                                   usage_stats: Optional[Dict] = None) -> str:
        """Log assistant response with usage statistics."""
        message_uuid = str(uuid4())
        
        message = {
            "parentUuid": parent_uuid,
            "isSidechain": False,
            "userType": "external",
            "cwd": self._get_working_directory(),
            "sessionId": self.session_id,
            "version": "1.0.0",
            "gitBranch": self._get_git_branch(),
            "message": {
                "id": f"msg_kollabor_{int(time.time())}",
                "type": "message",
                "role": "assistant",
                "model": "qwen/qwen3-4b",
                "content": [
                    {
                        "type": "text",
                        "text": content
                    }
                ],
                "stop_reason": None,
                "stop_sequence": None,
                "usage": usage_stats or {}
            },
            "requestId": f"req_kollabor_{int(time.time())}",
            "type": "assistant",
            "uuid": message_uuid,
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
        await self._append_to_jsonl(message)
        
        # Analyze assistant response for learning
        self._analyze_assistant_response(content)
        
        # Save updated conversation memory
        self._save_conversation_memory()
        
        return message_uuid
    
    async def log_system_message(self, content: str, parent_uuid: str, 
                                subtype: str = "informational",
                                tool_use_id: Optional[str] = None) -> str:
        """Log system messages including hook outputs and tool calls."""
        message_uuid = str(uuid4())
        
        message = {
            "parentUuid": parent_uuid,
            "isSidechain": False,
            "userType": "external",
            "cwd": self._get_working_directory(),
            "sessionId": self.session_id,
            "version": "1.0.0",
            "gitBranch": self._get_git_branch(),
            "type": "system",
            "subtype": subtype,
            "content": content,
            "isMeta": False,
            "timestamp": datetime.now().isoformat() + "Z",
            "uuid": message_uuid,
            "level": "info"
        }
        
        if tool_use_id:
            message["toolUseID"] = tool_use_id
        
        await self._append_to_jsonl(message)
        return message_uuid
    
    async def log_conversation_end(self):
        """Log conversation end and save memory."""
        # Update the root message with end time
        # Note: In production, we'd update the first line of JSONL
        # For now, append an end marker
        end_message = {
            "type": "conversation_end",
            "sessionId": self.session_id,
            "endTime": datetime.now().isoformat() + "Z",
            "uuid": str(uuid4()),
            "timestamp": datetime.now().isoformat() + "Z",
            "summary": {
                "total_messages": self.message_count,
                "duration": (datetime.now() - self.conversation_start_time).total_seconds(),
                "themes": list(set(self.conversation_themes)) if self.conversation_themes else [],
                "files_modified": list(self.file_interactions.keys()) if self.file_interactions else []
            }
        }
        
        await self._append_to_jsonl(end_message)
        
        # Save conversation memory
        self._save_conversation_memory()
        
        logger.info(f"Logged conversation end: {self.session_id}")
    
    def list_sessions(self, filters: Dict = None) -> List[Dict]:
        """List available sessions with metadata.
        
        Args:
            filters: Optional filters for sessions
            
        Returns:
            List of session metadata
        """
        sessions = []

        try:
            # Find both old format (session_*) and new format (YYMMDDHHMM-*) files
            all_files = (
                list(self.conversations_dir.glob("session_*.jsonl")) +
                list(self.conversations_dir.glob("[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-*.jsonl"))
            )

            for session_file in all_files:
                try:
                    session_info = self._parse_session_file(session_file, filters)
                    if session_info:
                        sessions.append(session_info)
                except Exception as e:
                    logger.warning(f"Failed to parse session file {session_file}: {e}")
                    continue
            
            # Sort by start time (newest first)
            sessions.sort(key=lambda x: x.get("start_time", ""), reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to scan sessions directory: {e}")
        
        return sessions
    
    def _parse_session_file(self, session_file: Path, filters: Dict = None) -> Optional[Dict]:
        """Parse a session file and extract metadata.
        
        Args:
            session_file: Path to session JSONL file
            filters: Optional filters
            
        Returns:
            Session metadata or None if should be filtered out
        """
        try:
            session_info = {
                "session_id": session_file.stem,
                "file_path": str(session_file),
                "start_time": None,
                "end_time": None,
                "message_count": 0,
                "working_directory": "unknown",
                "git_branch": "unknown",
                "topics": [],
                "duration": None,
                "size_bytes": session_file.stat().st_size,
                "preview_messages": []
            }
            
            with open(session_file, 'r') as f:
                lines = f.readlines()
            
            user_messages = []
            assistant_messages = []
            
            for line in lines:
                try:
                    data = json.loads(line.strip())
                    
                    # Extract metadata from conversation start
                    if data.get("type") == "conversation_metadata":
                        session_info["start_time"] = data.get("startTime")
                        session_info["working_directory"] = data.get("cwd", "unknown")
                        session_info["git_branch"] = data.get("gitBranch", "unknown")
                    
                    # Extract end time
                    elif data.get("type") == "conversation_end":
                        session_info["end_time"] = data.get("endTime")
                        summary = data.get("summary", {})
                        session_info["topics"] = summary.get("themes", [])
                    
                    # Count messages
                    elif data.get("type") == "user":
                        user_messages.append(data)
                        session_info["message_count"] += 1
                        
                        # Store preview messages (first 3 user messages)
                        if len(user_messages) <= 3:
                            content = data.get("message", {}).get("content", "")
                            preview = content[:100] + "..." if len(content) > 100 else content
                            session_info["preview_messages"].append({
                                "role": "user",
                                "content": preview,
                                "timestamp": data.get("timestamp")
                            })
                    
                    elif data.get("type") == "assistant":
                        assistant_messages.append(data)
                        session_info["message_count"] += 1
                        
                        # Store preview assistant messages
                        if len(assistant_messages) <= 2:
                            content = data.get("message", {}).get("content", [])
                            if isinstance(content, list) and content:
                                text_content = content[0].get("text", "")
                            else:
                                text_content = str(content)
                            
                            preview = text_content[:100] + "..." if len(text_content) > 100 else text_content
                            session_info["preview_messages"].append({
                                "role": "assistant", 
                                "content": preview,
                                "timestamp": data.get("timestamp")
                            })
                
                except json.JSONDecodeError:
                    continue
            
            # Calculate duration
            if session_info["start_time"] and session_info["end_time"]:
                try:
                    start = datetime.fromisoformat(session_info["start_time"].replace('Z', '+00:00'))
                    end = datetime.fromisoformat(session_info["end_time"].replace('Z', '+00:00'))
                    duration = end - start
                    session_info["duration"] = str(int(duration.total_seconds() / 60)) + "m"
                except:
                    session_info["duration"] = "unknown"
            
            # Apply filters
            if filters:
                if "date_range" in filters:
                    # Filter by date range
                    pass  # TODO: Implement date filtering
                
                if "working_directory" in filters:
                    if session_info["working_directory"] != filters["working_directory"]:
                        return None
                
                if "git_branch" in filters:
                    if session_info["git_branch"] != filters["git_branch"]:
                        return None
            
            return session_info
            
        except Exception as e:
            logger.warning(f"Failed to parse session file {session_file}: {e}")
            return None
    
    def get_session_summary(self, session_id: str) -> Dict:
        """Get session summary for preview.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session summary
        """
        try:
            # Find session file
            session_file = None
            for file_path in self.conversations_dir.glob(f"{session_id}*.jsonl"):
                session_file = file_path
                break
            
            if not session_file:
                return {}
            
            session_info = self._parse_session_file(session_file)
            if not session_info:
                return {}
            
            # Extract additional summary information
            summary = {
                "metadata": session_info,
                "key_topics": session_info.get("topics", []),
                "user_patterns": [],  # TODO: Extract from memory
                "project_context": {
                    "working_directory": session_info.get("working_directory"),
                    "git_branch": session_info.get("git_branch"),
                    "files_mentioned": []  # TODO: Extract from messages
                },
                "compatibility_score": 1.0  # TODO: Calculate based on environment
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get session summary for {session_id}: {e}")
            return {}
    
    def search_sessions(self, query: str) -> List[Dict]:
        """Search sessions by content.
        
        Args:
            query: Search query
            
        Returns:
            List of matching sessions
        """
        results = []
        query_lower = query.lower()

        try:
            # Search both old format (session_*) and new format (YYMMDDHHMM-*) files
            all_files = (
                list(self.conversations_dir.glob("session_*.jsonl")) +
                list(self.conversations_dir.glob("[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-*.jsonl"))
            )

            for session_file in all_files:
                try:
                    # Quick filename check first
                    if query_lower in session_file.name.lower():
                        session_info = self._parse_session_file(session_file)
                        if session_info:
                            results.append(session_info)
                        continue

                    # Content search
                    with open(session_file, 'r') as f:
                        content = f.read().lower()

                    if query_lower in content:
                        session_info = self._parse_session_file(session_file)
                        if session_info:
                            # Add search relevance info
                            session_info["search_relevance"] = self._calculate_search_relevance(
                                content, query_lower
                            )
                            results.append(session_info)

                except Exception as e:
                    logger.warning(f"Failed to search session file {session_file}: {e}")
                    continue
            
            # Sort by relevance (most relevant first)
            results.sort(key=lambda x: x.get("search_relevance", 0), reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to search sessions: {e}")
        
        return results
    
    def _calculate_search_relevance(self, content: str, query: str) -> float:
        """Calculate search relevance score.
        
        Args:
            content: Session content
            query: Search query
            
        Returns:
            Relevance score (0.0 to 1.0)
        """
        # Simple relevance calculation
        query_words = query.split()
        content_words = content.split()
        
        if not query_words:
            return 0.0
        if not content_words:
            return 0.0
        
        # Count exact matches
        exact_matches = content.count(query)
        
        # Count word matches
        word_matches = sum(1 for word in query_words if word in content)
        
        # Calculate relevance based on frequency and coverage
        relevance = (exact_matches * 0.5 + word_matches * 0.1) / len(content_words)
        
        return min(relevance * 100, 1.0)  # Normalize to 0-1
