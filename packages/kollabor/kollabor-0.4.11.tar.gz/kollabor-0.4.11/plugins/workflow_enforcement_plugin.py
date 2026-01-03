"""Workflow Enforcement Plugin for Kollabor CLI.

This plugin detects todo lists in LLM responses and enforces sequential completion
with tool calling verification and confirmation requirements.
"""

import asyncio
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

from core.events.models import EventType, HookPriority
from core.io.visual_effects import AgnosterSegment

logger = logging.getLogger(__name__)


class WorkflowState(Enum):
    """Workflow enforcement states."""
    INACTIVE = "inactive"          # No active workflow
    TODO_DETECTED = "todo_detected"  # Todo list found, waiting for user confirmation
    ENFORCING = "enforcing"        # Actively enforcing todo completion
    WAITING_CONFIRMATION = "waiting_confirmation"  # Waiting for completion confirmation
    BLOCKED = "blocked"            # User requested bypass or hit issue
    COMPLETED = "completed"        # Workflow successfully completed


@dataclass
class TodoItem:
    """Represents a single todo item."""
    index: int
    text: str
    terminal_command: Optional[str] = None
    completed: bool = False
    confirmed: bool = False
    attempted: bool = False
    failure_reason: Optional[str] = None
    timestamp_started: Optional[datetime] = None
    timestamp_completed: Optional[datetime] = None


