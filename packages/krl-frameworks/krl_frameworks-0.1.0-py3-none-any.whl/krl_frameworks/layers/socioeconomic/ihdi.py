# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Inequality-adjusted Human Development Index (IHDI)
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Inequality-adjusted Human Development Index (IHDI) Framework.

IHDI adjusts HDI for inequality in each dimension using the Atkinson
inequality measure. The IHDI captures losses in human development
due to inequality.

Core Methodology:
    1. Compute dimension indices (health, education, income) per HDI
    2. Compute Atkinson inequality index for each dimension
    3. Apply inequality adjustment: IHDI_dim = HDI_dim × (1 - A_dim)
    4. IHDI = geometric mean of adjusted dimension indices

The Atkinson Index:
    A = 1 - [geometric_mean(x) / arithmetic_mean(x)]
    
    Where x is the distribution of achievements in a dimension.
    A ranges from 0 (perfect equality) to 1 (maximum inequality).

Key Metrics:
    - IHDI: Inequality-adjusted composite index
    - Loss%: Percentage loss from HDI to IHDI
    - Coefficient of Human Inequality: Average inequality across dimensions

References:
    - UNDP Human Development Report Technical Notes
    - Atkinson, A.B. (1970). "On the Measurement of Inequality"
    - Alkire, S. & Foster, J. (2010). "Designing the IHDI"

Tier: COMMUNITY
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
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
    ViewType,
    ResultClass,
    TemporalSemantics,
)
from krl_frameworks.core.data_bundle import DataBundle
from krl_frameworks.core.state import CohortStateVector, StateTrajectory
from krl_frameworks.core.tier import Tier
from krl_frameworks.simulation.cbss import TransitionFunction

if TYPE_CHECKING:
    from krl_frameworks.core.config import FrameworkConfig

__all__ = ["IHDIFramework", "IHDITransition", "IHDIMetrics"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# IHDI Goalposts (same as HDI)
# ════════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class IHDIGoalposts:
    """UNDP goalposts for dimension normalization."""
    
    life_expectancy_min: float = 20.0
    life_expectancy_max: float = 85.0
    schooling_mean_min: float = 0.0
    schooling_mean_max: float = 15.0
    schooling_expected_min: float = 0.0
    schooling_expected_max: float = 18.0
    gni_min: float = 100.0
    gni_max: float = 75000.0


# ════════════════════════════════════════════════════════════════════════════════
# IHDI Metrics
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class IHDIMetrics:
    """
    Container for IHDI computation results.
    
    Attributes:
        ihdi: Inequality-adjusted HDI.
        hdi: Standard HDI (for comparison).
        loss_pct: Percentage loss from HDI to IHDI.
        health_index_adj: Adjusted health dimension index.
        education_index_adj: Adjusted education dimension index.
        income_index_adj: Adjusted income dimension index.
        atkinson_health: Atkinson index for health.
        atkinson_education: Atkinson index for education.
        atkinson_income: Atkinson index for income.
        coefficient_human_inequality: Average of Atkinson indices.
        classification: Development classification (based on IHDI).
    """
    
    ihdi: float
    hdi: float
    loss_pct: float
    health_index_adj: float
    education_index_adj: float
    income_index_adj: float
    atkinson_health: float
    atkinson_education: float
    atkinson_income: float
    coefficient_human_inequality: float
    classification: str
    
    @classmethod
    def classify(cls, ihdi: float) -> str:
        """Classify IHDI into development category."""
        if ihdi >= 0.8:
            return "Very High Human Development"
        elif ihdi >= 0.7:
            return "High Human Development"
        elif ihdi >= 0.55:
            return "Medium Human Development"
        else:
            return "Low Human Development"
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "ihdi": self.ihdi,
            "hdi": self.hdi,
            "loss_pct": self.loss_pct,
            "health_index_adj": self.health_index_adj,
            "education_index_adj": self.education_index_adj,
            "income_index_adj": self.income_index_adj,
            "atkinson_health": self.atkinson_health,
            "atkinson_education": self.atkinson_education,
            "atkinson_income": self.atkinson_income,
            "coefficient_human_inequality": self.coefficient_human_inequality,
            "classification": self.classification,
        }


