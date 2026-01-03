# Bug Fix #6: Unsafe Module Import

## 🚨 **CRITICAL SECURITY BUG** - CODE INJECTION

**Location:** `core/plugins/discovery.py:64-66`
**Severity:** Critical (Security Vulnerability)
**Impact:** Code injection possible, arbitrary code execution

## 📋 **Bug Description**

The plugin discovery system uses unsafe module imports that could allow malicious code execution through directory traversal or code injection attacks.

### Current Problematic Code
```python
# core/plugins/discovery.py:64-66 (approximate)
class PluginDiscovery:
    def load_plugin_module(self, plugin_name):
        """Load plugin module by name."""
        # ← DANGEROUS: Direct import without validation!
        module = importlib.import_module(f"plugins.{plugin_name}")
        return module

    def discover_plugins(self):
        """Discover all plugins in plugins directory."""
        plugins = []
        for file_path in Path("plugins").glob("*.py"):
            if file_path.name != "__init__.py":
                # ← Extracts filename directly without sanitization!
                plugin_name = file_path.stem
                plugins.append(plugin_name)
        return plugins
```

### The Issue
- **Direct module import** without name validation
- **No path sanitization** when discovering plugins
- **Potential directory traversal** attacks (../../../malicious)
- **Code injection** through malicious plugin names
- **Arbitrary code execution** vulnerability

## 🔧 **Fix Strategy**

### 1. Add Strict Name Validation and Sanitization
```python
import re
import importlib
import importlib.util
from pathlib import Path
from typing import Set, Optional, List
import logging

logger = logging.getLogger(__name__)

class PluginDiscovery:
    def __init__(self):
        # Strict validation patterns
        self.valid_plugin_name_pattern = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')
        self.max_plugin_name_length = 50
        self.blocked_names = {
            '__init__', '__pycache__', 'system', 'os', 'sys', 'subprocess',
            'eval', 'exec', 'compile', 'open', 'file', 'input', 'raw_input'
        }

    def _sanitize_plugin_name(self, plugin_name: str) -> Optional[str]:
        """Sanitize and validate plugin name."""
        if not plugin_name:
            logger.warning("Empty plugin name rejected")
            return None

        # Length check
        if len(plugin_name) > self.max_plugin_name_length:
            logger.warning(f"Plugin name too long: {plugin_name}")
            return None

        # Pattern validation (letters, numbers, underscores only)
        if not self.valid_plugin_name_pattern.match(plugin_name):
            logger.warning(f"Invalid plugin name pattern: {plugin_name}")
            return None

        # Block dangerous names
        if plugin_name.lower() in self.blocked_names:
            logger.warning(f"Blocked plugin name: {plugin_name}")
            return None

        # Block path traversal attempts
        if '..' in plugin_name or '/' in plugin_name or '\\' in plugin_name:
            logger.warning(f"Path traversal attempt in plugin name: {plugin_name}")
            return None

        # Block shell metacharacters
        if any(char in plugin_name for char in [';', '&', '|', '`', '$', '"', "'"]):
            logger.warning(f"Shell metacharacters in plugin name: {plugin_name}")
            return None

        return plugin_name

    def load_plugin_module(self, plugin_name: str):
        """Load plugin module with comprehensive security checks."""
        # Sanitize the plugin name first
        safe_name = self._sanitize_plugin_name(plugin_name)
        if not safe_name:
            raise ValueError(f"Invalid or unsafe plugin name: {plugin_name}")

        # Construct module path safely
        module_path = f"plugins.{safe_name}"

        try:
            # Additional safety: verify module exists in expected location
            if not self._verify_plugin_location(safe_name):
                raise ValueError(f"Plugin location verification failed: {safe_name}")

            # Load the module
            logger.info(f"Loading plugin module: {module_path}")
            module = importlib.import_module(module_path)

            # Verify the loaded module is actually our plugin
            if not self._verify_loaded_module(module, safe_name):
                raise ValueError(f"Module verification failed: {safe_name}")

            return module

        except ImportError as e:
            logger.error(f"Failed to import plugin {safe_name}: {e}")
            raise ValueError(f"Plugin import failed: {safe_name}")
        except Exception as e:
            logger.error(f"Unexpected error loading plugin {safe_name}: {e}")
            raise ValueError(f"Plugin loading failed: {safe_name}")

    def _verify_plugin_location(self, plugin_name: str) -> bool:
        """Verify plugin file exists in expected location."""
        try:
            # Construct expected file path
            plugin_file = Path("plugins") / f"{plugin_name}.py"

            # Resolve to absolute path to prevent symlink attacks
            plugin_file = plugin_file.resolve()

            # Verify it's within the plugins directory
            plugins_dir = Path("plugins").resolve()
            if not str(plugin_file).startswith(str(plugins_dir)):
                logger.error(f"Plugin file outside plugins directory: {plugin_file}")
                return False

            # Verify file exists and is a regular file
            if not plugin_file.is_file():
                logger.error(f"Plugin file not found: {plugin_file}")
                return False

            # Additional security: check file permissions
            if plugin_file.stat().st_mode & 0o777 != 0o644:
                logger.warning(f"Plugin file has unusual permissions: {plugin_file}")

            return True

        except Exception as e:
            logger.error(f"Error verifying plugin location: {e}")
            return False

    def _verify_loaded_module(self, module, plugin_name: str) -> bool:
        """Verify the loaded module is actually our plugin."""
        try:
            # Check module name matches
            if module.__name__ != f"plugins.{plugin_name}":
                logger.error(f"Module name mismatch: {module.__name__}")
                return False

            # Check module file location
            if hasattr(module, '__file__'):
                module_file = Path(module.__file__).resolve()
                plugins_dir = Path("plugins").resolve()

                if not str(module_file).startswith(str(plugins_dir)):
                    logger.error(f"Module file outside plugins directory: {module_file}")
                    return False

            # Verify module has expected plugin attributes
            if not hasattr(module, 'Plugin') and not hasattr(module, 'plugin_class'):
                logger.warning(f"Module {plugin_name} may not be a valid plugin")

            return True

        except Exception as e:
            logger.error(f"Error verifying loaded module: {e}")
            return False
