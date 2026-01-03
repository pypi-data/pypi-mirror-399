# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Layer 1: Socioeconomic / Academic Frameworks
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Layer 1: Socioeconomic and Academic Frameworks.

This layer contains foundational frameworks for multidimensional
socioeconomic analysis, including:

Community Tier (Individual Index Access):
    - MPI: Multidimensional Poverty Index (UNDP/Oxford)
    - HDI: Human Development Index (UNDP)
    - SPI: Social Progress Index (Social Progress Imperative)
    - IAM: Integrated Assessment Models (DICE, GCAM)

Professional Tier (Extended Analytics):
    - SAM-CGE: Social Accounting Matrix / Computable General Equilibrium
    - SAM-CGE-Poverty: Poverty-focused microsimulation linkage
    - CGE-Microsim: Full macro-micro chains
    - Spatial-Causal-Index: Hybrid spatial-causal-index models
"""

from krl_frameworks.layers.socioeconomic.mpi import MPIFramework
from krl_frameworks.layers.socioeconomic.hdi import HDIFramework
from krl_frameworks.layers.socioeconomic.spi import SPIFramework
from krl_frameworks.layers.socioeconomic.iam import IAMFramework
from krl_frameworks.layers.socioeconomic.sam_cge import SAMCGEFramework
from krl_frameworks.layers.socioeconomic.sam_cge_poverty import SAMCGEPovertyFramework
from krl_frameworks.layers.socioeconomic.cge_microsim import CGEMicrosimFramework
from krl_frameworks.layers.socioeconomic.spatial_causal_index import SpatialCausalIndexFramework
from krl_frameworks.layers.socioeconomic.wbi import WBIFramework
from krl_frameworks.layers.socioeconomic.ihdi import IHDIFramework
from krl_frameworks.layers.socioeconomic.nri import NRIFramework
from krl_frameworks.layers.socioeconomic.gii import GIIFramework

__all__ = [
    "MPIFramework",
    "HDIFramework",
    "SPIFramework",
    "IAMFramework",
    "SAMCGEFramework",
    "SAMCGEPovertyFramework",  # ✅ Week 4
    "CGEMicrosimFramework",  # ✅ Week 5
    "SpatialCausalIndexFramework",  # ✅ Week 5
    "WBIFramework",
    "IHDIFramework",
    "NRIFramework",
    "GIIFramework",
]
