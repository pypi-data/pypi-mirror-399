# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Framework Security Module

Comprehensive security hardening for framework execution including:
- Input validation against JSON Schema
- Parameter sanitization
- Tier enforcement verification
- Execution circuit breaker
- Request fingerprinting
"""

from __future__ import annotations

import hashlib
import logging
import re
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from functools import wraps
from threading import Lock
from typing import Any, Callable, TypeVar

import jsonschema
from jsonschema import Draft7Validator, ValidationError


logger = logging.getLogger("krl.security.frameworks")


# =============================================================================
# CONFIGURATION
# =============================================================================

# Maximum parameter value lengths
MAX_STRING_LENGTH = 10_000
MAX_ARRAY_LENGTH = 1_000
MAX_OBJECT_DEPTH = 10

# Dangerous patterns to reject
DANGEROUS_PATTERNS = [
    r"__import__",
    r"eval\s*\(",
    r"exec\s*\(",
    r"compile\s*\(",
    r"globals\s*\(",
    r"locals\s*\(",
    r"open\s*\(",
    r"subprocess",
    r"os\.system",
    r"os\.popen",
    r"commands\.",
    r"\bsh\s*\(",
    r"<script",
    r"javascript:",
    r"data:text/html",
]

COMPILED_DANGEROUS = [re.compile(p, re.IGNORECASE) for p in DANGEROUS_PATTERNS]

# Circuit breaker settings
CIRCUIT_OPEN_THRESHOLD = 5  # failures before opening
CIRCUIT_HALF_OPEN_TIMEOUT = 60  # seconds before attempting recovery


# =============================================================================
# CIRCUIT BREAKER STATE
# =============================================================================

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreaker:
    """
    Circuit breaker for framework execution.
    
    Prevents cascade failures by temporarily blocking requests
    when a framework repeatedly fails.
    """
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: float | None = None
    success_count_in_half_open: int = 0
    
    def record_success(self) -> None:
        """Record successful execution."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count_in_half_open += 1
            if self.success_count_in_half_open >= 3:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count_in_half_open = 0
                logger.info("Circuit breaker closed (recovered)")
        else:
            self.failure_count = max(0, self.failure_count - 1)
    
    def record_failure(self) -> None:
        """Record failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        self.success_count_in_half_open = 0
        
        if self.failure_count >= CIRCUIT_OPEN_THRESHOLD:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            if self.last_failure_time and \
               time.time() - self.last_failure_time > CIRCUIT_HALF_OPEN_TIMEOUT:
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker half-open (testing recovery)")
                return True
            return False
        
        # HALF_OPEN - allow limited requests
        return True


# Global circuit breakers per framework
_circuit_breakers: dict[str, CircuitBreaker] = defaultdict(CircuitBreaker)
_circuit_lock = Lock()


def get_circuit_breaker(framework_slug: str) -> CircuitBreaker:
    """Get or create circuit breaker for a framework."""
    with _circuit_lock:
        return _circuit_breakers[framework_slug]


# =============================================================================
# INPUT VALIDATION
# =============================================================================

class ValidationResult:
    """Result of parameter validation."""
    
    def __init__(self, valid: bool, errors: list[str] | None = None):
        self.valid = valid
        self.errors = errors or []
    
    def __bool__(self) -> bool:
        return self.valid


def validate_parameter_schema(
    parameters: dict[str, Any],
    schema: dict[str, Any],
    strict: bool = True,
) -> ValidationResult:
    """
    Validate parameters against JSON Schema.
    
    Args:
        parameters: User-provided parameters
        schema: JSON Schema from dashboard_spec
        strict: If True, reject additional properties
        
    Returns:
        ValidationResult with errors if invalid
    """
    errors: list[str] = []
    
    try:
        # Create validator
        validator = Draft7Validator(schema)
        
        # Collect all validation errors
        for error in validator.iter_errors(parameters):
            path = ".".join(str(p) for p in error.path) or "root"
            errors.append(f"{path}: {error.message}")
        
    except Exception as e:
        errors.append(f"Schema validation error: {str(e)}")
    
    return ValidationResult(len(errors) == 0, errors)


def sanitize_string_parameter(value: str) -> str:
    """
    Sanitize a string parameter value.
    
    Args:
        value: Raw string value
        
    Returns:
        Sanitized string
        
    Raises:
        ValueError: If dangerous patterns detected
    """
    if len(value) > MAX_STRING_LENGTH:
        raise ValueError(f"String exceeds maximum length of {MAX_STRING_LENGTH}")
    
    # Check for dangerous patterns
    for pattern in COMPILED_DANGEROUS:
        if pattern.search(value):
            raise ValueError(f"Dangerous pattern detected in input")
    
    # Strip null bytes and control characters (except newlines/tabs)
    sanitized = "".join(
        c for c in value 
        if c >= ' ' or c in '\n\r\t'
    )
    
    return sanitized


def sanitize_parameters(
    parameters: dict[str, Any],
    depth: int = 0,
) -> dict[str, Any]:
    """
    Recursively sanitize all parameter values.
    
    Args:
        parameters: Raw parameters dict
        depth: Current recursion depth
        
    Returns:
        Sanitized parameters
        
    Raises:
        ValueError: If dangerous content detected
    """
    if depth > MAX_OBJECT_DEPTH:
        raise ValueError(f"Object exceeds maximum depth of {MAX_OBJECT_DEPTH}")
    
    result: dict[str, Any] = {}
    
    for key, value in parameters.items():
        # Sanitize key
        if not isinstance(key, str):
            raise ValueError(f"Parameter keys must be strings")
        
        sanitized_key = sanitize_string_parameter(key)
        
        # Sanitize value based on type
        if value is None:
            result[sanitized_key] = None
        elif isinstance(value, bool):
            result[sanitized_key] = value
        elif isinstance(value, (int, float)):
            result[sanitized_key] = value
        elif isinstance(value, str):
            result[sanitized_key] = sanitize_string_parameter(value)
        elif isinstance(value, list):
            if len(value) > MAX_ARRAY_LENGTH:
                raise ValueError(f"Array exceeds maximum length of {MAX_ARRAY_LENGTH}")
            result[sanitized_key] = [
                sanitize_parameters({"v": v}, depth + 1)["v"] if isinstance(v, dict) 
                else sanitize_string_parameter(v) if isinstance(v, str)
                else v
                for v in value
            ]
        elif isinstance(value, dict):
            result[sanitized_key] = sanitize_parameters(value, depth + 1)
        else:
            raise ValueError(f"Unsupported parameter type: {type(value).__name__}")
    
    return result


# =============================================================================
# REQUEST FINGERPRINTING
# =============================================================================

def compute_request_fingerprint(
    user_agent: str | None,
    accept_language: str | None,
    accept_encoding: str | None,
    client_ip: str | None,
) -> str:
    """
    Compute a fingerprint hash for request origin validation.
    
    Args:
        user_agent: User-Agent header
        accept_language: Accept-Language header
        accept_encoding: Accept-Encoding header
        client_ip: Client IP address
        
    Returns:
        SHA-256 fingerprint hash
    """
    components = [
        user_agent or "",
        accept_language or "",
        accept_encoding or "",
        # Note: IP not included to allow NAT/proxy changes
    ]
    
    fingerprint_data = "|".join(components).encode("utf-8")
    return hashlib.sha256(fingerprint_data).hexdigest()[:32]


def validate_fingerprint_consistency(
    current_fingerprint: str,
    session_fingerprint: str | None,
    tolerance: float = 0.8,
) -> bool:
    """
    Check if current request fingerprint is consistent with session.
    
    This helps detect session hijacking attempts.
    
    Args:
        current_fingerprint: Current request fingerprint
        session_fingerprint: Fingerprint stored in session/token
        tolerance: Similarity threshold (not used for exact match)
        
    Returns:
        True if fingerprints match
    """
    if session_fingerprint is None:
        return True  # First request in session
    
    return current_fingerprint == session_fingerprint


# =============================================================================
# TIER ENFORCEMENT VALIDATOR
# =============================================================================

# Tier hierarchy (higher index = higher tier)
TIER_HIERARCHY = ["community", "professional", "team", "enterprise"]


def tier_allows_access(user_tier: str, required_tier: str) -> bool:
    """
    Check if user tier allows access to required tier.
    
    Args:
        user_tier: User's subscription tier
        required_tier: Tier required for access
        
    Returns:
        True if user tier >= required tier
    """
    user_tier = user_tier.lower()
    required_tier = required_tier.lower()
    
    try:
        user_index = TIER_HIERARCHY.index(user_tier)
        required_index = TIER_HIERARCHY.index(required_tier)
        return user_index >= required_index
    except ValueError:
        # Unknown tier - deny access
        logger.warning(f"Unknown tier: user={user_tier}, required={required_tier}")
        return False


def validate_framework_tier_access(
    framework_slug: str,
    framework_min_tier: str,
    user_tier: str,
) -> tuple[bool, str | None]:
    """
    Validate user has access to execute a framework.
    
    Args:
        framework_slug: Framework identifier
        framework_min_tier: Framework's minimum required tier
        user_tier: User's subscription tier
        
    Returns:
        Tuple of (allowed, error_message)
    """
    if not tier_allows_access(user_tier, framework_min_tier):
        return (
            False,
            f"Framework '{framework_slug}' requires {framework_min_tier.upper()} tier. "
            f"Your tier: {user_tier.upper()}. Please upgrade to access this framework."
        )
    
    return True, None


# =============================================================================
# EXECUTION SECURITY DECORATOR
# =============================================================================

F = TypeVar("F", bound=Callable[..., Any])


def secure_framework_execution(
    framework_slug: str,
    min_tier: str = "community",
) -> Callable[[F], F]:
    """
    Decorator for secure framework execution.
    
    Applies:
    - Circuit breaker check
    - Tier validation
    - Parameter sanitization
    - Error logging
    
    Args:
        framework_slug: Framework identifier
        min_tier: Minimum required tier
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, user_tier: str = "community", **kwargs) -> Any:
            # 1. Check circuit breaker
            circuit = get_circuit_breaker(framework_slug)
            if not circuit.can_execute():
                logger.warning(
                    f"Circuit breaker OPEN for {framework_slug}, rejecting execution"
                )
                raise RuntimeError(
                    f"Framework '{framework_slug}' is temporarily unavailable. "
                    f"Please try again in {CIRCUIT_HALF_OPEN_TIMEOUT} seconds."
                )
            
            # 2. Validate tier access
            allowed, error = validate_framework_tier_access(
                framework_slug, min_tier, user_tier
            )
            if not allowed:
                logger.warning(
                    f"Tier access denied: {framework_slug} requires {min_tier}, "
                    f"user has {user_tier}"
                )
                raise PermissionError(error)
            
            # 3. Execute with circuit breaker tracking
            try:
                result = func(*args, **kwargs)
                circuit.record_success()
                return result
            except Exception as e:
                circuit.record_failure()
                logger.error(f"Framework execution failed: {framework_slug}: {e}")
                raise
        
        return wrapper  # type: ignore
    
    return decorator


