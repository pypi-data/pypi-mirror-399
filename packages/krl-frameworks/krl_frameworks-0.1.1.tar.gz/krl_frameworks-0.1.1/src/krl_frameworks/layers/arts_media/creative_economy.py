# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Creative Economy Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Creative Economy Measurement Framework.

Measures economic impact of creative industries:
- Direct economic contribution
- Employment and workforce
- Multiplier effects
- Creative ecosystem health
- Innovation and IP metrics

References:
    - UNCTAD Creative Economy Reports
    - WIPO Creative Economy Studies
    - BEA Arts and Cultural Production Satellite Account
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
# Creative Economy Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class CreativeSector(Enum):
    """Creative industry sectors (UNCTAD classification)."""
    HERITAGE = "Cultural Heritage"
    ARTS = "Visual Arts"
    MEDIA = "Media & Entertainment"
    FUNCTIONAL = "Functional Creations"
    DESIGN = "Design"
    NEW_MEDIA = "New Media"
    PERFORMING_ARTS = "Performing Arts"
    PUBLISHING = "Publishing"
    AUDIOVISUAL = "Audiovisual"
    CRAFTS = "Crafts"


class EcosystemHealth(Enum):
    """Creative ecosystem health assessment."""
    THRIVING = "Thriving"
    GROWING = "Growing"
    STABLE = "Stable"
    CHALLENGED = "Challenged"
    DECLINING = "Declining"


@dataclass
class CreativeEconomyConfig:
    """Configuration for creative economy analysis."""
    
    # Sectors to include
    sectors: list[CreativeSector] = field(default_factory=lambda: list(CreativeSector))
    
    # Analysis parameters
    base_year: int = 2020
    analysis_year: int = 2024
    
    # Multiplier assumptions
    use_rims_multipliers: bool = True
    custom_multipliers: dict[CreativeSector, float] = field(default_factory=dict)
    
    # Geographic scope
    geographic_level: str = "national"  # national, state, metro, county


@dataclass
class EconomicMultipliers:
    """Economic impact multipliers."""
    
    # Output multiplier
    output_multiplier: float = 2.5
    
    # Employment multiplier
    employment_multiplier: float = 2.0
    
    # Earnings multiplier
    earnings_multiplier: float = 2.2
    
    # Value-added multiplier
    value_added_multiplier: float = 2.3
    
    # Tax multiplier
    tax_multiplier: float = 1.8


@dataclass
class DirectImpact:
    """Direct economic impact."""
    
    # Output
    gross_output: float = 0.0
    value_added: float = 0.0
    
    # Employment
    employment: int = 0
    full_time_equivalent: float = 0.0
    
    # Earnings
    compensation: float = 0.0
    avg_wage: float = 0.0
    
    # Business
    establishments: int = 0
    revenue: float = 0.0


@dataclass
class InducedImpact:
    """Indirect and induced economic impact."""
    
    # Indirect (supply chain)
    indirect_output: float = 0.0
    indirect_employment: int = 0
    indirect_earnings: float = 0.0
    
    # Induced (household spending)
    induced_output: float = 0.0
    induced_employment: int = 0
    induced_earnings: float = 0.0
    
    # Combined
    total_indirect_induced: float = 0.0


@dataclass
class TotalImpact:
    """Total economic impact."""
    
    direct: DirectImpact = field(default_factory=DirectImpact)
    indirect_induced: InducedImpact = field(default_factory=InducedImpact)
    
    # Totals
    total_output: float = 0.0
    total_employment: int = 0
    total_earnings: float = 0.0
    total_value_added: float = 0.0
    
    # Ratios
    gdp_share: float = 0.0
    employment_share: float = 0.0


@dataclass
class SectorMetrics:
    """Per-sector economic metrics."""
    
    sector: CreativeSector = CreativeSector.ARTS
    
    # Impact
    impact: TotalImpact = field(default_factory=TotalImpact)
    
    # Growth
    output_growth: float = 0.0
    employment_growth: float = 0.0
    
    # Share
    sector_share: float = 0.0


@dataclass
class EcosystemMetrics:
    """Creative ecosystem health metrics."""
    
    # Workforce
    creative_workers: int = 0
    creative_workers_pct: float = 0.0
    freelancer_pct: float = 0.0
    
    # Infrastructure
    creative_spaces: int = 0
    cultural_venues: int = 0
    coworking_spaces: int = 0
    
    # Support
    arts_funding_per_capita: float = 0.0
    grants_available: int = 0
    incubators: int = 0
    
    # Innovation
    patents_creative: int = 0
    trademarks_creative: int = 0
    copyrights_registered: int = 0
    
    # Overall health
    ecosystem_health: EcosystemHealth = EcosystemHealth.STABLE
    health_score: float = 0.0


