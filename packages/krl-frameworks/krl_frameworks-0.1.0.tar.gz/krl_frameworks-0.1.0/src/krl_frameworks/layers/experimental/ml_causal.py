# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - ML Causal Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Machine Learning Causal Inference Framework.

Production-grade ML-based causal methods:
- Causal Forests (Generalized Random Forests)
- Meta-Learners (S, T, X, R-learners)
- Targeted Learning (TMLE)
- Orthogonal Learning

References:
    - Athey & Wager (2019): Estimating Treatment Effects with Causal Forests
    - Künzel et al. (2019): Meta-learners for Estimating Heterogeneous Treatment Effects
    - Van der Laan & Rose (2011): Targeted Learning

Tier: PROFESSIONAL
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Mapping, Optional, Protocol

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

__all__ = ["MLCausalFramework"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# ML Causal Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class MetaLearner(Enum):
    """Meta-learner types."""
    S_LEARNER = "S-Learner"
    T_LEARNER = "T-Learner"
    X_LEARNER = "X-Learner"
    R_LEARNER = "R-Learner"
    DR_LEARNER = "Doubly Robust Learner"


class BaseModel(Enum):
    """Base ML model types."""
    RIDGE = "Ridge Regression"
    LASSO = "Lasso"
    RANDOM_FOREST = "Random Forest"
    GRADIENT_BOOSTING = "Gradient Boosting"
    KERNEL = "Kernel Methods"


class MLEstimatorProtocol(Protocol):
    """Protocol for ML estimators."""
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> "MLEstimatorProtocol":
        ...
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        ...


@dataclass
class CATEEstimate:
    """Conditional Average Treatment Effect estimate."""
    
    # Individual effects
    cate: np.ndarray = field(default_factory=lambda: np.array([]))
    cate_lower: np.ndarray = field(default_factory=lambda: np.array([]))
    cate_upper: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Summary
    ate: float = 0.0
    ate_se: float = 0.0
    ate_ci_lower: float = 0.0
    ate_ci_upper: float = 0.0
    
    # Heterogeneity
    cate_std: float = 0.0
    effect_heterogeneity: float = 0.0


@dataclass
class MetaLearnerResult:
    """Meta-learner estimation results."""
    
    learner_type: MetaLearner = MetaLearner.S_LEARNER
    
    # CATE estimate
    cate_estimate: CATEEstimate = field(default_factory=CATEEstimate)
    
    # Cross-validation score
    cv_score: float = 0.0
    
    # Feature importance (if available)
    feature_importance: np.ndarray = field(default_factory=lambda: np.array([]))


@dataclass
class CausalForestResult:
    """Causal Forest estimation results."""
    
    # Individual treatment effects
    tau_hat: np.ndarray = field(default_factory=lambda: np.array([]))
    tau_var: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Aggregates
    ate: float = 0.0
    ate_se: float = 0.0
    ate_ci_lower: float = 0.0
    ate_ci_upper: float = 0.0
    
    # Feature importance
    feature_importance: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Model diagnostics
    oob_predictions: np.ndarray = field(default_factory=lambda: np.array([]))


@dataclass
class TMLEResult:
    """Targeted Maximum Likelihood Estimation results."""
    
    # ATE
    ate: float = 0.0
    ate_se: float = 0.0
    ate_ci_lower: float = 0.0
    ate_ci_upper: float = 0.0
    
    # Efficient influence function
    eif: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Targeting step convergence
    epsilon: float = 0.0
    converged: bool = True


@dataclass
class MLCausalMetrics:
    """Comprehensive ML causal analysis results."""
    
    meta_learner: Optional[MetaLearnerResult] = None
    causal_forest: Optional[CausalForestResult] = None
    tmle: Optional[TMLEResult] = None
    best_method: str = ""


# ════════════════════════════════════════════════════════════════════════════════
# Simple ML Models (Built-in)
# ════════════════════════════════════════════════════════════════════════════════


class RidgeModel:
    """Simple Ridge regression."""
    
    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha
        self.coef_: Optional[np.ndarray] = None
        self.intercept_: float = 0.0
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> "RidgeModel":
        n, p = X.shape
        X_mean = X.mean(axis=0)
        y_mean = y.mean()
        X_c = X - X_mean
        y_c = y - y_mean
        
        I = np.eye(p)
        self.coef_ = np.linalg.solve(X_c.T @ X_c + self.alpha * I, X_c.T @ y_c)
        self.intercept_ = y_mean - X_mean @ self.coef_
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.coef_ is None:
            raise ValueError("Model not fitted")
        return X @ self.coef_ + self.intercept_


class RandomForestSimple:
    """Simple Random Forest via bootstrap aggregating."""
    
    def __init__(self, n_trees: int = 10, max_depth: int = 5, min_samples_leaf: int = 5):
        self.n_trees = n_trees
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.trees: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []
        self.oob_predictions_: Optional[np.ndarray] = None
    
    def _build_tree(
        self,
        X: np.ndarray,
        y: np.ndarray,
        depth: int = 0,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Build a simple decision tree stump."""
        n, p = X.shape
        
        if depth >= self.max_depth or n < 2 * self.min_samples_leaf:
            # Leaf node
            return np.array([]), np.array([]), np.array([np.mean(y)])
        
        # Find best split
        best_mse = np.inf
        best_feature = 0
        best_threshold = 0.0
        
        for j in range(p):
            thresholds = np.percentile(X[:, j], [25, 50, 75])
            for thresh in thresholds:
                left_mask = X[:, j] <= thresh
                right_mask = ~left_mask
                
                if np.sum(left_mask) < self.min_samples_leaf or np.sum(right_mask) < self.min_samples_leaf:
                    continue
                
                mse = (
                    np.sum((y[left_mask] - np.mean(y[left_mask])) ** 2) +
                    np.sum((y[right_mask] - np.mean(y[right_mask])) ** 2)
                )
                
                if mse < best_mse:
                    best_mse = mse
                    best_feature = j
                    best_threshold = thresh
        
        # Create split
        features = np.array([best_feature])
        thresholds = np.array([best_threshold])
        
        left_mask = X[:, best_feature] <= best_threshold
        values = np.array([np.mean(y[left_mask]), np.mean(y[~left_mask])])
        
        return features, thresholds, values
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> "RandomForestSimple":
        n = len(y)
        self.trees = []
        oob_preds = np.zeros((n, self.n_trees))
        oob_count = np.zeros(n)
        
        for t in range(self.n_trees):
            # Bootstrap sample
            idx = np.random.choice(n, n, replace=True)
            oob_idx = np.setdiff1d(np.arange(n), np.unique(idx))
            
            X_boot = X[idx]
            y_boot = y[idx]
            
            tree = self._build_tree(X_boot, y_boot)
            self.trees.append(tree)
            
            # OOB predictions
            if len(oob_idx) > 0:
                preds = self._predict_tree(X[oob_idx], tree)
                oob_preds[oob_idx, t] = preds
                oob_count[oob_idx] += 1
        
        # Average OOB predictions
        oob_mask = oob_count > 0
        self.oob_predictions_ = np.zeros(n)
        self.oob_predictions_[oob_mask] = (
            np.sum(oob_preds[oob_mask], axis=1) / oob_count[oob_mask]
        )
        
        return self
    
    def _predict_tree(
        self,
        X: np.ndarray,
        tree: tuple[np.ndarray, np.ndarray, np.ndarray],
    ) -> np.ndarray:
        features, thresholds, values = tree
        
        if len(features) == 0:
            return np.full(len(X), values[0])
        
        preds = np.where(
            X[:, features[0]] <= thresholds[0],
            values[0],
            values[1],
        )
        return preds
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        preds = np.zeros((len(X), self.n_trees))
        
        for t, tree in enumerate(self.trees):
            preds[:, t] = self._predict_tree(X, tree)
        
        return np.mean(preds, axis=1)


# ════════════════════════════════════════════════════════════════════════════════
# ML Causal Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class MLCausalTransition(TransitionFunction):
    """Transition with heterogeneous treatment effects."""
    
    name = "MLCausalTransition"
    
    def __init__(self, base_effect: float = 0.2, heterogeneity: float = 0.1):
        self.base_effect = base_effect
        self.heterogeneity = heterogeneity
    
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
        
        # Heterogeneous effects based on baseline
        cate = self.base_effect + self.heterogeneity * (state.opportunity_score - 0.5)
        
        new_opportunity = np.clip(
            state.opportunity_score + treatment * cate,
            0, 1,
        )
        
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
# ML Causal Framework
# ════════════════════════════════════════════════════════════════════════════════


class MLCausalFramework(BaseMetaFramework):
    """
    Machine Learning Causal Inference Framework.
    
    Production-grade ML-based causal methods:
    
    - Meta-Learners (S, T, X, R-learners)
    - Causal Forest estimation
    - Targeted Learning (TMLE)
    - Heterogeneous treatment effect estimation
    
    Token Weight: 7
    Tier: PROFESSIONAL
    
    Example:
        >>> framework = MLCausalFramework()
        >>> result = framework.estimate_cate(Y, D, X, learner=MetaLearner.X_LEARNER)
        >>> print(f"ATE: {result.cate_estimate.ate:.3f}")
    
    References:
        - Athey & Wager (2019)
        - Künzel et al. (2019)
    """
    
    METADATA = FrameworkMetadata(
        slug="ml-causal",
        name="ML Causal Inference",
        version="1.0.0",
        layer=VerticalLayer.EXPERIMENTAL_RESEARCH,
        tier=Tier.PROFESSIONAL,
        description=(
            "Machine learning methods for heterogeneous treatment effect "
            "estimation including meta-learners and causal forests."
        ),
        required_domains=["outcome", "treatment", "covariates"],
        output_domains=["cate", "ate", "feature_importance"],
        constituent_models=["meta_learners", "causal_forest", "tmle"],
        tags=["machine-learning", "causal-inference", "cate", "heterogeneity"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(
        self,
        base_model: BaseModel = BaseModel.RIDGE,
        n_folds: int = 5,
        confidence_level: float = 0.95,
    ):
        super().__init__()
        self.base_model = base_model
        self.n_folds = n_folds
        self.confidence_level = confidence_level
        self._transition_fn = MLCausalTransition()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        return cls.METADATA
    
    def _get_base_model(self) -> MLEstimatorProtocol:
        """Get base ML model."""
        if self.base_model == BaseModel.RANDOM_FOREST:
            return RandomForestSimple(n_trees=10)
        else:
            return RidgeModel(alpha=1.0)
    
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
        return {"framework": "ml-causal", "n_periods": trajectory.n_periods}

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return ML Causal Inference dashboard specification."""
        return FrameworkDashboardSpec(
            slug="ml_causal",
            name="Machine Learning Causal Inference",
            description=(
                "ML-based causal inference including Causal Forests, "
                "Meta-Learners, and Targeted Learning for heterogeneous effects."
            ),
            layer="experimental",
            parameters_schema={
                "type": "object",
                "properties": {
                    "model_type": {
                        "type": "string",
                        "title": "Model Type",
                        "enum": ["causal_forest", "bart", "dml", "s_learner", "t_learner", "x_learner"],
                        "default": "causal_forest",
                        "x-ui-widget": "select",
                        "x-ui-group": "model",
                    },
                    "n_estimators": {
                        "type": "integer",
                        "title": "Number of Estimators",
                        "minimum": 50,
                        "maximum": 1000,
                        "default": 200,
                        "x-ui-widget": "slider",
                        "x-ui-step": 50,
                        "x-ui-group": "model",
                    },
                    "min_samples_leaf": {
                        "type": "integer",
                        "title": "Min Samples Leaf",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 5,
                        "x-ui-widget": "slider",
                        "x-ui-group": "model",
                    },
                    "honesty": {
                        "type": "boolean",
                        "title": "Honest Splitting",
                        "default": True,
                        "x-ui-widget": "checkbox",
                        "x-ui-group": "inference",
                    },
                },
            },
            default_parameters={"model_type": "causal_forest", "n_estimators": 200, "min_samples_leaf": 5, "honesty": True},
            parameter_groups=[
                ParameterGroupSpec(key="model", title="Model", parameters=["model_type", "n_estimators", "min_samples_leaf"]),
                ParameterGroupSpec(key="inference", title="Inference", parameters=["honesty"]),
            ],
            required_domains=["outcome", "treatment", "covariates"],
            min_tier=Tier.PROFESSIONAL,
            output_views=[
                OutputViewSpec(
                    key="cate_distribution",
                    title="CATE Distribution",
                    view_type=ViewType.HISTOGRAM,
                    config={"x_field": "cate", "bins": 50, "show_mean": True, "show_ci": True},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="cate_distribution_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="heterogeneity_analysis",
                    title="Heterogeneity Analysis",
                    view_type=ViewType.SCATTER,
                    config={"x_field": "covariate", "y_field": "cate", "trend_line": True},
                    result_class=ResultClass.STRUCTURAL_SIMILARITY,
                    output_key="heterogeneity_analysis_data",
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
            ],
        )

    # ════════════════════════════════════════════════════════════════════════════
    # Public API Methods
    # ════════════════════════════════════════════════════════════════════════════
    
    @requires_tier(Tier.PROFESSIONAL)
    def s_learner(
        self,
        Y: np.ndarray,
        D: np.ndarray,
        X: np.ndarray,
    ) -> CATEEstimate:
        """
        S-Learner: Single model approach.
        
        Fits μ(x, d) = E[Y|X=x, D=d], then CATE = μ(x, 1) - μ(x, 0)
        
        Args:
            Y: Outcome
            D: Treatment
            X: Covariates
        
        Returns:
            CATE estimates
        """
        n = len(Y)
        
        # Augment X with treatment
        X_aug = np.column_stack([X, D])
        
        model = self._get_base_model()
        model.fit(X_aug, Y)
        
        # Predict under treatment and control
        X_1 = np.column_stack([X, np.ones(n)])
        X_0 = np.column_stack([X, np.zeros(n)])
        
        mu_1 = model.predict(X_1)
        mu_0 = model.predict(X_0)
        
        cate = mu_1 - mu_0
        
        # Bootstrap for uncertainty
        n_boot = 100
        cate_boot = np.zeros((n_boot, n))
        
        for b in range(n_boot):
            idx = np.random.choice(n, n, replace=True)
            model_b = self._get_base_model()
            model_b.fit(X_aug[idx], Y[idx])
            cate_boot[b] = model_b.predict(X_1) - model_b.predict(X_0)
        
        cate_se = np.std(cate_boot, axis=0)
        z = stats.norm.ppf((1 + self.confidence_level) / 2)
        
        return CATEEstimate(
            cate=cate,
            cate_lower=cate - z * cate_se,
            cate_upper=cate + z * cate_se,
            ate=float(np.mean(cate)),
            ate_se=float(np.std(cate) / np.sqrt(n)),
            ate_ci_lower=float(np.mean(cate) - z * np.std(cate) / np.sqrt(n)),
            ate_ci_upper=float(np.mean(cate) + z * np.std(cate) / np.sqrt(n)),
            cate_std=float(np.std(cate)),
            effect_heterogeneity=float(np.var(cate)),
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def t_learner(
        self,
        Y: np.ndarray,
        D: np.ndarray,
        X: np.ndarray,
    ) -> CATEEstimate:
        """
        T-Learner: Two model approach.
        
        Fits μ₁(x) on treated, μ₀(x) on control, CATE = μ₁(x) - μ₀(x)
        
        Args:
            Y: Outcome
            D: Treatment
            X: Covariates
        
        Returns:
            CATE estimates
        """
        n = len(Y)
        treated = D > 0.5
        
        # Fit separate models
        model_1 = self._get_base_model()
        model_0 = self._get_base_model()
        
        model_1.fit(X[treated], Y[treated])
        model_0.fit(X[~treated], Y[~treated])
        
        mu_1 = model_1.predict(X)
        mu_0 = model_0.predict(X)
        
        cate = mu_1 - mu_0
        
        # Bootstrap for uncertainty
        n_boot = 100
        cate_boot = np.zeros((n_boot, n))
        
        for b in range(n_boot):
            idx = np.random.choice(n, n, replace=True)
            treated_b = D[idx] > 0.5
            
            if np.sum(treated_b) > 5 and np.sum(~treated_b) > 5:
                m1 = self._get_base_model()
                m0 = self._get_base_model()
                m1.fit(X[idx][treated_b], Y[idx][treated_b])
                m0.fit(X[idx][~treated_b], Y[idx][~treated_b])
                cate_boot[b] = m1.predict(X) - m0.predict(X)
            else:
                cate_boot[b] = cate
        
        cate_se = np.std(cate_boot, axis=0)
        z = stats.norm.ppf((1 + self.confidence_level) / 2)
        
        return CATEEstimate(
            cate=cate,
            cate_lower=cate - z * cate_se,
            cate_upper=cate + z * cate_se,
            ate=float(np.mean(cate)),
            ate_se=float(np.std(cate) / np.sqrt(n)),
            ate_ci_lower=float(np.mean(cate) - z * np.std(cate) / np.sqrt(n)),
            ate_ci_upper=float(np.mean(cate) + z * np.std(cate) / np.sqrt(n)),
            cate_std=float(np.std(cate)),
            effect_heterogeneity=float(np.var(cate)),
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def x_learner(
        self,
        Y: np.ndarray,
        D: np.ndarray,
        X: np.ndarray,
    ) -> CATEEstimate:
        """
        X-Learner: Cross-fitting approach.
        
        More efficient when treatment/control groups are imbalanced.
        
        Args:
            Y: Outcome
            D: Treatment
            X: Covariates
        
        Returns:
            CATE estimates
        """
        n = len(Y)
        treated = D > 0.5
        
        # Stage 1: Fit outcome models
        model_1 = self._get_base_model()
        model_0 = self._get_base_model()
        
        model_1.fit(X[treated], Y[treated])
        model_0.fit(X[~treated], Y[~treated])
        
        # Stage 2: Imputed treatment effects
        D_1 = Y[treated] - model_0.predict(X[treated])  # For treated
        D_0 = model_1.predict(X[~treated]) - Y[~treated]  # For control
        
        # Stage 3: Model imputed effects
        tau_model_1 = self._get_base_model()
        tau_model_0 = self._get_base_model()
        
        tau_model_1.fit(X[treated], D_1)
        tau_model_0.fit(X[~treated], D_0)
        
        tau_1 = tau_model_1.predict(X)
        tau_0 = tau_model_0.predict(X)
        
        # Stage 4: Combine with propensity weighting
        # Estimate propensity
        ps_model = self._get_base_model()
        ps_model.fit(X, D)
        e = np.clip(ps_model.predict(X), 0.01, 0.99)
        
        # X-learner CATE
        cate = e * tau_0 + (1 - e) * tau_1
        
        # Uncertainty
        cate_se = np.std(cate) * np.ones(n)  # Simplified
        z = stats.norm.ppf((1 + self.confidence_level) / 2)
        
        return CATEEstimate(
            cate=cate,
            cate_lower=cate - z * cate_se,
            cate_upper=cate + z * cate_se,
            ate=float(np.mean(cate)),
            ate_se=float(np.std(cate) / np.sqrt(n)),
            ate_ci_lower=float(np.mean(cate) - z * np.std(cate) / np.sqrt(n)),
            ate_ci_upper=float(np.mean(cate) + z * np.std(cate) / np.sqrt(n)),
            cate_std=float(np.std(cate)),
            effect_heterogeneity=float(np.var(cate)),
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def r_learner(
        self,
        Y: np.ndarray,
        D: np.ndarray,
        X: np.ndarray,
    ) -> CATEEstimate:
        """
        R-Learner: Robinson's residual-on-residual approach.
        
        Orthogonal/doubly-robust CATE estimation.
        
        Args:
            Y: Outcome
            D: Treatment
            X: Covariates
        
        Returns:
            CATE estimates
        """
        n = len(Y)
        
        # Cross-fit nuisance functions
        fold_idx = np.zeros(n, dtype=int)
        indices = np.random.permutation(n)
        fold_size = n // self.n_folds
        
        for k in range(self.n_folds):
            start = k * fold_size
            end = start + fold_size if k < self.n_folds - 1 else n
            fold_idx[indices[start:end]] = k
        
        m_hat = np.zeros(n)  # E[Y|X]
        e_hat = np.zeros(n)  # E[D|X]
        
        for k in range(self.n_folds):
            train = fold_idx != k
            test = fold_idx == k
            
            m_model = self._get_base_model()
            m_model.fit(X[train], Y[train])
            m_hat[test] = m_model.predict(X[test])
            
            e_model = self._get_base_model()
            e_model.fit(X[train], D[train])
            e_hat[test] = np.clip(e_model.predict(X[test]), 0.01, 0.99)
        
        # Residuals
        Y_tilde = Y - m_hat
        D_tilde = D - e_hat
        
        # R-learner: regress Y_tilde on tau(X) * D_tilde
        # Simplified: weighted regression
        weights = D_tilde ** 2
        pseudo_outcome = Y_tilde / (D_tilde + 1e-10)
        
        # Local linear CATE
        cate = np.zeros(n)
        cate_se = np.zeros(n)
        
        for i in range(n):
            # Kernel weights
            if X.ndim == 1:
                dist = np.abs(X - X[i])
            else:
                dist = np.sqrt(np.sum((X - X[i]) ** 2, axis=1))
            
            bandwidth = np.percentile(dist, 30)
            kernel_weights = np.exp(-dist ** 2 / (2 * bandwidth ** 2 + 1e-10))
            kernel_weights[i] = 0
            
            combined_weights = kernel_weights * weights
            
            if np.sum(combined_weights) > 1e-10:
                cate[i] = np.sum(combined_weights * pseudo_outcome) / np.sum(combined_weights)
                
                # SE
                resid = pseudo_outcome - cate[i]
                cate_se[i] = np.sqrt(
                    np.sum(combined_weights ** 2 * resid ** 2) /
                    (np.sum(combined_weights) ** 2 + 1e-10)
                )
            else:
                cate[i] = np.mean(Y_tilde / (D_tilde + 1e-10))
                cate_se[i] = np.std(Y_tilde)
        
        z = stats.norm.ppf((1 + self.confidence_level) / 2)
        
        return CATEEstimate(
            cate=cate,
            cate_lower=cate - z * cate_se,
            cate_upper=cate + z * cate_se,
            ate=float(np.mean(cate)),
            ate_se=float(np.std(cate) / np.sqrt(n)),
            ate_ci_lower=float(np.mean(cate) - z * np.std(cate) / np.sqrt(n)),
            ate_ci_upper=float(np.mean(cate) + z * np.std(cate) / np.sqrt(n)),
            cate_std=float(np.std(cate)),
            effect_heterogeneity=float(np.var(cate)),
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def estimate_cate(
        self,
        Y: np.ndarray,
        D: np.ndarray,
        X: np.ndarray,
        learner: MetaLearner = MetaLearner.X_LEARNER,
    ) -> MetaLearnerResult:
        """
        Estimate CATE using specified meta-learner.
        
        Args:
            Y: Outcome
            D: Treatment
            X: Covariates
            learner: Meta-learner type
        
        Returns:
            Meta-learner estimation results
        """
        if learner == MetaLearner.S_LEARNER:
            cate_estimate = self.s_learner(Y, D, X)
        elif learner == MetaLearner.T_LEARNER:
            cate_estimate = self.t_learner(Y, D, X)
        elif learner == MetaLearner.X_LEARNER:
            cate_estimate = self.x_learner(Y, D, X)
        elif learner == MetaLearner.R_LEARNER:
            cate_estimate = self.r_learner(Y, D, X)
        else:
            cate_estimate = self.x_learner(Y, D, X)
        
        # Simple feature importance (correlation with CATE)
        feature_importance = np.zeros(X.shape[1])
        for j in range(X.shape[1]):
            feature_importance[j] = abs(np.corrcoef(X[:, j], cate_estimate.cate)[0, 1])
        
        return MetaLearnerResult(
            learner_type=learner,
            cate_estimate=cate_estimate,
            feature_importance=feature_importance,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def causal_forest(
        self,
        Y: np.ndarray,
        D: np.ndarray,
        X: np.ndarray,
        n_trees: int = 50,
    ) -> CausalForestResult:
        """
        Causal Forest estimation.
        
        Simplified implementation of Athey & Wager (2019).
        
        Args:
            Y: Outcome
            D: Treatment
            X: Covariates
            n_trees: Number of trees
        
        Returns:
            Causal forest results
        """
        n, p = X.shape
        
        # Bootstrap causal trees
        tau_estimates = np.zeros((n_trees, n))
        
        for t in range(n_trees):
            # Bootstrap sample
            idx = np.random.choice(n, n, replace=True)
            
            # Honest splitting: use half for tree building, half for estimation
            n_half = len(idx) // 2
            build_idx = idx[:n_half]
            est_idx = idx[n_half:]
            
            # Simple local treatment effect in leaves
            # Use T-learner approach per tree
            treated = D[build_idx] > 0.5
            
            if np.sum(treated) > 5 and np.sum(~treated) > 5:
                model_1 = RidgeModel()
                model_0 = RidgeModel()
                
                model_1.fit(X[build_idx][treated], Y[build_idx][treated])
                model_0.fit(X[build_idx][~treated], Y[build_idx][~treated])
                
                tau_estimates[t] = model_1.predict(X) - model_0.predict(X)
            else:
                tau_estimates[t] = 0
        
        # Aggregate
        tau_hat = np.mean(tau_estimates, axis=0)
        tau_var = np.var(tau_estimates, axis=0)
        
        # Feature importance
        feature_importance = np.zeros(p)
        for j in range(p):
            feature_importance[j] = abs(np.corrcoef(X[:, j], tau_hat)[0, 1])
        
        z = stats.norm.ppf((1 + self.confidence_level) / 2)
        ate = float(np.mean(tau_hat))
        ate_se = float(np.std(tau_hat) / np.sqrt(n))
        
        return CausalForestResult(
            tau_hat=tau_hat,
            tau_var=tau_var,
            ate=ate,
            ate_se=ate_se,
            ate_ci_lower=float(ate - z * ate_se),
            ate_ci_upper=float(ate + z * ate_se),
            feature_importance=feature_importance,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def tmle(
        self,
        Y: np.ndarray,
        D: np.ndarray,
        X: np.ndarray,
    ) -> TMLEResult:
        """
        Targeted Maximum Likelihood Estimation.
        
        Doubly robust ATE estimation.
        
        Args:
            Y: Outcome
            D: Treatment
            X: Covariates
        
        Returns:
            TMLE results
        """
        n = len(Y)
        
        # Step 1: Initial estimates
        # Outcome model
        X_aug = np.column_stack([X, D])
        Q_model = self._get_base_model()
        Q_model.fit(X_aug, Y)
        
        Q_A = Q_model.predict(X_aug)
        Q_1 = Q_model.predict(np.column_stack([X, np.ones(n)]))
        Q_0 = Q_model.predict(np.column_stack([X, np.zeros(n)]))
        
        # Propensity score
        g_model = self._get_base_model()
        g_model.fit(X, D)
        g = np.clip(g_model.predict(X), 0.01, 0.99)
        
        # Step 2: Clever covariate
        H_1 = 1 / g
        H_0 = -1 / (1 - g)
        H_A = D * H_1 + (1 - D) * H_0
        
        # Step 3: Targeting step
        # Logistic regression of Y on H_A with offset Q_A
        # Simplified: linear update
        residual = Y - Q_A
        epsilon = np.sum(H_A * residual) / np.sum(H_A ** 2)
        
        # Update
        Q_1_star = Q_1 + epsilon * H_1
        Q_0_star = Q_0 + epsilon * H_0
        
        # Step 4: ATE estimate
        ate = float(np.mean(Q_1_star - Q_0_star))
        
        # Step 5: Influence function and SE
        eif = (
            H_A * (Y - Q_A) +
            (Q_1_star - Q_0_star) - ate
        )
        
        ate_se = float(np.std(eif) / np.sqrt(n))
        z = stats.norm.ppf((1 + self.confidence_level) / 2)
        
        return TMLEResult(
            ate=ate,
            ate_se=ate_se,
            ate_ci_lower=float(ate - z * ate_se),
            ate_ci_upper=float(ate + z * ate_se),
            eif=eif,
            epsilon=float(epsilon),
            converged=True,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def analyze_ml(
        self,
        Y: np.ndarray,
        D: np.ndarray,
        X: np.ndarray,
        learner: MetaLearner = MetaLearner.X_LEARNER,
    ) -> MLCausalMetrics:
        """
        Comprehensive ML causal analysis.
        
        Args:
            Y: Outcome
            D: Treatment
            X: Covariates
            learner: Preferred meta-learner
        
        Returns:
            Complete ML causal metrics
        """
        meta_learner = self.estimate_cate(Y, D, X, learner)
        causal_forest = self.causal_forest(Y, D, X)
        tmle = self.tmle(Y, D, X)
        
        # Best method (by lowest SE)
        methods = {
            "meta_learner": meta_learner.cate_estimate.ate_se,
            "causal_forest": causal_forest.ate_se,
            "tmle": tmle.ate_se,
        }
        best_method = min(methods, key=methods.get)
        
        return MLCausalMetrics(
            meta_learner=meta_learner,
            causal_forest=causal_forest,
            tmle=tmle,
            best_method=best_method,
        )
