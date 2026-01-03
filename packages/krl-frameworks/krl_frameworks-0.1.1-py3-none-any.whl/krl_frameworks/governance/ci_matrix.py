# ════════════════════════════════════════════════════════════════════════════════
# KRL Ecosystem CI Matrix Specification
# ════════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Author: KRL Platform Engineering
# Last Updated: 2025-12-30
# ════════════════════════════════════════════════════════════════════════════════

"""
CI Matrix Design for Package Governance Enforcement.

This document specifies the comprehensive CI test matrices that prove ecosystem
integrity across all package combinations and execution modes.

DESIGN PRINCIPLES:
    1. Every failure mode must be explicitly tested
    2. All package boundary violations must be detected
    3. Version skew must be exposed, not hidden
    4. LIVE mode requirements are constitutional, not configurable
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

__all__ = [
    "TestScenario",
    "ExpectedOutcome",
    "CIMatrix",
    "get_core_scenarios",
    "get_connector_scenarios",
    "get_toolkit_scenarios",
    "get_integration_scenarios",
]


class ExpectedOutcome(str, Enum):
    """
    Expected test outcome.
    
    PASS: Test should succeed
    FAIL: Test should fail with explicit error
    WARN: Test should pass with warnings (TEST mode only)
    SKIP: Test should be skipped (optional dependency missing)
    """
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"


@dataclass
class TestScenario:
    """
    A single CI test scenario specification.
    
    Attributes:
        id: Unique scenario identifier (e.g., "CORE-001")
        name: Human-readable scenario name
        description: What invariant is being tested
        packages_installed: List of packages to install for this test
        packages_excluded: List of packages explicitly NOT installed
        execution_mode: LIVE, TEST, or DEBUG
        user_tier: User subscription tier
        expected_outcome: Expected test result
        expected_error: Expected error type (if FAIL)
        remediation: How to fix if invariant violated
        category: Test category (core, connector, toolkit, integration)
    """
    id: str
    name: str
    description: str
    packages_installed: list[str]
    packages_excluded: list[str] = field(default_factory=list)
    execution_mode: str = "test"
    user_tier: str = "community"
    expected_outcome: ExpectedOutcome = ExpectedOutcome.PASS
    expected_error: str | None = None
    remediation: str = ""
    category: str = "core"
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for CI configuration."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "packages_installed": self.packages_installed,
            "packages_excluded": self.packages_excluded,
            "execution_mode": self.execution_mode,
            "user_tier": self.user_tier,
            "expected_outcome": self.expected_outcome.value,
            "expected_error": self.expected_error,
            "remediation": self.remediation,
            "category": self.category,
        }


# ════════════════════════════════════════════════════════════════════════════════
# CORE RUNTIME SCENARIOS
# Tests the krl-core package in isolation and with frameworks
# ════════════════════════════════════════════════════════════════════════════════

def get_core_scenarios() -> list[TestScenario]:
    """
    Core runtime test scenarios.
    
    These test that krl-core has zero domain logic dependencies.
    """
    return [
        # CORE-001: krl-core installs standalone
        TestScenario(
            id="CORE-001",
            name="Core Runtime Standalone Installation",
            description="krl-core must install without any domain packages",
            packages_installed=["krl-open-core", "krl-types"],
            packages_excluded=[
                "krl-data-connectors",
                "krl-causal-policy-toolkit",
                "krl-geospatial-tools",
                "krl-network-analysis",
                "krl-model-zoo",
                "krl-frameworks",
            ],
            execution_mode="test",
            expected_outcome=ExpectedOutcome.PASS,
            remediation="krl-core has forbidden domain dependencies",
            category="core",
        ),
        
        # CORE-002: ExecutionContext works without connectors
        TestScenario(
            id="CORE-002",
            name="ExecutionContext Without Connectors",
            description="ExecutionContext must initialize without krl-data-connectors",
            packages_installed=["krl-open-core", "krl-types", "krl-frameworks"],
            packages_excluded=["krl-data-connectors"],
            execution_mode="test",
            expected_outcome=ExpectedOutcome.PASS,
            remediation="ExecutionContext incorrectly depends on connectors",
            category="core",
        ),
        
        # CORE-003: BindingRegistry works without toolkits
        TestScenario(
            id="CORE-003",
            name="BindingRegistry Without Toolkits",
            description="BindingRegistry must initialize without any toolkit packages",
            packages_installed=["krl-open-core", "krl-types", "krl-frameworks"],
            packages_excluded=[
                "krl-causal-policy-toolkit",
                "krl-geospatial-tools",
                "krl-network-analysis",
            ],
            execution_mode="test",
            expected_outcome=ExpectedOutcome.PASS,
            remediation="BindingRegistry incorrectly depends on toolkits",
            category="core",
        ),
        
        # CORE-004: CapabilityDeclaration validation without bindings
        TestScenario(
            id="CORE-004",
            name="Capability Declaration Validates Without Bindings",
            description="CapabilityDeclaration.validate() must return errors, not raise, when bindings missing",
            packages_installed=["krl-open-core", "krl-types", "krl-frameworks"],
            packages_excluded=["krl-data-connectors"],
            execution_mode="test",
            expected_outcome=ExpectedOutcome.PASS,
            remediation="CapabilityDeclaration raises instead of returning errors",
            category="core",
        ),
    ]


# ════════════════════════════════════════════════════════════════════════════════
# CONNECTOR LAYER SCENARIOS
# Tests krl-data-connectors package isolation and tier enforcement
# ════════════════════════════════════════════════════════════════════════════════

def get_connector_scenarios() -> list[TestScenario]:
    """
    Connector layer test scenarios.
    
    These test connector tier enforcement and data isolation.
    """
    return [
        # CONN-001: Connectors install without frameworks
        TestScenario(
            id="CONN-001",
            name="Connectors Standalone Installation",
            description="krl-data-connectors must install without krl-frameworks",
            packages_installed=["krl-open-core", "krl-types", "krl-data-connectors"],
            packages_excluded=["krl-frameworks"],
            execution_mode="test",
            expected_outcome=ExpectedOutcome.PASS,
            remediation="krl-data-connectors has forbidden framework dependency",
            category="connector",
        ),
        
        # CONN-002: Connectors don't depend on toolkits
        TestScenario(
            id="CONN-002",
            name="Connectors Independent of Toolkits",
            description="krl-data-connectors must not import any toolkit packages",
            packages_installed=["krl-open-core", "krl-types", "krl-data-connectors"],
            packages_excluded=[
                "krl-causal-policy-toolkit",
                "krl-geospatial-tools",
                "krl-network-analysis",
            ],
            execution_mode="test",
            expected_outcome=ExpectedOutcome.PASS,
            remediation="krl-data-connectors incorrectly depends on toolkits",
            category="connector",
        ),
        
        # CONN-003: Community tier connectors work without API key
        TestScenario(
            id="CONN-003",
            name="Community Connector No API Key Required",
            description="Community tier connectors must work without API keys",
            packages_installed=["krl-open-core", "krl-types", "krl-data-connectors"],
            execution_mode="test",
            user_tier="community",
            expected_outcome=ExpectedOutcome.PASS,
            remediation="Community connectors incorrectly require API keys",
            category="connector",
        ),
        
        # CONN-004: Professional connector denied for community tier
        TestScenario(
            id="CONN-004",
            name="Professional Connector Tier Enforcement",
            description="Professional connectors must deny access to community tier",
            packages_installed=["krl-open-core", "krl-types", "krl-data-connectors"],
            execution_mode="test",
            user_tier="community",
            expected_outcome=ExpectedOutcome.FAIL,
            expected_error="TierAccessDeniedError",
            remediation="Tier enforcement not working for professional connectors",
            category="connector",
        ),
        
        # CONN-005: LIVE mode requires real connector configuration
        TestScenario(
            id="CONN-005",
            name="LIVE Mode Connector Configuration Required",
            description="LIVE mode must fail if connector not properly configured",
            packages_installed=["krl-open-core", "krl-types", "krl-data-connectors"],
            execution_mode="live",
            expected_outcome=ExpectedOutcome.FAIL,
            expected_error="MissingCapabilityError",
            remediation="LIVE mode allows unconfigured connectors",
            category="connector",
        ),
    ]


# ════════════════════════════════════════════════════════════════════════════════
# TOOLKIT LAYER SCENARIOS
# Tests toolkit packages for independence and correct capability binding
# ════════════════════════════════════════════════════════════════════════════════

def get_toolkit_scenarios() -> list[TestScenario]:
    """
    Toolkit layer test scenarios.
    
    These test toolkit isolation and method binding.
    """
    return [
        # TOOL-001: Causal toolkit installs without connectors
        TestScenario(
            id="TOOL-001",
            name="Causal Toolkit Standalone Installation",
            description="krl-causal-policy-toolkit must not depend on krl-data-connectors",
            packages_installed=["krl-open-core", "krl-types", "krl-causal-policy-toolkit"],
            packages_excluded=["krl-data-connectors"],
            execution_mode="test",
            expected_outcome=ExpectedOutcome.PASS,
            remediation="krl-causal-policy-toolkit has connector dependency",
            category="toolkit",
        ),
        
        # TOOL-002: Geospatial toolkit installs without connectors
        TestScenario(
            id="TOOL-002",
            name="Geospatial Toolkit Standalone Installation",
            description="krl-geospatial-tools must not depend on krl-data-connectors",
            packages_installed=["krl-open-core", "krl-types", "krl-geospatial-tools"],
            packages_excluded=["krl-data-connectors"],
            execution_mode="test",
            expected_outcome=ExpectedOutcome.PASS,
            remediation="krl-geospatial-tools has connector dependency",
            category="toolkit",
        ),
        
        # TOOL-003: Toolkits don't depend on frameworks
        TestScenario(
            id="TOOL-003",
            name="Toolkits Independent of Frameworks",
            description="No toolkit may import krl-frameworks",
            packages_installed=[
                "krl-open-core",
                "krl-types",
                "krl-causal-policy-toolkit",
                "krl-geospatial-tools",
                "krl-network-analysis",
            ],
            packages_excluded=["krl-frameworks"],
            execution_mode="test",
            expected_outcome=ExpectedOutcome.PASS,
            remediation="Toolkit incorrectly depends on krl-frameworks",
            category="toolkit",
        ),
        
        # TOOL-004: DiD method binding works in isolation
        TestScenario(
            id="TOOL-004",
            name="DiD Method Binding Isolation",
            description="Difference-in-Differences must work without other toolkits",
            packages_installed=["krl-open-core", "krl-types", "krl-causal-policy-toolkit"],
            packages_excluded=["krl-geospatial-tools", "krl-network-analysis"],
            execution_mode="test",
            expected_outcome=ExpectedOutcome.PASS,
            remediation="DiD has hidden cross-toolkit dependencies",
            category="toolkit",
        ),
    ]


# ════════════════════════════════════════════════════════════════════════════════
# MODEL ZOO SCENARIOS
# Tests krl-model-zoo tier isolation and model loading
# ════════════════════════════════════════════════════════════════════════════════

def get_model_zoo_scenarios() -> list[TestScenario]:
    """
    Model Zoo isolation and tier enforcement test scenarios.
    
    These test model loading, tier gating, and package independence.
    Unified krl-model-zoo has three tiers:
      - community: vision, nlp, time_series, audio, multimodal
      - professional: econometric, bayesian, causal, clustering, regression, etc.
      - enterprise: neural, hybrid, advanced, ensemble
    """
    return [
        # ZOO-001: Model Zoo installs without connectors
        TestScenario(
            id="ZOO-001",
            name="Model Zoo Standalone Installation",
            description="krl-model-zoo must not depend on krl-data-connectors",
            packages_installed=["krl-open-core", "krl-types", "krl-model-zoo"],
            packages_excluded=["krl-data-connectors"],
            execution_mode="test",
            expected_outcome=ExpectedOutcome.PASS,
            remediation="krl-model-zoo incorrectly depends on connectors",
            category="model_zoo",
        ),
        
        # ZOO-002: Model Zoo installs without toolkits
        TestScenario(
            id="ZOO-002",
            name="Model Zoo Independent of Toolkits",
            description="krl-model-zoo must not depend on any toolkit packages",
            packages_installed=["krl-open-core", "krl-types", "krl-model-zoo"],
            packages_excluded=[
                "krl-causal-policy-toolkit",
                "krl-geospatial-tools",
                "krl-network-analysis",
            ],
            execution_mode="test",
            expected_outcome=ExpectedOutcome.PASS,
            remediation="krl-model-zoo incorrectly depends on toolkits",
            category="model_zoo",
        ),
        
        # ZOO-003: Model Zoo doesn't depend on frameworks
        TestScenario(
            id="ZOO-003",
            name="Model Zoo Independent of Frameworks",
            description="krl-model-zoo must not import krl-frameworks",
            packages_installed=["krl-open-core", "krl-types", "krl-model-zoo"],
            packages_excluded=["krl-frameworks"],
            execution_mode="test",
            expected_outcome=ExpectedOutcome.PASS,
            remediation="krl-model-zoo incorrectly depends on krl-frameworks",
            category="model_zoo",
        ),
        
        # ZOO-004: Community tier models work for community users
        TestScenario(
            id="ZOO-004",
            name="Community Model Access - Allowed",
            description="Community tier models must be accessible to community users",
            packages_installed=["krl-open-core", "krl-types", "krl-model-zoo"],
            execution_mode="test",
            user_tier="community",
            expected_outcome=ExpectedOutcome.PASS,
            remediation="Community models incorrectly restricted",
            category="model_zoo",
        ),
        
        # ZOO-005: Professional tier models denied for community users
        TestScenario(
            id="ZOO-005",
            name="Professional Model Tier Enforcement",
            description="Professional tier models must deny access to community users",
            packages_installed=["krl-open-core", "krl-types", "krl-model-zoo[professional]"],
            execution_mode="test",
            user_tier="community",
            expected_outcome=ExpectedOutcome.FAIL,
            expected_error="TierAccessDeniedError",
            remediation="Tier enforcement not working for professional models",
            category="model_zoo",
        ),
        
        # ZOO-006: Enterprise tier models denied for professional users
        TestScenario(
            id="ZOO-006",
            name="Enterprise Model Tier Enforcement",
            description="Enterprise tier models must deny access to professional users",
            packages_installed=["krl-open-core", "krl-types", "krl-model-zoo[enterprise]"],
            execution_mode="test",
            user_tier="professional",
            expected_outcome=ExpectedOutcome.FAIL,
            expected_error="TierAccessDeniedError",
            remediation="Tier enforcement not working for enterprise models",
            category="model_zoo",
        ),
        
        # ZOO-007: RESNET50 (community vision) loads in TEST mode
        TestScenario(
            id="ZOO-007",
            name="Community Vision Model Loading",
            description="RESNET50 must load correctly in TEST mode",
            packages_installed=["krl-open-core", "krl-types", "krl-model-zoo"],
            execution_mode="test",
            user_tier="community",
            expected_outcome=ExpectedOutcome.PASS,
            remediation="RESNET50 model fails to load",
            category="model_zoo",
        ),
        
        # ZOO-008: GARCH (professional econometric) loads for professional tier
        TestScenario(
            id="ZOO-008",
            name="Professional Econometric Model Loading",
            description="GARCH must load correctly for professional tier users",
            packages_installed=["krl-open-core", "krl-types", "krl-model-zoo[professional]"],
            execution_mode="test",
            user_tier="professional",
            expected_outcome=ExpectedOutcome.PASS,
            remediation="GARCH model fails to load for professional users",
            category="model_zoo",
        ),
        
        # ZOO-009: TRANSFORMER_XL (enterprise neural) loads for enterprise tier
        TestScenario(
            id="ZOO-009",
            name="Enterprise Neural Model Loading",
            description="TRANSFORMER_XL must load correctly for enterprise tier users",
            packages_installed=["krl-open-core", "krl-types", "krl-model-zoo[enterprise]"],
            execution_mode="test",
            user_tier="enterprise",
            expected_outcome=ExpectedOutcome.PASS,
            remediation="TRANSFORMER_XL model fails to load for enterprise users",
            category="model_zoo",
        ),
        
        # ZOO-010: LIVE mode requires model validation
        TestScenario(
            id="ZOO-010",
            name="LIVE Mode Model Validation Required",
            description="LIVE mode must validate model integrity before loading",
            packages_installed=["krl-open-core", "krl-types", "krl-model-zoo"],
            execution_mode="live",
            expected_outcome=ExpectedOutcome.PASS,
            remediation="Model validation not enforced in LIVE mode",
            category="model_zoo",
        ),
        
        # ZOO-011: Corrupted model rejected in LIVE mode
        TestScenario(
            id="ZOO-011",
            name="Corrupted Model Rejection (LIVE mode)",
            description="LIVE mode must reject models that fail integrity checks",
            packages_installed=["krl-open-core", "krl-types", "krl-model-zoo"],
            execution_mode="live",
            expected_outcome=ExpectedOutcome.FAIL,
            expected_error="ModelIntegrityError",
            remediation="LIVE mode allows corrupted models",
            category="model_zoo",
        ),
        
        # ZOO-012: Model binding resolution works without framework
        TestScenario(
            id="ZOO-012",
            name="Model Binding Standalone Resolution",
            description="Model bindings must resolve without krl-frameworks present",
            packages_installed=["krl-open-core", "krl-types", "krl-model-zoo"],
            packages_excluded=["krl-frameworks"],
            execution_mode="test",
            expected_outcome=ExpectedOutcome.PASS,
            remediation="Model binding requires framework - violates isolation",
            category="model_zoo",
        ),
    ]


# ════════════════════════════════════════════════════════════════════════════════
# FRAMEWORK INTEGRATION SCENARIOS
# Tests krl-frameworks with various package combinations
# ════════════════════════════════════════════════════════════════════════════════

def get_integration_scenarios() -> list[TestScenario]:
    """
    Framework integration test scenarios.
    
    These test the framework layer's handling of missing/present packages.
    """
    return [
        # INTEG-001: Framework without connectors in TEST mode
        TestScenario(
            id="INTEG-001",
            name="Framework Without Connectors (TEST mode)",
            description="krl-frameworks must degrade gracefully without connectors in TEST mode",
            packages_installed=["krl-open-core", "krl-types", "krl-frameworks"],
            packages_excluded=["krl-data-connectors"],
            execution_mode="test",
            expected_outcome=ExpectedOutcome.WARN,
            remediation="Framework should warn but continue in TEST mode",
            category="integration",
        ),
        
        # INTEG-002: Framework without connectors in LIVE mode
        TestScenario(
            id="INTEG-002",
            name="Framework Without Connectors (LIVE mode) - MUST FAIL",
            description="krl-frameworks MUST fail hard without connectors in LIVE mode",
            packages_installed=["krl-open-core", "krl-types", "krl-frameworks"],
            packages_excluded=["krl-data-connectors"],
            execution_mode="live",
            expected_outcome=ExpectedOutcome.FAIL,
            expected_error="MissingCapabilityError",
            remediation="LIVE mode incorrectly permits missing connectors",
            category="integration",
        ),
        
        # INTEG-003: Framework without toolkits in TEST mode
        TestScenario(
            id="INTEG-003",
            name="Framework Without Toolkits (TEST mode)",
            description="Frameworks not requiring toolkits must work without them",
            packages_installed=[
                "krl-open-core",
                "krl-types",
                "krl-frameworks",
                "krl-data-connectors",
            ],
            packages_excluded=[
                "krl-causal-policy-toolkit",
                "krl-geospatial-tools",
                "krl-network-analysis",
            ],
            execution_mode="test",
            expected_outcome=ExpectedOutcome.PASS,
            remediation="Framework incorrectly requires all toolkits",
            category="integration",
        ),
        
        # INTEG-004: MPIFramework with complete dependencies
        TestScenario(
            id="INTEG-004",
            name="MPIFramework Full Dependency Stack",
            description="MPIFramework with all required data domains must work",
            packages_installed=[
                "krl-open-core",
                "krl-types",
                "krl-frameworks",
                "krl-data-connectors",
            ],
            execution_mode="test",
            expected_outcome=ExpectedOutcome.PASS,
            remediation="MPIFramework fails with complete dependencies",
            category="integration",
        ),
        
        # INTEG-005: DiDFramework requires causal toolkit
        TestScenario(
            id="INTEG-005",
            name="DiDFramework Toolkit Requirement",
            description="DiDFramework must require krl-causal-policy-toolkit",
            packages_installed=[
                "krl-open-core",
                "krl-types",
                "krl-frameworks",
                "krl-data-connectors",
            ],
            packages_excluded=["krl-causal-policy-toolkit"],
            execution_mode="live",
            expected_outcome=ExpectedOutcome.FAIL,
            expected_error="MissingCapabilityError",
            remediation="DiDFramework does not require causal toolkit",
            category="integration",
        ),
        
        # INTEG-006: Version skew detection
        TestScenario(
            id="INTEG-006",
            name="Version Skew Detection",
            description="Incompatible package versions must be detected at startup",
            packages_installed=[
                "krl-open-core>=0.2.0",
                "krl-types>=0.2.0",
                "krl-frameworks>=0.1.0",
                "krl-data-connectors==0.1.0",  # Deliberately old version
            ],
            execution_mode="live",
            expected_outcome=ExpectedOutcome.FAIL,
            expected_error="PackageVersionIncompatibleError",
            remediation="Version skew not detected between packages",
            category="integration",
        ),
        
        # INTEG-007: Capability schema backward compatibility
        TestScenario(
            id="INTEG-007",
            name="Capability Schema Backward Compatibility",
            description="New framework version must accept old capability declarations",
            packages_installed=[
                "krl-open-core",
                "krl-types",
                "krl-frameworks",
            ],
            execution_mode="test",
            expected_outcome=ExpectedOutcome.PASS,
            remediation="Capability schema broke backward compatibility",
            category="integration",
        ),
        
        # INTEG-008: Production environment forces LIVE mode
        TestScenario(
            id="INTEG-008",
            name="Production Environment LIVE Mode Enforcement",
            description="Production environment must reject non-LIVE execution",
            packages_installed=[
                "krl-open-core",
                "krl-types",
                "krl-frameworks",
            ],
            execution_mode="test",  # Attempting TEST in production
            expected_outcome=ExpectedOutcome.FAIL,
            expected_error="ProductionViolationError",
            remediation="Production guard not enforcing LIVE mode",
            category="integration",
        ),
    ]


# ════════════════════════════════════════════════════════════════════════════════
# CI MATRIX BUILDER
# ════════════════════════════════════════════════════════════════════════════════

class CIMatrix:
    """
    CI test matrix builder for GitHub Actions.
    
    Generates matrix configurations for comprehensive ecosystem testing.
    """
    
    @staticmethod
    def get_all_scenarios() -> list[TestScenario]:
        """Get all test scenarios across all categories."""
        return (
            get_core_scenarios()
            + get_connector_scenarios()
            + get_toolkit_scenarios()
            + get_model_zoo_scenarios()
            + get_integration_scenarios()
        )
    
    @staticmethod
    def to_github_matrix() -> dict[str, Any]:
        """
        Generate GitHub Actions matrix configuration.
        
        Returns a matrix that can be used with:
        strategy:
          matrix: ${{ fromJson(needs.generate-matrix.outputs.matrix) }}
        """
        scenarios = CIMatrix.get_all_scenarios()
        
        return {
            "include": [
                {
                    "scenario_id": s.id,
                    "scenario_name": s.name,
                    "packages": " ".join(s.packages_installed),
                    "excluded_packages": " ".join(s.packages_excluded),
                    "execution_mode": s.execution_mode,
                    "user_tier": s.user_tier,
                    "expected_outcome": s.expected_outcome.value,
                    "expected_error": s.expected_error or "",
                    "category": s.category,
                }
                for s in scenarios
            ]
        }
    
    @staticmethod
    def get_failure_mode_table() -> list[dict[str, str]]:
        """
        Generate failure mode table for documentation.
        
        Returns a table of all expected failures with remediation.
        """
        scenarios = CIMatrix.get_all_scenarios()
        failures = [s for s in scenarios if s.expected_outcome == ExpectedOutcome.FAIL]
        
        return [
            {
                "scenario": f.id,
                "invariant": f.description,
                "expected_error": f.expected_error or "N/A",
                "remediation": f.remediation,
            }
            for f in failures
        ]


# ════════════════════════════════════════════════════════════════════════════════
# FAILURE MODE REFERENCE TABLE
# ════════════════════════════════════════════════════════════════════════════════

FAILURE_MODES = """
┌───────────────┬──────────────────────────────────────────┬─────────────────────────────────────────────┐
│ Failure Mode  │ Trigger Condition                        │ Resolution Action                           │
├───────────────┼──────────────────────────────────────────┼─────────────────────────────────────────────┤
│ PACKAGE_NOT   │ Required package not installed           │ pip install <package>                       │
│ _INSTALLED    │                                          │                                             │
├───────────────┼──────────────────────────────────────────┼─────────────────────────────────────────────┤
│ VERSION_SKEW  │ Installed version < minimum required     │ pip install '<package>>=<min_version>'      │
├───────────────┼──────────────────────────────────────────┼─────────────────────────────────────────────┤
│ BINDING_NOT   │ Package installed but method missing     │ Check package version, may need upgrade     │
│ _FOUND        │                                          │                                             │
├───────────────┼──────────────────────────────────────────┼─────────────────────────────────────────────┤
│ IMPORT_ERROR  │ Package installed but fails to import    │ Check dependencies, reinstall package       │
├───────────────┼──────────────────────────────────────────┼─────────────────────────────────────────────┤
│ MODE_VIOLATION│ Non-LIVE mode in production              │ Set EXECUTION_MODE=live                     │
├───────────────┼──────────────────────────────────────────┼─────────────────────────────────────────────┤
│ TIER_DENIED   │ User tier < required tier                │ Upgrade subscription tier                   │
├───────────────┼──────────────────────────────────────────┼─────────────────────────────────────────────┤
│ MISSING_API   │ API key required but not set             │ Set API key in environment/config           │
│ _KEY          │                                          │                                             │
├───────────────┼──────────────────────────────────────────┼─────────────────────────────────────────────┤
│ CIRCULAR_DEP  │ Package A imports B imports A            │ Architecture violation - fix dependency     │
├───────────────┼──────────────────────────────────────────┼─────────────────────────────────────────────┤
│ PRODUCTION    │ Production detected but LIVE not forced  │ Constitutional failure - fix ProductionGuard│
│ _VIOLATION    │                                          │                                             │
└───────────────┴──────────────────────────────────────────┴─────────────────────────────────────────────┘
"""
