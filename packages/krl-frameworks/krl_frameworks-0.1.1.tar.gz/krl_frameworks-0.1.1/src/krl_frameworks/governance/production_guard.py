# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Production Guard
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Production Guard for Runtime Governance.

Enforces that production environments MUST use ExecutionMode.LIVE.
Non-LIVE execution in production is a hard failure, not a configuration option.

Environment Detection:
    The guard detects production via multiple signals:
    1. PRODUCTION=true (explicit flag)
    2. ENVIRONMENT=production
    3. NODE_ENV=production (for polyglot deployments)
    4. RAILWAY_ENVIRONMENT=production (Railway.app)
    5. RENDER=true (Render.com)
    6. AWS_EXECUTION_ENV contains 'production'

Design Principle:
    Production is hostile territory. The system assumes TEST mode by default,
    but when production is detected, LIVE mode becomes mandatory.
    This is not configurable—it is constitutional.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from krl_frameworks.core.execution_context import ExecutionContext, ExecutionMode

__all__ = [
    "ProductionEnvironment",
    "ProductionGuard",
    "ProductionViolationError",
    "is_production",
    "detect_environment",
]


class ProductionEnvironment(str, Enum):
    """
    Detected deployment environment.
    
    DEVELOPMENT: Local development, CI, staging
    PRODUCTION: Live customer-facing deployment
    UNKNOWN: Cannot determine (treated as development)
    """
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    UNKNOWN = "unknown"


class ProductionViolationError(RuntimeError):
    """
    Raised when production environment constraints are violated.
    
    This is a hard failure that cannot be caught and ignored.
    It indicates a fundamental misconfiguration that must be fixed.
    """
    
    def __init__(
        self,
        violation: str,
        detected_mode: str,
        required_mode: str = "live",
    ) -> None:
        self.violation = violation
        self.detected_mode = detected_mode
        self.required_mode = required_mode
        super().__init__(
            f"PRODUCTION VIOLATION: {violation}. "
            f"Detected mode '{detected_mode}' but production requires '{required_mode}'. "
            f"This is not a recoverable error."
        )


def detect_environment() -> ProductionEnvironment:
    """
    Detect the current deployment environment.
    
    Checks multiple environment variables to determine if running
    in production. Returns PRODUCTION if any production signal is found.
    
    Returns:
        ProductionEnvironment indicating detected environment.
    
    Environment Variables Checked:
        - PRODUCTION: "true" → production
        - ENVIRONMENT: "production" → production
        - NODE_ENV: "production" → production
        - RAILWAY_ENVIRONMENT: "production" → production
        - RENDER: "true" → production (Render.com always sets this in prod)
        - AWS_EXECUTION_ENV: contains "production" → production
        - KUBERNETES_SERVICE_HOST: present → production (K8s deployment)
        - DYNO: present → production (Heroku)
    """
    # Explicit production flag (highest priority)
    if os.getenv("PRODUCTION", "").lower() == "true":
        return ProductionEnvironment.PRODUCTION
    
    # Environment variable checks
    env = os.getenv("ENVIRONMENT", "").lower()
    if env == "production":
        return ProductionEnvironment.PRODUCTION
    
    node_env = os.getenv("NODE_ENV", "").lower()
    if node_env == "production":
        return ProductionEnvironment.PRODUCTION
    
    # Platform-specific detection
    if os.getenv("RAILWAY_ENVIRONMENT", "").lower() == "production":
        return ProductionEnvironment.PRODUCTION
    
    if os.getenv("RENDER", "").lower() == "true":
        return ProductionEnvironment.PRODUCTION
    
    aws_env = os.getenv("AWS_EXECUTION_ENV", "").lower()
    if "production" in aws_env:
        return ProductionEnvironment.PRODUCTION
    
    # Kubernetes detection (assumes K8s = production)
    if os.getenv("KUBERNETES_SERVICE_HOST"):
        return ProductionEnvironment.PRODUCTION
    
    # Heroku detection
    if os.getenv("DYNO"):
        return ProductionEnvironment.PRODUCTION
    
    # Check for explicit development signals
    if env in ("development", "dev", "local", "test", "testing", "ci"):
        return ProductionEnvironment.DEVELOPMENT
    
    if node_env in ("development", "dev", "test"):
        return ProductionEnvironment.DEVELOPMENT
    
    return ProductionEnvironment.UNKNOWN


