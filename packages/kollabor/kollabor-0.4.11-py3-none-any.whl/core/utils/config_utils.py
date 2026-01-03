"""Configuration utilities for Kollabor."""

import os
import sys
from pathlib import Path
import logging
import shutil

logger = logging.getLogger(__name__)

# Platform check
IS_WINDOWS = sys.platform == "win32"

# CLI override for system prompt file (set via --system-prompt argument)
_cli_system_prompt_file: str | None = None


def set_cli_system_prompt_file(file_path: str | None) -> None:
    """Set the CLI override for system prompt file.

    Args:
        file_path: Path to the system prompt file, or None to clear
    """
    global _cli_system_prompt_file
    _cli_system_prompt_file = file_path
    if file_path:
        logger.info(f"CLI system prompt override set: {file_path}")


def _resolve_system_prompt_path(filename: str) -> Path | None:
    """Resolve a system prompt filename to a full path.

    Searches in order:
    1. As-is (if absolute path or exists in cwd)
    2. Local .kollabor-cli/agents/default/
    3. Global ~/.kollabor-cli/agents/default/

    Args:
        filename: The filename or path provided by the user

    Returns:
        Resolved Path if found, None otherwise
    """
    # Expand ~ in path
    expanded = Path(filename).expanduser()

    # 1. Check as-is (absolute path or relative from cwd)
    if expanded.exists():
        return expanded

    # If it's an absolute path that doesn't exist, don't search further
    if expanded.is_absolute():
        return None

    # Get just the filename for searching in directories
    name = expanded.name

    # Also try with .md extension if not present
    names_to_try = [name]
    if not name.endswith('.md'):
        names_to_try.append(f"{name}.md")

    # 2. Local .kollabor-cli/agents/default/
    local_agent_dir = Path.cwd() / ".kollabor-cli" / "agents" / "default"
    for n in names_to_try:
        candidate = local_agent_dir / n
        if candidate.exists():
            return candidate

    # 3. Global ~/.kollabor-cli/agents/default/
    global_agent_dir = Path.home() / ".kollabor-cli" / "agents" / "default"
    for n in names_to_try:
        candidate = global_agent_dir / n
        if candidate.exists():
            return candidate

    return None


def get_config_directory() -> Path:
    """Get the Kollabor configuration directory.

    Resolution order:
    1. Local .kollabor-cli/ in current directory (project-specific override)
    2. Global ~/.kollabor-cli/ (default for most users)

    Returns:
        Path to the configuration directory
    """
    local_config_dir = Path.cwd() / ".kollabor-cli"
    global_config_dir = Path.home() / ".kollabor-cli"

    if local_config_dir.exists():
        return local_config_dir
    else:
        return global_config_dir


def ensure_config_directory() -> Path:
    """Get and ensure the configuration directory exists.

    Returns:
        Path to the configuration directory
    """
    config_dir = get_config_directory()
    config_dir.mkdir(exist_ok=True)
    return config_dir


def get_system_prompt_path() -> Path:
    """Get the system prompt file path, preferring env var over local/global.

    Resolution order:
    1. KOLLABOR_SYSTEM_PROMPT_FILE environment variable (custom file path)
    2. Local .kollabor-cli/agents/default/system_prompt.md (project-specific)
    3. Global ~/.kollabor-cli/agents/default/system_prompt.md (global default)

    Returns:
        Path to the system prompt file
    """
    # Check for environment variable override
    env_prompt_file = os.environ.get("KOLLABOR_SYSTEM_PROMPT_FILE")
    if env_prompt_file:
        env_path = Path(env_prompt_file).expanduser()
        if env_path.exists():
            logger.debug(f"Using system prompt from KOLLABOR_SYSTEM_PROMPT_FILE: {env_path}")
            return env_path
        else:
            logger.warning(f"KOLLABOR_SYSTEM_PROMPT_FILE points to non-existent file: {env_path}")

    local_config_dir = Path.cwd() / ".kollabor-cli"
    global_config_dir = Path.home() / ".kollabor-cli"

    # New agent-based paths
    local_agent_prompt = local_config_dir / "agents" / "default" / "system_prompt.md"
    global_agent_prompt = global_config_dir / "agents" / "default" / "system_prompt.md"

    # On Windows, prefer default_win.md if it exists (in agent directory)
    if IS_WINDOWS:
        local_win_prompt = local_config_dir / "agents" / "default" / "system_prompt_win.md"
        global_win_prompt = global_config_dir / "agents" / "default" / "system_prompt_win.md"

        if local_win_prompt.exists():
            logger.debug(f"Using Windows-specific system prompt: {local_win_prompt}")
            return local_win_prompt
        if global_win_prompt.exists():
            logger.debug(f"Using Windows-specific system prompt: {global_win_prompt}")
            return global_win_prompt

    # If local exists, use it (override)
    if local_agent_prompt.exists():
        return local_agent_prompt
    # Otherwise use global
    else:
        return global_agent_prompt


