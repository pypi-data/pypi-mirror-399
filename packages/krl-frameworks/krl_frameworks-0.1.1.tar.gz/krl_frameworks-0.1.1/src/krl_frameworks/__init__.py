# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Enterprise Meta-Framework Orchestration Platform
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
KRL Frameworks: Enterprise-grade meta-framework orchestration platform
for socioeconomic analysis with deterministic CBSS pipelines.

This package provides a unified orchestration layer for 25+ socioeconomic
meta-frameworks across 6 vertical layers:

    Layer 1: Socioeconomic/Academic (MPI, HDI, SPI, IAMs, SAM-CGE)
    Layer 2: Government/Policy (Resilience Dashboards, Interagency Tools)
    Layer 3: Experimental/Research (Spatial Causal, SD-ABM Hybrids)
    Layer 4: Financial/Economic (Macro-Financial CGE, Risk Indices)
    Layer 5: Arts/Media/Entertainment (Cultural CGE, Media Impact)
    Layer 6: Meta/Peer Frameworks (REMSOM, IAM-Policy Stacks)

Key Features:
    - Deterministic CBSS Execution: Cohort-Based State Simulation
    - DAG Orchestration: Cross-layer causal graph composition
    - Peer Architecture: All meta-frameworks operate as equals
    - Tier Gating: Community/Professional/Enterprise access control
    - Audit-Ready: Versioned snapshots, reproducible pipelines

Quick Start:
    >>> from krl_frameworks import (
    ...     FrameworkRegistry,
    ...     CohortStateVector,
    ...     DataBundle,
    ... )
    >>> from krl_frameworks.layers.socioeconomic import MPIFramework
    >>>
    >>> # Create data bundle
    >>> bundle = DataBundle.from_dataframes({
    ...     "health": health_df,
    ...     "education": edu_df,
    ...     "income": income_df,
    ... })
    >>>
    >>> # Initialize and execute framework
    >>> mpi = MPIFramework()
    >>> mpi.fit(bundle)
    >>> result = mpi.simulate(steps=10)
    >>>
    >>> # Access results
    >>> print(result.metrics["mpi"])
    >>> print(result.state.deprivation_vector)

