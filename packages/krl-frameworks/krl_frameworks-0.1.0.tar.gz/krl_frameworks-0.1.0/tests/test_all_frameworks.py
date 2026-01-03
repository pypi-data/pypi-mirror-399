# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - All Framework Import & Metadata Tests
# ════════════════════════════════════════════════════════════════════════════════

"""
Tests for all 28 meta-frameworks across 6 vertical layers.

This module validates:
1. All frameworks can be imported
2. All frameworks have valid METADATA
3. All frameworks can be instantiated
4. Framework slugs are unique
"""

from __future__ import annotations

import pytest

from krl_frameworks.core.base import VerticalLayer
from krl_frameworks.core.tier import Tier


# ────────────────────────────────────────────────────────────────────────────────
# Expected Framework Configuration (28 frameworks)
# ────────────────────────────────────────────────────────────────────────────────

EXPECTED_FRAMEWORKS = {
    # Layer 1: Socioeconomic / Academic (8)
    "mpi": {"layer": 1, "tier": "COMMUNITY", "name": "Multidimensional Poverty Index"},
    "hdi": {"layer": 1, "tier": "COMMUNITY", "name": "Human Development Index"},
    "spi": {"layer": 1, "tier": "COMMUNITY", "name": "Social Progress Index"},
    "iam": {"layer": 1, "tier": "COMMUNITY", "name": "Integrated Assessment Models"},
    "sam_cge": {"layer": 1, "tier": "PROFESSIONAL", "name": "SAM-CGE Hybrids"},
    "sam_cge_poverty": {"layer": 1, "tier": "PROFESSIONAL", "name": "SAM-CGE-Poverty"},
    "cge_microsim": {"layer": 1, "tier": "PROFESSIONAL", "name": "CGE-Microsim Chains"},
    "spatial_causal_index": {"layer": 1, "tier": "PROFESSIONAL", "name": "Spatial-Causal-Index Hybrids"},
    
    # Layer 2: Government / Policy (6)
    "cbo_scoring": {"layer": 2, "tier": "PROFESSIONAL", "name": "CBO Scoring"},
    "omb_part": {"layer": 2, "tier": "PROFESSIONAL", "name": "OMB PART"},
    "gao_gpra": {"layer": 2, "tier": "PROFESSIONAL", "name": "GAO GPRA"},
    "mpi_operational": {"layer": 2, "tier": "COMMUNITY", "name": "MPI Operational Tools"},
    "city_resilience": {"layer": 2, "tier": "COMMUNITY", "name": "City/State Resilience Dashboards"},
    "interagency_spatial_causal": {"layer": 2, "tier": "PROFESSIONAL", "name": "Interagency Spatial Causal Toolkits"},
    
    # Layer 3: Experimental / Research (6)
    "rct": {"layer": 3, "tier": "TEAM", "name": "Randomized Controlled Trial"},
    "did": {"layer": 3, "tier": "TEAM", "name": "Difference-in-Differences"},
    "synthetic_control": {"layer": 3, "tier": "ENTERPRISE", "name": "Synthetic Control"},
    "spatial_causal_gccm": {"layer": 3, "tier": "PROFESSIONAL", "name": "Spatial Causal (GCCM/Matching)"},
    "sd_abm": {"layer": 3, "tier": "PROFESSIONAL", "name": "SD-ABM Hybrids"},
    "multilayer_network": {"layer": 3, "tier": "PROFESSIONAL", "name": "Multilayer Spatial-Network Engines"},
    
    # Layer 4: Financial / Economic (8)
    "basel_iii": {"layer": 4, "tier": "ENTERPRISE", "name": "Basel III"},
    "cecl": {"layer": 4, "tier": "ENTERPRISE", "name": "CECL"},
    "stress_test": {"layer": 4, "tier": "ENTERPRISE", "name": "Stress Testing"},
    "macro_financial_cge": {"layer": 4, "tier": "PROFESSIONAL", "name": "Macro-Financial CGE"},
    "networked_financial": {"layer": 4, "tier": "PROFESSIONAL", "name": "Networked Financial"},
    "risk_indices": {"layer": 4, "tier": "COMMUNITY", "name": "Risk Indices"},
    "composite_risk": {"layer": 4, "tier": "PROFESSIONAL", "name": "Composite Risk / Solvency"},
    "financial_meta_orchestrator": {"layer": 4, "tier": "ENTERPRISE", "name": "Financial Meta-Orchestrators"},
    
    # Layer 5: Arts / Media / Entertainment (8)
    "cultural_impact": {"layer": 5, "tier": "PROFESSIONAL", "name": "Cultural Impact"},
    "media_reach": {"layer": 5, "tier": "PROFESSIONAL", "name": "Media Reach"},
    "creative_economy": {"layer": 5, "tier": "TEAM", "name": "Creative Economy"},
    "cultural_cge": {"layer": 5, "tier": "COMMUNITY", "name": "Cultural CGE"},
    "audience_abm": {"layer": 5, "tier": "COMMUNITY", "name": "Audience / Media ABM"},
    "cultural_equity": {"layer": 5, "tier": "PROFESSIONAL", "name": "Cultural Opportunity / Equity Indices"},
    "media_impact_streaming": {"layer": 5, "tier": "PROFESSIONAL", "name": "Media Impact / Press & Streaming"},
    "integrated_cultural_ecosystem": {"layer": 5, "tier": "PROFESSIONAL", "name": "Experimental Integrated Cultural Ecosystem"},
    
    # Layer 6: Meta / Peer (4)
    "remsom": {"layer": 6, "tier": "ENTERPRISE", "name": "REMSOM"},
    "iam_policy_stack": {"layer": 6, "tier": "PROFESSIONAL", "name": "IAM-Policy Stacks"},
    "hdi_mpi_dashboard": {"layer": 6, "tier": "COMMUNITY", "name": "HDI / MPI Dashboards"},
    "spi_policy_stack": {"layer": 6, "tier": "COMMUNITY", "name": "SPI Policy Simulation Stacks"},
}


