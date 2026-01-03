# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Bunching Estimator Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Bunching Estimator Framework.

Implements bunching analysis for policy evaluation:
- Notch and kink bunching estimation
- Counterfactual distribution construction
- Elasticity estimation from bunching
- Manipulation testing
- Frictions analysis

References:
    - Saez (2010) - Tax Notches and Bunching
    - Kleven & Waseem (2013) - Bunching Estimation Methods
    - Chetty et al. (2011) - Adjustment Costs and Bunching

Tier: PROFESSIONAL
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Mapping, Optional, Tuple

import numpy as np
from scipy import stats, optimize, interpolate

from krl_frameworks.core.base import (
    BaseMetaFramework,
    FrameworkMetadata,
    VerticalLayer,
)
from krl_frameworks.core.dashboard_spec import (
    FrameworkDashboardSpec,
    OutputViewSpec,
    ParameterGroupSpec,
    ViewType,
    ResultClass,
    TemporalSemantics,
)
from krl_frameworks.core.data_bundle import DataBundle
from krl_frameworks.core.state import CohortStateVector, StateTrajectory
from krl_frameworks.core.tier import Tier, requires_tier
from krl_frameworks.simulation.cbss import TransitionFunction

if TYPE_CHECKING:
    from krl_frameworks.core.config import FrameworkConfig

