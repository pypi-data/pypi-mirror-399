# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Network Readiness Index (NRI)
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Network Readiness Index (NRI) Framework.

NRI measures the propensity for countries to exploit opportunities
offered by information and communications technology (ICT).

Core Methodology (Portulans Institute / WEF):
    1. Technology pillar: Access, Content, Future Technologies
    2. People pillar: Individuals, Businesses, Governments
    3. Governance pillar: Trust, Regulation, Inclusion
    4. Impact pillar: Economy, Quality of Life, SDG Contribution

Each pillar has sub-pillars with multiple indicators, aggregated
using min-max normalization and arithmetic means.

CBSS Integration:
    - Tracks NRI components per cohort over time
    - Models digital divide closure dynamics
    - Projects technology adoption trajectories

References:
    - Portulans Institute Network Readiness Index (2020-2024)
    - World Economic Forum Global IT Report methodology
    - Dutta, S. & Lanvin, B. "The Network Readiness Index"

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

__all__ = ["NRIFramework", "NRITransition", "NRIMetrics", "NRIConfig"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# NRI Configuration
# ════════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class NRIConfig:
    """
    Configuration for NRI computation.
    
    Attributes:
        pillar_weights: Weights for each of the 4 pillars.
        normalize_to_100: Whether to scale final score to [0, 100].
    """
    
    # Equal weights by default (per NRI methodology)
    pillar_weights: dict[str, float] = field(default_factory=lambda: {
        "technology": 0.25,
        "people": 0.25,
        "governance": 0.25,
        "impact": 0.25,
    })
    
    normalize_to_100: bool = True


# ════════════════════════════════════════════════════════════════════════════════
# NRI Metrics
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class NRIMetrics:
    """
    Container for NRI computation results.
    
    Attributes:
        nri: Overall Network Readiness Index score.
        technology_score: Technology pillar score.
        people_score: People pillar score.
        governance_score: Governance pillar score.
        impact_score: Impact pillar score.
        sub_pillar_scores: Detailed sub-pillar scores.
        classification: Readiness classification.
        digital_divide_index: Gap from frontier (100 - NRI).
    """
    
    nri: float
    technology_score: float
    people_score: float
    governance_score: float
    impact_score: float
    sub_pillar_scores: dict[str, float]
    classification: str
    digital_divide_index: float
    
    @classmethod
    def classify(cls, nri: float) -> str:
        """Classify NRI into readiness tier."""
        if nri >= 70:
            return "High Readiness"
        elif nri >= 50:
            return "Upper-Middle Readiness"
        elif nri >= 35:
            return "Lower-Middle Readiness"
        else:
            return "Low Readiness"
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "nri": self.nri,
            "technology_score": self.technology_score,
            "people_score": self.people_score,
            "governance_score": self.governance_score,
            "impact_score": self.impact_score,
            "sub_pillar_scores": self.sub_pillar_scores,
            "classification": self.classification,
            "digital_divide_index": self.digital_divide_index,
        }


# ════════════════════════════════════════════════════════════════════════════════
# NRI Sub-Pillar Indicators
# ════════════════════════════════════════════════════════════════════════════════

# Technology pillar sub-pillars and their indicators
TECHNOLOGY_INDICATORS = {
    "access": [
        "mobile_subscriptions",  # Mobile cellular subscriptions per 100
        "internet_users",        # Internet users %
        "broadband_subscriptions",  # Fixed broadband per 100
        "4g_coverage",           # 4G population coverage %
    ],
    "content": [
        "digital_content_creation",
        "mobile_app_development",
        "ict_patents",
    ],
    "future_tech": [
        "ai_readiness",
        "iot_adoption",
        "cloud_computing_use",
    ],
}

PEOPLE_INDICATORS = {
    "individuals": [
        "digital_skills",
        "internet_usage_diversity",
        "adult_literacy",
    ],
    "businesses": [
        "business_ict_adoption",
        "firms_with_website",
        "e_commerce_participation",
    ],
    "governments": [
        "egov_services",
        "online_service_index",
        "open_data_availability",
    ],
}

