# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Layer 6: Meta / Peer Frameworks
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Layer 6: Meta and Peer Frameworks.

This layer contains orchestration meta-frameworks that coordinate
and compose outputs from frameworks across all other layers:

Community Tier:
    - HDIMPIDashboardFramework: Development indicator dashboards
    - SPIPolicyStackFramework: Social Progress simulation stacks
    - IOTablesFramework: Input-Output economic tables

Professional Tier:
    - IAMPolicyStackFramework: IAM + Policy simulation stacks
    - FrameworkOrchestrator: Pipeline orchestration
    - ABMFramework: Generic Agent-Based Model meta-framework
    - CGEFramework: Computable General Equilibrium meta-framework

Enterprise Tier (Framework Orchestration):
    - REMSOMFramework: Regional Economic Multisectoral Open Model
    - CompositionEngine: Cross-layer composition patterns
"""

from krl_frameworks.layers.meta.remsom import REMSOMFramework
from krl_frameworks.layers.meta.remsomV2 import (
    REMSOMFramework as REMSOMFrameworkV2,
    REMSOMConfig as REMSOMConfigV2,
    REMSOMStack,
    OpportunityDomain,
    OpportunityScore,
    SpatialStructure,
    CausalEstimate,
    MobilityTrajectory,
    PolicyScenario,
    REMSOMAnalysisResult,
    CobbDouglasDynamicsConfig,
    CobbDouglasMobilityEngine,
    SpatialWeightsBuilder,
    SpatialWeightsResult,
)
from krl_frameworks.layers.meta.advanced import (
    IAMPolicyStackFramework,
    HDIMPIDashboardFramework,
    SPIPolicyStackFramework,
)
from krl_frameworks.layers.meta.io_tables import IOTablesFramework
from krl_frameworks.layers.meta.orchestrator import FrameworkOrchestrator
from krl_frameworks.layers.meta.composition import CompositionEngine
from krl_frameworks.layers.meta.abm import ABMFramework
from krl_frameworks.layers.meta.cge import CGEFramework

__all__ = [
    # Community Tier
    "HDIMPIDashboardFramework",
    "SPIPolicyStackFramework",
    "IOTablesFramework",
    # Professional Tier
    "IAMPolicyStackFramework",
    "FrameworkOrchestrator",
    "ABMFramework",
    "CGEFramework",
    # Enterprise Tier - REMSOM v1 (legacy)
    "REMSOMFramework",
    "CompositionEngine",
    # Enterprise Tier - REMSOM v2 (observatory architecture)
    "REMSOMFrameworkV2",
    "REMSOMConfigV2",
    "REMSOMStack",
    "OpportunityDomain",
    "OpportunityScore",
    "SpatialStructure",
    "CausalEstimate",
    "MobilityTrajectory",
    "PolicyScenario",
    "REMSOMAnalysisResult",
    # REMSOM v2 Dynamics
    "CobbDouglasDynamicsConfig",
    "CobbDouglasMobilityEngine",
    "SpatialWeightsBuilder",
    "SpatialWeightsResult",
]
