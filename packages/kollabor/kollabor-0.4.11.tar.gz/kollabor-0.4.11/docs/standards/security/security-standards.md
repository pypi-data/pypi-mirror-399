# Security Standards

## Document Information
- **Version**: 1.0
- **Date**: 2025-09-09
- **Status**: Active
- **Classification**: Internal

## 1. Security Principles

### 1.1 Core Security Principles
- **Defense in Depth**: Multiple layers of security controls
- **Principle of Least Privilege**: Minimum necessary access rights
- **Fail Secure**: Systems fail to a secure state
- **Zero Trust**: Never trust, always verify
- **Security by Design**: Security built-in from the start

### 1.2 Threat Model
Our applications face these primary threats:
- Injection attacks (SQL, Command, Code)
- Authentication and session management flaws
- Cross-site scripting (XSS)
- Insecure direct object references
- Security misconfiguration
- Sensitive data exposure
- Insufficient logging and monitoring

## 2. Authentication and Authorization

### 2.1 Authentication Requirements
#### Password Policy
- Minimum 12 characters length
- Must contain uppercase, lowercase, numbers, and special characters
- No common passwords or dictionary words
- Password history of 24 passwords
- Account lockout after 5 failed attempts

#### Multi-Factor Authentication (MFA)
- Required for all administrative accounts
- Recommended for all user accounts
- Support for TOTP, SMS, and hardware tokens

#### Session Management
```python
import secrets
import hashlib
from datetime import datetime, timedelta

class SecureSession:
    def __init__(self):
        self.session_timeout = timedelta(hours=8)
        self.idle_timeout = timedelta(minutes=30)
    
    def generate_session_token(self) -> str:
        """Generate cryptographically secure session token."""
        return secrets.token_urlsafe(32)
    
    def hash_password(self, password: str, salt: bytes = None) -> tuple:
        """Hash password using PBKDF2 with salt."""
        if salt is None:
            salt = secrets.token_bytes(32)
        
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000  # iterations
        )
        return key, salt
```

### 2.2 Authorization Model
#### Role-Based Access Control (RBAC)
```python
from enum import Enum
from typing import Set, Dict

class Permission(Enum):
    READ_USER = "user:read"
    WRITE_USER = "user:write"
    DELETE_USER = "user:delete"
    ADMIN_ACCESS = "admin:access"
    SYSTEM_CONFIG = "system:config"

class Role:
    def __init__(self, name: str, permissions: Set[Permission]):
        self.name = name
        self.permissions = permissions

# Define roles
ROLES: Dict[str, Role] = {
    "user": Role("user", {Permission.READ_USER}),
    "moderator": Role("moderator", {Permission.READ_USER, Permission.WRITE_USER}),
    "admin": Role("admin", {Permission.READ_USER, Permission.WRITE_USER, 
                           Permission.DELETE_USER, Permission.ADMIN_ACCESS}),
    "system_admin": Role("system_admin", set(Permission))
}
```

## 3. Data Protection

### 3.1 Data Classification
| Classification | Description | Examples | Requirements |
|----------------|-------------|----------|--------------|
| Public | Can be freely shared | Marketing materials | None |
| Internal | Internal use only | Employee directories | Access controls |
| Confidential | Sensitive business data | Financial reports | Encryption + logging |
| Restricted | Highly sensitive | PII, credentials | Strong encryption + audit |

### 3.2 Encryption Standards
#### Encryption at Rest
- **Algorithm**: AES-256-GCM
- **Key Management**: Hardware Security Module (HSM) or Key Management Service
- **Database**: Transparent Data Encryption (TDE)
- **Files**: Full disk encryption

```python
from cryptography.fernet import Fernet
import base64
import os

class DataEncryption:
    def __init__(self, key: bytes = None):
        if key is None:
            key = Fernet.generate_key()
        self.cipher = Fernet(key)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data for storage."""
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data from storage."""
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted_data = self.cipher.decrypt(encrypted_bytes)
        return decrypted_data.decode()
```

#### Encryption in Transit
- **TLS Version**: TLS 1.2 minimum, TLS 1.3 preferred
- **Cipher Suites**: AEAD ciphers only (AES-GCM, ChaCha20-Poly1305)
- **Certificate Validation**: Always verify certificates
- **HSTS**: HTTP Strict Transport Security enabled

### 3.3 PII Handling
#### Data Minimization
- Collect only necessary PII
- Implement data retention policies
- Secure deletion after retention period