def get_system_prompt_content() -> str:
    """Get the system prompt content, checking CLI args, env vars, and files.

    Resolution order:
    1. CLI --system-prompt argument (highest priority)
    2. KOLLABOR_SYSTEM_PROMPT environment variable (direct string)
    3. KOLLABOR_SYSTEM_PROMPT_FILE environment variable (custom file path)
    4. Local .kollabor-cli/agents/default/system_prompt.md (project-specific override)
    5. Global ~/.kollabor-cli/agents/default/system_prompt.md (global default)
    6. Fallback to minimal default

    Returns:
        System prompt content as string
    """
    global _cli_system_prompt_file

    # Check for CLI override (highest priority)
    if _cli_system_prompt_file:
        cli_path = _resolve_system_prompt_path(_cli_system_prompt_file)
        if cli_path and cli_path.exists():
            try:
                content = cli_path.read_text(encoding='utf-8')
                logger.info(f"Loaded system prompt from CLI argument: {cli_path}")
                return content
            except Exception as e:
                logger.error(f"Failed to read CLI system prompt from {cli_path}: {e}")
        else:
            logger.error(f"CLI system prompt file not found: {_cli_system_prompt_file}")
            # Don't fall through - this is an explicit user request, so fail clearly
            return f"""[SYSTEM PROMPT LOAD FAILURE]

The system prompt file specified via --system-prompt was not found:
  {_cli_system_prompt_file}

Searched in:
  - Current directory
  - .kollabor-cli/system_prompt/
  - ~/.kollabor-cli/system_prompt/

Please check the file path and try again.

I'll do my best to help, but my responses may not follow the expected format.
"""

    # Check for direct environment variable string
    env_prompt = os.environ.get("KOLLABOR_SYSTEM_PROMPT")
    if env_prompt:
        logger.debug("Using system prompt from KOLLABOR_SYSTEM_PROMPT environment variable")
        return env_prompt

    # Otherwise read from file (respects KOLLABOR_SYSTEM_PROMPT_FILE via get_system_prompt_path)
    system_prompt_path = get_system_prompt_path()
    if system_prompt_path.exists():
        try:
            content = system_prompt_path.read_text(encoding='utf-8')
            logger.info(f"Loaded system prompt from: {system_prompt_path}")
            return content
        except Exception as e:
            logger.error(f"Failed to read system prompt from {system_prompt_path}: {e}")
            return get_default_system_prompt()
    else:
        logger.warning(f"System prompt file not found: {system_prompt_path}, using default")
        return get_default_system_prompt()


def get_default_system_prompt() -> str:
    """Get the default system prompt content when no file exists.

    Returns a minimal fallback that alerts the user about the missing prompt.

    Returns:
        Default system prompt string
    """
    # Emergency fallback - alert user that system prompt failed to load
    logger.warning("Using emergency fallback system prompt - this should not happen in production")
    return """[SYSTEM PROMPT LOAD FAILURE]

You are Kollabor, an AI coding assistant. However, your full system prompt
failed to load. This is a critical configuration issue.

IMPORTANT: Alert the user immediately about this problem:

"Warning: My system prompt failed to load properly. I'm operating in a limited
fallback mode. Please check your Kollabor installation:

1. Verify ~/.kollabor-cli/agents/default/system_prompt.md exists
2. Run 'kollab' to trigger automatic initialization
3. Review the logs at ~/.kollabor-cli/logs/kollabor.log for errors

I'll do my best to help, but my responses may not follow the expected format
until this is resolved."

Despite this issue, try to be helpful and assist the user with their request.
"""


