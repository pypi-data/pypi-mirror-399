# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Execution Context
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Execution Context for Framework Runtime.

This module defines the ExecutionContext that governs runtime behavior.
The critical distinction is between LIVE and TEST modes:

- LIVE mode: Real connectors, real data, fail-fast on missing dependencies
- TEST mode: Synthetic data allowed, graceful degradation permitted

Design Principles:
    1. No silent fallbacks in LIVE mode
    2. Missing dependencies cause hard failures
    3. Context is explicit, not inferred
    4. All execution decisions are auditable
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Iterator
import uuid

if TYPE_CHECKING:
    from krl_frameworks.core.bindings import BindingRegistry
    from krl_frameworks.core.capabilities import CapabilityDeclaration

__all__ = [
    "ExecutionMode",
    "ExecutionContext",
    "get_execution_context",
    "set_execution_context",
    "execution_context",
    "MissingCapabilityError",
    "ExecutionModeViolationError",
]


class ExecutionMode(str, Enum):
    """
    Execution mode for framework runtime.
    
    LIVE: Production execution with real data and strict validation.
    TEST: Testing execution with synthetic data permitted.
    DEBUG: Development mode with verbose logging and relaxed validation.
    """
    LIVE = "live"
    TEST = "test"
    DEBUG = "debug"
    
    @classmethod
    def from_env(cls) -> "ExecutionMode":
        """
        Get execution mode from environment variable.
        
        Reads EXECUTION_MODE env var, defaults to TEST for safety.
        """
        mode_str = os.getenv("EXECUTION_MODE", "test").lower()
        try:
            return cls(mode_str)
        except ValueError:
            return cls.TEST
    
    @property
    def allows_synthetic_data(self) -> bool:
        """Whether synthetic/mock data is permitted."""
        return self in (ExecutionMode.TEST, ExecutionMode.DEBUG)
    
    @property
    def allows_fallbacks(self) -> bool:
        """Whether graceful degradation is permitted."""
        return self in (ExecutionMode.TEST, ExecutionMode.DEBUG)
    
    @property
    def requires_strict_validation(self) -> bool:
        """Whether all capabilities must be validated."""
        return self == ExecutionMode.LIVE


class MissingCapabilityError(Exception):
    """
    Raised when a required capability is not available.
    
    This is a hard failure - execution cannot proceed.
    """
    
    def __init__(
        self,
        capability_type: str,
        capability_name: str,
        message: str = "",
    ) -> None:
        self.capability_type = capability_type
        self.capability_name = capability_name
        super().__init__(
            message or f"Missing required {capability_type}: {capability_name}"
        )


class ExecutionModeViolationError(Exception):
    """
    Raised when an operation violates the current execution mode.
    
    For example, using mock data in LIVE mode.
    """
    
    def __init__(
        self,
        operation: str,
        current_mode: ExecutionMode,
        required_mode: ExecutionMode | None = None,
    ) -> None:
        self.operation = operation
        self.current_mode = current_mode
        self.required_mode = required_mode
        
        if required_mode:
            message = (
                f"Operation '{operation}' requires {required_mode.value} mode "
                f"but current mode is {current_mode.value}"
            )
        else:
            message = (
                f"Operation '{operation}' is not permitted in {current_mode.value} mode"
            )
        super().__init__(message)


