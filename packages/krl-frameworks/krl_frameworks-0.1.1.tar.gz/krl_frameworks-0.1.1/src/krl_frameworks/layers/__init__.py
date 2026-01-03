# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Vertical Layer Implementations
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Framework implementations organized by vertical layer.

28 Meta-Frameworks across 6 Vertical Layers:

    Layer 1 - Socioeconomic / Academic (8):
        MPI, HDI, SPI, IAM (DICE/GCAM), SAM-CGE, SAM-CGE-Poverty,
        CGE-Microsim, Spatial-Causal-Index
        
    Layer 2 - Government / Policy (6):
        CBO Scoring, OMB PART, GAO GPRA, MPI Operational,
        City/State Resilience, Interagency Spatial Causal
        
    Layer 3 - Experimental / Research (6):
        RCT, Difference-in-Differences, Synthetic Control,
        Spatial Causal (GCCM), SD-ABM Hybrids, Multilayer Network
        
    Layer 4 - Financial / Economic (8):
        Basel III, CECL, Stress Testing, Macro-Financial CGE,
        Networked Financial, Risk Indices, Composite Risk, Financial Meta-Orchestrator
        
    Layer 5 - Arts / Media / Entertainment (8):
        Cultural Impact, Media Reach, Creative Economy, Cultural CGE,
        Audience ABM, Cultural Equity, Media Impact, Integrated Cultural
        
    Layer 6 - Meta / Peer (4):
        REMSOM, IAM-Policy-Stack, HDI/MPI Dashboard, SPI Policy Stack
