# File Operations Tool Specification

**Version**: 2.1 (Updated with multi-occurrence behavior)
**Status**: Ready for Implementation
**Created**: 2025-11-07
**Updated**: 2025-11-07
**Style**: Nested XML (No Attributes)

---

## ⚡ Key Behavioral Rules

### `<edit>` - Replace All Occurrences
- **Replaces ALL matches** - if pattern appears 5 times, all 5 are replaced
- **Reports count** - tells you how many replacements were made
- **Never fails on ambiguous** - just replaces all and reports
- To replace only one location: provide more context in `<find>` block

### `<insert_after>` and `<insert_before>` - Exact Match Required
- **Pattern must appear exactly once** - fails if 0 or 2+ matches
- **Reports line numbers** - if ambiguous, shows all locations
- **Error message guides** - suggests using `<edit>` for ambiguous cases

### No Attributes Allowed
- ❌ `<insert mode="after">` - NO ATTRIBUTES
- ✅ `<insert_after>` - SEPARATE TAGS
- ✅ `<insert_before>` - SEPARATE TAGS
- ✅ `<create_overwrite>` - SEPARATE TAGS (not `overwrite="true"`)

---

## 1. Overview

Add comprehensive file operation tools to Kollabor CLI's LLM, allowing the glm-4.6 model to safely manage files without using risky shell commands.

**Current Problem**: LLM must use `sed -i`, `awk`, `echo >`, `rm`, `mv` which are:
- ❌ Risky (can corrupt/delete files permanently)
- ❌ Hard to get right (escaping, quoting issues)
- ❌ No validation or safety checks
- ❌ No rollback capability

**Proposed Solution**: Structured XML tags for file operations with built-in safety.

---

## 2. Syntax Standard (User Selected)

**Nested XML with Clear Tags**

```xml
<operation>
<file>path/to/file</file>
<action-specific-tags>
content here
</action-specific-tags>
</operation>
```

**Why This Style**:
- ✅ Self-documenting and explicit
- ✅ Easy to validate with XML parser
- ✅ Handles multi-line content naturally
- ✅ Clear visual structure for debugging
- ✅ Extensible (easy to add new tags/operations)

---

## 3. Core Operations

### 3.1 Edit File (Replace Content)

Replace exact string match in existing file. **Can replace multiple occurrences.**

**Syntax**:
```xml
<edit>
<file>core/llm/llm_service.py</file>
<find>
class LLMService:
    def __init__(self):
</find>
<replace>
class LLMService:
    def __init__(self, config):
        self.config = config
</replace>
</edit>
```

**Behavior**:
1. Read file content
2. Search for exact match of `<find>` content
3. Replace **ALL occurrences** with `<replace>` content
4. Write back to file
5. Create `.bak` backup before modification
6. **Report how many replacements were made**

**Validation**:
- File must exist
- `<find>` content must match at least once (fail if 0 matches)
- **If multiple matches**: Replace all and report count

**Success Message Format**:
- 1 match: `"Replaced 1 occurrence in core/llm/llm_service.py"`
- 3 matches: `"Replaced 3 occurrences in core/llm/llm_service.py (lines 42, 78, 145)"`

---

### 3.2 Create File (New File)

Create a new file with content.

**Syntax**:
```xml
<create>
<file>plugins/new_plugin.py</file>
<content>
"""New plugin implementation."""

import logging

class NewPlugin:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
</content>
</create>
```

**Behavior**:
1. Check if file already exists
2. Create parent directories if needed
3. Write content to file
4. Set appropriate permissions (644)

**Validation**:
- File must NOT already exist (fail if exists)
- Parent directory must be writable
- Content cannot be empty

**Alternative - Overwrite Existing File**:

To overwrite an existing file, use `<create_overwrite>`:
```xml
<create_overwrite>
<file>plugins/existing_file.py</file>
<content>
New content (will overwrite existing file)
</content>
</create_overwrite>
```

---

### 3.3 Delete File

Delete an existing file (with safety checks).

**Syntax**:
```xml
<delete>
<file>plugins/old_plugin.py</file>
</delete>
```

**Behavior**:
1. Check if file exists
2. Create backup as `.deleted` before removal
3. Delete the file

**Validation**:
- File must exist
- File must not be in protected paths (prevent deleting core files)
- Create backup for safety

**Protected Paths** (cannot delete):
- `core/application.py`
- `main.py`
- Any file in `.git/`
- Any file in `venv/` or `.venv/`

---

### 3.4 Move/Rename File

Move or rename a file.

**Syntax**:
```xml
<move>
<from>plugins/old_name.py</from>
<to>plugins/new_name.py</to>
</move>
```

**Behavior**:
1. Check source file exists
2. Check destination doesn't exist
3. Create parent directories for destination if needed
4. Move file atomically

**Validation**:
- Source must exist
- Destination must NOT exist (fail if exists)
- Source and destination cannot be the same

---

### 3.5 Copy File

Copy a file to new location.

**Syntax**:
```xml
<copy>
<from>plugins/example_plugin.py</from>
<to>plugins/example_plugin_backup.py</to>
</copy>
```

**Behavior**:
1. Check source exists
2. Check destination doesn't exist (or use overwrite flag)
3. Copy file with metadata (permissions, timestamps)

**Validation**:
- Source must exist
- Destination must NOT exist

**To Overwrite Existing Destination**:

Use `<copy_overwrite>`:
```xml
<copy_overwrite>
<from>config.json</from>
<to>config.backup.json</to>
</copy_overwrite>
```

---

### 3.6 Append to File

Add content to end of existing file.

**Syntax**:
```xml
<append>
<file>core/llm/llm_service.py</file>
<content>

# New helper function
def helper():
    pass
</content>
</append>
```

**Behavior**:
1. Check file exists
2. Read current content
3. Append new content to end
4. Create `.bak` backup before modification

**Validation**:
- File must exist
- Content cannot be empty

---

### 3.7 Insert After Pattern

Insert content immediately after a specific pattern. **Pattern must appear exactly once.**

**Syntax**:
```xml
<insert_after>
<file>core/llm/llm_service.py</file>
<pattern>import logging</pattern>
<content>
from typing import Optional
</content>
</insert_after>
```

**Behavior**:
1. Find pattern in file
2. Insert content immediately after pattern (on new line)
3. Create `.bak` backup

**Validation**:
- File must exist
- Pattern must match **exactly once** (fail if 0 or 2+ matches)

**Error Messages**:
- 0 matches: `"Pattern not found: 'import logging'"`
- 2+ matches: `"Ambiguous pattern: 'import logging' appears 3 times at lines 5, 12, 45. Pattern must be unique. Use <edit> with full context instead."`

---

### 3.8 Insert Before Pattern

Insert content immediately before a specific pattern. **Pattern must appear exactly once.**

**Syntax**:
```xml
<insert_before>
<file>core/llm/llm_service.py</file>
<pattern>class LLMService:</pattern>
<content>
# Service implementation below
</content>
</insert_before>
```

**Behavior**:
1. Find pattern in file
2. Insert content immediately before pattern (on new line)
3. Create `.bak` backup

**Validation**:
- File must exist
- Pattern must match **exactly once** (fail if 0 or 2+ matches)

**Error Messages**:
- 0 matches: `"Pattern not found: 'class LLMService:'"`
- 2+ matches: `"Ambiguous pattern: 'class LLMService:' appears 2 times at lines 15, 89. Pattern must be unique. Use <edit> with full context instead."`

---

### 3.9 Create Directory

Create a new directory (with parents).

**Syntax**:
```xml
<mkdir>
<path>plugins/new_feature/components</path>
</mkdir>
```

**Behavior**:
1. Create directory and all parent directories (like `mkdir -p`)
2. Set permissions to 755