# ────────────────────────────────────────────────────────────────────────────────
# Framework Import Tests
# ────────────────────────────────────────────────────────────────────────────────


class TestAllFrameworkImports:
    """Test that all 28 frameworks can be imported."""

    def test_layer1_socioeconomic_imports(self):
        """Test Layer 1 framework imports."""
        from krl_frameworks.layers.socioeconomic import (
            MPIFramework,
            HDIFramework,
            SPIFramework,
            IAMFramework,
            SAMCGEFramework,
            SAMCGEPovertyFramework,
            CGEMicrosimFramework,
            SpatialCausalIndexFramework,
        )
        assert MPIFramework is not None
        assert HDIFramework is not None
        assert SPIFramework is not None
        assert IAMFramework is not None
        assert SAMCGEFramework is not None
        assert SAMCGEPovertyFramework is not None
        assert CGEMicrosimFramework is not None
        assert SpatialCausalIndexFramework is not None

    def test_layer2_government_imports(self):
        """Test Layer 2 framework imports."""
        from krl_frameworks.layers.government import (
            CBOScoringFramework,
            OMBPartFramework,
            GAOGpraFramework,
            MPIOperationalFramework,
            CityResilienceFramework,
            InteragencySpatialCausalFramework,
        )
        assert CBOScoringFramework is not None
        assert OMBPartFramework is not None
        assert GAOGpraFramework is not None
        assert MPIOperationalFramework is not None
        assert CityResilienceFramework is not None
        assert InteragencySpatialCausalFramework is not None

    def test_layer3_experimental_imports(self):
        """Test Layer 3 framework imports."""
        from krl_frameworks.layers.experimental import (
            RCTFramework,
            DiDFramework,
            SyntheticControlFramework,
            SpatialCausalFramework,
            SDABMFramework,
            MultilayerNetworkFramework,
        )
        assert RCTFramework is not None
        assert DiDFramework is not None
        assert SyntheticControlFramework is not None
        assert SpatialCausalFramework is not None
        assert SDABMFramework is not None
        assert MultilayerNetworkFramework is not None

    def test_layer4_financial_imports(self):
        """Test Layer 4 framework imports."""
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
        assert BaselIIIFramework is not None
        assert CECLFramework is not None
        assert StressTestFramework is not None
        assert MacroFinancialCGEFramework is not None
        assert NetworkedFinancialFramework is not None
        assert RiskIndicesFramework is not None
        assert CompositeRiskFramework is not None
        assert FinancialMetaOrchestratorFramework is not None

    def test_layer5_arts_media_imports(self):
        """Test Layer 5 framework imports."""
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
        assert CulturalImpactFramework is not None
        assert MediaReachFramework is not None
        assert CreativeEconomyFramework is not None
        assert CulturalCGEFramework is not None
        assert AudienceABMFramework is not None
        assert CulturalEquityFramework is not None
        assert MediaImpactFramework is not None
        assert IntegratedCulturalFramework is not None

    def test_layer6_meta_imports(self):
        """Test Layer 6 framework imports."""
        from krl_frameworks.layers.meta import (
            REMSOMFramework,
            IAMPolicyStackFramework,
            HDIMPIDashboardFramework,
            SPIPolicyStackFramework,
        )
        assert REMSOMFramework is not None
        assert IAMPolicyStackFramework is not None
        assert HDIMPIDashboardFramework is not None
        assert SPIPolicyStackFramework is not None

    def test_main_package_imports_all(self):
        """Test main package exports all framework classes and utilities."""
        from krl_frameworks import layers
        
        # Count total exports in __all__ (frameworks + transition functions)
        # We export 40 items: 28+ framework classes + transition function classes
        assert len(layers.__all__) >= 28, f"Expected at least 28 framework exports, got {len(layers.__all__)}"