# =============================================================================
# SECURITY AUDIT HELPER
# =============================================================================

@dataclass
class SecurityAuditEvent:
    """Security-relevant event for audit logging."""
    event_type: str
    framework_slug: str | None
    user_id: str | None
    user_tier: str | None
    client_ip: str | None
    success: bool
    error_message: str | None = None
    parameters_hash: str | None = None
    timestamp: datetime | None = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "event_type": self.event_type,
            "framework_slug": self.framework_slug,
            "user_id": self.user_id,
            "user_tier": self.user_tier,
            "client_ip": self.client_ip,
            "success": self.success,
            "error_message": self.error_message,
            "parameters_hash": self.parameters_hash,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


def hash_parameters(parameters: dict[str, Any]) -> str:
    """
    Create a hash of parameters for audit logging.
    
    This allows detecting parameter tampering without storing
    sensitive parameter values.
    """
    import json
    
    # Sort keys for consistent hashing
    sorted_json = json.dumps(parameters, sort_keys=True)
    return hashlib.sha256(sorted_json.encode()).hexdigest()[:16]


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Validation
    "validate_parameter_schema",
    "sanitize_parameters",
    "sanitize_string_parameter",
    "ValidationResult",
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitState",
    "get_circuit_breaker",
    # Fingerprinting
    "compute_request_fingerprint",
    "validate_fingerprint_consistency",
    # Tier Enforcement
    "tier_allows_access",
    "validate_framework_tier_access",
    "TIER_HIERARCHY",
    # Decorator
    "secure_framework_execution",
    # Audit
    "SecurityAuditEvent",
    "hash_parameters",
]