**Validation**:
- Path must not already exist as a file
- Parent path must be writable

---

### 3.10 Delete Directory

Delete an empty directory.

**Syntax**:
```xml
<rmdir>
<path>plugins/old_feature</path>
</rmdir>
```

**Behavior**:
1. Check directory is empty
2. Remove directory

**Validation**:
- Directory must exist
- Directory must be empty (fail if contains files)
- Cannot delete protected directories

**Protected Directories**:
- `core/`
- `.git/`
- `venv/`
- `.venv/`

---

### 3.11 Read File (for verification)

Read file content (similar to `cat` but structured).

**Syntax**:
```xml
<read>
<file>core/llm/llm_service.py</file>
</read>
```

**Behavior**:
1. Read file content
2. Return content in tool result

**Validation**:
- File must exist
- File must be text (not binary)

**Optional - Read Specific Lines**:
```xml
<read>
<file>core/llm/llm_service.py</file>
<lines>10-20</lines>
</read>
```

---

## 4. Comprehensive Examples

### Example 1: Simple Import Addition

```xml
<edit>
<file>core/llm/llm_service.py</file>
<find>
import logging
from typing import Dict
</find>
<replace>
import logging
from typing import Dict, Optional, List
</replace>
</edit>
```

---

### Example 2: Multi-line Method Replacement

```xml
<edit>
<file>plugins/example_plugin.py</file>
<find>
    def initialize(self):
        """Initialize plugin."""
        pass
</find>
<replace>
    def initialize(self, config):
        """Initialize plugin with configuration.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Plugin initialized with config: {config}")
</replace>
</edit>
```

---

### Example 3: Create New Plugin File

```xml
<create>
<file>plugins/analytics_plugin.py</file>
<content>
"""Analytics plugin for tracking usage metrics."""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AnalyticsPlugin:
    """Track and report usage analytics."""

    def __init__(self, event_bus, config):
        """Initialize analytics plugin.

        Args:
            event_bus: Event bus for hook registration
            config: Configuration manager
        """
        self.event_bus = event_bus
        self.config = config
        self.metrics = {}
        logger.info("Analytics plugin initialized")

    def track_event(self, event_name: str, data: dict):
        """Track an analytics event."""
        timestamp = datetime.now().isoformat()
        self.metrics[event_name] = {
            "timestamp": timestamp,
            "data": data
        }
        logger.debug(f"Tracked event: {event_name}")
</content>
</create>
```

---

### Example 4: Delete Old Backup Files

```xml
<delete>
<file>backups/old_config.json.bak</file>
</delete>
```

---

### Example 5: Rename Plugin

```xml
<move>
<from>plugins/old_analytics.py</from>
<to>plugins/analytics_plugin.py</to>
</move>
```

---

### Example 6: Create Plugin Directory Structure

```xml
<mkdir>
<path>plugins/analytics/components</path>
</mkdir>
```

Then create files:
```xml
<create>
<file>plugins/analytics/__init__.py</file>
<content>
"""Analytics plugin package."""
from .analytics_plugin import AnalyticsPlugin

__all__ = ['AnalyticsPlugin']
</content>
</create>
```

---

### Example 7: Append Helper Function

```xml
<append>
<file>core/utils/dict_utils.py</file>
<content>


def flatten_dict(nested_dict: dict, parent_key: str = '', sep: str = '.') -> dict:
    """Flatten a nested dictionary.

    Args:
        nested_dict: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator for nested keys

    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in nested_dict.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
</content>
</append>
```

---

### Example 8: Insert Import After Existing Imports

```xml
<insert_after>
<file>core/llm/llm_service.py</file>
<pattern>from typing import Dict</pattern>
<content>
from pathlib import Path
</content>
</insert_after>
```

---

### Example 9: Copy Config Template

```xml
<copy>
<from>.kollabor-cli/config.default.json</from>
<to>.kollabor-cli/config.json</to>
</copy>
```

---

### Example 10: Read File to Verify Change

```xml
<read>
<file>core/llm/llm_service.py</file>
<lines>1-20</lines>
</read>
```

---

## 5. Edge Cases & Error Handling

### Edge Case 1: Find String Not Found

**Input**:
```xml
<edit>
<file>core/llm/llm_service.py</file>
<find>THIS STRING DOES NOT EXIST</find>
<replace>New content</replace>
</edit>
```

**Result**:
```python
ToolExecutionResult(
    success=False,
    error="Pattern not found in file: core/llm/llm_service.py"
)
```

**No file modification occurs.**

---

### Edge Case 2: Multiple Occurrences with `<edit>`

**Input**:
```xml
<edit>
<file>core/llm/llm_service.py</file>
<find>logger.info</find>
<replace>logger.debug</replace>
</edit>
```

If `logger.info` appears 5 times:

**Result** (SUCCESS - replaces all):
```python
ToolExecutionResult(
    success=True,
    output="✅ Replaced 5 occurrences of 'logger.info' in core/llm/llm_service.py\nLocations: lines 42, 78, 103, 145, 201\nBackup: core/llm/llm_service.py.bak"
)
```

**All 5 occurrences are replaced.** If you want to replace only one specific location, provide more context:
```xml
<edit>
<file>core/llm/llm_service.py</file>
<find>
def initialize(self):
    logger.info("Starting initialization")
</find>
<replace>
def initialize(self):
    logger.debug("Starting initialization")
</replace>
</edit>
```

---

### Edge Case 2b: Multiple Occurrences with `<insert_after>` (ERROR)

**Input**:
```xml
<insert_after>
<file>core/llm/llm_service.py</file>
<pattern>import logging</pattern>
<content>
from typing import Optional
</content>
</insert_after>
```

If `import logging` appears 3 times:

**Result** (FAILURE - ambiguous):
```python
ToolExecutionResult(
    success=False,
    error="❌ Ambiguous pattern: 'import logging' appears 3 times in core/llm/llm_service.py\nLocations: lines 5, 42, 89\nPattern must be unique for insert operations. Use <edit> with full context instead."
)
```

**Solution**: Use `<edit>` with full context to target specific location:
```xml
<edit>
<file>core/llm/llm_service.py</file>
<find>
import logging
from typing import Dict
</find>
<replace>
import logging
from typing import Optional
from typing import Dict
</replace>
</edit>
```

---

### Edge Case 3: File Doesn't Exist

**Input**:
```xml
<edit>
<file>non_existent_file.py</file>
<find>something</find>
<replace>something else</replace>
</edit>
```

**Result**:
```python
ToolExecutionResult(
    success=False,
    error="File not found: non_existent_file.py"
)
```

---

### Edge Case 4: Creating File That Already Exists

**Input**:
```xml
<create>
<file>core/llm/llm_service.py</file>
<content>New content</content>
</create>
```

**Result**:
```python
ToolExecutionResult(
    success=False,
    error="File already exists: core/llm/llm_service.py. Use <edit> to modify existing files or <create_overwrite> to replace."
)
```

**Solution**: Use `<create_overwrite>`:
```xml
<create_overwrite>
<file>temp_file.py</file>
<content>Overwrite existing content</content>
</create_overwrite>
```

---

### Edge Case 5: Deleting Protected File

**Input**:
```xml
<delete>
<file>core/application.py</file>
</delete>
```

**Result**:
```python
ToolExecutionResult(
    success=False,
    error="Cannot delete protected file: core/application.py"
)
```

---

### Edge Case 6: Moving to Existing File

**Input**:
```xml
<move>
<from>file1.py</from>
<to>file2.py</to>
</move>
```

If `file2.py` already exists:

**Result**:
```python
ToolExecutionResult(
    success=False,
    error="Destination already exists: file2.py. Delete it first or choose different destination."
)
```

---

### Edge Case 7: Binary File Detection