@dataclass
class WorkflowContext:
    """Maintains context for active workflow."""
    original_request: str = ""
    todo_items: List[TodoItem] = field(default_factory=list)
    current_todo_index: int = 0
    state: WorkflowState = WorkflowState.INACTIVE
    llm_response_with_todos: str = ""
    bypass_requested: bool = False
    bypass_reason: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class WorkflowEnforcementPlugin:
    """Plugin that enforces todo completion with tool calling verification."""
    
    def __init__(self, state_manager, event_bus, renderer, config):
        """Initialize workflow enforcement plugin."""
        self.state_manager = state_manager
        self.event_bus = event_bus
        self.renderer = renderer
        self.config = config
        
        # Workflow state
        self.workflow_context = WorkflowContext()
        
        # Configuration
        self.enabled = config.get("workflow_enforcement.enabled", True)
        self.require_tool_calls = config.get("workflow_enforcement.require_tool_calls", True)
        self.confirmation_timeout = config.get("workflow_enforcement.confirmation_timeout", 300)  # 5 minutes
        self.bypass_keywords = config.get("workflow_enforcement.bypass_keywords", 
                                         ["bypass", "skip", "blocked", "issue", "problem"])
        
        logger.info("Workflow Enforcement Plugin initialized")
    
    @staticmethod
    def get_default_config():
        """Return default configuration for the plugin."""
        return {
            "workflow_enforcement": {
                "enabled": False,
                "require_tool_calls": True,
                "confirmation_timeout": 300,
                "bypass_keywords": ["bypass", "skip", "blocked", "issue", "problem"],
                "auto_start_workflows": True,
                "show_progress_in_status": True
            }
        }

    @staticmethod
    def get_config_widgets() -> Dict[str, Any]:
        """Get configuration widgets for this plugin."""
        return {
            "title": "Workflow Enforcement",
            "widgets": [
                {"type": "checkbox", "label": "Require Tool Calls", "config_path": "workflow_enforcement.require_tool_calls", "help": "Require workflows to include tool calls"},
                {"type": "slider", "label": "Confirmation Timeout", "config_path": "workflow_enforcement.confirmation_timeout", "min_value": 30, "max_value": 600, "step": 30, "help": "Workflow confirmation timeout (seconds)"},
                {"type": "checkbox", "label": "Auto Start Workflows", "config_path": "workflow_enforcement.auto_start_workflows", "help": "Automatically start detected workflows"},
                {"type": "checkbox", "label": "Show Progress in Status", "config_path": "workflow_enforcement.show_progress_in_status", "help": "Display workflow progress in status bar"}
            ]
        }

    async def initialize(self):
        """Initialize the plugin."""
        # Load any persistent workflow state
        await self._load_workflow_state()

        # Register status view
        await self._register_status_view()

        logger.info("Workflow enforcement plugin initialized")

    async def _register_status_view(self) -> None:
        """Register workflow enforcement status view."""
        try:
            if (self.renderer and
                hasattr(self.renderer, 'status_renderer') and
                self.renderer.status_renderer and
                hasattr(self.renderer.status_renderer, 'status_registry') and
                self.renderer.status_renderer.status_registry):

                from core.io.status_renderer import StatusViewConfig, BlockConfig

                view = StatusViewConfig(
                    name="Workflow Enforcement",
                    plugin_source="workflow_enforcement",
                    priority=450,
                    blocks=[BlockConfig(
                        width_fraction=1.0,
                        content_provider=self._get_status_content,
                        title="Workflow",
                        priority=100
                    )],
                )

                registry = self.renderer.status_renderer.status_registry
                registry.register_status_view("workflow_enforcement", view)
                logger.info("Registered 'Workflow Enforcement' status view")

        except Exception as e:
            logger.error(f"Failed to register status view: {e}")

    def _get_status_content(self) -> List[str]:
        """Get workflow enforcement status (agnoster style)."""
        try:
            # Only show if workflow is active
            if self.workflow_context.state == WorkflowState.INACTIVE:
                return []

            seg = AgnosterSegment()

            if self.workflow_context.state == WorkflowState.ENFORCING:
                current_todo = self._get_current_todo()
                if current_todo:
                    progress = f"{current_todo.index + 1}/{len(self.workflow_context.todo_items)}"
                    seg.add_lime("Workflow", "dark")
                    seg.add_cyan(f"Todo {progress}", "dark")
                    seg.add_neutral(current_todo.text[:30] + "..." if len(current_todo.text) > 30 else current_todo.text, "mid")
                else:
                    seg.add_lime("Workflow", "dark")
                    seg.add_cyan("Enforcing", "dark")
            elif self.workflow_context.state == WorkflowState.WAITING_CONFIRMATION:
                seg.add_lime("Workflow", "dark")
                seg.add_cyan("Awaiting Confirm", "dark")
            elif self.workflow_context.state == WorkflowState.BLOCKED:
                seg.add_lime("Workflow", "dark")
                seg.add_neutral("Blocked", "mid")
            elif self.workflow_context.state == WorkflowState.TODO_DETECTED:
                seg.add_lime("Workflow", "dark")
                seg.add_cyan(f"{len(self.workflow_context.todo_items)} todos detected")
            else:
                seg.add_lime("Workflow", "dark")
                seg.add_cyan(self.workflow_context.state.value.title(), "dark")

            return [seg.render()]

        except Exception as e:
            logger.error(f"Error getting status content: {e}")
            seg = AgnosterSegment()
            seg.add_neutral("Workflow: Error", "dark")
            return [seg.render()]
    
    async def register_hooks(self):
        """Register hooks for workflow enforcement."""
        if not self.enabled:
            logger.info("Workflow enforcement plugin disabled")
            return
            
        # Hook into LLM responses to detect todos
        await self.event_bus.register_hook(
            EventType.LLM_RESPONSE_POST,
            "workflow_todo_detector",
            self._detect_and_process_todos,
            HookPriority.PREPROCESSING
        )
        
        # Hook into user input to handle confirmations and bypass
        await self.event_bus.register_hook(
            EventType.USER_INPUT_PRE,
            "workflow_input_processor",
            self._process_user_input,
            HookPriority.PREPROCESSING
        )
        
        # Hook into LLM requests to inject workflow context
        await self.event_bus.register_hook(
            EventType.LLM_REQUEST_PRE,
            "workflow_context_injector", 
            self._inject_workflow_context,
            HookPriority.PREPROCESSING
        )
        
        logger.info("Workflow enforcement hooks registered")
    
    async def _detect_and_process_todos(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect todo lists in LLM responses and initiate workflow enforcement."""
        if self.workflow_context.state == WorkflowState.ENFORCING:
            # Already in workflow - check if this is a completion response
            return await self._handle_workflow_response(event_data)
        
        response_content = event_data.get("response", "")
        todos = self._extract_todo_list(response_content)
        
        if todos and len(todos) > 0:
            logger.info(f"Detected {len(todos)} todo items, initiating workflow enforcement")
            
            # Initialize workflow context
            self.workflow_context = WorkflowContext(
                original_request=event_data.get("original_request", ""),
                todo_items=todos,
                state=WorkflowState.TODO_DETECTED,
                llm_response_with_todos=response_content,
                started_at=datetime.now()
            )
            
            # Save workflow state
            await self._save_workflow_state()
            
            # Modify the response to include workflow activation message
            activation_msg = self._create_workflow_activation_message()
            event_data["response"] = f"{response_content}\n\n{activation_msg}"
            
            # Display workflow activation via hook message
            self.renderer.write_hook_message(
                f"[*] Workflow Enforcement Activated - {len(todos)} todos detected"
            )
        
        return event_data
    
    async def _process_user_input(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user input for workflow commands and confirmations."""
        if self.workflow_context.state == WorkflowState.INACTIVE:
            return event_data
            
        user_input = event_data.get("message", "").strip().lower()
        
        # Check for bypass request
        if any(keyword in user_input for keyword in self.bypass_keywords):
            return await self._handle_bypass_request(event_data, user_input)
        
        # Handle workflow state transitions
        if self.workflow_context.state == WorkflowState.TODO_DETECTED:
            if "start workflow" in user_input or "yes" in user_input or "confirm" in user_input:
                return await self._start_workflow_enforcement(event_data)
            elif "no" in user_input or "cancel" in user_input:
                return await self._cancel_workflow(event_data)
        
        elif self.workflow_context.state == WorkflowState.WAITING_CONFIRMATION:
            if "completed" in user_input or "done" in user_input or "finished" in user_input:
                return await self._confirm_todo_completion(event_data)
            elif "failed" in user_input or "error" in user_input:
                return await self._handle_todo_failure(event_data, user_input)
        
        return event_data
    
    async def _inject_workflow_context(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Inject workflow context into LLM requests."""
        if self.workflow_context.state == WorkflowState.ENFORCING:
            current_todo = self._get_current_todo()
            if current_todo:
                context_injection = f"""
                
WORKFLOW ENFORCEMENT ACTIVE:
- Original Request: {self.workflow_context.original_request}
- Current Todo ({current_todo.index + 1}/{len(self.workflow_context.todo_items)}): {current_todo.text}
- Required: Use <terminal> tags for all commands as shown in examples
- Status: {'ATTEMPTED' if current_todo.attempted else 'PENDING'}

You MUST complete this todo item using proper tool calling before proceeding.
"""
                
                # Prepend workflow context to the message
                original_message = event_data.get("message", "")
                event_data["message"] = f"{context_injection}\n\n{original_message}"
        
        return event_data
    
    def _extract_todo_list(self, text: str) -> List[TodoItem]:
        """Extract todo items from markdown text."""
        todos = []
        
        # Pattern to match markdown todo items with optional terminal commands
        todo_pattern = r'^\s*-\s*\[\s*\]\s*(.+?)(?:\s*<terminal>(.+?)</terminal>)?$'
        
        lines = text.split('\n')
        todo_index = 0
        
        for line in lines:
            match = re.match(todo_pattern, line, re.MULTILINE)
            if match:
                todo_text = match.group(1).strip()
                terminal_command = match.group(2).strip() if match.group(2) else None
                
                todos.append(TodoItem(
                    index=todo_index,
                    text=todo_text,
                    terminal_command=terminal_command
                ))
                todo_index += 1
        
        return todos
    
    def _create_workflow_activation_message(self) -> str:
        """Create the workflow activation message."""
        todo_count = len(self.workflow_context.todo_items)
        
        msg = f"""
[*] **WORKFLOW ENFORCEMENT ACTIVATED**

I've detected {todo_count} todo items that require completion. The workflow system will:

1.**Enforce Sequential Completion** - Each todo must be completed in order
2.**Require Tool Calling** - All commands must use <terminal> tags  
3.**Wait for Confirmation** - You must confirm each completion
4.**Track Progress** - Monitor completion status
5.**Allow Bypass** - Use keywords: {', '.join(self.bypass_keywords)}

**Next Steps:**
- Reply "**start workflow**" to begin enforcement
- Reply "**cancel**" to proceed without workflow
- Each todo will be presented individually for completion

**Current Todo Queue:**
{self._format_todo_queue()}
"""
        return msg
    
    def _format_todo_queue(self) -> str:
        """Format the todo queue for display."""
        lines = []
        for i, todo in enumerate(self.workflow_context.todo_items):
            status = "[DONE]" if todo.completed else "[ACTIVE]" if i == self.workflow_context.current_todo_index else "[PENDING]"
            command_info = f" `{todo.terminal_command}`" if todo.terminal_command else ""
            lines.append(f"{status} **{i+1}.** {todo.text}{command_info}")
        return '\n'.join(lines)
    
    async def _start_workflow_enforcement(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start enforcing workflow completion."""
        self.workflow_context.state = WorkflowState.ENFORCING
        await self._save_workflow_state()
        
        # Present first todo
        first_todo = self._get_current_todo()
        if first_todo:
            first_todo.attempted = True
            first_todo.timestamp_started = datetime.now()
            
            enforcement_msg = self._create_todo_enforcement_message(first_todo)
            
            # Replace user message with workflow enforcement
            event_data["message"] = enforcement_msg
            
            self.renderer.write_hook_message(
                f"Workflow Started - Todo 1/{len(self.workflow_context.todo_items)}: {first_todo.text[:50]}..."
            )
        
        return event_data
    
    async def _cancel_workflow(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel workflow enforcement."""
        self.workflow_context.state = WorkflowState.INACTIVE
        await self._save_workflow_state()
        
        event_data["message"] = "Workflow enforcement cancelled. Proceeding with normal operation."
        
        self.renderer.write_hook_message("Workflow Enforcement Cancelled")
        return event_data
    
    def _create_todo_enforcement_message(self, todo_item: TodoItem) -> str:
        """Create enforcement message for a specific todo."""
        progress = f"{todo_item.index + 1}/{len(self.workflow_context.todo_items)}"
        
        msg = f"""
**WORKFLOW ENFORCEMENT - TODO {progress}**

**Original Request:** {self.workflow_context.original_request}

**Current Todo:** {todo_item.text}

**Requirements:**
- Complete this todo item fully
- Use <terminal> tags for all commands (required!)
- Show your work with actual tool execution  
- Reply "**completed**" when finished

"""
        
        if todo_item.terminal_command:
            msg += f"**Suggested Command:** `{todo_item.terminal_command}`\n\n"
        
        msg += f"""**Bypass Options:**
- Reply "**bypass [reason]**" if blocked
- Reply "**failed [reason]**" if unable to complete

**Progress:** {self._format_todo_queue()}

---

**Now complete this todo using proper <terminal> tags and confirm when done.**
"""
        
        return msg
    
    async def _confirm_todo_completion(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle todo completion confirmation."""
        current_todo = self._get_current_todo()
        if not current_todo:
            return event_data
        
        # Mark current todo as completed
        current_todo.completed = True
        current_todo.confirmed = True
        current_todo.timestamp_completed = datetime.now()
        
        # Move to next todo or complete workflow
        self.workflow_context.current_todo_index += 1
        
        if self.workflow_context.current_todo_index >= len(self.workflow_context.todo_items):
            # Workflow completed!
            return await self._complete_workflow(event_data)
        else:
            # Present next todo
            next_todo = self._get_current_todo()
            next_todo.attempted = True
            next_todo.timestamp_started = datetime.now()
            
            next_msg = self._create_todo_enforcement_message(next_todo)
            event_data["message"] = next_msg
            
            self.renderer.write_hook_message(
                f"Todo {current_todo.index + 1} completed! Moving to Todo {next_todo.index + 1}/{len(self.workflow_context.todo_items)}"
            )
        
        await self._save_workflow_state()
        return event_data
    
    async def _complete_workflow(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete the workflow successfully."""
        self.workflow_context.state = WorkflowState.COMPLETED
        self.workflow_context.completed_at = datetime.now()
        
        completion_stats = self._generate_completion_stats()
        
        completion_msg = f"""
**WORKFLOW ENFORCEMENT COMPLETED!**

**Original Request:** {self.workflow_context.original_request}

**Results:**
- **All {len(self.workflow_context.todo_items)} todos completed successfully**
- **Tool calling enforced throughout**
- **Total time:** {completion_stats['duration']}
- **Success rate:** {completion_stats['success_rate']}%

{completion_stats['summary']}

**Workflow enforcement is now deactivated.** You can continue with normal operation.
"""
        
        event_data["message"] = completion_msg
        
        self.renderer.write_hook_message("Workflow Enforcement Completed Successfully!")
        
        # Reset workflow state
        self.workflow_context = WorkflowContext()
        await self._save_workflow_state()
        
        return event_data
    
    async def _handle_bypass_request(self, event_data: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Handle workflow bypass requests."""
        bypass_reason = user_input.replace("bypass", "").replace("skip", "").strip()
        
        self.workflow_context.bypass_requested = True
        self.workflow_context.bypass_reason = bypass_reason
        self.workflow_context.state = WorkflowState.BLOCKED
        
        bypass_msg = f"""
[!] **WORKFLOW BYPASS ACTIVATED**

**Reason:** {bypass_reason or "No reason provided"}

**Options:**
1. Reply "**resume**" to continue workflow from current todo
2. Reply "**abort**" to completely cancel workflow enforcement  
3. Continue with normal operation - workflow remains paused

**Current Progress:** {self._format_todo_queue()}
"""
        
        event_data["message"] = bypass_msg
        
        self.renderer.write_hook_message(f"[!] Workflow Bypassed: {bypass_reason}")
        
        await self._save_workflow_state()
        return event_data
    
    async def _handle_todo_failure(self, event_data: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Handle todo failure reports."""
        current_todo = self._get_current_todo()
        if current_todo:
            failure_reason = user_input.replace("failed", "").replace("error", "").strip()
            current_todo.failure_reason = failure_reason
            
            failure_msg = f"""
**TODO FAILURE REPORTED**

**Failed Todo:** {current_todo.text}
**Reason:** {failure_reason or "No reason provided"}

**Options:**
1. Reply "**retry**" to attempt this todo again
2. Reply "**skip**" to mark as failed and move to next todo
3. Reply "**bypass workflow**" to exit workflow enforcement

Would you like to retry this todo or skip it?
"""
            
            event_data["message"] = failure_msg
            
            self.renderer.write_hook_message(f"Todo Failed: {current_todo.text[:50]}...")
        
        return event_data
    
    def _get_current_todo(self) -> Optional[TodoItem]:
        """Get the current todo item being worked on."""
        if (0 <= self.workflow_context.current_todo_index < len(self.workflow_context.todo_items)):
            return self.workflow_context.todo_items[self.workflow_context.current_todo_index]
        return None
    
    def _generate_completion_stats(self) -> Dict[str, Any]:
        """Generate workflow completion statistics."""
        completed_todos = [todo for todo in self.workflow_context.todo_items if todo.completed]
        failed_todos = [todo for todo in self.workflow_context.todo_items if todo.failure_reason]
        
        duration = "N/A"
        if self.workflow_context.started_at and self.workflow_context.completed_at:
            delta = self.workflow_context.completed_at - self.workflow_context.started_at
            duration = f"{delta.total_seconds():.1f} seconds"
        
        success_rate = (len(completed_todos) / len(self.workflow_context.todo_items)) * 100 if self.workflow_context.todo_items else 0
        
        summary_lines = []
        for i, todo in enumerate(self.workflow_context.todo_items):
            status = "COMPLETED" if todo.completed else "FAILED" if todo.failure_reason else "SKIPPED"
            summary_lines.append(f"  {i+1}. {todo.text[:60]}... - {status}")
        
        return {
            "duration": duration,
            "success_rate": int(success_rate),
            "completed_count": len(completed_todos),
            "failed_count": len(failed_todos),
            "summary": "\n".join(summary_lines)
        }
    
    async def _save_workflow_state(self):
        """Save workflow state to persistent storage."""
        try:
            await self.state_manager.set_state("workflow_enforcement", {
                "workflow_context": {
                    "original_request": self.workflow_context.original_request,
                    "current_todo_index": self.workflow_context.current_todo_index,
                    "state": self.workflow_context.state.value,
                    "bypass_requested": self.workflow_context.bypass_requested,
                    "bypass_reason": self.workflow_context.bypass_reason,
                    "todo_items": [
                        {
                            "index": todo.index,
                            "text": todo.text,
                            "terminal_command": todo.terminal_command,
                            "completed": todo.completed,
                            "confirmed": todo.confirmed,
                            "attempted": todo.attempted,
                            "failure_reason": todo.failure_reason
                        }
                        for todo in self.workflow_context.todo_items
                    ]
                }
            })
        except Exception as e:
            logger.warning(f"Failed to save workflow state: {e}")
    
    async def _load_workflow_state(self):
        """Load workflow state from persistent storage."""
        try:
            state_data = await self.state_manager.get_state("workflow_enforcement")
            if state_data and "workflow_context" in state_data:
                context_data = state_data["workflow_context"]
                
                # Reconstruct workflow context
                self.workflow_context.original_request = context_data.get("original_request", "")
                self.workflow_context.current_todo_index = context_data.get("current_todo_index", 0)
                self.workflow_context.state = WorkflowState(context_data.get("state", WorkflowState.INACTIVE.value))
                self.workflow_context.bypass_requested = context_data.get("bypass_requested", False)
                self.workflow_context.bypass_reason = context_data.get("bypass_reason", "")
                
                # Reconstruct todo items
                todo_items_data = context_data.get("todo_items", [])
                self.workflow_context.todo_items = [
                    TodoItem(
                        index=item["index"],
                        text=item["text"],
                        terminal_command=item.get("terminal_command"),
                        completed=item.get("completed", False),
                        confirmed=item.get("confirmed", False),
                        attempted=item.get("attempted", False),
                        failure_reason=item.get("failure_reason")
                    )
                    for item in todo_items_data
                ]
                
                if self.workflow_context.state != WorkflowState.INACTIVE:
                    logger.info(f"Restored workflow state: {self.workflow_context.state.value}")
        except Exception as e:
            logger.warning(f"Failed to load workflow state: {e}")
    
    async def _handle_workflow_response(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle LLM responses during active workflow enforcement."""
        response_content = event_data.get("response", "")
        
        # Check if response contains terminal commands (indicates compliance)
        has_terminal_commands = "<terminal>" in response_content and "</terminal>" in response_content
        
        current_todo = self._get_current_todo()
        if current_todo and not current_todo.completed:
            if has_terminal_commands:
                # Good! LLM is using terminal commands
                # Transition to waiting for confirmation
                self.workflow_context.state = WorkflowState.WAITING_CONFIRMATION
                
                confirmation_prompt = f"""
                
---
**WORKFLOW CHECK**: I can see you've used terminal commands to work on this todo.

**Todo**: {current_todo.text}

Please reply "**completed**" when you've finished this todo item, or "**failed [reason]**" if you encountered issues.
"""
                event_data["response"] = f"{response_content}{confirmation_prompt}"
                
            else:
                # LLM not using terminal commands - enforce compliance
                enforcement_reminder = f"""
                
---
**WORKFLOW VIOLATION**: You must use <terminal> tags for commands!

**Current Todo**: {current_todo.text}

Please redo this todo using proper <terminal>command</terminal> tags as shown in the examples.
"""
                event_data["response"] = f"{response_content}{enforcement_reminder}"
        
        return event_data
    
    async def shutdown(self):
        """Cleanup when plugin shuts down."""
        await self._save_workflow_state()
        logger.info("Workflow enforcement plugin shutdown")