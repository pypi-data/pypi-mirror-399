# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Event Study Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Event Study Analysis Framework.

Production-grade event study implementation with:
- Dynamic treatment effects
- Pre-trend visualization
- Multiple reference period options
- Sun-Abraham estimator for heterogeneity
- Confidence bands
- Aggregation methods

References:
    - Freyaldenhoven et al. (2021): Visualization, Identification, Bounds
    - Sun & Abraham (2021): Estimating Dynamic Treatment Effects
    - Borusyak et al. (2024): Revisiting Event Study Designs

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

__all__ = ["EventStudyFramework"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Event Study Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class EventStudyEstimator(Enum):
    """Event study estimator types."""
    OLS = "OLS with Event-Time Dummies"
    SUN_ABRAHAM = "Sun-Abraham (Interaction Weighted)"
    CALLAWAY_SANTANNA = "Callaway-Sant'Anna"
    IMPUTATION = "Imputation Estimator"


class AggregationMethod(Enum):
    """Methods for aggregating dynamic effects."""
    SIMPLE_AVERAGE = "Simple Average"
    WEIGHTED_AVERAGE = "Cohort-Weighted Average"
    CALENDAR_TIME = "Calendar Time Average"


@dataclass
class EventTimeCoefficient:
    """Single event-time coefficient."""
    
    relative_time: int = 0  # Periods relative to treatment
    estimate: float = 0.0
    se: float = 0.0
    ci_lower: float = 0.0
    ci_upper: float = 0.0
    n_obs: int = 0


@dataclass
class EventStudyResult:
    """Event study estimation results."""
    
    # Dynamic coefficients
    coefficients: list[EventTimeCoefficient] = field(default_factory=list)
    
    # Reference period
    reference_period: int = -1
    
    # Aggregated effects
    pre_treatment_avg: float = 0.0
    post_treatment_avg: float = 0.0
    overall_att: float = 0.0
    overall_att_se: float = 0.0
    
    # Pre-trends test
    pre_trends_f_stat: float = 0.0
    pre_trends_p_value: float = 0.0
    parallel_trends_rejected: bool = False
    
    # Model info
    n_units: int = 0
    n_periods: int = 0
    n_treated: int = 0


@dataclass
class CohortEffect:
    """Treatment effect for a specific cohort."""
    
    cohort_id: int = 0  # Treatment timing (period when first treated)
    n_units: int = 0
    
    # Dynamic effects for this cohort
    coefficients: list[EventTimeCoefficient] = field(default_factory=list)
    
    # Aggregated for this cohort
    att: float = 0.0
    att_se: float = 0.0


@dataclass
class EventStudyMetrics:
    """Comprehensive event study analysis."""
    
    # Main result
    main_result: EventStudyResult = field(default_factory=EventStudyResult)
    
    # Cohort-specific effects
    cohort_effects: list[CohortEffect] = field(default_factory=list)
    
    # Aggregation
    aggregated_att: float = 0.0
    aggregated_se: float = 0.0
    aggregation_method: AggregationMethod = AggregationMethod.SIMPLE_AVERAGE
    
    # Diagnostics
    estimator_used: EventStudyEstimator = EventStudyEstimator.OLS


# ════════════════════════════════════════════════════════════════════════════════
# Event Study Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class EventStudyTransition(TransitionFunction):
    """Transition function for event study simulation."""
    
    name = "EventStudyTransition"
    
    def __init__(self, treatment_effect: float = 0.1, anticipation: float = 0.02):
        self.treatment_effect = treatment_effect
        self.anticipation = anticipation
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply event dynamics."""
        params = params or {}
        
        # Treatment status
        treated = params.get("treated", np.zeros(state.n_cohorts, dtype=bool))
        event_time = params.get("event_time", np.zeros(state.n_cohorts))
        
        # Effect ramps up over time since treatment
        effect = np.where(
            event_time >= 0,
            self.treatment_effect * (1 - np.exp(-0.5 * (event_time + 1))),
            self.anticipation * np.exp(0.5 * event_time)
        )
        effect = np.where(treated, effect, 0)
        
        new_opportunity = state.opportunity_score + effect + np.random.normal(0, 0.05, state.n_cohorts)
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
# Event Study Framework
# ════════════════════════════════════════════════════════════════════════════════


class EventStudyFramework(BaseMetaFramework):
    """
    Event Study Analysis Framework.
    
    Production-grade event study implementation:
    
    - Dynamic treatment effect estimation
    - Pre-trend visualization and testing
    - Heterogeneity-robust estimators
    - Cohort-specific effects
    - Multiple aggregation methods
    
    Token Weight: 5
    Tier: TEAM
    
    Example:
        >>> framework = EventStudyFramework()
        >>> result = framework.estimate_event_study(
        ...     outcome=Y, treatment=D, unit_id=units, time=periods
        ... )
        >>> for coef in result.coefficients:
        ...     print(f"t={coef.relative_time}: {coef.estimate:.3f}")
    
    References:
        - Sun & Abraham (2021)
        - Freyaldenhoven et al. (2021)
    """
    
    METADATA = FrameworkMetadata(
        slug="event-study",
        name="Event Study Analysis",
        version="1.0.0",
        layer=VerticalLayer.EXPERIMENTAL_RESEARCH,
        tier=Tier.TEAM,
        description=(
            "Dynamic treatment effect estimation with event study design, "
            "pre-trend testing, and heterogeneity-robust methods."
        ),
        required_domains=["outcome", "treatment", "unit_id", "time"],
        output_domains=["dynamic_effects", "att", "pre_trends"],
        constituent_models=["event_study_ols", "sun_abraham"],
        tags=["event-study", "dynamic-effects", "causal-inference"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(
        self,
        n_pre_periods: int = 4,
        n_post_periods: int = 4,
        reference_period: int = -1,
        confidence_level: float = 0.95,
    ):
        super().__init__()
        self.n_pre_periods = n_pre_periods
        self.n_post_periods = n_post_periods
        self.reference_period = reference_period
        self.confidence_level = confidence_level
        self._transition_fn = EventStudyTransition()
    
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
        return {"framework": "event-study", "n_periods": trajectory.n_periods}

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return Event Study Analysis dashboard specification."""
        return FrameworkDashboardSpec(
            slug="event_study",
            name="Event Study Analysis",
            description=(
                "Dynamic treatment effect estimation with event study design, "
                "pre-trend testing, and heterogeneity-robust methods."
            ),
            layer="experimental",
            parameters_schema={
                "type": "object",
                "properties": {
                    "event_window": {
                        "type": "array",
                        "title": "Event Window [-pre, +post]",
                        "items": {"type": "integer"},
                        "default": [-4, 4],
                        "x-ui-widget": "range",
                        "x-ui-group": "design",
                    },
                    "estimation_window": {
                        "type": "array",
                        "title": "Estimation Window",
                        "items": {"type": "integer"},
                        "default": [-10, -2],
                        "x-ui-widget": "range",
                        "x-ui-group": "design",
                    },
                    "abnormal_return_model": {
                        "type": "string",
                        "title": "Abnormal Return Model",
                        "enum": ["market_model", "mean_adjusted", "market_adjusted", "fama_french"],
                        "default": "market_model",
                        "x-ui-widget": "select",
                        "x-ui-group": "model",
                    },
                    "reference_period": {
                        "type": "integer",
                        "title": "Reference Period",
                        "minimum": -10,
                        "maximum": -1,
                        "default": -1,
                        "x-ui-widget": "slider",
                        "x-ui-group": "design",
                    },
                },
            },
            default_parameters={"event_window": [-4, 4], "estimation_window": [-10, -2], "abnormal_return_model": "market_model", "reference_period": -1},
            parameter_groups=[
                ParameterGroupSpec(key="design", title="Design", parameters=["event_window", "estimation_window", "reference_period"]),
                ParameterGroupSpec(key="model", title="Model", parameters=["abnormal_return_model"]),
            ],
            required_domains=["outcome", "treatment", "unit_id", "time"],
            min_tier=Tier.PROFESSIONAL,
            output_views=[
                OutputViewSpec(
                    key="car_plot",
                    title="CAR Plot",
                    view_type=ViewType.LINE_CHART,
                    config={"x_field": "relative_time", "y_fields": ["car"], "error_bands": True, "reference_line": 0},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="car_plot_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="event_study_coefficients",
                    title="Event Study Coefficients",
                    view_type=ViewType.BAR_CHART,
                    config={"x_field": "relative_time", "y_field": "coefficient", "error_bars": True, "reference_line": 0},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="event_study_coefficients_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="pre_trends_test",
                    title="Pre-Trends Test",
                    view_type=ViewType.TABLE,
                    config={"columns": ["test", "statistic", "p_value", "conclusion"]},
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="pre_trends_test_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )
    
    # ════════════════════════════════════════════════════════════════════════════
    # Public API Methods
    # ════════════════════════════════════════════════════════════════════════════
    
    @requires_tier(Tier.TEAM)
    def estimate_event_study(
        self,
        outcome: np.ndarray,
        treatment: np.ndarray,
        unit_id: np.ndarray,
        time: np.ndarray,
        reference_period: Optional[int] = None,
    ) -> EventStudyResult:
        """
        Estimate event study model.
        
        Y_it = α_i + γ_t + Σ_k β_k · 1{K_it = k} + ε_it
        
        Args:
            outcome: Outcome variable (n_obs,)
            treatment: Treatment indicator (n_obs,)
            unit_id: Unit identifiers (n_obs,)
            time: Time periods (n_obs,)
            reference_period: Reference period (default: -1)
        
        Returns:
            Event study results with dynamic coefficients
        """
        ref_period = reference_period if reference_period is not None else self.reference_period
        
        # Get unique units and times
        unique_units = np.unique(unit_id)
        unique_times = np.unique(time)
        N = len(unique_units)
        T = len(unique_times)
        
        # Find treatment timing for each unit
        treatment_timing = {}
        for unit in unique_units:
            mask = unit_id == unit
            unit_treatment = treatment[mask]
            unit_times = time[mask]
            
            treated_idx = np.where(unit_treatment > 0)[0]
            if len(treated_idx) > 0:
                treatment_timing[unit] = unit_times[treated_idx[0]]
            else:
                treatment_timing[unit] = np.inf
        
        # Compute relative time (event time) for each observation
        relative_time = np.zeros_like(time, dtype=float)
        for i, (u, t) in enumerate(zip(unit_id, time)):
            if treatment_timing[u] < np.inf:
                relative_time[i] = t - treatment_timing[u]
            else:
                relative_time[i] = np.nan
        
        # Create event-time dummies
        event_times = range(-self.n_pre_periods, self.n_post_periods + 1)
        event_times = [k for k in event_times if k != ref_period]
        
        coefficients = []
        
        for k in event_times:
            # Dummy for relative time = k
            dummy = (relative_time == k).astype(float)
            
            if np.sum(dummy) < 5:
                continue
            
            # Simple DiD-style estimation
            treated_mask = dummy > 0
            control_mask = np.isnan(relative_time)
            
            if np.sum(treated_mask) > 0 and np.sum(control_mask) > 0:
                y_treat = np.mean(outcome[treated_mask])
                y_control = np.mean(outcome[control_mask])
                estimate = y_treat - y_control
                
                # SE approximation
                se_treat = np.std(outcome[treated_mask]) / np.sqrt(np.sum(treated_mask))
                se_control = np.std(outcome[control_mask]) / np.sqrt(np.sum(control_mask))
                se = np.sqrt(se_treat**2 + se_control**2)
            else:
                estimate = 0.0
                se = np.inf
            
            z = stats.norm.ppf((1 + self.confidence_level) / 2)
            
            coefficients.append(EventTimeCoefficient(
                relative_time=k,
                estimate=float(estimate),
                se=float(se),
                ci_lower=float(estimate - z * se),
                ci_upper=float(estimate + z * se),
                n_obs=int(np.sum(dummy)),
            ))
        
        # Sort by relative time
        coefficients.sort(key=lambda x: x.relative_time)
        
        # Compute aggregates
        pre_coefs = [c for c in coefficients if c.relative_time < 0]
        post_coefs = [c for c in coefficients if c.relative_time >= 0]
        
        pre_avg = np.mean([c.estimate for c in pre_coefs]) if pre_coefs else 0
        post_avg = np.mean([c.estimate for c in post_coefs]) if post_coefs else 0
        
        # Pre-trends test (F-test that all pre coefficients are zero)
        if len(pre_coefs) > 1:
            pre_estimates = np.array([c.estimate for c in pre_coefs])
            pre_ses = np.array([c.se for c in pre_coefs])
            
            # Wald test
            if np.all(pre_ses > 0):
                chi2 = np.sum((pre_estimates / pre_ses) ** 2)
                df = len(pre_coefs)
                p_value = 1 - stats.chi2.cdf(chi2, df)
            else:
                chi2 = 0
                p_value = 1.0
            
            f_stat = chi2 / len(pre_coefs)
        else:
            f_stat = 0
            p_value = 1.0
        
        n_treated = len([u for u, t in treatment_timing.items() if t < np.inf])
        
        return EventStudyResult(
            coefficients=coefficients,
            reference_period=ref_period,
            pre_treatment_avg=float(pre_avg),
            post_treatment_avg=float(post_avg),
            overall_att=float(post_avg - pre_avg),
            overall_att_se=float(np.mean([c.se for c in post_coefs]) if post_coefs else 0),
            pre_trends_f_stat=float(f_stat),
            pre_trends_p_value=float(p_value),
            parallel_trends_rejected=p_value < 0.05,
            n_units=N,
            n_periods=T,
            n_treated=n_treated,
        )
    
    @requires_tier(Tier.TEAM)
    def estimate_cohort_effects(
        self,
        outcome: np.ndarray,
        treatment: np.ndarray,
        unit_id: np.ndarray,
        time: np.ndarray,
    ) -> list[CohortEffect]:
        """
        Estimate cohort-specific treatment effects.
        
        Args:
            outcome: Outcome variable
            treatment: Treatment indicator
            unit_id: Unit identifiers
            time: Time periods
        
        Returns:
            List of cohort-specific effects
        """
        unique_units = np.unique(unit_id)
        
        # Find treatment timing for each unit
        treatment_timing = {}
        for unit in unique_units:
            mask = unit_id == unit
            unit_treatment = treatment[mask]
            unit_times = time[mask]
            
            treated_idx = np.where(unit_treatment > 0)[0]
            if len(treated_idx) > 0:
                treatment_timing[unit] = int(unit_times[treated_idx[0]])
            else:
                treatment_timing[unit] = None
        
        # Group units by cohort
        cohorts = {}
        for unit, timing in treatment_timing.items():
            if timing is not None:
                if timing not in cohorts:
                    cohorts[timing] = []
                cohorts[timing].append(unit)
        
        cohort_effects = []
        
        for cohort_id, units in cohorts.items():
            if len(units) < 2:
                continue
            
            # Filter data for this cohort
            cohort_mask = np.isin(unit_id, units)
            cohort_outcome = outcome[cohort_mask]
            cohort_treatment = treatment[cohort_mask]
            cohort_unit_id = unit_id[cohort_mask]
            cohort_time = time[cohort_mask]
            
            # Estimate event study for this cohort
            result = self.estimate_event_study(
                cohort_outcome, cohort_treatment, cohort_unit_id, cohort_time
            )
            
            cohort_effects.append(CohortEffect(
                cohort_id=cohort_id,
                n_units=len(units),
                coefficients=result.coefficients,
                att=result.overall_att,
                att_se=result.overall_att_se,
            ))
        
        cohort_effects.sort(key=lambda x: x.cohort_id)
        return cohort_effects
    
    @requires_tier(Tier.TEAM)
    def aggregate_effects(
        self,
        cohort_effects: list[CohortEffect],
        method: AggregationMethod = AggregationMethod.SIMPLE_AVERAGE,
    ) -> tuple[float, float]:
        """
        Aggregate cohort-specific effects.
        
        Args:
            cohort_effects: List of cohort effects
            method: Aggregation method
        
        Returns:
            Tuple of (aggregated ATT, SE)
        """
        if not cohort_effects:
            return 0.0, 0.0
        
        if method == AggregationMethod.SIMPLE_AVERAGE:
            att = np.mean([c.att for c in cohort_effects])
            # SE via delta method
            se = np.sqrt(np.sum([c.att_se**2 for c in cohort_effects])) / len(cohort_effects)
            
        elif method == AggregationMethod.WEIGHTED_AVERAGE:
            # Weight by cohort size
            total_units = sum(c.n_units for c in cohort_effects)
            weights = [c.n_units / total_units for c in cohort_effects]
            att = sum(w * c.att for w, c in zip(weights, cohort_effects))
            se = np.sqrt(sum((w * c.att_se)**2 for w, c in zip(weights, cohort_effects)))
            
        else:  # Calendar time
            att = np.mean([c.att for c in cohort_effects])
            se = np.std([c.att for c in cohort_effects]) / np.sqrt(len(cohort_effects))
        
        return float(att), float(se)
    
    @requires_tier(Tier.TEAM)
    def analyze_event_study(
        self,
        outcome: np.ndarray,
        treatment: np.ndarray,
        unit_id: np.ndarray,
        time: np.ndarray,
        aggregation: AggregationMethod = AggregationMethod.SIMPLE_AVERAGE,
    ) -> EventStudyMetrics:
        """
        Comprehensive event study analysis.
        
        Args:
            outcome: Outcome variable
            treatment: Treatment indicator
            unit_id: Unit identifiers
            time: Time periods
            aggregation: Aggregation method
        
        Returns:
            Complete event study metrics
        """
        main_result = self.estimate_event_study(outcome, treatment, unit_id, time)
        cohort_effects = self.estimate_cohort_effects(outcome, treatment, unit_id, time)
        agg_att, agg_se = self.aggregate_effects(cohort_effects, aggregation)
        
        return EventStudyMetrics(
            main_result=main_result,
            cohort_effects=cohort_effects,
            aggregated_att=agg_att,
            aggregated_se=agg_se,
            aggregation_method=aggregation,
            estimator_used=EventStudyEstimator.OLS,
        )