**Input**:
```xml
<edit>
<file>image.png</file>
<find>bytes</find>
<replace>different bytes</replace>
</edit>
```

**Result**:
```python
ToolExecutionResult(
    success=False,
    error="Cannot edit binary file: image.png"
)
```

---

### Edge Case 8: Permission Denied

**Input**:
```xml
<create>
<file>/etc/system_file.txt</file>
<content>content</content>
</create>
```

**Result**:
```python
ToolExecutionResult(
    success=False,
    error="Permission denied: /etc/system_file.txt"
)
```

---

### Edge Case 9: Empty Find/Replace

**Input**:
```xml
<edit>
<file>file.py</file>
<find></find>
<replace>something</replace>
</edit>
```

**Result**:
```python
ToolExecutionResult(
    success=False,
    error="<find> content cannot be empty"
)
```

---

### Edge Case 10: Special Characters in Content

**Input**:
```xml
<edit>
<file>test.py</file>
<find>
pattern = r'<.*?>'
</find>
<replace>
pattern = r'<[^>]+>'
</replace>
</edit>
```

**Handling**: Use CDATA for XML-unsafe content:
```xml
<edit>
<file>test.py</file>
<find><![CDATA[
pattern = r'<.*?>'
]]></find>
<replace><![CDATA[
pattern = r'<[^>]+>'
]]></replace>
</edit>
```

**Or**: Parser should handle `<` and `>` within tag content naturally (text nodes).

---

### Edge Case 11: Whitespace Sensitivity

**Input**:
```xml
<edit>
<file>file.py</file>
<find>
def func():
    pass
</find>
<replace>
def func():
        pass
</replace>
</edit>
```

**Behavior**: Exact match required, including whitespace.

If file has 4-space indent but `<find>` uses 2-space:
```python
ToolExecutionResult(
    success=False,
    error="Pattern not found (check indentation/whitespace)"
)
```

---

### Edge Case 12: Parent Directory Doesn't Exist

**Input**:
```xml
<create>
<file>non_existent_dir/file.py</file>
<content>content</content>
</create>
```

**Result - Option A** (Create parents):
```python
ToolExecutionResult(
    success=True,
    output="Created parent directories and file: non_existent_dir/file.py"
)
```

**Result - Option B** (Fail):
```python
ToolExecutionResult(
    success=False,
    error="Parent directory does not exist: non_existent_dir/"
)
```

**DECISION NEEDED**: Auto-create parents or fail?

---

### Edge Case 13: Syntax Error After Edit (Python files)

**Input**:
```xml
<edit>
<file>plugin.py</file>
<find>
def valid_function():
    return True
</find>
<replace>
def invalid_function(
    # Missing closing paren
    return True
</replace>
</edit>
```

**With Syntax Validation Enabled**:
```python
ToolExecutionResult(
    success=False,
    error="Syntax validation failed: invalid syntax at line 2. Edit rolled back from backup."
)
```

**File is restored from `.bak` backup.**

**Without Syntax Validation**:
```python
ToolExecutionResult(
    success=True,
    output="File edited successfully (warning: syntax not validated)"
)
```

**DECISION NEEDED**: Enable Python syntax validation?

---

### Edge Case 14: Large File Performance

**Input**:
```xml
<edit>
<file>huge_file.py</file>
<find>small pattern</find>
<replace>replacement</replace>
</edit>
```

If file is 10MB+:

**Behavior**:
- Add file size limit (default: 10MB)
- Fail with helpful error if exceeded

```python
ToolExecutionResult(
    success=False,
    error="File too large: huge_file.py (15.2MB). Maximum: 10MB. Use terminal commands for large files."
)
```

---

### Edge Case 15: Circular Move

**Input**:
```xml
<move>
<from>dir1/file.py</from>
<to>dir1/file.py</to>
</move>
```

**Result**:
```python
ToolExecutionResult(
    success=False,
    error="Source and destination are the same: dir1/file.py"
)
```

---

## 6. Safety Features

### 6.1 Automatic Backups

**All Destructive Operations Create Backups**:

| Operation | Backup Created |
|-----------|----------------|
| `<edit>` | `file.py.bak` before modification |
| `<delete>` | `file.py.deleted` before removal |
| `<append>` | `file.py.bak` before append |
| `<insert>` | `file.py.bak` before insert |
| `<create overwrite="true">` | `file.py.bak` if overwriting |

**Backup Naming**:
```
original_file.py
original_file.py.bak      (edit/append/insert)
original_file.py.deleted  (delete)
```

**Backup Retention**: Keep last backup only (overwrite previous `.bak`)

---

### 6.2 Protected Paths

**Cannot Delete/Move**:
- `core/application.py`
- `main.py`
- `core/llm/*.py` (core LLM services)
- `.git/**` (git directory)
- `venv/**` (virtual environment)
- `.venv/**` (virtual environment)

**Configuration**: Add to config.json:
```json
{
  "file_operations": {
    "protected_files": [
      "core/application.py",
      "main.py"
    ],
    "protected_patterns": [
      "core/llm/*.py",
      ".git/**",
      "venv/**"
    ]
  }
}
```

---

### 6.3 File Size Limits

**Default Limits**:
- Max file size to edit: 10 MB
- Max file size to create: 5 MB
- Max file size to read: 10 MB

**Configuration**:
```json
{
  "file_operations": {
    "max_edit_size_mb": 10,
    "max_create_size_mb": 5,
    "max_read_size_mb": 10
  }
}
```

---

### 6.4 Syntax Validation (Optional)

**For Python Files**:
After editing `.py` files, optionally validate syntax:

```python
import ast

def validate_python_syntax(filepath: str) -> bool:
    try:
        with open(filepath, 'r') as f:
            ast.parse(f.read())
        return True
    except SyntaxError:
        return False
```

**On Validation Failure**:
1. Log error with line number
2. Restore from `.bak` backup
3. Return error to LLM

**Configuration**:
```json
{
  "file_operations": {
    "validate_python_syntax": true,
    "rollback_on_syntax_error": true
  }
}
```

---

### 6.5 Binary File Detection

**Check File Type**:
```python
def is_text_file(filepath: str) -> bool:
    """Check if file is text (not binary)."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            f.read(1024)  # Try reading first 1KB as text
        return True
    except UnicodeDecodeError:
        return False
```

**Block Binary Operations**:
- Cannot edit binary files
- Cannot append to binary files
- Can still copy/move/delete binary files

---

## 7. Tool Result Format

### Success - Edit (Single Replacement)
```python
ToolExecutionResult(
    tool_id="file_edit_0",
    tool_type="file_edit",
    success=True,
    output="✅ Replaced 1 occurrence in core/llm/llm_service.py\nBackup: core/llm/llm_service.py.bak",
    execution_time=0.08
)
```

### Success - Edit (Multiple Replacements)
```python
ToolExecutionResult(
    tool_id="file_edit_0",
    tool_type="file_edit",
    success=True,
    output="✅ Replaced 5 occurrences in core/llm/llm_service.py\nLocations: lines 42, 78, 103, 145, 201\nBackup: core/llm/llm_service.py.bak",
    execution_time=0.12
)
```

### Success - Create
```python
ToolExecutionResult(
    tool_id="file_create_0",
    tool_type="file_create",
    success=True,
    output="✅ Created plugins/analytics_plugin.py (245 bytes)",
    execution_time=0.03
)
```

### Success - Delete
```python
ToolExecutionResult(
    tool_id="file_delete_0",
    tool_type="file_delete",
    success=True,
    output="✅ Deleted backups/old_file.py\nBackup: backups/old_file.py.deleted",
    execution_time=0.02
)
```

### Success - Move
```python
ToolExecutionResult(
    tool_id="file_move_0",
    tool_type="file_move",
    success=True,
    output="✅ Moved plugins/old_name.py → plugins/new_name.py",
    execution_time=0.04
)
```

