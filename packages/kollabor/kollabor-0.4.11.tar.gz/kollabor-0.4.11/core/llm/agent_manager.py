"""
Agent and Skill Manager.

Manages agents defined in .kollabor-cli/agents/ directories:
- Each agent has a system_prompt.md and optional skill files
- Skills are loaded dynamically and appended to system prompt
- Supports both local (project) and global (user) agent directories

Directory structure:
    .kollabor-cli/agents/
        default/
            system_prompt.md
        lint-editor/
            system_prompt.md
            agent.json          # Optional config
            create-tasks.md     # Skill file
            fix-file.md         # Another skill
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Skill:
    """
    A skill that can be loaded into an agent's context.

    Skills are markdown files containing instructions or context
    that can be dynamically loaded during a session.

    Attributes:
        name: Skill identifier (filename without extension)
        content: Full content of the skill file
        file_path: Path to the skill file
        description: Optional description extracted from file header
    """

    name: str
    content: str
    file_path: Path
    description: str = ""

    @classmethod
    def from_file(cls, file_path: Path) -> Optional["Skill"]:
        """
        Load skill from a markdown file.

        Extracts description from HTML comment at start of file:
        <!-- Description text here -->

        Args:
            file_path: Path to the .md file

        Returns:
            Skill instance or None on error
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to read skill file {file_path}: {e}")
            return None

        # Extract description from HTML comment at start
        description = ""
        lines = content.split("\n")
        if lines and lines[0].strip().startswith("<!--"):
            comment_lines = []
            for line in lines:
                comment_lines.append(line)
                if "-->" in line:
                    break
            comment_text = "\n".join(comment_lines)
            description = (
                comment_text.replace("<!--", "")
                .replace("-->", "")
                .strip()
            )

        return cls(
            name=file_path.stem,
            content=content,
            file_path=file_path,
            description=description,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert skill to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "file_path": str(self.file_path),
        }


@dataclass
class Agent:
    """
    An agent configuration with system prompt and available skills.

    Agents are loaded from directories containing:
    - system_prompt.md (required)
    - agent.json (optional config)
    - *.md files (skills)

    Attributes:
        name: Agent identifier (directory name)
        directory: Path to agent directory
        system_prompt: Base system prompt content
        skills: Available skills (name -> Skill)
        active_skills: Currently loaded skill names
        profile: Optional preferred LLM profile
        description: Human-readable description
    """

    name: str
    directory: Path
    system_prompt: str
    skills: Dict[str, Skill] = field(default_factory=dict)
    active_skills: List[str] = field(default_factory=list)
    profile: Optional[str] = None
    description: str = ""

    @classmethod
    def from_directory(cls, agent_dir: Path) -> Optional["Agent"]:
        """
        Load agent from a directory.

        Args:
            agent_dir: Path to agent directory

        Returns:
            Agent instance or None if invalid
        """
        if not agent_dir.is_dir():
            return None

        # Load system prompt (required)
        system_prompt_file = agent_dir / "system_prompt.md"
        if not system_prompt_file.exists():
            logger.warning(f"Agent {agent_dir.name} missing system_prompt.md")
            return None

        try:
            system_prompt = system_prompt_file.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to read system prompt for {agent_dir.name}: {e}")
            return None

        # Load skills (all .md files except system_prompt.md)
        skills: Dict[str, Skill] = {}
        for md_file in agent_dir.glob("*.md"):
            if md_file.name != "system_prompt.md":
                skill = Skill.from_file(md_file)
                if skill:
                    skills[skill.name] = skill

        # Load optional config
        profile = None
        description = ""
        config_file = agent_dir / "agent.json"
        if config_file.exists():
            try:
                config = json.loads(config_file.read_text(encoding="utf-8"))
                profile = config.get("profile")
                description = config.get("description", "")
            except Exception as e:
                logger.warning(f"Failed to load agent config for {agent_dir.name}: {e}")

        return cls(
            name=agent_dir.name,
            directory=agent_dir,
            system_prompt=system_prompt,
            skills=skills,
            profile=profile,
            description=description,
        )

    def get_full_system_prompt(self) -> str:
        """
        Get system prompt with active skills appended.

        Skills are added under "## Skill: {name}" headers.

        Returns:
            Combined system prompt string
        """
        parts = [self.system_prompt]

        for skill_name in self.active_skills:
            if skill_name in self.skills:
                skill = self.skills[skill_name]
                parts.append(f"\n\n## Skill: {skill_name}\n\n{skill.content}")

        return "\n".join(parts)

    def load_skill(self, skill_name: str) -> bool:
        """
        Load a skill into active context.

        Args:
            skill_name: Name of skill to load

        Returns:
            True if loaded, False if not found
        """
        if skill_name not in self.skills:
            logger.error(f"Skill not found: {skill_name}")
            return False

        if skill_name not in self.active_skills:
            self.active_skills.append(skill_name)
            logger.info(f"Loaded skill: {skill_name}")
        return True

    def unload_skill(self, skill_name: str) -> bool:
        """
        Unload a skill from active context.

        Args:
            skill_name: Name of skill to unload

        Returns:
            True if unloaded, False if not loaded
        """
        if skill_name in self.active_skills:
            self.active_skills.remove(skill_name)
            logger.info(f"Unloaded skill: {skill_name}")
            return True
        return False

    def list_skills(self) -> List[Skill]:
        """Get list of available skills."""
        return list(self.skills.values())

    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a specific skill by name."""
        return self.skills.get(name)

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation."""
        return {
            "name": self.name,
            "directory": str(self.directory),
            "description": self.description,
            "profile": self.profile,
            "skills": [s.to_dict() for s in self.skills.values()],
            "active_skills": self.active_skills,
        }