@dataclass
class ExecutionContext:
    """
    Runtime execution context for framework execution.
    
    The context carries:
    - Execution mode (LIVE/TEST/DEBUG)
    - User tier for access control
    - Binding registry with resolved dependencies
    - Execution metadata for audit logging
    
    All framework executions must occur within an ExecutionContext.
    The context enforces mode-specific constraints.
    
    Example:
        >>> with execution_context(ExecutionMode.LIVE, user_tier="professional") as ctx:
        ...     result = framework.fit(data_bundle)
        ...     # All operations validated against LIVE mode constraints
    
    Example (environment-based):
        >>> # Set EXECUTION_MODE=live in environment
        >>> ctx = ExecutionContext.from_env()
        >>> ctx.validate_capabilities(framework.CAPABILITIES)
    """
    mode: ExecutionMode = field(default_factory=ExecutionMode.from_env)
    user_tier: str = "community"
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    bindings: "BindingRegistry | None" = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    # Audit trail
    _validation_errors: list[str] = field(default_factory=list, repr=False)
    _warnings: list[str] = field(default_factory=list, repr=False)
    
    def __post_init__(self) -> None:
        """Initialize bindings if not provided."""
        if self.bindings is None:
            from krl_frameworks.core.bindings import BindingRegistry
            self.bindings = BindingRegistry()
    
    @classmethod
    def from_env(cls, user_tier: str = "community") -> "ExecutionContext":
        """
        Create context from environment variables.
        
        Reads:
        - EXECUTION_MODE: "live", "test", or "debug"
        - USER_TIER: Override user tier (optional)
        """
        mode = ExecutionMode.from_env()
        tier = os.getenv("USER_TIER", user_tier)
        return cls(mode=mode, user_tier=tier)
    
    @classmethod
    def live(cls, user_tier: str = "community", **kwargs: Any) -> "ExecutionContext":
        """Create a LIVE execution context."""
        return cls(mode=ExecutionMode.LIVE, user_tier=user_tier, **kwargs)
    
    @classmethod
    def test(cls, user_tier: str = "community", **kwargs: Any) -> "ExecutionContext":
        """Create a TEST execution context."""
        return cls(mode=ExecutionMode.TEST, user_tier=user_tier, **kwargs)
    
    @classmethod
    def debug(cls, user_tier: str = "community", **kwargs: Any) -> "ExecutionContext":
        """Create a DEBUG execution context."""
        return cls(mode=ExecutionMode.DEBUG, user_tier=user_tier, **kwargs)
    
    def validate_capabilities(
        self,
        capabilities: "CapabilityDeclaration",
        *,
        raise_on_error: bool = True,
    ) -> list[str]:
        """
        Validate that all required capabilities are satisfied.
        
        In LIVE mode, any missing required capability causes a hard failure.
        In TEST/DEBUG mode, warnings are logged but execution may proceed.
        
        Args:
            capabilities: The capability declaration to validate.
            raise_on_error: Whether to raise on validation failure.
        
        Returns:
            List of validation error messages.
        
        Raises:
            MissingCapabilityError: If required capability missing in LIVE mode.
        """
        if self.bindings is None:
            from krl_frameworks.core.bindings import BindingRegistry
            self.bindings = BindingRegistry()
        
        errors = capabilities.validate(self.bindings)
        self._validation_errors.extend(errors)
        
        if errors and self.mode.requires_strict_validation:
            if raise_on_error:
                raise MissingCapabilityError(
                    capability_type="capabilities",
                    capability_name="multiple",
                    message=f"Capability validation failed: {'; '.join(errors)}",
                )
        elif errors and not self.mode.requires_strict_validation:
            # Log warnings but allow execution in TEST/DEBUG mode
            self._warnings.extend(
                f"[{self.mode.value}] {error}" for error in errors
            )
        
        return errors
    
    def require_live_data(self, domain: str) -> None:
        """
        Assert that live data is required for a domain.
        
        In LIVE mode, raises if no connector is bound for the domain.
        In TEST mode, logs a warning but continues.
        
        Args:
            domain: Data domain that requires live data.
        
        Raises:
            MissingCapabilityError: If LIVE mode and no connector bound.
        """
        if self.bindings is None or not self.bindings.has_connector(domain):
            if self.mode.requires_strict_validation:
                raise MissingCapabilityError(
                    capability_type="connector",
                    capability_name=domain,
                    message=f"Live data required for domain '{domain}' but no connector bound",
                )
            else:
                self._warnings.append(
                    f"[{self.mode.value}] No connector for domain '{domain}', "
                    "synthetic data may be used"
                )
    
    def assert_not_synthetic(self, data_source: str) -> None:
        """
        Assert that data is not synthetic.
        
        Call this when receiving data to enforce LIVE mode constraints.
        
        Args:
            data_source: Description of the data source.
        
        Raises:
            ExecutionModeViolationError: If LIVE mode and data is synthetic.
        """
        if self.mode == ExecutionMode.LIVE and "synthetic" in data_source.lower():
            raise ExecutionModeViolationError(
                operation=f"Using synthetic data from '{data_source}'",
                current_mode=self.mode,
            )
    
    def log_warning(self, message: str) -> None:
        """Log a warning to the execution context."""
        self._warnings.append(f"[{self.mode.value}] {message}")
    
    @property
    def validation_errors(self) -> list[str]:
        """Get all validation errors."""
        return list(self._validation_errors)
    
    @property
    def warnings(self) -> list[str]:
        """Get all warnings."""
        return list(self._warnings)
    
    def to_audit_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for audit logging.
        
        Includes all information needed for compliance and debugging.
        """
        return {
            "execution_id": self.execution_id,
            "mode": self.mode.value,
            "user_tier": self.user_tier,
            "started_at": self.started_at.isoformat(),
            "validation_errors": self._validation_errors,
            "warnings": self._warnings,
            "metadata": self.metadata,
        }


# ════════════════════════════════════════════════════════════════════════════════
# Context Variable and Context Manager
# ════════════════════════════════════════════════════════════════════════════════

# Thread-local (async-safe) execution context
_current_context: ContextVar[ExecutionContext | None] = ContextVar(
    "execution_context", default=None
)


def get_execution_context() -> ExecutionContext | None:
    """
    Get the current execution context.
    
    Returns None if no context is active.
    """
    return _current_context.get()


def set_execution_context(ctx: ExecutionContext | None) -> None:
    """
    Set the current execution context.
    
    Generally, prefer using the execution_context context manager.
    """
    _current_context.set(ctx)


@contextmanager
def execution_context(
    mode: ExecutionMode | str | None = None,
    user_tier: str = "community",
    **kwargs: Any,
) -> Iterator[ExecutionContext]:
    """
    Context manager for framework execution.
    
    Creates an ExecutionContext and sets it as the current context
    for the duration of the block.
    
    Args:
        mode: Execution mode (LIVE/TEST/DEBUG) or string. If None, reads from env.
        user_tier: User's subscription tier.
        **kwargs: Additional context parameters.
    
    Yields:
        The active ExecutionContext.
    
    Example:
        >>> with execution_context(ExecutionMode.LIVE) as ctx:
        ...     result = framework.fit(bundle)
        ...     print(f"Executed with {len(ctx.warnings)} warnings")
    """
    if mode is None:
        exec_mode = ExecutionMode.from_env()
    elif isinstance(mode, str):
        exec_mode = ExecutionMode(mode.lower())
    else:
        exec_mode = mode
    
    ctx = ExecutionContext(mode=exec_mode, user_tier=user_tier, **kwargs)
    token = _current_context.set(ctx)
    
    try:
        yield ctx
    finally:
        _current_context.reset(token)