GOVERNANCE_INDICATORS = {
    "trust": [
        "cybersecurity_index",
        "privacy_protection",
        "secure_internet_servers",
    ],
    "regulation": [
        "ict_regulatory_quality",
        "rule_of_law",
        "ease_of_doing_business",
    ],
    "inclusion": [
        "gender_gap_ict",
        "rural_internet_access",
        "affordability",
    ],
}

IMPACT_INDICATORS = {
    "economy": [
        "ict_gdp_contribution",
        "ict_employment",
        "productivity_growth",
    ],
    "quality_of_life": [
        "e_health_adoption",
        "e_education",
        "digital_wellbeing",
    ],
    "sdg_contribution": [
        "tech_sdg_impact",
        "environmental_sustainability",
        "social_inclusion_tech",
    ],
}


# ════════════════════════════════════════════════════════════════════════════════
# NRI Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class NRITransition(TransitionFunction):
    """
    Transition function for NRI cohort state evolution.
    
    Models digital technology adoption dynamics:
    - S-curve adoption patterns
    - Digital divide convergence
    - Technology spillover effects
    """
    
    name = "NRITransition"
    
    def __init__(
        self,
        adoption_rate: float = 0.03,
        convergence_speed: float = 0.02,
        spillover_factor: float = 0.1,
    ):
        self.adoption_rate = adoption_rate
        self.convergence_speed = convergence_speed
        self.spillover_factor = spillover_factor
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply NRI transition with S-curve dynamics."""
        params = params or {}
        
        adoption = params.get("adoption_rate", self.adoption_rate)
        convergence = params.get("convergence_speed", self.convergence_speed)
        spillover = params.get("spillover_factor", self.spillover_factor)
        
        # S-curve technology adoption (logistic growth)
        # opportunity_score represents NRI in normalized form
        current = state.opportunity_score
        
        # Logistic growth toward frontier
        growth = adoption * current * (1 - current)
        
        # Convergence: laggards catch up faster
        gap = 1 - current
        catch_up = convergence * gap
        
        # Spillover from high-connectivity neighbors (mean field)
        mean_level = np.mean(current)
        spillover_effect = spillover * (mean_level - current)
        
        new_opportunity = np.clip(
            current + growth + catch_up + spillover_effect, 0, 1
        )
        
        # Employment benefits from digitalization
        new_employment = np.clip(
            state.employment_prob + adoption * 0.3 * gap, 0, 1
        )
        
        # Credit access improves with digital financial inclusion
        new_credit = np.clip(
            state.credit_access_prob + adoption * 0.4 * gap, 0, 1
        )
        
        return CohortStateVector(
            employment_prob=new_employment,
            health_burden_score=state.health_burden_score * (1 - adoption * 0.1),
            credit_access_prob=new_credit,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=new_opportunity,
            sector_output=state.sector_output * (1 + adoption * 0.5),
            deprivation_vector=state.deprivation_vector * (1 - adoption * 0.2),
        )


# ════════════════════════════════════════════════════════════════════════════════
# NRI Framework
# ════════════════════════════════════════════════════════════════════════════════


class NRIFramework(BaseMetaFramework):
    """
    Network Readiness Index (NRI) Framework.
    
    Computes NRI from technology, people, governance, and impact
    pillar indicators using min-max normalization and weighted
    aggregation.
    
    Example:
        >>> bundle = DataBundle.from_dataframes({
        ...     "ict": ict_df,  # ICT indicators data
        ... })
        >>> nri = NRIFramework()
        >>> metrics = nri.compute_nri(bundle)
        >>> print(f"NRI Score: {metrics.nri:.1f}")
        >>> print(f"Classification: {metrics.classification}")
    """
    
    def __init__(
        self,
        config: Optional[NRIConfig] = None,
    ):
        super().__init__()
        self.nri_config = config or NRIConfig()
        self._transition_fn = NRITransition()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        """Return NRI framework metadata."""
        return FrameworkMetadata(
            slug="nri",
            name="Network Readiness Index",
            version="1.0.0",
            layer=VerticalLayer.SOCIOECONOMIC_ACADEMIC,
            tier=Tier.COMMUNITY,
            description=(
                "Portulans Institute NRI measuring ICT readiness across "
                "technology, people, governance, and impact pillars."
            ),
            required_domains=["ict"],
            output_domains=["nri", "pillar_scores", "sub_pillar_scores"],
            constituent_models=["minmax_normalizer", "pillar_aggregator"],
            tags=["socioeconomic", "digital", "ict", "technology", "readiness"],
            author="Khipu Research Labs",
            license="Apache-2.0",
        )
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Compute initial state from ICT indicators."""
        ict_data = bundle.get("ict") if bundle.has_domain("ict") else None
        
        if ict_data is None:
            n_cohorts = getattr(config, "cohort_size", 100)
            return CohortStateVector.zeros(n_cohorts)
        
        df = ict_data.data
        n_cohorts = len(df)
        
        # Extract key indicators
        if "internet_users" in df.columns:
            internet = df["internet_users"].values / 100  # Normalize to [0, 1]
        else:
            internet = np.full(n_cohorts, 0.5)
        
        if "mobile_subscriptions" in df.columns:
            mobile = np.clip(df["mobile_subscriptions"].values / 150, 0, 1)
        else:
            mobile = np.full(n_cohorts, 0.6)
        
        if "broadband_subscriptions" in df.columns:
            broadband = np.clip(df["broadband_subscriptions"].values / 50, 0, 1)
        else:
            broadband = np.full(n_cohorts, 0.3)
        
        # Composite opportunity score from access indicators
        opportunity = (internet + mobile + broadband) / 3
        
        return CohortStateVector(
            employment_prob=np.full(n_cohorts, 0.7),
            health_burden_score=np.full(n_cohorts, 0.3),
            credit_access_prob=np.clip(opportunity * 0.8, 0, 1),
            housing_cost_ratio=np.full(n_cohorts, 0.3),
            opportunity_score=opportunity,
            sector_output=np.full(n_cohorts, 1.0),
            deprivation_vector=1 - opportunity,
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        step: int,
    ) -> CohortStateVector:
        """Apply NRI transition using the configured transition function."""
        from krl_frameworks.core.config import FrameworkConfig
        return self._transition_fn(state, step, FrameworkConfig())
    
    def _normalize_indicator(
        self,
        values: np.ndarray,
        minimum: Optional[float] = None,
        maximum: Optional[float] = None,
    ) -> np.ndarray:
        """Min-max normalize indicator values to [0, 1]."""
        values = np.asarray(values, dtype=float)
        valid_mask = ~np.isnan(values)
        
        if minimum is None:
            minimum = np.nanmin(values)
        if maximum is None:
            maximum = np.nanmax(values)
        
        if maximum > minimum:
            normalized = (values - minimum) / (maximum - minimum)
        else:
            normalized = np.zeros_like(values)
        
        return np.clip(normalized, 0, 1)
    
    def _compute_pillar_score(
        self,
        df,
        indicators: dict[str, list[str]],
    ) -> tuple[float, dict[str, float]]:
        """Compute pillar score from sub-pillar indicators."""
        sub_pillar_scores = {}
        
        for sub_pillar, indicator_list in indicators.items():
            available = [ind for ind in indicator_list if ind in df.columns]
            if available:
                scores = []
                for ind in available:
                    values = df[ind].values.astype(float)
                    norm = self._normalize_indicator(values)
                    scores.append(np.nanmean(norm))
                sub_pillar_scores[sub_pillar] = float(np.mean(scores))
            else:
                sub_pillar_scores[sub_pillar] = 0.5  # Default
        
        pillar_score = np.mean(list(sub_pillar_scores.values()))
        return float(pillar_score), sub_pillar_scores
    
    def _compute_metrics(
        self,
        trajectory: StateTrajectory,
    ) -> dict[str, Any]:
        """Compute NRI metrics from trajectory."""
        state = trajectory.final_state
        
        # Infer pillar scores from state
        technology_score = float(np.mean(state.opportunity_score))
        people_score = float(np.mean(state.employment_prob))
        governance_score = float(np.mean(state.credit_access_prob))
        impact_score = float(1 - np.mean(state.deprivation_vector))
        
        # Aggregate NRI
        weights = self.nri_config.pillar_weights
        nri = (
            technology_score * weights["technology"] +
            people_score * weights["people"] +
            governance_score * weights["governance"] +
            impact_score * weights["impact"]
        )
        
        if self.nri_config.normalize_to_100:
            nri *= 100
            technology_score *= 100
            people_score *= 100
            governance_score *= 100
            impact_score *= 100
        
        return NRIMetrics(
            nri=nri,
            technology_score=technology_score,
            people_score=people_score,
            governance_score=governance_score,
            impact_score=impact_score,
            sub_pillar_scores={},
            classification=NRIMetrics.classify(nri),
            digital_divide_index=100 - nri if self.nri_config.normalize_to_100 else 1 - nri,
        ).to_dict()
    
    def compute_nri(
        self,
        bundle: DataBundle,
        config: Optional[FrameworkConfig] = None,
    ) -> NRIMetrics:
        """
        Compute NRI from ICT indicator data.
        
        Args:
            bundle: DataBundle with 'ict' domain containing indicators.
            config: Optional framework configuration.
        
        Returns:
            NRIMetrics with NRI score and pillar breakdown.
        """
        from krl_frameworks.core.config import FrameworkConfig
        config = config or FrameworkConfig()
        
        ict_data = bundle.get("ict") if bundle.has_domain("ict") else None
        
        if ict_data is None:
            return NRIMetrics(
                nri=50.0,
                technology_score=50.0,
                people_score=50.0,
                governance_score=50.0,
                impact_score=50.0,
                sub_pillar_scores={},
                classification="Lower-Middle Readiness",
                digital_divide_index=50.0,
            )
        
        df = ict_data.data
        
        # Compute pillar scores
        tech_score, tech_sub = self._compute_pillar_score(df, TECHNOLOGY_INDICATORS)
        people_score, people_sub = self._compute_pillar_score(df, PEOPLE_INDICATORS)
        gov_score, gov_sub = self._compute_pillar_score(df, GOVERNANCE_INDICATORS)
        impact_score, impact_sub = self._compute_pillar_score(df, IMPACT_INDICATORS)
        
        # Merge sub-pillar scores
        sub_pillars = {**tech_sub, **people_sub, **gov_sub, **impact_sub}
        
        # Weighted aggregate
        weights = self.nri_config.pillar_weights
        nri = (
            tech_score * weights["technology"] +
            people_score * weights["people"] +
            gov_score * weights["governance"] +
            impact_score * weights["impact"]
        )
        
        # Scale
        if self.nri_config.normalize_to_100:
            nri *= 100
            tech_score *= 100
            people_score *= 100
            gov_score *= 100
            impact_score *= 100
            sub_pillars = {k: v * 100 for k, v in sub_pillars.items()}
        
        return NRIMetrics(
            nri=float(nri),
            technology_score=float(tech_score),
            people_score=float(people_score),
            governance_score=float(gov_score),
            impact_score=float(impact_score),
            sub_pillar_scores=sub_pillars,
            classification=NRIMetrics.classify(nri),
            digital_divide_index=float(100 - nri) if self.nri_config.normalize_to_100 else float(1 - nri),
        )
    
    def benchmark(
        self,
        bundle: DataBundle,
        reference_country: str = "USA",
    ) -> dict[str, Any]:
        """
        Benchmark NRI against a reference country.
        
        Args:
            bundle: DataBundle with ICT data including reference.
            reference_country: Country code to benchmark against.
        
        Returns:
            Dict with benchmark comparisons.
        """
        metrics = self.compute_nri(bundle)
        
        # Compute gap to reference (simplified)
        ref_nri = 80.0  # Typical for high-income countries
        
        return {
            "nri": metrics.nri,
            "reference_nri": ref_nri,
            "gap": ref_nri - metrics.nri,
            "gap_pct": 100 * (ref_nri - metrics.nri) / ref_nri,
            "years_to_catch_up": (ref_nri - metrics.nri) / 2.0,  # Assuming 2 pts/year
        }

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Return NRI dashboard specification.

        Parameters extracted from NRIConfig and NRITransition.
        """
        return FrameworkDashboardSpec(
            slug="nri",
            name="Network Readiness Index",
            description="Portulans Institute/WEF index measuring ICT readiness across Technology, People, Governance, and Impact pillars",
            layer="socioeconomic",
            min_tier=Tier.COMMUNITY,
            parameters_schema={
                "type": "object",
                "properties": {
                    # ═══════════════════════════════════════════════════════
                    # Technology Adoption Dynamics
                    # ═══════════════════════════════════════════════════════
                    "adoption_rate": {
                        "type": "number",
                        "title": "Technology Adoption Rate",
                        "description": "S-curve logistic growth rate for ICT adoption",
                        "minimum": 0.0,
                        "maximum": 0.1,
                        "default": 0.03,
                        "x-ui-widget": "slider",
                        "x-ui-group": "dynamics",
                        "x-ui-order": 1,
                        "x-ui-help": "Rate of ICT technology adoption following S-curve dynamics (default: 3% per year)",
                    },
                    "convergence_speed": {
                        "type": "number",
                        "title": "Digital Divide Convergence Speed",
                        "description": "Rate at which lagging regions catch up to frontier",
                        "minimum": 0.0,
                        "maximum": 0.1,
                        "default": 0.02,
                        "x-ui-widget": "slider",
                        "x-ui-group": "dynamics",
                        "x-ui-order": 2,
                        "x-ui-help": "Speed of convergence to frontier NRI (catch-up growth)",
                    },
                    "spillover_factor": {
                        "type": "number",
                        "title": "Technology Spillover Factor",
                        "description": "Cross-regional technology diffusion spillover effect",
                        "minimum": 0.0,
                        "maximum": 0.5,
                        "default": 0.1,
                        "x-ui-widget": "slider",
                        "x-ui-group": "dynamics",
                        "x-ui-order": 3,
                        "x-ui-help": "Strength of spillover effects from high-NRI regions to neighbors",
                    },

                    # ═══════════════════════════════════════════════════════
                    # Pillar Weights
                    # ═══════════════════════════════════════════════════════
                    "weight_technology": {
                        "type": "number",
                        "title": "Technology Pillar Weight",
                        "description": "Weight for Technology pillar (Access, Content, Future Tech)",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.25,
                        "x-ui-widget": "slider",
                        "x-ui-group": "weights",
                        "x-ui-order": 4,
                        "x-ui-help": "NRI standard: equal weights (0.25 each)",
                    },
                    "weight_people": {
                        "type": "number",
                        "title": "People Pillar Weight",
                        "description": "Weight for People pillar (Individuals, Businesses, Governments)",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.25,
                        "x-ui-widget": "slider",
                        "x-ui-group": "weights",
                        "x-ui-order": 5,
                        "x-ui-help": "NRI standard: equal weights (0.25 each)",
                    },
                    "weight_governance": {
                        "type": "number",
                        "title": "Governance Pillar Weight",
                        "description": "Weight for Governance pillar (Trust, Regulation, Inclusion)",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.25,
                        "x-ui-widget": "slider",
                        "x-ui-group": "weights",
                        "x-ui-order": 6,
                        "x-ui-help": "NRI standard: equal weights (0.25 each)",
                    },
                    "weight_impact": {
                        "type": "number",
                        "title": "Impact Pillar Weight",
                        "description": "Weight for Impact pillar (Economy, Quality of Life, SDG)",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.25,
                        "x-ui-widget": "slider",
                        "x-ui-group": "weights",
                        "x-ui-order": 7,
                        "x-ui-help": "NRI standard: equal weights (0.25 each)",
                    },

                    # ═══════════════════════════════════════════════════════
                    # Output Configuration
                    # ═══════════════════════════════════════════════════════
                    "normalize_to_100": {
                        "type": "boolean",
                        "title": "Normalize to 100-point Scale",
                        "description": "Scale final NRI score to [0, 100] instead of [0, 1]",
                        "default": True,
                        "x-ui-widget": "checkbox",
                        "x-ui-group": "output",
                        "x-ui-order": 8,
                        "x-ui-help": "Standard NRI reports use 0-100 scale",
                    },
                },
                "required": [],
            },
            default_parameters={
                "adoption_rate": 0.03,
                "convergence_speed": 0.02,
                "spillover_factor": 0.1,
                "weight_technology": 0.25,
                "weight_people": 0.25,
                "weight_governance": 0.25,
                "weight_impact": 0.25,
                "normalize_to_100": True,
            },
            parameter_groups=[
                {
                    "id": "dynamics",
                    "label": "ICT Adoption Dynamics",
                    "description": "Technology diffusion and digital divide convergence parameters",
                    "order": 1,
                },
                {
                    "id": "weights",
                    "label": "Pillar Weights",
                    "description": "Weights for the 4 NRI pillars (must sum to 1.0)",
                    "order": 2,
                },
                {
                    "id": "output",
                    "label": "Output Configuration",
                    "description": "Scaling and formatting options",
                    "order": 3,
                },
            ],
            output_views=[
                OutputViewSpec(
                    key="nri_gauge",
                    title="NRI Score",
                    view_type=ViewType.GAUGE,
                    description="Overall Network Readiness Index (0-100 scale)",
                    config={
                        "metric_path": "nri",
                        "min": 0.0,
                        "max": 100.0,
                        "thresholds": [35, 50, 70],
                        "colors": ["#ef4444", "#f59e0b", "#22c55e"],
                    },
                result_class=ResultClass.SCALAR_INDEX,
                output_key="nri_gauge_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="pillars",
                    title="NRI Pillars",
                    view_type=ViewType.BAR_CHART,
                    description="Scores across Technology, People, Governance, and Impact pillars",
                    config={
                        "x_axis": "pillar",
                        "y_axis": "score",
                    },
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="pillars_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="sub_pillars",
                    title="Sub-Pillar Breakdown",
                    view_type=ViewType.BAR_CHART,
                    description="Detailed scores for all 12 NRI sub-pillars",
                    config={
                        "x_axis": "sub_pillar",
                        "y_axis": "score",
                    },
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="sub_pillars_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="digital_divide",
                    title="Digital Divide Index",
                    view_type=ViewType.GAUGE,
                    description="Gap from frontier (100 - NRI), lower is better",
                    config={
                        "metric_path": "digital_divide_index",
                        "min": 0.0,
                        "max": 100.0,
                        "thresholds": [30, 50, 65],
                        "colors": ["#22c55e", "#f59e0b", "#ef4444"],
                    },
                result_class=ResultClass.SCALAR_INDEX,
                output_key="digital_divide_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="summary_table",
                    title="NRI Summary",
                    view_type=ViewType.TABLE,
                    description="Complete NRI metrics and classification",
                    config={
                        "columns": [
                            {"key": "nri", "label": "NRI Score", "format": ".1f"},
                            {"key": "technology_score", "label": "Technology", "format": ".1f"},
                            {"key": "people_score", "label": "People", "format": ".1f"},
                            {"key": "governance_score", "label": "Governance", "format": ".1f"},
                            {"key": "impact_score", "label": "Impact", "format": ".1f"},
                            {"key": "classification", "label": "Classification"},
                            {"key": "digital_divide_index", "label": "Digital Divide", "format": ".1f"},
                        ],
                    },
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="summary_table_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )
