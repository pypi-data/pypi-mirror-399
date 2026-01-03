# Troubleshooting Guide

## Overview
This guide provides comprehensive troubleshooting information for common issues encountered with the Chat App, AI tool integrations, and development workflows.

## Quick Diagnostic Checklist

### System Health Check
```bash
# Quick system status check
python -c "
import sys
print(f'Python version: {sys.version}')
print(f'Platform: {sys.platform}')

try:
    import aiohttp
    print('aiohttp: Available')
except ImportError:
    print('aiohttp: MISSING - run pip install aiohttp')

try:
    import anthropic
    print('anthropic: Available')
except ImportError:
    print('anthropic: MISSING - run pip install anthropic')
"
```

### Environment Validation
```bash
# Check environment variables
echo "API Keys configured:"
echo "ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:+SET}"
echo "OPENAI_API_KEY: ${OPENAI_API_KEY:+SET}"
echo "GITHUB_TOKEN: ${GITHUB_TOKEN:+SET}"

# Check configuration directory
ls -la .kollabor-cli/
echo "Config file:"
cat .kollabor-cli/config.json | jq '.'
```

## Common Issues and Solutions

### 1. Application Startup Issues

#### Issue: Application fails to start
**Symptoms**:
- Command `python main.py` produces error
- Import errors or module not found
- Permission denied errors

**Diagnosis Steps**:
```bash
# Check Python version and virtual environment
python --version
which python

# Verify virtual environment activation
echo $VIRTUAL_ENV

# Check installed packages
pip list | grep -E "(aiohttp|anthropic)"

# Test import statements
python -c "import core.application; print('Core imports OK')"
```

**Solutions**:
1. **Virtual Environment Issues**:
   ```bash
   # Recreate virtual environment
   deactivate
   rm -rf venv
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Missing Dependencies**:
   ```bash
   # Install missing packages
   pip install aiohttp anthropic
   ```

3. **Permission Issues**:
   ```bash
   # Fix directory permissions
   chmod -R 755 .kollabor-cli/
   chmod 644 .kollabor-cli/config.json
   ```

#### Issue: Configuration errors on startup
**Symptoms**:
- "Config file not found" error
- Invalid JSON in configuration
- Plugin discovery failures

**Solutions**:
1. **Reset Configuration**:
   ```bash
   # Backup existing config
   mv .kollabor-cli/config.json .kollabor-cli/config.json.backup
   
   # Let application regenerate default config
   python main.py
   ```

2. **Fix JSON Syntax**:
   ```bash
   # Validate JSON syntax
   python -m json.tool .kollabor-cli/config.json
   
   # If invalid, restore from backup or reset
   ```

### 2. AI API Connection Issues

#### Issue: Claude API connection failures
**Symptoms**:
- "Authentication failed" errors
- "Rate limit exceeded" messages
- Connection timeout errors

**Diagnosis**:
```python
# Test API connection
import asyncio
import anthropic

async def test_claude_api():
    try:
        client = anthropic.AsyncAnthropic(api_key="your-key-here")
        response = await client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hello"}]
        )
        print("API connection successful")
        print(f"Response: {response.content[0].text}")
    except Exception as e:
        print(f"API connection failed: {e}")

asyncio.run(test_claude_api())
```

**Solutions**:
1. **Invalid API Key**:
   ```bash
   # Verify API key format (should start with 'sk-ant-')
   echo $ANTHROPIC_API_KEY | cut -c1-10
   
   # Set correct API key
   export ANTHROPIC_API_KEY="sk-ant-your-actual-key"
   ```

2. **Rate Limiting**:
   ```python
   # Add rate limiting to API calls
   import asyncio
   from aiohttp import ClientSession
   
   class RateLimitedClient:
       def __init__(self, requests_per_minute=60):
           self.delay = 60 / requests_per_minute
           self.last_request = 0
   
       async def make_request(self, func, *args, **kwargs):
           current_time = time.time()
           time_since_last = current_time - self.last_request
           if time_since_last < self.delay:
               await asyncio.sleep(self.delay - time_since_last)
           
           self.last_request = time.time()
           return await func(*args, **kwargs)
   ```

3. **Network Issues**:
   ```bash
   # Test network connectivity
   curl -I https://api.anthropic.com/v1/messages
   
   # Check DNS resolution
   nslookup api.anthropic.com
   
   # Test with different DNS server
   nslookup api.anthropic.com 8.8.8.8
   ```

### 3. Plugin System Issues

#### Issue: Plugin loading failures
**Symptoms**:
- "Plugin not found" errors
- Import errors in plugin code
- Plugin initialization failures

**Diagnosis**:
```bash
# Check plugin directory structure
find plugins/ -name "*.py" -type f

