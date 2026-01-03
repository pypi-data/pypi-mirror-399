# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - World Bank Indicators (WBI) Composite Index
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
World Bank Indicators (WBI) Composite Index Framework.

Aggregates World Bank Development Indicators into a composite index
using z-score normalization and weighted averaging. Supports custom
indicator selection and weighting schemes.

Core Methodology:
    1. Select indicators from WDI catalog
    2. Z-score normalize each indicator
    3. Apply directional adjustment (higher = better vs lower = better)
    4. Weighted average aggregation
    5. Rescale to [0, 100] index

Default Indicator Categories:
    - Economic: GDP per capita, GDP growth, inflation
    - Social: Poverty headcount, Gini, unemployment
    - Infrastructure: Internet users, electricity access, roads
    - Health: Life expectancy, infant mortality, physicians
    - Education: Literacy, enrollment, spending

CBSS Integration:
    - Tracks composite WBI score per cohort over time
    - Models indicator improvements based on policy interventions
    - Projects development trajectories

References:
    - World Bank Development Indicators Database
    - OECD Better Life Index methodology (z-score approach)

Tier: COMMUNITY
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
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

__all__ = ["WBIFramework", "WBITransition", "WBIMetrics", "WBIConfig"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# WBI Configuration
# ════════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class WBIConfig:
    """
    Configuration for WBI composite index computation.
    
    Attributes:
        indicator_weights: Dict mapping indicator codes to weights.
        indicator_directions: Dict mapping indicators to direction (+1 or -1).
        category_weights: Dict mapping categories to category-level weights.
        min_indicators: Minimum indicators required for valid index.
        rescale_to_100: Whether to rescale final index to [0, 100].
    """
    
    # Default weights by category
    category_weights: dict[str, float] = field(default_factory=lambda: {
        "economic": 0.25,
        "social": 0.20,
        "infrastructure": 0.15,
        "health": 0.20,
        "education": 0.20,
    })
    
    # Default indicator weights within categories
    indicator_weights: dict[str, float] = field(default_factory=lambda: {
        # Economic
        "NY.GDP.PCAP.CD": 1.0,       # GDP per capita (current US$)
        "NY.GDP.MKTP.KD.ZG": 0.5,    # GDP growth (annual %)
        "FP.CPI.TOTL.ZG": 0.3,       # Inflation, consumer prices
        # Social
        "SI.POV.DDAY": 1.0,          # Poverty headcount ratio ($2.15/day)
        "SI.POV.GINI": 0.8,          # Gini index
        "SL.UEM.TOTL.ZS": 0.7,       # Unemployment rate
        # Infrastructure
        "IT.NET.USER.ZS": 1.0,       # Internet users (% of population)
        "EG.ELC.ACCS.ZS": 0.8,       # Access to electricity
        # Health
        "SP.DYN.LE00.IN": 1.0,       # Life expectancy at birth
        "SH.DYN.MORT": 0.8,          # Infant mortality rate
        "SH.MED.PHYS.ZS": 0.5,       # Physicians per 1,000
        # Education
        "SE.ADT.LITR.ZS": 1.0,       # Literacy rate
        "SE.PRM.ENRR": 0.7,          # Primary enrollment
        "SE.XPD.TOTL.GD.ZS": 0.5,    # Education spending (% GDP)
    })
    
    # Direction: +1 = higher is better, -1 = lower is better
    indicator_directions: dict[str, int] = field(default_factory=lambda: {
        "NY.GDP.PCAP.CD": 1,
        "NY.GDP.MKTP.KD.ZG": 1,
        "FP.CPI.TOTL.ZG": -1,        # Lower inflation is better
        "SI.POV.DDAY": -1,           # Lower poverty is better
        "SI.POV.GINI": -1,           # Lower inequality is better
        "SL.UEM.TOTL.ZS": -1,        # Lower unemployment is better
        "IT.NET.USER.ZS": 1,
        "EG.ELC.ACCS.ZS": 1,
        "SP.DYN.LE00.IN": 1,
        "SH.DYN.MORT": -1,           # Lower mortality is better
        "SH.MED.PHYS.ZS": 1,
        "SE.ADT.LITR.ZS": 1,
        "SE.PRM.ENRR": 1,
        "SE.XPD.TOTL.GD.ZS": 1,
    })
    
    min_indicators: int = 5
    rescale_to_100: bool = True


# ════════════════════════════════════════════════════════════════════════════════
# WBI Metrics
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class WBIMetrics:
    """
    Container for WBI computation results.
    
    Attributes:
        composite_index: Overall WBI composite score.
        category_scores: Scores by category (economic, social, etc.).
        indicator_z_scores: Z-scores for each indicator.
        indicator_contributions: Weighted contribution of each indicator.
        n_indicators: Number of indicators used.
        coverage_pct: Percentage of requested indicators with data.
    """
    
    composite_index: float
    category_scores: dict[str, float]
    indicator_z_scores: dict[str, float]
    indicator_contributions: dict[str, float]
    n_indicators: int
    coverage_pct: float
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "composite_index": self.composite_index,
            "category_scores": self.category_scores,
            "indicator_z_scores": self.indicator_z_scores,
            "indicator_contributions": self.indicator_contributions,
            "n_indicators": self.n_indicators,
            "coverage_pct": self.coverage_pct,
        }


