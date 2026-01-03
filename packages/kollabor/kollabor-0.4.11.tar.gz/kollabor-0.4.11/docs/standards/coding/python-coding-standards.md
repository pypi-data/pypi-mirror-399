# Python Coding Standards

## Document Information
- **Version**: 1.0
- **Date**: 2025-09-09
- **Status**: Active

## 1. Code Style and Formatting

### 1.1 PEP 8 Compliance
All Python code must follow PEP 8 guidelines with the following project-specific modifications:

- **Line Length**: 88 characters (Black formatter default)
- **Indentation**: 4 spaces (no tabs)
- **Quote Style**: Double quotes for strings, single quotes for character literals

### 1.2 Import Organization
```python
# Standard library imports
import os
import sys
from typing import Dict, List, Optional

# Third-party imports
import aiohttp
import asyncio

# Local application imports
from core.events import EventBus
from core.config import ConfigManager
```

### 1.3 Function and Class Definitions
```python
class ExampleClass:
    """Brief class description.
    
    Detailed class description if needed.
    
    Attributes:
        attribute_name: Description of attribute
    """
    
    def __init__(self, param: str, optional_param: Optional[int] = None):
        self.attribute_name = param
        self._private_attribute = optional_param
    
    async def async_method(self) -> Dict[str, Any]:
        """Brief method description.
        
        Returns:
            Dictionary containing result data
        """
        return {}
```

## 2. Naming Conventions

### 2.1 Variables and Functions
- Use `snake_case` for variables and functions
- Use descriptive names that indicate purpose
- Avoid single-character names except for counters in short loops

```python
# Good
user_count = 0
def calculate_total_price():
    pass

# Avoid
c = 0
def calc():
    pass
```

### 2.2 Classes
- Use `PascalCase` for class names
- Use descriptive names that indicate the class purpose

```python
class UserManager:
    pass

class DatabaseConnection:
    pass
```

### 2.3 Constants
- Use `SCREAMING_SNAKE_CASE` for constants
- Define at module level

```python
DEFAULT_TIMEOUT = 30
MAX_RETRY_ATTEMPTS = 3
API_BASE_URL = "https://api.example.com"
```

### 2.4 Private Members
- Use single leading underscore for internal use
- Use double leading underscore for name mangling when necessary

```python
class Example:
    def __init__(self):
        self.public_attribute = "visible"
        self._internal_attribute = "internal use"
        self.__private_attribute = "name mangled"
```

## 3. Type Hints

### 3.1 Required Type Hints
All function signatures must include type hints:

```python
from typing import Dict, List, Optional, Union, Any

def process_data(
    input_data: List[Dict[str, Any]], 
    timeout: Optional[float] = None
) -> Dict[str, Union[str, int]]:
    """Process input data and return results."""
    return {}
```

### 3.2 Complex Types
Use typing module for complex type definitions:

```python
from typing import TypedDict, Protocol, Callable

class UserData(TypedDict):
    name: str
    age: int
    email: Optional[str]

class Processor(Protocol):
    def process(self, data: str) -> str:
        ...

EventHandler = Callable[[str], None]
```

## 4. Documentation Standards

### 4.1 Docstrings
Use Google-style docstrings for all public functions and classes:

```python
def calculate_metrics(data: List[Dict], weights: Optional[Dict] = None) -> Dict:
    """Calculate weighted metrics from input data.
    
    This function processes a list of data dictionaries and applies
    optional weights to calculate various metrics.
    
    Args:
        data: List of dictionaries containing metric data
        weights: Optional dictionary of weights for different metrics
        
    Returns:
        Dictionary containing calculated metrics with keys:
        - 'total': Total weighted sum
        - 'average': Weighted average
        - 'count': Number of data points processed
        
    Raises:
        ValueError: If data is empty or contains invalid values
        TypeError: If data structure is incorrect
        
    Example:
        >>> data = [{'value': 10, 'type': 'A'}, {'value': 20, 'type': 'B'}]
        >>> weights = {'A': 1.0, 'B': 2.0}
        >>> result = calculate_metrics(data, weights)
        >>> print(result['total'])
        50.0
    """
    pass
```

### 4.2 Inline Comments
- Use comments sparingly for complex logic
- Explain why, not what
- Keep comments up to date with code changes

```python
# Calculate exponential backoff delay to prevent API rate limiting
delay = min(base_delay * (2 ** attempt), max_delay)
```

## 5. Error Handling

### 5.1 Exception Handling
```python
import logging

logger = logging.getLogger(__name__)

async def fetch_data(url: str) -> Optional[Dict]:
    """Fetch data from URL with proper error handling."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
    except aiohttp.ClientError as e:
        logger.error(f"HTTP client error fetching {url}: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error fetching {url}: {e}")
        return None
```