### Failure - Pattern Not Found
```python
ToolExecutionResult(
    tool_id="file_edit_0",
    tool_type="file_edit",
    success=False,
    error="❌ Pattern not found in core/llm/llm_service.py\n\nSearched for:\n  class OldName:\n\nFile not modified.",
    execution_time=0.05
)
```

### Failure - Ambiguous Match (Insert Operations Only)
```python
ToolExecutionResult(
    tool_id="file_insert_after_0",
    tool_type="file_insert_after",
    success=False,
    error="❌ Ambiguous pattern: 'import logging' appears 3 times in core/llm/llm_service.py\n\nLocations:\n  Line 5: import logging\n  Line 42: import logging\n  Line 89: import logging\n\nPattern must be unique for insert operations. Use <edit> with full context instead.",
    execution_time=0.06
)
```

**Note**: `<edit>` operations do NOT fail on ambiguous matches - they replace all occurrences and report the count.

---

## 8. Implementation Architecture

### 8.1 Response Parser Updates

**File**: `core/llm/response_parser.py`

```python
class ResponseParser:
    def __init__(self):
        # Existing patterns
        self.thinking_pattern = re.compile(r'<think>(.*?)</think>', re.DOTALL | re.IGNORECASE)
        self.terminal_pattern = re.compile(r'<terminal>(.*?)</terminal>', re.DOTALL | re.IGNORECASE)

        # NEW: File operation patterns (no attributes - simple tags only)
        self.edit_pattern = re.compile(r'<edit>(.*?)</edit>', re.DOTALL | re.IGNORECASE)
        self.create_pattern = re.compile(r'<create>(.*?)</create>', re.DOTALL | re.IGNORECASE)
        self.create_overwrite_pattern = re.compile(r'<create_overwrite>(.*?)</create_overwrite>', re.DOTALL | re.IGNORECASE)
        self.delete_pattern = re.compile(r'<delete>(.*?)</delete>', re.DOTALL | re.IGNORECASE)
        self.move_pattern = re.compile(r'<move>(.*?)</move>', re.DOTALL | re.IGNORECASE)
        self.copy_pattern = re.compile(r'<copy>(.*?)</copy>', re.DOTALL | re.IGNORECASE)
        self.copy_overwrite_pattern = re.compile(r'<copy_overwrite>(.*?)</copy_overwrite>', re.DOTALL | re.IGNORECASE)
        self.append_pattern = re.compile(r'<append>(.*?)</append>', re.DOTALL | re.IGNORECASE)
        self.insert_after_pattern = re.compile(r'<insert_after>(.*?)</insert_after>', re.DOTALL | re.IGNORECASE)
        self.insert_before_pattern = re.compile(r'<insert_before>(.*?)</insert_before>', re.DOTALL | re.IGNORECASE)
        self.mkdir_pattern = re.compile(r'<mkdir>(.*?)</mkdir>', re.DOTALL | re.IGNORECASE)
        self.rmdir_pattern = re.compile(r'<rmdir>(.*?)</rmdir>', re.DOTALL | re.IGNORECASE)
        self.read_pattern = re.compile(r'<read>(.*?)</read>', re.DOTALL | re.IGNORECASE)

    def _extract_file_operations(self, content: str) -> List[Dict[str, Any]]:
        """Extract all file operation blocks."""
        operations = []

        # Extract edit operations
        for match in self.edit_pattern.finditer(content):
            operations.append(self._parse_edit_operation(match.group(1)))

        # Extract create operations
        for match in self.create_pattern.finditer(content):
            operations.append(self._parse_create_operation(match.group(0), match.group(1)))

        # ... extract other operations

        return operations

    def _parse_edit_operation(self, xml_content: str) -> Dict[str, Any]:
        """Parse <edit> XML content."""
        # Extract nested tags
        file_match = re.search(r'<file>(.*?)</file>', xml_content, re.DOTALL)
        find_match = re.search(r'<find>(.*?)</find>', xml_content, re.DOTALL)
        replace_match = re.search(r'<replace>(.*?)</replace>', xml_content, re.DOTALL)

        return {
            "type": "file_edit",
            "file": file_match.group(1).strip() if file_match else None,
            "find": find_match.group(1) if find_match else None,
            "replace": replace_match.group(1) if replace_match else None
        }
```

---

### 8.2 Tool Executor Updates

**File**: `core/llm/tool_executor.py`

```python
class ToolExecutor:
    async def execute_tool(self, tool_data: Dict[str, Any]) -> ToolExecutionResult:
        """Execute a single tool."""
        tool_type = tool_data.get("type", "unknown")

        if tool_type == "terminal":
            return await self._execute_terminal_command(tool_data)
        elif tool_type == "mcp_tool":
            return await self._execute_mcp_tool(tool_data)

        # NEW: File operations
        elif tool_type == "file_edit":
            return await self._execute_file_edit(tool_data)
        elif tool_type == "file_create":
            return await self._execute_file_create(tool_data)
        elif tool_type == "file_delete":
            return await self._execute_file_delete(tool_data)
        elif tool_type == "file_move":
            return await self._execute_file_move(tool_data)
        elif tool_type == "file_copy":
            return await self._execute_file_copy(tool_data)
        elif tool_type == "file_append":
            return await self._execute_file_append(tool_data)
        elif tool_type == "file_insert_after":
            return await self._execute_file_insert_after(tool_data)
        elif tool_type == "file_insert_before":
            return await self._execute_file_insert_before(tool_data)
        elif tool_type == "file_mkdir":
            return await self._execute_file_mkdir(tool_data)
        elif tool_type == "file_rmdir":
            return await self._execute_file_rmdir(tool_data)
        elif tool_type == "file_read":
            return await self._execute_file_read(tool_data)
        else:
            return ToolExecutionResult(
                tool_id=tool_data.get("id", "unknown"),
                tool_type=tool_type,
                success=False,
                error=f"Unknown tool type: {tool_type}"
            )

    async def _execute_file_edit(self, tool_data: Dict[str, Any]) -> ToolExecutionResult:
        """Execute file edit operation."""
        filepath = tool_data.get("file")
        find_content = tool_data.get("find")
        replace_content = tool_data.get("replace")

        # Validation
        if not filepath or not find_content or replace_content is None:
            return ToolExecutionResult(
                tool_id=tool_data.get("id", "unknown"),
                tool_type="file_edit",
                success=False,
                error="Missing required fields: file, find, replace"
            )

        # Check file exists
        if not os.path.exists(filepath):
            return ToolExecutionResult(
                tool_id=tool_data.get("id", "unknown"),
                tool_type="file_edit",
                success=False,
                error=f"File not found: {filepath}"
            )

        # Read file
        with open(filepath, 'r') as f:
            content = f.read()

        # Check pattern match
        count = content.count(find_content)
        if count == 0:
            return ToolExecutionResult(
                tool_id=tool_data.get("id", "unknown"),
                tool_type="file_edit",
                success=False,
                error=f"Pattern not found in {filepath}"
            )

        # Find line numbers where pattern appears (for reporting)
        lines = content.split('\n')
        line_numbers = []
        for i, line in enumerate(lines, 1):
            if find_content in '\n'.join(lines[max(0, i-1):i+10]):  # Check multi-line patterns
                # More sophisticated line number detection needed here
                pass

        # Create backup
        backup_path = f"{filepath}.bak"
        shutil.copy2(filepath, backup_path)

        # Perform replacement (REPLACE ALL occurrences)
        new_content = content.replace(find_content, replace_content)

        # Write back
        with open(filepath, 'w') as f:
            f.write(new_content)

        # Optional: Validate Python syntax
        if filepath.endswith('.py') and self.config.get("file_operations.validate_python_syntax"):
            if not self._validate_python_syntax(filepath):
                # Rollback
                shutil.copy2(backup_path, filepath)
                return ToolExecutionResult(
                    tool_id=tool_data.get("id", "unknown"),
                    tool_type="file_edit",
                    success=False,
                    error=f"Syntax validation failed. Edit rolled back."
                )

        # Build success message with count
        if count == 1:
            output_msg = f"✅ Replaced 1 occurrence in {filepath}\nBackup: {backup_path}"
        else:
            output_msg = f"✅ Replaced {count} occurrences in {filepath}\nBackup: {backup_path}"

        return ToolExecutionResult(
            tool_id=tool_data.get("id", "unknown"),
            tool_type="file_edit",
            success=True,
            output=output_msg
        )
```

