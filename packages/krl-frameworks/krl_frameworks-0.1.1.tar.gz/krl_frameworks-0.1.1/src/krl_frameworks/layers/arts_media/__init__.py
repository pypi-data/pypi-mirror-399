# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Arts & Media Layer
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Layer 5: Arts & Media Frameworks.

Impact assessment frameworks for cultural and creative sectors:

Community Tier:
    - CulturalImpactFramework: Cultural impact analysis
    - MediaReachFramework: Media reach and influence
    - CreativeEconomyFramework: Creative economy measurement
    - CulturalCGEFramework: Cultural economics with CGE
    - AudienceABMFramework: Agent-based audience simulation

Professional Tier:
    - CulturalEquityFramework: Cultural opportunity/equity indices
    - MediaImpactFramework: Media impact for press & streaming
    - IntegratedCulturalFramework: Experimental integrated ecosystem
    - ContentValuationFramework: Content lifecycle and asset valuation
    - IPValuationFramework: Intellectual property valuation
    - PlatformEconomicsFramework: Two-sided market and platform economics
"""

from krl_frameworks.layers.arts_media.cultural_impact import (
    CulturalImpactFramework,
    CulturalImpactConfig,
    CulturalImpactMetrics,
    CulturalDimension,
    ImpactScore,
)
from krl_frameworks.layers.arts_media.media_reach import (
    MediaReachFramework,
    MediaReachConfig,
    MediaReachMetrics,
    MediaChannel,
    AudienceMetrics,
)
from krl_frameworks.layers.arts_media.creative_economy import (
    CreativeEconomyFramework,
    CreativeEconomyConfig,
    CreativeEconomyMetrics,
    CreativeSector,
    EconomicMultipliers,
)
from krl_frameworks.layers.arts_media.advanced import (
    CulturalCGEFramework,
    AudienceABMFramework,
    CulturalEquityFramework,
    MediaImpactFramework,
    IntegratedCulturalFramework,
)
from krl_frameworks.layers.arts_media.content_valuation import ContentValuationFramework
from krl_frameworks.layers.arts_media.ip_valuation import IPValuationFramework
from krl_frameworks.layers.arts_media.platform_economics import PlatformEconomicsFramework

__all__ = [
    # Cultural Impact
    "CulturalImpactFramework",
    "CulturalImpactConfig",
    "CulturalImpactMetrics",
    "CulturalDimension",
    "ImpactScore",
    # Media Reach
    "MediaReachFramework",
    "MediaReachConfig",
    "MediaReachMetrics",
    "MediaChannel",
    "AudienceMetrics",
    # Creative Economy
    "CreativeEconomyFramework",
    "CreativeEconomyConfig",
    "CreativeEconomyMetrics",
    "CreativeSector",
    "EconomicMultipliers",
    # Advanced Frameworks
    "CulturalCGEFramework",
    "AudienceABMFramework",
    "CulturalEquityFramework",
    "MediaImpactFramework",
    "IntegratedCulturalFramework",
    # New Professional Frameworks
    "ContentValuationFramework",
    "IPValuationFramework",
    "PlatformEconomicsFramework",
]