"""

# Layer 1: Socioeconomic
from krl_frameworks.layers.socioeconomic import (
    HDIFramework,
    MPIFramework,
    SPIFramework,
    IAMFramework,
    SAMCGEFramework,
    SAMCGEPovertyFramework,
    CGEMicrosimFramework,
    SpatialCausalIndexFramework,
)

# Layer 2: Government
from krl_frameworks.layers.government import (
    CBOScoringFramework,
    OMBPartFramework,
    GAOGpraFramework,
    MPIOperationalFramework,
    CityResilienceFramework,
    InteragencySpatialCausalFramework,
)

# Layer 3: Experimental
from krl_frameworks.layers.experimental import (
    RCTFramework,
    DiDFramework,
    SyntheticControlFramework,
    SpatialCausalFramework,
    SDABMFramework,
    MultilayerNetworkFramework,
)

# Layer 4: Financial
from krl_frameworks.layers.financial import (
    BaselIIIFramework,
    CECLFramework,
    StressTestFramework,
    MacroFinancialCGEFramework,
    NetworkedFinancialFramework,
    RiskIndicesFramework,
    CompositeRiskFramework,
    FinancialMetaOrchestratorFramework,
)

# Layer 5: Arts & Media
from krl_frameworks.layers.arts_media import (
    CulturalImpactFramework,
    MediaReachFramework,
    CreativeEconomyFramework,
    CulturalCGEFramework,
    AudienceABMFramework,
    CulturalEquityFramework,
    MediaImpactFramework,
    IntegratedCulturalFramework,
)

# Layer 6: Meta
from krl_frameworks.layers.meta import (
    REMSOMFramework,
    REMSOMFrameworkV2,
    IAMPolicyStackFramework,
    HDIMPIDashboardFramework,
    SPIPolicyStackFramework,
)

__all__ = [
    # Layer 1: Socioeconomic (5 implemented, 3 TODO)
    "MPIFramework",
    "HDIFramework",
    "SPIFramework",
    "IAMFramework",
    "SAMCGEFramework",
    "SAMCGEPovertyFramework",
    "CGEMicrosimFramework",
    "SpatialCausalIndexFramework",
    # Layer 2: Government (6)
    "CBOScoringFramework",
    "OMBPartFramework",
    "GAOGpraFramework",
    "MPIOperationalFramework",
    "CityResilienceFramework",
    "InteragencySpatialCausalFramework",
    # Layer 3: Experimental (6)
    "RCTFramework",
    "DiDFramework",
    "SyntheticControlFramework",
    "SpatialCausalFramework",
    "SDABMFramework",
    "MultilayerNetworkFramework",
    # Layer 4: Financial (8)
    "BaselIIIFramework",
    "CECLFramework",
    "StressTestFramework",
    "MacroFinancialCGEFramework",
    "NetworkedFinancialFramework",
    "RiskIndicesFramework",
    "CompositeRiskFramework",
    "FinancialMetaOrchestratorFramework",
    # Layer 5: Arts & Media (8)
    "CulturalImpactFramework",
    "MediaReachFramework",
    "CreativeEconomyFramework",
    "CulturalCGEFramework",
    "AudienceABMFramework",
    "CulturalEquityFramework",
    "MediaImpactFramework",
    "IntegratedCulturalFramework",
    # Layer 6: Meta (5 - includes v1 for backward compat, v2 is primary)
    "REMSOMFramework",
    "REMSOMFrameworkV2",
    "IAMPolicyStackFramework",
    "HDIMPIDashboardFramework",
    "SPIPolicyStackFramework",
]


# ════════════════════════════════════════════════════════════════════════════════
# Auto-Registration
# ════════════════════════════════════════════════════════════════════════════════

def _register_all_frameworks() -> None:
    """Register all framework classes with the global registry."""
    from krl_frameworks.core.registry import get_global_registry
    
    registry = get_global_registry()
    
    # All framework classes to register
    frameworks = [
        # Layer 1: Socioeconomic
        MPIFramework,
        HDIFramework,
        SPIFramework,
        IAMFramework,
        SAMCGEFramework,
        SAMCGEPovertyFramework,
        CGEMicrosimFramework,
        SpatialCausalIndexFramework,
        # Layer 2: Government
        CBOScoringFramework,
        OMBPartFramework,
        GAOGpraFramework,
        MPIOperationalFramework,
        CityResilienceFramework,
        InteragencySpatialCausalFramework,
        # Layer 3: Experimental
        RCTFramework,
        DiDFramework,
        SyntheticControlFramework,
        SpatialCausalFramework,
        SDABMFramework,
        MultilayerNetworkFramework,
        # Layer 4: Financial
        BaselIIIFramework,
        CECLFramework,
        StressTestFramework,
        MacroFinancialCGEFramework,
        NetworkedFinancialFramework,
        RiskIndicesFramework,
        CompositeRiskFramework,
        FinancialMetaOrchestratorFramework,
        # Layer 5: Arts & Media
        CulturalImpactFramework,
        MediaReachFramework,
        CreativeEconomyFramework,
        CulturalCGEFramework,
        AudienceABMFramework,
        CulturalEquityFramework,
        MediaImpactFramework,
        IntegratedCulturalFramework,
        # Layer 6: Meta (REMSOMFrameworkV2 replaces legacy REMSOMFramework)
        REMSOMFrameworkV2,
        IAMPolicyStackFramework,
        HDIMPIDashboardFramework,
        SPIPolicyStackFramework,
    ]
    
    for fw_class in frameworks:
        try:
            # Frameworks use metadata() classmethod, but registry expects METADATA attr
            # Dynamically add METADATA from the classmethod if not present
            if not hasattr(fw_class, "METADATA") and hasattr(fw_class, "metadata"):
                fw_class.METADATA = fw_class.metadata()
            
            slug = fw_class.METADATA.slug if hasattr(fw_class, "METADATA") else None
            if slug and not registry.has(slug):
                registry.register(fw_class)
        except Exception as e:
            # Skip frameworks that fail to register (e.g., missing metadata)
            import logging
            logging.getLogger(__name__).debug(f"Failed to register {fw_class.__name__}: {e}")


# Auto-register on import
_register_all_frameworks()