---

## 9. Configuration

**Add to `.kollabor-cli/config.json`**:

```json
{
  "file_operations": {
    "enabled": true,
    "automatic_backups": true,
    "validate_python_syntax": true,
    "rollback_on_syntax_error": true,
    "max_edit_size_mb": 10,
    "max_create_size_mb": 5,
    "max_read_size_mb": 10,
    "protected_files": [
      "core/application.py",
      "main.py",
      "core/llm/llm_service.py"
    ],
    "protected_patterns": [
      ".git/**",
      "venv/**",
      ".venv/**",
      "node_modules/**"
    ],
    "allow_binary_operations": false,
    "create_parent_directories": true
  }
}
```

---

## 10. System Prompt Integration

**Add to `.marco/default.md`**:

```markdown
## File Operations

You can safely modify files using structured XML tags.

### Edit File (Replace Content)

<edit>
<file>path/to/file.py</file>
<find>
exact content to find
</find>
<replace>
new content to replace with
</replace>
</edit>

**Rules**:
- `<find>` content must match at least once in file (error if not found)
- **Replaces ALL occurrences** - reports count back to you
- If pattern appears 5 times, all 5 are replaced
- To replace only one specific location, provide more context in `<find>` block
- Whitespace and indentation must match exactly
- Automatic `.bak` backup created before editing

### Create New File

<create>
<file>path/to/new_file.py</file>
<content>
file content here
</content>
</create>

### Delete File

<delete>
<file>path/to/file.py</file>
</delete>

**Note**: Protected files (core/application.py, main.py, etc.) cannot be deleted.

### Move/Rename File

<move>
<from>old/path/file.py</from>
<to>new/path/file.py</to>
</move>

### Copy File

<copy>
<from>source/file.py</from>
<to>destination/file.py</to>
</copy>

### Append to File

<append>
<file>path/to/file.py</file>
<content>
content to append at end
</content>
</append>

### Insert After Pattern

<insert_after>
<file>path/to/file.py</file>
<pattern>import logging</pattern>
<content>
from typing import Optional
</content>
</insert_after>

**Important**: Pattern must appear exactly once in file. If pattern appears multiple times, operation fails with error showing line numbers.

### Insert Before Pattern

<insert_before>
<file>path/to/file.py</file>
<pattern>class MyClass:</pattern>
<content>
# Comment above class
</content>
</insert_before>

**Important**: Pattern must appear exactly once in file. For ambiguous patterns, use `<edit>` with full context instead.

---

**All operations create automatic backups and validate file integrity.**
```

---

## 11. Implementation Checklist

### Phase 1: Core Edit Operation
- [ ] Add `edit_pattern` to ResponseParser
- [ ] Implement `_parse_edit_operation()` in ResponseParser
- [ ] Add "file_edit" to tool type handling in ToolExecutor
- [ ] Implement `_execute_file_edit()` in ToolExecutor
- [ ] Add file validation (exists, readable, text-only)
- [ ] Add exact match counting (0/1/many)
- [ ] Add backup creation
- [ ] Add Python syntax validation (optional)
- [ ] Add rollback on validation failure

### Phase 2: Create/Delete Operations
- [ ] Add `create_pattern` to ResponseParser
- [ ] Add `delete_pattern` to ResponseParser
- [ ] Implement `_parse_create_operation()`
- [ ] Implement `_parse_delete_operation()`
- [ ] Implement `_execute_file_create()`
- [ ] Implement `_execute_file_delete()`
- [ ] Add protected file checking
- [ ] Add overwrite flag support for create

### Phase 3: Move/Copy Operations
- [ ] Add `move_pattern` to ResponseParser
- [ ] Add `copy_pattern` to ResponseParser
- [ ] Implement `_parse_move_operation()`
- [ ] Implement `_parse_copy_operation()`
- [ ] Implement `_execute_file_move()`
- [ ] Implement `_execute_file_copy()`
- [ ] Add parent directory creation for move/copy

### Phase 4: Advanced Operations
- [ ] Add `append_pattern` to ResponseParser
- [ ] Add `insert_pattern` to ResponseParser
- [ ] Implement `_execute_file_append()`
- [ ] Implement `_execute_file_insert()`
- [ ] Add mode detection for insert (before/after)
- [ ] Add pattern matching for insert

### Phase 5: Directory Operations
- [ ] Add `mkdir_pattern` to ResponseParser
- [ ] Add `rmdir_pattern` to ResponseParser
- [ ] Implement `_execute_file_mkdir()`
- [ ] Implement `_execute_file_rmdir()`
- [ ] Add recursive directory creation
- [ ] Add empty directory validation for rmdir

### Phase 6: Safety & Config
- [ ] Add configuration section to config.json
- [ ] Implement protected file checking
- [ ] Implement file size limits
- [ ] Implement binary file detection
- [ ] Add backup management
- [ ] Add syntax validation toggle

### Phase 7: Testing
- [ ] Unit tests for ResponseParser (each operation type)
- [ ] Unit tests for ToolExecutor (each operation)
- [ ] Integration tests (end-to-end file operations)
- [ ] Edge case tests (all 15 edge cases)
- [ ] Error handling tests
- [ ] Protected file tests
- [ ] Binary file detection tests
- [ ] Syntax validation tests

### Phase 8: Documentation
- [ ] Update system prompt (`.marco/default.md`)
- [ ] Add examples to system prompt
- [ ] Update CLAUDE.md
- [ ] Create user documentation
- [ ] Add inline code comments
- [ ] Create troubleshooting guide

---

## 12. XML Parsing Strategy (No XML Parser)

### Why Not Use Native XML Parsers?

**Problem with XML Parsers**:
- Would require LLM to escape code: `<![CDATA[code here]]>`
- Too complex for LLM to generate reliably
- Extra cognitive load
- More tokens wasted on escaping

**Our Solution**: Simple regex-based parsing that treats tag content as raw text.

---

### Parsing Algorithm

#### Step 1: Find Operation Blocks (Outer Tags)

Extract top-level operation blocks using regex:

```python
import re

class FileOperationParser:
    def __init__(self):
        # Operation-level patterns (outer tags only)
        self.edit_pattern = re.compile(
            r'<edit>(.*?)</edit>',
            re.DOTALL | re.IGNORECASE
        )
        self.create_pattern = re.compile(
            r'<create>(.*?)</create>',
            re.DOTALL | re.IGNORECASE
        )
        self.insert_after_pattern = re.compile(
            r'<insert_after>(.*?)</insert_after>',
            re.DOTALL | re.IGNORECASE
        )
        # ... etc for all operations

    def parse_response(self, llm_response: str) -> List[dict]:
        """Extract all file operations from LLM response."""
        operations = []

        # Find all <edit> blocks
        for match in self.edit_pattern.finditer(llm_response):
            inner_content = match.group(1)
            try:
                op = self._parse_edit_block(inner_content)
                operations.append(op)
            except ValueError as e:
                logger.error(f"Invalid <edit> block: {e}")
                # Continue parsing other blocks

        # Find all <create> blocks
        for match in self.create_pattern.finditer(llm_response):
            inner_content = match.group(1)
            try:
                op = self._parse_create_block(inner_content)
                operations.append(op)
            except ValueError as e:
                logger.error(f"Invalid <create> block: {e}")

        # ... same for other operations

        return operations
```

