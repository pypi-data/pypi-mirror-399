# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Tier Access Control
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Tier-based access control for KRL Frameworks.

This module provides the @requires_tier() decorator and supporting
infrastructure for enforcing subscription tier restrictions on
framework access. It integrates with krl-types for canonical tier
definitions and supports runtime enforcement with audit logging.

Tier Hierarchy:
    COMMUNITY < PROFESSIONAL < TEAM < ENTERPRISE < CUSTOM

Community-tier frameworks (MPI, HDI, SPI) are freely accessible.
Enterprise-tier frameworks (REMSOM, IAMs, CGE hybrids, DAG orchestration)
require elevated subscription levels.
"""

from __future__ import annotations

import functools
import logging
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import IntEnum
from typing import TYPE_CHECKING, Any, Callable, TypeVar

from krl_frameworks.core.exceptions import TierAccessError

if TYPE_CHECKING:
    from collections.abc import Awaitable


# ════════════════════════════════════════════════════════════════════════════════
# Tier Enum (aligned with krl-types)
# ════════════════════════════════════════════════════════════════════════════════


class Tier(IntEnum):
    """
    Subscription tiers with numeric ordering for comparison.
    
    This enum provides integer values for tier comparison,
    allowing simple `>=` checks for access control.
    
    Values are aligned with krl-types.billing.Tier but use
    IntEnum for ordering support.
    """
    
    COMMUNITY = 0
    PROFESSIONAL = 1
    PRO = 1  # Alias for backward compatibility
    TEAM = 2
    ENTERPRISE = 3
    CUSTOM = 4
    
    @classmethod
    def from_string(cls, value: str) -> Tier:
        """
        Convert a string to Tier, case-insensitive.
        
        Args:
            value: Tier name as string.
        
        Returns:
            Corresponding Tier enum value.
        
        Raises:
            ValueError: If tier name is not recognized.
        """
        normalized = value.upper().strip()
        
        # Handle aliases
        if normalized == "PRO":
            normalized = "PROFESSIONAL"
        
        try:
            return cls[normalized]
        except KeyError:
            valid = [t.name for t in cls if t.name != "PRO"]
            raise ValueError(
                f"Invalid tier '{value}'. Valid tiers: {valid}"
            ) from None
    
    @property
    def display_name(self) -> str:
        """Human-readable tier name."""
        names = {
            Tier.COMMUNITY: "Community",
            Tier.PROFESSIONAL: "Professional",
            Tier.TEAM: "Team",
            Tier.ENTERPRISE: "Enterprise",
            Tier.CUSTOM: "Custom",
        }
        return names.get(self, self.name.title())
    
    def can_access(self, required: Tier) -> bool:
        """
        Check if this tier can access a resource requiring `required` tier.
        
        Args:
            required: The tier required for access.
        
        Returns:
            True if this tier >= required tier.
        """
        return self.value >= required.value
    
    @classmethod
    def from_api(cls, api_tier: Any) -> Tier:
        """
        Convert from krl-types billing Tier to framework Tier.
        
        This provides explicit conversion from the API tier enum
        without importing krl-types directly into framework logic.
        
        Args:
            api_tier: A krl_types.billing.Tier enum value, or string.
        
        Returns:
            Corresponding framework Tier.
        
        Raises:
            ValueError: If tier cannot be mapped.
        
        Example:
            >>> from krl_types.billing import Tier as APITier
            >>> framework_tier = Tier.from_api(APITier.ENTERPRISE)
            >>> framework_tier
            <Tier.ENTERPRISE: 3>
        """
        # Handle string input (API returns string)
        if isinstance(api_tier, str):
            return cls.from_string(api_tier)
        
        # Handle enum with .value attribute (krl-types Tier)
        if hasattr(api_tier, "value"):
            tier_value = api_tier.value
            # krl-types uses lowercase string values
            if isinstance(tier_value, str):
                return cls.from_string(tier_value)
            # Numeric value
            if isinstance(tier_value, int):
                return cls(tier_value)
        
        # Handle enum with .name attribute
        if hasattr(api_tier, "name"):
            return cls.from_string(api_tier.name)
        
        raise ValueError(
            f"Cannot convert {type(api_tier).__name__} to Tier. "
            f"Expected krl_types.billing.Tier, string, or int."
        )
    
    def to_api(self) -> str:
        """
        Convert to API-compatible tier representation.
        
        Returns lowercase string matching krl-types.billing.Tier values.
        This format is used in API requests/responses and database storage.
        
        Returns:
            Lowercase tier name string.
        
        Example:
            >>> Tier.ENTERPRISE.to_api()
            'enterprise'
        """
        # Handle PRO alias
        if self == Tier.PRO:
            return "professional"
        return self.name.lower()


# ════════════════════════════════════════════════════════════════════════════════
# Tier Context
# ════════════════════════════════════════════════════════════════════════════════


# Context variable for current user's tier (set by middleware/auth)
_current_tier: ContextVar[Tier] = ContextVar("current_tier", default=Tier.COMMUNITY)
_current_user_id: ContextVar[str | None] = ContextVar("current_user_id", default=None)


def get_current_tier() -> Tier:
    """Get the current user's tier from context."""
    return _current_tier.get()


