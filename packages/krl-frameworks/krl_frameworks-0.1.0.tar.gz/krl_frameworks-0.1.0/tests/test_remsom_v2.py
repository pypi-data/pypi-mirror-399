# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - REMSOM v2 Unit Tests
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Unit tests for REMSOM v2 (Observatory Architecture).

Tests cover:
- REMSOMFramework initialization and metadata
- CobbDouglasMobilityEngine trajectory projections
- SpatialWeightsBuilder construction
- REMSOMAnalysisResult serialization
- Framework registry lazy loading
- REMSOM v1 deprecation warning
"""

import warnings
from datetime import datetime
from typing import Any, Dict

import numpy as np
import pytest


class TestREMSOMV2Imports:
    """Test that all REMSOM v2 exports are importable."""
    
    def test_import_framework(self):
        """Test REMSOMFrameworkV2 import."""
        from krl_frameworks.layers.meta.remsomV2 import REMSOMFramework
        assert REMSOMFramework is not None
    
    def test_import_config(self):
        """Test REMSOMConfig import."""
        from krl_frameworks.layers.meta.remsomV2 import REMSOMConfig
        assert REMSOMConfig is not None
    
    def test_import_enums(self):
        """Test enum imports."""
        from krl_frameworks.layers.meta.remsomV2 import (
            OpportunityDomain,
            REMSOMStack,
        )
        assert OpportunityDomain.EDUCATION is not None
        assert REMSOMStack.INDEX is not None
    
    def test_import_data_classes(self):
        """Test dataclass imports."""
        from krl_frameworks.layers.meta.remsomV2 import (
            OpportunityScore,
            SpatialStructure,
            CausalEstimate,
            MobilityTrajectory,
            PolicyScenario,
            REMSOMAnalysisResult,
        )
        assert all(cls is not None for cls in [
            OpportunityScore, SpatialStructure, CausalEstimate,
            MobilityTrajectory, PolicyScenario, REMSOMAnalysisResult
        ])
    
    def test_import_cobb_douglas(self):
        """Test Cobb-Douglas dynamics imports."""
        from krl_frameworks.layers.meta.remsomV2 import (
            CobbDouglasDynamicsConfig,
            CobbDouglasMobilityEngine,
        )
        assert CobbDouglasDynamicsConfig is not None
        assert CobbDouglasMobilityEngine is not None
    
    def test_import_spatial_weights(self):
        """Test spatial weights builder imports."""
        from krl_frameworks.layers.meta.remsomV2 import (
            SpatialWeightsBuilder,
            SpatialWeightsResult,
        )
        assert SpatialWeightsBuilder is not None
        assert SpatialWeightsResult is not None


class TestOpportunityDomain:
    """Test OpportunityDomain enumeration."""
    
    def test_core_domains(self):
        """Test core HDI-style domains exist."""
        from krl_frameworks.layers.meta.remsomV2 import OpportunityDomain
        
        core_domains = [
            OpportunityDomain.EDUCATION,
            OpportunityDomain.HEALTH,
            OpportunityDomain.INCOME,
        ]
        assert all(d is not None for d in core_domains)
    
    def test_extended_domains(self):
        """Test extended SPI-style domains exist."""
        from krl_frameworks.layers.meta.remsomV2 import OpportunityDomain
        
        extended = [
            OpportunityDomain.HOUSING,
            OpportunityDomain.DIGITAL_ACCESS,
            OpportunityDomain.ENVIRONMENT,
            OpportunityDomain.SAFETY,
        ]
        assert all(d is not None for d in extended)
    
    def test_mobility_domains(self):
        """Test mobility-specific domains exist."""
        from krl_frameworks.layers.meta.remsomV2 import OpportunityDomain
        
        mobility = [
            OpportunityDomain.LABOR_MARKET,
            OpportunityDomain.CREDIT_ACCESS,
            OpportunityDomain.TRANSPORT,
        ]
        assert all(d is not None for d in mobility)


class TestREMSOMStack:
    """Test REMSOMStack enumeration."""
    
    def test_three_stacks(self):
        """Test all three model stacks exist."""
        from krl_frameworks.layers.meta.remsomV2 import REMSOMStack
        
        assert REMSOMStack.INDEX is not None
        assert REMSOMStack.SPATIAL is not None
        assert REMSOMStack.CAUSAL is not None


class TestREMSOMConfig:
    """Test REMSOMConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        from krl_frameworks.layers.meta.remsomV2 import REMSOMConfig
        
        config = REMSOMConfig()
        assert config.geography_level == "county"  # Default is county
        assert config.base_year == 2024  # Default is 2024
        assert config.projection_horizon == 10
    
    def test_custom_config(self):
        """Test custom configuration."""
        from krl_frameworks.layers.meta.remsomV2 import (
            REMSOMConfig,
            OpportunityDomain,
        )
        
        config = REMSOMConfig(
            domains=[OpportunityDomain.EDUCATION, OpportunityDomain.INCOME],
            geography_level="county",
            base_year=2022,
            projection_horizon=5,
        )
        assert len(config.domains) == 2
        assert config.geography_level == "county"
        assert config.base_year == 2022