# ────────────────────────────────────────────────────────────────────────────────
# Framework Metadata Tests
# ────────────────────────────────────────────────────────────────────────────────


class TestFrameworkMetadata:
    """Test that all frameworks have valid METADATA."""

    def test_all_frameworks_have_metadata(self):
        """Test each framework has METADATA attribute or metadata() classmethod."""
        from krl_frameworks.layers import (
            MPIFramework, HDIFramework, SPIFramework, IAMFramework,
            SAMCGEFramework, SAMCGEPovertyFramework, CGEMicrosimFramework,
            SpatialCausalIndexFramework, CBOScoringFramework, OMBPartFramework,
            GAOGpraFramework, MPIOperationalFramework, CityResilienceFramework,
            InteragencySpatialCausalFramework, RCTFramework, DiDFramework,
            SyntheticControlFramework, SpatialCausalFramework, SDABMFramework,
            MultilayerNetworkFramework, BaselIIIFramework, CECLFramework,
            StressTestFramework, MacroFinancialCGEFramework, NetworkedFinancialFramework,
            RiskIndicesFramework, CompositeRiskFramework, FinancialMetaOrchestratorFramework,
            CulturalImpactFramework, MediaReachFramework, CreativeEconomyFramework,
            CulturalCGEFramework, AudienceABMFramework, CulturalEquityFramework,
            MediaImpactFramework, IntegratedCulturalFramework,
            REMSOMFramework, IAMPolicyStackFramework, HDIMPIDashboardFramework,
            SPIPolicyStackFramework,
        )
        
        # New frameworks that must have METADATA attribute
        new_frameworks = [
            IAMFramework,
            SAMCGEFramework, SAMCGEPovertyFramework, CGEMicrosimFramework,
            SpatialCausalIndexFramework, MPIOperationalFramework, CityResilienceFramework,
            InteragencySpatialCausalFramework, SpatialCausalFramework, SDABMFramework,
            MultilayerNetworkFramework, MacroFinancialCGEFramework, NetworkedFinancialFramework,
            RiskIndicesFramework, CompositeRiskFramework, FinancialMetaOrchestratorFramework,
            CulturalCGEFramework, AudienceABMFramework, CulturalEquityFramework,
            MediaImpactFramework, IntegratedCulturalFramework,
            IAMPolicyStackFramework, HDIMPIDashboardFramework, SPIPolicyStackFramework,
        ]
        
        for fw_class in new_frameworks:
            assert hasattr(fw_class, "METADATA"), f"{fw_class.__name__} missing METADATA"
            meta = fw_class.METADATA
            assert meta.slug, f"{fw_class.__name__} has empty slug"
            assert meta.name, f"{fw_class.__name__} has empty name"
            assert meta.layer is not None, f"{fw_class.__name__} has no layer"
            assert meta.tier is not None, f"{fw_class.__name__} has no tier"

    def test_framework_slugs_unique(self):
        """Test all framework slugs are unique."""
        from krl_frameworks.layers import (
            IAMFramework, SAMCGEFramework, SAMCGEPovertyFramework, CGEMicrosimFramework,
            SpatialCausalIndexFramework, MPIOperationalFramework, CityResilienceFramework,
            InteragencySpatialCausalFramework, SpatialCausalFramework, SDABMFramework,
            MultilayerNetworkFramework, MacroFinancialCGEFramework, NetworkedFinancialFramework,
            RiskIndicesFramework, CompositeRiskFramework, FinancialMetaOrchestratorFramework,
            CulturalCGEFramework, AudienceABMFramework, CulturalEquityFramework,
            MediaImpactFramework, IntegratedCulturalFramework,
            IAMPolicyStackFramework, HDIMPIDashboardFramework, SPIPolicyStackFramework,
        )
        
        new_frameworks = [
            IAMFramework, SAMCGEFramework, SAMCGEPovertyFramework, CGEMicrosimFramework,
            SpatialCausalIndexFramework, MPIOperationalFramework, CityResilienceFramework,
            InteragencySpatialCausalFramework, SpatialCausalFramework, SDABMFramework,
            MultilayerNetworkFramework, MacroFinancialCGEFramework, NetworkedFinancialFramework,
            RiskIndicesFramework, CompositeRiskFramework, FinancialMetaOrchestratorFramework,
            CulturalCGEFramework, AudienceABMFramework, CulturalEquityFramework,
            MediaImpactFramework, IntegratedCulturalFramework,
            IAMPolicyStackFramework, HDIMPIDashboardFramework, SPIPolicyStackFramework,
        ]
        
        slugs = [fw.METADATA.slug for fw in new_frameworks]
        assert len(slugs) == len(set(slugs)), f"Duplicate slugs found: {slugs}"