def set_current_tier(tier: Tier | str) -> None:
    """
    Set the current user's tier in context.
    
    This should be called by authentication middleware before
    any framework operations.
    
    Args:
        tier: Tier enum or string name.
    """
    if isinstance(tier, str):
        tier = Tier.from_string(tier)
    _current_tier.set(tier)


def get_current_user_id() -> str | None:
    """Get the current user's ID from context."""
    return _current_user_id.get()


def set_current_user_id(user_id: str | None) -> None:
    """Set the current user's ID in context."""
    _current_user_id.set(user_id)


@dataclass
class TierContext:
    """
    Context manager for temporarily setting tier context.
    
    Useful for testing and for service-to-service calls where
    the caller's tier should be used.
    
    Example:
        >>> with TierContext(Tier.ENTERPRISE, user_id="admin"):
        ...     result = enterprise_framework.simulate()
    """
    
    tier: Tier
    user_id: str | None = None
    _previous_tier: Tier = field(init=False, repr=False)
    _previous_user_id: str | None = field(init=False, repr=False)
    
    def __enter__(self) -> TierContext:
        self._previous_tier = get_current_tier()
        self._previous_user_id = get_current_user_id()
        set_current_tier(self.tier)
        set_current_user_id(self.user_id)
        return self
    
    def __exit__(self, *args: Any) -> None:
        set_current_tier(self._previous_tier)
        set_current_user_id(self._previous_user_id)


# ════════════════════════════════════════════════════════════════════════════════
# Tier Access Audit Log
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class TierAccessEvent:
    """
    Record of a tier access check for auditing.
    
    Attributes:
        timestamp: When the access check occurred.
        user_id: User making the request.
        current_tier: User's current tier.
        required_tier: Tier required for the resource.
        framework_slug: Framework being accessed.
        method_name: Method being called.
        granted: Whether access was granted.
        reason: Explanation if access was denied.
    """
    
    timestamp: datetime
    user_id: str | None
    current_tier: Tier
    required_tier: Tier
    framework_slug: str
    method_name: str
    granted: bool
    reason: str = ""
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "current_tier": self.current_tier.name,
            "required_tier": self.required_tier.name,
            "framework_slug": self.framework_slug,
            "method_name": self.method_name,
            "granted": self.granted,
            "reason": self.reason,
        }


# Audit log storage (in production, this would be a database or log service)
_tier_access_log: list[TierAccessEvent] = []
_audit_logger = logging.getLogger("krl_frameworks.tier_access")


