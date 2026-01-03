# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Cultural Impact Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Cultural Impact Assessment Framework.

Measures the multidimensional impact of cultural interventions:
- Heritage preservation and revitalization
- Community cultural engagement
- Artistic production and quality
- Cultural identity and cohesion
- Intergenerational transmission

References:
    - UNESCO Culture for Development Indicators
    - Cultural Vitality Index methodologies
    - Arts Impact studies (NEA, various)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import numpy as np
import pandas as pd

from krl_frameworks.core import (
    BaseMetaFramework,
    CohortStateVector,
    DataBundle,
    FrameworkConfig,
    FrameworkMetadata,
    Tier,
    VerticalLayer,
    requires_tier,
)
from krl_frameworks.core.dashboard_spec import (
    FrameworkDashboardSpec,
    OutputViewSpec,
    ParameterGroupSpec,
    ViewType,
    ResultClass,
    TemporalSemantics,
)
from krl_frameworks.core.state import StateTrajectory
from krl_frameworks.simulation import TransitionFunction


# ════════════════════════════════════════════════════════════════════════════════
# Cultural Impact Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class CulturalDimension(Enum):
    """Dimensions of cultural impact."""
    HERITAGE = "Heritage Preservation"
    IDENTITY = "Cultural Identity"
    PARTICIPATION = "Cultural Participation"
    DIVERSITY = "Cultural Diversity"
    CREATIVITY = "Creative Expression"
    TRANSMISSION = "Intergenerational Transmission"
    COHESION = "Social Cohesion"


class ImpactLevel(Enum):
    """Level of cultural impact."""
    TRANSFORMATIVE = "Transformative"
    SIGNIFICANT = "Significant"
    MODERATE = "Moderate"
    MINOR = "Minor"
    NEGLIGIBLE = "Negligible"


@dataclass
class CulturalImpactConfig:
    """Configuration for cultural impact assessment."""
    
    # Assessment scope
    dimensions: list[CulturalDimension] = field(default_factory=lambda: list(CulturalDimension))
    
    # Weighting (by dimension)
    dimension_weights: dict[CulturalDimension, float] = field(default_factory=lambda: {
        CulturalDimension.HERITAGE: 0.15,
        CulturalDimension.IDENTITY: 0.15,
        CulturalDimension.PARTICIPATION: 0.20,
        CulturalDimension.DIVERSITY: 0.15,
        CulturalDimension.CREATIVITY: 0.15,
        CulturalDimension.TRANSMISSION: 0.10,
        CulturalDimension.COHESION: 0.10,
    })
    
    # Assessment parameters
    baseline_period: int = 12  # months
    evaluation_period: int = 24  # months
    
    # Thresholds
    impact_thresholds: dict[ImpactLevel, float] = field(default_factory=lambda: {
        ImpactLevel.TRANSFORMATIVE: 0.8,
        ImpactLevel.SIGNIFICANT: 0.6,
        ImpactLevel.MODERATE: 0.4,
        ImpactLevel.MINOR: 0.2,
        ImpactLevel.NEGLIGIBLE: 0.0,
    })


@dataclass
class ImpactScore:
    """Score for a single cultural dimension."""
    
    dimension: CulturalDimension = CulturalDimension.HERITAGE
    
    # Scores (0-1 scale)
    baseline_score: float = 0.0
    current_score: float = 0.0
    change_score: float = 0.0
    
    # Normalized impact
    impact_magnitude: float = 0.0
    impact_level: ImpactLevel = ImpactLevel.NEGLIGIBLE
    
    # Confidence
    confidence: float = 0.0
    sample_size: int = 0


@dataclass
class CommunityMetrics:
    """Community-level cultural metrics."""
    
    # Engagement
    participation_rate: float = 0.0  # % of population
    event_attendance: int = 0
    volunteer_hours: int = 0
    
    # Infrastructure
    cultural_venues: int = 0
    heritage_sites: int = 0
    public_art_installations: int = 0
    
    # Organizations
    cultural_organizations: int = 0
    artists_per_capita: float = 0.0
    cultural_funding_per_capita: float = 0.0


@dataclass
class CulturalImpactMetrics:
    """Comprehensive cultural impact metrics."""
    
    # Dimension scores
    dimension_scores: dict[CulturalDimension, ImpactScore] = field(default_factory=dict)
    
    # Aggregate
    composite_impact_score: float = 0.0
    overall_impact_level: ImpactLevel = ImpactLevel.NEGLIGIBLE
    
    # Community metrics
    community: CommunityMetrics = field(default_factory=CommunityMetrics)
    
    # Trends
    trajectory: str = ""  # "improving", "stable", "declining"
    sustainability_score: float = 0.0