#### PII Processing
```python
import hashlib
import re
from typing import Optional

class PIIProcessor:
    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email for logging."""
        if '@' not in email:
            return '***'
        local, domain = email.split('@')
        return f"{local[0]}***@{domain}"
    
    @staticmethod
    def mask_credit_card(cc_number: str) -> str:
        """Mask credit card number."""
        cc_clean = re.sub(r'\D', '', cc_number)
        if len(cc_clean) < 8:
            return '****'
        return f"****-****-****-{cc_clean[-4:]}"
    
    @staticmethod
    def hash_pii(data: str) -> str:
        """Hash PII for analytics (irreversible)."""
        return hashlib.sha256(data.encode()).hexdigest()
```

## 4. Input Validation and Sanitization

### 4.1 Input Validation Framework
```python
import re
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ValidationRule:
    field_name: str
    required: bool = True
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    allowed_values: Optional[List[str]] = None

class InputValidator:
    def __init__(self):
        self.rules: Dict[str, ValidationRule] = {}
    
    def add_rule(self, rule: ValidationRule):
        """Add validation rule for a field."""
        self.rules[rule.field_name] = rule
    
    def validate(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate input data against rules."""
        errors = []
        
        for field_name, rule in self.rules.items():
            value = data.get(field_name)
            
            # Required field check
            if rule.required and (value is None or value == ''):
                errors.append(f"{field_name} is required")
                continue
            
            if value is None:
                continue
                
            # String validations
            if isinstance(value, str):
                if rule.min_length and len(value) < rule.min_length:
                    errors.append(f"{field_name} must be at least {rule.min_length} characters")
                
                if rule.max_length and len(value) > rule.max_length:
                    errors.append(f"{field_name} must not exceed {rule.max_length} characters")
                
                if rule.pattern and not re.match(rule.pattern, value):
                    errors.append(f"{field_name} format is invalid")
                
                if rule.allowed_values and value not in rule.allowed_values:
                    errors.append(f"{field_name} must be one of: {', '.join(rule.allowed_values)}")
        
        return len(errors) == 0, errors

# Common validation patterns
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PHONE_PATTERN = r'^\+?1?[0-9]{10,15}$'
UUID_PATTERN = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
```

### 4.2 SQL Injection Prevention
```python
import sqlite3
from typing import Any, List, Optional

class SecureDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def execute_query(self, query: str, params: tuple = ()) -> Optional[List[tuple]]:
        """Execute query with parameterized statements."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                conn.commit()
                return None
        except sqlite3.Error as e:
            # Log error without exposing sensitive information
            logger.error(f"Database error: {type(e).__name__}")
            raise
    
    def get_user_by_id(self, user_id: int) -> Optional[tuple]:
        """Safe user lookup with parameterized query."""
        query = "SELECT id, username, email FROM users WHERE id = ?"
        result = self.execute_query(query, (user_id,))
        return result[0] if result else None
```

## 5. API Security

### 5.1 API Authentication
```python
import jwt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class APIAuthentication:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = 'HS256'
        self.token_expiry = timedelta(hours=1)
    
    def generate_api_key(self) -> str:
        """Generate secure API key."""
        return secrets.token_urlsafe(32)
    
    def create_jwt_token(self, user_id: str, permissions: List[str]) -> str:
        """Create JWT token with claims."""
        payload = {
            'user_id': user_id,
            'permissions': permissions,
            'exp': datetime.utcnow() + self.token_expiry,
            'iat': datetime.utcnow(),
            'jti': secrets.token_urlsafe(16)  # JWT ID for revocation
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def validate_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate and decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
```

### 5.2 Rate Limiting
```python
import time
from collections import defaultdict, deque
from typing import Dict, Deque

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, Deque[float]] = defaultdict(deque)
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed under rate limit."""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        request_times = self.requests[identifier]
        while request_times and request_times[0] < minute_ago:
            request_times.popleft()
        
        # Check if under limit
        if len(request_times) < self.requests_per_minute:
            request_times.append(now)
            return True
        
        return False
```

## 6. Logging and Monitoring

