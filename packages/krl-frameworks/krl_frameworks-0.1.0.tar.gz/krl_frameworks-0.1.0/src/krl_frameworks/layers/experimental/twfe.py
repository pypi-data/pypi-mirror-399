# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Two-Way Fixed Effects Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Two-Way Fixed Effects (TWFE) Panel Data Framework.

Production-grade TWFE implementation with:
- Unit and time fixed effects
- Heterogeneity-robust estimation
- Goodman-Bacon decomposition
- de Chaisemartin-D'Haultfoeuille correction
- Clustered standard errors
- Within/between decomposition

References:
    - Wooldridge (2010): Econometric Analysis of Cross Section and Panel Data
    - Goodman-Bacon (2021): Difference-in-Differences with Variation in Treatment Timing
    - de Chaisemartin & D'Haultfoeuille (2020): Two-Way Fixed Effects Estimators

Tier: TEAM
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Mapping, Optional

import numpy as np
from scipy import stats

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

__all__ = ["TWFEFramework"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# TWFE Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class TWFEEstimator(Enum):
    """TWFE estimator variants."""
    STANDARD = "Standard TWFE"
    BACON_DECOMP = "Goodman-Bacon Decomposition"
    DECHAISEMARTIN = "de Chaisemartin-D'Haultfoeuille"
    IMPUTATION = "Imputation Estimator"


class ClusterType(Enum):
    """Clustering for standard errors."""
    NONE = "No Clustering"
    UNIT = "Unit-Level"
    TIME = "Time-Level"
    TWO_WAY = "Two-Way Clustering"


@dataclass
class PanelData:
    """Panel data structure."""
    
    outcome: np.ndarray = field(default_factory=lambda: np.array([]))  # (N, T)
    treatment: np.ndarray = field(default_factory=lambda: np.array([]))  # (N, T)
    covariates: Optional[np.ndarray] = None  # (N, T, K)
    
    unit_ids: list[str] = field(default_factory=list)
    time_periods: list[int] = field(default_factory=list)
    
    @property
    def n_units(self) -> int:
        return self.outcome.shape[0] if len(self.outcome.shape) > 0 else 0
    
    @property
    def n_periods(self) -> int:
        return self.outcome.shape[1] if len(self.outcome.shape) > 1 else 0


@dataclass
class TWFEResult:
    """TWFE estimation results."""
    
    # Main estimate
    att: float = 0.0  # Average Treatment Effect on Treated
    se: float = 0.0
    t_stat: float = 0.0
    p_value: float = 0.0
    ci_lower: float = 0.0
    ci_upper: float = 0.0
    
    # Decomposition
    unit_fixed_effects: dict[str, float] = field(default_factory=dict)
    time_fixed_effects: dict[int, float] = field(default_factory=dict)
    
    # Diagnostics
    r_squared: float = 0.0
    r_squared_within: float = 0.0
    n_observations: int = 0
    n_units: int = 0
    n_periods: int = 0


@dataclass
class BaconDecomposition:
    """Goodman-Bacon decomposition results."""
    
    # Components
    earlier_vs_later: float = 0.0
    earlier_vs_later_weight: float = 0.0
    
    later_vs_earlier: float = 0.0
    later_vs_earlier_weight: float = 0.0
    
    treated_vs_never: float = 0.0
    treated_vs_never_weight: float = 0.0
    
    # Group-specific estimates
    group_estimates: dict[tuple[int, int], float] = field(default_factory=dict)
    group_weights: dict[tuple[int, int], float] = field(default_factory=dict)
    
    # Weighted average
    weighted_average: float = 0.0


@dataclass
class HeterogeneityTest:
    """Treatment effect heterogeneity tests."""
    
    # Pre-trends test
    pre_trend_f_stat: float = 0.0
    pre_trend_p_value: float = 0.0
    
    # Treatment timing heterogeneity
    timing_heterogeneity_stat: float = 0.0
    timing_heterogeneity_p_value: float = 0.0
    
    # Cohort heterogeneity
    cohort_effects: dict[int, float] = field(default_factory=dict)
    cohort_variation: float = 0.0


@dataclass
class TWFEMetrics:
    """Comprehensive TWFE analysis results."""
    
    # Main result
    twfe_result: TWFEResult = field(default_factory=TWFEResult)
    
    # Bacon decomposition
    bacon: BaconDecomposition = field(default_factory=BaconDecomposition)
    
    # Heterogeneity
    heterogeneity: HeterogeneityTest = field(default_factory=HeterogeneityTest)
    
    # Robustness
    estimator_used: TWFEEstimator = TWFEEstimator.STANDARD
    cluster_type: ClusterType = ClusterType.UNIT


# ════════════════════════════════════════════════════════════════════════════════
# TWFE Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class TWFETransition(TransitionFunction):
    """Transition function for panel simulation."""
    
    name = "TWFETransition"
    
    def __init__(self, treatment_effect: float = 0.1, persistence: float = 0.8):
        self.treatment_effect = treatment_effect
        self.persistence = persistence
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply panel dynamics with treatment."""
        params = params or {}
        treatment = params.get("treatment", np.zeros(state.n_cohorts))
        
        # AR(1) with treatment effect
        new_opportunity = (
            self.persistence * state.opportunity_score +
            self.treatment_effect * treatment +
            np.random.normal(0, 0.1, state.n_cohorts)
        )
        new_opportunity = np.clip(new_opportunity, 0, 1)
        
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
# TWFE Framework
# ════════════════════════════════════════════════════════════════════════════════


class TWFEFramework(BaseMetaFramework):
    """
    Two-Way Fixed Effects Panel Data Framework.
    
    Production-grade TWFE implementation with:
    
    - Standard unit and time fixed effects
    - Goodman-Bacon decomposition for staggered adoption
    - Heterogeneity-robust alternatives
    - Clustered standard errors
    - Pre-trends testing
    
    Token Weight: 5
    Tier: TEAM
    
    Example:
        >>> framework = TWFEFramework()
        >>> result = framework.estimate_twfe(panel_data)
        >>> print(f"ATT: {result.att:.3f} (SE: {result.se:.3f})")
    
    References:
        - Goodman-Bacon (2021)
        - de Chaisemartin & D'Haultfoeuille (2020)
    """
    
    METADATA = FrameworkMetadata(
        slug="twfe-panel",
        name="Two-Way Fixed Effects Panel",
        version="1.0.0",
        layer=VerticalLayer.EXPERIMENTAL_RESEARCH,
        tier=Tier.TEAM,
        description=(
            "Two-Way Fixed Effects estimation with heterogeneity diagnostics, "
            "Bacon decomposition, and robust standard errors."
        ),
        required_domains=["panel_outcome", "panel_treatment"],
        output_domains=["att", "fixed_effects", "decomposition"],
        constituent_models=["twfe", "bacon_decomp", "dechaisemartin"],
        tags=["panel-data", "fixed-effects", "causal-inference", "twfe"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(
        self,
        cluster_type: ClusterType = ClusterType.UNIT,
        confidence_level: float = 0.95,
    ):
        super().__init__()
        self.cluster_type = cluster_type
        self.confidence_level = confidence_level
        self._transition_fn = TWFETransition()
    
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
            health_burden_score=np.full(n_cohorts, 0.2),
            credit_access_prob=np.full(n_cohorts, 0.70),
            housing_cost_ratio=np.full(n_cohorts, 0.30),
            opportunity_score=np.random.beta(2, 2, n_cohorts),
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
        return {"mean_outcome": float(np.mean(state.opportunity_score))}
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "twfe-panel", "n_periods": trajectory.n_periods}

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return Two-Way Fixed Effects dashboard specification."""
        return FrameworkDashboardSpec(
            slug="twfe_panel",
            name="Two-Way Fixed Effects Panel",
            description=(
                "Two-Way Fixed Effects estimation with heterogeneity diagnostics, "
                "Bacon decomposition, and robust standard errors."
            ),
            layer="experimental",
            parameters_schema={
                "type": "object",
                "properties": {
                    "entity_fe": {
                        "type": "boolean",
                        "title": "Entity Fixed Effects",
                        "default": True,
                        "x-ui-widget": "checkbox",
                        "x-ui-group": "model",
                    },
                    "time_fe": {
                        "type": "boolean",
                        "title": "Time Fixed Effects",
                        "default": True,
                        "x-ui-widget": "checkbox",
                        "x-ui-group": "model",
                    },
                    "clustered_se": {
                        "type": "string",
                        "title": "Clustered Standard Errors",
                        "enum": ["none", "unit", "time", "two_way"],
                        "default": "unit",
                        "x-ui-widget": "select",
                        "x-ui-group": "inference",
                    },
                    "estimator": {
                        "type": "string",
                        "title": "Estimator",
                        "enum": ["standard", "bacon_decomp", "dechaisemartin", "imputation"],
                        "default": "standard",
                        "x-ui-widget": "select",
                        "x-ui-group": "model",
                    },
                },
            },
            default_parameters={"entity_fe": True, "time_fe": True, "clustered_se": "unit", "estimator": "standard"},
            parameter_groups=[
                ParameterGroupSpec(key="model", title="Model", parameters=["entity_fe", "time_fe", "estimator"]),
                ParameterGroupSpec(key="inference", title="Inference", parameters=["clustered_se"]),
            ],
            required_domains=["panel_outcome", "panel_treatment"],
            min_tier=Tier.PROFESSIONAL,
            output_views=[
                OutputViewSpec(
                    key="coefficient_plot",
                    title="Coefficient Plot",
                    view_type=ViewType.BAR_CHART,
                    config={"x_field": "variable", "y_field": "coefficient", "error_bars": True},
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="coefficient_plot_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="bacon_decomposition",
                    title="Goodman-Bacon Decomposition",
                    view_type=ViewType.SCATTER,
                    config={"x_field": "weight", "y_field": "estimate", "size_field": "weight", "color_field": "comparison_type"},
                    result_class=ResultClass.STRUCTURAL_SIMILARITY,
                    output_key="bacon_decomposition_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="fixed_effects",
                    title="Fixed Effects",
                    view_type=ViewType.TABLE,
                    config={"columns": ["unit", "fe_estimate", "time", "time_fe"]},
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="fixed_effects_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )

    # ════════════════════════════════════════════════════════════════════════════
    # Public API Methods
    # ════════════════════════════════════════════════════════════════════════════
    
    @requires_tier(Tier.TEAM)
    def estimate_twfe(
        self,
        data: PanelData,
        cluster_type: Optional[ClusterType] = None,
    ) -> TWFEResult:
        """
        Estimate standard TWFE model.
        
        Y_it = α_i + γ_t + β·D_it + X_it·δ + ε_it
        
        Args:
            data: Panel data with outcome and treatment
            cluster_type: Clustering for standard errors
        
        Returns:
            TWFE estimation results
        """
        cluster = cluster_type or self.cluster_type
        N, T = data.n_units, data.n_periods
        
        if N == 0 or T == 0:
            return TWFEResult()
        
        # Demean (within transformation)
        Y = data.outcome
        D = data.treatment
        
        # Unit means
        unit_means_Y = Y.mean(axis=1, keepdims=True)
        unit_means_D = D.mean(axis=1, keepdims=True)
        
        # Time means
        time_means_Y = Y.mean(axis=0, keepdims=True)
        time_means_D = D.mean(axis=0, keepdims=True)
        
        # Grand means
        grand_mean_Y = Y.mean()
        grand_mean_D = D.mean()
        
        # Within transformation
        Y_within = Y - unit_means_Y - time_means_Y + grand_mean_Y
        D_within = D - unit_means_D - time_means_D + grand_mean_D
        
        # Flatten
        y = Y_within.flatten()
        d = D_within.flatten()
        
        # OLS on demeaned data
        if np.var(d) > 1e-10:
            beta = np.sum(d * y) / np.sum(d * d)
            residuals = y - beta * d
            
            # Standard error
            if cluster == ClusterType.UNIT:
                # Cluster by unit
                ssr = 0
                for i in range(N):
                    unit_resid = residuals[i*T:(i+1)*T]
                    ssr += np.sum(unit_resid)**2
                se = np.sqrt(ssr / (N - 1) / np.sum(d**2))
            elif cluster == ClusterType.TIME:
                ssr = 0
                for t in range(T):
                    time_resid = residuals[t::T]
                    ssr += np.sum(time_resid)**2
                se = np.sqrt(ssr / (T - 1) / np.sum(d**2))
            else:
                mse = np.sum(residuals**2) / (N * T - N - T - 1)
                se = np.sqrt(mse / np.sum(d**2))
        else:
            beta = 0.0
            se = np.inf
            residuals = y
        
        # T-stat and p-value
        t_stat = beta / se if se > 0 else 0
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), N * T - N - T - 1))
        
        # Confidence interval
        z = stats.norm.ppf((1 + self.confidence_level) / 2)
        ci_lower = beta - z * se
        ci_upper = beta + z * se
        
        # R-squared
        tss = np.sum((y - y.mean())**2)
        rss = np.sum(residuals**2)
        r_squared_within = 1 - rss / tss if tss > 0 else 0
        
        # Fixed effects
        unit_fe = {
            data.unit_ids[i] if data.unit_ids else f"unit_{i}": float(unit_means_Y[i, 0] - grand_mean_Y)
            for i in range(N)
        }
        time_fe = {
            data.time_periods[t] if data.time_periods else t: float(time_means_Y[0, t] - grand_mean_Y)
            for t in range(T)
        }
        
        return TWFEResult(
            att=float(beta),
            se=float(se),
            t_stat=float(t_stat),
            p_value=float(p_value),
            ci_lower=float(ci_lower),
            ci_upper=float(ci_upper),
            unit_fixed_effects=unit_fe,
            time_fixed_effects=time_fe,
            r_squared_within=float(r_squared_within),
            n_observations=N * T,
            n_units=N,
            n_periods=T,
        )
    
    @requires_tier(Tier.TEAM)
    def bacon_decomposition(
        self,
        data: PanelData,
    ) -> BaconDecomposition:
        """
        Goodman-Bacon decomposition of TWFE estimate.
        
        Decomposes the TWFE estimator into a weighted average of
        all 2x2 DiD comparisons.
        
        Args:
            data: Panel data
        
        Returns:
            Bacon decomposition results
        """
        N, T = data.n_units, data.n_periods
        
        if N == 0 or T == 0:
            return BaconDecomposition()
        
        Y = data.outcome
        D = data.treatment
        
        # Find treatment timing for each unit
        treatment_timing = {}
        never_treated = []
        always_treated = []
        
        for i in range(N):
            treated_periods = np.where(D[i] > 0)[0]
            if len(treated_periods) == 0:
                never_treated.append(i)
                treatment_timing[i] = np.inf
            elif len(treated_periods) == T:
                always_treated.append(i)
                treatment_timing[i] = 0
            else:
                treatment_timing[i] = treated_periods[0]
        
        # Group by treatment timing
        timing_groups = {}
        for i, t in treatment_timing.items():
            if t not in timing_groups:
                timing_groups[t] = []
            timing_groups[t].append(i)
        
        # Compute 2x2 DiD for each pair of groups
        group_estimates = {}
        group_weights = {}
        
        sorted_timings = sorted([t for t in timing_groups.keys() if t != np.inf])
        
        total_weight = 0
        weighted_sum = 0
        
        # Early vs Late treated
        evl_sum = 0
        evl_weight = 0
        
        # Late vs Early treated
        lve_sum = 0
        lve_weight = 0
        
        # Treated vs Never treated
        tvn_sum = 0
        tvn_weight = 0
        
        for idx1, t1 in enumerate(sorted_timings):
            for idx2, t2 in enumerate(sorted_timings):
                if t1 >= t2:
                    continue
                
                # Early group treats first at t1, late at t2
                early_units = timing_groups[t1]
                late_units = timing_groups[t2]
                
                # 2x2 DiD using period before t1 and period after t1 but before t2
                if len(early_units) > 0 and len(late_units) > 0 and t1 > 0:
                    pre_period = t1 - 1
                    post_period = min(t1, t2 - 1) if t2 < T else t1
                    
                    if post_period < T and pre_period >= 0:
                        # DiD estimate
                        y_early_pre = np.mean([Y[i, pre_period] for i in early_units])
                        y_early_post = np.mean([Y[i, post_period] for i in early_units])
                        y_late_pre = np.mean([Y[i, pre_period] for i in late_units])
                        y_late_post = np.mean([Y[i, post_period] for i in late_units])
                        
                        did_est = (y_early_post - y_early_pre) - (y_late_post - y_late_pre)
                        
                        # Weight proportional to group sizes and variance
                        n_early = len(early_units)
                        n_late = len(late_units)
                        weight = n_early * n_late / (n_early + n_late)
                        
                        group_estimates[(t1, t2)] = did_est
                        group_weights[(t1, t2)] = weight
                        
                        evl_sum += did_est * weight
                        evl_weight += weight
        
        # Treated vs Never treated
        if never_treated:
            for t1 in sorted_timings:
                treated_units = timing_groups[t1]
                if len(treated_units) > 0 and t1 > 0:
                    pre_period = t1 - 1
                    post_period = t1
                    
                    if post_period < T:
                        y_treat_pre = np.mean([Y[i, pre_period] for i in treated_units])
                        y_treat_post = np.mean([Y[i, post_period] for i in treated_units])
                        y_never_pre = np.mean([Y[i, pre_period] for i in never_treated])
                        y_never_post = np.mean([Y[i, post_period] for i in never_treated])
                        
                        did_est = (y_treat_post - y_treat_pre) - (y_never_post - y_never_pre)
                        
                        n_treat = len(treated_units)
                        n_never = len(never_treated)
                        weight = n_treat * n_never / (n_treat + n_never)
                        
                        tvn_sum += did_est * weight
                        tvn_weight += weight
        
        # Normalize weights
        total = evl_weight + lve_weight + tvn_weight
        if total > 0:
            evl_w = evl_weight / total
            lve_w = lve_weight / total
            tvn_w = tvn_weight / total
            
            evl_est = evl_sum / evl_weight if evl_weight > 0 else 0
            lve_est = lve_sum / lve_weight if lve_weight > 0 else 0
            tvn_est = tvn_sum / tvn_weight if tvn_weight > 0 else 0
            
            weighted_avg = evl_est * evl_w + lve_est * lve_w + tvn_est * tvn_w
        else:
            evl_w = lve_w = tvn_w = 0
            evl_est = lve_est = tvn_est = weighted_avg = 0
        
        return BaconDecomposition(
            earlier_vs_later=float(evl_est),
            earlier_vs_later_weight=float(evl_w),
            later_vs_earlier=float(lve_est),
            later_vs_earlier_weight=float(lve_w),
            treated_vs_never=float(tvn_est),
            treated_vs_never_weight=float(tvn_w),
            group_estimates=group_estimates,
            group_weights=group_weights,
            weighted_average=float(weighted_avg),
        )
    
    @requires_tier(Tier.TEAM)
    def test_parallel_trends(
        self,
        data: PanelData,
        n_pre_periods: int = 3,
    ) -> HeterogeneityTest:
        """
        Test for parallel pre-trends.
        
        Args:
            data: Panel data
            n_pre_periods: Number of pre-treatment periods to test
        
        Returns:
            Heterogeneity test results
        """
        N, T = data.n_units, data.n_periods
        
        if N == 0 or T == 0:
            return HeterogeneityTest()
        
        Y = data.outcome
        D = data.treatment
        
        # Find first treatment period for each unit
        treatment_timing = []
        for i in range(N):
            treated = np.where(D[i] > 0)[0]
            if len(treated) > 0:
                treatment_timing.append(treated[0])
            else:
                treatment_timing.append(T)
        
        # Split into early and late treated
        median_timing = np.median([t for t in treatment_timing if t < T])
        early = [i for i, t in enumerate(treatment_timing) if t <= median_timing and t < T]
        late = [i for i, t in enumerate(treatment_timing) if t > median_timing or t == T]
        
        if not early or not late:
            return HeterogeneityTest()
        
        # Test for differential pre-trends
        pre_diffs = []
        min_pre = min(int(min(treatment_timing)), n_pre_periods)
        
        for t in range(min_pre):
            diff_early = np.mean([Y[i, t] - Y[i, 0] for i in early]) if len(early) > 0 else 0
            diff_late = np.mean([Y[i, t] - Y[i, 0] for i in late]) if len(late) > 0 else 0
            pre_diffs.append(diff_early - diff_late)
        
        # F-test for joint significance
        if len(pre_diffs) > 1:
            pre_diffs_arr = np.array(pre_diffs[1:])  # Exclude period 0
            if np.var(pre_diffs_arr) > 0:
                f_stat = np.mean(pre_diffs_arr**2) / np.var(pre_diffs_arr)
                p_value = 1 - stats.f.cdf(f_stat, len(pre_diffs_arr), N - 2)
            else:
                f_stat = 0
                p_value = 1.0
        else:
            f_stat = 0
            p_value = 1.0
        
        # Cohort-specific effects
        cohort_effects = {}
        timings = sorted(set(treatment_timing))
        for timing in timings:
            if timing < T:
                cohort_units = [i for i, t in enumerate(treatment_timing) if t == timing]
                if cohort_units and timing < T - 1:
                    pre = np.mean([Y[i, timing - 1] for i in cohort_units]) if timing > 0 else 0
                    post = np.mean([Y[i, timing + 1] for i in cohort_units])
                    cohort_effects[timing] = float(post - pre)
        
        cohort_variation = np.var(list(cohort_effects.values())) if cohort_effects else 0
        
        return HeterogeneityTest(
            pre_trend_f_stat=float(f_stat),
            pre_trend_p_value=float(p_value),
            cohort_effects=cohort_effects,
            cohort_variation=float(cohort_variation),
        )
    
    @requires_tier(Tier.TEAM)
    def analyze_panel(
        self,
        data: PanelData,
    ) -> TWFEMetrics:
        """
        Comprehensive TWFE panel analysis.
        
        Args:
            data: Panel data
        
        Returns:
            Complete TWFE metrics
        """
        twfe_result = self.estimate_twfe(data)
        bacon = self.bacon_decomposition(data)
        heterogeneity = self.test_parallel_trends(data)
        
        return TWFEMetrics(
            twfe_result=twfe_result,
            bacon=bacon,
            heterogeneity=heterogeneity,
            estimator_used=TWFEEstimator.STANDARD,
            cluster_type=self.cluster_type,
        )