# ════════════════════════════════════════════════════════════════════════════════
# Cultural Impact Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class CulturalTransition(TransitionFunction):
    """
    Cultural impact transition function.
    
    Models the evolution of cultural engagement and impact.
    """
    
    def __init__(self, config: CulturalImpactConfig):
        self.config = config
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        params: Optional[dict[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply cultural transition."""
        params = params or {}
        
        # Cultural interventions improve engagement
        intervention_effect = params.get("intervention_intensity", 0.1)
        
        # Community engagement increases (opportunity score)
        engagement_growth = 0.01 * intervention_effect
        new_opportunity = np.clip(
            state.opportunity_score + engagement_growth,
            0.0, 1.0
        )
        
        # Cultural health improves (reduces "burden")
        wellbeing_effect = intervention_effect * 0.05
        new_health_burden = np.clip(
            state.health_burden_score - wellbeing_effect,
            0.0, 1.0
        )
        
        # Social cohesion strengthens
        cohesion_effect = intervention_effect * 0.03
        new_employment = np.clip(
            state.employment_prob + cohesion_effect,
            0.0, 1.0
        )
        
        # Cultural economy effects
        economy_growth = intervention_effect * 0.02
        new_output = state.sector_output * (1 + economy_growth)
        
        return CohortStateVector(
            employment_prob=new_employment,
            health_burden_score=new_health_burden,
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=new_opportunity,
            sector_output=new_output,
            deprivation_vector=state.deprivation_vector,
            step=t + 1,
        )


# ════════════════════════════════════════════════════════════════════════════════
# Cultural Impact Framework
# ════════════════════════════════════════════════════════════════════════════════


class CulturalImpactFramework(BaseMetaFramework):
    """
    Cultural Impact Assessment Framework.
    
    Measures multidimensional cultural impacts:
    
    1. Heritage: Preservation and revitalization
    2. Identity: Cultural identity strengthening
    3. Participation: Community engagement
    4. Diversity: Cultural diversity and inclusion
    5. Creativity: Artistic production and innovation
    6. Transmission: Intergenerational knowledge transfer
    7. Cohesion: Social bonding through culture
    
    Tier: PROFESSIONAL (cultural sector analysis)
    
    Example:
        >>> framework = CulturalImpactFramework()
        >>> bundle = DataBundle.from_dataframes({
        ...     "survey": cultural_survey_df,
        ...     "events": cultural_events_df
        ... })
        >>> metrics = framework.assess_impact(bundle)
        >>> print(f"Composite Score: {metrics.composite_impact_score:.2f}")
        >>> print(f"Impact Level: {metrics.overall_impact_level.value}")
    """
    
    METADATA = FrameworkMetadata(
        slug="cultural_impact",
        name="Cultural Impact Assessment Framework",
        version="1.0.0",
        layer=VerticalLayer.ARTS_MEDIA_ENTERTAINMENT,
        tier=Tier.PROFESSIONAL,
        description="Multidimensional cultural impact assessment using UNESCO indicators",
        required_domains=["survey"],
        output_domains=["cultural_score", "dimension_analysis", "trend_trajectory"],
        constituent_models=["heritage_scorer", "diversity_analyzer", "vitality_assessor", "sustainability_evaluator"],
        tags=["arts", "cultural_impact", "unesco", "assessment", "heritage"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self, config: Optional[CulturalImpactConfig] = None):
        super().__init__()
        self.cultural_config = config or CulturalImpactConfig()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        return cls.METADATA
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Compute initial state from survey data."""
        survey_data = bundle.get("survey")
        survey_df = survey_data.data
        
        n_cohorts = len(survey_df)
        
        # Extract baseline cultural engagement
        if "engagement_score" in survey_df.columns:
            engagement = survey_df["engagement_score"].values[:n_cohorts] / 100
        else:
            engagement = np.full(n_cohorts, 0.5)
        
        # Extract participation rates
        if "participation" in survey_df.columns:
            participation = survey_df["participation"].values[:n_cohorts]
        else:
            participation = np.full(n_cohorts, 0.3)
        
        return CohortStateVector(
            employment_prob=np.clip(engagement, 0.1, 0.99),  # Engagement proxy
            health_burden_score=np.full(n_cohorts, 0.2),  # Cultural "stress"
            credit_access_prob=participation,  # Participation as proxy
            housing_cost_ratio=np.full(n_cohorts, 0.3),
            opportunity_score=np.clip(engagement, 0, 1),
            sector_output=np.full((n_cohorts, 10), 1000),  # Cultural output
            deprivation_vector=np.zeros((n_cohorts, 6)),
            step=0,
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Apply cultural transition."""
        transition = CulturalTransition(self.cultural_config)
        return transition(state, t, config, {"intervention_intensity": 0.15})
    
    def _compute_metrics(
        self,
        trajectory: StateTrajectory,
    ) -> CulturalImpactMetrics:
        """Compute cultural impact metrics."""
        metrics = CulturalImpactMetrics()
        
        if len(trajectory) < 1:
            return metrics
        
        initial = trajectory.initial_state
        final = trajectory[-1]
        
        # Compute dimension scores
        for dim in self.cultural_config.dimensions:
            score = self._compute_dimension_score(initial, final, dim)
            metrics.dimension_scores[dim] = score
        
        # Composite score
        total_weight = sum(self.cultural_config.dimension_weights.values())
        weighted_sum = sum(
            metrics.dimension_scores.get(dim, ImpactScore()).impact_magnitude 
            * self.cultural_config.dimension_weights.get(dim, 0)
            for dim in self.cultural_config.dimensions
        )
        metrics.composite_impact_score = weighted_sum / total_weight if total_weight > 0 else 0
        
        # Overall impact level
        for level, threshold in sorted(
            self.cultural_config.impact_thresholds.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            if metrics.composite_impact_score >= threshold:
                metrics.overall_impact_level = level
                break
        
        # Trajectory
        if len(trajectory) >= 2:
            first_half_avg = np.mean([s.opportunity_score.mean() for s in trajectory[:len(trajectory)//2]])
            second_half_avg = np.mean([s.opportunity_score.mean() for s in trajectory[len(trajectory)//2:]])
            
            if second_half_avg > first_half_avg * 1.05:
                metrics.trajectory = "improving"
            elif second_half_avg < first_half_avg * 0.95:
                metrics.trajectory = "declining"
            else:
                metrics.trajectory = "stable"
        
        # Sustainability
        metrics.sustainability_score = min(1.0, metrics.composite_impact_score * 1.2)
        
        # Community metrics
        metrics.community = CommunityMetrics(
            participation_rate=float(final.credit_access_prob.mean()),
            event_attendance=int(final.sector_output.sum() / 10),
            cultural_organizations=max(1, int(final.sector_output.sum() / 1000)),
        )
        
        return metrics
    
    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Dashboard specification for cultural impact assessment.
        
        Parameters extracted from CulturalImpactConfig:
        - dimension_weights: Heritage, Identity, Participation, Diversity, Creativity
        - baseline_period: Assessment baseline in months (default 12)
        - evaluation_period: Evaluation window in months (default 24)
        - impact_thresholds: Configurable via aggregation_method
        """
        return FrameworkDashboardSpec(
            slug="cultural_impact",
            name="Cultural Impact Assessment",
            description=(
                "Cultural impact measurement and valuation using UNESCO "
                "Culture for Development indicators and Cultural Vitality Index."
            ),
            layer="arts_media",
            parameters_schema={
                "type": "object",
                "properties": {
                    # Dimension weights (from CulturalImpactConfig.dimension_weights)
                    "heritage_weight": {
                        "type": "number",
                        "title": "Heritage Weight",
                        "description": "Weight for Heritage Preservation dimension",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.15,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.05,
                        "x-ui-group": "weights",
                    },
                    "identity_weight": {
                        "type": "number",
                        "title": "Identity Weight",
                        "description": "Weight for Cultural Identity dimension",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.15,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.05,
                        "x-ui-group": "weights",
                    },
                    "participation_weight": {
                        "type": "number",
                        "title": "Participation Weight",
                        "description": "Weight for Cultural Participation dimension",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.20,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.05,
                        "x-ui-group": "weights",
                    },
                    "diversity_weight": {
                        "type": "number",
                        "title": "Diversity Weight",
                        "description": "Weight for Cultural Diversity dimension",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.15,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.05,
                        "x-ui-group": "weights",
                    },
                    "creativity_weight": {
                        "type": "number",
                        "title": "Creativity Weight",
                        "description": "Weight for Creative Expression dimension",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.15,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.05,
                        "x-ui-group": "weights",
                    },
                    # Time periods (from CulturalImpactConfig)
                    "baseline_period": {
                        "type": "integer",
                        "title": "Baseline Period",
                        "description": "Baseline assessment period in months",
                        "minimum": 3,
                        "maximum": 60,
                        "default": 12,
                        "x-ui-widget": "slider",
                        "x-ui-group": "time_horizon",
                    },
                    "evaluation_period": {
                        "type": "integer",
                        "title": "Evaluation Period",
                        "description": "Evaluation window in months",
                        "minimum": 6,
                        "maximum": 120,
                        "default": 24,
                        "x-ui-widget": "slider",
                        "x-ui-group": "time_horizon",
                    },
                },
                "required": [],
            },
            default_parameters={
                "heritage_weight": 0.15,
                "identity_weight": 0.15,
                "participation_weight": 0.20,
                "diversity_weight": 0.15,
                "creativity_weight": 0.15,
                "baseline_period": 12,
                "evaluation_period": 24,
            },
            min_tier=Tier.PROFESSIONAL,
            parameter_groups=[
                ParameterGroupSpec(
                    key="weights",
                    title="Dimension Weights",
                    description="Configure weights for cultural impact dimensions (should sum to ~1.0)",
                    collapsed_by_default=False,
                    parameters=["heritage_weight", "identity_weight", "participation_weight", 
                               "diversity_weight", "creativity_weight"],
                ),
                ParameterGroupSpec(
                    key="time_horizon",
                    title="Time Horizon",
                    description="Define assessment time periods",
                    collapsed_by_default=True,
                    parameters=["baseline_period", "evaluation_period"],
                ),
            ],
            output_views=[
                OutputViewSpec(
                    key="impact_score",
                    title="Impact Score",
                    view_type=ViewType.GAUGE,
                    description="Composite cultural impact score",
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="impact_score_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="dimension_breakdown",
                    title="Dimension Breakdown",
                    view_type=ViewType.BAR_CHART,
                    description="Impact scores by cultural dimension",
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="dimension_breakdown_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="temporal_trends",
                    title="Temporal Trends",
                    view_type=ViewType.LINE_CHART,
                    description="Cultural impact trajectory over time",
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="temporal_trends_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )
    
    def _compute_dimension_score(
        self,
        initial: CohortStateVector,
        final: CohortStateVector,
        dimension: CulturalDimension,
    ) -> ImpactScore:
        """Compute score for a single dimension."""
        # Map dimensions to state components
        dim_mapping = {
            CulturalDimension.HERITAGE: "opportunity_score",
            CulturalDimension.IDENTITY: "employment_prob",
            CulturalDimension.PARTICIPATION: "credit_access_prob",
            CulturalDimension.DIVERSITY: "opportunity_score",
            CulturalDimension.CREATIVITY: "sector_output",
            CulturalDimension.TRANSMISSION: "employment_prob",
            CulturalDimension.COHESION: "employment_prob",
        }
        
        attr = dim_mapping.get(dimension, "opportunity_score")
        
        initial_val = getattr(initial, attr)
        final_val = getattr(final, attr)
        
        if isinstance(initial_val, np.ndarray):
            baseline = float(initial_val.mean())
            current = float(final_val.mean())
        else:
            baseline = float(initial_val)
            current = float(final_val)
        
        # Normalize to 0-1 if needed
        if attr == "sector_output":
            baseline = min(1.0, baseline / 10000)
            current = min(1.0, current / 10000)
        
        change = current - baseline
        magnitude = abs(change)
        
        # Determine impact level
        impact_level = ImpactLevel.NEGLIGIBLE
        for level, threshold in sorted(
            self.cultural_config.impact_thresholds.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            if magnitude >= threshold / 5:  # Scale for dimension level
                impact_level = level
                break
        
        return ImpactScore(
            dimension=dimension,
            baseline_score=baseline,
            current_score=current,
            change_score=change,
            impact_magnitude=min(1.0, magnitude * 2),
            impact_level=impact_level,
            confidence=0.85,
            sample_size=len(initial.employment_prob),
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def assess_impact(
        self,
        bundle: DataBundle,
        config: Optional[FrameworkConfig] = None,
    ) -> CulturalImpactMetrics:
        """
        Assess cultural impact.
        
        Args:
            bundle: DataBundle with survey data
            config: Optional framework configuration
        
        Returns:
            CulturalImpactMetrics with dimension scores
        """
        config = config or FrameworkConfig()
        
        initial_state = self._compute_initial_state(bundle, config)
        trajectory = StateTrajectory(states=[initial_state])
        
        # Project over evaluation period
        current = initial_state
        periods = self.cultural_config.evaluation_period // 3  # Quarterly
        
        for t in range(periods):
            current = self._transition(current, t, config)
            trajectory.append(current)
        
        return self._compute_metrics(trajectory)
    
    @requires_tier(Tier.TEAM)
    def compare_communities(
        self,
        bundles: list[DataBundle],
        community_names: list[str],
        config: Optional[FrameworkConfig] = None,
    ) -> dict[str, CulturalImpactMetrics]:
        """
        Compare cultural impact across communities.
        
        Args:
            bundles: List of DataBundles, one per community
            community_names: Names for each community
            config: Optional framework configuration
        
        Returns:
            Dictionary of community name -> metrics
        """
        results = {}
        
        for name, bundle in zip(community_names, bundles):
            metrics = self.assess_impact(bundle, config)
            results[name] = metrics
        
        return results


# ════════════════════════════════════════════════════════════════════════════════
# Exports
# ════════════════════════════════════════════════════════════════════════════════

__all__ = [
    "CulturalImpactFramework",
    "CulturalImpactConfig",
    "CulturalImpactMetrics",
    "CulturalDimension",
    "ImpactScore",
    "ImpactLevel",
    "CommunityMetrics",
    "CulturalTransition",
]