**Key Point**: `.*?` (non-greedy) matches everything between first `<edit>` and first `</edit>`, treating it as raw text.

---

#### Step 2: Extract Nested Tags (Inner Content)

Parse nested tags from the inner content:

```python
def _parse_edit_block(self, content: str) -> dict:
    """Parse <edit> inner content into structured data."""

    # Extract nested tags using regex
    file_match = re.search(r'<file>(.*?)</file>', content, re.DOTALL)
    find_match = re.search(r'<find>(.*?)</find>', content, re.DOTALL)
    replace_match = re.search(r'<replace>(.*?)</replace>', content, re.DOTALL)

    # Validate required tags exist
    if not file_match:
        raise ValueError("Missing required tag: <file>")
    if not find_match:
        raise ValueError("Missing required tag: <find>")
    if not replace_match:
        raise ValueError("Missing required tag: <replace>")

    # Extract raw content (everything between tags is TEXT)
    return {
        "type": "file_edit",
        "file": file_match.group(1).strip(),      # Strip whitespace from file path
        "find": find_match.group(1),              # Preserve exact whitespace
        "replace": replace_match.group(1)         # Preserve exact whitespace
    }

def _parse_create_block(self, content: str) -> dict:
    """Parse <create> inner content."""
    file_match = re.search(r'<file>(.*?)</file>', content, re.DOTALL)
    content_match = re.search(r'<content>(.*?)</content>', content, re.DOTALL)

    if not file_match:
        raise ValueError("Missing <file> tag")
    if not content_match:
        raise ValueError("Missing <content> tag")

    return {
        "type": "file_create",
        "file": file_match.group(1).strip(),
        "content": content_match.group(1)
    }

def _parse_insert_after_block(self, content: str) -> dict:
    """Parse <insert_after> inner content."""
    file_match = re.search(r'<file>(.*?)</file>', content, re.DOTALL)
    pattern_match = re.search(r'<pattern>(.*?)</pattern>', content, re.DOTALL)
    content_match = re.search(r'<content>(.*?)</content>', content, re.DOTALL)

    if not file_match:
        raise ValueError("Missing <file> tag")
    if not pattern_match:
        raise ValueError("Missing <pattern> tag")
    if not content_match:
        raise ValueError("Missing <content> tag")

    return {
        "type": "file_insert_after",
        "file": file_match.group(1).strip(),
        "pattern": pattern_match.group(1),
        "content": content_match.group(1)
    }
```

---

#### Step 3: Validate Extracted Data

```python
def validate_edit_operation(op: dict) -> tuple[bool, str]:
    """Validate edit operation structure and content."""

    # Check required fields exist
    if not op.get("file"):
        return False, "Empty <file> tag"

    if not op.get("find"):
        return False, "Empty <find> tag"

    if op.get("replace") is None:  # Allow empty string
        return False, "Missing <replace> tag"

    # Validate file path
    filepath = op["file"]

    if ".." in filepath:
        return False, f"Security: Path traversal detected in '{filepath}'"

    if filepath.startswith("/"):
        return False, f"Security: Absolute paths not allowed '{filepath}'"

    if len(filepath) > 255:
        return False, f"File path too long: {len(filepath)} chars (max 255)"

    # All validation passed
    return True, ""


def validate_create_operation(op: dict) -> tuple[bool, str]:
    """Validate create operation."""

    if not op.get("file"):
        return False, "Empty <file> tag"

    if not op.get("content"):
        return False, "Empty <content> tag"

    filepath = op["file"]

    if ".." in filepath:
        return False, f"Security: Path traversal detected"

    if filepath.startswith("/"):
        return False, f"Security: Absolute paths not allowed"

    return True, ""
```

---

### How This Handles Edge Cases

#### Edge Case 1: Code with `<` and `>` Characters

**Input**:
```xml
<edit>
<file>test.py</file>
<find>
if x < 5 and y > 3:
    pattern = r'<.*?>'
</find>
<replace>
if x <= 5 and y >= 3:
    pattern = r'<[^>]+>'
</replace>
</edit>
```

**Parsing**:
```python
# Regex matches: <find> ... </find>
# Content between tags is treated as RAW TEXT:
find_content = "if x < 5 and y > 3:\n    pattern = r'<.*?>'"

# The < and > inside are just text characters
# No escaping needed!
```

✅ **Works perfectly** - regex only looks for `<find>` and `</find>` tags, everything else is text.

---

#### Edge Case 2: Nested XML-like Structure

**Input**:
```xml
<edit>
<file>template.html</file>
<find>
<div class="old">
  <span>Content</span>
</div>
</find>
<replace>
<div class="new">
  <span>Updated</span>
</div>
</replace>
</edit>
```

**Parsing**:
```python
# Regex matches FIRST <find> to FIRST </find>
find_content = '''<div class="old">
  <span>Content</span>
</div>'''

# HTML tags inside are just TEXT
# No conflict with operation tags
```

✅ **Works perfectly** - only top-level operation tags are parsed.

---

#### Edge Case 3: Code Comments with Tag Names

**Input**:
```xml
<edit>
<file>parser.py</file>
<find>
# TODO: Fix <tag> parsing
# The </tag> closer is broken
def parse():
    pass
</find>
<replace>
# DONE: Fixed <tag> parsing
# The </tag> closer works now
def parse():
    return parsed_data
</replace>
</edit>
```

**Parsing**:
```python
find_content = '''# TODO: Fix <tag> parsing
# The </tag> closer is broken
def parse():
    pass'''
```

✅ **Works perfectly** - comments are just text.

---

#### Edge Case 4: String Literals with Closing Tags

**Input**:
```xml
<edit>
<file>test.py</file>
<find>
error_msg = "Missing </find> tag"
</find>
<replace>
error_msg = "Missing closing tag"
</replace>
</edit>
```

**Problem**: The regex `<find>(.*?)</find>` will match up to the FIRST `</find>`, which is inside the string literal!

**Result**:
```python
# WRONG - stops at first </find>
find_content = 'error_msg = "Missing '
# The rest is ignored
```

❌ **This breaks!**

**Solutions**:

**Option A**: Document this limitation
```markdown
**Known Limitation**: Content cannot contain literal `</tag>` strings.

If you need to include closing tags in your code:
- Use variables: `closing = '</find>'`
- Use escape sequences: `'<' + '/find' + '>'`
- Use different quotes: `"</find>"` if parsing single quotes
```

**Option B**: Greedy matching (match to LAST occurrence)
```python
# Match to LAST </find> instead of first
find_match = re.search(r'<find>(.*)</find>', content, re.DOTALL)
```

But this also breaks if content ends with `</find>`.

**Option C**: Multi-pass parsing with tag balancing
```python
def extract_tag_content(tag_name: str, content: str) -> str:
    """Extract content between balanced tags."""
    start_tag = f"<{tag_name}>"
    end_tag = f"</{tag_name}>"

    start_idx = content.find(start_tag)
    if start_idx == -1:
        raise ValueError(f"Missing <{tag_name}> tag")

    # Start after opening tag
    pos = start_idx + len(start_tag)
    depth = 1

    while pos < len(content) and depth > 0:
        # Check for nested opening tags
        if content[pos:pos+len(start_tag)] == start_tag:
            depth += 1
            pos += len(start_tag)
        # Check for closing tags
        elif content[pos:pos+len(end_tag)] == end_tag:
            depth -= 1
            if depth == 0:
                # Found matching closing tag
                return content[start_idx + len(start_tag):pos]
            pos += len(end_tag)
        else:
            pos += 1

    raise ValueError(f"Unclosed <{tag_name}> tag")
```