class AgentManager:
    """
    Manages agent discovery, loading, and skill management.

    Searches for agents in:
    1. Local: .kollabor-cli/agents/ (project-specific, higher priority)
    2. Global: ~/.kollabor-cli/agents/ (user defaults)

    Local agents override global agents with the same name.
    """

    def __init__(self, config=None):
        """
        Initialize agent manager.

        Args:
            config: Configuration object (optional)
        """
        self.config = config
        self._agents: Dict[str, Agent] = {}
        self._active_agent_name: Optional[str] = None

        # Agent directories (in discovery order, lowest to highest priority)
        # 1. Global: ~/.kollabor-cli/agents/ (user defaults)
        # 2. Local: .kollabor-cli/agents/ (project-specific, where agents are created)
        self.global_agents_dir = Path.home() / ".kollabor-cli" / "agents"
        self.local_agents_dir = Path.cwd() / ".kollabor-cli" / "agents"

        self._discover_agents()

    def _discover_agents(self) -> None:
        """Discover all available agents from directories."""
        # Load from global first (lowest priority)
        if self.global_agents_dir.exists():
            for agent_dir in self.global_agents_dir.iterdir():
                if agent_dir.is_dir():
                    agent = Agent.from_directory(agent_dir)
                    if agent:
                        self._agents[agent.name] = agent
                        logger.debug(f"Discovered global agent: {agent.name}")

        # Load from .kollabor-cli/agents/ (higher priority, overrides global)
        if self.local_agents_dir.exists():
            for agent_dir in self.local_agents_dir.iterdir():
                if agent_dir.is_dir():
                    agent = Agent.from_directory(agent_dir)
                    if agent:
                        self._agents[agent.name] = agent
                        logger.debug(f"Discovered local agent: {agent.name}")

        logger.info(f"Discovered {len(self._agents)} agents")

    def get_agent(self, name: str) -> Optional[Agent]:
        """
        Get agent by name.

        Args:
            name: Agent name

        Returns:
            Agent instance or None if not found
        """
        return self._agents.get(name)

    def get_active_agent(self) -> Optional[Agent]:
        """
        Get the currently active agent.

        Returns:
            Active Agent or "default" agent or None
        """
        if self._active_agent_name:
            agent = self._agents.get(self._active_agent_name)
            if agent:
                return agent

        # Fall back to "default" agent
        return self._agents.get("default")

    def set_active_agent(self, name: str) -> bool:
        """
        Set the active agent.

        Args:
            name: Agent name to activate

        Returns:
            True if successful, False if agent not found
        """
        if name not in self._agents:
            logger.error(f"Agent not found: {name}")
            return False

        old_agent = self._active_agent_name
        self._active_agent_name = name
        logger.info(f"Activated agent: {old_agent} -> {name}")
        return True

    def clear_active_agent(self) -> None:
        """Clear the active agent (use default or no agent)."""
        self._active_agent_name = None
        logger.info("Cleared active agent")

    def list_agents(self) -> List[Agent]:
        """
        List all available agents.

        Returns:
            List of Agent instances
        """
        return list(self._agents.values())

    def get_agent_names(self) -> List[str]:
        """
        Get list of agent names.

        Returns:
            List of agent name strings
        """
        return list(self._agents.keys())

    def has_agent(self, name: str) -> bool:
        """Check if an agent exists."""
        return name in self._agents

    def list_skills(self, agent_name: Optional[str] = None) -> List[Skill]:
        """
        List skills for an agent.

        Args:
            agent_name: Agent name (default: active agent)

        Returns:
            List of Skill instances
        """
        agent = self._agents.get(agent_name) if agent_name else self.get_active_agent()
        if not agent:
            return []
        return agent.list_skills()

    def load_skill(
        self, skill_name: str, agent_name: Optional[str] = None
    ) -> bool:
        """
        Load a skill into an agent's active context.

        Args:
            skill_name: Name of skill to load
            agent_name: Agent name (default: active agent)

        Returns:
            True if loaded, False otherwise
        """
        agent = self._agents.get(agent_name) if agent_name else self.get_active_agent()
        if not agent:
            logger.error("No agent available to load skill")
            return False

        return agent.load_skill(skill_name)

    def unload_skill(
        self, skill_name: str, agent_name: Optional[str] = None
    ) -> bool:
        """
        Unload a skill from an agent's active context.

        Args:
            skill_name: Name of skill to unload
            agent_name: Agent name (default: active agent)

        Returns:
            True if unloaded, False otherwise
        """
        agent = self._agents.get(agent_name) if agent_name else self.get_active_agent()
        if not agent:
            return False

        return agent.unload_skill(skill_name)

    def get_system_prompt(self) -> Optional[str]:
        """
        Get the full system prompt for the active agent.

        Includes base system prompt and active skills.

        Returns:
            System prompt string or None if no agent
        """
        agent = self.get_active_agent()
        if agent:
            return agent.get_full_system_prompt()
        return None

    def get_preferred_profile(self) -> Optional[str]:
        """
        Get the preferred LLM profile for the active agent.

        Returns:
            Profile name or None
        """
        agent = self.get_active_agent()
        if agent:
            return agent.profile
        return None

    @property
    def active_agent_name(self) -> Optional[str]:
        """Get the name of the active agent."""
        return self._active_agent_name

    def is_active(self, name: str) -> bool:
        """Check if an agent is the active one."""
        return name == self._active_agent_name

    def get_agent_summary(self, name: Optional[str] = None) -> str:
        """
        Get a human-readable summary of an agent.

        Args:
            name: Agent name (default: active agent)

        Returns:
            Formatted summary string
        """
        agent = self._agents.get(name) if name else self.get_active_agent()
        if not agent:
            return f"Agent '{name}' not found" if name else "No active agent"

        lines = [
            f"Agent: {agent.name}",
            f"  Directory: {agent.directory}",
        ]
        if agent.description:
            lines.append(f"  Description: {agent.description}")
        if agent.profile:
            lines.append(f"  Preferred Profile: {agent.profile}")

        skills = agent.list_skills()
        if skills:
            lines.append(f"  Skills ({len(skills)}):")
            for skill in skills:
                active = "*" if skill.name in agent.active_skills else " "
                desc = f" - {skill.description[:40]}..." if skill.description else ""
                lines.append(f"    [{active}] {skill.name}{desc}")
        else:
            lines.append("  Skills: none")

        return "\n".join(lines)

    def refresh(self) -> None:
        """Re-discover agents from directories."""
        self._agents.clear()
        self._discover_agents()

    def create_agent(
        self,
        name: str,
        description: str = "",
        profile: Optional[str] = None,
        system_prompt: str = "",
    ) -> Optional[Agent]:
        """
        Create a new agent with directory structure.

        Creates .kollabor-cli/agents/<name>/ directory with:
        - system_prompt.md
        - agent.json (if profile or description specified)

        Args:
            name: Agent name (becomes directory name)
            description: Agent description
            profile: Preferred LLM profile name
            system_prompt: Base system prompt content

        Returns:
            Created Agent or None on failure
        """
        import json

        # Check if agent already exists
        if name in self._agents:
            logger.warning(f"Agent already exists: {name}")
            return None

        # Create in .kollabor-cli/agents/ directory
        agent_dir = self.local_agents_dir / name

        if agent_dir.exists():
            logger.warning(f"Agent directory already exists: {agent_dir}")
            return None

        try:
            # Create directory structure
            agent_dir.mkdir(parents=True, exist_ok=True)

            # Create system_prompt.md
            default_prompt = system_prompt or f"""# {name.replace('-', ' ').title()} Agent

You are a specialized assistant.

## Your Mission

{description or 'Help users with their tasks.'}

## Approach

1. Analyze the user's request
2. Provide clear, actionable guidance
3. Follow best practices
"""
            prompt_file = agent_dir / "system_prompt.md"
            prompt_file.write_text(default_prompt, encoding="utf-8")

            # Create agent.json if profile or description specified
            if profile or description:
                agent_json = {
                    "description": description or f"Agent: {name}",
                }
                if profile and profile != "(none)":
                    agent_json["profile"] = profile

                json_file = agent_dir / "agent.json"
                json_file.write_text(
                    json.dumps(agent_json, indent=4, ensure_ascii=False),
                    encoding="utf-8"
                )

            # Load the newly created agent
            agent = Agent.from_directory(agent_dir)
            if agent:
                self._agents[name] = agent
                logger.info(f"Created agent: {name} at {agent_dir}")
                return agent

            return None

        except Exception as e:
            logger.error(f"Failed to create agent {name}: {e}")
            # Clean up on failure
            if agent_dir.exists():
                import shutil
                shutil.rmtree(agent_dir, ignore_errors=True)
            return None