For more information, see: https://docs.krlabs.dev/frameworks
"""

from krl_frameworks.__version__ import __version__, __version_info__

# ════════════════════════════════════════════════════════════════════════════════
# Core Abstractions
# ════════════════════════════════════════════════════════════════════════════════

from krl_frameworks.core import (
    # Base framework
    BaseMetaFramework,
    FrameworkExecutionResult,
    FrameworkMetadata,
    VerticalLayer,
    # Configuration
    AggregationMethod,
    ConvergenceMethod,
    FrameworkConfig,
    SimulationConfig,
    # State
    CohortStateVector,
    FloatArray,
    StateTrajectory,
    # Data
    DataBundle,
    DataDomain,
    DomainData,
    # Registry
    FrameworkRegistry,
    RegistryEntry,
    get_framework,
    get_global_registry,
    register_framework,
    # Tier
    Tier,
    TierAccessEvent,
    TierContext,
    check_tier_access,
    get_current_tier,
    requires_tier,
    set_current_tier,
    tier_gate,
    tier_protected_class,
    # Exceptions
    ConfigurationError,
    DAGError,
    DataBundleValidationError,
    ExecutionError,
    FrameworkException,
    FrameworkNotFoundError,
    SimulationError,
    StateValidationError,
    TierAccessError,
    ValidationError,
)

# ════════════════════════════════════════════════════════════════════════════════
# Simulation Engine
# ════════════════════════════════════════════════════════════════════════════════

from krl_frameworks.simulation import (
    # CBSS Core
    CBSSEngine,
    ConvergenceChecker,
    CompositeTransition,
    IdentityTransition,
    LinearDecayTransition,
    PolicyShock,
    PolicyShockEngine,
    SimulationResult,
    TransitionFunction,
    # Advanced Transitions
    MarkovTransition,
    MarkovConfig,
    TransitionType,
    NeuralTransition,
    NeuralConfig,
    ActivationFn,
    EnsembleTransition,
    EnsembleConfig,
    EnsembleMethod,
    LinearTransition,
)

# ════════════════════════════════════════════════════════════════════════════════
# DAG Orchestration
# ════════════════════════════════════════════════════════════════════════════════

from krl_frameworks.dag import (
    DAGEdge,
    DAGNode,
    DataFlowMapper,
    ExecutionResult,
    ExecutionStatus,
    FrameworkDAG,
    PipelineBuilder,
    TopologicalExecutor,
)

# ════════════════════════════════════════════════════════════════════════════════
# Layer Frameworks
# ════════════════════════════════════════════════════════════════════════════════

from krl_frameworks.layers import (
    # Layer 1: Socioeconomic
    HDIFramework,
    MPIFramework,
    SPIFramework,
    # Layer 2: Government
    CBOScoringFramework,
    OMBPartFramework,
    GAOGpraFramework,
    # Layer 3: Experimental
    RCTFramework,
    DiDFramework,
    SyntheticControlFramework,
    # Layer 4: Financial
    BaselIIIFramework,
    CECLFramework,
    StressTestFramework,
    # Layer 5: Arts & Media
    CulturalImpactFramework,
    MediaReachFramework,
    CreativeEconomyFramework,
    # Layer 6: Meta
    REMSOMFramework,
)

# ════════════════════════════════════════════════════════════════════════════════
# Package Metadata
# ════════════════════════════════════════════════════════════════════════════════

__author__ = "Khipu Research Labs"
__email__ = "engineering@krlabs.dev"
__license__ = "Apache-2.0"

# ════════════════════════════════════════════════════════════════════════════════
# Public API
# ════════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Version
    "__version__",
    "__version_info__",
    # Base framework
    "BaseMetaFramework",
    "FrameworkMetadata",
    "FrameworkExecutionResult",
    "VerticalLayer",
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
    "check_tier_access",
    "tier_gate",
    # Simulation Engine
    "CBSSEngine",
    "TransitionFunction",
    "CompositeTransition",
    "IdentityTransition",
    "LinearDecayTransition",
    "PolicyShock",
    "PolicyShockEngine",
    "SimulationResult",
    "ConvergenceChecker",
    # Advanced Transitions
    "MarkovTransition",
    "MarkovConfig",
    "TransitionType",
    "NeuralTransition",
    "NeuralConfig",
    "ActivationFn",
    "EnsembleTransition",
    "EnsembleConfig",
    "EnsembleMethod",
    "LinearTransition",
    # DAG Orchestration
    "FrameworkDAG",
    "DAGNode",
    "DAGEdge",
    "TopologicalExecutor",
    "PipelineBuilder",
    "DataFlowMapper",
    "ExecutionResult",
    "ExecutionStatus",
    # Layer 1 Frameworks
    "MPIFramework",
    "HDIFramework",
    "SPIFramework",
    # Layer 2 Frameworks
    "CBOScoringFramework",
    "OMBPartFramework",
    "GAOGpraFramework",
    # Layer 3 Frameworks
    "RCTFramework",
    "DiDFramework",
    "SyntheticControlFramework",
    # Layer 4 Frameworks
    "BaselIIIFramework",
    "CECLFramework",
    "StressTestFramework",
    # Layer 5 Frameworks
    "CulturalImpactFramework",
    "MediaReachFramework",
    "CreativeEconomyFramework",
    # Layer 6 Frameworks
    "REMSOMFramework",
    # Exceptions (commonly used)
    "FrameworkException",
    "TierAccessError",
    "ValidationError",
    "DataBundleValidationError",
    "StateValidationError",
    "ConfigurationError",
    "ExecutionError",
    "SimulationError",
    "DAGError",
    "FrameworkNotFoundError",
]