# ════════════════════════════════════════════════════════════════════════════════
# IHDI Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class IHDITransition(TransitionFunction):
    """
    Transition function for IHDI cohort state evolution.
    
    Models both HDI improvement and inequality dynamics:
    - Average development improvements (per HDI)
    - Inequality reduction/increase based on policy
    """
    
    name = "IHDITransition"
    
    def __init__(
        self,
        development_rate: float = 0.01,
        inequality_reduction_rate: float = 0.005,
    ):
        self.development_rate = development_rate
        self.inequality_reduction_rate = inequality_reduction_rate
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply IHDI transition with inequality dynamics."""
        params = params or {}
        
        dev_rate = params.get("development_rate", self.development_rate)
        ineq_rate = params.get("inequality_reduction_rate", self.inequality_reduction_rate)
        
        # Development improves averages
        new_opportunity = np.clip(
            state.opportunity_score + dev_rate * (1 - state.opportunity_score),
            0, 1
        )
        new_health_burden = np.clip(
            state.health_burden_score * (1 - dev_rate), 0, 1
        )
        
        # Inequality reduction compresses distribution
        # (reduce variance in deprivation)
        mean_dep = np.mean(state.deprivation_vector)
        new_deprivation = state.deprivation_vector + ineq_rate * (
            mean_dep - state.deprivation_vector
        )
        new_deprivation = np.clip(new_deprivation * (1 - dev_rate * 0.5), 0, 1)
        
        return CohortStateVector(
            employment_prob=np.clip(state.employment_prob + dev_rate * 0.3, 0, 1),
            health_burden_score=new_health_burden,
            credit_access_prob=np.clip(state.credit_access_prob + dev_rate * 0.2, 0, 1),
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=new_opportunity,
            sector_output=state.sector_output * (1 + dev_rate),
            deprivation_vector=new_deprivation,
        )


# ════════════════════════════════════════════════════════════════════════════════
# IHDI Framework
# ════════════════════════════════════════════════════════════════════════════════


class IHDIFramework(BaseMetaFramework):
    """
    Inequality-adjusted Human Development Index (IHDI) Framework.
    
    Computes IHDI by adjusting HDI dimensions for inequality using
    the Atkinson inequality measure.
    
    Example:
        >>> bundle = DataBundle.from_dataframes({
        ...     "health": health_df,      # with life_expectancy distribution
        ...     "education": edu_df,      # with schooling distribution
        ...     "economic": econ_df,      # with income distribution
        ... })
        >>> ihdi = IHDIFramework()
        >>> metrics = ihdi.compute_ihdi(bundle)
        >>> print(f"IHDI: {metrics.ihdi:.3f}")
        >>> print(f"Loss from HDI: {metrics.loss_pct:.1f}%")
    """
    
    def __init__(
        self,
        goalposts: Optional[IHDIGoalposts] = None,
    ):
        super().__init__()
        self.goalposts = goalposts or IHDIGoalposts()
        self._transition_fn = IHDITransition()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        """Return IHDI framework metadata."""
        return FrameworkMetadata(
            slug="ihdi",
            name="Inequality-adjusted Human Development Index",
            version="1.0.0",
            layer=VerticalLayer.SOCIOECONOMIC_ACADEMIC,
            tier=Tier.COMMUNITY,
            description=(
                "UNDP IHDI adjusting HDI for inequality using "
                "Atkinson inequality measures across dimensions."
            ),
            required_domains=["health", "education", "economic"],
            output_domains=["ihdi", "hdi", "atkinson_indices", "loss_pct"],
            constituent_models=["atkinson_inequality", "geometric_aggregator"],
            tags=["socioeconomic", "development", "ihdi", "inequality", "undp"],
            author="Khipu Research Labs",
            license="Apache-2.0",
        )
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Compute initial state from HDI components with inequality."""
        health_data = bundle.get("health") if bundle.has_domain("health") else None
        edu_data = bundle.get("education") if bundle.has_domain("education") else None
        econ_data = bundle.get("economic") if bundle.has_domain("economic") else None
        
        n_cohorts = 100
        if health_data:
            n_cohorts = len(health_data.data)
        elif edu_data:
            n_cohorts = len(edu_data.data)
        elif econ_data:
            n_cohorts = len(econ_data.data)
        
        # Extract life expectancy distribution
        if health_data and "life_expectancy" in health_data.data.columns:
            life_exp = health_data.data["life_expectancy"].values
            health_idx = self._normalize_dimension(
                life_exp,
                self.goalposts.life_expectancy_min,
                self.goalposts.life_expectancy_max,
            )
            health_burden = 1 - health_idx
        else:
            health_burden = np.random.beta(2, 5, n_cohorts)  # Simulated distribution
        
        # Extract education (schooling years)
        if edu_data and "mean_schooling" in edu_data.data.columns:
            schooling = edu_data.data["mean_schooling"].values
            edu_idx = self._normalize_dimension(
                schooling,
                self.goalposts.schooling_mean_min,
                self.goalposts.schooling_mean_max,
            )
            opportunity = edu_idx
        else:
            opportunity = np.random.beta(5, 2, n_cohorts)
        
        # Extract income distribution
        if econ_data and "gni_per_capita" in econ_data.data.columns:
            gni = econ_data.data["gni_per_capita"].values
            income_idx = self._normalize_income(gni)
            deprivation = 1 - income_idx
        else:
            deprivation = np.random.beta(2, 5, n_cohorts)
        
        return CohortStateVector(
            employment_prob=np.full(n_cohorts, 0.7),
            health_burden_score=health_burden,
            credit_access_prob=np.full(n_cohorts, 0.5),
            housing_cost_ratio=np.full(n_cohorts, 0.3),
            opportunity_score=opportunity,
            sector_output=np.full(n_cohorts, 1.0),
            deprivation_vector=deprivation,
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        step: int,
    ) -> CohortStateVector:
        """Apply IHDI transition using the configured transition function."""
        from krl_frameworks.core.config import FrameworkConfig
        return self._transition_fn(state, step, FrameworkConfig())
    
    def _normalize_dimension(
        self,
        values: np.ndarray,
        minimum: float,
        maximum: float,
    ) -> np.ndarray:
        """Normalize dimension using goalposts."""
        return np.clip((values - minimum) / (maximum - minimum), 0, 1)
    
    def _normalize_income(self, gni: np.ndarray) -> np.ndarray:
        """Normalize income using log transformation."""
        log_min = np.log(self.goalposts.gni_min)
        log_max = np.log(self.goalposts.gni_max)
        log_gni = np.log(np.maximum(gni, 1))
        return np.clip((log_gni - log_min) / (log_max - log_min), 0, 1)
    
    def _compute_atkinson(self, distribution: np.ndarray, epsilon: float = 1.0) -> float:
        """
        Compute Atkinson inequality index.
        
        A = 1 - (geometric_mean / arithmetic_mean)
        
        For epsilon = 1, this is the standard UNDP formulation.
        """
        # Remove zeros and negative values
        valid = distribution[distribution > 0]
        if len(valid) < 2:
            return 0.0
        
        arithmetic_mean = np.mean(valid)
        if arithmetic_mean <= 0:
            return 0.0
        
        # Geometric mean via log
        log_mean = np.mean(np.log(valid))
        geometric_mean = np.exp(log_mean)
        
        atkinson = 1 - (geometric_mean / arithmetic_mean)
        return float(np.clip(atkinson, 0, 1))
    
    def _compute_metrics(
        self,
        trajectory: StateTrajectory,
    ) -> dict[str, Any]:
        """Compute IHDI metrics from trajectory."""
        state = trajectory.final_state
        
        # Compute dimension indices from state
        health_idx = 1 - np.mean(state.health_burden_score)
        education_idx = np.mean(state.opportunity_score)
        income_idx = 1 - np.mean(state.deprivation_vector)
        
        # Compute Atkinson indices (using distribution variance as proxy)
        atkinson_health = self._compute_atkinson(1 - state.health_burden_score)
        atkinson_education = self._compute_atkinson(state.opportunity_score)
        atkinson_income = self._compute_atkinson(1 - state.deprivation_vector)
        
        # Coefficient of Human Inequality
        coef_inequality = (atkinson_health + atkinson_education + atkinson_income) / 3
        
        # Compute adjusted indices
        health_adj = health_idx * (1 - atkinson_health)
        education_adj = education_idx * (1 - atkinson_education)
        income_adj = income_idx * (1 - atkinson_income)
        
        # HDI = geometric mean of dimension indices
        hdi = (health_idx * education_idx * income_idx) ** (1/3)
        
        # IHDI = geometric mean of adjusted indices
        ihdi = (health_adj * education_adj * income_adj) ** (1/3)
        
        # Loss percentage
        loss_pct = 100 * (1 - ihdi / hdi) if hdi > 0 else 0.0
        
        return IHDIMetrics(
            ihdi=float(ihdi),
            hdi=float(hdi),
            loss_pct=float(loss_pct),
            health_index_adj=float(health_adj),
            education_index_adj=float(education_adj),
            income_index_adj=float(income_adj),
            atkinson_health=float(atkinson_health),
            atkinson_education=float(atkinson_education),
            atkinson_income=float(atkinson_income),
            coefficient_human_inequality=float(coef_inequality),
            classification=IHDIMetrics.classify(ihdi),
        ).to_dict()
    
    def compute_ihdi(
        self,
        bundle: DataBundle,
        config: Optional[FrameworkConfig] = None,
    ) -> IHDIMetrics:
        """
        Compute IHDI from dimension distributions.
        
        Args:
            bundle: DataBundle with health, education, economic domains.
            config: Optional framework configuration.
        
        Returns:
            IHDIMetrics with IHDI, Atkinson indices, and loss percentage.
        """
        from krl_frameworks.core.config import FrameworkConfig
        config = config or FrameworkConfig()
        
        # Extract distributions
        health_dist = self._extract_health_distribution(bundle)
        edu_dist = self._extract_education_distribution(bundle)
        income_dist = self._extract_income_distribution(bundle)
        
        # Compute dimension indices (averages)
        health_idx = np.mean(health_dist)
        education_idx = np.mean(edu_dist)
        income_idx = np.mean(income_dist)
        
        # Compute Atkinson indices
        atkinson_health = self._compute_atkinson(health_dist)
        atkinson_education = self._compute_atkinson(edu_dist)
        atkinson_income = self._compute_atkinson(income_dist)
        
        # Coefficient of Human Inequality
        coef_inequality = (atkinson_health + atkinson_education + atkinson_income) / 3
        
        # Adjusted indices
        health_adj = health_idx * (1 - atkinson_health)
        education_adj = education_idx * (1 - atkinson_education)
        income_adj = income_idx * (1 - atkinson_income)
        
        # HDI and IHDI
        hdi = (health_idx * education_idx * income_idx) ** (1/3)
        ihdi = (health_adj * education_adj * income_adj) ** (1/3)
        
        loss_pct = 100 * (1 - ihdi / hdi) if hdi > 0 else 0.0
        
        return IHDIMetrics(
            ihdi=float(ihdi),
            hdi=float(hdi),
            loss_pct=float(loss_pct),
            health_index_adj=float(health_adj),
            education_index_adj=float(education_adj),
            income_index_adj=float(income_adj),
            atkinson_health=float(atkinson_health),
            atkinson_education=float(atkinson_education),
            atkinson_income=float(atkinson_income),
            coefficient_human_inequality=float(coef_inequality),
            classification=IHDIMetrics.classify(ihdi),
        )
    
    def _extract_health_distribution(self, bundle: DataBundle) -> np.ndarray:
        """Extract normalized health distribution."""
        if bundle.has_domain("health"):
            df = bundle.get("health").data
            if "life_expectancy" in df.columns:
                values = df["life_expectancy"].values.astype(float)
                return self._normalize_dimension(
                    values,
                    self.goalposts.life_expectancy_min,
                    self.goalposts.life_expectancy_max,
                )
        return np.random.beta(5, 2, 100)  # Default distribution
    
    def _extract_education_distribution(self, bundle: DataBundle) -> np.ndarray:
        """Extract normalized education distribution."""
        if bundle.has_domain("education"):
            df = bundle.get("education").data
            if "mean_schooling" in df.columns:
                values = df["mean_schooling"].values.astype(float)
                return self._normalize_dimension(
                    values,
                    self.goalposts.schooling_mean_min,
                    self.goalposts.schooling_mean_max,
                )
        return np.random.beta(5, 2, 100)
    
    def _extract_income_distribution(self, bundle: DataBundle) -> np.ndarray:
        """Extract normalized income distribution."""
        if bundle.has_domain("economic"):
            df = bundle.get("economic").data
            if "gni_per_capita" in df.columns:
                values = df["gni_per_capita"].values.astype(float)
                return self._normalize_income(values)
        return np.random.beta(3, 3, 100)

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Return IHDI dashboard specification.

        Parameters extracted from IHDIGoalposts and IHDITransition.
        """
        return FrameworkDashboardSpec(
            slug="ihdi",
            name="Inequality-adjusted Human Development Index",
            description="UNDP IHDI adjusting HDI for inequality using Atkinson measures across health, education, and income dimensions",
            layer="socioeconomic",
            min_tier=Tier.COMMUNITY,
            parameters_schema={
                "type": "object",
                "properties": {
                    # ═══════════════════════════════════════════════════════
                    # Development Dynamics
                    # ═══════════════════════════════════════════════════════
                    "development_rate": {
                        "type": "number",
                        "title": "Development Rate",
                        "description": "Annual rate of average development improvement across dimensions",
                        "minimum": 0.0,
                        "maximum": 0.1,
                        "default": 0.01,
                        "x-ui-widget": "slider",
                        "x-ui-group": "dynamics",
                        "x-ui-order": 1,
                        "x-ui-help": "Rate of improvement in health, education, and income averages (default: 1% per year)",
                    },
                    "inequality_reduction_rate": {
                        "type": "number",
                        "title": "Inequality Reduction Rate",
                        "description": "Annual rate of inequality reduction through policy interventions",
                        "minimum": 0.0,
                        "maximum": 0.05,
                        "default": 0.005,
                        "x-ui-widget": "slider",
                        "x-ui-group": "dynamics",
                        "x-ui-order": 2,
                        "x-ui-help": "Rate of compression in dimension distributions (reduces Atkinson indices)",
                    },

                    # ═══════════════════════════════════════════════════════
                    # Normalization Goalposts (Health)
                    # ═══════════════════════════════════════════════════════
                    "life_expectancy_min": {
                        "type": "number",
                        "title": "Life Expectancy Minimum (years)",
                        "description": "UNDP minimum goalpost for life expectancy normalization",
                        "minimum": 15.0,
                        "maximum": 30.0,
                        "default": 20.0,
                        "x-ui-widget": "number",
                        "x-ui-group": "goalposts",
                        "x-ui-order": 3,
                        "x-ui-help": "UNDP standard: 20 years",
                    },
                    "life_expectancy_max": {
                        "type": "number",
                        "title": "Life Expectancy Maximum (years)",
                        "description": "UNDP maximum goalpost for life expectancy normalization",
                        "minimum": 70.0,
                        "maximum": 100.0,
                        "default": 85.0,
                        "x-ui-widget": "number",
                        "x-ui-group": "goalposts",
                        "x-ui-order": 4,
                        "x-ui-help": "UNDP standard: 85 years",
                    },

                    # ═══════════════════════════════════════════════════════
                    # Normalization Goalposts (Education)
                    # ═══════════════════════════════════════════════════════
                    "schooling_mean_max": {
                        "type": "number",
                        "title": "Mean Schooling Maximum (years)",
                        "description": "UNDP maximum goalpost for mean years of schooling",
                        "minimum": 10.0,
                        "maximum": 20.0,
                        "default": 15.0,
                        "x-ui-widget": "number",
                        "x-ui-group": "goalposts",
                        "x-ui-order": 5,
                        "x-ui-help": "UNDP standard: 15 years",
                    },

                    # ═══════════════════════════════════════════════════════
                    # Normalization Goalposts (Income)
                    # ═══════════════════════════════════════════════════════
                    "gni_min": {
                        "type": "number",
                        "title": "GNI per Capita Minimum ($)",
                        "description": "UNDP minimum goalpost for GNI per capita (PPP)",
                        "minimum": 50.0,
                        "maximum": 500.0,
                        "default": 100.0,
                        "x-ui-widget": "number",
                        "x-ui-group": "goalposts",
                        "x-ui-order": 6,
                        "x-ui-help": "UNDP standard: $100 (PPP)",
                    },
                    "gni_max": {
                        "type": "number",
                        "title": "GNI per Capita Maximum ($)",
                        "description": "UNDP maximum goalpost for GNI per capita (PPP)",
                        "minimum": 50000.0,
                        "maximum": 150000.0,
                        "default": 75000.0,
                        "x-ui-widget": "number",
                        "x-ui-group": "goalposts",
                        "x-ui-order": 7,
                        "x-ui-help": "UNDP standard: $75,000 (PPP)",
                    },
                },
                "required": [],
            },
            default_parameters={
                "development_rate": 0.01,
                "inequality_reduction_rate": 0.005,
                "life_expectancy_min": 20.0,
                "life_expectancy_max": 85.0,
                "schooling_mean_max": 15.0,
                "gni_min": 100.0,
                "gni_max": 75000.0,
            },
            parameter_groups=[
                {
                    "id": "dynamics",
                    "label": "Development Dynamics",
                    "description": "Rates of development improvement and inequality reduction",
                    "order": 1,
                },
                {
                    "id": "goalposts",
                    "label": "UNDP Normalization Goalposts",
                    "description": "Min/max bounds for dimension normalization (UNDP standards)",
                    "order": 2,
                },
            ],
            output_views=[
                OutputViewSpec(
                    key="ihdi_gauge",
                    title="IHDI Score",
                    view_type=ViewType.GAUGE,
                    description="Inequality-adjusted Human Development Index (0-1 scale)",
                    config={
                        "metric_path": "ihdi",
                        "min": 0.0,
                        "max": 1.0,
                        "thresholds": [0.55, 0.7, 0.8],
                        "colors": ["#ef4444", "#f59e0b", "#22c55e"],
                    },
                result_class=ResultClass.SCALAR_INDEX,
                output_key="ihdi_gauge_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="comparison",
                    title="IHDI vs HDI Comparison",
                    view_type=ViewType.BAR_CHART,
                    description="Comparison of IHDI and HDI with loss percentage",
                    config={
                        "x_axis": "index_type",
                        "y_axis": "value",
                    },
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="comparison_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="dimensions",
                    title="Adjusted Dimension Indices",
                    view_type=ViewType.BAR_CHART,
                    description="Health, Education, and Income indices after inequality adjustment",
                    config={
                        "x_axis": "dimension",
                        "y_axis": "value",
                    },
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="dimensions_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="atkinson",
                    title="Atkinson Inequality Indices",
                    view_type=ViewType.BAR_CHART,
                    description="Inequality measures for each dimension (0 = perfect equality, 1 = max inequality)",
                    config={
                        "x_axis": "dimension",
                        "y_axis": "atkinson_index",
                    },
                result_class=ResultClass.DOMAIN_DECOMPOSITION,
                output_key="atkinson_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="summary_table",
                    title="IHDI Summary",
                    view_type=ViewType.TABLE,
                    description="Complete IHDI metrics including classification",
                    config={
                        "columns": [
                            {"key": "ihdi", "label": "IHDI", "format": ".3f"},
                            {"key": "hdi", "label": "HDI", "format": ".3f"},
                            {"key": "loss_pct", "label": "Loss (%)", "format": ".1f"},
                            {"key": "coefficient_human_inequality", "label": "Coef. Inequality", "format": ".3f"},
                            {"key": "classification", "label": "Classification"},
                        ],
                    },
                result_class=ResultClass.CONFIDENCE_PROVENANCE,
                output_key="summary_table_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
            ],
        )
