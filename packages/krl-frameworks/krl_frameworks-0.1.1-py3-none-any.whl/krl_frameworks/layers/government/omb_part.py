# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - OMB PART Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Office of Management and Budget - Program Assessment Rating Tool (PART).

Implements the OMB PART methodology for evaluating federal program
effectiveness, including:
- Program Purpose & Design (20%)
- Strategic Planning (10%)
- Program Management (20%)
- Program Results/Accountability (50%)

Note: While PART was officially discontinued in 2009, its methodology
remains influential for program evaluation and has been adapted into
modern evidence-based policy frameworks.

References:
    - OMB Circular A-11, Part 6: The Federal Performance Framework
    - Government Performance and Results Modernization Act (GPRAMA)
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
# PART-Specific Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class ProgramRating(Enum):
    """PART program rating categories."""
    EFFECTIVE = "Effective"
    MODERATELY_EFFECTIVE = "Moderately Effective"
    ADEQUATE = "Adequate"
    INEFFECTIVE = "Ineffective"
    RESULTS_NOT_DEMONSTRATED = "Results Not Demonstrated"


@dataclass
class PARTConfig:
    """Configuration for PART assessment."""
    
    # Section weights (must sum to 1.0)
    purpose_design_weight: float = 0.20
    strategic_planning_weight: float = 0.10
    management_weight: float = 0.20
    results_weight: float = 0.50
    
    # Scoring thresholds
    effective_threshold: float = 85.0
    moderately_effective_threshold: float = 70.0
    adequate_threshold: float = 50.0
    
    # Assessment options
    require_outcome_measures: bool = True
    include_efficiency_measures: bool = True
    use_comparison_group: bool = False


@dataclass
class PARTScore:
    """PART assessment section scores."""
    
    # Section scores (0-100)
    purpose_design_score: float = 0.0
    strategic_planning_score: float = 0.0
    management_score: float = 0.0
    results_score: float = 0.0
    
    # Weighted total
    total_score: float = 0.0
    
    # Rating
    rating: ProgramRating = ProgramRating.RESULTS_NOT_DEMONSTRATED
    
    # Question-level detail
    question_responses: dict[str, bool] = field(default_factory=dict)
    question_explanations: dict[str, str] = field(default_factory=dict)
    
    # Improvement plan
    improvement_actions: list[str] = field(default_factory=list)
    
    @classmethod
    def from_scores(
        cls,
        purpose: float,
        planning: float,
        management: float,
        results: float,
        config: Optional[PARTConfig] = None,
    ) -> "PARTScore":
        """Create PARTScore from section scores."""
        config = config or PARTConfig()
        
        total = (
            purpose * config.purpose_design_weight +
            planning * config.strategic_planning_weight +
            management * config.management_weight +
            results * config.results_weight
        )
        
        # Determine rating
        if total >= config.effective_threshold:
            rating = ProgramRating.EFFECTIVE
        elif total >= config.moderately_effective_threshold:
            rating = ProgramRating.MODERATELY_EFFECTIVE
        elif total >= config.adequate_threshold:
            rating = ProgramRating.ADEQUATE
        elif results > 0:
            rating = ProgramRating.INEFFECTIVE
        else:
            rating = ProgramRating.RESULTS_NOT_DEMONSTRATED
        
        return cls(
            purpose_design_score=purpose,
            strategic_planning_score=planning,
            management_score=management,
            results_score=results,
            total_score=total,
            rating=rating,
        )


@dataclass
class OMBPartMetrics:
    """Comprehensive OMB PART metrics."""
    
    # Overall score
    part_score: PARTScore = field(default_factory=PARTScore)
    
    # Efficiency metrics
    cost_per_outcome: float = 0.0
    efficiency_trend: str = "stable"  # improving, stable, declining
    
    # Outcome achievement
    targets_met: int = 0
    targets_total: int = 0
    target_achievement_rate: float = 0.0
    
    # Comparison metrics
    peer_program_ranking: Optional[int] = None
    percentile_rank: Optional[float] = None
    
    # Recommendations
    recommendations: list[str] = field(default_factory=list)
    funding_recommendation: str = ""