def log_tier_access(event: TierAccessEvent) -> None:
    """Log a tier access event."""
    _tier_access_log.append(event)
    
    level = logging.INFO if event.granted else logging.WARNING
    _audit_logger.log(
        level,
        "Tier access %s: user=%s tier=%s required=%s framework=%s.%s",
        "GRANTED" if event.granted else "DENIED",
        event.user_id,
        event.current_tier.name,
        event.required_tier.name,
        event.framework_slug,
        event.method_name,
    )


def get_tier_access_log() -> list[TierAccessEvent]:
    """Get the tier access audit log."""
    return _tier_access_log.copy()


def clear_tier_access_log() -> None:
    """Clear the tier access audit log (for testing)."""
    _tier_access_log.clear()


# ════════════════════════════════════════════════════════════════════════════════
# Requires Tier Decorator
# ════════════════════════════════════════════════════════════════════════════════


F = TypeVar("F", bound=Callable[..., Any])


def requires_tier(
    tier: Tier | str,
    *,
    audit: bool = True,
    raise_on_deny: bool = True,
) -> Callable[[F], F]:
    """
    Decorator to enforce tier-based access control on framework methods.
    
    This decorator checks the current user's tier against the required
    tier before allowing method execution. It supports both sync and
    async methods.
    
    Args:
        tier: Minimum tier required for access.
        audit: Whether to log access attempts (default True).
        raise_on_deny: Whether to raise TierAccessError on denial.
            If False, returns None instead.
    
    Returns:
        Decorated function with tier checking.
    
    Example:
        >>> class MyFramework(BaseMetaFramework):
        ...     @requires_tier(Tier.ENTERPRISE)
        ...     def simulate(self, steps: int) -> SimulationResult:
        ...         # Only Enterprise+ users can call this
        ...         ...
        
        >>> @requires_tier("professional")
        ... def pro_feature():
        ...     ...
    
    Raises:
        TierAccessError: When current tier < required tier and raise_on_deny=True.
    """
    # Convert string to Tier if needed
    required_tier = tier if isinstance(tier, Tier) else Tier.from_string(tier)
    
    def decorator(func: F) -> F:
        # Check if function is async
        is_async = hasattr(func, "__wrapped__") or (
            hasattr(func, "__code__") and 
            func.__code__.co_flags & 0x80  # CO_COROUTINE
        )
        
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            return _check_and_execute(
                func, args, kwargs,
                required_tier=required_tier,
                audit=audit,
                raise_on_deny=raise_on_deny,
            )
        
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            result = _check_and_execute(
                func, args, kwargs,
                required_tier=required_tier,
                audit=audit,
                raise_on_deny=raise_on_deny,
            )
            # If the function is async, await it
            if hasattr(result, "__await__"):
                return await result
            return result
        
        # Attach metadata for introspection
        wrapper = async_wrapper if is_async else sync_wrapper
        wrapper._required_tier = required_tier  # type: ignore[attr-defined]
        wrapper._tier_protected = True  # type: ignore[attr-defined]
        
        return wrapper  # type: ignore[return-value]
    
    return decorator


def _check_and_execute(
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    *,
    required_tier: Tier,
    audit: bool,
    raise_on_deny: bool,
) -> Any:
    """Execute tier check and function if allowed."""
    current_tier = get_current_tier()
    user_id = get_current_user_id()
    
    # Extract framework_slug from self if available
    framework_slug = ""
    if args and hasattr(args[0], "slug"):
        framework_slug = args[0].slug
    elif args and hasattr(args[0], "__class__"):
        framework_slug = args[0].__class__.__name__
    
    # Check access
    granted = current_tier.can_access(required_tier)
    
    # Log access attempt
    if audit:
        event = TierAccessEvent(
            timestamp=datetime.now(timezone.utc),
            user_id=user_id,
            current_tier=current_tier,
            required_tier=required_tier,
            framework_slug=framework_slug,
            method_name=func.__name__,
            granted=granted,
            reason="" if granted else f"Requires {required_tier.display_name} tier",
        )
        log_tier_access(event)
    
    # Enforce access
    if not granted:
        if raise_on_deny:
            raise TierAccessError(
                f"Access denied: {func.__name__} requires {required_tier.display_name} tier, "
                f"but current tier is {current_tier.display_name}",
                required_tier=required_tier.name,
                current_tier=current_tier.name,
                framework_slug=framework_slug,
            )
        return None
    
    # Execute function
    return func(*args, **kwargs)