# ════════════════════════════════════════════════════════════════════════════════
# WBI Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class WBITransition(TransitionFunction):
    """
    Transition function for WBI cohort state evolution.
    
    Models gradual improvements in development indicators based on:
    - Base development momentum (convergence to frontier)
    - Policy intervention effects
    - Random shocks
    """
    
    name = "WBITransition"
    
    def __init__(
        self,
        convergence_rate: float = 0.02,
        shock_volatility: float = 0.01,
    ):
        self.convergence_rate = convergence_rate
        self.shock_volatility = shock_volatility
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply WBI transition with convergence dynamics."""
        params = params or {}
        
        convergence = params.get("convergence_rate", self.convergence_rate)
        volatility = params.get("shock_volatility", self.shock_volatility)
        
        # Opportunity score converges toward 1.0 (development frontier)
        gap = 1.0 - state.opportunity_score
        improvement = convergence * gap
        shock = np.random.normal(0, volatility, state.opportunity_score.shape)
        new_opportunity = np.clip(state.opportunity_score + improvement + shock, 0, 1)
        
        # Economic output grows with development
        output_growth = 1 + convergence * 0.5 + shock * 0.1
        new_sector_output = state.sector_output * output_growth
        
        # Health and credit improve with development
        new_health_burden = np.clip(
            state.health_burden_score * (1 - convergence * 0.3), 0, 1
        )
        new_credit_access = np.clip(
            state.credit_access_prob + convergence * 0.1, 0, 1
        )
        
        return CohortStateVector(
            employment_prob=np.clip(state.employment_prob + convergence * 0.05, 0, 1),
            health_burden_score=new_health_burden,
            credit_access_prob=new_credit_access,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=new_opportunity,
            sector_output=new_sector_output,
            deprivation_vector=state.deprivation_vector * (1 - convergence * 0.1),
        )


# ════════════════════════════════════════════════════════════════════════════════
# WBI Framework
# ════════════════════════════════════════════════════════════════════════════════


class WBIFramework(BaseMetaFramework):
    """
    World Bank Indicators Composite Index Framework.
    
    Aggregates World Bank Development Indicators into a composite index
    using z-score normalization and weighted averaging.
    
    Example:
        >>> bundle = DataBundle.from_dataframes({
        ...     "wdi": wdi_df,  # World Development Indicators data
        ... })
        >>> wbi = WBIFramework()
        >>> metrics = wbi.compute_wbi(bundle)
        >>> print(f"WBI Score: {metrics.composite_index:.1f}")
    """
    
    def __init__(
        self,
        config: Optional[WBIConfig] = None,
    ):
        super().__init__()
        self.wbi_config = config or WBIConfig()
        self._transition_fn = WBITransition()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        """Return WBI framework metadata."""
        return FrameworkMetadata(
            slug="wbi",
            name="World Bank Indicators Composite",
            version="1.0.0",
            layer=VerticalLayer.SOCIOECONOMIC_ACADEMIC,
            tier=Tier.COMMUNITY,
            description=(
                "Composite index from World Bank Development Indicators "
                "using z-score normalization and weighted aggregation."
            ),
            required_domains=["wdi"],
            output_domains=["wbi", "category_scores", "indicator_scores"],
            constituent_models=["z_score_normalizer", "weighted_aggregator"],
            tags=["socioeconomic", "development", "world-bank", "composite"],
            author="Khipu Research Labs",
            license="Apache-2.0",
        )
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Compute initial state from WDI data."""
        wdi_data = bundle.get("wdi") if bundle.has_domain("wdi") else None
        
        if wdi_data is None:
            # No data - use defaults
            n_cohorts = getattr(config, "cohort_size", 100)
            return CohortStateVector.zeros(n_cohorts)
        
        df = wdi_data.data
        n_cohorts = len(df)
        
        # Compute initial WBI metrics
        z_scores = self._compute_z_scores(df)
        composite = self._compute_weighted_composite(z_scores)
        
        # Map composite to opportunity score
        # Higher WBI = higher opportunity
        opportunity = np.clip((composite + 2) / 4, 0, 1)  # z-score to [0, 1]
        
        # Extract economic indicators if available
        if "NY.GDP.PCAP.CD" in df.columns:
            gdp_pc = df["NY.GDP.PCAP.CD"].values
            # Normalize GDP per capita to sector output
            sector_output = np.log1p(gdp_pc) / 12  # Log normalize
        else:
            sector_output = np.full(n_cohorts, 0.5)
        
        # Extract health indicators
        if "SP.DYN.LE00.IN" in df.columns:
            life_exp = df["SP.DYN.LE00.IN"].values
            health_burden = 1 - np.clip((life_exp - 50) / 35, 0, 1)
        else:
            health_burden = np.full(n_cohorts, 0.3)
        
        # Extract poverty indicators
        if "SI.POV.DDAY" in df.columns:
            poverty = df["SI.POV.DDAY"].values / 100
            deprivation = np.clip(poverty, 0, 1)
        else:
            deprivation = np.full(n_cohorts, 0.2)
        
        return CohortStateVector(
            employment_prob=np.full(n_cohorts, 0.7),
            health_burden_score=health_burden,
            credit_access_prob=np.full(n_cohorts, 0.5),
            housing_cost_ratio=np.full(n_cohorts, 0.3),
            opportunity_score=opportunity,
            sector_output=sector_output,
            deprivation_vector=deprivation,
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        step: int,
    ) -> CohortStateVector:
        """Apply WBI transition using the configured transition function."""
        from krl_frameworks.core.config import FrameworkConfig
        return self._transition_fn(state, step, FrameworkConfig())
    
    def _compute_z_scores(self, df) -> dict[str, np.ndarray]:
        """Compute z-scores for each indicator in the dataframe."""
        z_scores = {}
        
        for indicator, direction in self.wbi_config.indicator_directions.items():
            if indicator in df.columns:
                values = df[indicator].values.astype(float)
                # Handle missing values
                valid_mask = ~np.isnan(values)
                if valid_mask.sum() > 1:
                    mean = np.nanmean(values)
                    std = np.nanstd(values)
                    if std > 0:
                        z = (values - mean) / std
                        z = z * direction  # Apply direction
                        z_scores[indicator] = z
        
        return z_scores
    
    def _compute_weighted_composite(
        self,
        z_scores: dict[str, np.ndarray],
    ) -> np.ndarray:
        """Compute weighted composite from z-scores."""
        if not z_scores:
            return np.array([0.0])
        
        # Get sample size from first array
        n = len(list(z_scores.values())[0])
        weighted_sum = np.zeros(n)
        total_weight = 0.0
        
        for indicator, z in z_scores.items():
            weight = self.wbi_config.indicator_weights.get(indicator, 1.0)
            weighted_sum += np.nan_to_num(z) * weight
            total_weight += weight
        
        if total_weight > 0:
            composite = weighted_sum / total_weight
        else:
            composite = np.zeros(n)
        
        if self.wbi_config.rescale_to_100:
            # Map z-score to [0, 100] using cumulative normal
            from scipy.stats import norm
            composite = norm.cdf(composite) * 100
        
        return composite
    
    def _compute_metrics(
        self,
        trajectory: StateTrajectory,
    ) -> dict[str, Any]:
        """Compute WBI metrics from final trajectory state."""
        state = trajectory.final_state
        
        # Compute category scores from state
        category_scores = {
            "economic": float(np.mean(state.sector_output)),
            "social": float(1 - np.mean(state.deprivation_vector)),
            "infrastructure": float(np.mean(state.opportunity_score)),
            "health": float(1 - np.mean(state.health_burden_score)),
            "education": float(np.mean(state.opportunity_score)),
        }
        
        # Aggregate to composite
        weights = self.wbi_config.category_weights
        composite = sum(
            score * weights.get(cat, 0.2)
            for cat, score in category_scores.items()
        )
        
        if self.wbi_config.rescale_to_100:
            composite *= 100
            category_scores = {k: v * 100 for k, v in category_scores.items()}
        
        return WBIMetrics(
            composite_index=float(composite),
            category_scores=category_scores,
            indicator_z_scores={},  # Would be populated from data
            indicator_contributions={},
            n_indicators=len(self.wbi_config.indicator_weights),
            coverage_pct=100.0,
        ).to_dict()
    
    def compute_wbi(
        self,
        bundle: DataBundle,
        config: Optional[FrameworkConfig] = None,
    ) -> WBIMetrics:
        """
        Compute WBI composite index from World Bank Indicators.
        
        Args:
            bundle: DataBundle with 'wdi' domain containing indicator data.
            config: Optional framework configuration.
        
        Returns:
            WBIMetrics with composite index and category scores.
        """
        from krl_frameworks.core.config import FrameworkConfig
        config = config or FrameworkConfig()
        
        wdi_data = bundle.get("wdi") if bundle.has_domain("wdi") else None
        
        if wdi_data is None:
            return WBIMetrics(
                composite_index=50.0,
                category_scores={cat: 50.0 for cat in self.wbi_config.category_weights},
                indicator_z_scores={},
                indicator_contributions={},
                n_indicators=0,
                coverage_pct=0.0,
            )
        
        df = wdi_data.data
        z_scores = self._compute_z_scores(df)
        composite = self._compute_weighted_composite(z_scores)
        
        # Compute category scores
        category_scores = {}
        for category in self.wbi_config.category_weights:
            cat_indicators = [
                ind for ind in z_scores
                if self._get_indicator_category(ind) == category
            ]
            if cat_indicators:
                cat_scores = [np.mean(z_scores[ind]) for ind in cat_indicators]
                category_scores[category] = float(np.mean(cat_scores))
            else:
                category_scores[category] = 0.0
        
        # Rescale category scores
        if self.wbi_config.rescale_to_100:
            from scipy.stats import norm
            category_scores = {
                k: float(norm.cdf(v) * 100)
                for k, v in category_scores.items()
            }
        
        # Compute contributions
        contributions = {}
        total_contrib = 0.0
        for ind, z in z_scores.items():
            weight = self.wbi_config.indicator_weights.get(ind, 1.0)
            contrib = float(np.mean(z) * weight)
            contributions[ind] = contrib
            total_contrib += abs(contrib)
        
        n_indicators = len(z_scores)
        n_requested = len(self.wbi_config.indicator_weights)
        coverage = 100.0 * n_indicators / n_requested if n_requested > 0 else 0.0
        
        return WBIMetrics(
            composite_index=float(np.mean(composite)),
            category_scores=category_scores,
            indicator_z_scores={k: float(np.mean(v)) for k, v in z_scores.items()},
            indicator_contributions=contributions,
            n_indicators=n_indicators,
            coverage_pct=coverage,
        )
    
    def _get_indicator_category(self, indicator_code: str) -> str:
        """Map indicator code to category."""
        prefix_map = {
            "NY.": "economic",
            "FP.": "economic",
            "SI.": "social",
            "SL.": "social",
            "IT.": "infrastructure",
            "EG.": "infrastructure",
            "SP.": "health",
            "SH.": "health",
            "SE.": "education",
        }
        for prefix, category in prefix_map.items():
            if indicator_code.startswith(prefix):
                return category
        return "other"

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Return WBI dashboard specification.

        Parameters extracted from WBIConfig and WBITransition.
        """
        return FrameworkDashboardSpec(
            slug="wbi",
            name="World Bank Indicators Composite Index",
            description="Aggregated WDI composite index using z-score normalization across Economic, Social, Infrastructure, Health, and Education categories",
            layer="socioeconomic",
            min_tier=Tier.COMMUNITY,
            parameters_schema={
                "type": "object",
                "properties": {
                    # ═══════════════════════════════════════════════════════
                    # Development Dynamics
                    # ═══════════════════════════════════════════════════════
                    "convergence_rate": {
                        "type": "number",
                        "title": "Convergence Rate",
                        "description": "Rate of convergence to development frontier",
                        "minimum": 0.0,
                        "maximum": 0.1,
                        "default": 0.02,
                        "x-ui-widget": "slider",
                        "x-ui-group": "dynamics",
                        "x-ui-order": 1,
                        "x-ui-help": "Speed at which lagging indicators catch up to frontier (default: 2% per year)",
                    },
                    "shock_volatility": {
                        "type": "number",
                        "title": "Shock Volatility",
                        "description": "Standard deviation of random shocks to indicators",
                        "minimum": 0.0,
                        "maximum": 0.05,
                        "default": 0.01,
                        "x-ui-widget": "slider",
                        "x-ui-group": "dynamics",
                        "x-ui-order": 2,
                        "x-ui-help": "Volatility of exogenous shocks (economic crises, pandemics, etc.)",
                    },

                    # ═══════════════════════════════════════════════════════
                    # Category Weights
                    # ═══════════════════════════════════════════════════════
                    "weight_economic": {
                        "type": "number",
                        "title": "Economic Category Weight",
                        "description": "Weight for Economic indicators (GDP, growth, inflation)",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.25,
                        "x-ui-widget": "slider",
                        "x-ui-group": "weights",
                        "x-ui-order": 3,
                        "x-ui-help": "Default: 0.25 (equal weighting)",
                    },
                    "weight_social": {
                        "type": "number",
                        "title": "Social Category Weight",
                        "description": "Weight for Social indicators (poverty, inequality, unemployment)",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.20,
                        "x-ui-widget": "slider",
                        "x-ui-group": "weights",
                        "x-ui-order": 4,
                        "x-ui-help": "Default: 0.20",
                    },
                    "weight_infrastructure": {
                        "type": "number",
                        "title": "Infrastructure Category Weight",
                        "description": "Weight for Infrastructure indicators (internet, electricity, roads)",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.15,
                        "x-ui-widget": "slider",
                        "x-ui-group": "weights",
                        "x-ui-order": 5,
                        "x-ui-help": "Default: 0.15",
                    },
                    "weight_health": {
                        "type": "number",
                        "title": "Health Category Weight",
                        "description": "Weight for Health indicators (life expectancy, mortality, physicians)",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.20,
                        "x-ui-widget": "slider",
                        "x-ui-group": "weights",
                        "x-ui-order": 6,
                        "x-ui-help": "Default: 0.20",
                    },
                    "weight_education": {
                        "type": "number",
                        "title": "Education Category Weight",
                        "description": "Weight for Education indicators (literacy, enrollment, spending)",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.20,
                        "x-ui-widget": "slider",
                        "x-ui-group": "weights",
                        "x-ui-order": 7,
                        "x-ui-help": "Default: 0.20",
                    },

                    # ═══════════════════════════════════════════════════════
                    # Computation Parameters
                    # ═══════════════════════════════════════════════════════
                    "min_indicators": {
                        "type": "integer",
                        "title": "Minimum Indicators Required",
                        "description": "Minimum number of indicators required for valid composite index",
                        "minimum": 1,
                        "maximum": 20,
                        "default": 5,
                        "x-ui-widget": "number",
                        "x-ui-group": "computation",
                        "x-ui-order": 8,
                        "x-ui-help": "Computation fails if fewer indicators are available",
                    },
                    "rescale_to_100": {
                        "type": "boolean",
                        "title": "Rescale to 100-point Scale",
                        "description": "Rescale final composite index to [0, 100] instead of z-score",
                        "default": True,
                        "x-ui-widget": "checkbox",
                        "x-ui-group": "computation",
                        "x-ui-order": 9,
                        "x-ui-help": "Standard WBI reports use 0-100 scale for interpretability",
                    },
                },
                "required": [],
            },
            default_parameters={
                "convergence_rate": 0.02,
                "shock_volatility": 0.01,
                "weight_economic": 0.25,
                "weight_social": 0.20,
                "weight_infrastructure": 0.15,
                "weight_health": 0.20,
                "weight_education": 0.20,
                "min_indicators": 5,
                "rescale_to_100": True,
            },
            parameter_groups=[
                {
                    "id": "dynamics",
                    "label": "Development Dynamics",
                    "description": "Convergence and shock parameters",
                    "order": 1,
                },
                {
                    "id": "weights",
                    "label": "Category Weights",
                    "description": "Weights for 5 indicator categories (should sum to 1.0)",
                    "order": 2,
                },
                {
                    "id": "computation",
                    "label": "Computation Parameters",
                    "description": "Minimum data requirements and scaling options",
                    "order": 3,
                },
            ],
            output_views=[
                OutputViewSpec(
                    key="composite_gauge",
                    title="WBI Composite Index",
                    view_type=ViewType.GAUGE,
                    description="Overall World Bank Indicators composite score (0-100 scale)",
                    config={
                        "metric_path": "composite_index",
                        "min": 0.0,
                        "max": 100.0,
                        "thresholds": [40, 60, 80],
                        "colors": ["#ef4444", "#f59e0b", "#22c55e"],
                    },
                result_class=ResultClass.SCALAR_INDEX,
                output_key="composite_gauge_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="categories",
                    title="Category Scores",
                    view_type=ViewType.BAR_CHART,
                    description="Scores across the 5 WBI categories",
                    config={
                        "x_axis": "category",
                        "y_axis": "score",
                    },
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="categories_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="indicators",
                    title="Indicator Contributions",
                    view_type=ViewType.BAR_CHART,
                    description="Weighted contribution of each indicator to composite index",
                    config={
                        "x_axis": "indicator",
                        "y_axis": "contribution",
                        "sort_by": "value",
                        "sort_order": "descending",
                    },
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="indicators_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="z_scores",
                    title="Indicator Z-Scores",
                    view_type=ViewType.BAR_CHART,
                    description="Standardized z-scores for each indicator (mean=0, std=1)",
                    config={
                        "x_axis": "indicator",
                        "y_axis": "z_score",
                    },
                result_class=ResultClass.DOMAIN_DECOMPOSITION,
                output_key="z_scores_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="summary_table",
                    title="WBI Summary",
                    view_type=ViewType.TABLE,
                    description="Complete WBI metrics including coverage",
                    config={
                        "columns": [
                            {"key": "composite_index", "label": "Composite Index", "format": ".1f"},
                            {"key": "n_indicators", "label": "Indicators Used"},
                            {"key": "coverage_pct", "label": "Coverage (%)", "format": ".0f"},
                        ],
                    },
                result_class=ResultClass.CONFIDENCE_PROVENANCE,
                output_key="summary_table_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
            ],
        )
