# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - GAO GPRA Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Government Accountability Office - GPRA Analysis Framework.

Implements GAO's framework for analyzing agency performance under the
Government Performance and Results Act (GPRA) and the GPRA Modernization
Act of 2010, including:

- Strategic goal alignment assessment
- Performance measure quality evaluation
- Cross-agency priority (CAP) goal tracking
- Evidence-building capacity analysis

References:
    - GAO-21-104660: Managing for Results
    - GPRA Modernization Act of 2010 (P.L. 111-352)
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
from krl_frameworks.core.state import StateTrajectory
from krl_frameworks.simulation import TransitionFunction
from krl_frameworks.core.dashboard_spec import (
    FrameworkDashboardSpec,
    OutputViewSpec,
    ParameterGroupSpec,
    ViewType,
    ResultClass,
    TemporalSemantics,
)


# ════════════════════════════════════════════════════════════════════════════════
# GPRA-Specific Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class MeasureQuality(Enum):
    """Performance measure quality ratings."""
    HIGH = "High"
    MODERATE = "Moderate"
    LOW = "Low"
    INSUFFICIENT = "Insufficient Data"


class GoalStatus(Enum):
    """Strategic goal achievement status."""
    MET = "Met"
    NOT_MET = "Not Met"
    TRENDING_MET = "Trending Toward Met"
    NO_DATA = "No Data Available"


@dataclass
class GPRAConfig:
    """Configuration for GPRA analysis."""
    
    # Assessment dimensions
    assess_strategic_alignment: bool = True
    assess_measure_quality: bool = True
    assess_evidence_capacity: bool = True
    assess_cap_goals: bool = True
    
    # Quality thresholds
    reliability_threshold: float = 0.80
    validity_threshold: float = 0.75
    timeliness_threshold_days: int = 90
    
    # Target achievement
    achievement_threshold: float = 0.90  # 90% of target = met


@dataclass
class PerformanceMeasure:
    """Individual GPRA performance measure."""
    
    measure_id: str = ""
    name: str = ""
    goal_id: str = ""
    
    # Values
    target: float = 0.0
    actual: float = 0.0
    prior_year: float = 0.0
    
    # Quality attributes
    is_outcome: bool = False
    is_quantifiable: bool = True
    has_baseline: bool = True
    has_annual_target: bool = True
    
    # Status
    status: GoalStatus = GoalStatus.NO_DATA
    quality: MeasureQuality = MeasureQuality.INSUFFICIENT
    
    @property
    def achievement_rate(self) -> float:
        """Calculate target achievement rate."""
        if self.target == 0:
            return 0.0
        return self.actual / self.target


@dataclass
class GPRAScore:
    """GPRA analysis scores."""
    
    # Dimension scores (0-100)
    strategic_alignment_score: float = 0.0
    measure_quality_score: float = 0.0
    evidence_capacity_score: float = 0.0
    cap_goal_score: float = 0.0
    
    # Overall score
    overall_score: float = 0.0
    
    # Measure-level results
    measures_assessed: int = 0
    measures_met: int = 0
    outcome_measures_count: int = 0
    
    # Quality breakdown
    high_quality_measures: int = 0
    moderate_quality_measures: int = 0
    low_quality_measures: int = 0


@dataclass
class GAOGpraMetrics:
    """Comprehensive GAO GPRA analysis metrics."""
    
    # Score
    gpra_score: GPRAScore = field(default_factory=GPRAScore)
    
    # Strategic plan assessment
    mission_clarity: float = 0.0
    goal_hierarchy_complete: bool = False
    stakeholder_engagement: str = ""
    
    # Performance measures
    measures: list[PerformanceMeasure] = field(default_factory=list)
    
    # Evidence building
    learning_agenda_exists: bool = False
    evaluation_capacity_score: float = 0.0
    data_governance_score: float = 0.0
    
    # Recommendations
    improvement_areas: list[str] = field(default_factory=list)
    best_practices: list[str] = field(default_factory=list)


