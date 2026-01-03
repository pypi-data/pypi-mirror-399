# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Core Module
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Core module for KRL Frameworks.

This module provides the foundational abstractions, types, and utilities
used across all framework implementations.

Public API:
    - BaseMetaFramework: Abstract base class for all frameworks
    - FrameworkRegistry: Registry for framework discovery
    - CohortStateVector: Canonical state vector for CBSS
    - DataBundle: Data injection container
    - Tier, @requires_tier: Tier-based access control
    - VerticalLayer: The 6-layer architecture enum
    - Exceptions: Comprehensive exception hierarchy
"""

from krl_frameworks.core.base import (
    BaseMetaFramework,
    FrameworkExecutionResult,
    FrameworkMetadata,
    VerticalLayer,
)
from krl_frameworks.core.config import (
    AggregationMethod,
    ConvergenceMethod,
    FrameworkConfig,
    SimulationConfig,
)
from krl_frameworks.core.dashboard_spec import (
    FrameworkDashboardSpec,
    OutputViewSpec,
    ParameterGroupSpec,
    ResultEnvelope,
    ViewType,
)
from krl_frameworks.core.output_envelope import (
    DimensionManifest,
    FrameworkOutputEnvelope,
    ProvenanceRecord,
    create_dimension_manifest,
    create_provenance_record,
)
from krl_frameworks.core.data_bundle import (
    DataBundle,
    DataDomain,
    DomainData,
)
from krl_frameworks.core.exceptions import (
    AuditError,
    ConfigurationError,
    ConvergenceError,
    CyclicDependencyError,
    DAGError,
    DataBundleValidationError,
    DuplicateFrameworkError,
    ExecutionError,
    FrameworkException,
    FrameworkNotFoundError,
    LayerViolationError,
    LicenseValidationError,
    MissingDependencyError,
    RegistryError,
    SimulationError,
    StateValidationError,
    TierAccessError,
    TransitionError,
    ValidationError,
)
from krl_frameworks.core.registry import (
    FrameworkRegistry,
    RegistryEntry,
    get_framework,
    get_global_registry,
    register_framework,
)
from krl_frameworks.core.state import (
    CohortStateVector,
    FloatArray,
    StateTrajectory,
)
from krl_frameworks.core.tier import (
    Tier,
    TierAccessEvent,
    TierContext,
    check_tier_access,
    clear_tier_access_log,
    get_accessible_tiers,
    get_current_tier,
    get_current_user_id,
    get_tier_access_log,
    log_tier_access,
    requires_tier,
    set_current_tier,
    set_current_user_id,
    tier_gate,
    tier_protected_class,
)
# Integration Spine (Runtime Dependency Resolution)
from krl_frameworks.core.capabilities import (
    CapabilityDeclaration,
    CapabilityScope,
    ConnectorRequirement,
    ModelZooRequirement,
    ToolkitRequirement,
)
from krl_frameworks.core.execution_context import (
    ExecutionContext,
    ExecutionMode,
    ExecutionModeViolationError,
    MissingCapabilityError,
    execution_context,
    get_execution_context,
    set_execution_context,
)
from krl_frameworks.core.bindings import (
    BindingRegistry,
    ConnectorBinding,
    ModelZooBinding,
    ToolkitBinding,
)

__all__ = [
    # Base framework
    "BaseMetaFramework",
    "FrameworkMetadata",
    "FrameworkExecutionResult",
    "VerticalLayer",
    # Dashboard specification
    "FrameworkDashboardSpec",
    "OutputViewSpec",
    "ParameterGroupSpec",
    "ResultEnvelope",
    "ViewType",
    # Output Envelope
    "FrameworkOutputEnvelope",
    "DimensionManifest",
    "ProvenanceRecord",
    "create_dimension_manifest",
    "create_provenance_record",
    # Configuration
    "FrameworkConfig",
    "SimulationConfig",
    "ConvergenceMethod",
    "AggregationMethod",
    # State
    "CohortStateVector",
    "StateTrajectory",
    "FloatArray",
    # Data
    "DataBundle",
    "DataDomain",
    "DomainData",
    # Registry
    "FrameworkRegistry",
    "RegistryEntry",
    "get_global_registry",
    "register_framework",
    "get_framework",
    # Tier
    "Tier",
    "TierContext",
    "TierAccessEvent",
    "requires_tier",
    "tier_protected_class",
    "get_current_tier",
    "set_current_tier",
    "get_current_user_id",
    "set_current_user_id",
    "check_tier_access",
    "get_accessible_tiers",
    "tier_gate",
    "log_tier_access",
    "get_tier_access_log",
    "clear_tier_access_log",
    # Integration Spine - Capabilities
    "CapabilityDeclaration",
    "CapabilityScope",
    "ConnectorRequirement",
    "ToolkitRequirement",
    "ModelZooRequirement",
    # Integration Spine - Execution Context
    "ExecutionContext",
    "ExecutionMode",
    "execution_context",
    "get_execution_context",
    "set_execution_context",
    "MissingCapabilityError",
    "ExecutionModeViolationError",
    # Integration Spine - Bindings
    "BindingRegistry",
    "ConnectorBinding",
    "ToolkitBinding",
    "ModelZooBinding",
    # Exceptions
    "FrameworkException",
    "TierAccessError",
    "LicenseValidationError",
    "ValidationError",
    "DataBundleValidationError",
    "StateValidationError",
    "ConfigurationError",
    "ExecutionError",
    "SimulationError",
    "ConvergenceError",
    "TransitionError",
    "DAGError",
    "CyclicDependencyError",
    "MissingDependencyError",
    "LayerViolationError",
    "RegistryError",
    "FrameworkNotFoundError",
    "DuplicateFrameworkError",
    "AuditError",
]