@dataclass
class CreativeEconomyMetrics:
    """Comprehensive creative economy metrics."""
    
    # Total impact
    total_impact: TotalImpact = field(default_factory=TotalImpact)
    
    # By sector
    sector_metrics: dict[CreativeSector, SectorMetrics] = field(default_factory=dict)
    
    # Multipliers used
    multipliers: EconomicMultipliers = field(default_factory=EconomicMultipliers)
    
    # Ecosystem
    ecosystem: EcosystemMetrics = field(default_factory=EcosystemMetrics)
    
    # Trends
    output_trend: list[float] = field(default_factory=list)
    employment_trend: list[float] = field(default_factory=list)
    
    # Summary
    creative_intensity: float = 0.0  # Creative output per capita
    export_value: float = 0.0


# ════════════════════════════════════════════════════════════════════════════════
# Creative Economy Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class CreativeEconomyTransition(TransitionFunction):
    """
    Creative economy transition function.
    
    Models the growth and evolution of creative industries.
    """
    
    def __init__(self, config: CreativeEconomyConfig):
        self.config = config
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        params: Optional[dict[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply creative economy transition."""
        params = params or {}
        
        # Growth drivers
        investment = params.get("investment_rate", 0.05)
        tech_adoption = params.get("tech_adoption", 0.1)
        
        # Output growth
        base_growth = 0.03  # 3% baseline
        growth_rate = base_growth + investment * 0.5 + tech_adoption * 0.3
        
        new_output = state.sector_output * (1 + growth_rate)
        
        # Employment growth (slower than output - productivity gains)
        employment_growth = growth_rate * 0.7
        new_employment = np.clip(
            state.employment_prob + employment_growth * 0.05,
            0.0, 0.99
        )
        
        # Creative opportunity expands
        opportunity_growth = growth_rate * 0.3
        new_opportunity = np.clip(
            state.opportunity_score + opportunity_growth,
            0.0, 1.0
        )
        
        return CohortStateVector(
            employment_prob=new_employment,
            health_burden_score=state.health_burden_score,
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=new_opportunity,
            sector_output=new_output,
            deprivation_vector=state.deprivation_vector,
            step=t + 1,
        )


# ════════════════════════════════════════════════════════════════════════════════
# Creative Economy Framework
# ════════════════════════════════════════════════════════════════════════════════


class CreativeEconomyFramework(BaseMetaFramework):
    """
    Creative Economy Measurement Framework.
    
    Measures economic impact of creative industries:
    
    1. Direct Impact: Jobs, wages, output in creative sectors
    2. Indirect Impact: Supply chain effects
    3. Induced Impact: Household spending effects
    4. Multipliers: RIMS II or custom multipliers
    5. Ecosystem Health: Workforce, infrastructure, support
    
    Tier: PROFESSIONAL (economic impact analysis)
    
    Example:
        >>> framework = CreativeEconomyFramework()
        >>> bundle = DataBundle.from_dataframes({
        ...     "economic_data": econ_df,
        ...     "employment": employment_df
        ... })
        >>> metrics = framework.measure_impact(bundle)
        >>> print(f"Total Output: ${metrics.total_impact.total_output:,.0f}")
        >>> print(f"Total Employment: {metrics.total_impact.total_employment:,}")
    """
    
    METADATA = FrameworkMetadata(
        slug="creative_economy",
        name="Creative Economy Measurement Framework",
        version="1.0.0",
        layer=VerticalLayer.ARTS_MEDIA_ENTERTAINMENT,
        tier=Tier.PROFESSIONAL,
        description="Economic impact measurement for creative industries using multiplier analysis",
        required_domains=["economic_data"],
        output_domains=["economic_impact", "multiplier_effects", "sector_analysis"],
        constituent_models=["multiplier_calculator", "sector_classifier", "impact_aggregator", "io_modeler"],
        tags=["arts", "creative_economy", "economic_impact", "multipliers", "creative_industries"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    # Default multipliers by sector
    DEFAULT_MULTIPLIERS: dict[CreativeSector, EconomicMultipliers] = {
        CreativeSector.MEDIA: EconomicMultipliers(2.8, 2.2, 2.5, 2.6, 2.0),
        CreativeSector.AUDIOVISUAL: EconomicMultipliers(3.0, 2.4, 2.7, 2.8, 2.2),
        CreativeSector.DESIGN: EconomicMultipliers(2.3, 1.9, 2.1, 2.2, 1.7),
        CreativeSector.PERFORMING_ARTS: EconomicMultipliers(2.1, 1.8, 2.0, 2.0, 1.6),
        CreativeSector.PUBLISHING: EconomicMultipliers(2.4, 2.0, 2.2, 2.3, 1.8),
    }
    
    def __init__(self, config: Optional[CreativeEconomyConfig] = None):
        super().__init__()
        self.economy_config = config or CreativeEconomyConfig()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        return cls.METADATA
    
    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Dashboard specification for creative economy measurement.
        
        Parameters extracted from CreativeEconomyConfig:
        - base_year: Baseline year for analysis (default 2020)
        - analysis_year: Target year for analysis (default 2024)
        - use_rims_multipliers: Use RIMS II multipliers (default True)
        - geographic_level: national/state/metro/county
        """
        return FrameworkDashboardSpec(
            slug="creative_economy",
            name="Creative Economy Measurement",
            description=(
                "Creative economy measurement using UNCTAD methodology and "
                "BEA Arts and Cultural Production Satellite Account frameworks."
            ),
            layer="arts_media",
            parameters_schema={
                "type": "object",
                "properties": {
                    # Time parameters (from CreativeEconomyConfig)
                    "base_year": {
                        "type": "integer",
                        "title": "Base Year",
                        "description": "Baseline year for economic comparison",
                        "minimum": 2010,
                        "maximum": 2030,
                        "default": 2020,
                        "x-ui-widget": "dropdown",
                        "x-ui-group": "time",
                    },
                    "analysis_year": {
                        "type": "integer",
                        "title": "Analysis Year",
                        "description": "Target year for analysis",
                        "minimum": 2015,
                        "maximum": 2030,
                        "default": 2024,
                        "x-ui-widget": "dropdown",
                        "x-ui-group": "time",
                    },
                    # Multiplier settings
                    "use_rims_multipliers": {
                        "type": "boolean",
                        "title": "Use RIMS Multipliers",
                        "description": "Use Bureau of Economic Analysis RIMS II multipliers",
                        "default": True,
                        "x-ui-widget": "checkbox",
                        "x-ui-group": "multipliers",
                    },
                    "output_multiplier": {
                        "type": "number",
                        "title": "Output Multiplier",
                        "description": "Custom output multiplier (if not using RIMS)",
                        "minimum": 1.0,
                        "maximum": 5.0,
                        "default": 2.5,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.1,
                        "x-ui-group": "multipliers",
                    },
                    "employment_multiplier": {
                        "type": "number",
                        "title": "Employment Multiplier",
                        "description": "Custom employment multiplier",
                        "minimum": 1.0,
                        "maximum": 5.0,
                        "default": 2.0,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.1,
                        "x-ui-group": "multipliers",
                    },
                    # Geographic scope
                    "geographic_level": {
                        "type": "string",
                        "title": "Geographic Level",
                        "description": "Level of geographic aggregation",
                        "enum": ["national", "state", "metro", "county"],
                        "default": "national",
                        "x-ui-widget": "dropdown",
                        "x-ui-group": "scope",
                    },
                },
                "required": [],
            },
            default_parameters={
                "base_year": 2020,
                "analysis_year": 2024,
                "use_rims_multipliers": True,
                "output_multiplier": 2.5,
                "employment_multiplier": 2.0,
                "geographic_level": "national",
            },
            min_tier=Tier.TEAM,
            parameter_groups=[
                ParameterGroupSpec(
                    key="time",
                    title="Time Period",
                    description="Define analysis time frame",
                    collapsed_by_default=False,
                    parameters=["base_year", "analysis_year"],
                ),
                ParameterGroupSpec(
                    key="multipliers",
                    title="Economic Multipliers",
                    description="Configure economic impact multipliers",
                    collapsed_by_default=True,
                    parameters=["use_rims_multipliers", "output_multiplier", "employment_multiplier"],
                ),
                ParameterGroupSpec(
                    key="scope",
                    title="Geographic Scope",
                    description="Select geographic analysis level",
                    collapsed_by_default=True,
                    parameters=["geographic_level"],
                ),
            ],
            output_views=[
                OutputViewSpec(
                    key="sector_contribution",
                    title="Sector Contribution",
                    view_type=ViewType.BAR_CHART,
                    description="Economic contribution by creative sector",
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="sector_contribution_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="employment_metrics",
                    title="Employment Metrics",
                    view_type=ViewType.TABLE,
                    description="Creative workforce statistics",
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="employment_metrics_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="growth_trends",
                    title="Growth Trends",
                    view_type=ViewType.LINE_CHART,
                    description="Creative economy growth trajectory",
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="growth_trends_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Compute initial state from economic data."""
        econ_data = bundle.get("economic_data")
        econ_df = econ_data.data
        
        n_cohorts = max(1, len(econ_df))
        
        # Extract output by sector
        if "output" in econ_df.columns:
            output = econ_df["output"].values[:n_cohorts]
        else:
            output = np.full(n_cohorts, 1e9)  # $1B default
        
        # Extract employment
        if "employment" in econ_df.columns:
            employment = econ_df["employment"].values[:n_cohorts]
            employment_rate = employment / employment.max() if employment.max() > 0 else np.full(n_cohorts, 0.5)
        else:
            employment_rate = np.full(n_cohorts, 0.5)
        
        return CohortStateVector(
            employment_prob=np.clip(employment_rate, 0.01, 0.99),
            health_burden_score=np.full(n_cohorts, 0.1),
            credit_access_prob=np.full(n_cohorts, 0.5),
            housing_cost_ratio=np.full(n_cohorts, 0.3),
            opportunity_score=np.full(n_cohorts, 0.5),
            sector_output=output.reshape(-1, 1).repeat(10, axis=1) / 10,
            deprivation_vector=np.zeros((n_cohorts, 6)),
            step=0,
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Apply creative economy transition."""
        transition = CreativeEconomyTransition(self.economy_config)
        return transition(state, t, config)
    
    def _compute_metrics(
        self,
        trajectory: StateTrajectory,
    ) -> CreativeEconomyMetrics:
        """Compute creative economy metrics."""
        metrics = CreativeEconomyMetrics()
        
        if len(trajectory) < 1:
            return metrics
        
        final = trajectory[-1]
        initial = trajectory.initial_state
        
        # Direct impact
        direct_output = float(final.sector_output.sum())
        direct_employment = int(final.employment_prob.sum() * 1000)  # Scale
        avg_wage = 65000  # Assumed average
        
        direct = DirectImpact(
            gross_output=direct_output,
            value_added=direct_output * 0.55,  # ~55% value added ratio
            employment=direct_employment,
            full_time_equivalent=direct_employment * 0.9,
            compensation=direct_employment * avg_wage,
            avg_wage=avg_wage,
            establishments=max(1, direct_employment // 10),
            revenue=direct_output * 0.9,
        )
        
        # Get multipliers (use default average)
        multipliers = EconomicMultipliers()
        metrics.multipliers = multipliers
        
        # Indirect/induced
        indirect_induced = InducedImpact(
            indirect_output=direct_output * (multipliers.output_multiplier - 1) * 0.4,
            indirect_employment=int(direct_employment * (multipliers.employment_multiplier - 1) * 0.4),
            indirect_earnings=direct.compensation * (multipliers.earnings_multiplier - 1) * 0.4,
            induced_output=direct_output * (multipliers.output_multiplier - 1) * 0.6,
            induced_employment=int(direct_employment * (multipliers.employment_multiplier - 1) * 0.6),
            induced_earnings=direct.compensation * (multipliers.earnings_multiplier - 1) * 0.6,
        )
        indirect_induced.total_indirect_induced = (
            indirect_induced.indirect_output + indirect_induced.induced_output
        )
        
        # Total impact
        total = TotalImpact(
            direct=direct,
            indirect_induced=indirect_induced,
            total_output=direct_output * multipliers.output_multiplier,
            total_employment=int(direct_employment * multipliers.employment_multiplier),
            total_earnings=direct.compensation * multipliers.earnings_multiplier,
            total_value_added=direct.value_added * multipliers.value_added_multiplier,
            gdp_share=0.045,  # ~4.5% typical creative economy share
            employment_share=0.055,
        )
        
        metrics.total_impact = total
        
        # Sector breakdown
        n_sectors = len(self.economy_config.sectors)
        for i, sector in enumerate(self.economy_config.sectors[:5]):  # Top 5
            sector_share = 0.2  # Equal distribution
            
            sector_direct = DirectImpact(
                gross_output=direct_output * sector_share,
                value_added=direct.value_added * sector_share,
                employment=int(direct_employment * sector_share),
                compensation=direct.compensation * sector_share,
            )
            
            sector_total = TotalImpact(
                direct=sector_direct,
                total_output=total.total_output * sector_share,
                total_employment=int(total.total_employment * sector_share),
            )
            
            # Growth
            initial_output = float(initial.sector_output.sum())
            growth = (direct_output - initial_output) / initial_output if initial_output > 0 else 0
            
            metrics.sector_metrics[sector] = SectorMetrics(
                sector=sector,
                impact=sector_total,
                output_growth=growth,
                employment_growth=growth * 0.7,
                sector_share=sector_share,
            )
        
        # Ecosystem
        metrics.ecosystem = EcosystemMetrics(
            creative_workers=direct_employment,
            creative_workers_pct=0.055,
            freelancer_pct=0.35,
            creative_spaces=max(1, direct_employment // 50),
            cultural_venues=max(1, direct_employment // 100),
            arts_funding_per_capita=15.0,
            ecosystem_health=EcosystemHealth.GROWING if total.gdp_share > 0.04 else EcosystemHealth.STABLE,
            health_score=70 + float(final.opportunity_score.mean()) * 30,
        )
        
        # Trends
        metrics.output_trend = [float(s.sector_output.sum()) for s in trajectory]
        metrics.employment_trend = [float(s.employment_prob.sum()) * 1000 for s in trajectory]
        
        # Summary
        population = 330_000_000  # US population
        metrics.creative_intensity = direct_output / population
        metrics.export_value = direct_output * 0.15  # 15% export ratio
        
        return metrics
    
    @requires_tier(Tier.PROFESSIONAL)
    def measure_impact(
        self,
        bundle: DataBundle,
        config: Optional[FrameworkConfig] = None,
    ) -> CreativeEconomyMetrics:
        """
        Measure creative economy impact.
        
        Args:
            bundle: DataBundle with economic_data
            config: Optional framework configuration
        
        Returns:
            CreativeEconomyMetrics with full impact analysis
        """
        config = config or FrameworkConfig()
        
        initial_state = self._compute_initial_state(bundle, config)
        trajectory = StateTrajectory(states=[initial_state])
        
        # Project for analysis period
        years = self.economy_config.analysis_year - self.economy_config.base_year
        periods = years * 4  # Quarterly
        
        current = initial_state
        for t in range(periods):
            current = self._transition(current, t, config)
            trajectory.append(current)
        
        return self._compute_metrics(trajectory)
    
    @requires_tier(Tier.TEAM)
    def compare_regions(
        self,
        bundles: list[DataBundle],
        region_names: list[str],
        config: Optional[FrameworkConfig] = None,
    ) -> dict[str, CreativeEconomyMetrics]:
        """
        Compare creative economy across regions.
        
        Args:
            bundles: List of DataBundles, one per region
            region_names: Names for each region
            config: Optional framework configuration
        
        Returns:
            Dictionary of region name -> metrics
        """
        results = {}
        
        for name, bundle in zip(region_names, bundles):
            metrics = self.measure_impact(bundle, config)
            results[name] = metrics
        
        return results
    
    @requires_tier(Tier.ENTERPRISE)
    def project_growth(
        self,
        bundle: DataBundle,
        years: int = 5,
        growth_scenario: str = "baseline",
        config: Optional[FrameworkConfig] = None,
    ) -> list[CreativeEconomyMetrics]:
        """
        Project creative economy growth.
        
        Args:
            bundle: DataBundle with baseline economic data
            years: Number of years to project
            growth_scenario: "baseline", "high", "low"
            config: Optional framework configuration
        
        Returns:
            List of yearly metrics projections
        """
        config = config or FrameworkConfig()
        
        initial_state = self._compute_initial_state(bundle, config)
        
        # Scenario multipliers
        scenario_mult = {
            "baseline": 1.0,
            "high": 1.5,
            "low": 0.6,
        }.get(growth_scenario, 1.0)
        
        projections = []
        current = initial_state
        
        for year in range(years):
            trajectory = StateTrajectory(states=[current])
            
            # Project one year (4 quarters)
            for q in range(4):
                current = self._transition(current, year * 4 + q, config)
                trajectory.append(current)
            
            yearly_metrics = self._compute_metrics(trajectory)
            
            # Adjust for scenario
            yearly_metrics.total_impact.total_output *= scenario_mult ** year
            
            projections.append(yearly_metrics)
        
        return projections


# ════════════════════════════════════════════════════════════════════════════════
# Exports
# ════════════════════════════════════════════════════════════════════════════════

__all__ = [
    "CreativeEconomyFramework",
    "CreativeEconomyConfig",
    "CreativeEconomyMetrics",
    "CreativeSector",
    "EconomicMultipliers",
    "DirectImpact",
    "InducedImpact",
    "TotalImpact",
    "SectorMetrics",
    "EcosystemMetrics",
    "EcosystemHealth",
    "CreativeEconomyTransition",
]