def initialize_system_prompt() -> None:
    """Initialize agents from bundled seed folder.

    Copies ALL agents from bundled agents/ folder to global ~/.kollabor-cli/agents/
    on first install, then copies default agent to local .kollabor-cli/agents/.

    Priority order:
    1. If local .kollabor-cli/agents/default/ exists -> use local (already set up)
    2. Migrate from old .kollabor-cli/system_prompt/default.md if it exists
    3. Copy ALL agents from seed folder to global ~/.kollabor-cli/agents/
    4. Copy default agent from global to local

    This ensures global has all bundled agents, and local has the default.
    """
    try:
        local_config_dir = Path.cwd() / ".kollabor-cli"
        global_config_dir = Path.home() / ".kollabor-cli"

        local_agents_dir = local_config_dir / "agents"
        global_agents_dir = global_config_dir / "agents"
        local_default_dir = local_agents_dir / "default"
        global_default_dir = global_agents_dir / "default"

        # Old legacy directories (for migration)
        old_local_prompt_dir = local_config_dir / "system_prompt"
        old_global_prompt_dir = global_config_dir / "system_prompt"

        # Step 1: Check if local default agent already exists
        local_prompt_file = local_default_dir / "system_prompt.md"
        if local_prompt_file.exists():
            logger.info(f"Using local system prompt from: {local_prompt_file}")
            return

        # Step 2: Migrate from old local system_prompt/ if it exists
        old_local_default = old_local_prompt_dir / "default.md"
        if old_local_default.exists():
            logger.info(f"Migrating system prompt from old location: {old_local_default}")
            _migrate_old_prompt_to_agent(old_local_default, local_default_dir)
            return

        # Step 3: Ensure global agents directory has all seed agents
        _copy_seed_agents_to_global(global_agents_dir, old_global_prompt_dir)

        # Step 4: Copy default agent from global to local
        global_prompt_file = global_default_dir / "system_prompt.md"
        if global_prompt_file.exists():
            _copy_agent_prompt_to_local(global_default_dir, local_default_dir)
        else:
            # Fallback: create local directly from seed
            _create_agent_from_defaults(local_default_dir)

    except Exception as e:
        logger.error(f"Failed to initialize system prompt: {e}")


def _copy_seed_agents_to_global(global_agents_dir: Path, old_global_prompt_dir: Path) -> None:
    """Copy all agents from bundled seed folder to global agents directory.

    Args:
        global_agents_dir: Target global agents directory (~/.kollabor-cli/agents/)
        old_global_prompt_dir: Old system_prompt dir for migration
    """
    # Find bundled seed agents folder
    package_dir = Path(__file__).parent.parent.parent
    seed_agents_dir = package_dir / "agents"

    if not seed_agents_dir.exists():
        # Fallback for development mode
        seed_agents_dir = Path.cwd() / "agents"

    if not seed_agents_dir.exists():
        logger.warning("No seed agents folder found")
        # Try migration from old location
        old_global_default = old_global_prompt_dir / "default.md"
        if old_global_default.exists():
            logger.info(f"Migrating global system prompt from old location: {old_global_default}")
            _migrate_old_prompt_to_agent(old_global_default, global_agents_dir / "default")
        return

    global_agents_dir.mkdir(parents=True, exist_ok=True)

    # Copy each agent from seed to global
    for agent_dir in seed_agents_dir.iterdir():
        if agent_dir.is_dir():
            target_agent_dir = global_agents_dir / agent_dir.name
            if not target_agent_dir.exists():
                target_agent_dir.mkdir(parents=True, exist_ok=True)
                for item in agent_dir.iterdir():
                    if item.is_file():
                        target_file = target_agent_dir / item.name
                        if not target_file.exists():
                            shutil.copy2(item, target_file)
                            logger.debug(f"Copied seed agent file: {agent_dir.name}/{item.name}")
                logger.info(f"Installed seed agent to global: {agent_dir.name}")