def is_production() -> bool:
    """
    Quick check if currently running in production.
    
    Returns:
        True if production environment detected.
    """
    return detect_environment() == ProductionEnvironment.PRODUCTION


@dataclass
class ProductionGuard:
    """
    Enforces production environment constraints.
    
    The ProductionGuard is the constitutional enforcement layer.
    When production is detected, it mandates LIVE execution mode.
    There is no override. There is no escape hatch.
    
    Usage:
        >>> guard = ProductionGuard()
        >>> guard.enforce(execution_context)  # Raises if non-LIVE in production
    
    Integration:
        The guard should be invoked:
        1. At ExecutionContext creation
        2. At Framework.fit() entry
        3. At any boundary where mode matters
    
    Example:
        >>> from krl_frameworks.governance import ProductionGuard
        >>> 
        >>> guard = ProductionGuard()
        >>> if guard.is_production:
        ...     print("Production mode - LIVE enforcement active")
        >>> 
        >>> # This will raise if in production with non-LIVE mode
        >>> guard.enforce(my_execution_context)
    """
    
    # Cache environment detection (environment doesn't change at runtime)
    _environment: ProductionEnvironment | None = None
    
    # Testing override: force production mode for testing enforcement
    _force_production: bool = False
    
    @classmethod
    def for_testing(cls, force_production: bool = True) -> "ProductionGuard":
        """
        Create a ProductionGuard for testing purposes.
        
        Args:
            force_production: If True, always behaves as if in production.
        
        Returns:
            ProductionGuard configured for testing.
        """
        guard = cls()
        guard._force_production = force_production
        return guard
    
    @property
    def environment(self) -> ProductionEnvironment:
        """Get the detected environment (cached)."""
        if self._force_production:
            return ProductionEnvironment.PRODUCTION
        if self._environment is None:
            self._environment = detect_environment()
        return self._environment
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == ProductionEnvironment.PRODUCTION
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment in (
            ProductionEnvironment.DEVELOPMENT,
            ProductionEnvironment.UNKNOWN,
        )
    
    def enforce(self, context: "ExecutionContext") -> None:
        """
        Enforce production constraints on execution context.
        
        In production:
        - LIVE mode is REQUIRED
        - TEST/DEBUG mode raises ProductionViolationError
        
        In development:
        - All modes are permitted
        
        Args:
            context: The execution context to validate.
        
        Raises:
            ProductionViolationError: If production but mode is not LIVE.
        """
        from krl_frameworks.core.execution_context import ExecutionMode
        
        if not self.is_production:
            return  # Development allows all modes
        
        if context.mode != ExecutionMode.LIVE:
            raise ProductionViolationError(
                violation="Non-LIVE execution mode in production environment",
                detected_mode=context.mode.value,
                required_mode=ExecutionMode.LIVE.value,
            )
    
    def enforce_mode(self, mode: "ExecutionMode") -> None:
        """
        Enforce production constraints on a mode value.
        
        Convenience method for when you have a mode but not a full context.
        
        Args:
            mode: The execution mode to validate.
        
        Raises:
            ProductionViolationError: If production but mode is not LIVE.
        """
        from krl_frameworks.core.execution_context import ExecutionMode
        
        if not self.is_production:
            return
        
        if mode != ExecutionMode.LIVE:
            raise ProductionViolationError(
                violation="Non-LIVE execution mode in production environment",
                detected_mode=mode.value,
                required_mode=ExecutionMode.LIVE.value,
            )
    
    def assert_can_use_synthetic_data(self) -> None:
        """
        Assert that synthetic data usage is permitted.
        
        In production, synthetic data is NEVER permitted.
        
        Raises:
            ProductionViolationError: If in production.
        """
        if self.is_production:
            raise ProductionViolationError(
                violation="Synthetic data usage attempted in production",
                detected_mode="synthetic",
                required_mode="live_data_only",
            )
    
    @classmethod
    def get_instance(cls) -> "ProductionGuard":
        """
        Get a singleton ProductionGuard instance.
        
        The guard is stateless (environment is cached at class level),
        so a singleton is safe and efficient.
        """
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance


# Module-level convenience function
_guard: ProductionGuard | None = None


def get_production_guard() -> ProductionGuard:
    """Get the global ProductionGuard instance."""
    global _guard
    if _guard is None:
        _guard = ProductionGuard()
    return _guard
