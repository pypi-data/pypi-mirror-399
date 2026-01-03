# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Core Exceptions
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Exception hierarchy for KRL Frameworks.

This module defines a comprehensive exception hierarchy for handling errors
across the framework orchestration pipeline, including tier access control,
validation, execution, and DAG operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from krl_frameworks.core.state import CohortStateVector


# ════════════════════════════════════════════════════════════════════════════════
# Base Exception
# ════════════════════════════════════════════════════════════════════════════════


class FrameworkException(Exception):
    """
    Base exception for all KRL Frameworks errors.
    
    All custom exceptions in krl-frameworks inherit from this class,
    allowing for unified exception handling across the platform.
    
    Attributes:
        message: Human-readable error description.
        details: Optional dictionary with additional error context.
        framework_slug: Optional identifier of the framework that raised the error.
    """
    
    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
        framework_slug: str | None = None,
    ) -> None:
        self.message = message
        self.details = details or {}
        self.framework_slug = framework_slug
        super().__init__(self.message)
    
    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        if self.framework_slug:
            return f"{cls_name}(framework={self.framework_slug!r}, message={self.message!r})"
        return f"{cls_name}(message={self.message!r})"
    
    def to_dict(self) -> dict[str, Any]:
        """Convert exception to a dictionary for API responses and logging."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "framework_slug": self.framework_slug,
            "details": self.details,
        }


# ════════════════════════════════════════════════════════════════════════════════
# Tier Access Exceptions
# ════════════════════════════════════════════════════════════════════════════════


class TierAccessError(FrameworkException):
    """
    Raised when a user attempts to access a framework beyond their tier.
    
    This exception is raised by the @requires_tier decorator when the
    current user's subscription tier does not meet the framework's requirements.
    
    Attributes:
        required_tier: The minimum tier required for access.
        current_tier: The user's current tier.
    """
    
    def __init__(
        self,
        message: str,
        *,
        required_tier: str,
        current_tier: str,
        framework_slug: str | None = None,
    ) -> None:
        super().__init__(
            message,
            details={
                "required_tier": required_tier,
                "current_tier": current_tier,
            },
            framework_slug=framework_slug,
        )
        self.required_tier = required_tier
        self.current_tier = current_tier


class LicenseValidationError(FrameworkException):
    """
    Raised when license validation fails for a framework.
    
    This can occur when:
    - License key is invalid or expired
    - License does not include the requested framework
    - License usage limits have been exceeded
    """
    
    def __init__(
        self,
        message: str,
        *,
        license_id: str | None = None,
        framework_slug: str | None = None,
    ) -> None:
        super().__init__(
            message,
            details={"license_id": license_id},
            framework_slug=framework_slug,
        )
        self.license_id = license_id


# ════════════════════════════════════════════════════════════════════════════════
# Validation Exceptions
# ════════════════════════════════════════════════════════════════════════════════


class ValidationError(FrameworkException):
    """
    Raised when input validation fails.
    
    This is the base class for all validation-related errors including
    data validation, configuration validation, and state validation.
    """
    
    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        value: Any = None,
        framework_slug: str | None = None,
    ) -> None:
        super().__init__(
            message,
            details={"field": field, "value": repr(value) if value is not None else None},
            framework_slug=framework_slug,
        )
        self.field = field
        self.value = value


class DataBundleValidationError(ValidationError):
    """
    Raised when DataBundle validation fails.
    
    This occurs when:
    - Required domains are missing
    - Data format is invalid
    - Data types don't match expected schema
    """
    
    def __init__(
        self,
        message: str,
        *,
        missing_domains: list[str] | None = None,
        invalid_domains: list[str] | None = None,
        framework_slug: str | None = None,
    ) -> None:
        super().__init__(
            message,
            field="domains",
            framework_slug=framework_slug,
        )
        self.missing_domains = missing_domains or []
        self.invalid_domains = invalid_domains or []
        self.details.update({
            "missing_domains": self.missing_domains,
            "invalid_domains": self.invalid_domains,
        })


class StateValidationError(ValidationError):
    """
    Raised when CohortStateVector validation fails.
    
    This occurs when:
    - State dimensions are inconsistent
    - Values are out of valid range
    - Required fields are missing or null
    """
    
    def __init__(
        self,
        message: str,
        *,
        state_field: str | None = None,
        expected_shape: tuple[int, ...] | None = None,
        actual_shape: tuple[int, ...] | None = None,
        framework_slug: str | None = None,
    ) -> None:
        super().__init__(
            message,
            field=state_field,
            framework_slug=framework_slug,
        )
        self.expected_shape = expected_shape
        self.actual_shape = actual_shape
        self.details.update({
            "expected_shape": expected_shape,
            "actual_shape": actual_shape,
        })


class ConfigurationError(ValidationError):
    """
    Raised when framework configuration is invalid.
    
    This occurs when:
    - Required configuration parameters are missing
    - Parameter values are out of valid range
    - Incompatible parameter combinations are specified
    """
    pass


# ════════════════════════════════════════════════════════════════════════════════
# Execution Exceptions
# ════════════════════════════════════════════════════════════════════════════════


class ExecutionError(FrameworkException):
    """
    Raised when framework execution fails.
    
    This is the base class for all execution-related errors including
    simulation failures, convergence issues, and runtime errors.
    """
    
    def __init__(
        self,
        message: str,
        *,
        execution_id: str | None = None,
        step: int | None = None,
        framework_slug: str | None = None,
    ) -> None:
        super().__init__(
            message,
            details={"execution_id": execution_id, "step": step},
            framework_slug=framework_slug,
        )
        self.execution_id = execution_id
        self.step = step


class SimulationError(ExecutionError):
    """
    Raised when CBSS simulation encounters an error.
    
    This can occur during:
    - State transition computation
    - Policy shock application
    - Convergence checking
    """
    
    def __init__(
        self,
        message: str,
        *,
        current_state: CohortStateVector | None = None,
        execution_id: str | None = None,
        step: int | None = None,
        framework_slug: str | None = None,
    ) -> None:
        super().__init__(
            message,
            execution_id=execution_id,
            step=step,
            framework_slug=framework_slug,
        )
        self.current_state = current_state


class ConvergenceError(ExecutionError):
    """
    Raised when simulation fails to converge within specified iterations.
    
    Attributes:
        max_iterations: Maximum iterations attempted.
        final_error: The error metric at termination.
        tolerance: The convergence tolerance that was not met.
    """
    
    def __init__(
        self,
        message: str,
        *,
        max_iterations: int,
        final_error: float,
        tolerance: float,
        framework_slug: str | None = None,
    ) -> None:
        super().__init__(
            message,
            framework_slug=framework_slug,
        )
        self.max_iterations = max_iterations
        self.final_error = final_error
        self.tolerance = tolerance
        self.details.update({
            "max_iterations": max_iterations,
            "final_error": final_error,
            "tolerance": tolerance,
        })


class TransitionError(ExecutionError):
    """
    Raised when a state transition function fails.
    
    This occurs when:
    - Transition matrix is singular
    - State values become invalid (NaN, Inf)
    - Constraints are violated
    """
    
    def __init__(
        self,
        message: str,
        *,
        transition_name: str | None = None,
        from_state: str | None = None,
        to_state: str | None = None,
        framework_slug: str | None = None,
    ) -> None:
        super().__init__(
            message,
            framework_slug=framework_slug,
        )
        self.transition_name = transition_name
        self.from_state = from_state
        self.to_state = to_state
        self.details.update({
            "transition_name": transition_name,
            "from_state": from_state,
            "to_state": to_state,
        })


# ════════════════════════════════════════════════════════════════════════════════
# DAG Exceptions
# ════════════════════════════════════════════════════════════════════════════════


class DAGError(FrameworkException):
    """
    Base exception for DAG-related errors.
    
    This is raised when issues occur during DAG composition,
    validation, or execution.
    """
    pass


class CyclicDependencyError(DAGError):
    """
    Raised when a cyclic dependency is detected in the framework DAG.
    
    Cross-layer framework compositions must form a directed acyclic graph.
    This exception is raised when a cycle is detected during DAG validation.
    
    Attributes:
        cycle: List of framework slugs forming the cycle.
    """
    
    def __init__(
        self,
        message: str,
        *,
        cycle: list[str],
    ) -> None:
        super().__init__(
            message,
            details={"cycle": cycle},
        )
        self.cycle = cycle


class MissingDependencyError(DAGError):
    """
    Raised when a required framework dependency is not available.
    
    This occurs when:
    - A framework references a dependency not in the registry
    - A required upstream framework has not been executed
    - Cross-layer dependencies are not satisfied
    
    Attributes:
        framework_slug: The framework with the missing dependency.
        missing_dependency: The dependency that is not available.
    """
    
    def __init__(
        self,
        message: str,
        *,
        framework_slug: str,
        missing_dependency: str,
    ) -> None:
        super().__init__(
            message,
            details={"missing_dependency": missing_dependency},
            framework_slug=framework_slug,
        )
        self.missing_dependency = missing_dependency


class LayerViolationError(DAGError):
    """
    Raised when cross-layer constraints are violated.
    
    This occurs when:
    - Data flows in an invalid direction between layers
    - Layer ordering constraints are not respected
    - Incompatible frameworks are composed
    """
    
    def __init__(
        self,
        message: str,
        *,
        source_layer: int | str,
        target_layer: int | str,
        framework_slug: str | None = None,
    ) -> None:
        super().__init__(
            message,
            details={
                "source_layer": source_layer,
                "target_layer": target_layer,
            },
            framework_slug=framework_slug,
        )
        self.source_layer = source_layer
        self.target_layer = target_layer


# ════════════════════════════════════════════════════════════════════════════════
# Registry Exceptions
# ════════════════════════════════════════════════════════════════════════════════


class RegistryError(FrameworkException):
    """Base exception for framework registry errors."""
    pass


class FrameworkNotFoundError(RegistryError):
    """
    Raised when a requested framework is not found in the registry.
    
    Attributes:
        slug: The framework slug that was not found.
    """
    
    def __init__(
        self,
        slug: str,
        *,
        available_frameworks: list[str] | None = None,
    ) -> None:
        message = f"Framework '{slug}' not found in registry"
        super().__init__(
            message,
            details={"available_frameworks": available_frameworks},
            framework_slug=slug,
        )
        self.slug = slug
        self.available_frameworks = available_frameworks


class DuplicateFrameworkError(RegistryError):
    """
    Raised when attempting to register a framework with a duplicate slug.
    
    Attributes:
        slug: The duplicate framework slug.
    """
    
    def __init__(self, slug: str) -> None:
        message = f"Framework '{slug}' is already registered"
        super().__init__(message, framework_slug=slug)
        self.slug = slug


# ════════════════════════════════════════════════════════════════════════════════
# Audit Exceptions
# ════════════════════════════════════════════════════════════════════════════════


class AuditError(FrameworkException):
    """
    Raised when audit logging or snapshot operations fail.
    
    This exception indicates issues with:
    - Execution logging
    - State snapshot creation
    - Reproducibility verification
    """
    
    def __init__(
        self,
        message: str,
        *,
        execution_id: str | None = None,
        operation: str | None = None,
        framework_slug: str | None = None,
    ) -> None:
        super().__init__(
            message,
            details={
                "execution_id": execution_id,
                "operation": operation,
            },
            framework_slug=framework_slug,
        )
        self.execution_id = execution_id
        self.operation = operation


# ════════════════════════════════════════════════════════════════════════════════
# Export All Exceptions
# ════════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Base
    "FrameworkException",
    # Tier access
    "TierAccessError",
    "LicenseValidationError",
    # Validation
    "ValidationError",
    "DataBundleValidationError",
    "StateValidationError",
    "ConfigurationError",
    # Execution
    "ExecutionError",
    "SimulationError",
    "ConvergenceError",
    "TransitionError",
    # DAG
    "DAGError",
    "CyclicDependencyError",
    "MissingDependencyError",
    "LayerViolationError",
    # Registry
    "RegistryError",
    "FrameworkNotFoundError",
    "DuplicateFrameworkError",
    # Audit
    "AuditError",
]