```

### 2. Secure Plugin Discovery
```python
def discover_plugins(self) -> List[str]:
    """Discover plugins with comprehensive security validation."""
    plugins = []
    plugins_dir = Path("plugins")

    try:
        # Verify plugins directory exists and is actually a directory
        if not plugins_dir.is_dir():
            logger.warning(f"Plugins directory not found: {plugins_dir}")
            return plugins

        # Resolve to absolute path to prevent symlink attacks
        plugins_dir = plugins_dir.resolve()

        # Ensure we're not following dangerous symlinks
        if not self._is_safe_directory(plugins_dir):
            logger.error(f"Unsafe plugins directory: {plugins_dir}")
            return plugins

        # Discover plugin files
        for file_path in plugins_dir.glob("*.py"):
            try:
                # Skip __init__.py and other special files
                if file_path.name.startswith("__"):
                    continue

                # Skip test files
                if file_path.name.startswith("test_") or file_path.name.endswith("_test.py"):
                    continue

                # Get relative path and extract name
                relative_path = file_path.relative_to(plugins_dir)
                plugin_name = relative_path.stem

                # Validate plugin name
                safe_name = self._sanitize_plugin_name(plugin_name)
                if safe_name:
                    plugins.append(safe_name)
                    logger.debug(f"Discovered valid plugin: {safe_name}")
                else:
                    logger.warning(f"Skipping invalid plugin: {plugin_name}")

            except Exception as e:
                logger.error(f"Error processing plugin file {file_path}: {e}")
                continue

    except Exception as e:
        logger.error(f"Error discovering plugins: {e}")

    return plugins

def _is_safe_directory(self, directory: Path) -> bool:
    """Check if directory is safe for plugin discovery."""
    try:
        # Resolve any symlinks
        resolved_dir = directory.resolve()

        # Check directory permissions
        stat_info = resolved_dir.stat()
        mode = stat_info.st_mode

        # Directory should not be world-writable
        if mode & 0o002:  # Others write permission
            logger.error(f"Directory is world-writable: {resolved_dir}")
            return False

        # Should not be group-writable (optional, based on security requirements)
        if mode & 0o020:  # Group write permission
            logger.warning(f"Directory is group-writable: {resolved_dir}")

        # Check if owned by current user (Unix systems)
        if hasattr(stat_info, 'st_uid'):
            import os
            if stat_info.st_uid != os.getuid():
                logger.warning(f"Directory not owned by current user: {resolved_dir}")

        return True

    except Exception as e:
        logger.error(f"Error checking directory safety: {e}")
        return False
```

### 3. Add Plugin Signature Verification (Optional Advanced Security)
```python
import hashlib
from typing import Dict