**Recommendation**: Use **Option A** (document limitation) + **Option C** (tag balancing) for edge cases.

---

### Complete Parser Implementation

```python
import re
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)


class FileOperationParser:
    """Parse file operations from LLM response without XML parser."""

    def __init__(self):
        # Operation-level patterns (outer tags)
        self.edit_pattern = re.compile(r'<edit>(.*?)</edit>', re.DOTALL | re.IGNORECASE)
        self.create_pattern = re.compile(r'<create>(.*?)</create>', re.DOTALL | re.IGNORECASE)
        self.create_overwrite_pattern = re.compile(r'<create_overwrite>(.*?)</create_overwrite>', re.DOTALL | re.IGNORECASE)
        self.delete_pattern = re.compile(r'<delete>(.*?)</delete>', re.DOTALL | re.IGNORECASE)
        self.move_pattern = re.compile(r'<move>(.*?)</move>', re.DOTALL | re.IGNORECASE)
        self.copy_pattern = re.compile(r'<copy>(.*?)</copy>', re.DOTALL | re.IGNORECASE)
        self.copy_overwrite_pattern = re.compile(r'<copy_overwrite>(.*?)</copy_overwrite>', re.DOTALL | re.IGNORECASE)
        self.append_pattern = re.compile(r'<append>(.*?)</append>', re.DOTALL | re.IGNORECASE)
        self.insert_after_pattern = re.compile(r'<insert_after>(.*?)</insert_after>', re.DOTALL | re.IGNORECASE)
        self.insert_before_pattern = re.compile(r'<insert_before>(.*?)</insert_before>', re.DOTALL | re.IGNORECASE)
        self.mkdir_pattern = re.compile(r'<mkdir>(.*?)</mkdir>', re.DOTALL | re.IGNORECASE)
        self.rmdir_pattern = re.compile(r'<rmdir>(.*?)</rmdir>', re.DOTALL | re.IGNORECASE)
        self.read_pattern = re.compile(r'<read>(.*?)</read>', re.DOTALL | re.IGNORECASE)

    def parse_response(self, llm_response: str) -> List[Dict[str, Any]]:
        """Extract all file operations from LLM response.

        Returns:
            List of operation dictionaries with type and parameters
        """
        operations = []

        # Parse each operation type
        operations.extend(self._parse_operations(self.edit_pattern, self._parse_edit_block, llm_response))
        operations.extend(self._parse_operations(self.create_pattern, self._parse_create_block, llm_response))
        operations.extend(self._parse_operations(self.create_overwrite_pattern, self._parse_create_overwrite_block, llm_response))
        operations.extend(self._parse_operations(self.insert_after_pattern, self._parse_insert_after_block, llm_response))
        operations.extend(self._parse_operations(self.insert_before_pattern, self._parse_insert_before_block, llm_response))
        # ... etc for all operation types

        return operations

    def _parse_operations(self, pattern: re.Pattern, parser_func: callable, text: str) -> List[Dict[str, Any]]:
        """Generic operation parser."""
        operations = []

        for match in pattern.finditer(text):
            inner_content = match.group(1)
            try:
                op = parser_func(inner_content)
                operations.append(op)
            except ValueError as e:
                logger.error(f"Invalid operation block: {e}")
                # Continue parsing other blocks

        return operations

    def _extract_tag(self, tag_name: str, content: str, required: bool = True) -> str:
        """Extract content between tags.

        Args:
            tag_name: Tag name (without < >)
            content: Content to search in
            required: If True, raises ValueError if tag not found

        Returns:
            Content between tags, or None if not found and not required
        """
        pattern = re.compile(f'<{tag_name}>(.*?)</{tag_name}>', re.DOTALL | re.IGNORECASE)
        match = pattern.search(content)

        if not match:
            if required:
                raise ValueError(f"Missing required tag: <{tag_name}>")
            return None

        return match.group(1)

    def _parse_edit_block(self, content: str) -> Dict[str, Any]:
        """Parse <edit> block."""
        return {
            "type": "file_edit",
            "file": self._extract_tag("file", content).strip(),
            "find": self._extract_tag("find", content),      # Preserve whitespace
            "replace": self._extract_tag("replace", content)  # Preserve whitespace
        }

    def _parse_create_block(self, content: str) -> Dict[str, Any]:
        """Parse <create> block."""
        return {
            "type": "file_create",
            "file": self._extract_tag("file", content).strip(),
            "content": self._extract_tag("content", content)
        }

    def _parse_create_overwrite_block(self, content: str) -> Dict[str, Any]:
        """Parse <create_overwrite> block."""
        return {
            "type": "file_create_overwrite",
            "file": self._extract_tag("file", content).strip(),
            "content": self._extract_tag("content", content)
        }

    def _parse_insert_after_block(self, content: str) -> Dict[str, Any]:
        """Parse <insert_after> block."""
        return {
            "type": "file_insert_after",
            "file": self._extract_tag("file", content).strip(),
            "pattern": self._extract_tag("pattern", content),
            "content": self._extract_tag("content", content)
        }

    def _parse_insert_before_block(self, content: str) -> Dict[str, Any]:
        """Parse <insert_before> block."""
        return {
            "type": "file_insert_before",
            "file": self._extract_tag("file", content).strip(),
            "pattern": self._extract_tag("pattern", content),
            "content": self._extract_tag("content", content)
        }
```

---

### Validation Functions

```python
def validate_file_path(filepath: str) -> Tuple[bool, str]:
    """Validate file path for security and correctness.

    Returns:
        (is_valid, error_message)
    """
    if not filepath:
        return False, "Empty file path"

    # Security: No path traversal
    if ".." in filepath:
        return False, f"Path traversal detected: {filepath}"

    # Security: No absolute paths
    if filepath.startswith("/"):
        return False, f"Absolute paths not allowed: {filepath}"

    # Practical: Path length limit
    if len(filepath) > 255:
        return False, f"Path too long: {len(filepath)} chars (max 255)"

    # Security: No null bytes
    if "\x00" in filepath:
        return False, "Null byte in file path"

    return True, ""


def validate_operation(op: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate a parsed operation.

    Returns:
        (is_valid, error_message)
    """
    op_type = op.get("type")

    if op_type == "file_edit":
        # Check required fields
        if not op.get("file"):
            return False, "Missing file path"
        if not op.get("find"):
            return False, "Empty <find> content"
        if op.get("replace") is None:
            return False, "Missing <replace> tag"

        # Validate file path
        return validate_file_path(op["file"])

    elif op_type in ("file_create", "file_create_overwrite"):
        if not op.get("file"):
            return False, "Missing file path"
        if not op.get("content"):
            return False, "Empty <content> tag"

        return validate_file_path(op["file"])

    elif op_type in ("file_insert_after", "file_insert_before"):
        if not op.get("file"):
            return False, "Missing file path"
        if not op.get("pattern"):
            return False, "Empty <pattern> tag"
        if not op.get("content"):
            return False, "Empty <content> tag"

        return validate_file_path(op["file"])

    # ... validation for other operation types

    return True, ""
```

---

### Error Reporting

```python
def format_parse_error(error: ValueError, operation_type: str, content_preview: str) -> str:
    """Format parsing error for LLM feedback.

    Args:
        error: The validation error
        operation_type: Type of operation (e.g., "edit", "create")
        content_preview: First 200 chars of malformed content

    Returns:
        Formatted error message for LLM
    """
    return f"""❌ Malformed <{operation_type}> block

Error: {str(error)}

Content preview:
{content_preview[:200]}...

Expected format:
<{operation_type}>
<file>path/to/file</file>
<find>content to find</find>
<replace>replacement content</replace>
</{operation_type}>

Please check:
- All required tags are present
- Tags are properly closed
- No typos in tag names
"""
```

