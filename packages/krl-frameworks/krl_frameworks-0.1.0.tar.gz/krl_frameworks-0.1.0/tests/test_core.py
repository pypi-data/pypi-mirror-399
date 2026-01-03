# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Core Module Tests
# ════════════════════════════════════════════════════════════════════════════════

"""Tests for krl_frameworks.core module."""

from __future__ import annotations

import numpy as np
import pytest

from krl_frameworks.core import (
    BaseMetaFramework,
    CohortStateVector,
    DataBundle,
    FrameworkConfig,
    FrameworkMetadata,
    FrameworkRegistry,
    Tier,
    TierAccessError,
    TierContext,
    VerticalLayer,
    get_current_tier,
    register_framework,
    requires_tier,
    set_current_tier,
    tier_gate,
)
from krl_frameworks.core.exceptions import (
    DataBundleValidationError,
    FrameworkException,
    FrameworkNotFoundError,
    StateValidationError,
)


# ────────────────────────────────────────────────────────────────────────────────
# CohortStateVector Tests
# ────────────────────────────────────────────────────────────────────────────────


class TestCohortStateVector:
    """Tests for CohortStateVector dataclass."""

    def test_creation_with_valid_data(self, sample_cohort_state):
        """Test successful creation with valid numpy arrays."""
        assert sample_cohort_state.n_cohorts == 100
        assert sample_cohort_state.n_sectors == 10
        assert sample_cohort_state.n_deprivation_dimensions == 6

    def test_probability_bounds_validation(self):
        """Test that probability fields can be created with any values (validation is explicit)."""
        # CohortStateVector allows any values by default; validation is done via .validate()
        state = CohortStateVector(
            employment_prob=np.array([1.5]),  # Out of bounds but allowed at creation
            health_burden_score=np.array([0.1]),
            credit_access_prob=np.array([0.5]),
            housing_cost_ratio=np.array([0.3]),
            opportunity_score=np.array([0.5]),
            sector_output=np.zeros((1, 5)),
            deprivation_vector=np.zeros((1, 6)),
        )
        # Validation raises when explicitly called
        with pytest.raises(StateValidationError):
            state.validate()

    def test_zeros_factory(self):
        """Test CohortStateVector.zeros() factory method."""
        state = CohortStateVector.zeros(n_cohorts=50, n_sectors=8, n_deprivation_dims=4)
        assert state.n_cohorts == 50
        assert state.n_sectors == 8
        assert state.n_deprivation_dimensions == 4
        np.testing.assert_array_equal(state.employment_prob, np.zeros(50))

    def test_to_dict(self, sample_cohort_state):
        """Test CohortStateVector.to_dict() method."""
        d = sample_cohort_state.to_dict()
        assert "employment_prob" in d
        assert "n_cohorts" in d
        assert d["n_cohorts"] == 100

    def test_to_dataframe(self, sample_cohort_state):
        """Test CohortStateVector.to_dataframe() method."""
        df = sample_cohort_state.to_dataframe()
        assert len(df) == 100  # n_cohorts rows
        assert "employment_prob" in df.columns


# ────────────────────────────────────────────────────────────────────────────────
# DataBundle Tests
# ────────────────────────────────────────────────────────────────────────────────


class TestDataBundle:
    """Tests for DataBundle data injection container."""

    def test_creation_from_dataframes(self, sample_data_bundle):
        """Test DataBundle construction from pandas DataFrames."""
        assert "labor" in sample_data_bundle.domains
        assert "health" in sample_data_bundle.domains
        assert "education" in sample_data_bundle.domains

    def test_domain_access(self, sample_data_bundle):
        """Test accessing domain data via get()."""
        labor = sample_data_bundle.get("labor")
        assert labor is not None
        assert "employment_rate" in labor.data.columns

    def test_missing_domain_raises(self, sample_data_bundle):
        """Test accessing non-existent domain raises DataBundleValidationError."""
        with pytest.raises(DataBundleValidationError):
            sample_data_bundle.get("nonexistent")

    def test_has_domain(self, sample_data_bundle):
        """Test has_domain() method."""
        assert sample_data_bundle.has_domain("labor")
        assert not sample_data_bundle.has_domain("nonexistent")

    def test_content_hash_deterministic(self, sample_data_bundle):
        """Test that content hash is deterministic."""
        hash1 = sample_data_bundle.content_hash
        hash2 = sample_data_bundle.content_hash
        assert hash1 == hash2

    def test_empty_bundle_creation(self):
        """Test creating empty DataBundle."""
        bundle = DataBundle()
        assert len(bundle.domains) == 0


# ────────────────────────────────────────────────────────────────────────────────
# Tier Access Control Tests
# ────────────────────────────────────────────────────────────────────────────────