### 5.2 Custom Exceptions
```python
class ChatAppError(Exception):
    """Base exception for chat application."""
    pass

class ConfigurationError(ChatAppError):
    """Raised when configuration is invalid."""
    pass

class PluginLoadError(ChatAppError):
    """Raised when plugin fails to load."""
    
    def __init__(self, plugin_name: str, reason: str):
        self.plugin_name = plugin_name
        self.reason = reason
        super().__init__(f"Failed to load plugin '{plugin_name}': {reason}")
```

## 6. Async Programming

### 6.1 Async Best Practices
```python
import asyncio
from typing import List

async def process_items_concurrently(items: List[str]) -> List[str]:
    """Process multiple items concurrently."""
    tasks = [process_single_item(item) for item in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle exceptions in results
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Failed to process item {items[i]}: {result}")
        else:
            processed_results.append(result)
    
    return processed_results

async def process_single_item(item: str) -> str:
    """Process a single item asynchronously."""
    await asyncio.sleep(0.1)  # Simulate async work
    return f"processed_{item}"
```

### 6.2 Context Managers
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def database_transaction():
    """Async context manager for database transactions."""
    transaction = await db.begin_transaction()
    try:
        yield transaction
        await transaction.commit()
    except Exception:
        await transaction.rollback()
        raise
    finally:
        await transaction.close()

# Usage
async def update_user(user_id: int, data: Dict):
    async with database_transaction() as tx:
        await tx.execute("UPDATE users SET ... WHERE id = ?", user_id)
```

## 7. Testing Standards

### 7.1 Test Structure
```python
import unittest
from unittest.mock import Mock, patch, AsyncMock
import asyncio

class TestUserManager(unittest.TestCase):
    """Test cases for UserManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user_manager = UserManager()
        self.mock_db = Mock()
    
    def test_create_user_valid_data(self):
        """Test user creation with valid data."""
        user_data = {"name": "John Doe", "email": "john@example.com"}
        result = self.user_manager.create_user(user_data)
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "John Doe")
    
    @patch('module.external_api_call')
    async def test_async_operation(self, mock_api):
        """Test async operation with mocked external call."""
        mock_api.return_value = {"status": "success"}
        result = await self.user_manager.async_operation()
        self.assertEqual(result["status"], "success")
        mock_api.assert_called_once()
```

### 7.2 Test Naming
- Test methods should start with `test_`
- Use descriptive names that explain what is being tested
- Format: `test_[method_name]_[condition]_[expected_result]`

## 8. Configuration and Environment

### 8.1 Configuration Management
```python
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class AppConfig:
    """Application configuration settings."""
    api_url: str
    timeout: float
    debug: bool
    max_connections: int
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create configuration from environment variables."""
        return cls(
            api_url=os.getenv('API_URL', 'http://localhost:8000'),
            timeout=float(os.getenv('TIMEOUT', '30.0')),
            debug=os.getenv('DEBUG', 'false').lower() == 'true',
            max_connections=int(os.getenv('MAX_CONNECTIONS', '10'))
        )
```

## 9. Logging Standards

### 9.1 Logging Setup
```python
import logging
import sys
from typing import Optional

def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None
) -> None:
    """Set up application logging."""
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

# Usage
logger = logging.getLogger(__name__)
logger.info("Application started")
logger.error("Error occurred: %s", error_message)
```

## 10. Performance Guidelines

### 10.1 General Performance Tips
- Use list comprehensions for simple transformations
- Avoid unnecessary string concatenation in loops
- Use appropriate data structures (set for membership testing, dict for lookups)
- Profile code before optimizing

```python
# Good - List comprehension
squared_numbers = [x**2 for x in numbers if x > 0]

# Avoid - Loop with append
squared_numbers = []
for x in numbers:
    if x > 0:
        squared_numbers.append(x**2)

# Good - Use set for membership testing
valid_ids = {1, 2, 3, 4, 5}
if user_id in valid_ids:
    process_user(user_id)
```

## 11. Code Review Checklist

### 11.1 Before Submitting
- [ ] Code follows PEP 8 and project style guidelines
- [ ] All functions have type hints and docstrings
- [ ] Tests are written and passing
- [ ] No hardcoded values or credentials
- [ ] Error handling is appropriate
- [ ] Logging is used appropriately
- [ ] Code is readable and well-documented
- [ ] Performance considerations addressed

### 11.2 Security Considerations
- [ ] No secrets in code
- [ ] Input validation implemented
- [ ] SQL injection prevention
- [ ] Proper error message handling (no sensitive info leakage)
- [ ] Authentication and authorization checks

## 12. Enforcement

### 12.1 Automated Checks
These standards are enforced through:
- Pre-commit hooks
- CI/CD pipeline checks
- Code review requirements

### 12.2 Tools
- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **flake8**: Style and error checking
- **pytest**: Testing framework