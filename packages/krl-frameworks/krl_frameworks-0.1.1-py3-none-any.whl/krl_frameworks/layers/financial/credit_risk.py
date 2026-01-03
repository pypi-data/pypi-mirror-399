# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Credit Risk Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Credit Risk Assessment Framework.

Production-grade credit risk modeling with:
- Probability of Default (PD) models
- Loss Given Default (LGD) estimation
- Exposure at Default (EAD) calculation
- Expected Loss (EL) computation
- Credit scoring models
- Portfolio credit risk (Vasicek, CreditMetrics)
- Transition matrices

References:
    - Basel II/III IRB Approach
    - Vasicek (2002). "The Distribution of Loan Portfolio Value"
    - Merton (1974). "On the Pricing of Corporate Debt"
    - CreditMetrics Technical Document, JPMorgan

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
from krl_frameworks.core.data_bundle import DataBundle
from krl_frameworks.core.state import CohortStateVector, StateTrajectory
from krl_frameworks.core.tier import Tier, requires_tier
from krl_frameworks.core.dashboard_spec import (
    FrameworkDashboardSpec,
    OutputViewSpec,
    ParameterGroupSpec,
    ViewType,
    ResultClass,
    TemporalSemantics,
)
from krl_frameworks.simulation.cbss import TransitionFunction

if TYPE_CHECKING:
    from krl_frameworks.core.config import FrameworkConfig

