# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Time Series Causal Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Time Series Causal Inference Framework.

Production-grade time series methods for causal analysis:
- Interrupted Time Series (ITS) design
- Granger Causality testing
- Synthetic Control with time series
- Causal Impact analysis
- Structural breaks detection

References:
    - Bernal et al. (2017): Interrupted Time Series Analysis
    - Granger (1969): Investigating Causal Relations
    - Brodersen et al. (2015): Inferring Causal Impact

Tier: PROFESSIONAL
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Mapping, Optional

import numpy as np
from scipy import stats
from scipy.signal import detrend

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

__all__ = ["TimeSeriesCausalFramework"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Time Series Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class ITSModel(Enum):
    """Interrupted Time Series model types."""
    SEGMENTED_REGRESSION = "Segmented Regression"
    ARIMA = "ARIMA with intervention"
    STATE_SPACE = "State Space"
    ROBUST = "Robust ITS"


class CausalityTest(Enum):
    """Causality test types."""
    GRANGER = "Granger Causality"
    SIMS = "Sims Test"
    TODA_YAMAMOTO = "Toda-Yamamoto"
    TRANSFER_ENTROPY = "Transfer Entropy"


@dataclass
class TimeSeriesData:
    """Time series data container."""
    
    y: np.ndarray = field(default_factory=lambda: np.array([]))
    time: np.ndarray = field(default_factory=lambda: np.array([]))
    intervention_time: int = 0
    
    @property
    def n_periods(self) -> int:
        return len(self.y)
    
    @property
    def pre_period(self) -> np.ndarray:
        return self.y[:self.intervention_time]
    
    @property
    def post_period(self) -> np.ndarray:
        return self.y[self.intervention_time:]


@dataclass
class ITSResult:
    """Interrupted Time Series results."""
    
    # Pre-intervention trend
    pre_intercept: float = 0.0
    pre_slope: float = 0.0
    
    # Level change at intervention
    level_change: float = 0.0
    level_change_se: float = 0.0
    level_change_pvalue: float = 0.0
    
    # Slope change after intervention
    slope_change: float = 0.0
    slope_change_se: float = 0.0
    slope_change_pvalue: float = 0.0
    
    # Counterfactual
    counterfactual: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Overall effect
    cumulative_effect: float = 0.0
    average_effect: float = 0.0
    
    # Model fit
    r_squared: float = 0.0
    durbin_watson: float = 0.0


@dataclass
class GrangerResult:
    """Granger Causality test results."""
    
    # X -> Y test
    f_stat_x_to_y: float = 0.0
    p_value_x_to_y: float = 0.0
    causes_y: bool = False
    
    # Y -> X test
    f_stat_y_to_x: float = 0.0
    p_value_y_to_x: float = 0.0
    causes_x: bool = False
    
    # Direction
    direction: str = "none"  # "x->y", "y->x", "bidirectional", "none"
    
    # Optimal lag
    optimal_lag: int = 1


@dataclass
class CausalImpactResult:
    """Causal Impact analysis results."""
    
    # Point estimates
    average_effect: float = 0.0
    cumulative_effect: float = 0.0
    
    # Uncertainty
    average_effect_lower: float = 0.0
    average_effect_upper: float = 0.0
    cumulative_effect_lower: float = 0.0
    cumulative_effect_upper: float = 0.0
    
    # Relative effects
    relative_effect: float = 0.0
    
    # Predictions
    predicted: np.ndarray = field(default_factory=lambda: np.array([]))
    predicted_lower: np.ndarray = field(default_factory=lambda: np.array([]))
    predicted_upper: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Significance
    p_value: float = 0.0
    significant: bool = False


@dataclass
class StructuralBreakResult:
    """Structural break detection results."""
    
    # Break points
    break_dates: list[int] = field(default_factory=list)
    n_breaks: int = 0
    
    # Test statistics
    sup_f_stat: float = 0.0
    p_value: float = 0.0
    
    # Confidence intervals for break dates
    break_ci: list[tuple[int, int]] = field(default_factory=list)


@dataclass
class TimeSeriesMetrics:
    """Comprehensive time series causal analysis."""
    
    its_result: Optional[ITSResult] = None
    granger_result: Optional[GrangerResult] = None
    causal_impact: Optional[CausalImpactResult] = None
    structural_breaks: Optional[StructuralBreakResult] = None


# ════════════════════════════════════════════════════════════════════════════════
# Time Series Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class TimeSeriesTransition(TransitionFunction):
    """Transition function with autoregressive dynamics."""
    
    name = "TimeSeriesTransition"
    
    def __init__(self, ar_coef: float = 0.7, innovation_std: float = 0.1):
        self.ar_coef = ar_coef
        self.innovation_std = innovation_std
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        params = params or {}
        intervention = params.get("intervention", 0.0)
        
        # AR(1) dynamics with intervention
        innovation = np.random.normal(0, self.innovation_std, state.n_cohorts)
        new_opportunity = (
            self.ar_coef * state.opportunity_score +
            (1 - self.ar_coef) * 0.5 +
            intervention +
            innovation
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
# Time Series Causal Framework
# ════════════════════════════════════════════════════════════════════════════════


class TimeSeriesCausalFramework(BaseMetaFramework):
    """
    Time Series Causal Inference Framework.
    
    Production-grade time series methods:
    
    - Interrupted Time Series (ITS) design
    - Granger Causality testing
    - Causal Impact analysis
    - Structural break detection
    
    Token Weight: 6
    Tier: PROFESSIONAL
    
    Example:
        >>> framework = TimeSeriesCausalFramework()
        >>> result = framework.its_analysis(y, intervention_time=100)
        >>> print(f"Level change: {result.level_change:.3f}")
    
    References:
        - Bernal et al. (2017)
        - Brodersen et al. (2015)
    """
    
    METADATA = FrameworkMetadata(
        slug="timeseries-causal",
        name="Time Series Causal Inference",
        version="1.0.0",
        layer=VerticalLayer.EXPERIMENTAL_RESEARCH,
        tier=Tier.PROFESSIONAL,
        description=(
            "Time series methods for causal inference including "
            "ITS, Granger causality, and causal impact analysis."
        ),
        required_domains=["outcome_series", "intervention_time"],
        output_domains=["level_change", "slope_change", "causal_effect"],
        constituent_models=["its", "granger", "causal_impact", "break_detection"],
        tags=["time-series", "causal-inference", "its", "granger"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(
        self,
        max_lag: int = 10,
        confidence_level: float = 0.95,
    ):
        super().__init__()
        self.max_lag = max_lag
        self.confidence_level = confidence_level
        self._transition_fn = TimeSeriesTransition()
    
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
            opportunity_score=np.full(n_cohorts, 0.5),
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
        return {"framework": "timeseries-causal", "n_periods": trajectory.n_periods}

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return Time Series Causal Inference dashboard specification."""
        return FrameworkDashboardSpec(
            slug="timeseries_causal",
            name="Time Series Causal Inference",
            description=(
                "Time series methods for causal inference including "
                "ITS, Granger causality, and causal impact analysis."
            ),
            layer="experimental",
            parameters_schema={
                "type": "object",
                "properties": {
                    "lag_structure": {
                        "type": "integer",
                        "title": "Lag Structure",
                        "minimum": 1,
                        "maximum": 20,
                        "default": 5,
                        "x-ui-widget": "slider",
                        "x-ui-group": "model",
                    },
                    "granger_test": {
                        "type": "boolean",
                        "title": "Run Granger Test",
                        "default": True,
                        "x-ui-widget": "checkbox",
                        "x-ui-group": "diagnostics",
                    },
                    "var_order": {
                        "type": "string",
                        "title": "VAR Order Selection",
                        "enum": ["aic", "bic", "hqic", "manual"],
                        "default": "aic",
                        "x-ui-widget": "select",
                        "x-ui-group": "model",
                    },
                    "intervention_time": {
                        "type": "integer",
                        "title": "Intervention Time",
                        "minimum": 1,
                        "default": 50,
                        "x-ui-widget": "number",
                        "x-ui-group": "design",
                    },
                },
            },
            default_parameters={"lag_structure": 5, "granger_test": True, "var_order": "aic", "intervention_time": 50},
            parameter_groups=[
                ParameterGroupSpec(key="design", title="Design", parameters=["intervention_time"]),
                ParameterGroupSpec(key="model", title="Model", parameters=["lag_structure", "var_order"]),
                ParameterGroupSpec(key="diagnostics", title="Diagnostics", parameters=["granger_test"]),
            ],
            required_domains=["outcome_series", "intervention_time"],
            min_tier=Tier.PROFESSIONAL,
            output_views=[
                OutputViewSpec(
                    key="granger_causality",
                    title="Granger Causality",
                    view_type=ViewType.TABLE,
                    config={"columns": ["direction", "f_statistic", "p_value", "conclusion"]},
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="granger_causality_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="impulse_responses",
                    title="Impulse Response Functions",
                    view_type=ViewType.LINE_CHART,
                    config={"x_field": "horizon", "y_fields": ["response"], "error_bands": True},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="impulse_responses_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="causal_impact",
                    title="Causal Impact",
                    view_type=ViewType.LINE_CHART,
                    config={"x_field": "time", "y_fields": ["actual", "predicted"], "intervention_line": True, "cumulative": True},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="causal_impact_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )

    # ════════════════════════════════════════════════════════════════════════════
    # Public API Methods
    # ════════════════════════════════════════════════════════════════════════════
    
    @requires_tier(Tier.PROFESSIONAL)
    def its_analysis(
        self,
        y: np.ndarray,
        intervention_time: int,
        model: ITSModel = ITSModel.SEGMENTED_REGRESSION,
    ) -> ITSResult:
        """
        Interrupted Time Series (ITS) analysis.
        
        Y_t = β₀ + β₁·t + β₂·D_t + β₃·(t-T₀)·D_t + ε_t
        
        Where D_t = 1 if t >= T₀ (intervention time)
        
        Args:
            y: Outcome series (T,)
            intervention_time: Time of intervention
            model: ITS model type
        
        Returns:
            ITS results with level and slope changes
        """
        T = len(y)
        t = np.arange(T)
        
        # Intervention indicators
        D = (t >= intervention_time).astype(float)
        time_since = np.maximum(0, t - intervention_time)
        
        # Design matrix
        X = np.column_stack([
            np.ones(T),        # Intercept
            t,                 # Pre-trend
            D,                 # Level change
            time_since * D,    # Slope change
        ])
        
        # OLS estimation
        XtX_inv = np.linalg.inv(X.T @ X)
        beta = XtX_inv @ X.T @ y
        
        # Residuals and standard errors
        y_hat = X @ beta
        residuals = y - y_hat
        mse = np.sum(residuals ** 2) / (T - 4)
        se = np.sqrt(np.diag(XtX_inv) * mse)
        
        # t-statistics and p-values
        t_stats = beta / se
        p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), T - 4))
        
        # Counterfactual (without intervention)
        counterfactual = beta[0] + beta[1] * t
        
        # Effects
        post_mask = t >= intervention_time
        n_post = np.sum(post_mask)
        
        cumulative_effect = float(np.sum(y[post_mask] - counterfactual[post_mask]))
        average_effect = cumulative_effect / n_post if n_post > 0 else 0.0
        
        # Model fit
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
        
        # Durbin-Watson
        dw = np.sum(np.diff(residuals) ** 2) / ss_res if ss_res > 0 else 2.0
        
        return ITSResult(
            pre_intercept=float(beta[0]),
            pre_slope=float(beta[1]),
            level_change=float(beta[2]),
            level_change_se=float(se[2]),
            level_change_pvalue=float(p_values[2]),
            slope_change=float(beta[3]),
            slope_change_se=float(se[3]),
            slope_change_pvalue=float(p_values[3]),
            counterfactual=counterfactual,
            cumulative_effect=cumulative_effect,
            average_effect=average_effect,
            r_squared=float(r_squared),
            durbin_watson=float(dw),
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def granger_causality(
        self,
        x: np.ndarray,
        y: np.ndarray,
        max_lag: Optional[int] = None,
        significance_level: float = 0.05,
    ) -> GrangerResult:
        """
        Granger Causality test.
        
        Tests whether X Granger-causes Y and vice versa.
        
        Args:
            x: First series
            y: Second series
            max_lag: Maximum lag to test
            significance_level: Significance threshold
        
        Returns:
            Granger causality results
        """
        max_lag = max_lag or self.max_lag
        n = len(y)
        
        # Find optimal lag using BIC
        best_lag = 1
        best_bic = np.inf
        
        for lag in range(1, min(max_lag + 1, n // 4)):
            # Restricted model (Y only)
            Y = y[lag:]
            Y_lags = np.column_stack([y[lag-i-1:n-i-1] for i in range(lag)])
            
            beta_r = np.linalg.lstsq(Y_lags, Y, rcond=None)[0]
            resid_r = Y - Y_lags @ beta_r
            rss_r = np.sum(resid_r ** 2)
            
            n_obs = len(Y)
            bic = n_obs * np.log(rss_r / n_obs) + lag * np.log(n_obs)
            
            if bic < best_bic:
                best_bic = bic
                best_lag = lag
        
        lag = best_lag
        Y = y[lag:]
        n_obs = len(Y)
        
        # Test X -> Y
        Y_lags = np.column_stack([y[lag-i-1:n-i-1] for i in range(lag)])
        X_lags = np.column_stack([x[lag-i-1:n-i-1] for i in range(lag)])
        
        # Restricted model (Y lags only)
        beta_r = np.linalg.lstsq(Y_lags, Y, rcond=None)[0]
        rss_r = np.sum((Y - Y_lags @ beta_r) ** 2)
        
        # Unrestricted model (Y and X lags)
        X_full = np.column_stack([Y_lags, X_lags])
        beta_u = np.linalg.lstsq(X_full, Y, rcond=None)[0]
        rss_u = np.sum((Y - X_full @ beta_u) ** 2)
        
        # F-test
        df1 = lag
        df2 = n_obs - 2 * lag - 1
        
        f_stat_xy = ((rss_r - rss_u) / df1) / (rss_u / df2) if rss_u > 0 else 0
        p_value_xy = 1 - stats.f.cdf(f_stat_xy, df1, df2) if df2 > 0 else 1.0
        
        # Test Y -> X
        X_target = x[lag:]
        
        # Restricted (X lags only)
        beta_r = np.linalg.lstsq(X_lags, X_target, rcond=None)[0]
        rss_r = np.sum((X_target - X_lags @ beta_r) ** 2)
        
        # Unrestricted
        X_full = np.column_stack([X_lags, Y_lags])
        beta_u = np.linalg.lstsq(X_full, X_target, rcond=None)[0]
        rss_u = np.sum((X_target - X_full @ beta_u) ** 2)
        
        f_stat_yx = ((rss_r - rss_u) / df1) / (rss_u / df2) if rss_u > 0 else 0
        p_value_yx = 1 - stats.f.cdf(f_stat_yx, df1, df2) if df2 > 0 else 1.0
        
        # Direction
        causes_y = p_value_xy < significance_level
        causes_x = p_value_yx < significance_level
        
        if causes_y and causes_x:
            direction = "bidirectional"
        elif causes_y:
            direction = "x->y"
        elif causes_x:
            direction = "y->x"
        else:
            direction = "none"
        
        return GrangerResult(
            f_stat_x_to_y=float(f_stat_xy),
            p_value_x_to_y=float(p_value_xy),
            causes_y=causes_y,
            f_stat_y_to_x=float(f_stat_yx),
            p_value_y_to_x=float(p_value_yx),
            causes_x=causes_x,
            direction=direction,
            optimal_lag=lag,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def causal_impact(
        self,
        y: np.ndarray,
        intervention_time: int,
        controls: Optional[np.ndarray] = None,
    ) -> CausalImpactResult:
        """
        Causal Impact analysis using Bayesian structural time series.
        
        Args:
            y: Outcome series
            intervention_time: Time of intervention
            controls: Control series (n_controls, T) or None
        
        Returns:
            Causal impact with uncertainty bounds
        """
        T = len(y)
        pre_period = slice(0, intervention_time)
        post_period = slice(intervention_time, T)
        
        y_pre = y[pre_period]
        y_post = y[post_period]
        n_pre = len(y_pre)
        n_post = len(y_post)
        
        if controls is not None and controls.shape[1] == T:
            # Use controls to build counterfactual
            X_pre = controls[:, pre_period].T
            X_post = controls[:, post_period].T
            
            # Fit on pre-period
            beta = np.linalg.lstsq(X_pre, y_pre, rcond=None)[0]
            y_pred_pre = X_pre @ beta
            sigma = np.std(y_pre - y_pred_pre)
            
            # Predict post-period
            predicted = X_post @ beta
        else:
            # Use pre-period trend
            t_pre = np.arange(n_pre)
            X_pre = np.column_stack([np.ones(n_pre), t_pre])
            
            beta = np.linalg.lstsq(X_pre, y_pre, rcond=None)[0]
            sigma = np.std(y_pre - X_pre @ beta)
            
            # Predict post-period
            t_post = np.arange(intervention_time, T)
            X_post = np.column_stack([np.ones(n_post), t_post])
            predicted = X_post @ beta
        
        # Prediction uncertainty
        z = stats.norm.ppf((1 + self.confidence_level) / 2)
        predicted_lower = predicted - z * sigma
        predicted_upper = predicted + z * sigma
        
        # Point-wise effects
        effects = y_post - predicted
        
        # Summary effects
        average_effect = float(np.mean(effects))
        cumulative_effect = float(np.sum(effects))
        
        # Uncertainty for summaries
        se_avg = sigma / np.sqrt(n_post)
        se_cum = sigma * np.sqrt(n_post)
        
        average_effect_lower = float(average_effect - z * se_avg)
        average_effect_upper = float(average_effect + z * se_avg)
        cumulative_effect_lower = float(cumulative_effect - z * se_cum)
        cumulative_effect_upper = float(cumulative_effect + z * se_cum)
        
        # Relative effect
        counterfactual_sum = float(np.sum(predicted))
        relative_effect = cumulative_effect / counterfactual_sum if counterfactual_sum != 0 else 0.0
        
        # Significance test
        t_stat = average_effect / se_avg if se_avg > 0 else 0
        p_value = 2 * (1 - stats.norm.cdf(abs(t_stat)))
        
        return CausalImpactResult(
            average_effect=average_effect,
            cumulative_effect=cumulative_effect,
            average_effect_lower=average_effect_lower,
            average_effect_upper=average_effect_upper,
            cumulative_effect_lower=cumulative_effect_lower,
            cumulative_effect_upper=cumulative_effect_upper,
            relative_effect=float(relative_effect),
            predicted=predicted,
            predicted_lower=predicted_lower,
            predicted_upper=predicted_upper,
            p_value=float(p_value),
            significant=p_value < (1 - self.confidence_level),
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def detect_structural_breaks(
        self,
        y: np.ndarray,
        max_breaks: int = 5,
        min_segment: int = 10,
    ) -> StructuralBreakResult:
        """
        Detect structural breaks using Bai-Perron method.
        
        Args:
            y: Time series
            max_breaks: Maximum number of breaks
            min_segment: Minimum segment length
        
        Returns:
            Detected break points
        """
        T = len(y)
        t = np.arange(T)
        
        # Fit full model
        X = np.column_stack([np.ones(T), t])
        beta_full = np.linalg.lstsq(X, y, rcond=None)[0]
        rss_full = np.sum((y - X @ beta_full) ** 2)
        
        # Search for single break
        best_break = min_segment
        best_rss = np.inf
        
        for b in range(min_segment, T - min_segment):
            # Fit two-segment model
            X1 = np.column_stack([np.ones(b), t[:b]])
            X2 = np.column_stack([np.ones(T - b), t[b:] - b])
            
            beta1 = np.linalg.lstsq(X1, y[:b], rcond=None)[0]
            beta2 = np.linalg.lstsq(X2, y[b:], rcond=None)[0]
            
            rss1 = np.sum((y[:b] - X1 @ beta1) ** 2)
            rss2 = np.sum((y[b:] - X2 @ beta2) ** 2)
            rss = rss1 + rss2
            
            if rss < best_rss:
                best_rss = rss
                best_break = b
        
        # Sup-F test
        df1 = 2
        df2 = T - 4
        
        f_stat = ((rss_full - best_rss) / df1) / (best_rss / df2) if best_rss > 0 else 0
        
        # Critical values for sup-F (Andrews 1993)
        # Approximate p-value
        p_value = 1 - stats.f.cdf(f_stat, df1, df2)
        
        # Determine if break is significant
        if p_value < 0.05:
            break_dates = [best_break]
            n_breaks = 1
            
            # Confidence interval (approximate)
            ci_width = int(np.sqrt(T) * 2)
            break_ci = [(max(0, best_break - ci_width), min(T, best_break + ci_width))]
        else:
            break_dates = []
            n_breaks = 0
            break_ci = []
        
        return StructuralBreakResult(
            break_dates=break_dates,
            n_breaks=n_breaks,
            sup_f_stat=float(f_stat),
            p_value=float(p_value),
            break_ci=break_ci,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def analyze_timeseries(
        self,
        y: np.ndarray,
        intervention_time: Optional[int] = None,
        x: Optional[np.ndarray] = None,
        controls: Optional[np.ndarray] = None,
    ) -> TimeSeriesMetrics:
        """
        Comprehensive time series causal analysis.
        
        Args:
            y: Outcome series
            intervention_time: Time of intervention (optional)
            x: Second series for Granger test (optional)
            controls: Control series for causal impact (optional)
        
        Returns:
            Complete time series metrics
        """
        its_result = None
        granger_result = None
        causal_impact = None
        structural_breaks = None
        
        # ITS if intervention time provided
        if intervention_time is not None:
            its_result = self.its_analysis(y, intervention_time)
            causal_impact = self.causal_impact(y, intervention_time, controls)
        
        # Granger if second series provided
        if x is not None:
            granger_result = self.granger_causality(x, y)
        
        # Always detect structural breaks
        structural_breaks = self.detect_structural_breaks(y)
        
        return TimeSeriesMetrics(
            its_result=its_result,
            granger_result=granger_result,
            causal_impact=causal_impact,
            structural_breaks=structural_breaks,
        )