__all__ = ["BunchingFramework"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Bunching Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class BunchingType(Enum):
    """Types of bunching."""
    KINK = "Kink (marginal rate change)"
    NOTCH = "Notch (discrete jump)"


class PolicyType(Enum):
    """Types of policies that create bunching."""
    TAX_BRACKET = "Tax Bracket"
    BENEFIT_THRESHOLD = "Benefit Threshold"
    REGULATORY_LIMIT = "Regulatory Limit"
    PRICE_CEILING = "Price Ceiling"
    ELIGIBILITY_CUTOFF = "Eligibility Cutoff"


@dataclass
class ThresholdParams:
    """Parameters defining a bunching threshold."""
    
    threshold: float = 0.0  # The threshold value
    bunching_type: BunchingType = BunchingType.KINK
    policy_type: PolicyType = PolicyType.TAX_BRACKET
    
    # For kinks: marginal rate change
    rate_below: float = 0.0
    rate_above: float = 0.0
    
    # For notches: discrete change
    notch_size: float = 0.0  # e.g., tax increase at threshold


@dataclass
class BunchingWindow:
    """Definition of bunching analysis window."""
    
    lower_bound: float = 0.0  # Below threshold
    upper_bound: float = 0.0  # Above threshold
    
    # Exclusion window (dominated region for notches)
    exclude_lower: float = 0.0
    exclude_upper: float = 0.0
    
    # Bin width
    bin_width: float = 100.0


@dataclass
class CounterfactualDist:
    """Counterfactual distribution estimate."""
    
    # Polynomial fit parameters
    poly_order: int = 7
    coefficients: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Fitted values
    bin_centers: np.ndarray = field(default_factory=lambda: np.array([]))
    counterfactual_counts: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Integration constant
    integration_constraint: float = 0.0
    
    # Fit quality
    r_squared: float = 0.0


@dataclass
class BunchingEstimate:
    """Bunching estimation results."""
    
    # Excess bunching
    excess_mass: float = 0.0  # Excess bunching (b)
    excess_mass_se: float = 0.0  # Standard error
    
    # Normalized bunching
    normalized_bunching: float = 0.0  # b/h0
    
    # Missing mass (for notches)
    missing_mass: float = 0.0
    
    # Implied marginal buncher
    marginal_buncher: float = 0.0  # z* - z_threshold
    
    # Elasticity estimate
    elasticity: float = 0.0
    elasticity_se: float = 0.0
    
    # Confidence interval
    elasticity_ci_lower: float = 0.0
    elasticity_ci_upper: float = 0.0


@dataclass
class ManipulationTest:
    """McCrary density manipulation test results."""
    
    test_statistic: float = 0.0
    p_value: float = 0.0
    
    # Density estimates at threshold
    density_below: float = 0.0
    density_above: float = 0.0
    
    # Log difference
    log_diff: float = 0.0
    log_diff_se: float = 0.0
    
    # Manipulation detected
    manipulation_detected: bool = False


@dataclass
class FrictionsAnalysis:
    """Optimization frictions analysis."""
    
    # Friction parameters
    friction_share: float = 0.0  # Share of non-responders
    
    # Attenuation
    attenuation_factor: float = 0.0
    
    # Structural vs reduced form
    structural_elasticity: float = 0.0
    reduced_form_elasticity: float = 0.0
    
    # Diffuse bunching indicator
    diffuse_bunching: bool = False


@dataclass
class BunchingMetrics:
    """Complete bunching analysis metrics."""
    
    threshold: ThresholdParams = field(default_factory=ThresholdParams)
    window: BunchingWindow = field(default_factory=BunchingWindow)
    counterfactual: CounterfactualDist = field(default_factory=CounterfactualDist)
    estimate: BunchingEstimate = field(default_factory=BunchingEstimate)
    manipulation: ManipulationTest = field(default_factory=ManipulationTest)
    frictions: Optional[FrictionsAnalysis] = None


# ════════════════════════════════════════════════════════════════════════════════
# Bunching Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class BunchingTransition(TransitionFunction):
    """Transition function for bunching simulation."""
    
    name = "BunchingTransition"
    
    def __init__(self, elasticity: float = 0.25):
        self.elasticity = elasticity
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        params = params or {}
        
        threshold = params.get("threshold", 0.5)
        rate_change = params.get("rate_change", 0.1)
        
        # Simulate behavioral response
        response = self.elasticity * rate_change
        
        # Those near threshold bunch
        near_threshold = np.abs(state.opportunity_score - threshold) < 0.1
        adjustment = np.where(near_threshold, -response * 0.5, 0)
        
        new_opportunity = np.clip(state.opportunity_score + adjustment, 0, 1)
        
        return CohortStateVector(
            employment_prob=state.employment_prob,
            health_burden_score=state.health_burden_score,
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=new_opportunity,
            sector_output=state.sector_output,
            deprivation_vector=state.deprivation_vector,
        )


# ════════════════════════════════════════════════════════════════════════════════
# Bunching Framework
# ════════════════════════════════════════════════════════════════════════════════


class BunchingFramework(BaseMetaFramework):
    """
    Bunching Estimator Framework.
    
    Production-grade bunching analysis following Saez (2010) and Kleven-Waseem (2013):
    
    - Kink and notch bunching estimation
    - Counterfactual distribution construction
    - Elasticity estimation
    - McCrary manipulation testing
    - Frictions and attenuation analysis
    
    Token Weight: 5
    Tier: PROFESSIONAL
    
    Example:
        >>> framework = BunchingFramework()
        >>> result = framework.estimate_bunching(data, threshold=50000)
        >>> print(f"Elasticity: {result.estimate.elasticity:.3f}")
    
    References:
        - Saez (2010)
        - Kleven & Waseem (2013)
    """
    
    METADATA = FrameworkMetadata(
        slug="bunching",
        name="Bunching Estimator",
        version="1.0.0",
        layer=VerticalLayer.EXPERIMENTAL_RESEARCH,
        tier=Tier.PROFESSIONAL,
        description=(
            "Bunching estimator for policy evaluation using "
            "Saez (2010) and Kleven-Waseem (2013) methodology."
        ),
        required_domains=["running_variable", "threshold"],
        output_domains=["excess_mass", "elasticity", "counterfactual"],
        constituent_models=["polynomial_fit", "mccrary_test", "frictions"],
        tags=["bunching", "elasticity", "policy", "quasi-experimental"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(
        self,
        default_poly_order: int = 7,
        default_bin_width: float = 100.0,
        bootstrap_iterations: int = 500,
    ):
        super().__init__()
        self.default_poly_order = default_poly_order
        self.default_bin_width = default_bin_width
        self.bootstrap_iterations = bootstrap_iterations
        self._transition_fn = BunchingTransition()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        return cls.METADATA
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        n_cohorts = config.cohort_size or 100
        return CohortStateVector(
            employment_prob=np.full(n_cohorts, 0.70),
            health_burden_score=np.full(n_cohorts, 0.25),
            credit_access_prob=np.full(n_cohorts, 0.65),
            housing_cost_ratio=np.full(n_cohorts, 0.32),
            opportunity_score=np.random.uniform(0, 1, n_cohorts),
            sector_output=np.full((n_cohorts, 5), 1000.0),
            deprivation_vector=np.full((n_cohorts, 6), 0.25),
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        return self._transition_fn(state, t, config)
    
    def _compute_metrics(self, state: CohortStateVector) -> dict[str, Any]:
        return {
            "mean_opportunity": float(np.mean(state.opportunity_score)),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "bunching", "n_periods": trajectory.n_periods}

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return Bunching Estimator dashboard specification."""
        return FrameworkDashboardSpec(
            slug="bunching",
            name="Bunching Estimator",
            description=(
                "Bunching estimator for policy evaluation using "
                "Saez (2010) and Kleven-Waseem (2013) methodology."
            ),
            layer="experimental",
            parameters_schema={
                "type": "object",
                "properties": {
                    "bandwidth": {
                        "type": "number",
                        "title": "Bandwidth",
                        "minimum": 100.0,
                        "maximum": 10000.0,
                        "default": 1000.0,
                        "x-ui-widget": "slider",
                        "x-ui-group": "estimation",
                    },
                    "notch_location": {
                        "type": "number",
                        "title": "Notch/Kink Location",
                        "default": 50000.0,
                        "x-ui-widget": "number",
                        "x-ui-group": "design",
                    },
                    "polynomial_order": {
                        "type": "integer",
                        "title": "Polynomial Order",
                        "minimum": 3,
                        "maximum": 12,
                        "default": 7,
                        "x-ui-widget": "slider",
                        "x-ui-group": "estimation",
                    },
                    "bunching_type": {
                        "type": "string",
                        "title": "Bunching Type",
                        "enum": ["kink", "notch"],
                        "default": "kink",
                        "x-ui-widget": "select",
                        "x-ui-group": "design",
                    },
                },
            },
            default_parameters={"bandwidth": 1000.0, "notch_location": 50000.0, "polynomial_order": 7, "bunching_type": "kink"},
            parameter_groups=[
                ParameterGroupSpec(key="design", title="Design", parameters=["notch_location", "bunching_type"]),
                ParameterGroupSpec(key="estimation", title="Estimation", parameters=["bandwidth", "polynomial_order"]),
            ],
            required_domains=["running_variable", "threshold"],
            min_tier=Tier.PROFESSIONAL,
            output_views=[
                OutputViewSpec(
                    key="bunching_plot",
                    title="Bunching Plot",
                    view_type=ViewType.BAR_CHART,
                    config={"x_field": "bin_center", "y_field": "count", "counterfactual_line": True, "threshold_line": True},
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="bunching_plot_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="elasticity_estimate",
                    title="Elasticity Estimate",
                    view_type=ViewType.KPI_CARD,
                    config={"format": ".3f", "show_ci": True},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="elasticity_estimate_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="excess_mass",
                    title="Excess Mass Analysis",
                    view_type=ViewType.TABLE,
                    config={"columns": ["metric", "value", "std_error"]},
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="excess_mass_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )

    # ════════════════════════════════════════════════════════════════════════════
    # Public API Methods
    # ════════════════════════════════════════════════════════════════════════════
    
    @requires_tier(Tier.PROFESSIONAL)
    def create_bins(
        self,
        data: np.ndarray,
        threshold: float,
        window: BunchingWindow,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create histogram bins for bunching analysis.
        
        Args:
            data: Running variable data
            threshold: Policy threshold
            window: Bunching window specification
        
        Returns:
            Tuple of (bin_centers, counts)
        """
        # Define bins
        lower = threshold - window.lower_bound
        upper = threshold + window.upper_bound
        
        n_bins = int((upper - lower) / window.bin_width)
        bins = np.linspace(lower, upper, n_bins + 1)
        bin_centers = (bins[:-1] + bins[1:]) / 2
        
        # Count observations in each bin
        counts, _ = np.histogram(data, bins=bins)
        
        return bin_centers, counts.astype(float)
    
    @requires_tier(Tier.PROFESSIONAL)
    def fit_counterfactual(
        self,
        bin_centers: np.ndarray,
        counts: np.ndarray,
        threshold: float,
        window: BunchingWindow,
        poly_order: int = 7,
    ) -> CounterfactualDist:
        """
        Fit counterfactual distribution using polynomial.
        
        Args:
            bin_centers: Bin centers
            counts: Bin counts
            threshold: Policy threshold
            window: Bunching window
            poly_order: Polynomial order
        
        Returns:
            Counterfactual distribution
        """
        # Identify excluded region (bunching region)
        exclude_mask = (
            (bin_centers >= threshold - window.exclude_lower) &
            (bin_centers <= threshold + window.exclude_upper)
        )
        
        # Fit polynomial excluding bunching region
        fit_mask = ~exclude_mask
        
        if sum(fit_mask) < poly_order + 1:
            # Not enough data points
            logger.warning("Insufficient data for polynomial fit")
            return CounterfactualDist(poly_order=poly_order)
        
        # Normalize for numerical stability
        x_norm = (bin_centers - threshold) / window.lower_bound
        
        try:
            # Fit polynomial to non-excluded region
            coeffs = np.polyfit(x_norm[fit_mask], counts[fit_mask], poly_order)
            poly = np.poly1d(coeffs)
            
            # Predict counterfactual for all bins
            counterfactual = poly(x_norm)
            counterfactual = np.maximum(counterfactual, 0)  # Non-negative counts
            
            # R-squared
            ss_res = np.sum((counts[fit_mask] - poly(x_norm[fit_mask])) ** 2)
            ss_tot = np.sum((counts[fit_mask] - np.mean(counts[fit_mask])) ** 2)
            r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0
            
            # Integration constraint (excess mass = missing mass)
            excess = np.sum(counts[exclude_mask] - counterfactual[exclude_mask])
            
            return CounterfactualDist(
                poly_order=poly_order,
                coefficients=coeffs,
                bin_centers=bin_centers,
                counterfactual_counts=counterfactual,
                integration_constraint=excess,
                r_squared=r_squared,
            )
            
        except Exception as e:
            logger.error(f"Counterfactual fit failed: {e}")
            return CounterfactualDist(poly_order=poly_order)
    
    @requires_tier(Tier.PROFESSIONAL)
    def compute_excess_mass(
        self,
        counts: np.ndarray,
        counterfactual: CounterfactualDist,
        threshold: float,
        window: BunchingWindow,
    ) -> Tuple[float, float]:
        """
        Compute excess bunching mass.
        
        Args:
            counts: Observed counts
            counterfactual: Counterfactual distribution
            threshold: Policy threshold
            window: Bunching window
        
        Returns:
            Tuple of (excess_mass, normalized_bunching)
        """
        bin_centers = counterfactual.bin_centers
        cf_counts = counterfactual.counterfactual_counts
        
        # Bunching region
        bunch_mask = (
            (bin_centers >= threshold - window.exclude_lower) &
            (bin_centers <= threshold + window.exclude_upper)
        )
        
        # Excess mass
        excess = np.sum(counts[bunch_mask]) - np.sum(cf_counts[bunch_mask])
        
        # Normalize by counterfactual height at threshold
        threshold_idx = np.argmin(np.abs(bin_centers - threshold))
        h0 = cf_counts[threshold_idx] if threshold_idx < len(cf_counts) else 1
        
        normalized = excess / h0 if h0 > 0 else 0
        
        return excess, normalized
    
    @requires_tier(Tier.PROFESSIONAL)
    def estimate_elasticity_kink(
        self,
        normalized_bunching: float,
        rate_below: float,
        rate_above: float,
        threshold: float,
    ) -> float:
        """
        Estimate elasticity from kink bunching.
        
        Following Saez (2010):
        e = b / (log(1-t1) - log(1-t0)) * z*
        
        Args:
            normalized_bunching: Normalized excess bunching
            rate_below: Marginal rate below threshold
            rate_above: Marginal rate above threshold
            threshold: Policy threshold
        
        Returns:
            Elasticity estimate
        """
        # Net-of-tax rate change
        log_change = np.log(1 - rate_above) - np.log(1 - rate_below)
        
        if abs(log_change) < 1e-10:
            return 0.0
        
        # Simplified elasticity (assuming marginal buncher at threshold)
        elasticity = normalized_bunching / abs(log_change)
        
        return elasticity
    
    @requires_tier(Tier.PROFESSIONAL)
    def estimate_elasticity_notch(
        self,
        excess_mass: float,
        missing_mass: float,
        notch_size: float,
        threshold: float,
        counterfactual: CounterfactualDist,
    ) -> float:
        """
        Estimate elasticity from notch bunching.
        
        Following Kleven & Waseem (2013).
        
        Args:
            excess_mass: Excess bunching mass
            missing_mass: Missing mass above threshold
            notch_size: Size of notch (discrete jump)
            threshold: Policy threshold
            counterfactual: Counterfactual distribution
        
        Returns:
            Elasticity estimate
        """
        # Find marginal buncher (where missing mass ends)
        cf = counterfactual.counterfactual_counts
        centers = counterfactual.bin_centers
        
        # Above threshold
        above_mask = centers > threshold
        above_centers = centers[above_mask]
        
        if len(above_centers) == 0:
            return 0.0
        
        # z* - z: distance of marginal buncher
        # Simplified: use integration constraint
        delta_z = excess_mass / (np.mean(cf[above_mask]) + 1e-10)
        
        # Elasticity from notch
        # e = (z* - z) / z / notch_size
        if threshold > 0 and notch_size > 0:
            elasticity = delta_z / threshold / notch_size
        else:
            elasticity = 0.0
        
        return elasticity
    
    @requires_tier(Tier.PROFESSIONAL)
    def mccrary_test(
        self,
        data: np.ndarray,
        threshold: float,
        bandwidth: Optional[float] = None,
    ) -> ManipulationTest:
        """
        McCrary density discontinuity test.
        
        Args:
            data: Running variable
            threshold: Threshold to test
            bandwidth: Bandwidth for local linear regression
        
        Returns:
            Manipulation test results
        """
        # Default bandwidth (Silverman's rule)
        if bandwidth is None:
            bandwidth = 1.06 * np.std(data) * len(data) ** (-1/5)
        
        # Split data
        below = data[data < threshold]
        above = data[data >= threshold]
        
        if len(below) < 10 or len(above) < 10:
            return ManipulationTest(manipulation_detected=False)
        
        # Estimate densities at threshold using local linear regression
        # Simplified: use kernel density estimation
        try:
            kde_below = stats.gaussian_kde(below, bw_method=bandwidth / np.std(below))
            kde_above = stats.gaussian_kde(above, bw_method=bandwidth / np.std(above))
            
            # Evaluate at threshold
            f_below = float(kde_below(threshold - 0.001)[0])
            f_above = float(kde_above(threshold + 0.001)[0])
            
            # Log difference
            if f_below > 0 and f_above > 0:
                log_diff = np.log(f_above) - np.log(f_below)
            else:
                log_diff = 0.0
            
            # Standard error (bootstrap would be better)
            n = len(data)
            se = np.sqrt(1 / (n * bandwidth) * (1/f_below + 1/f_above)) if f_below > 0 and f_above > 0 else 1.0
            
            # Test statistic
            t_stat = log_diff / se if se > 0 else 0
            p_value = 2 * (1 - stats.norm.cdf(abs(t_stat)))
            
            return ManipulationTest(
                test_statistic=t_stat,
                p_value=p_value,
                density_below=f_below,
                density_above=f_above,
                log_diff=log_diff,
                log_diff_se=se,
                manipulation_detected=p_value < 0.05,
            )
            
        except Exception as e:
            logger.error(f"McCrary test failed: {e}")
            return ManipulationTest(manipulation_detected=False)
    
    @requires_tier(Tier.PROFESSIONAL)
    def bootstrap_standard_errors(
        self,
        data: np.ndarray,
        threshold: ThresholdParams,
        window: BunchingWindow,
        n_iterations: int = 500,
    ) -> Tuple[float, float]:
        """
        Bootstrap standard errors for bunching estimate.
        
        Args:
            data: Running variable data
            threshold: Threshold parameters
            window: Bunching window
            n_iterations: Number of bootstrap iterations
        
        Returns:
            Tuple of (elasticity_se, excess_mass_se)
        """
        elasticities = []
        excess_masses = []
        
        n = len(data)
        
        for _ in range(n_iterations):
            # Bootstrap sample
            sample = np.random.choice(data, size=n, replace=True)
            
            # Estimate bunching
            try:
                bin_centers, counts = self.create_bins(sample, threshold.threshold, window)
                cf = self.fit_counterfactual(bin_centers, counts, threshold.threshold, window)
                excess, normalized = self.compute_excess_mass(counts, cf, threshold.threshold, window)
                
                if threshold.bunching_type == BunchingType.KINK:
                    e = self.estimate_elasticity_kink(
                        normalized,
                        threshold.rate_below,
                        threshold.rate_above,
                        threshold.threshold,
                    )
                else:
                    e = self.estimate_elasticity_notch(
                        excess, 0, threshold.notch_size,
                        threshold.threshold, cf,
                    )
                
                elasticities.append(e)
                excess_masses.append(excess)
                
            except Exception:
                continue
        
        if len(elasticities) > 10:
            elasticity_se = float(np.std(elasticities))
            excess_mass_se = float(np.std(excess_masses))
        else:
            elasticity_se = 0.0
            excess_mass_se = 0.0
        
        return elasticity_se, excess_mass_se
    
    @requires_tier(Tier.PROFESSIONAL)
    def estimate_bunching(
        self,
        data: np.ndarray,
        threshold: float,
        bunching_type: BunchingType = BunchingType.KINK,
        rate_below: float = 0.0,
        rate_above: float = 0.0,
        notch_size: float = 0.0,
        window_width: float = 0.15,  # As fraction of threshold
        exclude_width: float = 0.02,  # As fraction of threshold
    ) -> BunchingEstimate:
        """
        Main bunching estimation method.
        
        Args:
            data: Running variable data
            threshold: Policy threshold
            bunching_type: Kink or notch
            rate_below: Marginal rate below (for kinks)
            rate_above: Marginal rate above (for kinks)
            notch_size: Notch size (for notches)
            window_width: Analysis window as fraction of threshold
            exclude_width: Exclusion window as fraction of threshold
        
        Returns:
            Bunching estimate
        """
        # Setup parameters
        thresh_params = ThresholdParams(
            threshold=threshold,
            bunching_type=bunching_type,
            rate_below=rate_below,
            rate_above=rate_above,
            notch_size=notch_size,
        )
        
        window = BunchingWindow(
            lower_bound=threshold * window_width,
            upper_bound=threshold * window_width,
            exclude_lower=threshold * exclude_width,
            exclude_upper=threshold * exclude_width,
            bin_width=threshold * 0.01,  # 1% bins
        )
        
        # Create bins and fit counterfactual
        bin_centers, counts = self.create_bins(data, threshold, window)
        counterfactual = self.fit_counterfactual(bin_centers, counts, threshold, window)
        
        # Compute excess mass
        excess, normalized = self.compute_excess_mass(counts, counterfactual, threshold, window)
        
        # Estimate elasticity
        if bunching_type == BunchingType.KINK:
            elasticity = self.estimate_elasticity_kink(
                normalized, rate_below, rate_above, threshold
            )
        else:
            elasticity = self.estimate_elasticity_notch(
                excess, 0, notch_size, threshold, counterfactual
            )
        
        # Bootstrap standard errors
        e_se, m_se = self.bootstrap_standard_errors(
            data, thresh_params, window,
            n_iterations=min(100, self.bootstrap_iterations),  # Faster
        )
        
        # Confidence interval
        ci_lower = elasticity - 1.96 * e_se
        ci_upper = elasticity + 1.96 * e_se
        
        return BunchingEstimate(
            excess_mass=excess,
            excess_mass_se=m_se,
            normalized_bunching=normalized,
            missing_mass=0.0,  # Would compute for notches
            marginal_buncher=excess / (np.mean(counts) + 1e-10),
            elasticity=elasticity,
            elasticity_se=e_se,
            elasticity_ci_lower=ci_lower,
            elasticity_ci_upper=ci_upper,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def full_analysis(
        self,
        data: np.ndarray,
        threshold: float,
        bunching_type: BunchingType = BunchingType.KINK,
        rate_below: float = 0.0,
        rate_above: float = 0.0,
        notch_size: float = 0.0,
    ) -> BunchingMetrics:
        """
        Complete bunching analysis.
        
        Args:
            data: Running variable data
            threshold: Policy threshold
            bunching_type: Kink or notch
            rate_below: Marginal rate below
            rate_above: Marginal rate above
            notch_size: Notch size
        
        Returns:
            Complete bunching metrics
        """
        # Setup
        thresh_params = ThresholdParams(
            threshold=threshold,
            bunching_type=bunching_type,
            rate_below=rate_below,
            rate_above=rate_above,
            notch_size=notch_size,
        )
        
        window = BunchingWindow(
            lower_bound=threshold * 0.15,
            upper_bound=threshold * 0.15,
            exclude_lower=threshold * 0.02,
            exclude_upper=threshold * 0.02,
            bin_width=threshold * 0.01,
        )
        
        # Binning and counterfactual
        bin_centers, counts = self.create_bins(data, threshold, window)
        counterfactual = self.fit_counterfactual(bin_centers, counts, threshold, window)
        
        # Main estimate
        estimate = self.estimate_bunching(
            data, threshold, bunching_type,
            rate_below, rate_above, notch_size,
        )
        
        # McCrary test
        manipulation = self.mccrary_test(data, threshold)
        
        # Frictions (simplified)
        frictions = FrictionsAnalysis(
            friction_share=0.2,  # Would estimate from diffuse bunching
            attenuation_factor=0.8,
            structural_elasticity=estimate.elasticity / 0.8,
            reduced_form_elasticity=estimate.elasticity,
            diffuse_bunching=estimate.normalized_bunching < 0.5,
        )
        
        return BunchingMetrics(
            threshold=thresh_params,
            window=window,
            counterfactual=counterfactual,
            estimate=estimate,
            manipulation=manipulation,
            frictions=frictions,
        )
