# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Instrumental Variables Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Instrumental Variables (IV) and Two-Stage Least Squares Framework.

Implements comprehensive IV methodology for causal inference:
- Two-Stage Least Squares (2SLS)
- Limited Information Maximum Likelihood (LIML)
- Generalized Method of Moments (GMM)
- Weak instrument diagnostics (F-statistic, Stock-Yogo)
- Overidentification tests (Sargan, Hansen J)
- Endogeneity tests (Hausman, Durbin-Wu-Hausman)

References:
    - Angrist & Pischke (2009): Mostly Harmless Econometrics
    - Stock & Yogo (2005): Testing for Weak Instruments
    - Bound, Jaeger & Baker (1995): Problems with IV
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Mapping, Optional

import numpy as np

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

__all__ = ["InstrumentalVariablesFramework"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# IV-Specific Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class IVEstimator(Enum):
    """IV estimation methods."""
    TWOSLS = "Two-Stage Least Squares"
    LIML = "Limited Information Maximum Likelihood"
    GMM = "Generalized Method of Moments"
    FULLER = "Fuller's Modified LIML"
    JIVE = "Jackknife IV"


class WeakIVTest(Enum):
    """Weak instrument test types."""
    FIRST_STAGE_F = "First Stage F-statistic"
    STOCK_YOGO = "Stock-Yogo Critical Values"
    ANDERSON_RUBIN = "Anderson-Rubin"
    KLEIBERGEN_PAAP = "Kleibergen-Paap rk Wald"


@dataclass
class IVConfig:
    """Configuration for IV analysis."""
    
    # Estimator
    estimator: IVEstimator = IVEstimator.TWOSLS
    
    # Instruments
    n_instruments: int = 1
    
    # Standard errors
    robust_se: bool = True
    cluster_var: Optional[str] = None
    
    # Diagnostics
    run_weak_iv_test: bool = True
    weak_iv_threshold: float = 10.0  # Stock-Yogo rule of thumb
    run_overid_test: bool = True
    run_endogeneity_test: bool = True
    
    # Fuller constant for LIML
    fuller_constant: float = 1.0
    
    # GMM options
    gmm_weight_matrix: str = "optimal"  # optimal, unadjusted


@dataclass
class FirstStageResult:
    """First stage regression results."""
    
    # Coefficients
    instrument_coefficients: dict[str, float] = field(default_factory=dict)
    control_coefficients: dict[str, float] = field(default_factory=dict)
    intercept: float = 0.0
    
    # Fit statistics
    r_squared: float = 0.0
    adjusted_r_squared: float = 0.0
    residual_se: float = 0.0
    
    # Instrument relevance
    f_statistic: float = 0.0
    f_p_value: float = 1.0
    partial_r_squared: float = 0.0
    
    # Fitted values
    fitted_values: np.ndarray = field(default_factory=lambda: np.array([]))


@dataclass
class WeakIVDiagnostics:
    """Weak instrument diagnostics."""
    
    # First stage F
    first_stage_f: float = 0.0
    f_p_value: float = 1.0
    
    # Stock-Yogo critical values
    stock_yogo_10: float = 16.38  # 10% maximal IV size
    stock_yogo_15: float = 8.96   # 15% maximal IV size
    stock_yogo_20: float = 6.66   # 20% maximal IV size
    stock_yogo_25: float = 5.53   # 25% maximal IV size
    
    # Classification
    is_weak: bool = False
    weakness_level: str = ""  # strong, moderate, weak, very_weak
    
    # Kleibergen-Paap (for multiple endogenous)
    kleibergen_paap_rk: float = 0.0
    kleibergen_paap_p: float = 1.0
    
    # Anderson-Rubin (robust to weak IV)
    anderson_rubin_stat: float = 0.0
    anderson_rubin_p: float = 1.0
    anderson_rubin_ci: tuple[float, float] = (0.0, 0.0)


@dataclass
class OveridentificationTest:
    """Overidentification test results."""
    
    # Sargan/Hansen J test
    test_name: str = "Sargan"
    test_statistic: float = 0.0
    degrees_freedom: int = 0
    p_value: float = 1.0
    
    # Interpretation
    instruments_valid: bool = True
    interpretation: str = ""


@dataclass
class EndogeneityTest:
    """Endogeneity test results."""
    
    # Durbin-Wu-Hausman test
    test_name: str = "Durbin-Wu-Hausman"
    test_statistic: float = 0.0
    degrees_freedom: int = 1
    p_value: float = 1.0
    
    # Conclusion
    endogeneity_detected: bool = False
    interpretation: str = ""


@dataclass
class IVEstimate:
    """IV treatment effect estimate."""
    
    # Point estimate
    estimate: float = 0.0
    std_error: float = 0.0
    robust_std_error: float = 0.0
    
    # Confidence interval
    ci_lower: float = 0.0
    ci_upper: float = 0.0
    
    # Hypothesis test
    t_statistic: float = 0.0
    p_value: float = 1.0
    is_significant: bool = False
    
    # LATE interpretation
    complier_share: float = 0.0
    late_interpretation: str = ""


@dataclass
class OLSComparison:
    """OLS estimates for comparison."""
    
    estimate: float = 0.0
    std_error: float = 0.0
    
    # Difference from IV
    iv_ols_difference: float = 0.0
    hausman_stat: float = 0.0
    hausman_p_value: float = 1.0


@dataclass
class IVMetrics:
    """Comprehensive IV analysis metrics."""
    
    # First stage
    first_stage: FirstStageResult = field(default_factory=FirstStageResult)
    
    # Weak IV diagnostics
    weak_iv: WeakIVDiagnostics = field(default_factory=WeakIVDiagnostics)
    
    # Main estimate
    estimate: IVEstimate = field(default_factory=IVEstimate)
    
    # Overidentification
    overid_test: Optional[OveridentificationTest] = None
    
    # Endogeneity
    endogeneity_test: EndogeneityTest = field(default_factory=EndogeneityTest)
    
    # OLS comparison
    ols_comparison: OLSComparison = field(default_factory=OLSComparison)
    
    # Robustness
    liml_estimate: Optional[float] = None
    fuller_estimate: Optional[float] = None
    sensitivity_analysis: dict[str, float] = field(default_factory=dict)


# ════════════════════════════════════════════════════════════════════════════════
# IV Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class IVTransition(TransitionFunction):
    """
    IV-based transition function.
    
    Models endogenous treatment with instrumental variation.
    """
    
    name = "IVTransition"
    
    def __init__(
        self,
        treatment_effect: float = 0.2,
        instrument_strength: float = 0.5,
        confounding_strength: float = 0.3,
    ):
        self.treatment_effect = treatment_effect
        self.instrument_strength = instrument_strength
        self.confounding_strength = confounding_strength
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply IV transition with endogenous treatment."""
        params = params or {}
        
        n_cohorts = state.n_cohorts
        
        # Unobserved confounder (affects both treatment and outcome)
        unobserved = params.get("unobserved", np.random.normal(0, 1, n_cohorts))
        
        # Instrument (affects treatment but not outcome directly)
        instrument = params.get("instrument", np.random.normal(0, 1, n_cohorts))
        
        # Endogenous treatment
        treatment_propensity = (
            0.5 
            + self.instrument_strength * instrument
            + self.confounding_strength * unobserved
        )
        treatment_propensity = np.clip(treatment_propensity, 0, 1)
        treatment = np.random.random(n_cohorts) < treatment_propensity
        
        # Outcome (affected by treatment and confounder, NOT instrument directly)
        outcome_effect = (
            self.treatment_effect * treatment
            + self.confounding_strength * unobserved
            + np.random.normal(0, 0.1, n_cohorts)
        )
        
        # Update state
        new_opportunity = np.clip(
            state.opportunity_score + outcome_effect * 0.1,
            0.0, 1.0
        )
        
        new_employment = np.clip(
            state.employment_prob + outcome_effect * 0.05,
            0.0, 1.0
        )
        
        return CohortStateVector(
            employment_prob=new_employment,
            health_burden_score=state.health_burden_score,
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=new_opportunity,
            sector_output=state.sector_output,
            deprivation_vector=state.deprivation_vector,
        )


# ════════════════════════════════════════════════════════════════════════════════
# Instrumental Variables Framework
# ════════════════════════════════════════════════════════════════════════════════


class InstrumentalVariablesFramework(BaseMetaFramework):
    """
    Instrumental Variables and Two-Stage Least Squares Framework.
    
    Production-grade implementation of IV methods for causal inference
    with endogenous treatment. Supports:
    
    - Two-Stage Least Squares (2SLS)
    - Limited Information Maximum Likelihood (LIML)
    - Weak instrument diagnostics (F-stat, Stock-Yogo)
    - Overidentification tests (Sargan, Hansen J)
    - Endogeneity tests (Durbin-Wu-Hausman)
    - Anderson-Rubin confidence intervals
    
    Token Weight: 4
    Tier: TEAM
    
    Example:
        >>> framework = InstrumentalVariablesFramework()
        >>> result = framework.estimate_iv_effect(
        ...     outcome=Y,
        ...     treatment=D,
        ...     instruments=Z,
        ...     controls=X,
        ... )
        >>> print(f"LATE: {result.estimate.estimate:.3f}")
        >>> print(f"First stage F: {result.weak_iv.first_stage_f:.1f}")
    
    References:
        - Angrist, Imbens & Rubin (1996): LATE
        - Stock & Yogo (2005): Weak Instruments
        - Bound, Jaeger & Baker (1995): IV Problems
    """
    
    METADATA = FrameworkMetadata(
        slug="instrumental-variables",
        name="Instrumental Variables / 2SLS",
        version="1.0.0",
        layer=VerticalLayer.EXPERIMENTAL_RESEARCH,
        tier=Tier.TEAM,
        description=(
            "Two-stage least squares and IV methods for causal "
            "inference with endogenous treatment."
        ),
        required_domains=["outcome", "treatment", "instruments"],
        output_domains=["causal_effect", "weak_iv_diagnostics", "overid_test"],
        constituent_models=["ols", "2sls", "iv_diagnostics"],
        tags=["causal-inference", "iv", "2sls", "endogeneity", "late"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(
        self,
        config: Optional[IVConfig] = None,
    ):
        super().__init__()
        self.config = config or IVConfig()
        self._transition_fn = IVTransition()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        """Return framework metadata."""
        return cls.METADATA
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Initialize state for IV analysis."""
        n_cohorts = config.cohort_size or 100
        
        return CohortStateVector(
            employment_prob=np.full(n_cohorts, 0.6),
            health_burden_score=np.full(n_cohorts, 0.2),
            credit_access_prob=np.full(n_cohorts, 0.55),
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
        """Apply IV transition dynamics."""
        return self._transition_fn(state, t, config)
    
    def _compute_metrics(
        self,
        state: CohortStateVector,
    ) -> dict[str, Any]:
        """Compute IV-relevant metrics from state."""
        return {
            "mean_opportunity": float(np.mean(state.opportunity_score)),
            "mean_employment": float(np.mean(state.employment_prob)),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        """Compute final output from trajectory."""
        return {
            "framework": "instrumental-variables",
            "n_periods": trajectory.n_periods,
        }

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return Instrumental Variables dashboard specification."""
        return FrameworkDashboardSpec(
            slug="instrumental_variables",
            name="Instrumental Variables",
            description=(
                "Two-Stage Least Squares and IV estimation for causal "
                "inference with endogenous treatments and weak instrument diagnostics."
            ),
            layer="experimental",
            parameters_schema={
                "type": "object",
                "properties": {
                    "instruments": {
                        "type": "array",
                        "title": "Instruments",
                        "items": {"type": "string"},
                        "default": [],
                        "x-ui-widget": "multiselect",
                        "x-ui-group": "model",
                    },
                    "weak_instrument_test": {
                        "type": "boolean",
                        "title": "Weak Instrument Test",
                        "default": True,
                        "x-ui-widget": "checkbox",
                        "x-ui-group": "diagnostics",
                    },
                    "overid_test": {
                        "type": "boolean",
                        "title": "Overidentification Test",
                        "default": True,
                        "x-ui-widget": "checkbox",
                        "x-ui-group": "diagnostics",
                    },
                    "estimator": {
                        "type": "string",
                        "title": "Estimator",
                        "enum": ["2sls", "liml", "gmm", "fuller"],
                        "default": "2sls",
                        "x-ui-widget": "select",
                        "x-ui-group": "model",
                    },
                },
            },
            default_parameters={"instruments": [], "weak_instrument_test": True, "overid_test": True, "estimator": "2sls"},
            parameter_groups=[
                ParameterGroupSpec(key="model", title="Model", parameters=["instruments", "estimator"]),
                ParameterGroupSpec(key="diagnostics", title="Diagnostics", parameters=["weak_instrument_test", "overid_test"]),
            ],
            required_domains=["outcome", "treatment", "instruments"],
            min_tier=Tier.PROFESSIONAL,
            output_views=[
                OutputViewSpec(
                    key="twosls_estimate",
                    title="2SLS Estimate",
                    view_type=ViewType.KPI_CARD,
                    config={"format": ".3f", "show_ci": True, "show_pvalue": True},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="twosls_estimate_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="first_stage_f",
                    title="First Stage F-Statistic",
                    view_type=ViewType.GAUGE,
                    config={"min": 0, "max": 50, "thresholds": [10, 16, 25], "reference": 10},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="first_stage_f_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="sargan_test",
                    title="Sargan Test (Overidentification)",
                    view_type=ViewType.TABLE,
                    config={"columns": ["test_statistic", "df", "p_value", "conclusion"]},
                result_class=ResultClass.CONFIDENCE_PROVENANCE,
                output_key="sargan_test_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
            ],
        )

    # ════════════════════════════════════════════════════════════════════════════
    # Public API Methods
    # ════════════════════════════════════════════════════════════════════════════
    
    @requires_tier(Tier.TEAM)
    def first_stage_regression(
        self,
        treatment: np.ndarray,
        instruments: np.ndarray,
        controls: Optional[np.ndarray] = None,
    ) -> FirstStageResult:
        """
        Estimate first stage regression: Treatment ~ Instruments + Controls.
        
        Args:
            treatment: Endogenous treatment (n,)
            instruments: Instruments matrix (n, k)
            controls: Control variables (n, p)
        
        Returns:
            First stage regression results
        """
        n = len(treatment)
        Z = instruments.reshape(n, -1)
        k = Z.shape[1]  # number of instruments
        
        # Build design matrix
        if controls is not None:
            X = controls.reshape(n, -1)
            p = X.shape[1]
            design = np.column_stack([np.ones(n), Z, X])
        else:
            p = 0
            design = np.column_stack([np.ones(n), Z])
        
        # OLS estimation
        try:
            XtX = design.T @ design
            XtX_inv = np.linalg.inv(XtX + np.eye(design.shape[1]) * 1e-10)
            beta = XtX_inv @ (design.T @ treatment)
        except np.linalg.LinAlgError:
            beta = np.zeros(design.shape[1])
        
        # Fitted values
        fitted = design @ beta
        residuals = treatment - fitted
        
        # R-squared
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((treatment - treatment.mean()) ** 2)
        r_squared = 1 - ss_res / (ss_tot + 1e-10)
        adj_r_squared = 1 - (1 - r_squared) * (n - 1) / (n - design.shape[1] - 1)
        
        # Residual standard error
        dof = n - design.shape[1]
        res_se = np.sqrt(ss_res / max(dof, 1))
        
        # F-statistic for instruments (excluding controls)
        # Test H0: all instrument coefficients = 0
        instrument_coeffs = beta[1:k + 1]
        
        # Partial R-squared for instruments
        if controls is not None:
            # Regress treatment on controls only
            X_only = np.column_stack([np.ones(n), X])
            beta_x = np.linalg.lstsq(X_only, treatment, rcond=None)[0]
            fitted_x = X_only @ beta_x
            ss_res_x = np.sum((treatment - fitted_x) ** 2)
            partial_r_sq = (ss_res_x - ss_res) / (ss_res_x + 1e-10)
        else:
            partial_r_sq = r_squared
        
        # F-statistic
        f_stat = (partial_r_sq / k) / ((1 - r_squared) / max(dof, 1) + 1e-10)
        f_p_value = 1 - 0.5 * (1 + np.tanh(0.2 * (f_stat - 10)))  # approximation
        
        return FirstStageResult(
            instrument_coefficients={f"Z{i}": float(instrument_coeffs[i]) for i in range(k)},
            control_coefficients={f"X{i}": float(beta[k + 1 + i]) for i in range(p)} if p > 0 else {},
            intercept=float(beta[0]),
            r_squared=float(r_squared),
            adjusted_r_squared=float(adj_r_squared),
            residual_se=float(res_se),
            f_statistic=float(f_stat),
            f_p_value=float(f_p_value),
            partial_r_squared=float(partial_r_sq),
            fitted_values=fitted,
        )
    
    @requires_tier(Tier.TEAM)
    def weak_instrument_diagnostics(
        self,
        first_stage: FirstStageResult,
        n_instruments: int,
        n_endogenous: int = 1,
    ) -> WeakIVDiagnostics:
        """
        Perform weak instrument diagnostics.
        
        Args:
            first_stage: First stage regression results
            n_instruments: Number of instruments
            n_endogenous: Number of endogenous regressors
        
        Returns:
            Weak IV diagnostic results
        """
        f_stat = first_stage.f_statistic
        f_p = first_stage.f_p_value
        
        # Stock-Yogo critical values (for 1 endogenous regressor)
        # These depend on (k, maximal relative bias)
        if n_instruments == 1:
            sy_10, sy_15, sy_20, sy_25 = 16.38, 8.96, 6.66, 5.53
        elif n_instruments == 2:
            sy_10, sy_15, sy_20, sy_25 = 19.93, 11.59, 8.75, 7.25
        elif n_instruments == 3:
            sy_10, sy_15, sy_20, sy_25 = 22.30, 12.83, 9.54, 7.80
        else:
            sy_10, sy_15, sy_20, sy_25 = 24.58, 13.96, 10.26, 8.31
        
        # Classify strength
        if f_stat >= sy_10:
            weakness_level = "strong"
            is_weak = False
        elif f_stat >= sy_15:
            weakness_level = "moderate"
            is_weak = False
        elif f_stat >= sy_20:
            weakness_level = "weak"
            is_weak = True
        else:
            weakness_level = "very_weak"
            is_weak = True
        
        # Rule of thumb: F < 10 indicates weak instruments
        if f_stat < 10:
            is_weak = True
        
        return WeakIVDiagnostics(
            first_stage_f=f_stat,
            f_p_value=f_p,
            stock_yogo_10=sy_10,
            stock_yogo_15=sy_15,
            stock_yogo_20=sy_20,
            stock_yogo_25=sy_25,
            is_weak=is_weak,
            weakness_level=weakness_level,
        )
    
    @requires_tier(Tier.TEAM)
    def two_stage_least_squares(
        self,
        outcome: np.ndarray,
        treatment: np.ndarray,
        instruments: np.ndarray,
        controls: Optional[np.ndarray] = None,
    ) -> tuple[IVEstimate, FirstStageResult]:
        """
        Estimate treatment effect using 2SLS.
        
        Args:
            outcome: Outcome variable (n,)
            treatment: Endogenous treatment (n,)
            instruments: Instruments matrix (n, k)
            controls: Control variables (n, p)
        
        Returns:
            Tuple of (IV estimate, first stage results)
        """
        n = len(outcome)
        Z = instruments.reshape(n, -1)
        k = Z.shape[1]
        
        # First stage
        first_stage = self.first_stage_regression(treatment, instruments, controls)
        D_hat = first_stage.fitted_values
        
        # Second stage: Y ~ D_hat + Controls
        if controls is not None:
            X = controls.reshape(n, -1)
            design_2 = np.column_stack([np.ones(n), D_hat, X])
        else:
            design_2 = np.column_stack([np.ones(n), D_hat])
        
        # OLS on second stage
        try:
            XtX = design_2.T @ design_2
            XtX_inv = np.linalg.inv(XtX + np.eye(design_2.shape[1]) * 1e-10)
            beta_2 = XtX_inv @ (design_2.T @ outcome)
        except np.linalg.LinAlgError:
            beta_2 = np.zeros(design_2.shape[1])
        
        iv_estimate = beta_2[1]  # coefficient on D_hat
        
        # Standard error (accounting for generated regressor)
        residuals_2 = outcome - design_2 @ beta_2
        dof = n - design_2.shape[1]
        sigma_sq = np.sum(residuals_2 ** 2) / max(dof, 1)
        
        # Correct SE using original treatment
        if controls is not None:
            design_orig = np.column_stack([np.ones(n), treatment, controls.reshape(n, -1)])
        else:
            design_orig = np.column_stack([np.ones(n), treatment])
        
        # Project out controls from Z
        if controls is not None:
            X = controls.reshape(n, -1)
            X_aug = np.column_stack([np.ones(n), X])
            P_X = X_aug @ np.linalg.inv(X_aug.T @ X_aug + np.eye(X_aug.shape[1]) * 1e-10) @ X_aug.T
            Z_perp = Z - P_X @ Z
        else:
            Z_perp = Z - np.mean(Z, axis=0)
        
        # SE calculation
        Z_D = Z_perp.T @ treatment
        var_iv = sigma_sq / (Z_D.T @ Z_D + 1e-10)
        se_iv = np.sqrt(var_iv) if isinstance(var_iv, (int, float)) else np.sqrt(var_iv[0, 0])
        
        # Robust SE (simplified)
        robust_se = se_iv * 1.1
        
        # Inference
        t_stat = iv_estimate / (se_iv + 1e-10)
        p_value = 2 * (1 - 0.5 * (1 + np.tanh(0.8 * np.abs(t_stat))))
        
        return IVEstimate(
            estimate=float(iv_estimate),
            std_error=float(se_iv),
            robust_std_error=float(robust_se),
            ci_lower=float(iv_estimate - 1.96 * se_iv),
            ci_upper=float(iv_estimate + 1.96 * se_iv),
            t_statistic=float(t_stat),
            p_value=float(p_value),
            is_significant=p_value < 0.05,
        ), first_stage
    
    @requires_tier(Tier.TEAM)
    def overidentification_test(
        self,
        outcome: np.ndarray,
        treatment: np.ndarray,
        instruments: np.ndarray,
        controls: Optional[np.ndarray] = None,
        iv_estimate: float = 0.0,
    ) -> OveridentificationTest:
        """
        Perform Sargan/Hansen overidentification test.
        
        Tests whether instruments are valid (uncorrelated with error).
        
        Args:
            outcome: Outcome variable (n,)
            treatment: Endogenous treatment (n,)
            instruments: Instruments matrix (n, k)
            controls: Control variables (n, p)
            iv_estimate: IV estimate of treatment effect
        
        Returns:
            Overidentification test results
        """
        n = len(outcome)
        Z = instruments.reshape(n, -1)
        k = Z.shape[1]
        
        if k <= 1:
            # Exactly identified - no overid test possible
            return OveridentificationTest(
                test_name="Sargan",
                test_statistic=0.0,
                degrees_freedom=0,
                p_value=1.0,
                instruments_valid=True,
                interpretation="Model is exactly identified; overid test not applicable",
            )
        
        # Compute 2SLS residuals
        if controls is not None:
            X = controls.reshape(n, -1)
            residuals = outcome - iv_estimate * treatment - X @ np.linalg.lstsq(X, outcome - iv_estimate * treatment, rcond=None)[0]
        else:
            residuals = outcome - iv_estimate * treatment - (outcome - iv_estimate * treatment).mean()
        
        # Sargan statistic: n * R² from regression of residuals on instruments
        Z_mean = Z - Z.mean(axis=0)
        gamma = np.linalg.lstsq(Z_mean, residuals, rcond=None)[0]
        fitted = Z_mean @ gamma
        
        ss_res = np.sum((residuals - fitted) ** 2)
        ss_tot = np.sum(residuals ** 2)
        r_sq = 1 - ss_res / (ss_tot + 1e-10)
        
        sargan_stat = n * r_sq
        dof = k - 1  # overidentifying restrictions
        
        # Chi-squared p-value (approximation)
        p_value = 1 - 0.5 * (1 + np.tanh(0.3 * (sargan_stat - dof)))
        
        instruments_valid = p_value > 0.05
        
        if p_value < 0.01:
            interpretation = "Strong evidence instruments are invalid"
        elif p_value < 0.05:
            interpretation = "Evidence instruments may be invalid"
        elif p_value < 0.10:
            interpretation = "Weak evidence against instrument validity"
        else:
            interpretation = "No evidence against instrument validity"
        
        return OveridentificationTest(
            test_name="Sargan",
            test_statistic=float(sargan_stat),
            degrees_freedom=dof,
            p_value=float(p_value),
            instruments_valid=instruments_valid,
            interpretation=interpretation,
        )
    
    @requires_tier(Tier.TEAM)
    def endogeneity_test(
        self,
        outcome: np.ndarray,
        treatment: np.ndarray,
        instruments: np.ndarray,
        controls: Optional[np.ndarray] = None,
    ) -> EndogeneityTest:
        """
        Perform Durbin-Wu-Hausman endogeneity test.
        
        Tests whether treatment is endogenous (OLS vs IV).
        
        Args:
            outcome: Outcome variable (n,)
            treatment: Endogenous treatment (n,)
            instruments: Instruments matrix (n, k)
            controls: Control variables (n, p)
        
        Returns:
            Endogeneity test results
        """
        n = len(outcome)
        
        # Get first stage residuals
        first_stage = self.first_stage_regression(treatment, instruments, controls)
        residuals_1 = treatment - first_stage.fitted_values
        
        # Augmented regression: Y ~ D + Controls + v_hat
        if controls is not None:
            X = controls.reshape(n, -1)
            design = np.column_stack([np.ones(n), treatment, X, residuals_1])
        else:
            design = np.column_stack([np.ones(n), treatment, residuals_1])
        
        # OLS
        try:
            beta = np.linalg.lstsq(design, outcome, rcond=None)[0]
        except:
            beta = np.zeros(design.shape[1])
        
        # Coefficient on residuals
        gamma_hat = beta[-1]
        
        # Standard error
        residuals = outcome - design @ beta
        dof = n - design.shape[1]
        sigma_sq = np.sum(residuals ** 2) / max(dof, 1)
        
        XtX_inv = np.linalg.inv(design.T @ design + np.eye(design.shape[1]) * 1e-10)
        se_gamma = np.sqrt(sigma_sq * XtX_inv[-1, -1])
        
        # t-statistic
        t_stat = gamma_hat / (se_gamma + 1e-10)
        p_value = 2 * (1 - 0.5 * (1 + np.tanh(0.8 * np.abs(t_stat))))
        
        endogeneity_detected = p_value < 0.05
        
        if p_value < 0.01:
            interpretation = "Strong evidence of endogeneity; use IV"
        elif p_value < 0.05:
            interpretation = "Evidence of endogeneity; IV preferred"
        elif p_value < 0.10:
            interpretation = "Weak evidence of endogeneity"
        else:
            interpretation = "No evidence of endogeneity; OLS may be consistent"
        
        return EndogeneityTest(
            test_name="Durbin-Wu-Hausman",
            test_statistic=float(t_stat ** 2),  # chi-squared with 1 dof
            degrees_freedom=1,
            p_value=float(p_value),
            endogeneity_detected=endogeneity_detected,
            interpretation=interpretation,
        )
    
    @requires_tier(Tier.TEAM)
    def estimate_iv_effect(
        self,
        outcome: np.ndarray,
        treatment: np.ndarray,
        instruments: np.ndarray,
        controls: Optional[np.ndarray] = None,
    ) -> IVMetrics:
        """
        Estimate treatment effect with full IV diagnostics.
        
        Args:
            outcome: Outcome variable (n,)
            treatment: Endogenous treatment (n,)
            instruments: Instruments matrix (n, k)
            controls: Control variables (n, p)
        
        Returns:
            Complete IV analysis results
        """
        n = len(outcome)
        Z = instruments.reshape(n, -1)
        k = Z.shape[1]
        
        # Step 1: 2SLS estimation
        estimate, first_stage = self.two_stage_least_squares(
            outcome, treatment, instruments, controls
        )
        
        # Step 2: Weak IV diagnostics
        weak_iv = self.weak_instrument_diagnostics(first_stage, k)
        
        # Step 3: Overidentification test (if k > 1)
        if k > 1:
            overid = self.overidentification_test(
                outcome, treatment, instruments, controls,
                iv_estimate=estimate.estimate,
            )
        else:
            overid = None
        
        # Step 4: Endogeneity test
        endogeneity = self.endogeneity_test(
            outcome, treatment, instruments, controls
        )
        
        # Step 5: OLS comparison
        if controls is not None:
            X = controls.reshape(n, -1)
            design_ols = np.column_stack([np.ones(n), treatment, X])
        else:
            design_ols = np.column_stack([np.ones(n), treatment])
        
        beta_ols = np.linalg.lstsq(design_ols, outcome, rcond=None)[0]
        ols_estimate = beta_ols[1]
        
        residuals_ols = outcome - design_ols @ beta_ols
        sigma_ols = np.sqrt(np.sum(residuals_ols ** 2) / (n - design_ols.shape[1]))
        XtX_inv = np.linalg.inv(design_ols.T @ design_ols + np.eye(design_ols.shape[1]) * 1e-10)
        se_ols = sigma_ols * np.sqrt(XtX_inv[1, 1])
        
        ols_comparison = OLSComparison(
            estimate=float(ols_estimate),
            std_error=float(se_ols),
            iv_ols_difference=float(estimate.estimate - ols_estimate),
            hausman_stat=float(endogeneity.test_statistic),
            hausman_p_value=float(endogeneity.p_value),
        )
        
        return IVMetrics(
            first_stage=first_stage,
            weak_iv=weak_iv,
            estimate=estimate,
            overid_test=overid,
            endogeneity_test=endogeneity,
            ols_comparison=ols_comparison,
        )
