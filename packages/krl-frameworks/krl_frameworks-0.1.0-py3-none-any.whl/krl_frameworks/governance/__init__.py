# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Runtime Governance Layer
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Runtime Governance Layer for KRL Frameworks.

This package provides the enterprise-grade execution substrate that enforces:
- Production guards (LIVE-only in production environments)
- Automatic binding resolution (capabilities → connectors/toolkits)
- Structured audit logging for all resolution decisions
- Multi-framework pipeline capability closure validation
- Package resolution with fail-fast behavior
- CI matrix enforcement for ecosystem integrity

Components:
    - ProductionGuard: Environment detection and LIVE mode enforcement
    - ConnectorFactoryRegistry: Tier-gated connector factory management
    - BindingResolver: Automatic capability → binding resolution
    - CapabilityClosureValidator: Pipeline-level capability validation
    - PackageResolver: Capability → Package resolution algorithm
    - CIMatrix: Test scenario specifications for CI enforcement
    - PackageTemplates: Canonical pyproject.toml templates
    - AuditLogger: Structured JSON logging for compliance

Non-Negotiable Architectural Doctrine:
    1. Capabilities are declarative contracts, not imports
    2. Bindings are runtime-resolved, not statically assumed
    3. Execution mode enforces truth (LIVE ≠ TEST)
    4. Package boundaries are enforcement boundaries
    5. Silent degradation is forbidden

Design Principles:
    1. Fail-fast in LIVE mode — no silent degradation
    2. Explicit over implicit — all resolution decisions logged
    3. Tier enforcement at every boundary
    4. Production is hostile territory — non-LIVE forbidden
"""

from krl_frameworks.governance.production_guard import (
    ProductionEnvironment,
    ProductionGuard,
    ProductionViolationError,
    detect_environment,
    is_production,
    get_production_guard,
)
from krl_frameworks.governance.connector_registry import (
    ConnectorFactory,
    ConnectorFactoryRegistry,
    ConnectorProtocol,
    ConnectorNotFoundError,
    TierAccessDeniedError,
    get_global_connector_registry,
    register_connector_factory,
)
from krl_frameworks.governance.binding_resolver import (
    BindingResolver,
    BindingResolutionError,
    ResolutionResult,
    ResolutionFailure,
    get_binding_resolver,
)
from krl_frameworks.governance.audit import (
    AuditEvent,
    AuditEventType,
    AuditLogger,
    get_audit_logger,
)
from krl_frameworks.governance.closure_validator import (
    CapabilityClosure,
    ClosureConflict,
    ClosureValidator,
    ClosureValidationError,
)
from krl_frameworks.governance.package_resolver import (
    PackageResolver,
    ResolutionStatus,
    FailureReason,
    PackageSpec,
    CAPABILITY_PACKAGE_MAP,
    get_global_resolver,
    resolve_capabilities,
)
from krl_frameworks.governance.ci_matrix import (
    TestScenario,
    ExpectedOutcome,
    CIMatrix,
    get_core_scenarios,
    get_connector_scenarios,
    get_toolkit_scenarios,
    get_integration_scenarios,
)
from krl_frameworks.governance.package_templates import (
    PackageTemplate,
    ECOSYSTEM_PACKAGES,
    VERSIONS,
    get_template,
    validate_pyproject,
    check_forbidden_dependencies,
)

__all__ = [
    # Production Guard
    "ProductionEnvironment",
    "ProductionGuard",
    "ProductionViolationError",
    "detect_environment",
    "is_production",
    "get_production_guard",
    # Connector Registry
    "ConnectorFactory",
    "ConnectorFactoryRegistry",
    "ConnectorProtocol",
    "ConnectorNotFoundError",
    "TierAccessDeniedError",
    "get_global_connector_registry",
    "register_connector_factory",
    # Binding Resolver
    "BindingResolver",
    "BindingResolutionError",
    "ResolutionResult",
    "ResolutionFailure",
    "get_binding_resolver",
    # Audit
    "AuditEvent",
    "AuditEventType",
    "AuditLogger",
    "get_audit_logger",
    # Closure Validator
    "CapabilityClosure",
    "ClosureConflict",
    "ClosureValidator",
    "ClosureValidationError",
    # Package Resolver (Capability → Package Resolution Algorithm)
    "PackageResolver",
    "ResolutionStatus",
    "FailureReason",
    "PackageSpec",
    "CAPABILITY_PACKAGE_MAP",
    "get_global_resolver",
    "resolve_capabilities",
    # CI Matrix (Governance Enforcement)
    "TestScenario",
    "ExpectedOutcome",
    "CIMatrix",
    "get_core_scenarios",
    "get_connector_scenarios",
    "get_toolkit_scenarios",
    "get_integration_scenarios",
    # Package Templates (Canonical pyproject.toml)
    "PackageTemplate",
    "ECOSYSTEM_PACKAGES",
    "VERSIONS",
    "get_template",
    "validate_pyproject",
    "check_forbidden_dependencies",
]