### 6.1 Security Logging Standards
```python
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any

class SecurityLogger:
    def __init__(self, logger_name: str = "security"):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
        
        # Structured logging format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_security_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: str = "INFO"
    ):
        """Log security-related events."""
        event_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "details": details or {},
            "severity": severity
        }
        
        log_message = json.dumps(event_data)
        
        if severity == "CRITICAL":
            self.logger.critical(log_message)
        elif severity == "ERROR":
            self.logger.error(log_message)
        elif severity == "WARNING":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def log_authentication_failure(self, username: str, ip_address: str):
        """Log authentication failure."""
        self.log_security_event(
            event_type="AUTH_FAILURE",
            user_id=username,
            ip_address=ip_address,
            details={"reason": "invalid_credentials"},
            severity="WARNING"
        )
    
    def log_privilege_escalation_attempt(self, user_id: str, resource: str):
        """Log privilege escalation attempt."""
        self.log_security_event(
            event_type="PRIVILEGE_ESCALATION",
            user_id=user_id,
            details={"resource": resource},
            severity="CRITICAL"
        )
```

### 6.2 Security Events to Monitor
- Authentication failures
- Authorization failures
- Privilege escalation attempts
- Data access anomalies
- Configuration changes
- System errors and exceptions
- Network connection attempts
- File system changes

## 7. Incident Response

### 7.1 Security Incident Categories
| Severity | Definition | Response Time | Escalation |
|----------|------------|---------------|------------|
| Critical | System compromise, data breach | Immediate | CISO, Executive team |
| High | Service disruption, failed attacks | 1 hour | Security team lead |
| Medium | Policy violations, suspicious activity | 4 hours | Security analyst |
| Low | Informational events | 24 hours | Documentation only |

### 7.2 Incident Response Process
1. **Detection**: Identify security incident
2. **Analysis**: Assess scope and impact
3. **Containment**: Limit damage and exposure
4. **Eradication**: Remove threat from environment
5. **Recovery**: Restore services and monitoring
6. **Lessons Learned**: Document and improve

## 8. Secure Development Lifecycle

### 8.1 Security Gates
#### Requirements Phase
- [ ] Security requirements defined
- [ ] Threat model completed
- [ ] Privacy impact assessment

#### Design Phase
- [ ] Security architecture review
- [ ] Data flow diagrams created
- [ ] Security controls designed

#### Development Phase
- [ ] Secure coding standards followed
- [ ] Static analysis tools run
- [ ] Code review completed

#### Testing Phase
- [ ] Security testing performed
- [ ] Penetration testing completed
- [ ] Vulnerability assessment done

#### Deployment Phase
- [ ] Security configuration verified
- [ ] Access controls validated
- [ ] Monitoring implemented

## 9. Third-Party Security

### 9.1 Vendor Security Assessment
- Security questionnaire completion
- SOC 2 Type II certification
- Penetration testing results
- Data processing agreements
- Incident response procedures

### 9.2 Dependency Management
```python
import hashlib
import requests
from typing import List, Dict

class DependencySecurityChecker:
    def __init__(self):
        self.known_vulnerabilities = {}  # Load from security database
    
    def check_package_integrity(self, package_name: str, expected_hash: str) -> bool:
        """Verify package integrity using hash."""
        # Download package and verify hash
        # Implementation depends on package manager
        pass
    
    def scan_vulnerabilities(self, dependencies: List[str]) -> Dict[str, List[str]]:
        """Scan dependencies for known vulnerabilities."""
        vulnerabilities = {}
        for dep in dependencies:
            if dep in self.known_vulnerabilities:
                vulnerabilities[dep] = self.known_vulnerabilities[dep]
        return vulnerabilities
```

## 10. Compliance Requirements

### 10.1 Data Protection Regulations
- **GDPR**: EU General Data Protection Regulation
- **CCPA**: California Consumer Privacy Act
- **HIPAA**: Health Insurance Portability and Accountability Act
- **SOX**: Sarbanes-Oxley Act

### 10.2 Security Frameworks
- **NIST Cybersecurity Framework**
- **ISO 27001/27002**
- **OWASP Top 10**
- **CIS Controls**

## 11. Security Training and Awareness

### 11.1 Required Training
- Security awareness training (annual)
- Secure coding practices (developers)
- Incident response procedures (IT staff)
- Privacy and data protection (all staff)

### 11.2 Security Communication
- Monthly security bulletins
- Quarterly security metrics
- Annual security assessment
- Incident notifications

## 12. Enforcement and Compliance

### 12.1 Security Metrics
- Mean time to detect (MTTD)
- Mean time to respond (MTTR)
- Number of security incidents
- Vulnerability remediation time
- Security training completion rates

### 12.2 Audit and Review
- Quarterly security reviews
- Annual penetration testing
- Continuous vulnerability scanning
- Regular access reviews
- Policy updates and approvals

This security standards document must be reviewed annually and updated as needed to address new threats and technologies.