# Test plugin imports manually
python -c "
import sys
sys.path.append('plugins')
try:
    import llm_plugin
    print('LLM plugin imports OK')
except Exception as e:
    print(f'LLM plugin import failed: {e}')
"
```

**Solutions**:
1. **Plugin Directory Issues**:
   ```bash
   # Ensure proper directory structure
   mkdir -p plugins
   touch plugins/__init__.py
   
   # Verify plugin files exist
   ls -la plugins/*.py
   ```

2. **Plugin Code Errors**:
   ```python
   # Add error handling to plugin loading
   class PluginRegistry:
       def load_plugin(self, plugin_path):
           try:
               # Plugin loading code
               pass
           except ImportError as e:
               logger.error(f"Plugin import failed: {e}")
               # Continue without this plugin
           except Exception as e:
               logger.error(f"Plugin initialization failed: {e}")
               # Log error and continue
   ```

#### Issue: Hook registration problems
**Symptoms**:
- Events not triggering plugin hooks
- Plugin status shows "inactive"
- Missing plugin functionality

**Solutions**:
1. **Verify Hook Registration**:
   ```python
   # Debug hook registration
   class DebugPlugin:
       async def register_hooks(self):
           print(f"Registering hooks for {self.__class__.__name__}")
           await self.event_bus.register_hook(
               event_type="USER_INPUT",
               hook_function=self.handle_input,
               priority=500
           )
           print("Hook registration complete")
   ```

2. **Check Event Bus Status**:
   ```python
   # Monitor event bus activity
   class EventBus:
       async def publish_event(self, event_type, data):
           print(f"Publishing event: {event_type}")
           print(f"Registered hooks: {len(self.hooks.get(event_type, []))}")
           # Continue with normal processing
   ```

### 4. Terminal Display Issues

#### Issue: Garbled terminal output
**Symptoms**:
- Overlapping text
- Incorrect colors or formatting
- Terminal not clearing properly

**Diagnosis**:
```bash
# Check terminal capabilities
echo "TERM: $TERM"
tput colors
tput lines
tput cols

# Test ANSI sequence support
echo -e "\033[31mRed text\033[0m"
echo -e "\033[2J\033[H"  # Clear screen and home cursor
```

**Solutions**:
1. **Terminal Compatibility**:
   ```python
   # Detect terminal capabilities
   import os
   import subprocess
   
   def detect_terminal_support():
       term = os.environ.get('TERM', 'unknown')
       try:
           colors = subprocess.check_output(['tput', 'colors'])
           color_count = int(colors.decode().strip())
       except:
           color_count = 8  # Default fallback
       
       return {
           'term_type': term,
           'colors': color_count,
           'supports_256_color': color_count >= 256
       }
   ```

2. **Screen Clearing Issues**:
   ```python
   # Robust screen clearing
   class TerminalManager:
       def clear_screen(self):
           # Try multiple methods
           methods = [
               '\033[2J\033[H',  # ANSI escape sequence
               '\033c',          # Reset terminal
           ]
           
           for method in methods:
               try:
                   print(method, end='')
                   break
               except:
                   continue
   ```

#### Issue: Slow rendering performance
**Symptoms**:
- Laggy response to user input
- Frame rate drops below target
- High CPU usage during rendering

**Solutions**:
1. **Optimize Render Loop**:
   ```python
   # Efficient rendering with dirty regions
   class TerminalRenderer:
       def __init__(self):
           self.dirty_regions = set()
           self.last_frame_time = 0
           self.target_fps = 20
   
       async def render_frame(self):
           current_time = time.time()
           if current_time - self.last_frame_time < 1/self.target_fps:
               return  # Skip frame if too soon
           
           if self.dirty_regions:
               self.render_dirty_regions()
               self.dirty_regions.clear()
           
           self.last_frame_time = current_time
   ```

2. **Reduce Terminal I/O**:
   ```python
   # Buffer output to reduce system calls
   class OutputBuffer:
       def __init__(self):
           self.buffer = []
   
       def write(self, text):
           self.buffer.append(text)
   
       def flush(self):
           if self.buffer:
               print(''.join(self.buffer), end='')
               self.buffer.clear()
   ```

### 5. Memory and Performance Issues

#### Issue: High memory usage
**Symptoms**:
- Application consuming excessive RAM
- System becoming unresponsive
- Out of memory errors

**Diagnosis**:
```python
# Memory usage monitoring
import psutil
import gc

def diagnose_memory_usage():
    process = psutil.Process()
    memory_info = process.memory_info()
    
    print(f"RSS Memory: {memory_info.rss / 1024 / 1024:.1f} MB")
    print(f"VMS Memory: {memory_info.vms / 1024 / 1024:.1f} MB")
    print(f"Memory Percent: {process.memory_percent():.1f}%")
    
    # Check for memory leaks
    gc.collect()
    print(f"Garbage objects: {len(gc.get_objects())}")
```

**Solutions**:
1. **Memory Leak Prevention**:
   ```python
   # Proper resource cleanup
   class ResourceManager:
       def __init__(self):
           self.resources = []
   
       async def __aenter__(self):
           return self
   
       async def __aexit__(self, exc_type, exc_val, exc_tb):
           for resource in self.resources:
               await resource.cleanup()
           self.resources.clear()
   ```

2. **Conversation History Management**:
   ```python
   # Limit conversation history size
   class ConversationManager:
       def __init__(self, max_messages=100):
           self.max_messages = max_messages
           self.messages = []
   
       def add_message(self, message):
           self.messages.append(message)
           if len(self.messages) > self.max_messages:
               # Remove oldest messages
               self.messages = self.messages[-self.max_messages:]
   ```

## Logging and Debugging

### Enable Debug Logging
```python
# Add to main.py or configuration
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.kollabor-cli/logs/debug.log'),
        logging.StreamHandler()  # Also log to console
    ]
)

# Enable specific component debugging
logger = logging.getLogger('event_bus')
logger.setLevel(logging.DEBUG)
```

### Debug Information Collection
```bash
#!/bin/bash
# debug_info.sh - Collect system debug information

echo "=== Chat App Debug Information ===" > debug_report.txt
echo "Timestamp: $(date)" >> debug_report.txt
echo "" >> debug_report.txt

echo "=== System Information ===" >> debug_report.txt
python --version >> debug_report.txt
echo "Platform: $(python -c 'import sys; print(sys.platform)')" >> debug_report.txt
echo "" >> debug_report.txt

echo "=== Dependencies ===" >> debug_report.txt
pip list | grep -E "(aiohttp|anthropic)" >> debug_report.txt
echo "" >> debug_report.txt

echo "=== Configuration ===" >> debug_report.txt
if [ -f .kollabor-cli/config.json ]; then
    echo "Config file exists" >> debug_report.txt
    python -m json.tool .kollabor-cli/config.json >> debug_report.txt 2>&1
else
    echo "Config file missing" >> debug_report.txt
fi
echo "" >> debug_report.txt

echo "=== Recent Logs ===" >> debug_report.txt
if [ -f .kollabor-cli/logs/kollabor.log ]; then
    tail -50 .kollabor-cli/logs/kollabor.log >> debug_report.txt
else
    echo "No log file found" >> debug_report.txt
fi

echo "Debug report saved to debug_report.txt"
```

## Recovery Procedures

### Complete System Reset
```bash
#!/bin/bash
# reset_system.sh - Complete system reset

echo "Backing up current configuration..."
if [ -d .kollabor ]; then
    mv .kollabor .kollabor.backup.$(date +%s)
fi

echo "Resetting virtual environment..."
deactivate 2>/dev/null || true
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate

echo "Reinstalling dependencies..."
pip install -r requirements.txt

echo "Starting fresh application..."
python main.py

echo "System reset complete. Check .kollabor.backup.* for old configuration."
```

### Selective Component Reset
```python
# Reset specific components
class SystemRecovery:
    @staticmethod
    async def reset_event_bus():
        """Reset event bus to clean state"""
        # Clear all registered hooks
        # Restart event processing
        pass
    
    @staticmethod
    async def reset_plugins():
        """Reload all plugins"""
        # Unload current plugins
        # Clear plugin registry
        # Rediscover and reload plugins
        pass
    
    @staticmethod
    def reset_configuration():
        """Reset to default configuration"""
        # Backup current config
        # Generate new default config
        # Merge essential user settings
        pass
```

## Support Resources

### Getting Help
1. **Documentation**: Check `docs/` directory for comprehensive guides
2. **Logs**: Review `.kollabor-cli/logs/kollabor.log` for error details
3. **Community**: GitHub Issues for bug reports and questions
4. **Debug Mode**: Run with `LOG_LEVEL=DEBUG` for detailed information

### Reporting Issues
When reporting issues, include:
1. **System Information**: OS, Python version, terminal type
2. **Error Messages**: Complete error output and stack traces
3. **Configuration**: Sanitized version of your configuration
4. **Steps to Reproduce**: Detailed steps to recreate the issue
5. **Debug Logs**: Recent log entries showing the problem

### Emergency Contacts
- **Critical Issues**: Use GitHub Issues with "critical" label
- **Security Issues**: Follow responsible disclosure practices
- **Documentation Issues**: Submit pull requests with fixes

---

*This troubleshooting guide covers the most common issues encountered with the Chat App and provides systematic approaches to diagnosis and resolution.*