class TestTierAccessControl:
    """Tests for tier-based access control."""

    def test_default_tier_is_community(self):
        """Test that default tier is COMMUNITY."""
        # Reset to default
        set_current_tier(Tier.COMMUNITY)
        assert get_current_tier() == Tier.COMMUNITY

    def test_set_tier(self):
        """Test setting current tier."""
        set_current_tier(Tier.ENTERPRISE)
        assert get_current_tier() == Tier.ENTERPRISE
        # Reset
        set_current_tier(Tier.COMMUNITY)

    def test_tier_context_manager(self):
        """Test TierContext context manager."""
        set_current_tier(Tier.COMMUNITY)
        assert get_current_tier() == Tier.COMMUNITY
        
        with TierContext(Tier.PROFESSIONAL, user_id="test-user"):
            assert get_current_tier() == Tier.PROFESSIONAL
        
        assert get_current_tier() == Tier.COMMUNITY

    def test_requires_tier_decorator_allows_higher(self):
        """Test @requires_tier allows higher tiers."""
        @requires_tier(Tier.PROFESSIONAL)
        def pro_feature():
            return "success"
        
        set_current_tier(Tier.ENTERPRISE)
        assert pro_feature() == "success"
        set_current_tier(Tier.COMMUNITY)

    def test_requires_tier_decorator_blocks_lower(self):
        """Test @requires_tier blocks lower tiers."""
        @requires_tier(Tier.ENTERPRISE)
        def enterprise_feature():
            return "success"
        
        set_current_tier(Tier.COMMUNITY)
        with pytest.raises(TierAccessError):
            enterprise_feature()

    def test_tier_gate_function(self):
        """Test tier_gate() returns tier-appropriate values."""
        set_current_tier(Tier.COMMUNITY)
        assert tier_gate("community", "pro", "enterprise") == "community"
        
        set_current_tier(Tier.PROFESSIONAL)
        assert tier_gate("community", "pro", "enterprise") == "pro"
        
        set_current_tier(Tier.ENTERPRISE)
        assert tier_gate("community", "pro", "enterprise") == "enterprise"
        
        # Reset
        set_current_tier(Tier.COMMUNITY)

    def test_tier_hierarchy(self):
        """Test tier hierarchy ordering."""
        assert Tier.COMMUNITY < Tier.PROFESSIONAL
        assert Tier.PROFESSIONAL < Tier.TEAM
        assert Tier.TEAM < Tier.ENTERPRISE
        assert Tier.ENTERPRISE < Tier.CUSTOM


# ────────────────────────────────────────────────────────────────────────────────
# Framework Registry Tests
# ────────────────────────────────────────────────────────────────────────────────


class TestFrameworkRegistry:
    """Tests for FrameworkRegistry."""

    def test_registry_creation(self):
        """Test creating a new registry."""
        registry = FrameworkRegistry()
        assert len(registry) == 0

    def test_list_by_layer(self):
        """Test listing frameworks by layer."""
        registry = FrameworkRegistry()
        # Empty registry filtering
        socio_frameworks = registry.list_by_layer(VerticalLayer.SOCIOECONOMIC_ACADEMIC)
        assert len(socio_frameworks) == 0

    def test_list_by_tier(self):
        """Test listing frameworks by tier."""
        registry = FrameworkRegistry()
        set_current_tier(Tier.COMMUNITY)
        
        available = registry.list_by_tier(Tier.COMMUNITY)
        assert isinstance(available, list)


# ────────────────────────────────────────────────────────────────────────────────
# VerticalLayer Tests
# ────────────────────────────────────────────────────────────────────────────────


class TestVerticalLayer:
    """Tests for VerticalLayer enum."""

    def test_layer_values(self):
        """Test all 6 vertical layers exist."""
        assert VerticalLayer.SOCIOECONOMIC_ACADEMIC.value == 1
        assert VerticalLayer.GOVERNMENT_POLICY.value == 2
        assert VerticalLayer.EXPERIMENTAL_RESEARCH.value == 3
        assert VerticalLayer.FINANCIAL_ECONOMIC.value == 4
        assert VerticalLayer.ARTS_MEDIA_ENTERTAINMENT.value == 5
        assert VerticalLayer.META_PEER_FRAMEWORKS.value == 6


# ────────────────────────────────────────────────────────────────────────────────
# FrameworkConfig Tests
# ────────────────────────────────────────────────────────────────────────────────


class TestFrameworkConfig:
    """Tests for FrameworkConfig."""

    def test_default_config(self, default_config):
        """Test default configuration values."""
        assert default_config.simulation is not None
        assert default_config.n_sectors == 10

    def test_config_attributes(self, default_config):
        """Test config has expected attributes."""
        assert hasattr(default_config, "simulation")
        assert hasattr(default_config, "aggregation_method")
        assert hasattr(default_config, "n_sectors")
        assert hasattr(default_config, "n_deprivation_dims")


# ────────────────────────────────────────────────────────────────────────────────
# Exception Tests
# ────────────────────────────────────────────────────────────────────────────────


class TestExceptions:
    """Tests for exception hierarchy."""

    def test_framework_exception_base(self):
        """Test FrameworkException is base exception."""
        assert issubclass(TierAccessError, FrameworkException)
        assert issubclass(DataBundleValidationError, FrameworkException)
        assert issubclass(StateValidationError, FrameworkException)
        assert issubclass(FrameworkNotFoundError, FrameworkException)

    def test_tier_access_error(self):
        """Test TierAccessError can be raised."""
        with pytest.raises(TierAccessError):
            raise TierAccessError(
                "Access denied",
                required_tier=Tier.ENTERPRISE,
                current_tier=Tier.COMMUNITY,
            )

    def test_state_validation_error(self):
        """Test StateValidationError can be raised."""
        with pytest.raises(StateValidationError):
            raise StateValidationError("Invalid state")