class PluginDiscovery:
    def __init__(self):
        # ... existing code ...
        self.allowed_signatures: Dict[str, str] = {}  # plugin_name -> sha256 hash
        self.require_signature = False

    def _verify_plugin_signature(self, plugin_name: str, plugin_file: Path) -> bool:
        """Verify plugin file signature (if enabled)."""
        if not self.require_signature:
            return True

        if plugin_name not in self.allowed_signatures:
            logger.error(f"No signature found for plugin: {plugin_name}")
            return False

        try:
            # Calculate file hash
            with open(plugin_file, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()

            expected_hash = self.allowed_signatures[plugin_name]
            if file_hash != expected_hash:
                logger.error(f"Plugin signature mismatch: {plugin_name}")
                return False

            logger.debug(f"Plugin signature verified: {plugin_name}")
            return True

        except Exception as e:
            logger.error(f"Error verifying plugin signature: {e}")
            return False

    def load_allowed_signatures(self, signatures_file: str):
        """Load allowed plugin signatures from file."""
        try:
            import json
            with open(signatures_file, 'r') as f:
                self.allowed_signatures = json.load(f)
            self.require_signature = True
            logger.info(f"Loaded {len(self.allowed_signatures)} plugin signatures")
        except Exception as e:
            logger.error(f"Error loading plugin signatures: {e}")
```

### 4. Add Configuration for Security Settings
```python
# core/config/plugin_config.py
class PluginSecurityConfig:
    max_plugin_name_length: int = 50
    require_signature_verification: bool = False
    allow_group_writable_directory: bool = False
    blocked_plugin_names: List[str] = [
        '__init__', '__pycache__', 'system', 'os', 'sys', 'subprocess',
        'eval', 'exec', 'compile', 'open', 'file', 'input'
    ]
    allowed_plugin_patterns: List[str] = [
        r'^[a-zA-Z][a-zA-Z0-9_]*$'  # Standard Python identifier pattern
    ]
```

### 5. Add Security Audit Logging
```python
def _log_security_event(self, event_type: str, details: dict):
    """Log security-related events for audit purposes."""
    security_log = logging.getLogger('plugin_security')

    log_entry = {
        'event': event_type,
        'timestamp': asyncio.get_event_loop().time(),
        'details': details
    }

    if event_type in ['BLOCKED_PLUGIN_NAME', 'PATH_TRAVERSAL_ATTEMPT', 'SIGNATURE_MISMATCH']:
        security_log.warning(f"Security event: {event_type} - {details}")
    else:
        security_log.info(f"Security event: {event_type} - {details}")
```

## ✅ **Implementation Steps**

1. **Implement strict name validation** with regex and blacklisting
2. **Add path sanitization** to prevent directory traversal
3. **Verify plugin locations** and prevent symlink attacks
4. **Implement module verification** after loading
5. **Add optional signature verification** for high-security environments
6. **Create comprehensive audit logging** for security events

## 🧪 **Testing Strategy**

1. **Test path traversal attempts** - ensure they're blocked
2. **Test malicious plugin names** - verify validation works
3. **Test symlink attacks** - ensure they're prevented
4. **Test signature verification** - verify hash checking works
5. **Test audit logging** - ensure security events are logged
6. **Test bypass attempts** - verify all attack vectors are covered

## 🚀 **Files to Modify**

- `core/plugins/discovery.py` - Main security fix location
- `core/config/plugin_config.py` - Add security configuration
- `tests/test_plugin_discovery.py` - Add security tests
- `security/plugin_signatures.json` - Optional signature file

## 📊 **Success Criteria**

- ✅ Plugin names are strictly validated and sanitized
- ✅ Path traversal attacks are prevented
- ✅ Plugin files are verified to be in expected locations
- ✅ Loaded modules are verified for authenticity
- ✅ Security events are properly logged
- ✅ Optional signature verification is available

## 💡 **Why This Fixes the Security Issue**

This fix eliminates the code injection vulnerability by:
- **Strict input validation** preventing dangerous characters and patterns
- **Path sanitization** preventing directory traversal attacks
- **Location verification** ensuring plugins come from trusted directories
- **Module verification** confirming loaded modules are authentic
- **Audit logging** providing visibility into security events
- **Optional signatures** providing additional protection for high-security environments

The unsafe import vulnerability is eliminated because every plugin name is thoroughly validated, every plugin file is verified to be in the expected location, and loaded modules are checked for authenticity before being used.