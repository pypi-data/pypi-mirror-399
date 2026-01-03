# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Double Machine Learning Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Double Machine Learning (DML) Framework.

Production-grade implementation of debiased/orthogonal ML methods:
- Partially Linear Regression (PLR)
- Interactive Regression Model (IRM)
- Average Treatment Effects with Cross-Fitting
- Automatic Debiasing
- Honest Inference

References:
    - Chernozhukov et al. (2018): Double/Debiased Machine Learning
    - Chernozhukov et al. (2017): Double/Debiased/Neyman Machine Learning
    - Athey & Wager (2019): Estimating Treatment Effects with Causal Forests

Tier: PROFESSIONAL
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Mapping, Optional, Protocol

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

__all__ = ["DMLFramework"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# DML Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class DMLModel(Enum):
    """DML model types."""
    PLR = "Partially Linear Regression"
    IRM = "Interactive Regression Model"
    PLIV = "Partially Linear IV"
    IIVM = "Interactive IV Model"


class MLMethod(Enum):
    """Machine learning methods for nuisance estimation."""
    LASSO = "Lasso"
    RIDGE = "Ridge"
    RANDOM_FOREST = "Random Forest"
    GRADIENT_BOOSTING = "Gradient Boosting"
    NEURAL_NETWORK = "Neural Network"
    ENSEMBLE = "Stacked Ensemble"


class MLEstimator(Protocol):
    """Protocol for ML estimators."""
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> "MLEstimator":
        ...
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        ...


@dataclass
class CrossFitResult:
    """Results from cross-fitting procedure."""
    
    n_folds: int = 5
    
    # Residualized outcomes
    Y_residual: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Residualized treatment
    D_residual: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Fold assignments
    fold_idx: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Nuisance predictions
    g_hat: np.ndarray = field(default_factory=lambda: np.array([]))  # E[Y|X]
    m_hat: np.ndarray = field(default_factory=lambda: np.array([]))  # E[D|X]


@dataclass
class DMLResult:
    """DML estimation results."""
    
    # Treatment effect estimate
    theta: float = 0.0
    se: float = 0.0
    t_stat: float = 0.0
    p_value: float = 0.0
    ci_lower: float = 0.0
    ci_upper: float = 0.0
    
    # Model details
    model_type: DMLModel = DMLModel.PLR
    n_folds: int = 5
    n_observations: int = 0
    
    # Nuisance quality
    outcome_r2: float = 0.0
    treatment_r2: float = 0.0
    
    # Orthogonality
    orthogonality_score: float = 0.0


@dataclass
class HeterogeneousEffect:
    """Heterogeneous treatment effect for a subgroup."""
    
    subgroup_name: str = ""
    subgroup_mask: np.ndarray = field(default_factory=lambda: np.array([]))
    
    theta: float = 0.0
    se: float = 0.0
    ci_lower: float = 0.0
    ci_upper: float = 0.0
    n_obs: int = 0


@dataclass
class CATEResult:
    """Conditional Average Treatment Effect results."""
    
    # Individual treatment effects
    cate: np.ndarray = field(default_factory=lambda: np.array([]))
    cate_se: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # ATE
    ate: float = 0.0
    ate_se: float = 0.0
    
    # Heterogeneity
    effect_variance: float = 0.0
    heterogeneous_effects: list[HeterogeneousEffect] = field(default_factory=list)


@dataclass
class DMLMetrics:
    """Comprehensive DML analysis results."""
    
    # Main result
    main_result: DMLResult = field(default_factory=DMLResult)
    
    # Cross-fitting details
    cross_fit: CrossFitResult = field(default_factory=CrossFitResult)
    
    # CATE (if computed)
    cate_result: Optional[CATEResult] = None
    
    # ML method used
    ml_method: MLMethod = MLMethod.LASSO


# ════════════════════════════════════════════════════════════════════════════════
# Simple ML Estimators (Built-in)
# ════════════════════════════════════════════════════════════════════════════════


class LassoEstimator:
    """Simple Lasso implementation via coordinate descent."""
    
    def __init__(self, alpha: float = 0.1, max_iter: int = 1000, tol: float = 1e-4):
        self.alpha = alpha
        self.max_iter = max_iter
        self.tol = tol
        self.coef_: Optional[np.ndarray] = None
        self.intercept_: float = 0.0
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> "LassoEstimator":
        n, p = X.shape
        
        # Center
        X_mean = X.mean(axis=0)
        y_mean = y.mean()
        X_centered = X - X_mean
        y_centered = y - y_mean
        
        # Initialize
        beta = np.zeros(p)
        
        for _ in range(self.max_iter):
            beta_old = beta.copy()
            
            for j in range(p):
                # Partial residual
                r_j = y_centered - X_centered @ beta + X_centered[:, j] * beta[j]
                
                # Soft threshold
                rho = X_centered[:, j] @ r_j / n
                z = X_centered[:, j] @ X_centered[:, j] / n
                
                if z > 0:
                    beta[j] = np.sign(rho) * max(0, abs(rho) - self.alpha) / z
                else:
                    beta[j] = 0
            
            if np.linalg.norm(beta - beta_old) < self.tol:
                break
        
        self.coef_ = beta
        self.intercept_ = y_mean - X_mean @ beta
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.coef_ is None:
            raise ValueError("Model not fitted")
        return X @ self.coef_ + self.intercept_


class RidgeEstimator:
    """Simple Ridge regression."""
    
    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha
        self.coef_: Optional[np.ndarray] = None
        self.intercept_: float = 0.0
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> "RidgeEstimator":
        n, p = X.shape
        
        # Add intercept
        X_mean = X.mean(axis=0)
        y_mean = y.mean()
        X_centered = X - X_mean
        y_centered = y - y_mean
        
        # Ridge closed form
        I = np.eye(p)
        self.coef_ = np.linalg.solve(X_centered.T @ X_centered + self.alpha * I, X_centered.T @ y_centered)
        self.intercept_ = y_mean - X_mean @ self.coef_
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.coef_ is None:
            raise ValueError("Model not fitted")
        return X @ self.coef_ + self.intercept_


# ════════════════════════════════════════════════════════════════════════════════
# DML Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class DMLTransition(TransitionFunction):
    """Transition function for DML simulation."""
    
    name = "DMLTransition"
    
    def __init__(self, treatment_effect: float = 0.5):
        self.treatment_effect = treatment_effect
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        params = params or {}
        treatment = params.get("treatment", np.zeros(state.n_cohorts))
        
        # DGP with confounding
        new_opportunity = (
            state.opportunity_score +
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
# DML Framework
# ════════════════════════════════════════════════════════════════════════════════


class DMLFramework(BaseMetaFramework):
    """
    Double Machine Learning Framework.
    
    Production-grade implementation of debiased ML methods:
    
    - Partially Linear Regression (PLR)
    - Interactive Regression Model (IRM)
    - Cross-fitting for honest inference
    - Built-in regularized estimators
    - Heterogeneous effect estimation
    
    Token Weight: 6
    Tier: PROFESSIONAL
    
    Example:
        >>> framework = DMLFramework()
        >>> result = framework.estimate_plr(Y, D, X)
        >>> print(f"ATE: {result.theta:.3f} (SE: {result.se:.3f})")
    
    References:
        - Chernozhukov et al. (2018)
        - Athey & Wager (2019)
    """
    
    METADATA = FrameworkMetadata(
        slug="double-ml",
        name="Double Machine Learning",
        version="1.0.0",
        layer=VerticalLayer.EXPERIMENTAL_RESEARCH,
        tier=Tier.PROFESSIONAL,
        description=(
            "Debiased/Orthogonal machine learning for causal inference "
            "with cross-fitting and honest inference."
        ),
        required_domains=["outcome", "treatment", "covariates"],
        output_domains=["ate", "cate", "nuisance_quality"],
        constituent_models=["plr", "irm", "causal_forest"],
        tags=["double-ml", "causal-inference", "machine-learning", "debiasing"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(
        self,
        n_folds: int = 5,
        ml_method: MLMethod = MLMethod.LASSO,
        confidence_level: float = 0.95,
    ):
        super().__init__()
        self.n_folds = n_folds
        self.ml_method = ml_method
        self.confidence_level = confidence_level
        self._transition_fn = DMLTransition()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        return cls.METADATA
    
    def _get_ml_estimator(self) -> MLEstimator:
        """Get ML estimator based on method."""
        if self.ml_method == MLMethod.LASSO:
            return LassoEstimator(alpha=0.1)
        elif self.ml_method == MLMethod.RIDGE:
            return RidgeEstimator(alpha=1.0)
        else:
            # Default to Ridge
            return RidgeEstimator(alpha=1.0)
    
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
        return {"framework": "double-ml", "n_periods": trajectory.n_periods}

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return Double Machine Learning dashboard specification."""
        return FrameworkDashboardSpec(
            slug="double_ml",
            name="Double Machine Learning",
            description=(
                "Double/Debiased Machine Learning for causal inference "
                "with automatic cross-fitting and honest inference."
            ),
            layer="experimental",
            parameters_schema={
                "type": "object",
                "properties": {
                    "ml_model": {
                        "type": "string",
                        "title": "ML Model",
                        "enum": ["lasso", "ridge", "random_forest", "gradient_boosting"],
                        "default": "lasso",
                        "x-ui-widget": "select",
                        "x-ui-group": "model",
                    },
                    "cross_fit_folds": {
                        "type": "integer",
                        "title": "Cross-Fit Folds",
                        "minimum": 2,
                        "maximum": 10,
                        "default": 5,
                        "x-ui-widget": "slider",
                        "x-ui-group": "estimation",
                    },
                    "regularization": {
                        "type": "number",
                        "title": "Regularization",
                        "minimum": 0.0,
                        "maximum": 10.0,
                        "default": 0.1,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.1,
                        "x-ui-group": "model",
                    },
                    "dml_model": {
                        "type": "string",
                        "title": "DML Model Type",
                        "enum": ["plr", "irm", "pliv", "iivm"],
                        "default": "plr",
                        "x-ui-widget": "select",
                        "x-ui-group": "model",
                    },
                },
            },
            default_parameters={"ml_model": "lasso", "cross_fit_folds": 5, "regularization": 0.1, "dml_model": "plr"},
            parameter_groups=[
                ParameterGroupSpec(key="model", title="Model", parameters=["ml_model", "dml_model", "regularization"]),
                ParameterGroupSpec(key="estimation", title="Estimation", parameters=["cross_fit_folds"]),
            ],
            required_domains=["outcome", "treatment", "covariates"],
            min_tier=Tier.PROFESSIONAL,
            output_views=[
                OutputViewSpec(
                    key="cate_estimates",
                    title="CATE Distribution",
                    view_type=ViewType.HISTOGRAM,
                    config={"x_field": "cate", "bins": 50, "show_mean": True},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="cate_estimates_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="feature_importance",
                    title="Feature Importance",
                    view_type=ViewType.BAR_CHART,
                    config={"x_field": "feature", "y_field": "importance", "sort": "descending"},
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="feature_importance_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="model_diagnostics",
                    title="Model Diagnostics",
                    view_type=ViewType.TABLE,
                    config={"columns": ["metric", "outcome_model", "treatment_model"]},
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="model_diagnostics_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )

    # ════════════════════════════════════════════════════════════════════════════
    # Public API Methods
    # ════════════════════════════════════════════════════════════════════════════
    
    @requires_tier(Tier.PROFESSIONAL)
    def cross_fit(
        self,
        Y: np.ndarray,
        D: np.ndarray,
        X: np.ndarray,
    ) -> CrossFitResult:
        """
        Perform cross-fitting for nuisance estimation.
        
        Args:
            Y: Outcome (n,)
            D: Treatment (n,)
            X: Covariates (n, p)
        
        Returns:
            Cross-fitting results with residualized outcomes
        """
        n = len(Y)
        
        # Create fold indices
        fold_idx = np.zeros(n, dtype=int)
        indices = np.random.permutation(n)
        fold_size = n // self.n_folds
        
        for k in range(self.n_folds):
            start = k * fold_size
            end = start + fold_size if k < self.n_folds - 1 else n
            fold_idx[indices[start:end]] = k
        
        # Initialize predictions
        g_hat = np.zeros(n)  # E[Y|X]
        m_hat = np.zeros(n)  # E[D|X]
        
        for k in range(self.n_folds):
            # Split
            train_mask = fold_idx != k
            test_mask = fold_idx == k
            
            X_train, X_test = X[train_mask], X[test_mask]
            Y_train = Y[train_mask]
            D_train = D[train_mask]
            
            # Fit outcome model
            outcome_model = self._get_ml_estimator()
            outcome_model.fit(X_train, Y_train)
            g_hat[test_mask] = outcome_model.predict(X_test)
            
            # Fit treatment model
            treatment_model = self._get_ml_estimator()
            treatment_model.fit(X_train, D_train)
            m_hat[test_mask] = treatment_model.predict(X_test)
        
        # Residualize
        Y_residual = Y - g_hat
        D_residual = D - m_hat
        
        return CrossFitResult(
            n_folds=self.n_folds,
            Y_residual=Y_residual,
            D_residual=D_residual,
            fold_idx=fold_idx,
            g_hat=g_hat,
            m_hat=m_hat,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def estimate_plr(
        self,
        Y: np.ndarray,
        D: np.ndarray,
        X: np.ndarray,
    ) -> DMLResult:
        """
        Estimate Partially Linear Regression model.
        
        Y = θ·D + g(X) + ε
        D = m(X) + η
        
        Uses cross-fitting and orthogonal score.
        
        Args:
            Y: Outcome (n,)
            D: Treatment (n,)
            X: Covariates (n, p)
        
        Returns:
            DML estimation results
        """
        n = len(Y)
        
        # Cross-fit
        cf = self.cross_fit(Y, D, X)
        
        # Orthogonal estimator: θ = Σ(D̃ · Ỹ) / Σ(D̃²)
        D_tilde = cf.D_residual
        Y_tilde = cf.Y_residual
        
        theta = np.sum(D_tilde * Y_tilde) / np.sum(D_tilde ** 2)
        
        # Residual after treatment effect
        residual = Y_tilde - theta * D_tilde
        
        # Standard error (robust)
        psi = D_tilde * residual
        J = np.mean(D_tilde ** 2)
        
        se = np.sqrt(np.mean(psi ** 2) / (n * J ** 2))
        
        # Inference
        t_stat = theta / se
        p_value = 2 * (1 - stats.norm.cdf(abs(t_stat)))
        
        z = stats.norm.ppf((1 + self.confidence_level) / 2)
        ci_lower = theta - z * se
        ci_upper = theta + z * se
        
        # R-squared for nuisance models
        outcome_r2 = 1 - np.var(Y - cf.g_hat) / np.var(Y) if np.var(Y) > 0 else 0
        treatment_r2 = 1 - np.var(D - cf.m_hat) / np.var(D) if np.var(D) > 0 else 0
        
        # Orthogonality score (should be close to 0)
        orth_score = abs(np.mean(D_tilde * cf.g_hat))
        
        return DMLResult(
            theta=float(theta),
            se=float(se),
            t_stat=float(t_stat),
            p_value=float(p_value),
            ci_lower=float(ci_lower),
            ci_upper=float(ci_upper),
            model_type=DMLModel.PLR,
            n_folds=self.n_folds,
            n_observations=n,
            outcome_r2=float(outcome_r2),
            treatment_r2=float(treatment_r2),
            orthogonality_score=float(orth_score),
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def estimate_irm(
        self,
        Y: np.ndarray,
        D: np.ndarray,
        X: np.ndarray,
    ) -> DMLResult:
        """
        Estimate Interactive Regression Model (IRM).
        
        Y = g(D, X) + ε  with E[ε|D,X] = 0
        
        Args:
            Y: Outcome (n,)
            D: Treatment (binary, n)
            X: Covariates (n, p)
        
        Returns:
            DML estimation results (ATE)
        """
        n = len(Y)
        
        # Create fold indices
        fold_idx = np.zeros(n, dtype=int)
        indices = np.random.permutation(n)
        fold_size = n // self.n_folds
        
        for k in range(self.n_folds):
            start = k * fold_size
            end = start + fold_size if k < self.n_folds - 1 else n
            fold_idx[indices[start:end]] = k
        
        # Initialize
        g1_hat = np.zeros(n)  # E[Y|D=1, X]
        g0_hat = np.zeros(n)  # E[Y|D=0, X]
        m_hat = np.zeros(n)   # P(D=1|X)
        
        for k in range(self.n_folds):
            train_mask = fold_idx != k
            test_mask = fold_idx == k
            
            X_train, X_test = X[train_mask], X[test_mask]
            Y_train, D_train = Y[train_mask], D[train_mask]
            
            # Propensity score
            ps_model = self._get_ml_estimator()
            ps_model.fit(X_train, D_train)
            m_hat[test_mask] = np.clip(ps_model.predict(X_test), 0.01, 0.99)
            
            # Outcome models by treatment status
            treated_mask = D_train > 0.5
            control_mask = D_train <= 0.5
            
            if np.sum(treated_mask) > 5:
                g1_model = self._get_ml_estimator()
                g1_model.fit(X_train[treated_mask], Y_train[treated_mask])
                g1_hat[test_mask] = g1_model.predict(X_test)
            else:
                g1_hat[test_mask] = np.mean(Y_train[treated_mask]) if np.sum(treated_mask) > 0 else 0
            
            if np.sum(control_mask) > 5:
                g0_model = self._get_ml_estimator()
                g0_model.fit(X_train[control_mask], Y_train[control_mask])
                g0_hat[test_mask] = g0_model.predict(X_test)
            else:
                g0_hat[test_mask] = np.mean(Y_train[control_mask]) if np.sum(control_mask) > 0 else 0
        
        # AIPW score
        score = (
            (D / m_hat) * (Y - g1_hat) -
            ((1 - D) / (1 - m_hat)) * (Y - g0_hat) +
            g1_hat - g0_hat
        )
        
        theta = np.mean(score)
        se = np.std(score) / np.sqrt(n)
        
        t_stat = theta / se if se > 0 else 0
        p_value = 2 * (1 - stats.norm.cdf(abs(t_stat)))
        
        z = stats.norm.ppf((1 + self.confidence_level) / 2)
        ci_lower = theta - z * se
        ci_upper = theta + z * se
        
        return DMLResult(
            theta=float(theta),
            se=float(se),
            t_stat=float(t_stat),
            p_value=float(p_value),
            ci_lower=float(ci_lower),
            ci_upper=float(ci_upper),
            model_type=DMLModel.IRM,
            n_folds=self.n_folds,
            n_observations=n,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def estimate_cate(
        self,
        Y: np.ndarray,
        D: np.ndarray,
        X: np.ndarray,
        effect_modifiers: Optional[np.ndarray] = None,
    ) -> CATEResult:
        """
        Estimate Conditional Average Treatment Effects.
        
        Args:
            Y: Outcome
            D: Treatment
            X: Covariates
            effect_modifiers: Variables for heterogeneity (default: X)
        
        Returns:
            CATE results
        """
        n = len(Y)
        Z = effect_modifiers if effect_modifiers is not None else X
        
        # Cross-fit for nuisance
        cf = self.cross_fit(Y, D, X)
        
        # Pseudo-outcome for CATE
        D_tilde = cf.D_residual
        Y_tilde = cf.Y_residual
        
        # Pseudo-outcome: (Ỹ - θ̂·D̃) / D̃ where θ̂ is the PLR estimate
        theta_hat = np.sum(D_tilde * Y_tilde) / np.sum(D_tilde ** 2)
        
        # Simple kernel-based CATE (local linear regression)
        cate = np.zeros(n)
        cate_se = np.zeros(n)
        
        for i in range(n):
            # Weights based on distance
            if Z.ndim == 1:
                dist = np.abs(Z - Z[i])
            else:
                dist = np.sqrt(np.sum((Z - Z[i]) ** 2, axis=1))
            
            bandwidth = np.percentile(dist, 30)
            weights = np.exp(-dist ** 2 / (2 * bandwidth ** 2 + 1e-10))
            weights[i] = 0  # Leave-one-out
            
            # Weighted PLR
            if np.sum(weights) > 0 and np.sum(weights * D_tilde ** 2) > 1e-10:
                cate[i] = np.sum(weights * D_tilde * Y_tilde) / np.sum(weights * D_tilde ** 2)
                
                # SE via weighted residuals
                resid = Y_tilde - cate[i] * D_tilde
                se_num = np.sum(weights ** 2 * resid ** 2)
                se_den = np.sum(weights * D_tilde ** 2) ** 2
                cate_se[i] = np.sqrt(se_num / (se_den + 1e-10))
            else:
                cate[i] = theta_hat
                cate_se[i] = np.std(Y_tilde) / np.sqrt(n)
        
        # ATE as mean of CATE
        ate = float(np.mean(cate))
        ate_se = float(np.std(cate) / np.sqrt(n))
        
        # Heterogeneity
        effect_variance = float(np.var(cate))
        
        # Subgroup effects (by quartiles of first effect modifier)
        heterogeneous_effects = []
        z_first = Z[:, 0] if Z.ndim > 1 else Z
        quartiles = np.percentile(z_first, [25, 50, 75])
        
        subgroups = [
            ("Q1 (lowest)", z_first <= quartiles[0]),
            ("Q2", (z_first > quartiles[0]) & (z_first <= quartiles[1])),
            ("Q3", (z_first > quartiles[1]) & (z_first <= quartiles[2])),
            ("Q4 (highest)", z_first > quartiles[2]),
        ]
        
        for name, mask in subgroups:
            if np.sum(mask) > 10:
                sub_cate = cate[mask]
                heterogeneous_effects.append(HeterogeneousEffect(
                    subgroup_name=name,
                    subgroup_mask=mask,
                    theta=float(np.mean(sub_cate)),
                    se=float(np.std(sub_cate) / np.sqrt(np.sum(mask))),
                    ci_lower=float(np.percentile(sub_cate, 2.5)),
                    ci_upper=float(np.percentile(sub_cate, 97.5)),
                    n_obs=int(np.sum(mask)),
                ))
        
        return CATEResult(
            cate=cate,
            cate_se=cate_se,
            ate=ate,
            ate_se=ate_se,
            effect_variance=effect_variance,
            heterogeneous_effects=heterogeneous_effects,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def analyze_dml(
        self,
        Y: np.ndarray,
        D: np.ndarray,
        X: np.ndarray,
        model: DMLModel = DMLModel.PLR,
        estimate_cate: bool = False,
    ) -> DMLMetrics:
        """
        Comprehensive DML analysis.
        
        Args:
            Y: Outcome
            D: Treatment
            X: Covariates
            model: DML model type
            estimate_cate: Whether to estimate heterogeneous effects
        
        Returns:
            Complete DML metrics
        """
        # Cross-fit
        cf = self.cross_fit(Y, D, X)
        
        # Main estimate
        if model == DMLModel.PLR:
            main_result = self.estimate_plr(Y, D, X)
        else:
            main_result = self.estimate_irm(Y, D, X)
        
        # CATE
        cate_result = self.estimate_cate(Y, D, X) if estimate_cate else None
        
        return DMLMetrics(
            main_result=main_result,
            cross_fit=cf,
            cate_result=cate_result,
            ml_method=self.ml_method,
        )