def _migrate_old_prompt_to_agent(old_prompt_file: Path, agent_dir: Path) -> None:
    """Migrate an old-style system prompt to new agent directory structure.

    Args:
        old_prompt_file: Path to old default.md file
        agent_dir: Target agent directory (e.g., .kollabor-cli/agents/default/)
    """
    agent_dir.mkdir(parents=True, exist_ok=True)

    new_prompt_file = agent_dir / "system_prompt.md"
    if not new_prompt_file.exists():
        shutil.copy2(old_prompt_file, new_prompt_file)
        logger.info(f"Migrated system prompt to: {new_prompt_file}")

        # Create agent.json with default config
        agent_json = agent_dir / "agent.json"
        if not agent_json.exists():
            import json
            agent_config = {
                "name": "default",
                "description": "Default agent with standard system prompt",
                "profile": None
            }
            agent_json.write_text(json.dumps(agent_config, indent=2), encoding='utf-8')
            logger.info(f"Created agent config: {agent_json}")


def _create_agent_from_defaults(agent_dir: Path) -> None:
    """Create default agent from bundled seed agents folder.

    Copies from bundled agents/<agent_name>/ to target directory.

    Args:
        agent_dir: Agent directory to create (e.g., ~/.kollabor-cli/agents/default/)
    """
    agent_name = agent_dir.name  # e.g., "default"

    # Find bundled seed agents folder
    package_dir = Path(__file__).parent.parent.parent  # Go up from core/utils/ to package root
    seed_agent_dir = package_dir / "agents" / agent_name

    if not seed_agent_dir.exists():
        # Fallback for development mode
        seed_agent_dir = Path.cwd() / "agents" / agent_name

    if seed_agent_dir.exists() and seed_agent_dir.is_dir():
        # Copy entire agent directory from seed
        agent_dir.mkdir(parents=True, exist_ok=True)
        for item in seed_agent_dir.iterdir():
            target = agent_dir / item.name
            if not target.exists():
                if item.is_file():
                    shutil.copy2(item, target)
                    logger.debug(f"Copied seed file: {item.name}")
        logger.info(f"Created agent from seed: {agent_dir}")
    else:
        # Fallback: create minimal agent
        agent_dir.mkdir(parents=True, exist_ok=True)

        prompt_file = agent_dir / "system_prompt.md"
        if not prompt_file.exists():
            prompt_file.write_text(get_default_system_prompt(), encoding='utf-8')
            logger.warning(f"Created fallback system prompt (seed not found): {prompt_file}")

        agent_json = agent_dir / "agent.json"
        if not agent_json.exists():
            import json
            agent_config = {
                "name": agent_name,
                "description": f"{agent_name} agent",
                "profile": None
            }
            agent_json.write_text(json.dumps(agent_config, indent=2), encoding='utf-8')
            logger.info(f"Created agent config: {agent_json}")


def _copy_agent_prompt_to_local(global_agent_dir: Path, local_agent_dir: Path) -> None:
    """Copy agent files from global to local directory.

    Args:
        global_agent_dir: Source global agent directory
        local_agent_dir: Target local agent directory
    """
    local_agent_dir.mkdir(parents=True, exist_ok=True)

    # Copy system_prompt.md
    global_prompt = global_agent_dir / "system_prompt.md"
    local_prompt = local_agent_dir / "system_prompt.md"
    if global_prompt.exists() and not local_prompt.exists():
        shutil.copy2(global_prompt, local_prompt)
        logger.info(f"Copied system prompt to local: {local_prompt}")

    # Copy agent.json if it exists
    global_config = global_agent_dir / "agent.json"
    local_config = local_agent_dir / "agent.json"
    if global_config.exists() and not local_config.exists():
        shutil.copy2(global_config, local_config)
        logger.debug(f"Copied agent config to local: {local_config}")

    # Copy any skill files (*.md except system_prompt.md)
    for skill_file in global_agent_dir.glob("*.md"):
        if skill_file.name != "system_prompt.md":
            local_skill = local_agent_dir / skill_file.name
            if not local_skill.exists():
                shutil.copy2(skill_file, local_skill)
                logger.debug(f"Copied skill to local: {skill_file.name}")