class TestCobbDouglasMobilityEngine:
    """Test Cobb-Douglas mobility projection engine."""
    
    def test_engine_initialization(self):
        """Test engine initializes with default config."""
        from krl_frameworks.layers.meta.remsomV2 import (
            CobbDouglasDynamicsConfig,
            CobbDouglasMobilityEngine,
        )
        
        config = CobbDouglasDynamicsConfig()
        engine = CobbDouglasMobilityEngine(config)
        
        assert engine is not None
        assert engine.config.labor_elasticity == 0.7
        assert engine.config.capital_share == 0.33
    
    def test_trajectory_projection(self):
        """Test trajectory projection returns valid output."""
        from krl_frameworks.layers.meta.remsomV2 import (
            CobbDouglasDynamicsConfig,
            CobbDouglasMobilityEngine,
            OpportunityScore,
            OpportunityDomain,
        )
        
        config = CobbDouglasDynamicsConfig()
        engine = CobbDouglasMobilityEngine(config)
        
        # Create mock opportunity score with correct field names
        initial_score = OpportunityScore(
            total=0.65,
            domain_scores={
                OpportunityDomain.EDUCATION: 0.7,
                OpportunityDomain.HEALTH: 0.6,
                OpportunityDomain.INCOME: 0.65,
            },
            domain_contributions={
                OpportunityDomain.EDUCATION: 0.23,
                OpportunityDomain.HEALTH: 0.20,
                OpportunityDomain.INCOME: 0.22,
            },
            geography_id="06037",
            cohort_id="25-34",
            year=2024,
            binding_constraints=[OpportunityDomain.HEALTH],
            improvement_potential={OpportunityDomain.HEALTH: 0.15},
        )
        
        trajectory = engine.project_trajectory(
            initial_score=initial_score,
            n_periods=10,
            n_sectors=5,
        )
        
        assert len(trajectory) == 11  # n_periods + 1 (initial)
        assert all(isinstance(v, (int, float)) for v in trajectory)
    
    def test_policy_shock_projection(self):
        """Test trajectory with policy shock."""
        from krl_frameworks.layers.meta.remsomV2 import (
            CobbDouglasDynamicsConfig,
            CobbDouglasMobilityEngine,
            OpportunityScore,
            OpportunityDomain,
        )
        
        config = CobbDouglasDynamicsConfig()
        engine = CobbDouglasMobilityEngine(config)
        
        initial_score = OpportunityScore(
            total=0.65,
            domain_scores={OpportunityDomain.EDUCATION: 0.7},
            domain_contributions={OpportunityDomain.EDUCATION: 0.65},
            geography_id="06037",
            cohort_id="25-34",
            year=2024,
            binding_constraints=[OpportunityDomain.EDUCATION],
            improvement_potential={OpportunityDomain.EDUCATION: 0.1},
        )
        
        # Education policy shock at period 3
        trajectory = engine.project_trajectory(
            initial_score=initial_score,
            n_periods=10,
            n_sectors=5,
            policy_shock={OpportunityDomain.EDUCATION: 0.1},
            policy_timing=3,
        )
        
        assert len(trajectory) == 11


class TestSpatialWeightsBuilder:
    """Test SpatialWeightsBuilder utility."""
    
    def test_synthetic_weights(self):
        """Test synthetic weights generation."""
        from krl_frameworks.layers.meta.remsomV2 import SpatialWeightsBuilder
        
        builder = SpatialWeightsBuilder()
        result = builder._build_synthetic(
            geography_level="county",
            state_fips="06",
            weight_type="queen",
            k=5,
        )
        
        assert result is not None
        assert result.weights_matrix.shape[0] == result.weights_matrix.shape[1]
        assert result.source == "synthetic"
        assert len(result.geo_ids) > 0
    
    def test_precomputed_weights(self):
        """Test wrapping precomputed weights."""
        from krl_frameworks.layers.meta.remsomV2 import SpatialWeightsBuilder
        
        builder = SpatialWeightsBuilder()
        
        # Create simple 3x3 weights matrix
        W = np.array([
            [0, 0.5, 0.5],
            [0.5, 0, 0.5],
            [0.5, 0.5, 0],
        ])
        geo_ids = ["001", "002", "003"]
        
        result = builder.from_precomputed(W, geo_ids)
        
        assert result.weights_matrix.shape == (3, 3)
        assert result.geo_ids == geo_ids
        assert result.source == "precomputed"