---

### Known Limitations & Workarounds

#### Limitation 1: Closing Tags in Content

**Problem**: Content cannot contain literal closing tags like `</find>`

**Workaround**:
```python
# Instead of:
code = '</find>'

# Use:
code = '<' + '/find' + '>'  # Concatenation
code = '</' + 'find>'       # Split differently
closing_tag = '</find>'     # Different variable name
```

**System Prompt Guidance**:
```markdown
**Important**: Avoid putting closing tags like `</find>`, `</replace>` inside your code content.

If you must include them:
- Use string concatenation: `'<' + '/find' + '>'`
- Use variables: `tag = '</find>'`
```

---

#### Limitation 2: Very Large Content Blocks

**Problem**: Regex can be slow on very large strings (>100KB)

**Workaround**:
- Add content size limit (e.g., 10MB max per operation)
- Warn LLM if content exceeds threshold

```python
MAX_OPERATION_SIZE = 10 * 1024 * 1024  # 10MB

def check_operation_size(content: str) -> Tuple[bool, str]:
    size = len(content)
    if size > MAX_OPERATION_SIZE:
        return False, f"Operation too large: {size} bytes (max {MAX_OPERATION_SIZE})"
    return True, ""
```

---

### Testing Strategy

```python
def test_parse_edit_simple():
    """Test basic edit parsing."""
    response = """
    <edit>
    <file>test.py</file>
    <find>old code</find>
    <replace>new code</replace>
    </edit>
    """

    parser = FileOperationParser()
    ops = parser.parse_response(response)

    assert len(ops) == 1
    assert ops[0]["type"] == "file_edit"
    assert ops[0]["file"] == "test.py"
    assert ops[0]["find"] == "old code"
    assert ops[0]["replace"] == "new code"


def test_parse_edit_with_xml_chars():
    """Test parsing code with < and > characters."""
    response = """
    <edit>
    <file>test.py</file>
    <find>
    if x < 5:
        pattern = r'<.*?>'
    </find>
    <replace>
    if x <= 5:
        pattern = r'<[^>]+>'
    </replace>
    </edit>
    """

    parser = FileOperationParser()
    ops = parser.parse_response(response)

    assert len(ops) == 1
    assert "x < 5" in ops[0]["find"]
    assert "r'<.*?>'" in ops[0]["find"]


def test_parse_multiple_operations():
    """Test parsing multiple operations in one response."""
    response = """
    I'll make these changes:

    <edit>
    <file>file1.py</file>
    <find>old1</find>
    <replace>new1</replace>
    </edit>

    Then create a new file:

    <create>
    <file>file2.py</file>
    <content>content here</content>
    </create>
    """

    parser = FileOperationParser()
    ops = parser.parse_response(response)

    assert len(ops) == 2
    assert ops[0]["type"] == "file_edit"
    assert ops[1]["type"] == "file_create"


def test_parse_missing_tag():
    """Test error handling for missing tags."""
    response = """
    <edit>
    <file>test.py</file>
    <find>old code</find>
    <!-- Missing </replace> tag -->
    </edit>
    """

    parser = FileOperationParser()
    ops = parser.parse_response(response)

    # Should skip malformed block and continue
    assert len(ops) == 0
```

---

### Integration with ResponseParser

Update the existing `ResponseParser` class:

```python
class ResponseParser:
    """Parse LLM responses for all content types."""

    def __init__(self):
        # Existing patterns
        self.thinking_pattern = re.compile(r'<think>(.*?)</think>', re.DOTALL | re.IGNORECASE)
        self.terminal_pattern = re.compile(r'<terminal>(.*?)</terminal>', re.DOTALL | re.IGNORECASE)

        # NEW: File operations parser
        self.file_ops_parser = FileOperationParser()

    def parse_response(self, raw_response: str) -> Dict[str, Any]:
        """Parse complete LLM response."""

        # Extract thinking blocks
        thinking_blocks = self._extract_thinking(raw_response)

        # Extract terminal commands
        terminal_commands = self._extract_terminal_commands(raw_response)

        # NEW: Extract file operations
        file_operations = self.file_ops_parser.parse_response(raw_response)

        # Clean content (remove all tags)
        clean_content = self._clean_content(raw_response)

        return {
            "raw": raw_response,
            "content": clean_content,
            "turn_completed": len(terminal_commands) == 0 and len(file_operations) == 0,
            "components": {
                "thinking": thinking_blocks,
                "terminal_commands": terminal_commands,
                "file_operations": file_operations  # NEW
            },
            "metadata": {
                "has_thinking": bool(thinking_blocks),
                "has_terminal_commands": bool(terminal_commands),
                "has_file_operations": bool(file_operations),  # NEW
                "total_tools": len(terminal_commands) + len(file_operations)
            }
        }
```

---

### Summary

**Parsing Strategy**:
1. ✅ Use regex (not XML parser) - simpler, no CDATA needed
2. ✅ Match outer tags first (`<edit>...</edit>`)
3. ✅ Extract inner tags as raw text
4. ✅ Validate required tags exist
5. ✅ Validate file paths for security
6. ✅ Report clear errors for malformed blocks

**Benefits**:
- LLM writes natural code (no escaping)
- Fast regex parsing
- Clear error messages
- Handles edge cases gracefully
- Security validation built-in

**Known Limitations**:
- Content cannot contain literal closing tags (rare edge case)
- Document workarounds in system prompt

---

## 13. Questions Requiring Decisions

### DECISION 1: Parent Directory Creation

When creating files in non-existent directories:

**Option A**: Auto-create parent directories (like `mkdir -p`)
**Option B**: Fail and require explicit `<mkdir>` first

**Your choice**: _______________

---

### DECISION 2: Python Syntax Validation

After editing `.py` files:

**Option A**: Always validate syntax, rollback on error
**Option B**: Validate only if config flag enabled
**Option C**: Never validate (trust the edit)

**Your choice**: _______________

---

### DECISION 3: Backup Retention

**Option A**: Keep only last backup (overwrite `.bak` each time)
**Option B**: Keep timestamped backups (`file.py.bak.20251107_153000`)
**Option C**: No automatic backups (user manages)

**Your choice**: _______________

---

### DECISION 4: Binary File Handling

**Option A**: Block all operations on binary files
**Option B**: Allow copy/move/delete, block edit/append/insert
**Option C**: Allow all operations (unsafe)

**Your choice**: _______________

---

### DECISION 5: Maximum File Size

**Option A**: 10MB limit (default)
**Option B**: 50MB limit (higher)
**Option C**: No limit (unsafe for large files)

**Your choice**: _______________

---

### DECISION 6: CDATA Handling

For content with `<` and `>` characters:

**Option A**: Require `<![CDATA[...]]>` for XML-unsafe content
**Option B**: Auto-detect and handle (more complex parsing)
**Option C**: Escape `<` as `&lt;` and `>` as `&gt;`

**Your choice**: _______________

---

## 13. Estimated Implementation

**Total Complexity**: Medium-High
**Estimated Time**: 6-10 hours
**Files Modified**: 5-8 files
**Risk Level**: Low-Medium (new feature, isolated from existing tools)

**Breakdown**:
- Phase 1 (Edit): 2 hours
- Phase 2 (Create/Delete): 1.5 hours
- Phase 3 (Move/Copy): 1.5 hours
- Phase 4 (Append/Insert): 2 hours
- Phase 5 (Directories): 1 hour
- Phase 6 (Safety/Config): 1.5 hours
- Phase 7 (Testing): 3 hours
- Phase 8 (Documentation): 1.5 hours

---

**END OF SPEC - READY FOR IMPLEMENTATION**

Please review and mark your decisions in Section 12!