# ════════════════════════════════════════════════════════════════════════════════
# Tier Utilities
# ════════════════════════════════════════════════════════════════════════════════


def check_tier_access(required: Tier | str) -> bool:
    """
    Check if current tier meets requirement without raising exception.
    
    Args:
        required: Required tier for access.
    
    Returns:
        True if current tier >= required tier.
    """
    if isinstance(required, str):
        required = Tier.from_string(required)
    
    return get_current_tier().can_access(required)


def get_accessible_tiers() -> list[Tier]:
    """
    Get list of tiers accessible by current user.
    
    Returns:
        List of Tier values that current tier can access.
    """
    current = get_current_tier()
    return [t for t in Tier if current.can_access(t)]


def tier_gate(
    community_value: Any,
    pro_value: Any = None,
    enterprise_value: Any = None,
) -> Any:
    """
    Return different values based on current tier.
    
    Useful for tier-based feature flags and configuration.
    
    Args:
        community_value: Value for Community tier.
        pro_value: Value for Professional tier (defaults to community_value).
        enterprise_value: Value for Enterprise tier (defaults to pro_value).
    
    Returns:
        Appropriate value for current tier.
    
    Example:
        >>> max_cohorts = tier_gate(1000, 10000, 100000)
        >>> feature_enabled = tier_gate(False, True, True)
    """
    if pro_value is None:
        pro_value = community_value
    if enterprise_value is None:
        enterprise_value = pro_value
    
    current = get_current_tier()
    
    if current >= Tier.ENTERPRISE:
        return enterprise_value
    elif current >= Tier.PROFESSIONAL:
        return pro_value
    else:
        return community_value


# ════════════════════════════════════════════════════════════════════════════════
# Class-level Tier Decorator
# ════════════════════════════════════════════════════════════════════════════════


def tier_protected_class(tier: Tier | str) -> Callable[[type], type]:
    """
    Class decorator to set default tier for all public methods.
    
    Individual methods can override with their own @requires_tier decorator.
    
    Args:
        tier: Default tier required for all public methods.
    
    Returns:
        Class decorator.
    
    Example:
        >>> @tier_protected_class(Tier.ENTERPRISE)
        ... class EnterpriseFramework(BaseMetaFramework):
        ...     def simulate(self):
        ...         ...  # Requires Enterprise tier
    """
    required_tier = tier if isinstance(tier, Tier) else Tier.from_string(tier)
    
    def decorator(cls: type) -> type:
        # Store tier requirement on class
        cls._default_tier = required_tier  # type: ignore[attr-defined]
        
        # Wrap public methods that aren't already protected
        for name in dir(cls):
            if name.startswith("_"):
                continue
            
            attr = getattr(cls, name)
            if not callable(attr):
                continue
            
            # Skip if already tier-protected
            if getattr(attr, "_tier_protected", False):
                continue
            
            # Apply tier protection
            wrapped = requires_tier(required_tier)(attr)
            setattr(cls, name, wrapped)
        
        return cls
    
    return decorator


# ════════════════════════════════════════════════════════════════════════════════
# Exports
# ════════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Core types
    "Tier",
    "TierContext",
    "TierAccessEvent",
    # Decorators
    "requires_tier",
    "tier_protected_class",
    # Context functions
    "get_current_tier",
    "set_current_tier",
    "get_current_user_id",
    "set_current_user_id",
    # Utilities
    "check_tier_access",
    "get_accessible_tiers",
    "tier_gate",
    # Audit
    "log_tier_access",
    "get_tier_access_log",
    "clear_tier_access_log",
]