# ════════════════════════════════════════════════════════════════════════════════
# OMB PART Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class OMBPartTransition(TransitionFunction):
    """
    OMB PART transition function.
    
    Models program performance evolution based on:
    - Management improvements
    - Resource allocation changes
    - Policy interventions
    """
    
    def __init__(self, config: PARTConfig):
        self.config = config
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        params: Optional[dict[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply PART-based performance transition."""
        params = params or {}
        
        # Management improvement rate
        mgmt_improvement = params.get("management_improvement", 0.02)
        resource_change = params.get("resource_change", 0.0)
        intervention_effect = params.get("intervention_effect", 0.0)
        
        # Update employment (program employment outcomes)
        employment_effect = (
            0.1 * mgmt_improvement +
            0.3 * resource_change +
            0.5 * intervention_effect
        )
        new_employment = np.clip(
            state.employment_prob * (1 + employment_effect),
            0.0, 1.0
        )
        
        # Update opportunity score (program access/quality)
        opportunity_effect = (
            0.2 * mgmt_improvement +
            0.2 * resource_change +
            0.3 * intervention_effect
        )
        new_opportunity = np.clip(
            state.opportunity_score * (1 + opportunity_effect),
            0.0, 1.0
        )
        
        # Update health burden (for health programs)
        health_effect = -0.1 * intervention_effect  # Negative = improvement
        new_health = np.clip(
            state.health_burden_score * (1 + health_effect),
            0.0, 1.0
        )
        
        # Sector output reflects program outputs
        output_growth = 1.0 + mgmt_improvement + 0.5 * resource_change
        new_sector_output = state.sector_output * output_growth
        
        return CohortStateVector(
            employment_prob=new_employment,
            health_burden_score=new_health,
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=new_opportunity,
            sector_output=new_sector_output,
            deprivation_vector=state.deprivation_vector,
            step=t + 1,
        )


# ════════════════════════════════════════════════════════════════════════════════
# OMB PART Framework
# ════════════════════════════════════════════════════════════════════════════════


class OMBPartFramework(BaseMetaFramework):
    """
    Office of Management and Budget PART Framework.
    
    Implements a modernized version of the PART methodology for
    evaluating federal program effectiveness across four dimensions:
    
    1. Program Purpose & Design (20%): Clear purpose, addresses problem
    2. Strategic Planning (10%): Annual and long-term performance measures
    3. Program Management (20%): Financial management, program improvement
    4. Program Results/Accountability (50%): Achieving outcomes, efficiency
    
    Tier: PROFESSIONAL (evaluation requires validated data)
    
    Example:
        >>> omb = OMBPartFramework()
        >>> bundle = DataBundle.from_dataframes({"program": program_df, "outcomes": outcomes_df})
        >>> score = omb.assess_program(bundle)
        >>> print(f"Rating: {score.rating.value} ({score.total_score:.1f})")
    """
    
    METADATA = FrameworkMetadata(
        slug="omb_part",
        name="OMB Program Assessment Rating Tool",
        version="1.0.0",
        layer=VerticalLayer.GOVERNMENT_POLICY,
        tier=Tier.PROFESSIONAL,
        description="Program effectiveness evaluation using OMB PART methodology",
        required_domains=["program", "outcomes"],
        output_domains=["part_rating", "effectiveness_score"],
        constituent_models=["purpose_evaluator", "planning_scorer", "management_assessor", "results_analyzer"],
        tags=["government", "omb", "part", "program_assessment", "effectiveness"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self, config: Optional[PARTConfig] = None):
        super().__init__()
        self.part_config = config or PARTConfig()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        return cls.METADATA
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Compute initial state from program and outcomes data."""
        program_data = bundle.get("program")
        outcomes_data = bundle.get("outcomes")
        
        program_df = program_data.data
        outcomes_df = outcomes_data.data
        
        n_cohorts = len(program_df)
        
        # Extract program performance baseline
        if "performance_score" in program_df.columns:
            performance = program_df["performance_score"].values[:n_cohorts] / 100
        else:
            performance = np.full(n_cohorts, 0.5)
        
        # Extract outcome rates
        if "outcome_rate" in outcomes_df.columns:
            outcomes = outcomes_df["outcome_rate"].values[:n_cohorts]
        else:
            outcomes = np.full(n_cohorts, 0.5)
        
        return CohortStateVector(
            employment_prob=np.clip(outcomes, 0, 1),
            health_burden_score=np.full(n_cohorts, 0.2),
            credit_access_prob=np.clip(performance, 0, 1),
            housing_cost_ratio=np.full(n_cohorts, 0.3),
            opportunity_score=np.clip(performance, 0, 1),
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
        """Apply PART transition function."""
        transition = OMBPartTransition(self.part_config)
        return transition(state, t, config)
    
    def _compute_metrics(
        self,
        trajectory: StateTrajectory,
    ) -> OMBPartMetrics:
        """Compute PART metrics from simulation trajectory."""
        metrics = OMBPartMetrics()
        
        if len(trajectory) < 2:
            return metrics
        
        final_state = trajectory.final_state
        
        # Calculate section scores from final state metrics
        purpose_score = 80.0  # Base score, would be from questionnaire
        planning_score = 75.0
        management_score = float(final_state.credit_access_prob.mean() * 100)
        results_score = float(final_state.opportunity_score.mean() * 100)
        
        # Create PART score
        metrics.part_score = PARTScore.from_scores(
            purpose=purpose_score,
            planning=planning_score,
            management=management_score,
            results=results_score,
            config=self.part_config,
        )
        
        # Calculate efficiency metrics
        total_output = final_state.sector_output.sum()
        total_outcomes = final_state.opportunity_score.sum()
        if total_outcomes > 0:
            metrics.cost_per_outcome = total_output / total_outcomes
        
        # Target achievement
        targets_met = np.sum(final_state.opportunity_score >= 0.7)
        metrics.targets_met = int(targets_met)
        metrics.targets_total = len(final_state.opportunity_score)
        metrics.target_achievement_rate = targets_met / metrics.targets_total
        
        return metrics

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return OMB PART dashboard specification."""
        return FrameworkDashboardSpec(
            slug="omb_part",
            name="OMB Program Assessment Rating Tool",
            description=(
                "Program effectiveness evaluation using OMB PART methodology "
                "across Purpose & Design, Strategic Planning, Management, and Results."
            ),
            layer="government",
            parameters_schema={
                "type": "object",
                "properties": {
                    "program_type": {
                        "type": "string",
                        "title": "Program Type",
                        "enum": ["discretionary", "mandatory", "block_grant", "regulatory", "research"],
                        "default": "discretionary",
                        "x-ui-widget": "select",
                        "x-ui-group": "program",
                    },
                    "assessment_criteria": {
                        "type": "array",
                        "title": "Assessment Criteria",
                        "items": {
                            "type": "string",
                            "enum": ["purpose_design", "strategic_planning", "management", "results"],
                        },
                        "default": ["purpose_design", "strategic_planning", "management", "results"],
                        "x-ui-widget": "multiselect",
                        "x-ui-group": "criteria",
                    },
                    "rating_period": {
                        "type": "string",
                        "title": "Rating Period",
                        "enum": ["annual", "biennial", "program_cycle"],
                        "default": "annual",
                        "x-ui-widget": "select",
                        "x-ui-group": "time",
                    },
                },
            },
            default_parameters={
                "program_type": "discretionary",
                "assessment_criteria": ["purpose_design", "strategic_planning", "management", "results"],
                "rating_period": "annual",
            },
            parameter_groups=[
                ParameterGroupSpec(key="program", title="Program", parameters=["program_type"]),
                ParameterGroupSpec(key="criteria", title="Criteria", parameters=["assessment_criteria"]),
                ParameterGroupSpec(key="time", title="Time Period", parameters=["rating_period"]),
            ],
            required_domains=["program", "outcomes"],
            min_tier=Tier.TEAM,
            output_views=[
                OutputViewSpec(
                    key="part_rating",
                    title="PART Rating",
                    view_type=ViewType.GAUGE,
                    config={"min": 0, "max": 100, "thresholds": [50, 70, 85], "labels": ["Ineffective", "Adequate", "Moderately Effective", "Effective"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="part_rating_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="criteria_scores",
                    title="Criteria Scores",
                    view_type=ViewType.BAR_CHART,
                    config={"x_field": "criteria", "y_field": "score", "color_by": "weight"},
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="criteria_scores_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="improvement_recommendations",
                    title="Improvement Recommendations",
                    view_type=ViewType.TABLE,
                    config={"columns": ["area", "current_score", "gap", "recommendation", "priority"]},
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="improvement_recommendations_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def assess_program(
        self,
        bundle: DataBundle,
        config: Optional[FrameworkConfig] = None,
    ) -> PARTScore:
        """
        Assess program using PART methodology.
        
        Args:
            bundle: DataBundle with program and outcomes data
            config: Optional framework configuration
        
        Returns:
            PARTScore with section and total scores
        """
        config = config or FrameworkConfig()
        
        initial_state = self._compute_initial_state(bundle, config)
        trajectory = StateTrajectory(states=[initial_state])
        
        # Simulate one period to get current metrics
        next_state = self._transition(initial_state, 0, config)
        trajectory.append(next_state)
        
        metrics = self._compute_metrics(trajectory)
        return metrics.part_score
    
    @requires_tier(Tier.TEAM)
    def benchmark_programs(
        self,
        bundles: list[DataBundle],
        program_names: list[str],
        config: Optional[FrameworkConfig] = None,
    ) -> pd.DataFrame:
        """
        Benchmark multiple programs against each other.
        
        Args:
            bundles: List of DataBundles, one per program
            program_names: Names of programs
            config: Optional framework configuration
        
        Returns:
            DataFrame with comparative rankings
        """
        config = config or FrameworkConfig()
        
        results = []
        for name, bundle in zip(program_names, bundles):
            score = self.assess_program(bundle, config)
            results.append({
                "program": name,
                "total_score": score.total_score,
                "rating": score.rating.value,
                "purpose_design": score.purpose_design_score,
                "strategic_planning": score.strategic_planning_score,
                "management": score.management_score,
                "results": score.results_score,
            })
        
        df = pd.DataFrame(results)
        df = df.sort_values("total_score", ascending=False)
        df["rank"] = range(1, len(df) + 1)
        
        return df


# ════════════════════════════════════════════════════════════════════════════════
# Exports
# ════════════════════════════════════════════════════════════════════════════════

__all__ = [
    "OMBPartFramework",
    "PARTConfig",
    "PARTScore",
    "OMBPartMetrics",
    "ProgramRating",
    "OMBPartTransition",
]