__all__ = ["CreditRiskFramework"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Credit Risk Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class RatingGrade(Enum):
    """Credit rating grades."""
    AAA = "AAA"
    AA = "AA"
    A = "A"
    BBB = "BBB"
    BB = "BB"
    B = "B"
    CCC = "CCC"
    CC = "CC"
    C = "C"
    D = "D"  # Default


class PDModel(Enum):
    """PD estimation models."""
    LOGISTIC = "Logistic Regression"
    MERTON = "Merton Structural"
    HISTORICAL = "Historical Default Rate"
    SCORE_BASED = "Score-Based"


@dataclass
class CreditExposure:
    """Individual credit exposure."""
    
    id: str = ""
    borrower_id: str = ""
    outstanding_balance: float = 0.0
    commitment_amount: float = 0.0
    credit_conversion_factor: float = 1.0
    collateral_value: float = 0.0
    rating: RatingGrade = RatingGrade.BBB
    industry: str = ""
    maturity_years: float = 1.0
    
    @property
    def ead(self) -> float:
        """Exposure at Default."""
        drawn = self.outstanding_balance
        undrawn = max(0, self.commitment_amount - self.outstanding_balance)
        return drawn + self.credit_conversion_factor * undrawn


@dataclass
class PDResult:
    """Probability of Default estimation result."""
    
    exposure_id: str = ""
    pd: float = 0.0  # 0-1
    pd_through_the_cycle: float = 0.0  # TTC PD
    pd_point_in_time: float = 0.0  # PIT PD
    confidence_interval: tuple[float, float] = (0.0, 0.0)
    model_used: PDModel = PDModel.LOGISTIC


@dataclass
class LGDResult:
    """Loss Given Default estimation result."""
    
    exposure_id: str = ""
    lgd: float = 0.45  # 0-1
    lgd_downturn: float = 0.0  # Downturn LGD
    recovery_rate: float = 0.55
    collateral_haircut: float = 0.0
    cure_rate: float = 0.0


@dataclass
class ELResult:
    """Expected Loss computation result."""
    
    exposure_id: str = ""
    pd: float = 0.0
    lgd: float = 0.0
    ead: float = 0.0
    expected_loss: float = 0.0  # EL = PD * LGD * EAD
    unexpected_loss: float = 0.0  # UL for capital
    risk_weight: float = 0.0  # Basel risk weight


@dataclass
class CreditScorecard:
    """Credit scoring model result."""
    
    score: float = 0.0  # 300-850 typical
    score_percentile: float = 0.0
    rating_grade: RatingGrade = RatingGrade.BBB
    component_scores: dict[str, float] = field(default_factory=dict)
    score_factors: list[str] = field(default_factory=list)


@dataclass
class TransitionMatrix:
    """Credit rating transition matrix."""
    
    matrix: np.ndarray = field(default_factory=lambda: np.eye(10))
    rating_labels: list[str] = field(default_factory=list)
    horizon_years: float = 1.0
    
    def get_probability(self, from_rating: str, to_rating: str) -> float:
        """Get transition probability."""
        if from_rating not in self.rating_labels or to_rating not in self.rating_labels:
            return 0.0
        i = self.rating_labels.index(from_rating)
        j = self.rating_labels.index(to_rating)
        return float(self.matrix[i, j])


@dataclass
class PortfolioCreditRisk:
    """Portfolio-level credit risk metrics."""
    
    total_ead: float = 0.0
    total_expected_loss: float = 0.0
    total_unexpected_loss: float = 0.0
    
    # Concentration
    herfindahl_index: float = 0.0
    top_10_concentration: float = 0.0
    
    # Distribution
    loss_var_95: float = 0.0
    loss_var_99: float = 0.0
    loss_es_99: float = 0.0
    
    # Capital
    economic_capital: float = 0.0
    regulatory_capital: float = 0.0


@dataclass
class CreditRiskMetrics:
    """Comprehensive credit risk assessment."""
    
    # Exposure-level
    pd_results: list[PDResult] = field(default_factory=list)
    lgd_results: list[LGDResult] = field(default_factory=list)
    el_results: list[ELResult] = field(default_factory=list)
    
    # Portfolio-level
    portfolio_risk: PortfolioCreditRisk = field(default_factory=PortfolioCreditRisk)
    
    # Transition
    transition_matrix: TransitionMatrix = field(default_factory=TransitionMatrix)
    
    # Vintage analysis
    vintage_default_rates: dict[str, float] = field(default_factory=dict)


# ════════════════════════════════════════════════════════════════════════════════
# Credit Risk Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class CreditRiskTransition(TransitionFunction):
    """
    Transition function for credit risk dynamics.
    
    Models credit quality migration and default events.
    """
    
    name = "CreditRiskTransition"
    
    def __init__(
        self,
        default_rate: float = 0.02,
        recovery_rate: float = 0.40,
        correlation: float = 0.15,
    ):
        self.default_rate = default_rate
        self.recovery_rate = recovery_rate
        self.correlation = correlation
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply credit risk dynamics."""
        params = params or {}
        
        n_cohorts = state.n_cohorts
        
        # Systematic factor (economy-wide)
        z = params.get("systematic_factor", np.random.normal(0, 1))
        
        # Idiosyncratic factors
        epsilon = np.random.normal(0, 1, n_cohorts)
        
        # Correlated asset returns
        rho = self.correlation
        asset_returns = np.sqrt(rho) * z + np.sqrt(1 - rho) * epsilon
        
        # Default threshold from PD
        default_threshold = stats.norm.ppf(self.default_rate)
        
        # Default indicator
        defaults = asset_returns < default_threshold
        
        # Update credit access (defaulted lose access)
        new_credit = state.credit_access_prob.copy()
        new_credit[defaults] *= (1 - 0.8)  # Major credit hit
        new_credit[~defaults] *= 0.99  # Slight improvement
        new_credit = np.clip(new_credit, 0.0, 1.0)
        
        return CohortStateVector(
            employment_prob=state.employment_prob,
            health_burden_score=state.health_burden_score,
            credit_access_prob=new_credit,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=state.opportunity_score,
            sector_output=state.sector_output,
            deprivation_vector=state.deprivation_vector,
        )


# ════════════════════════════════════════════════════════════════════════════════
# Credit Risk Framework
# ════════════════════════════════════════════════════════════════════════════════


class CreditRiskFramework(BaseMetaFramework):
    """
    Credit Risk Assessment Framework.
    
    Production-grade implementation of credit risk modeling:
    
    - PD estimation (logistic, Merton, historical)
    - LGD modeling with collateral
    - EAD calculation
    - Expected/Unexpected loss
    - Portfolio risk (Vasicek model)
    - Credit scoring
    - Transition matrices
    
    Token Weight: 5
    Tier: PROFESSIONAL
    
    Example:
        >>> framework = CreditRiskFramework()
        >>> pd_result = framework.estimate_pd(
        ...     exposure=loan,
        ...     features=borrower_features
        ... )
        >>> el = framework.compute_expected_loss(exposure, pd_result, lgd_result)
    
    References:
        - Basel II/III IRB Approach
        - Vasicek single-factor model
        - Merton structural model
    """
    
    METADATA = FrameworkMetadata(
        slug="credit-risk",
        name="Credit Risk Assessment",
        version="1.0.0",
        layer=VerticalLayer.FINANCIAL_ECONOMIC,
        tier=Tier.PROFESSIONAL,
        description=(
            "Comprehensive credit risk modeling with PD/LGD/EAD estimation, "
            "portfolio risk, and Basel-compliant capital calculation."
        ),
        required_domains=["exposures", "borrower_features", "historical_defaults"],
        output_domains=["pd", "lgd", "ead", "expected_loss", "capital"],
        constituent_models=["logistic_pd", "merton", "vasicek", "creditmetrics"],
        tags=["credit-risk", "pd", "lgd", "expected-loss", "basel"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    # Default rating PDs (through-the-cycle)
    RATING_PDS: dict[RatingGrade, float] = {
        RatingGrade.AAA: 0.0001,
        RatingGrade.AA: 0.0002,
        RatingGrade.A: 0.0005,
        RatingGrade.BBB: 0.002,
        RatingGrade.BB: 0.01,
        RatingGrade.B: 0.04,
        RatingGrade.CCC: 0.15,
        RatingGrade.CC: 0.30,
        RatingGrade.C: 0.50,
        RatingGrade.D: 1.0,
    }
    
    def __init__(
        self,
        correlation: float = 0.15,
        lgd_default: float = 0.45,
        confidence_level: float = 0.99,
    ):
        super().__init__()
        self.correlation = correlation
        self.lgd_default = lgd_default
        self.confidence_level = confidence_level
        self._transition_fn = CreditRiskTransition(correlation=correlation)
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        """Return framework metadata."""
        return cls.METADATA
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Initialize state for credit portfolio."""
        n_cohorts = config.cohort_size or 100
        
        return CohortStateVector(
            employment_prob=np.full(n_cohorts, 0.70),
            health_burden_score=np.full(n_cohorts, 0.2),
            credit_access_prob=np.random.beta(5, 2, n_cohorts),
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
        """Apply credit risk transition."""
        return self._transition_fn(state, t, config)
    
    def _compute_metrics(
        self,
        state: CohortStateVector,
    ) -> dict[str, Any]:
        """Compute credit risk metrics from state."""
        return {
            "default_rate": float(np.mean(state.credit_access_prob < 0.3)),
            "mean_credit_score": float(np.mean(state.credit_access_prob)),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        """Compute final output."""
        return {
            "framework": "credit-risk",
            "n_periods": trajectory.n_periods,
        }

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return Credit Risk dashboard specification."""
        return FrameworkDashboardSpec(
            slug="credit_risk",
            name="Credit Risk Assessment",
            description=(
                "Comprehensive credit risk modeling with PD/LGD/EAD estimation, "
                "portfolio risk analysis, and Basel-compliant capital calculation."
            ),
            layer="financial",
            parameters_schema={
                "type": "object",
                "properties": {
                    "pd_model": {
                        "type": "string",
                        "title": "PD Model",
                        "enum": ["logistic", "merton", "historical", "score_based"],
                        "default": "logistic",
                        "x-ui-widget": "select",
                        "x-ui-group": "methodology",
                    },
                    "lgd_assumption": {
                        "type": "number",
                        "title": "LGD Assumption (%)",
                        "minimum": 0,
                        "maximum": 100,
                        "default": 45,
                        "x-ui-widget": "slider",
                        "x-ui-step": 5,
                        "x-ui-format": ".0%",
                        "x-ui-group": "parameters",
                    },
                    "correlation_model": {
                        "type": "string",
                        "title": "Correlation Model",
                        "enum": ["vasicek", "creditmetrics", "copula"],
                        "default": "vasicek",
                        "x-ui-widget": "select",
                        "x-ui-group": "methodology",
                    },
                    "confidence_level": {
                        "type": "number",
                        "title": "Confidence Level",
                        "minimum": 0.9,
                        "maximum": 0.999,
                        "default": 0.999,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.001,
                        "x-ui-format": ".1%",
                        "x-ui-group": "parameters",
                    },
                },
            },
            default_parameters={
                "pd_model": "logistic",
                "lgd_assumption": 45,
                "correlation_model": "vasicek",
                "confidence_level": 0.999,
            },
            parameter_groups=[
                ParameterGroupSpec(key="methodology", title="Methodology", parameters=["pd_model", "correlation_model"]),
                ParameterGroupSpec(key="parameters", title="Risk Parameters", parameters=["lgd_assumption", "confidence_level"]),
            ],
            required_domains=["exposures", "borrower_features", "historical_defaults"],
            min_tier=Tier.PROFESSIONAL,
            output_views=[
                OutputViewSpec(
                    key="pd_distribution",
                    title="PD Distribution",
                    view_type=ViewType.HISTOGRAM,
                    config={"field": "pd", "bins": 20, "format": ".2%"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="pd_distribution_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="expected_loss",
                    title="Expected Loss",
                    view_type=ViewType.GAUGE,
                    config={"min": 0, "max": 0.1, "thresholds": [0.01, 0.03, 0.05], "format": ".2%"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="expected_loss_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="loss_distribution",
                    title="Loss Distribution",
                    view_type=ViewType.LINE_CHART,
                    config={"x_field": "loss_amount", "y_fields": ["probability", "cumulative"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="loss_distribution_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="concentration",
                    title="Portfolio Concentration",
                    view_type=ViewType.BAR_CHART,
                    config={"x_field": "rating", "y_field": "exposure", "stacked": True},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="concentration_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )
    
    # ════════════════════════════════════════════════════════════════════════════
    # Public API Methods
    # ════════════════════════════════════════════════════════════════════════════
    
    @requires_tier(Tier.PROFESSIONAL)
    def estimate_pd(
        self,
        exposure: CreditExposure,
        features: Optional[dict[str, float]] = None,
        model: PDModel = PDModel.LOGISTIC,
    ) -> PDResult:
        """
        Estimate Probability of Default.
        
        Args:
            exposure: Credit exposure
            features: Borrower characteristics for scoring
            model: PD model to use
        
        Returns:
            PD estimation result
        """
        features = features or {}
        
        if model == PDModel.HISTORICAL:
            # Use rating-based historical PD
            pd_ttc = self.RATING_PDS.get(exposure.rating, 0.02)
            pd_pit = pd_ttc  # Simplified
            
        elif model == PDModel.MERTON:
            # Merton structural model
            asset_value = features.get("asset_value", 100.0)
            debt_value = features.get("debt_value", 50.0)
            asset_volatility = features.get("asset_volatility", 0.25)
            T = exposure.maturity_years
            
            # Distance to default
            d2 = (np.log(asset_value / debt_value) - 0.5 * asset_volatility**2 * T) / (
                asset_volatility * np.sqrt(T)
            )
            pd_pit = float(stats.norm.cdf(-d2))
            pd_ttc = pd_pit * 0.8  # TTC adjustment
            
        else:  # LOGISTIC or SCORE_BASED
            # Logistic regression based on features
            # Simplified: use key risk factors
            leverage = features.get("leverage", 0.5)
            coverage = features.get("interest_coverage", 3.0)
            profitability = features.get("roi", 0.10)
            size = features.get("log_assets", 10.0)
            
            # Log-odds from features
            log_odds = (
                -3.0  # Intercept
                + 2.0 * leverage
                - 0.3 * coverage
                - 5.0 * profitability
                - 0.1 * size
            )
            pd_pit = float(1 / (1 + np.exp(-log_odds)))
            pd_ttc = pd_pit * 0.8  # TTC adjustment
        
        # Confidence interval (approximate)
        se = np.sqrt(pd_pit * (1 - pd_pit) / 100)  # Assume 100 observations
        ci_lower = max(0, pd_pit - 1.96 * se)
        ci_upper = min(1, pd_pit + 1.96 * se)
        
        return PDResult(
            exposure_id=exposure.id,
            pd=pd_pit,
            pd_through_the_cycle=pd_ttc,
            pd_point_in_time=pd_pit,
            confidence_interval=(ci_lower, ci_upper),
            model_used=model,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def estimate_lgd(
        self,
        exposure: CreditExposure,
        seniority: str = "senior_secured",
        economic_conditions: str = "normal",
    ) -> LGDResult:
        """
        Estimate Loss Given Default.
        
        Args:
            exposure: Credit exposure
            seniority: Debt seniority (senior_secured, senior_unsecured, subordinated)
            economic_conditions: normal, downturn
        
        Returns:
            LGD estimation result
        """
        # Base LGD by seniority
        base_lgd = {
            "senior_secured": 0.35,
            "senior_unsecured": 0.45,
            "subordinated": 0.70,
        }.get(seniority, 0.45)
        
        # Collateral adjustment
        if exposure.collateral_value > 0:
            collateral_coverage = exposure.collateral_value / max(exposure.ead, 1)
            haircut = 0.20  # Conservative haircut
            effective_collateral = exposure.collateral_value * (1 - haircut)
            lgd_adjustment = min(0.3, effective_collateral / max(exposure.ead, 1))
            base_lgd -= lgd_adjustment
        else:
            haircut = 0.0
        
        lgd = max(0.05, min(1.0, base_lgd))
        
        # Downturn LGD (10-20% higher)
        if economic_conditions == "downturn":
            lgd_downturn = min(1.0, lgd * 1.15)
        else:
            lgd_downturn = min(1.0, lgd * 1.10)
        
        # Cure rate (borrowers that cure before loss)
        cure_rate = max(0, 0.20 - lgd * 0.3)
        
        return LGDResult(
            exposure_id=exposure.id,
            lgd=lgd,
            lgd_downturn=lgd_downturn,
            recovery_rate=1 - lgd,
            collateral_haircut=haircut,
            cure_rate=cure_rate,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def compute_expected_loss(
        self,
        exposure: CreditExposure,
        pd_result: PDResult,
        lgd_result: LGDResult,
    ) -> ELResult:
        """
        Compute Expected Loss.
        
        EL = PD × LGD × EAD
        
        Args:
            exposure: Credit exposure
            pd_result: PD estimation
            lgd_result: LGD estimation
        
        Returns:
            Expected loss result
        """
        pd = pd_result.pd
        lgd = lgd_result.lgd
        ead = exposure.ead
        
        # Expected Loss
        el = pd * lgd * ead
        
        # Unexpected Loss (Vasicek formula)
        # UL = EAD * LGD * sqrt(PD * (1-PD)) * Φ^-1(confidence) * sqrt(correlation factor)
        rho = self.correlation
        ul = ead * lgd * np.sqrt(pd * (1 - pd)) * stats.norm.ppf(self.confidence_level) * np.sqrt(rho)
        
        # Basel risk weight (simplified IRB formula)
        # RW = 12.5 * LGD * [N((1-R)^-0.5 * G(PD) + (R/(1-R))^0.5 * G(0.999)) - PD]
        R = rho
        G_pd = stats.norm.ppf(pd) if pd > 0 else -10
        G_conf = stats.norm.ppf(self.confidence_level)
        
        if pd > 0 and pd < 1:
            conditional_pd = stats.norm.cdf(
                (G_pd + np.sqrt(R) * G_conf) / np.sqrt(1 - R)
            )
            K = lgd * (conditional_pd - pd)  # Capital charge
            rw = K * 12.5
        else:
            rw = 0.0
        
        return ELResult(
            exposure_id=exposure.id,
            pd=pd,
            lgd=lgd,
            ead=ead,
            expected_loss=el,
            unexpected_loss=ul,
            risk_weight=rw,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def compute_credit_score(
        self,
        features: dict[str, float],
    ) -> CreditScorecard:
        """
        Compute credit score from borrower features.
        
        Args:
            features: Borrower characteristics
        
        Returns:
            Credit scorecard result
        """
        # Scorecard components (simplified)
        components = {}
        
        # Payment history (35% weight)
        payment_history = features.get("payment_history", 0.95)
        components["payment_history"] = payment_history * 100
        
        # Credit utilization (30% weight)
        utilization = features.get("credit_utilization", 0.30)
        components["credit_utilization"] = max(0, 100 - utilization * 150)
        
        # Credit history length (15% weight)
        history_years = features.get("credit_history_years", 5)
        components["credit_history"] = min(100, history_years * 10)
        
        # Credit mix (10% weight)
        credit_types = features.get("credit_types", 2)
        components["credit_mix"] = min(100, credit_types * 25)
        
        # New credit (10% weight)
        new_accounts = features.get("new_accounts_12m", 1)
        components["new_credit"] = max(0, 100 - new_accounts * 20)
        
        # Weighted score
        weights = {
            "payment_history": 0.35,
            "credit_utilization": 0.30,
            "credit_history": 0.15,
            "credit_mix": 0.10,
            "new_credit": 0.10,
        }
        
        raw_score = sum(
            components[k] * weights[k] for k in weights
        )
        
        # Transform to 300-850 range
        final_score = 300 + raw_score * 5.5
        final_score = max(300, min(850, final_score))
        
        # Map to rating
        if final_score >= 800:
            rating = RatingGrade.AAA
        elif final_score >= 740:
            rating = RatingGrade.AA
        elif final_score >= 670:
            rating = RatingGrade.A
        elif final_score >= 580:
            rating = RatingGrade.BBB
        elif final_score >= 500:
            rating = RatingGrade.BB
        else:
            rating = RatingGrade.B
        
        # Score factors
        factors = []
        if components["credit_utilization"] < 50:
            factors.append("High credit utilization")
        if components["payment_history"] < 80:
            factors.append("Late payments detected")
        if components["credit_history"] < 50:
            factors.append("Short credit history")
        
        return CreditScorecard(
            score=final_score,
            score_percentile=stats.norm.cdf((final_score - 700) / 80) * 100,
            rating_grade=rating,
            component_scores=components,
            score_factors=factors,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def compute_portfolio_risk(
        self,
        exposures: list[CreditExposure],
        pd_results: list[PDResult],
        lgd_results: list[LGDResult],
    ) -> PortfolioCreditRisk:
        """
        Compute portfolio-level credit risk.
        
        Args:
            exposures: List of credit exposures
            pd_results: PD results for each exposure
            lgd_results: LGD results for each exposure
        
        Returns:
            Portfolio credit risk metrics
        """
        if not exposures:
            return PortfolioCreditRisk()
        
        # Map results by exposure id
        pd_map = {r.exposure_id: r.pd for r in pd_results}
        lgd_map = {r.exposure_id: r.lgd for r in lgd_results}
        
        total_ead = sum(e.ead for e in exposures)
        
        # Expected loss
        total_el = sum(
            pd_map.get(e.id, 0.02) * lgd_map.get(e.id, 0.45) * e.ead
            for e in exposures
        )
        
        # Concentration
        ead_shares = [e.ead / total_ead for e in exposures]
        hhi = sum(s**2 for s in ead_shares)
        sorted_shares = sorted(ead_shares, reverse=True)
        top_10_share = sum(sorted_shares[:10]) if len(sorted_shares) >= 10 else sum(sorted_shares)
        
        # Portfolio VaR using Vasicek model
        avg_pd = np.mean([pd_map.get(e.id, 0.02) for e in exposures])
        avg_lgd = np.mean([lgd_map.get(e.id, 0.45) for e in exposures])
        
        rho = self.correlation
        
        # Vasicek formula for conditional PD at 99%
        conditional_pd_99 = stats.norm.cdf(
            (stats.norm.ppf(avg_pd) + np.sqrt(rho) * stats.norm.ppf(0.99)) /
            np.sqrt(1 - rho)
        )
        
        loss_var_99 = conditional_pd_99 * avg_lgd * total_ead
        
        # 95% VaR
        conditional_pd_95 = stats.norm.cdf(
            (stats.norm.ppf(avg_pd) + np.sqrt(rho) * stats.norm.ppf(0.95)) /
            np.sqrt(1 - rho)
        )
        loss_var_95 = conditional_pd_95 * avg_lgd * total_ead
        
        # Expected Shortfall (approximate as 1.2 * VaR)
        loss_es_99 = loss_var_99 * 1.2
        
        # Unexpected loss
        total_ul = loss_var_99 - total_el
        
        # Capital
        economic_capital = total_ul  # Economic capital = UL
        regulatory_capital = total_ead * 0.08  # Basel simplified
        
        return PortfolioCreditRisk(
            total_ead=total_ead,
            total_expected_loss=total_el,
            total_unexpected_loss=total_ul,
            herfindahl_index=hhi,
            top_10_concentration=top_10_share,
            loss_var_95=loss_var_95,
            loss_var_99=loss_var_99,
            loss_es_99=loss_es_99,
            economic_capital=economic_capital,
            regulatory_capital=regulatory_capital,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def generate_transition_matrix(
        self,
        historical_migrations: Optional[list[tuple[str, str]]] = None,
    ) -> TransitionMatrix:
        """
        Generate credit rating transition matrix.
        
        Args:
            historical_migrations: List of (from_rating, to_rating) observations
        
        Returns:
            Transition matrix
        """
        ratings = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC", "CC", "C", "D"]
        n = len(ratings)
        
        if historical_migrations and len(historical_migrations) > 100:
            # Estimate from data
            matrix = np.zeros((n, n))
            counts = np.zeros(n)
            
            for from_r, to_r in historical_migrations:
                if from_r in ratings and to_r in ratings:
                    i = ratings.index(from_r)
                    j = ratings.index(to_r)
                    matrix[i, j] += 1
                    counts[i] += 1
            
            # Normalize
            for i in range(n):
                if counts[i] > 0:
                    matrix[i] = matrix[i] / counts[i]
                else:
                    matrix[i, i] = 1.0
        else:
            # Use stylized S&P-like matrix
            matrix = np.array([
                [0.9081, 0.0833, 0.0068, 0.0006, 0.0012, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
                [0.0070, 0.9065, 0.0779, 0.0064, 0.0006, 0.0014, 0.0002, 0.0000, 0.0000, 0.0000],
                [0.0009, 0.0227, 0.9105, 0.0552, 0.0074, 0.0026, 0.0001, 0.0006, 0.0000, 0.0000],
                [0.0002, 0.0033, 0.0595, 0.8693, 0.0530, 0.0117, 0.0012, 0.0004, 0.0000, 0.0014],
                [0.0003, 0.0014, 0.0067, 0.0773, 0.8053, 0.0884, 0.0100, 0.0025, 0.0003, 0.0078],
                [0.0000, 0.0011, 0.0024, 0.0043, 0.0648, 0.8346, 0.0407, 0.0216, 0.0028, 0.0277],
                [0.0022, 0.0000, 0.0022, 0.0130, 0.0238, 0.1083, 0.6393, 0.0975, 0.0195, 0.0942],
                [0.0000, 0.0000, 0.0000, 0.0000, 0.0227, 0.0454, 0.1136, 0.4546, 0.1591, 0.2046],
                [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0556, 0.0556, 0.0556, 0.4999, 0.3333],
                [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 1.0000],
            ])
        
        return TransitionMatrix(
            matrix=matrix,
            rating_labels=ratings,
            horizon_years=1.0,
        )
