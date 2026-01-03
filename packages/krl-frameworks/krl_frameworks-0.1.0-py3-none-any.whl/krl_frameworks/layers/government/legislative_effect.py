# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Legislative Effectiveness Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Legislative Effectiveness Analysis Framework.

Implements comprehensive legislative effectiveness measurement:
- Bill passage prediction
- Legislative impact scoring
- Policy implementation tracking
- Congressional effectiveness ratings

References:
    - Volden & Wiseman Legislative Effectiveness Score (LES)
    - Congressional Research Service methodology
    - Policy diffusion literature

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
from krl_frameworks.simulation.cbss import TransitionFunction
from krl_frameworks.core.dashboard_spec import (
    FrameworkDashboardSpec,
    OutputViewSpec,
    ParameterGroupSpec,
    ViewType,
    ResultClass,
    TemporalSemantics,
)

if TYPE_CHECKING:
    from krl_frameworks.core.config import FrameworkConfig

__all__ = ["LegislativeEffectFramework"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Legislative Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class BillStage(Enum):
    """Stages in legislative process."""
    INTRODUCED = "Introduced"
    COMMITTEE = "In Committee"
    SUBCOMMITTEE = "In Subcommittee"
    REPORTED = "Reported"
    PASSED_CHAMBER = "Passed One Chamber"
    CONFERENCE = "In Conference"
    PASSED_BOTH = "Passed Both Chambers"
    SIGNED = "Signed into Law"
    VETOED = "Vetoed"


class BillType(Enum):
    """Types of legislation."""
    HR = "House Bill"
    S = "Senate Bill"
    HRES = "House Resolution"
    SRES = "Senate Resolution"
    HJRES = "House Joint Resolution"
    SJRES = "Senate Joint Resolution"
    HCONRES = "House Concurrent Resolution"
    SCONRES = "Senate Concurrent Resolution"


class PolicyArea(Enum):
    """Major policy areas."""
    ECONOMY = "Economics and Finance"
    HEALTH = "Health"
    DEFENSE = "Armed Forces and National Security"
    EDUCATION = "Education"
    ENERGY = "Energy"
    ENVIRONMENT = "Environmental Protection"
    FOREIGN = "International Affairs"
    SOCIAL = "Social Welfare"
    INFRASTRUCTURE = "Transportation and Infrastructure"
    TECHNOLOGY = "Science and Technology"


@dataclass
class Legislator:
    """Legislator profile."""
    
    id: str = ""
    name: str = ""
    party: str = ""
    state: str = ""
    district: Optional[int] = None
    chamber: str = ""  # "House" or "Senate"
    
    # Tenure
    terms_served: int = 1
    seniority_rank: int = 0
    
    # Committee assignments
    committee_chairs: int = 0
    subcommittee_chairs: int = 0
    total_committee_assignments: int = 0
    
    # Majority status
    is_majority: bool = False


@dataclass
class Bill:
    """Legislative bill record."""
    
    id: str = ""
    title: str = ""
    bill_type: BillType = BillType.HR
    policy_area: PolicyArea = PolicyArea.ECONOMY
    
    # Sponsors
    sponsor: str = ""
    cosponsors: int = 0
    bipartisan_cosponsors: int = 0
    
    # Progress
    stage: BillStage = BillStage.INTRODUCED
    
    # Characteristics
    substantive: bool = True  # vs. commemorative
    landmark: bool = False


@dataclass
class LegislativeEffectivenessScore:
    """Legislative Effectiveness Score (LES) components."""
    
    # Bill counts by stage
    bills_introduced: int = 0
    beyond_committee: int = 0
    passed_chamber: int = 0
    became_law: int = 0
    
    # Substantive vs. commemorative
    substantive_introduced: int = 0
    substantive_laws: int = 0
    
    # Landmark legislation
    landmark_laws: int = 0
    
    # Weighted score components
    introduction_score: float = 0.0
    committee_score: float = 0.0
    passage_score: float = 0.0
    law_score: float = 0.0
    
    # Final LES
    les_raw: float = 0.0
    les_normalized: float = 0.0  # Relative to chamber median


@dataclass
class PassagePrediction:
    """Bill passage probability prediction."""
    
    bill_id: str = ""
    
    # Stage probabilities
    committee_prob: float = 0.0
    floor_prob: float = 0.0
    other_chamber_prob: float = 0.0
    signature_prob: float = 0.0
    
    # Final passage probability
    passage_prob: float = 0.0
    
    # Key factors
    sponsor_les_factor: float = 0.0
    bipartisan_factor: float = 0.0
    committee_factor: float = 0.0
    timing_factor: float = 0.0


@dataclass
class ImpactAssessment:
    """Legislative impact assessment."""
    
    bill_id: str = ""
    
    # Scope of impact
    national_scope: bool = True
    states_affected: int = 50
    population_affected: float = 0.0
    
    # Economic impact (millions $)
    budget_impact: float = 0.0
    economic_activity: float = 0.0
    
    # Policy significance
    policy_change_magnitude: float = 0.0  # 0-1 scale
    implementation_complexity: float = 0.0  # 0-1 scale
    
    # Sunset/duration
    permanent: bool = True
    sunset_years: Optional[int] = None


@dataclass
class LegislativeMetrics:
    """Complete legislative effectiveness metrics."""
    
    legislator: Legislator = field(default_factory=Legislator)
    effectiveness: LegislativeEffectivenessScore = field(
        default_factory=LegislativeEffectivenessScore
    )
    predictions: list[PassagePrediction] = field(default_factory=list)
    impacts: list[ImpactAssessment] = field(default_factory=list)
    
    # Comparative metrics
    chamber_rank: int = 0
    party_rank: int = 0
    state_delegation_rank: int = 0


# ════════════════════════════════════════════════════════════════════════════════
# Legislative Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class LegislativeTransition(TransitionFunction):
    """Transition function for legislative simulation."""
    
    name = "LegislativeTransition"
    
    def __init__(self, policy_effect: float = 0.02):
        self.policy_effect = policy_effect
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        params = params or {}
        
        # Policy implementation lag
        implementation_lag = params.get("implementation_lag", 2)
        
        if t >= implementation_lag:
            # Policy effects phase in gradually
            phase_in = 1 - np.exp(-0.3 * (t - implementation_lag))
            effect = self.policy_effect * phase_in
        else:
            effect = 0
        
        new_opportunity = np.clip(state.opportunity_score + effect, 0, 1)
        
        return CohortStateVector(
            employment_prob=state.employment_prob,
            health_burden_score=state.health_burden_score,
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=new_opportunity,
            sector_output=state.sector_output * (1 + effect * 0.25),
            deprivation_vector=state.deprivation_vector,
        )


# ════════════════════════════════════════════════════════════════════════════════
# Legislative Effectiveness Framework
# ════════════════════════════════════════════════════════════════════════════════


class LegislativeEffectFramework(BaseMetaFramework):
    """
    Legislative Effectiveness Analysis Framework.
    
    Production-grade implementation following Volden & Wiseman methodology:
    
    - Legislative Effectiveness Score (LES) calculation
    - Bill passage prediction
    - Policy impact assessment
    - Congressional effectiveness ranking
    
    Token Weight: 6
    Tier: PROFESSIONAL
    
    Example:
        >>> framework = LegislativeEffectFramework()
        >>> score = framework.compute_effectiveness(legislator, bills)
        >>> print(f"LES: {score.les_normalized:.2f}")
    
    References:
        - Volden & Wiseman (2014)
        - Congressional Research Service
    """
    
    METADATA = FrameworkMetadata(
        slug="legislative-effect",
        name="Legislative Effectiveness Analysis",
        version="1.0.0",
        layer=VerticalLayer.GOVERNMENT_POLICY,
        tier=Tier.PROFESSIONAL,
        description=(
            "Legislative effectiveness scoring and bill passage prediction "
            "based on Volden & Wiseman methodology."
        ),
        required_domains=["legislator_data", "bill_data"],
        output_domains=["effectiveness_score", "passage_prediction", "impact"],
        constituent_models=["les", "passage_model", "impact_assessment"],
        tags=["legislative", "effectiveness", "congress", "policy"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    # LES Weights (based on Volden & Wiseman)
    LES_WEIGHTS = {
        "introduced": 0.1,
        "beyond_committee": 0.25,
        "passed_chamber": 0.35,
        "became_law": 0.5,
        "substantive_multiplier": 2.0,
        "landmark_multiplier": 5.0,
    }
    
    def __init__(self):
        super().__init__()
        self._transition_fn = LegislativeTransition()
    
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
            health_burden_score=np.full(n_cohorts, 0.25),
            credit_access_prob=np.full(n_cohorts, 0.65),
            housing_cost_ratio=np.full(n_cohorts, 0.32),
            opportunity_score=np.full(n_cohorts, 0.5),
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
        return {
            "mean_opportunity": float(np.mean(state.opportunity_score)),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "legislative-effect", "n_periods": trajectory.n_periods}

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return Legislative Effect dashboard specification."""
        return FrameworkDashboardSpec(
            slug="legislative-effect",
            name="Legislative Effectiveness Analysis",
            description=(
                "Legislative effectiveness scoring and bill passage prediction "
                "based on Volden & Wiseman methodology."
            ),
            layer="government",
            parameters_schema={
                "type": "object",
                "properties": {
                    "legislation_id": {
                        "type": "string",
                        "title": "Legislation ID",
                        "default": "",
                        "x-ui-widget": "text",
                        "x-ui-group": "legislation",
                    },
                    "effect_dimensions": {
                        "type": "array",
                        "title": "Effect Dimensions",
                        "items": {
                            "type": "string",
                            "enum": ["economic", "social", "health", "environmental", "fiscal", "regulatory"],
                        },
                        "default": ["economic", "social"],
                        "x-ui-widget": "multiselect",
                        "x-ui-group": "effects",
                    },
                    "time_horizon": {
                        "type": "integer",
                        "title": "Time Horizon (years)",
                        "minimum": 1,
                        "maximum": 20,
                        "default": 10,
                        "x-ui-widget": "slider",
                        "x-ui-group": "time",
                    },
                },
            },
            default_parameters={
                "legislation_id": "",
                "effect_dimensions": ["economic", "social"],
                "time_horizon": 10,
            },
            parameter_groups=[
                ParameterGroupSpec(key="legislation", title="Legislation", parameters=["legislation_id"]),
                ParameterGroupSpec(key="effects", title="Effects", parameters=["effect_dimensions"]),
                ParameterGroupSpec(key="time", title="Time Horizon", parameters=["time_horizon"]),
            ],
            required_domains=["legislator_data", "bill_data"],
            min_tier=Tier.ENTERPRISE,
            output_views=[
                OutputViewSpec(
                    key="impact_summary",
                    title="Impact Summary",
                    view_type=ViewType.METRIC_GRID,
                    config={"metrics": [
                        {"key": "total_impact", "label": "Total Impact", "format": "$,.0f"},
                        {"key": "affected_pop", "label": "Affected Population", "format": ",.0f"},
                        {"key": "effectiveness_score", "label": "Effectiveness Score", "format": ".1f"},
                        {"key": "implementation_rate", "label": "Implementation Rate", "format": ".0%"},
                    ]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="impact_summary_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="affected_populations",
                    title="Affected Populations",
                    view_type=ViewType.BAR_CHART,
                    config={"x_field": "population_group", "y_field": "impact", "color_by": "direction"},
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="affected_populations_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="causal_pathway",
                    title="Causal Pathway",
                    view_type=ViewType.NETWORK,
                    config={"nodes": "mechanisms", "edges": "causal_links", "layout": "hierarchical"},
                    result_class=ResultClass.STRUCTURAL_SIMILARITY,
                    output_key="causal_pathway_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )

    # ════════════════════════════════════════════════════════════════════════════
    # Public API Methods
    # ════════════════════════════════════════════════════════════════════════════

    @requires_tier(Tier.PROFESSIONAL)
    def compute_effectiveness(
        self,
        legislator: Legislator,
        bills: list[Bill],
        chamber_median_les: float = 1.0,
    ) -> LegislativeEffectivenessScore:
        """
        Compute Legislative Effectiveness Score.
        
        Args:
            legislator: Legislator profile
            bills: List of sponsored bills
            chamber_median_les: Chamber median for normalization
        
        Returns:
            LES components and final score
        """
        # Count bills by stage
        sponsored = [b for b in bills if b.sponsor == legislator.id]
        
        introduced = len(sponsored)
        beyond_committee = sum(1 for b in sponsored if b.stage.value != "Introduced")
        passed = sum(1 for b in sponsored if b.stage in [
            BillStage.PASSED_CHAMBER, BillStage.PASSED_BOTH, BillStage.SIGNED
        ])
        laws = sum(1 for b in sponsored if b.stage == BillStage.SIGNED)
        
        # Substantive bills
        substantive = [b for b in sponsored if b.substantive]
        substantive_introduced = len(substantive)
        substantive_laws = sum(1 for b in substantive if b.stage == BillStage.SIGNED)
        
        # Landmark
        landmark_laws = sum(1 for b in sponsored if b.landmark and b.stage == BillStage.SIGNED)
        
        # Weighted scores
        w = self.LES_WEIGHTS
        
        intro_score = introduced * w["introduced"]
        comm_score = beyond_committee * w["beyond_committee"]
        pass_score = passed * w["passed_chamber"]
        law_score = laws * w["became_law"]
        
        # Apply multipliers for substantive and landmark
        if substantive_laws > 0:
            law_score += substantive_laws * w["became_law"] * (w["substantive_multiplier"] - 1)
        if landmark_laws > 0:
            law_score += landmark_laws * w["became_law"] * (w["landmark_multiplier"] - 1)
        
        raw_les = intro_score + comm_score + pass_score + law_score
        normalized_les = raw_les / chamber_median_les if chamber_median_les > 0 else raw_les
        
        return LegislativeEffectivenessScore(
            bills_introduced=introduced,
            beyond_committee=beyond_committee,
            passed_chamber=passed,
            became_law=laws,
            substantive_introduced=substantive_introduced,
            substantive_laws=substantive_laws,
            landmark_laws=landmark_laws,
            introduction_score=intro_score,
            committee_score=comm_score,
            passage_score=pass_score,
            law_score=law_score,
            les_raw=raw_les,
            les_normalized=normalized_les,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def predict_passage(
        self,
        bill: Bill,
        sponsor: Legislator,
        congress_year: int = 2,  # 1 or 2 within Congress
    ) -> PassagePrediction:
        """
        Predict bill passage probability.
        
        Args:
            bill: Bill to analyze
            sponsor: Bill sponsor
            congress_year: Year within Congress (1 or 2)
        
        Returns:
            Passage probability prediction
        """
        # Base rates by bill type
        base_rates = {
            BillType.HR: 0.04,
            BillType.S: 0.05,
            BillType.HRES: 0.10,
            BillType.SRES: 0.12,
            BillType.HJRES: 0.03,
            BillType.SJRES: 0.04,
        }
        base = base_rates.get(bill.bill_type, 0.04)
        
        # Sponsor factors
        sponsor_factor = 1.0
        if sponsor.is_majority:
            sponsor_factor *= 2.0
        if sponsor.committee_chairs > 0:
            sponsor_factor *= 1.8
        if sponsor.terms_served >= 6:
            sponsor_factor *= 1.3
        
        # Bipartisan factor
        bipartisan_ratio = (
            bill.bipartisan_cosponsors / bill.cosponsors
            if bill.cosponsors > 0 else 0
        )
        bipartisan_factor = 1 + bipartisan_ratio * 1.5
        
        # Timing factor
        timing_factor = 1.0 if congress_year == 1 else 0.6
        
        # Committee probability (subset of all bills)
        committee_prob = min(0.95, base * 3 * sponsor_factor)
        
        # Floor probability (subset that clear committee)
        floor_prob = min(0.90, base * 2 * sponsor_factor * bipartisan_factor)
        
        # Other chamber probability
        other_chamber_prob = min(0.85, floor_prob * 0.6 * bipartisan_factor)
        
        # Signature probability
        signature_prob = 0.90  # Most passed bills are signed
        
        # Overall passage probability
        passage_prob = min(0.95, (
            base * sponsor_factor * bipartisan_factor * timing_factor
        ))
        
        return PassagePrediction(
            bill_id=bill.id,
            committee_prob=committee_prob,
            floor_prob=floor_prob,
            other_chamber_prob=other_chamber_prob,
            signature_prob=signature_prob,
            passage_prob=passage_prob,
            sponsor_les_factor=sponsor_factor,
            bipartisan_factor=bipartisan_factor,
            committee_factor=1.5 if sponsor.committee_chairs > 0 else 1.0,
            timing_factor=timing_factor,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def assess_impact(
        self,
        bill: Bill,
        budget_score: float = 0.0,
    ) -> ImpactAssessment:
        """
        Assess legislative impact.
        
        Args:
            bill: Bill to assess
            budget_score: CBO budget score (if available)
        
        Returns:
            Impact assessment
        """
        # Scope determination
        national_scope = bill.policy_area in [
            PolicyArea.ECONOMY, PolicyArea.DEFENSE, PolicyArea.FOREIGN
        ]
        
        # Policy change magnitude (simplified)
        magnitude = 0.5
        if bill.landmark:
            magnitude = 0.9
        elif bill.substantive:
            magnitude = 0.6
        else:
            magnitude = 0.2
        
        # Implementation complexity
        complexity = 0.5
        if bill.policy_area in [PolicyArea.HEALTH, PolicyArea.ENVIRONMENT]:
            complexity = 0.8
        elif bill.policy_area in [PolicyArea.SOCIAL, PolicyArea.EDUCATION]:
            complexity = 0.7
        
        return ImpactAssessment(
            bill_id=bill.id,
            national_scope=national_scope,
            states_affected=50 if national_scope else 1,
            population_affected=330e6 if national_scope else 10e6,
            budget_impact=budget_score,
            economic_activity=abs(budget_score) * 2.5,  # Multiplier effect
            policy_change_magnitude=magnitude,
            implementation_complexity=complexity,
            permanent=True,
            sunset_years=None,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def rank_chamber(
        self,
        legislators: list[Legislator],
        bills_by_sponsor: dict[str, list[Bill]],
    ) -> list[tuple[str, float, int]]:
        """
        Rank all legislators in chamber by effectiveness.
        
        Args:
            legislators: List of legislators
            bills_by_sponsor: Bills grouped by sponsor ID
        
        Returns:
            List of (legislator_id, LES, rank) tuples
        """
        scores = []
        
        for leg in legislators:
            bills = bills_by_sponsor.get(leg.id, [])
            les = self.compute_effectiveness(leg, bills)
            scores.append((leg.id, les.les_raw))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Add ranks
        ranked = [(lid, score, i + 1) for i, (lid, score) in enumerate(scores)]
        
        return ranked
    
    @requires_tier(Tier.PROFESSIONAL)
    def full_analysis(
        self,
        legislator: Legislator,
        bills: list[Bill],
        chamber_legislators: Optional[list[Legislator]] = None,
    ) -> LegislativeMetrics:
        """
        Complete legislative effectiveness analysis.
        
        Args:
            legislator: Target legislator
            bills: All bills in Congress
            chamber_legislators: All chamber legislators (for ranking)
        
        Returns:
            Complete metrics
        """
        # Filter to legislator's bills
        sponsored_bills = [b for b in bills if b.sponsor == legislator.id]
        
        # Effectiveness score
        effectiveness = self.compute_effectiveness(legislator, bills)
        
        # Passage predictions for pending bills
        predictions = []
        for bill in sponsored_bills:
            if bill.stage not in [BillStage.SIGNED, BillStage.VETOED]:
                pred = self.predict_passage(bill, legislator)
                predictions.append(pred)
        
        # Impact assessments for passed legislation
        impacts = []
        for bill in sponsored_bills:
            if bill.stage == BillStage.SIGNED:
                impact = self.assess_impact(bill)
                impacts.append(impact)
        
        # Chamber rank (simplified if no comparison data)
        chamber_rank = 0
        if chamber_legislators:
            bills_by_sponsor = {}
            for b in bills:
                if b.sponsor not in bills_by_sponsor:
                    bills_by_sponsor[b.sponsor] = []
                bills_by_sponsor[b.sponsor].append(b)
            
            rankings = self.rank_chamber(chamber_legislators, bills_by_sponsor)
            for lid, _, rank in rankings:
                if lid == legislator.id:
                    chamber_rank = rank
                    break
        
        return LegislativeMetrics(
            legislator=legislator,
            effectiveness=effectiveness,
            predictions=predictions,
            impacts=impacts,
            chamber_rank=chamber_rank,
        )