# ════════════════════════════════════════════════════════════════════════════════
# GAO GPRA Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class GAOGpraTransition(TransitionFunction):
    """
    GAO GPRA performance evolution transition.
    
    Models agency performance improvement based on:
    - Strategic planning maturity
    - Performance management capacity
    - Evidence-based decision making
    """
    
    def __init__(self, config: GPRAConfig):
        self.config = config
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        params: Optional[dict[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply GPRA-based performance transition."""
        params = params or {}
        
        # Performance improvement factors
        planning_maturity = params.get("planning_maturity", 0.5)
        mgmt_capacity = params.get("management_capacity", 0.5)
        evidence_use = params.get("evidence_use", 0.3)
        
        # Calculate performance growth
        base_growth = 0.02  # 2% baseline improvement
        planning_effect = 0.03 * planning_maturity
        capacity_effect = 0.02 * mgmt_capacity
        evidence_effect = 0.04 * evidence_use
        
        total_growth = base_growth + planning_effect + capacity_effect + evidence_effect
        
        # Update opportunity score (performance achievement)
        new_opportunity = np.clip(
            state.opportunity_score * (1 + total_growth),
            0.0, 1.0
        )
        
        # Update credit access (resource effectiveness)
        resource_effect = 0.01 * (planning_maturity + mgmt_capacity)
        new_credit = np.clip(
            state.credit_access_prob * (1 + resource_effect),
            0.0, 1.0
        )
        
        # Sector output grows with performance
        new_sector_output = state.sector_output * (1 + total_growth * 0.5)
        
        return CohortStateVector(
            employment_prob=state.employment_prob,
            health_burden_score=state.health_burden_score,
            credit_access_prob=new_credit,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=new_opportunity,
            sector_output=new_sector_output,
            deprivation_vector=state.deprivation_vector,
            step=t + 1,
        )


# ════════════════════════════════════════════════════════════════════════════════
# GAO GPRA Framework
# ════════════════════════════════════════════════════════════════════════════════


class GAOGpraFramework(BaseMetaFramework):
    """
    Government Accountability Office GPRA Analysis Framework.
    
    Implements GAO's methodology for evaluating agency performance
    management under GPRA and the GPRA Modernization Act, covering:
    
    1. Strategic Plan Assessment: Goal clarity, alignment, stakeholder input
    2. Performance Measure Quality: Outcome focus, reliability, validity
    3. Evidence-Building Capacity: Learning agenda, evaluation, data governance
    4. Cross-Agency Priority Goals: CAP goal contribution and coordination
    
    Tier: PROFESSIONAL (government analysis requires validated data)
    
    Example:
        >>> gao = GAOGpraFramework()
        >>> bundle = DataBundle.from_dataframes({"strategic_plan": plan_df, "measures": measures_df})
        >>> metrics = gao.analyze_agency(bundle)
        >>> print(f"GPRA Score: {metrics.gpra_score.overall_score:.1f}")
    """
    
    METADATA = FrameworkMetadata(
        slug="gao_gpra",
        name="GAO GPRA Analysis Framework",
        version="1.0.0",
        layer=VerticalLayer.GOVERNMENT_POLICY,
        tier=Tier.PROFESSIONAL,
        description="GAO methodology for GPRA compliance and performance assessment",
        required_domains=["strategic_plan", "measures"],
        output_domains=["gpra_compliance", "performance_assessment"],
        constituent_models=["goal_analyzer", "measure_validator", "evidence_assessor", "cap_evaluator"],
        tags=["government", "gao", "gpra", "performance", "compliance"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self, config: Optional[GPRAConfig] = None):
        super().__init__()
        self.gpra_config = config or GPRAConfig()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        return cls.METADATA
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Compute initial state from strategic plan and measures data."""
        plan_data = bundle.get("strategic_plan")
        measures_data = bundle.get("measures")
        
        plan_df = plan_data.data
        measures_df = measures_data.data
        
        n_cohorts = len(measures_df) if len(measures_df) > 0 else len(plan_df)
        
        # Extract goal achievement rates
        if "achievement_rate" in measures_df.columns:
            achievement = measures_df["achievement_rate"].values[:n_cohorts]
        else:
            achievement = np.full(n_cohorts, 0.5)
        
        # Extract measure quality scores
        if "quality_score" in measures_df.columns:
            quality = measures_df["quality_score"].values[:n_cohorts] / 100
        else:
            quality = np.full(n_cohorts, 0.6)
        
        return CohortStateVector(
            employment_prob=np.full(n_cohorts, 0.9),
            health_burden_score=np.full(n_cohorts, 0.1),
            credit_access_prob=np.clip(quality, 0, 1),
            housing_cost_ratio=np.full(n_cohorts, 0.3),
            opportunity_score=np.clip(achievement, 0, 1),
            sector_output=np.full((n_cohorts, 10), 1e4),
            deprivation_vector=np.zeros((n_cohorts, 6)),
            step=0,
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Apply GPRA transition function."""
        transition = GAOGpraTransition(self.gpra_config)
        return transition(state, t, config)
    
    def _compute_metrics(
        self,
        trajectory: StateTrajectory,
    ) -> GAOGpraMetrics:
        """Compute GPRA metrics from simulation trajectory."""
        metrics = GAOGpraMetrics()
        
        if len(trajectory) < 1:
            return metrics
        
        final_state = trajectory.final_state
        
        # Calculate GPRA scores
        score = GPRAScore()
        
        # Strategic alignment from opportunity scores
        score.strategic_alignment_score = float(final_state.opportunity_score.mean() * 100)
        
        # Measure quality from credit access
        score.measure_quality_score = float(final_state.credit_access_prob.mean() * 100)
        
        # Evidence capacity (derived)
        score.evidence_capacity_score = (score.strategic_alignment_score + score.measure_quality_score) / 2
        
        # CAP goal score
        score.cap_goal_score = min(score.strategic_alignment_score * 1.1, 100)
        
        # Overall
        score.overall_score = (
            score.strategic_alignment_score * 0.35 +
            score.measure_quality_score * 0.30 +
            score.evidence_capacity_score * 0.20 +
            score.cap_goal_score * 0.15
        )
        
        # Count measures
        score.measures_assessed = len(final_state.opportunity_score)
        score.measures_met = int(np.sum(final_state.opportunity_score >= self.gpra_config.achievement_threshold))
        score.outcome_measures_count = int(score.measures_assessed * 0.4)  # Estimate
        
        # Quality breakdown
        score.high_quality_measures = int(np.sum(final_state.credit_access_prob >= 0.8))
        score.moderate_quality_measures = int(np.sum(
            (final_state.credit_access_prob >= 0.5) & (final_state.credit_access_prob < 0.8)
        ))
        score.low_quality_measures = int(np.sum(final_state.credit_access_prob < 0.5))
        
        metrics.gpra_score = score
        
        # Evidence building assessment
        metrics.learning_agenda_exists = score.evidence_capacity_score >= 50
        metrics.evaluation_capacity_score = score.evidence_capacity_score * 0.8
        metrics.data_governance_score = score.measure_quality_score * 0.7
        
        # Generate recommendations
        if score.strategic_alignment_score < 70:
            metrics.improvement_areas.append("Strengthen goal-measure alignment")
        if score.measure_quality_score < 70:
            metrics.improvement_areas.append("Improve outcome measure development")
        if score.evidence_capacity_score < 60:
            metrics.improvement_areas.append("Build evaluation capacity")
        
        if score.overall_score >= 80:
            metrics.best_practices.append("Strong performance management framework")
        
        return metrics

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return GAO GPRA dashboard specification."""
        return FrameworkDashboardSpec(
            slug="gao_gpra",
            name="GAO GPRA Analysis Framework",
            description=(
                "GAO methodology for GPRA compliance and performance assessment "
                "under the Government Performance and Results Modernization Act."
            ),
            layer="government",
            parameters_schema={
                "type": "object",
                "properties": {
                    "strategic_goals": {
                        "type": "array",
                        "title": "Strategic Goals",
                        "items": {
                            "type": "string",
                        },
                        "default": [],
                        "x-ui-widget": "multiselect",
                        "x-ui-group": "goals",
                    },
                    "performance_measures": {
                        "type": "array",
                        "title": "Performance Measures",
                        "items": {
                            "type": "string",
                            "enum": ["outcome", "output", "efficiency", "customer_service"],
                        },
                        "default": ["outcome", "output"],
                        "x-ui-widget": "multiselect",
                        "x-ui-group": "measures",
                    },
                    "fiscal_year": {
                        "type": "integer",
                        "title": "Fiscal Year",
                        "minimum": 2020,
                        "maximum": 2030,
                        "default": 2024,
                        "x-ui-widget": "slider",
                        "x-ui-group": "time",
                    },
                },
            },
            default_parameters={
                "strategic_goals": [],
                "performance_measures": ["outcome", "output"],
                "fiscal_year": 2024,
            },
            parameter_groups=[
                ParameterGroupSpec(key="goals", title="Strategic Goals", parameters=["strategic_goals"]),
                ParameterGroupSpec(key="measures", title="Measures", parameters=["performance_measures"]),
                ParameterGroupSpec(key="time", title="Time Period", parameters=["fiscal_year"]),
            ],
            required_domains=["strategic_plan", "measures"],
            min_tier=Tier.TEAM,
            output_views=[
                OutputViewSpec(
                    key="goal_achievement",
                    title="Goal Achievement",
                    view_type=ViewType.GAUGE,
                    config={"min": 0, "max": 100, "thresholds": [50, 80], "format": ".0f"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="goal_achievement_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="performance_trends",
                    title="Performance Trends",
                    view_type=ViewType.LINE_CHART,
                    config={"x_field": "fiscal_year", "y_field": "score", "color_by": "measure_type"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="performance_trends_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="audit_findings",
                    title="Audit Findings",
                    view_type=ViewType.TABLE,
                    config={"columns": ["finding_id", "category", "severity", "recommendation", "status"]},
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="audit_findings_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def analyze_agency(
        self,
        bundle: DataBundle,
        config: Optional[FrameworkConfig] = None,
    ) -> GAOGpraMetrics:
        """
        Analyze agency GPRA compliance and performance.
        
        Args:
            bundle: DataBundle with strategic_plan and measures data
            config: Optional framework configuration
        
        Returns:
            GAOGpraMetrics with comprehensive analysis results
        """
        config = config or FrameworkConfig()
        
        initial_state = self._compute_initial_state(bundle, config)
        trajectory = StateTrajectory(states=[initial_state])
        
        # Simulate current period
        next_state = self._transition(initial_state, 0, config)
        trajectory.append(next_state)
        
        return self._compute_metrics(trajectory)
    
    @requires_tier(Tier.ENTERPRISE)
    def assess_measure_quality(
        self,
        measures_df: pd.DataFrame,
    ) -> list[PerformanceMeasure]:
        """
        Assess quality of individual performance measures.
        
        Args:
            measures_df: DataFrame with measure details
        
        Returns:
            List of PerformanceMeasure objects with quality ratings
        """
        measures = []
        
        for _, row in measures_df.iterrows():
            measure = PerformanceMeasure(
                measure_id=str(row.get("measure_id", "")),
                name=str(row.get("name", "")),
                goal_id=str(row.get("goal_id", "")),
                target=float(row.get("target", 0)),
                actual=float(row.get("actual", 0)),
                prior_year=float(row.get("prior_year", 0)),
                is_outcome=bool(row.get("is_outcome", False)),
                is_quantifiable=bool(row.get("is_quantifiable", True)),
                has_baseline=bool(row.get("has_baseline", True)),
                has_annual_target=bool(row.get("has_annual_target", True)),
            )
            
            # Determine status
            if measure.target > 0:
                if measure.achievement_rate >= self.gpra_config.achievement_threshold:
                    measure.status = GoalStatus.MET
                elif measure.achievement_rate >= 0.8:
                    measure.status = GoalStatus.TRENDING_MET
                else:
                    measure.status = GoalStatus.NOT_MET
            
            # Determine quality
            quality_factors = [
                measure.is_outcome,
                measure.is_quantifiable,
                measure.has_baseline,
                measure.has_annual_target,
            ]
            quality_score = sum(quality_factors) / len(quality_factors)
            
            if quality_score >= 0.9:
                measure.quality = MeasureQuality.HIGH
            elif quality_score >= 0.7:
                measure.quality = MeasureQuality.MODERATE
            elif quality_score >= 0.5:
                measure.quality = MeasureQuality.LOW
            else:
                measure.quality = MeasureQuality.INSUFFICIENT
            
            measures.append(measure)
        
        return measures


# ════════════════════════════════════════════════════════════════════════════════
# Exports
# ════════════════════════════════════════════════════════════════════════════════

__all__ = [
    "GAOGpraFramework",
    "GPRAConfig",
    "GPRAScore",
    "GAOGpraMetrics",
    "PerformanceMeasure",
    "MeasureQuality",
    "GoalStatus",
    "GAOGpraTransition",
]
