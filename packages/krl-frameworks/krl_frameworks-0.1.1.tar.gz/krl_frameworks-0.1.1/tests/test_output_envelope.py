# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Output Envelope Contract Tests
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Contract tests for the Framework Output Envelope architecture.

These tests validate:
1. DimensionManifest canonical constraints
2. ProvenanceRecord separation of concerns
3. FrameworkOutputEnvelope integrity
4. REMSOM build_output_envelope behavior
5. Dimensional integrity (N sectors selected → N sectors returned)
"""

import pytest
import numpy as np

from krl_frameworks.core.output_envelope import (
    DimensionManifest,
    ProvenanceRecord,
    FrameworkOutputEnvelope,
    create_dimension_manifest,
    create_provenance_record,
)


class TestDimensionManifest:
    """Tests for DimensionManifest canonical behavior."""
    
    def test_creation_with_sectors(self):
        """Dimension manifest captures user-provided sector names."""
        manifest = DimensionManifest(
            sectors=("Information", "Finance", "Services"),
            geography="Virginia",
        )
        
        assert manifest.n_sectors == 3
        assert manifest.sectors == ("Information", "Finance", "Services")
        assert manifest.geography == "Virginia"
    
    def test_list_to_tuple_conversion(self):
        """Lists are converted to tuples for immutability."""
        manifest = DimensionManifest(
            sectors=["Information", "Finance", "Services"],
            time_periods=[2024, 2025, 2026],
            cohorts=["18-24", "25-34"],
        )
        
        assert isinstance(manifest.sectors, tuple)
        assert isinstance(manifest.time_periods, tuple)
        assert isinstance(manifest.cohorts, tuple)
    
    def test_duplicate_detection_in_sectors(self):
        """Duplicate sector names raise ValueError."""
        with pytest.raises(ValueError, match="duplicates"):
            DimensionManifest(
                sectors=("Information", "Finance", "Information"),
            )
    
    def test_duplicate_detection_in_cohorts(self):
        """Duplicate cohort labels raise ValueError."""
        with pytest.raises(ValueError, match="duplicates"):
            DimensionManifest(
                cohorts=("18-24", "25-34", "18-24"),
            )
    
    def test_serialization_roundtrip(self):
        """Manifest can be serialized and preserves data."""
        manifest = DimensionManifest(
            sectors=("Information", "Finance", "Services"),
            time_periods=(2024, 2025, 2026),
            cohorts=("18-24", "25-34"),
            geography="Virginia",
        )
        
        d = manifest.to_dict()
        
        assert d["sectors"] == ["Information", "Finance", "Services"]
        assert d["n_sectors"] == 3
        assert d["geography"] == "Virginia"
        assert d["time_periods"] == [2024, 2025, 2026]
    
    def test_factory_function(self):
        """create_dimension_manifest works correctly."""
        manifest = create_dimension_manifest(
            sectors=["A", "B"],
            time_periods=[1, 2, 3],
            geography="Test Region",
        )
        
        assert manifest.n_sectors == 2
        assert manifest.n_time_periods == 3


class TestProvenanceRecord:
    """Tests for ProvenanceRecord separation of concerns."""
    
    def test_user_params_vs_fallbacks(self):
        """User parameters and fallbacks are tracked separately."""
        provenance = ProvenanceRecord(
            user_parameters={"sector_names": ["A", "B", "C"]},
        )
        
        provenance.add_fallback("capital_share", 0.33, "No capital data available")
        
        assert "sector_names" in provenance.user_parameters
        assert "capital_share" in provenance.fallbacks_applied
        assert provenance.fallbacks_applied["capital_share"]["value"] == 0.33
        assert "No capital data" in provenance.fallbacks_applied["capital_share"]["reason"]
    
    def test_has_fallbacks_property(self):
        """has_fallbacks returns True when fallbacks exist."""
        provenance = ProvenanceRecord()
        assert not provenance.has_fallbacks
        
        provenance.add_fallback("test", 1.0, "reason")
        assert provenance.has_fallbacks
        assert provenance.fallback_count == 1
    
    def test_simulation_params_separate(self):
        """Simulation parameters are separate from user/fallback params."""
        provenance = ProvenanceRecord(
            user_parameters={"n_sectors": 3},
            simulation_params={"random_seed": 42, "convergence_tolerance": 1e-6},
        )
        
        assert "random_seed" not in provenance.user_parameters
        assert "random_seed" in provenance.simulation_params
    
    def test_data_source_tracking(self):
        """Data sources can be tracked."""
        provenance = ProvenanceRecord()
        provenance.add_data_source("BLS Employment Data")
        provenance.add_data_source("Census ACS")
        provenance.add_data_source("BLS Employment Data")  # Duplicate
        
        assert len(provenance.data_sources) == 2
        assert "BLS Employment Data" in provenance.data_sources


class TestFrameworkOutputEnvelope:
    """Tests for FrameworkOutputEnvelope integrity."""
    
    def test_creation_requires_slug_and_version(self):
        """Envelope requires framework_slug and version."""
        with pytest.raises(ValueError, match="framework_slug"):
            FrameworkOutputEnvelope(
                framework_slug="",
                framework_version="1.0.0",
                dimensions=DimensionManifest(),
                provenance=ProvenanceRecord(),
                outputs={},
            )
    
    def test_envelope_preserves_framework_outputs(self):
        """Envelope preserves framework-unique outputs unchanged."""
        outputs = {
            "sector_employment": {"Information": 0.85, "Finance": 0.91},
            "total_output": 1000000,
            "custom_metric": [1, 2, 3],
        }
        
        envelope = FrameworkOutputEnvelope(
            framework_slug="remsom",
            framework_version="1.0.0",
            dimensions=DimensionManifest(sectors=("Information", "Finance")),
            provenance=ProvenanceRecord(),
            outputs=outputs,
        )
        
        assert envelope.outputs == outputs
        assert envelope.outputs["sector_employment"]["Information"] == 0.85
    
    def test_serialization_roundtrip(self):
        """Envelope can be serialized and deserialized."""
        original = FrameworkOutputEnvelope(
            framework_slug="remsom",
            framework_version="1.0.0",
            dimensions=DimensionManifest(
                sectors=("Information", "Finance"),
                geography="Virginia",
            ),
            provenance=ProvenanceRecord(
                user_parameters={"n_sectors": 2},
            ),
            outputs={"employment_rate": 0.85},
        )
        
        d = original.to_dict()
        restored = FrameworkOutputEnvelope.from_dict(d)
        
        assert restored.framework_slug == "remsom"
        assert restored.dimensions.n_sectors == 2
        assert restored.dimensions.geography == "Virginia"
        assert restored.outputs["employment_rate"] == 0.85
    
    def test_dimension_validation_warnings(self):
        """validate_output_dimensions detects mismatches."""
        envelope = FrameworkOutputEnvelope(
            framework_slug="test",
            framework_version="1.0.0",
            dimensions=DimensionManifest(sectors=("A", "B", "C")),
            provenance=ProvenanceRecord(),
            outputs={
                # Keys don't match declared sectors
                "bad_output": {"X": 1, "Y": 2},
            },
        )
        
        warnings = envelope.validate_output_dimensions()
        assert len(warnings) > 0
        assert "bad_output" in warnings[0]


class TestDimensionalIntegrity:
    """
    Tests for the core contract: user selects N sectors → output has N sectors.
    
    This is the critical fix: eliminating dimensional drift where user
    selects 3 sectors but receives output for 10 hardcoded sectors.
    """
    
    def test_user_sector_selection_preserved(self):
        """User-selected sectors appear in output dimensions."""
        user_sectors = ["Information", "Finance", "Services"]
        
        manifest = DimensionManifest(sectors=tuple(user_sectors))
        envelope = FrameworkOutputEnvelope(
            framework_slug="remsom",
            framework_version="1.0.0",
            dimensions=manifest,
            provenance=ProvenanceRecord(
                user_parameters={"sector_names": user_sectors},
            ),
            outputs={
                "sector_output": {s: 100.0 for s in user_sectors},
            },
        )
        
        # Verify dimensional integrity
        assert len(envelope.dimensions.sectors) == 3
        assert set(envelope.dimensions.sectors) == set(user_sectors)
        assert set(envelope.outputs["sector_output"].keys()) == set(user_sectors)
    
    def test_no_extra_sectors_in_output(self):
        """Output contains only declared sectors, no extras."""
        declared_sectors = ("A", "B")
        
        envelope = FrameworkOutputEnvelope(
            framework_slug="test",
            framework_version="1.0.0",
            dimensions=DimensionManifest(sectors=declared_sectors),
            provenance=ProvenanceRecord(),
            outputs={
                "sector_output": {"A": 1, "B": 2},  # Correct
            },
        )
        
        # No extra sectors should appear
        assert "C" not in envelope.outputs["sector_output"]
        warnings = envelope.validate_output_dimensions()
        assert len(warnings) == 0


class TestREMSOMIntegration:
    """Integration tests for REMSOM envelope generation."""
    
    @pytest.fixture
    def remsom_framework(self):
        """Create a REMSOM framework for testing."""
        from krl_frameworks.layers.meta.remsom import REMSOMFramework, REMSOMConfig
        
        config = REMSOMConfig(
            n_sectors=3,
            sector_names=("Information", "Finance", "Services"),
            n_age_groups=3,
        )
        return REMSOMFramework(remsom_config=config)
    
    def test_remsom_config_sectors_appear_in_envelope(self, remsom_framework):
        """REMSOM uses config sector names in envelope."""
        # Create a mock result
        from krl_frameworks.core.base import FrameworkExecutionResult
        from krl_frameworks.core.state import CohortStateVector
        
        mock_state = CohortStateVector(
            employment_prob=np.array([0.7, 0.8, 0.75]),
            health_burden_score=np.array([0.2, 0.15, 0.18]),
            credit_access_prob=np.array([0.6, 0.7, 0.65]),
            housing_cost_ratio=np.array([0.3, 0.35, 0.32]),
            opportunity_score=np.array([0.5, 0.6, 0.55]),
            sector_output=np.array([[100, 200, 300], [110, 210, 310], [105, 205, 305]]),
            deprivation_vector=np.array([[0.1, 0.2, 0.3], [0.15, 0.25, 0.35], [0.12, 0.22, 0.32]]),
        )
        
        mock_result = FrameworkExecutionResult(
            execution_id="test-123",
            framework_slug="remsom",
            state=mock_state,
            metrics={
                "employment_rate": 0.75,
                "total_output": 1000,
                "sector_output": {"Information": 315, "Finance": 615, "Services": 915},
                "sector_employment": {"Information": 0.1, "Finance": 0.2, "Services": 0.45},
            },
            steps_executed=10,
            converged=True,
        )
        
        # Build envelope
        envelope = remsom_framework.build_output_envelope(
            mock_result,
            user_parameters={"sector_names": ["Information", "Finance", "Services"]},
        )
        
        # Verify dimensions match config
        assert envelope.dimensions.n_sectors == 3
        assert set(envelope.dimensions.sectors) == {"Information", "Finance", "Services"}
        
        # Verify outputs use canonical sector names
        assert "sector_output" in envelope.outputs
        assert set(envelope.outputs["sector_output"].keys()) == {"Information", "Finance", "Services"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