class TestREMSOMAnalysisResult:
    """Test REMSOMAnalysisResult serialization."""
    
    def test_to_dict(self):
        """Test to_dict serialization."""
        from krl_frameworks.layers.meta.remsomV2 import (
            REMSOMAnalysisResult,
            REMSOMConfig,
            OpportunityScore,
            OpportunityDomain,
        )
        
        result = REMSOMAnalysisResult(
            execution_id="test-001",
            timestamp=datetime.now(),
            config=REMSOMConfig(),
            opportunity_scores=[
                OpportunityScore(
                    total=0.65,
                    domain_scores={OpportunityDomain.EDUCATION: 0.7},
                    domain_contributions={OpportunityDomain.EDUCATION: 0.65},
                    geography_id="06037",
                    cohort_id="all",
                    year=2024,
                    binding_constraints=[OpportunityDomain.EDUCATION],
                    improvement_potential={OpportunityDomain.EDUCATION: 0.1},
                )
            ],
            aggregate_opportunity_index=0.65,
            domain_decomposition={OpportunityDomain.EDUCATION: 0.7},
            spatial_structure=None,
            causal_estimates=[],
            trajectories=[],
            binding_constraints_national=[OpportunityDomain.INCOME],
            high_leverage_interventions=["education_investment"],
            equity_gaps={"race_gap": 0.15},
            data_sources_used=["census_acs"],
            model_versions={"hdi": "1.0.0"},
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["execution_id"] == "test-001"
        assert "timestamp" in result_dict
        assert result_dict["index_results"]["aggregate_opportunity_index"] == 0.65
        assert "INCOME" in result_dict["policy_insights"]["binding_constraints"]


class TestREMSOMFrameworkMetadata:
    """Test REMSOMFramework metadata."""
    
    def test_metadata_slug(self):
        """Test framework slug is 'remsomv2'."""
        from krl_frameworks.layers.meta.remsomV2 import REMSOMFramework
        
        metadata = REMSOMFramework.metadata()
        assert metadata.slug == "remsomv2"
    
    def test_metadata_tier(self):
        """Test framework is ENTERPRISE tier."""
        from krl_frameworks.layers.meta.remsomV2 import REMSOMFramework
        from krl_frameworks.core.tier import Tier
        
        metadata = REMSOMFramework.metadata()
        assert metadata.tier == Tier.ENTERPRISE


class TestREMSOMFrameworkRegistries:
    """Test framework registries for lazy loading."""
    
    def test_index_frameworks_registry(self):
        """Test INDEX_FRAMEWORKS registry has correct entries."""
        from krl_frameworks.layers.meta.remsomV2 import REMSOMFramework
        
        registry = REMSOMFramework.INDEX_FRAMEWORKS
        
        assert "hdi" in registry
        assert "mpi" in registry
        assert "spi" in registry
        assert "gii" in registry
        assert "HDIFramework" in registry["hdi"]
    
    def test_causal_frameworks_registry(self):
        """Test CAUSAL_FRAMEWORKS registry has correct entries."""
        from krl_frameworks.layers.meta.remsomV2 import REMSOMFramework
        
        registry = REMSOMFramework.CAUSAL_FRAMEWORKS
        
        assert "did" in registry
        assert "rdd" in registry
        assert "iv" in registry
        assert "psm" in registry
        assert "dml" in registry
        # Verify DML path uses DMLFramework, not DoubleMLFramework
        assert "DMLFramework" in registry["dml"]
    
    def test_spatial_frameworks_registry(self):
        """Test SPATIAL_FRAMEWORKS registry has correct entries."""
        from krl_frameworks.layers.meta.remsomV2 import REMSOMFramework
        
        registry = REMSOMFramework.SPATIAL_FRAMEWORKS
        
        assert "sar" in registry
        assert "sem" in registry
        assert "gwr" in registry


class TestREMSOMV1Deprecation:
    """Test REMSOM v1 deprecation warning."""
    
    def test_v1_emits_deprecation_warning(self):
        """Test that REMSOMFramework v1 emits deprecation warning."""
        from krl_frameworks.layers.meta.remsom import REMSOMFramework
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Instantiate v1 framework
            framework = REMSOMFramework()
            
            # Check deprecation warning was emitted
            deprecation_warnings = [
                x for x in w if issubclass(x.category, DeprecationWarning)
            ]
            assert len(deprecation_warnings) >= 1
            assert "deprecated" in str(deprecation_warnings[0].message).lower()
            assert "REMSOMFrameworkV2" in str(deprecation_warnings[0].message)


class TestSpatialAdapterExports:
    """Test spatial adapter factory exports."""
    
    def test_adapter_factories_exported(self):
        """Test all spatial adapter factories are exported."""
        from krl_frameworks.adapters import (
            get_spatial_lag_adapter,
            get_spatial_error_adapter,
            get_gwr_adapter,
        )
        
        assert callable(get_spatial_lag_adapter)
        assert callable(get_spatial_error_adapter)
        assert callable(get_gwr_adapter)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
