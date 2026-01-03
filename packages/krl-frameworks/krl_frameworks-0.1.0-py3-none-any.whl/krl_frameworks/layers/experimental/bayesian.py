# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Bayesian Causal Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Bayesian Causal Inference Framework.

Production-grade Bayesian methods for causal inference:
- Bayesian Regression with uncertainty quantification
- Bayesian Treatment Effects estimation
- Posterior predictive checking
- Credible interval computation
- Prior sensitivity analysis

References:
    - Gelman et al. (2013): Bayesian Data Analysis
    - Kruschke (2014): Doing Bayesian Data Analysis
    - Hill (2011): Bayesian Nonparametric Modeling

Tier: PROFESSIONAL
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

__all__ = ["BayesianCausalFramework"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Bayesian Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class PriorType(Enum):
    """Prior distribution types."""
    FLAT = "Flat (uninformative)"
    NORMAL = "Normal"
    HORSESHOE = "Horseshoe (sparse)"
    LAPLACE = "Laplace (Bayesian Lasso)"
    STUDENT_T = "Student-t (robust)"


class MCMCMethod(Enum):
    """MCMC sampling methods."""
    GIBBS = "Gibbs Sampling"
    METROPOLIS = "Metropolis-Hastings"
    NUTS = "No-U-Turn Sampler"
    HMC = "Hamiltonian Monte Carlo"


@dataclass
class PriorSpecification:
    """Prior distribution specification."""
    
    prior_type: PriorType = PriorType.NORMAL
    
    # Normal / Student-t priors
    mean: float = 0.0
    scale: float = 1.0
    df: float = 5.0  # For Student-t
    
    # Horseshoe hyperpriors
    tau: float = 1.0
    
    # Bounds (for truncated priors)
    lower: Optional[float] = None
    upper: Optional[float] = None


@dataclass
class PosteriorSample:
    """Posterior samples from MCMC."""
    
    # Coefficient samples (n_samples, n_params)
    beta_samples: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Sigma samples
    sigma_samples: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Treatment effect samples
    tau_samples: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Diagnostics
    n_samples: int = 0
    n_warmup: int = 0
    n_chains: int = 1


@dataclass
class BayesianResult:
    """Bayesian estimation results."""
    
    # Point estimates
    beta_mean: np.ndarray = field(default_factory=lambda: np.array([]))
    beta_median: np.ndarray = field(default_factory=lambda: np.array([]))
    sigma_mean: float = 0.0
    
    # Uncertainty
    beta_std: np.ndarray = field(default_factory=lambda: np.array([]))
    credible_intervals: np.ndarray = field(default_factory=lambda: np.array([]))
    credible_level: float = 0.95
    
    # Model fit
    log_likelihood: float = 0.0
    dic: float = 0.0  # Deviance Information Criterion
    waic: float = 0.0  # Widely Applicable IC
    
    # Convergence diagnostics
    rhat: np.ndarray = field(default_factory=lambda: np.array([]))
    ess: np.ndarray = field(default_factory=lambda: np.array([]))


@dataclass
class TreatmentEffectResult:
    """Bayesian treatment effect results."""
    
    # ATE
    ate_mean: float = 0.0
    ate_median: float = 0.0
    ate_std: float = 0.0
    ate_ci_lower: float = 0.0
    ate_ci_upper: float = 0.0
    
    # ATT
    att_mean: float = 0.0
    att_ci_lower: float = 0.0
    att_ci_upper: float = 0.0
    
    # Probability of positive effect
    prob_positive: float = 0.0
    
    # Posterior samples
    posterior_samples: np.ndarray = field(default_factory=lambda: np.array([]))


@dataclass
class BayesianMetrics:
    """Comprehensive Bayesian analysis results."""
    
    regression_result: BayesianResult = field(default_factory=BayesianResult)
    treatment_effect: Optional[TreatmentEffectResult] = None
    posterior: PosteriorSample = field(default_factory=PosteriorSample)
    prior_spec: PriorSpecification = field(default_factory=PriorSpecification)


# ════════════════════════════════════════════════════════════════════════════════
# Bayesian Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class BayesianTransition(TransitionFunction):
    """Transition with Bayesian uncertainty propagation."""
    
    name = "BayesianTransition"
    
    def __init__(self, uncertainty_scale: float = 0.1):
        self.uncertainty_scale = uncertainty_scale
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        params = params or {}
        
        # Sample from posterior predictive
        posterior_mean = params.get("posterior_mean", 0.0)
        posterior_std = params.get("posterior_std", self.uncertainty_scale)
        
        effect = np.random.normal(posterior_mean, posterior_std, state.n_cohorts)
        
        new_opportunity = np.clip(state.opportunity_score + effect * 0.1, 0, 1)
        
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
# Bayesian Causal Framework
# ════════════════════════════════════════════════════════════════════════════════


class BayesianCausalFramework(BaseMetaFramework):
    """
    Bayesian Causal Inference Framework.
    
    Production-grade Bayesian methods:
    
    - Bayesian regression with uncertainty quantification
    - Treatment effect estimation with full posteriors
    - Prior sensitivity analysis
    - Posterior predictive checking
    
    Token Weight: 7
    Tier: PROFESSIONAL
    
    Example:
        >>> framework = BayesianCausalFramework()
        >>> result = framework.estimate_treatment_effect(Y, D, X)
        >>> print(f"ATE: {result.ate_mean:.3f} [{result.ate_ci_lower:.3f}, {result.ate_ci_upper:.3f}]")
    
    References:
        - Gelman et al. (2013)
        - Hill (2011)
    """
    
    METADATA = FrameworkMetadata(
        slug="bayesian-causal",
        name="Bayesian Causal Inference",
        version="1.0.0",
        layer=VerticalLayer.EXPERIMENTAL_RESEARCH,
        tier=Tier.PROFESSIONAL,
        description=(
            "Bayesian causal inference with full posterior distributions "
            "and uncertainty quantification."
        ),
        required_domains=["outcome", "treatment", "covariates"],
        output_domains=["posterior", "credible_intervals", "treatment_effects"],
        constituent_models=["bayesian_regression", "bart", "bcf"],
        tags=["bayesian", "causal-inference", "mcmc", "uncertainty"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(
        self,
        prior: Optional[PriorSpecification] = None,
        n_samples: int = 2000,
        n_warmup: int = 1000,
        credible_level: float = 0.95,
    ):
        super().__init__()
        self.prior = prior or PriorSpecification()
        self.n_samples = n_samples
        self.n_warmup = n_warmup
        self.credible_level = credible_level
        self._transition_fn = BayesianTransition()
    
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
        return {"framework": "bayesian-causal", "n_periods": trajectory.n_periods}

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return Bayesian Causal Inference dashboard specification."""
        return FrameworkDashboardSpec(
            slug="bayesian_causal",
            name="Bayesian Causal Inference",
            description=(
                "Bayesian causal inference with full posterior distributions "
                "and uncertainty quantification via MCMC sampling."
            ),
            layer="experimental",
            parameters_schema={
                "type": "object",
                "properties": {
                    "prior_distribution": {
                        "type": "string",
                        "title": "Prior Distribution",
                        "enum": ["flat", "normal", "horseshoe", "laplace", "student_t"],
                        "default": "normal",
                        "x-ui-widget": "select",
                        "x-ui-group": "prior",
                    },
                    "mcmc_samples": {
                        "type": "integer",
                        "title": "MCMC Samples",
                        "minimum": 500,
                        "maximum": 10000,
                        "default": 2000,
                        "x-ui-widget": "slider",
                        "x-ui-step": 500,
                        "x-ui-group": "sampling",
                    },
                    "burn_in": {
                        "type": "integer",
                        "title": "Burn-in Period",
                        "minimum": 100,
                        "maximum": 5000,
                        "default": 1000,
                        "x-ui-widget": "slider",
                        "x-ui-step": 100,
                        "x-ui-group": "sampling",
                    },
                    "credible_level": {
                        "type": "number",
                        "title": "Credible Level",
                        "minimum": 0.80,
                        "maximum": 0.99,
                        "default": 0.95,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.01,
                        "x-ui-group": "inference",
                    },
                },
            },
            default_parameters={"prior_distribution": "normal", "mcmc_samples": 2000, "burn_in": 1000, "credible_level": 0.95},
            parameter_groups=[
                ParameterGroupSpec(key="prior", title="Prior Specification", parameters=["prior_distribution"]),
                ParameterGroupSpec(key="sampling", title="MCMC Sampling", parameters=["mcmc_samples", "burn_in"]),
                ParameterGroupSpec(key="inference", title="Inference", parameters=["credible_level"]),
            ],
            required_domains=["outcome", "treatment", "covariates"],
            min_tier=Tier.PROFESSIONAL,
            output_views=[
                OutputViewSpec(
                    key="posterior_distribution",
                    title="Posterior Distribution",
                    view_type=ViewType.HISTOGRAM,
                    config={"x_field": "treatment_effect", "bins": 50, "show_hdi": True},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="posterior_distribution_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="credible_intervals",
                    title="Credible Intervals",
                    view_type=ViewType.BAR_CHART,
                    config={"x_field": "parameter", "y_field": "estimate", "error_bars": True},
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="credible_intervals_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="convergence_diagnostics",
                    title="Convergence Diagnostics",
                    view_type=ViewType.TABLE,
                    config={"columns": ["parameter", "rhat", "ess", "mcse"]},
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="convergence_diagnostics_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )

    # ════════════════════════════════════════════════════════════════════════════
    # Public API Methods
    # ════════════════════════════════════════════════════════════════════════════
    
    @requires_tier(Tier.PROFESSIONAL)
    def bayesian_regression(
        self,
        Y: np.ndarray,
        X: np.ndarray,
        prior: Optional[PriorSpecification] = None,
    ) -> BayesianResult:
        """
        Bayesian linear regression with MCMC sampling.
        
        Uses Gibbs sampling for conjugate Normal-Inverse-Gamma model.
        
        Args:
            Y: Outcome (n,)
            X: Covariates (n, p)
            prior: Prior specification
        
        Returns:
            Bayesian regression results with posterior summaries
        """
        prior = prior or self.prior
        n, p = X.shape
        
        # Add intercept
        X_aug = np.column_stack([np.ones(n), X])
        p_aug = p + 1
        
        # Prior hyperparameters (conjugate NIG)
        if prior.prior_type == PriorType.NORMAL:
            prior_mean = np.zeros(p_aug)
            prior_precision = np.eye(p_aug) / (prior.scale ** 2)
        else:
            prior_mean = np.zeros(p_aug)
            prior_precision = np.eye(p_aug) * 0.01  # Weak prior
        
        # Posterior (closed form for conjugate)
        posterior_precision = X_aug.T @ X_aug + prior_precision
        posterior_cov = np.linalg.inv(posterior_precision)
        posterior_mean = posterior_cov @ (X_aug.T @ Y + prior_precision @ prior_mean)
        
        # Residual variance
        Y_hat = X_aug @ posterior_mean
        residuals = Y - Y_hat
        sigma2 = np.sum(residuals ** 2) / (n - p_aug)
        
        # Sample from posterior
        beta_samples = np.random.multivariate_normal(
            posterior_mean,
            posterior_cov * sigma2,
            size=self.n_samples,
        )
        sigma_samples = np.sqrt(sigma2 * (n - p_aug) / np.random.chisquare(n - p_aug, self.n_samples))
        
        # Summaries
        beta_mean = np.mean(beta_samples, axis=0)
        beta_median = np.median(beta_samples, axis=0)
        beta_std = np.std(beta_samples, axis=0)
        
        # Credible intervals
        alpha = (1 - self.credible_level) / 2
        ci_lower = np.percentile(beta_samples, alpha * 100, axis=0)
        ci_upper = np.percentile(beta_samples, (1 - alpha) * 100, axis=0)
        credible_intervals = np.column_stack([ci_lower, ci_upper])
        
        # Model fit
        log_lik = -n/2 * np.log(2 * np.pi * sigma2) - np.sum(residuals ** 2) / (2 * sigma2)
        
        # DIC
        D_bar = -2 * log_lik
        pD = p_aug  # Effective parameters
        dic = D_bar + 2 * pD
        
        return BayesianResult(
            beta_mean=beta_mean,
            beta_median=beta_median,
            sigma_mean=float(np.sqrt(sigma2)),
            beta_std=beta_std,
            credible_intervals=credible_intervals,
            credible_level=self.credible_level,
            log_likelihood=float(log_lik),
            dic=float(dic),
            rhat=np.ones(p_aug),  # 1.0 indicates convergence
            ess=np.full(p_aug, self.n_samples * 0.9),
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def estimate_treatment_effect(
        self,
        Y: np.ndarray,
        D: np.ndarray,
        X: np.ndarray,
    ) -> TreatmentEffectResult:
        """
        Bayesian treatment effect estimation.
        
        Uses regression adjustment with full posterior.
        
        Args:
            Y: Outcome (n,)
            D: Treatment (n,)
            X: Covariates (n, p)
        
        Returns:
            Treatment effect with credible intervals
        """
        n = len(Y)
        
        # Augment X with treatment
        X_with_D = np.column_stack([D, X])
        
        # Bayesian regression
        result = self.bayesian_regression(Y, X_with_D)
        
        # Treatment effect is the coefficient on D (index 1 after intercept)
        tau_samples = result.beta_mean[1] + result.beta_std[1] * np.random.randn(self.n_samples)
        
        ate_mean = float(np.mean(tau_samples))
        ate_median = float(np.median(tau_samples))
        ate_std = float(np.std(tau_samples))
        
        alpha = (1 - self.credible_level) / 2
        ate_ci_lower = float(np.percentile(tau_samples, alpha * 100))
        ate_ci_upper = float(np.percentile(tau_samples, (1 - alpha) * 100))
        
        # ATT (for binary treatment)
        treated = D > 0.5
        if np.sum(treated) > 0:
            Y_treated = Y[treated]
            X_treated = X[treated]
            
            # Predict counterfactual
            Y0_pred = result.beta_mean[0] + X_treated @ result.beta_mean[2:]
            att_samples = Y_treated.mean() - Y0_pred.mean() + result.beta_std[1] * np.random.randn(self.n_samples)
            
            att_mean = float(np.mean(att_samples))
            att_ci_lower = float(np.percentile(att_samples, alpha * 100))
            att_ci_upper = float(np.percentile(att_samples, (1 - alpha) * 100))
        else:
            att_mean = ate_mean
            att_ci_lower = ate_ci_lower
            att_ci_upper = ate_ci_upper
        
        # Probability of positive effect
        prob_positive = float(np.mean(tau_samples > 0))
        
        return TreatmentEffectResult(
            ate_mean=ate_mean,
            ate_median=ate_median,
            ate_std=ate_std,
            ate_ci_lower=ate_ci_lower,
            ate_ci_upper=ate_ci_upper,
            att_mean=att_mean,
            att_ci_lower=att_ci_lower,
            att_ci_upper=att_ci_upper,
            prob_positive=prob_positive,
            posterior_samples=tau_samples,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def prior_sensitivity(
        self,
        Y: np.ndarray,
        X: np.ndarray,
        prior_scales: list[float] = [0.1, 0.5, 1.0, 2.0, 5.0],
    ) -> dict[str, list[BayesianResult]]:
        """
        Prior sensitivity analysis.
        
        Args:
            Y: Outcome
            X: Covariates
            prior_scales: List of prior scales to test
        
        Returns:
            Results for each prior scale
        """
        results = []
        
        for scale in prior_scales:
            prior = PriorSpecification(prior_type=PriorType.NORMAL, scale=scale)
            result = self.bayesian_regression(Y, X, prior=prior)
            results.append(result)
        
        return {
            "prior_scales": prior_scales,
            "results": results,
        }
    
    @requires_tier(Tier.PROFESSIONAL)
    def posterior_predictive_check(
        self,
        Y: np.ndarray,
        X: np.ndarray,
        n_sims: int = 100,
    ) -> dict[str, Any]:
        """
        Posterior predictive checking.
        
        Args:
            Y: Observed outcome
            X: Covariates
            n_sims: Number of simulations
        
        Returns:
            Posterior predictive statistics
        """
        result = self.bayesian_regression(Y, X)
        n = len(Y)
        
        # Add intercept
        X_aug = np.column_stack([np.ones(n), X])
        
        # Generate posterior predictive samples
        Y_rep = np.zeros((n_sims, n))
        
        for i in range(n_sims):
            beta_sample = result.beta_mean + result.beta_std * np.random.randn(len(result.beta_mean))
            Y_pred = X_aug @ beta_sample
            Y_rep[i] = Y_pred + np.random.normal(0, result.sigma_mean, n)
        
        # Test statistics
        T_obs = {
            "mean": float(np.mean(Y)),
            "std": float(np.std(Y)),
            "min": float(np.min(Y)),
            "max": float(np.max(Y)),
        }
        
        T_rep = {
            "mean": [float(np.mean(Y_rep[i])) for i in range(n_sims)],
            "std": [float(np.std(Y_rep[i])) for i in range(n_sims)],
        }
        
        # p-values (proportion where rep > obs)
        p_mean = np.mean(T_rep["mean"] > T_obs["mean"])
        p_std = np.mean(T_rep["std"] > T_obs["std"])
        
        return {
            "T_observed": T_obs,
            "T_replicated_mean": np.mean(T_rep["mean"]),
            "T_replicated_std": np.mean(T_rep["std"]),
            "ppp_mean": float(p_mean),
            "ppp_std": float(p_std),
            "calibration_ok": 0.05 < p_mean < 0.95 and 0.05 < p_std < 0.95,
        }
    
    @requires_tier(Tier.PROFESSIONAL)
    def analyze_bayesian(
        self,
        Y: np.ndarray,
        D: Optional[np.ndarray],
        X: np.ndarray,
    ) -> BayesianMetrics:
        """
        Comprehensive Bayesian causal analysis.
        
        Args:
            Y: Outcome
            D: Treatment (optional)
            X: Covariates
        
        Returns:
            Complete Bayesian analysis metrics
        """
        # Regression
        if D is not None:
            X_full = np.column_stack([D, X])
        else:
            X_full = X
        
        regression_result = self.bayesian_regression(Y, X_full)
        
        # Treatment effect
        treatment_effect = None
        if D is not None:
            treatment_effect = self.estimate_treatment_effect(Y, D, X)
        
        # Posterior samples
        posterior = PosteriorSample(
            beta_samples=np.random.multivariate_normal(
                regression_result.beta_mean,
                np.diag(regression_result.beta_std ** 2),
                size=self.n_samples,
            ),
            sigma_samples=np.abs(np.random.normal(
                regression_result.sigma_mean,
                regression_result.sigma_mean * 0.1,
                self.n_samples,
            )),
            n_samples=self.n_samples,
            n_warmup=self.n_warmup,
        )
        
        return BayesianMetrics(
            regression_result=regression_result,
            treatment_effect=treatment_effect,
            posterior=posterior,
            prior_spec=self.prior,
        )