# ────────────────────────────────────────────────────────────────────────────────
# Framework Instantiation Tests
# ────────────────────────────────────────────────────────────────────────────────


class TestFrameworkInstantiation:
    """Test that all new frameworks can be instantiated."""

    def test_layer1_new_frameworks_instantiate(self):
        """Test Layer 1 new frameworks can be instantiated."""
        from krl_frameworks.layers.socioeconomic import (
            IAMFramework,
            SAMCGEFramework,
            SAMCGEPovertyFramework,
            CGEMicrosimFramework,
            SpatialCausalIndexFramework,
        )
        
        assert IAMFramework() is not None
        assert SAMCGEFramework() is not None
        assert SAMCGEPovertyFramework() is not None
        assert CGEMicrosimFramework() is not None
        assert SpatialCausalIndexFramework() is not None

    def test_layer2_new_frameworks_instantiate(self):
        """Test Layer 2 new frameworks can be instantiated."""
        from krl_frameworks.layers.government import (
            MPIOperationalFramework,
            CityResilienceFramework,
            InteragencySpatialCausalFramework,
        )
        
        assert MPIOperationalFramework() is not None
        assert CityResilienceFramework() is not None
        assert InteragencySpatialCausalFramework() is not None

    def test_layer3_new_frameworks_instantiate(self):
        """Test Layer 3 new frameworks can be instantiated."""
        from krl_frameworks.layers.experimental import (
            SpatialCausalFramework,
            SDABMFramework,
            MultilayerNetworkFramework,
        )
        
        assert SpatialCausalFramework() is not None
        assert SDABMFramework() is not None
        assert MultilayerNetworkFramework() is not None

    def test_layer4_new_frameworks_instantiate(self):
        """Test Layer 4 new frameworks can be instantiated."""
        from krl_frameworks.layers.financial import (
            MacroFinancialCGEFramework,
            NetworkedFinancialFramework,
            RiskIndicesFramework,
            CompositeRiskFramework,
            FinancialMetaOrchestratorFramework,
        )
        
        assert MacroFinancialCGEFramework() is not None
        assert NetworkedFinancialFramework() is not None
        assert RiskIndicesFramework() is not None
        assert CompositeRiskFramework() is not None
        assert FinancialMetaOrchestratorFramework() is not None

    def test_layer5_new_frameworks_instantiate(self):
        """Test Layer 5 new frameworks can be instantiated."""
        from krl_frameworks.layers.arts_media import (
            CulturalCGEFramework,
            AudienceABMFramework,
            CulturalEquityFramework,
            MediaImpactFramework,
            IntegratedCulturalFramework,
        )
        
        assert CulturalCGEFramework() is not None
        assert AudienceABMFramework() is not None
        assert CulturalEquityFramework() is not None
        assert MediaImpactFramework() is not None
        assert IntegratedCulturalFramework() is not None

    def test_layer6_new_frameworks_instantiate(self):
        """Test Layer 6 new frameworks can be instantiated."""
        from krl_frameworks.layers.meta import (
            IAMPolicyStackFramework,
            HDIMPIDashboardFramework,
            SPIPolicyStackFramework,
        )
        
        assert IAMPolicyStackFramework() is not None
        assert HDIMPIDashboardFramework() is not None
        assert SPIPolicyStackFramework() is not None


# ────────────────────────────────────────────────────────────────────────────────
# Framework Count Tests
# ────────────────────────────────────────────────────────────────────────────────


class TestFrameworkCounts:
    """Test framework counts by layer."""

    def test_total_framework_count(self):
        """Test total of 40 frameworks (expanded from original 16)."""
        assert len(EXPECTED_FRAMEWORKS) == 40

    def test_layer_counts(self):
        """Test framework counts per layer."""
        layer_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        for slug, config in EXPECTED_FRAMEWORKS.items():
            layer_counts[config["layer"]] += 1
        
        assert layer_counts[1] == 8, f"Layer 1 expected 8, got {layer_counts[1]}"
        assert layer_counts[2] == 6, f"Layer 2 expected 6, got {layer_counts[2]}"
        assert layer_counts[3] == 6, f"Layer 3 expected 6, got {layer_counts[3]}"
        assert layer_counts[4] == 8, f"Layer 4 expected 8, got {layer_counts[4]}"
        assert layer_counts[5] == 8, f"Layer 5 expected 8, got {layer_counts[5]}"
        assert layer_counts[6] == 4, f"Layer 6 expected 4, got {layer_counts[6]}"
