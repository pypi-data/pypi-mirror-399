# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - REMSOM (Regional Economic Multisectoral Open Model)
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
REMSOM: Regional Economic Multisectoral Open Model.

REMSOM is Khipu Research Labs' flagship meta-framework for regional
economic simulation. It serves as a PEER framework within the
Khipu Frameworks architecture, not as a superior or orchestrating
layer.

Architecture:
    REMSOM operates as an equal participant in framework orchestration,
    providing cohort-based economic simulation that can:
    - Consume outputs from other frameworks (MPI, HDI, SPI)
    - Produce inputs for downstream frameworks
    - Be orchestrated via DAG pipelines

Core Model Components:
    1. Cohort State Machine: Age×Sector×Geography stratified populations
    2. Labor Market Transitions: Employment/unemployment dynamics
    3. Sector Output Model: Multi-sector production functions
    4. Human Capital Accumulation: Education and skill formation
    5. Health Burden Dynamics: Mortality and morbidity impacts

CBSS Integration:
    - Uses canonical CohortStateVector for state representation
    - Implements TransitionFunction for temporal evolution
    - Supports policy shock injection via PolicyShockEngine

Historical Note:
    REMSOM was originally prototyped in notebooks at:
    krl-data-connectors/notebooks/remsom_model.ipynb
    
    This module wraps that prototype and extends it with the
    standard BaseMetaFramework interface.

Tier: ENTERPRISE (full model requires orchestration access)
      COMMUNITY tier can access individual REMSOM indices
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Mapping, Optional, Sequence

import numpy as np

from krl_frameworks.core.base import (
    BaseMetaFramework,
    FrameworkExecutionResult,
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
from krl_frameworks.core.data_bundle import DataBundle, DataDomain
from krl_frameworks.core.exceptions import (
    DataBundleValidationError,
    ExecutionError,
)
from krl_frameworks.core.state import CohortStateVector, StateTrajectory
from krl_frameworks.core.tier import Tier, requires_tier
from krl_frameworks.simulation.cbss import (
    CBSSEngine,
    PolicyShock,
    SimulationResult,
    TransitionFunction,
)

if TYPE_CHECKING:
    from krl_frameworks.core.config import FrameworkConfig
    from krl_frameworks.core.output_envelope import (
        DimensionManifest,
        FrameworkOutputEnvelope,
    )

__all__ = [
    "REMSOMFramework",
    "REMSOMConfig",
    "REMSOMTransition",
    "REMSOMMetrics",
]

logger = logging.getLogger(__name__)

# Deprecation warning for v1
import warnings

def _emit_deprecation_warning():
    warnings.warn(
        "REMSOMFramework (v1) is deprecated and will be removed in a future release. "
        "Please migrate to REMSOMFrameworkV2 from krl_frameworks.layers.meta.remsomV2, "
        "which provides the executive-grade observatory architecture with three model stacks "
        "(Index, Spatial, Causal). See the migration guide at docs.khipuresearchlabs.org/remsom-v2",
        DeprecationWarning,
        stacklevel=3,
    )


# ════════════════════════════════════════════════════════════════════════════════
# REMSOM Configuration
# ════════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class REMSOMConfig:
    """
    Configuration for REMSOM model.
    
    All economic constants are exposed as configurable parameters to eliminate
    hardcoded values and enable full user control over simulation behavior.
    
    Attributes:
        n_sectors: Number of economic sectors.
        n_age_groups: Number of age cohort groups.
        labor_elasticity: Labor supply elasticity.
        capital_share: Capital share in production (α in Cobb-Douglas).
        depreciation_rate: Capital depreciation rate.
        discount_rate: Time preference discount rate.
        health_productivity_impact: How health burden affects productivity.
        education_skill_premium: Returns to education.
        tfp_growth_rate: Total factor productivity growth rate.
        sector_noise_std: Standard deviation of sector-level noise.
        employment_floor: Minimum employment probability.
        employment_cap: Maximum employment probability.
        health_burden_min: Minimum health burden score.
        health_burden_max: Maximum health burden score.
        health_mean_reversion_rate: Rate of mean reversion for health burden.
        health_mean_reversion_target: Target value for health mean reversion.
        credit_improvement_rate: Rate of credit access improvement.
        housing_pressure_factor: Factor for housing cost pressure from output.
        opportunity_growth_rate: Rate of opportunity score growth.
        sector_names: Names for each economic sector.
        cohort_labels: Labels for age cohorts (auto-generated if not provided).
        geography: Geographic scope label.
    """
    
    # Structure parameters
    n_sectors: int = 10
    n_age_groups: int = 5
    
    # Economic parameters
    labor_elasticity: float = 0.7
    capital_share: float = 0.33
    depreciation_rate: float = 0.05
    discount_rate: float = 0.03
    
    # Human capital parameters
    health_productivity_impact: float = 0.15
    education_skill_premium: float = 0.08
    
    # Simulation dynamics parameters
    tfp_growth_rate: float = 0.015
    sector_noise_std: float = 0.005
    
    # Employment dynamics
    employment_floor: float = 0.10
    employment_cap: float = 0.98
    employment_delta_scale: float = 0.1
    
    # Health dynamics
    health_burden_min: float = 0.02
    health_burden_max: float = 0.80
    health_mean_reversion_rate: float = 0.05
    health_mean_reversion_target: float = 0.20
    employment_health_effect: float = -0.01
    
    # Credit dynamics
    credit_min: float = 0.10
    credit_max: float = 0.95
    credit_improvement_rate: float = 0.02
    
    # Housing dynamics
    housing_min: float = 0.10
    housing_max: float = 0.70
    housing_pressure_factor: float = 0.01
    
    # Opportunity dynamics
    opportunity_min: float = 0.10
    opportunity_max: float = 0.95
    opportunity_growth_rate: float = 0.05
    
    # Sector names (default NAICS-inspired)
    sector_names: tuple[str, ...] = (
        "Agriculture",
        "Mining",
        "Manufacturing",
        "Utilities",
        "Construction",
        "Trade",
        "Transportation",
        "Information",
        "Finance",
        "Services",
    )
    
    # Optional cohort labels (auto-generated if empty)
    cohort_labels: tuple[str, ...] = ()
    
    # Geographic scope
    geography: str = "National"
    
    def __post_init__(self):
        if len(self.sector_names) != self.n_sectors:
            object.__setattr__(
                self, 
                "sector_names", 
                tuple(f"Sector_{i}" for i in range(self.n_sectors))
            )


# ════════════════════════════════════════════════════════════════════════════════
# REMSOM Metrics
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class REMSOMMetrics:
    """
    Container for REMSOM simulation results.
    
    Attributes:
        total_output: Aggregate economic output.
        employment_rate: Overall employment rate.
        sector_employment: Employment by sector.
        sector_output: Output by sector.
        human_capital_index: Aggregate human capital measure.
        health_adjusted_productivity: HAP index.
        gini_employment: Employment inequality (Gini).
        cohort_vulnerability: Per-cohort vulnerability scores.
    """
    
    total_output: float
    employment_rate: float
    sector_employment: dict[str, float]
    sector_output: dict[str, float]
    human_capital_index: float
    health_adjusted_productivity: float
    gini_employment: float
    cohort_vulnerability: np.ndarray = field(repr=False)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "total_output": self.total_output,
            "employment_rate": self.employment_rate,
            "sector_employment": self.sector_employment,
            "sector_output": self.sector_output,
            "human_capital_index": self.human_capital_index,
            "health_adjusted_productivity": self.health_adjusted_productivity,
            "gini_employment": self.gini_employment,
            "mean_vulnerability": float(self.cohort_vulnerability.mean()),
            "max_vulnerability": float(self.cohort_vulnerability.max()),
        }


# ════════════════════════════════════════════════════════════════════════════════
# REMSOM Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class REMSOMTransition(TransitionFunction):
    """
    REMSOM cohort state transition function.
    
    Implements the core REMSOM dynamics:
    1. Labor market transitions (hiring/separation)
    2. Sector reallocation
    3. Human capital accumulation
    4. Health burden evolution
    5. Productivity computation
    
    This is a vectorized implementation operating on the full
    CohortStateVector simultaneously.
    """
    
    name = "REMSOMTransition"
    
    def __init__(self, config: Optional[REMSOMConfig] = None):
        self.config = config or REMSOMConfig()
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """
        Apply REMSOM transition dynamics.
        
        The transition models:
        - Employment probability changes based on sector growth
        - Health burden evolution with mean reversion
        - Credit access linked to employment
        - Housing cost ratio adjustment
        - Sector output growth with TFP
        """
        params = params or {}
        cfg = self.config
        
        n_cohorts = state.n_cohorts
        n_sectors = state.n_sectors
        
        # ─────────────────────────────────────────────────────────────────────
        # 1. Sector Output Evolution
        # ─────────────────────────────────────────────────────────────────────
        # Simple Cobb-Douglas growth with labor and productivity shocks
        
        # Aggregate labor supply (weighted by employment prob)
        labor_supply = state.employment_prob.mean()
        
        # TFP growth (use config value, allow param override)
        tfp_growth = params.get("tfp_growth", cfg.tfp_growth_rate)
        sector_noise = np.random.normal(0, cfg.sector_noise_std, n_sectors)
        sector_growth = 1 + tfp_growth + sector_noise
        
        # Apply growth to sector output
        new_sector_output = state.sector_output * sector_growth[np.newaxis, :]
        
        # Health-adjusted productivity penalty
        avg_health_burden = state.health_burden_score.mean()
        health_penalty = 1 - cfg.health_productivity_impact * avg_health_burden
        new_sector_output *= health_penalty
        
        # ─────────────────────────────────────────────────────────────────────
        # 2. Employment Dynamics
        # ─────────────────────────────────────────────────────────────────────
        # Employment prob changes based on sector output growth
        
        # Average sector growth as employment driver
        avg_sector_growth = sector_growth.mean()
        employment_delta = (avg_sector_growth - 1) * cfg.labor_elasticity
        
        # Heterogeneous impact by cohort (opportunity score modulates)
        cohort_employment_delta = employment_delta * (0.5 + state.opportunity_score)
        
        new_employment_prob = np.clip(
            state.employment_prob + cohort_employment_delta * cfg.employment_delta_scale,
            cfg.employment_floor,
            cfg.employment_cap,
        )
        
        # ─────────────────────────────────────────────────────────────────────
        # 3. Health Burden Evolution
        # ─────────────────────────────────────────────────────────────────────
        # Mean-reverting process with employment effects
        
        # Employed cohorts have improving health
        health_effect = cfg.employment_health_effect * state.employment_prob
        
        # Mean reversion to baseline
        mean_reversion = cfg.health_mean_reversion_rate * (
            cfg.health_mean_reversion_target - state.health_burden_score
        )
        
        new_health_burden = np.clip(
            state.health_burden_score + health_effect + mean_reversion,
            cfg.health_burden_min,
            cfg.health_burden_max,
        )
        
        # ─────────────────────────────────────────────────────────────────────
        # 4. Credit Access Dynamics
        # ─────────────────────────────────────────────────────────────────────
        # Credit access improves with employment
        
        credit_improvement = cfg.credit_improvement_rate * (new_employment_prob - 0.5)
        new_credit_access = np.clip(
            state.credit_access_prob + credit_improvement,
            cfg.credit_min,
            cfg.credit_max,
        )
        
        # ─────────────────────────────────────────────────────────────────────
        # 5. Housing Cost Dynamics
        # ─────────────────────────────────────────────────────────────────────
        # Housing costs rise with sector output (demand pressure)
        
        output_pressure = np.log1p(new_sector_output.mean(axis=1)) / 10
        new_housing_ratio = np.clip(
            state.housing_cost_ratio * (1 + output_pressure * cfg.housing_pressure_factor),
            cfg.housing_min,
            cfg.housing_max,
        )
        
        # ─────────────────────────────────────────────────────────────────────
        # 6. Opportunity Score Update
        # ─────────────────────────────────────────────────────────────────────
        # Opportunity increases with education investment (proxy: credit access)
        
        education_effect = cfg.education_skill_premium * new_credit_access
        new_opportunity = np.clip(
            state.opportunity_score + education_effect * cfg.opportunity_growth_rate,
            cfg.opportunity_min,
            cfg.opportunity_max,
        )
        
        # ─────────────────────────────────────────────────────────────────────
        # 7. Deprivation Vector Update
        # ─────────────────────────────────────────────────────────────────────
        # Aggregate improvements reduce deprivation
        
        improvement_factor = (
            0.3 * (new_employment_prob - state.employment_prob) +
            0.2 * (state.health_burden_score - new_health_burden) +
            0.2 * (new_credit_access - state.credit_access_prob) +
            0.3 * (new_opportunity - state.opportunity_score)
        )
        
        new_deprivation = np.clip(
            state.deprivation_vector * (1 - improvement_factor[:, np.newaxis] * 0.5),
            0,
            1
        )
        
        return CohortStateVector(
            employment_prob=new_employment_prob,
            health_burden_score=new_health_burden,
            credit_access_prob=new_credit_access,
            housing_cost_ratio=new_housing_ratio,
            opportunity_score=new_opportunity,
            sector_output=new_sector_output,
            deprivation_vector=new_deprivation,
        )


# ════════════════════════════════════════════════════════════════════════════════
# REMSOM Framework
# ════════════════════════════════════════════════════════════════════════════════


class REMSOMFramework(BaseMetaFramework):
    """
    REMSOM: Regional Economic Multisectoral Open Model.
    
    Khipu's flagship meta-framework for regional economic simulation.
    REMSOM operates as a peer framework within the orchestration
    architecture, consuming and producing data for other frameworks.
    
    Community Tier Access:
        - Individual REMSOM indices (employment rate, sector output)
        - Static snapshots without simulation
    
    Enterprise Tier Access:
        - Full simulation with CBSSEngine
        - Policy shock analysis
        - Multi-period projections
        - DAG orchestration integration
    
    Example:
        >>> remsom = REMSOMFramework()
        >>> bundle = DataBundle.from_dataframes({
        ...     "labor": labor_df,
        ...     "economic": econ_df,
        ... })
        >>> result = remsom.fit(bundle).simulate(n_periods=20)
        >>> print(result.metrics["employment_rate"])
    
    Peer Framework Integration:
        REMSOM can consume outputs from:
        - MPI → deprivation-adjusted labor supply
        - HDI → human capital initialization
        - SPI → opportunity score calibration
        
        REMSOM produces outputs for:
        - Financial frameworks → sector output
        - Policy frameworks → employment projections
    """
    
    def __init__(
        self,
        remsom_config: Optional[REMSOMConfig] = None,
        seed: Optional[int] = None,
        user_parameters: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize REMSOM framework.
        
        Args:
            remsom_config: REMSOM-specific configuration.
            seed: Random seed for reproducibility.
            user_parameters: User-provided parameters (stored for envelope building).
        
        .. deprecated::
            REMSOMFramework (v1) is deprecated. Use REMSOMFrameworkV2 instead.
        """
        _emit_deprecation_warning()
        super().__init__()
        self.remsom_config = remsom_config or REMSOMConfig()
        self.seed = seed
        self._user_parameters = user_parameters or {}
        self._transition_fn = REMSOMTransition(self.remsom_config)
        self._engine: Optional[CBSSEngine] = None
        # Track which values came from data vs fallbacks
        self._data_fallbacks: dict[str, tuple[Any, str]] = {}
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        """Return REMSOM framework metadata."""
        return FrameworkMetadata(
            slug="remsom",
            name="Regional Economic Multisectoral Open Model",
            version="1.0.0",
            layer=VerticalLayer.META_PEER_FRAMEWORKS,
            tier=Tier.ENTERPRISE,  # Full simulation requires Enterprise
            description=(
                "Khipu's flagship meta-framework for regional economic "
                "simulation. Operates as peer framework within DAG "
                "orchestration, modeling cohort-based labor markets, "
                "multi-sector production, and human capital dynamics."
            ),
            required_domains=["labor", "economic"],
            output_domains=[
                "employment_rate",
                "sector_output",
                "human_capital_index",
                "health_adjusted_productivity",
            ],
            constituent_models=[
                "labor_market_simulator",
                "production_function",
                "human_capital_accumulator",
                "sector_linkage_model",
            ],
            tags=["meta", "remsom", "regional_economics", "simulation", "multisector"],
            author="Khipu Research Labs",
            license="Apache-2.0",
        )
    
    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Return REMSOM dashboard specification.
        
        REMSOM is the stress test for the generic dashboard template.
        If REMSOM renders correctly without special cases, any framework can.
        """
        return FrameworkDashboardSpec(
            slug="remsom",
            name="Regional Economic Multisectoral Open Model",
            description=(
                "Simulate regional economic dynamics across multiple sectors. "
                "Model cohort-based labor markets, production functions, and "
                "human capital accumulation under policy shocks."
            ),
            layer="meta",
            parameters_schema={
                "type": "object",
                "properties": {
                    # Model Structure
                    "n_sectors": {
                        "type": "integer",
                        "title": "Number of Sectors",
                        "description": "Number of economic sectors to model",
                        "minimum": 2,
                        "maximum": 20,
                        "default": 10,
                        "x-ui-widget": "slider",
                        "x-ui-step": 1,
                        "x-ui-group": "model_structure",
                        "x-ui-order": 1,
                    },
                    "n_age_groups": {
                        "type": "integer",
                        "title": "Age Cohorts",
                        "description": "Number of age cohort groups",
                        "minimum": 2,
                        "maximum": 10,
                        "default": 5,
                        "x-ui-widget": "slider",
                        "x-ui-step": 1,
                        "x-ui-group": "model_structure",
                        "x-ui-order": 2,
                    },
                    "sector_names": {
                        "type": "array",
                        "title": "Sector Names",
                        "description": "Names for each economic sector",
                        "items": {"type": "string"},
                        "default": [
                            "Agriculture", "Mining", "Manufacturing", "Utilities",
                            "Construction", "Trade", "Transportation", "Information",
                            "Finance", "Services"
                        ],
                        "x-ui-widget": "chips",
                        "x-ui-allow-custom": True,
                        "x-ui-group": "model_structure",
                        "x-ui-order": 3,
                    },
                    # Economic Parameters
                    "labor_elasticity": {
                        "type": "number",
                        "title": "Labor Elasticity",
                        "description": "Labor supply elasticity (ε)",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0.7,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.05,
                        "x-ui-group": "economic_parameters",
                        "x-ui-order": 1,
                    },
                    "capital_share": {
                        "type": "number",
                        "title": "Capital Share",
                        "description": "Capital share in Cobb-Douglas production (α)",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0.33,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.01,
                        "x-ui-unit": "",
                        "x-ui-group": "economic_parameters",
                        "x-ui-order": 2,
                    },
                    "depreciation_rate": {
                        "type": "number",
                        "title": "Depreciation Rate",
                        "description": "Annual capital depreciation rate (δ)",
                        "minimum": 0,
                        "maximum": 0.2,
                        "default": 0.05,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.005,
                        "x-ui-unit": "%",
                        "x-ui-format": ".1%",
                        "x-ui-group": "economic_parameters",
                        "x-ui-order": 3,
                    },
                    "discount_rate": {
                        "type": "number",
                        "title": "Discount Rate",
                        "description": "Time preference discount rate (ρ)",
                        "minimum": 0,
                        "maximum": 0.1,
                        "default": 0.03,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.005,
                        "x-ui-unit": "%",
                        "x-ui-format": ".1%",
                        "x-ui-group": "economic_parameters",
                        "x-ui-order": 4,
                    },
                    # Human Capital Parameters
                    "health_productivity_impact": {
                        "type": "number",
                        "title": "Health-Productivity Impact",
                        "description": "How health burden affects productivity",
                        "minimum": 0,
                        "maximum": 0.5,
                        "default": 0.15,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.01,
                        "x-ui-group": "human_capital",
                        "x-ui-order": 1,
                    },
                    "education_skill_premium": {
                        "type": "number",
                        "title": "Education Skill Premium",
                        "description": "Returns to education (β)",
                        "minimum": 0,
                        "maximum": 0.2,
                        "default": 0.08,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.01,
                        "x-ui-group": "human_capital",
                        "x-ui-order": 2,
                    },
                    # Simulation Parameters
                    "n_periods": {
                        "type": "integer",
                        "title": "Simulation Periods",
                        "description": "Number of time periods to simulate",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20,
                        "x-ui-widget": "slider",
                        "x-ui-step": 1,
                        "x-ui-unit": "years",
                        "x-ui-group": "simulation",
                        "x-ui-order": 1,
                    },
                    "tfp_growth": {
                        "type": "number",
                        "title": "TFP Growth Rate",
                        "description": "Total factor productivity annual growth",
                        "minimum": 0,
                        "maximum": 0.05,
                        "default": 0.015,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.001,
                        "x-ui-unit": "%",
                        "x-ui-format": ".1%",
                        "x-ui-group": "simulation",
                        "x-ui-order": 2,
                    },
                },
                "required": [],
            },
            default_parameters={
                "n_sectors": 10,
                "n_age_groups": 5,
                "sector_names": [
                    "Agriculture", "Mining", "Manufacturing", "Utilities",
                    "Construction", "Trade", "Transportation", "Information",
                    "Finance", "Services"
                ],
                "labor_elasticity": 0.7,
                "capital_share": 0.33,
                "depreciation_rate": 0.05,
                "discount_rate": 0.03,
                "health_productivity_impact": 0.15,
                "education_skill_premium": 0.08,
                "n_periods": 20,
                "tfp_growth": 0.015,
            },
            parameter_groups=[
                ParameterGroupSpec(
                    key="model_structure",
                    title="Model Structure",
                    description="Configure the sectoral and cohort structure",
                    collapsed_by_default=False,
                    parameters=["n_sectors", "n_age_groups", "sector_names"],
                ),
                ParameterGroupSpec(
                    key="economic_parameters",
                    title="Economic Parameters",
                    description="Core production function and market parameters",
                    collapsed_by_default=False,
                    parameters=["labor_elasticity", "capital_share", "depreciation_rate", "discount_rate"],
                ),
                ParameterGroupSpec(
                    key="human_capital",
                    title="Human Capital",
                    description="Health and education impact parameters",
                    collapsed_by_default=True,
                    parameters=["health_productivity_impact", "education_skill_premium"],
                ),
                ParameterGroupSpec(
                    key="simulation",
                    title="Simulation Settings",
                    description="Time horizon and growth assumptions",
                    collapsed_by_default=False,
                    parameters=["n_periods", "tfp_growth"],
                ),
            ],
            required_domains=["labor", "economic"],
            min_tier=Tier.ENTERPRISE,
            output_views=[
                # Summary Metrics
                OutputViewSpec(
                    key="summary_metrics",
                    title="Summary",
                    view_type=ViewType.METRIC_GRID,
                    description="Key performance indicators",
                    config={
                        "metrics": [
                            {"key": "total_output", "label": "Total Output", "format": "$,.0f"},
                            {"key": "employment_rate", "label": "Employment Rate", "format": ".1%"},
                            {"key": "human_capital_index", "label": "Human Capital Index", "format": ".2f"},
                            {"key": "gini_employment", "label": "Employment Gini", "format": ".3f"},
                        ]
                    },
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="summary_metrics_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                # Employment Trajectory
                OutputViewSpec(
                    key="employment_trajectory",
                    title="Employment",
                    view_type=ViewType.TIMESERIES,
                    description="Employment rate evolution over simulation period",
                    config={
                        "y_axis": "Employment Rate (%)",
                        "x_axis": "Period",
                        "series": [{"key": "employment_rate", "label": "Employment Rate"}],
                    },
                result_class=ResultClass.SCALAR_INDEX,
                output_key="employment_trajectory_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                # Sector Output
                OutputViewSpec(
                    key="sector_output",
                    title="Sector Output",
                    view_type=ViewType.BAR_CHART,
                    description="Economic output by sector",
                    config={
                        "x_axis": "Sector",
                        "y_axis": "Output",
                        "orientation": "horizontal",
                    },
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="sector_output_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                # Sector Output Trajectory
                OutputViewSpec(
                    key="sector_trajectory",
                    title="Sector Dynamics",
                    view_type=ViewType.AREA_CHART,
                    description="Sector output evolution (stacked)",
                    config={
                        "stacked": True,
                        "x_axis": "Period",
                        "y_axis": "Output",
                    },
                result_class=ResultClass.SCALAR_INDEX,
                output_key="sector_trajectory_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                # Health-Adjusted Productivity
                OutputViewSpec(
                    key="health_adjusted_productivity",
                    title="HAP Index",
                    view_type=ViewType.GAUGE,
                    description="Health-adjusted productivity index",
                    config={
                        "min": 0,
                        "max": 1,
                        "thresholds": [0.5, 0.7, 0.85],
                        "colors": ["#ef4444", "#f59e0b", "#22c55e"],
                    },
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="health_adjusted_productivity_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                # Cohort Vulnerability Heatmap
                OutputViewSpec(
                    key="cohort_vulnerability",
                    title="Vulnerability",
                    view_type=ViewType.HEATMAP,
                    description="Vulnerability scores by cohort and sector",
                    config={
                        "x_axis": "Sector",
                        "y_axis": "Cohort",
                        "color_scale": "RdYlGn",
                        "reverse_scale": True,
                    },
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="cohort_vulnerability_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                # Data Table
                OutputViewSpec(
                    key="detailed_results",
                    title="Data",
                    view_type=ViewType.TABLE,
                    description="Detailed simulation results",
                    config={
                        "columns": [
                            {"key": "period", "label": "Period"},
                            {"key": "employment_rate", "label": "Employment", "format": ".2%"},
                            {"key": "total_output", "label": "Output", "format": "$,.0f"},
                            {"key": "human_capital_index", "label": "HCI", "format": ".3f"},
                        ],
                        "sortable": True,
                        "filterable": True,
                    },
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="detailed_results_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
            documentation_url="https://docs.khipuresearch.com/frameworks/remsom",
            example_config={
                "n_sectors": 10,
                "labor_elasticity": 0.7,
                "n_periods": 20,
            },
        )
    
    def _validate_bundle(self, bundle: DataBundle) -> None:
        """Validate required data domains."""
        required = {"labor", "economic"}
        available = set(bundle.domains.keys())
        missing = required - available
        
        if missing:
            raise DataBundleValidationError(
                f"REMSOM requires domains: {required}. Missing: {missing}"
            )
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
    ) -> CohortStateVector:
        """
        Compute initial REMSOM state from data bundle.
        
        Extracts labor market, economic, and optional health/education
        data to initialize the cohort state vector.
        Tracks which values come from data vs. fallbacks.
        """
        self._validate_bundle(bundle)
        
        # Clear previous fallback tracking
        self._data_fallbacks = {}
        
        cfg = self.remsom_config
        
        # Get labor data (required)
        labor_data = bundle.get("labor").data
        n_cohorts = len(labor_data)
        
        # Employment probability from employment rate
        if "employment_rate" in labor_data.columns:
            employment_prob = labor_data["employment_rate"].values
        elif "unemployment_rate" in labor_data.columns:
            employment_prob = 1 - labor_data["unemployment_rate"].values
        else:
            employment_prob = np.full(n_cohorts, 0.65)
            self._data_fallbacks["employment_prob"] = (0.65, "No employment/unemployment rate in labor data")
        
        employment_prob = np.clip(employment_prob, 0.1, 0.98)
        
        # Economic data for sector output (required)
        econ_data = bundle.get("economic").data
        
        if "sector_output" in econ_data.columns:
            # Assume it's a multi-column or needs reshaping
            sector_output = np.full((n_cohorts, cfg.n_sectors), 100.0)
            self._data_fallbacks["sector_output"] = (100.0, "sector_output column format not parseable")
        elif "gdp" in econ_data.columns:
            gdp = econ_data["gdp"].values[:n_cohorts]
            # Distribute GDP across sectors using BEA-based shares
            sector_shares = np.array([0.05, 0.03, 0.12, 0.02, 0.06, 
                                      0.15, 0.08, 0.10, 0.14, 0.25])
            sector_output = gdp[:, np.newaxis] * sector_shares[np.newaxis, :]
        else:
            sector_output = np.full((n_cohorts, cfg.n_sectors), 100.0)
            self._data_fallbacks["sector_output"] = (100.0, "No GDP or sector_output in economic data")
        
        # Health data (optional)
        health_data = bundle.get("health") if bundle.has_domain("health") else None
        if health_data is not None and "mortality_rate" in health_data.data.columns:
            mortality = health_data.data["mortality_rate"].values[:n_cohorts]
            health_burden = np.clip(mortality * 30, 0.05, 0.6)
        else:
            health_burden = np.full(n_cohorts, 0.2)
            self._data_fallbacks["health_burden_score"] = (0.2, "No health data - using default burden")
        
        # Education data (optional) → opportunity score
        edu_data = bundle.get("education") if bundle.has_domain("education") else None
        if edu_data is not None:
            edu_df = edu_data.data
            if "hs_graduation_rate" in edu_df.columns:
                opportunity = edu_df["hs_graduation_rate"].values[:n_cohorts]
            else:
                opportunity = np.full(n_cohorts, 0.5)
                self._data_fallbacks["opportunity_score"] = (0.5, "No hs_graduation_rate in education data")
        else:
            opportunity = np.full(n_cohorts, 0.5)
            self._data_fallbacks["opportunity_score"] = (0.5, "No education data provided")
        
        opportunity = np.clip(opportunity, 0.1, 0.9)
        
        # Credit access (derived from employment and opportunity)
        credit_access = np.clip(
            0.3 + 0.4 * employment_prob + 0.3 * opportunity,
            0.2, 0.9
        )
        
        # Housing cost ratio (placeholder)
        housing_ratio = np.full(n_cohorts, 0.3)
        self._data_fallbacks["housing_cost_ratio"] = (0.3, "Housing data not yet connected")
        
        # Deprivation vector (6 dims)
        deprivation = np.column_stack([
            health_burden,
            1 - opportunity,
            1 - credit_access,
            housing_ratio,
            1 - employment_prob * 0.5,
            np.random.uniform(0.1, 0.3, n_cohorts),
        ])
        
        return CohortStateVector(
            employment_prob=employment_prob,
            health_burden_score=np.clip(health_burden, 0, 1),
            credit_access_prob=credit_access,
            housing_cost_ratio=housing_ratio,
            opportunity_score=opportunity,
            sector_output=sector_output,
            deprivation_vector=np.clip(deprivation, 0, 1),
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        t: int,
    ) -> CohortStateVector:
        """Apply REMSOM transition dynamics."""
        return self._transition_fn(state, t, self.config)
    
    def _compute_metrics(
        self,
        state: CohortStateVector,
    ) -> dict[str, Any]:
        """Compute REMSOM metrics from final cohort state."""
        return self._compute_remsom_metrics(state).to_dict()
    
    def _compute_remsom_metrics(
        self,
        state: CohortStateVector,
    ) -> REMSOMMetrics:
        """
        Compute REMSOM metrics from cohort state.
        
        Aggregates cohort-level data into model outputs.
        """
        cfg = self.remsom_config
        
        # Aggregate employment
        employment_rate = float(state.employment_prob.mean())
        
        # Sector-level aggregates
        sector_totals = state.sector_output.sum(axis=0)
        total_output = float(sector_totals.sum())
        
        sector_employment = {}
        sector_output = {}
        for i, name in enumerate(cfg.sector_names[:cfg.n_sectors]):
            sector_output[name] = float(sector_totals[i])
            # Estimate sector employment (proportional to output)
            sector_employment[name] = float(
                employment_rate * sector_totals[i] / max(total_output, 1e-6)
            )
        
        # Human capital index
        human_capital = float(
            state.opportunity_score.mean() * 
            (1 - state.health_burden_score.mean())
        )
        
        # Health-adjusted productivity
        hap = float(
            (1 - state.health_burden_score.mean()) * 
            (1 + cfg.education_skill_premium * state.opportunity_score.mean())
        )
        
        # Employment Gini coefficient
        employment_sorted = np.sort(state.employment_prob)
        n = len(employment_sorted)
        cumulative = np.cumsum(employment_sorted)
        gini_employment = float(
            (n + 1 - 2 * np.sum(cumulative) / cumulative[-1]) / n
        ) if n > 0 and cumulative[-1] > 0 else 0.0
        
        # Cohort vulnerability (composite risk score)
        vulnerability = (
            0.3 * (1 - state.employment_prob) +
            0.2 * state.health_burden_score +
            0.2 * (1 - state.credit_access_prob) +
            0.15 * state.housing_cost_ratio +
            0.15 * (1 - state.opportunity_score)
        )
        
        return REMSOMMetrics(
            total_output=total_output,
            employment_rate=employment_rate,
            sector_employment=sector_employment,
            sector_output=sector_output,
            human_capital_index=human_capital,
            health_adjusted_productivity=hap,
            gini_employment=gini_employment,
            cohort_vulnerability=vulnerability,
        )
    
    def build_output_envelope(
        self,
        result: FrameworkExecutionResult,
        user_parameters: dict[str, Any] | None = None,
    ) -> "FrameworkOutputEnvelope":
        """
        Build a self-describing output envelope for REMSOM results.
        
        REMSOM is the sole authority over its output schema. This method
        produces an envelope that declares canonical dimensions and
        framework-unique outputs. The API layer must pass through unchanged.
        
        Args:
            result: FrameworkExecutionResult from simulation.
            user_parameters: Original user parameters (for provenance).
        
        Returns:
            FrameworkOutputEnvelope with REMSOM-specific structure.
        """
        from krl_frameworks.core.output_envelope import (
            DimensionManifest,
            FrameworkOutputEnvelope,
            ProvenanceRecord,
        )
        
        # Use provided params, fall back to stored params, then empty
        user_params = user_parameters or self._user_parameters or {}
        cfg = self.remsom_config
        
        # Build canonical dimensions from config
        # User-provided sector names take precedence
        sector_names = user_params.get("sector_names", list(cfg.sector_names[:cfg.n_sectors]))
        if isinstance(sector_names, tuple):
            sector_names = list(sector_names)
        
        # Build cohort labels from age groups
        n_age = user_params.get("n_age_groups", cfg.n_age_groups)
        cohort_labels = self._generate_cohort_labels(n_age)
        
        # Build time period labels
        n_periods = user_params.get("n_periods", result.steps_executed or 20)
        base_year = user_params.get("base_year", 2024)
        time_periods = list(range(base_year, base_year + n_periods + 1))
        
        # Geographic scope
        geography = user_params.get("geo_scope", user_params.get("geography", "National"))
        
        # Create dimension manifest
        dimensions = DimensionManifest(
            sectors=tuple(sector_names),
            time_periods=tuple(time_periods),
            cohorts=tuple(cohort_labels),
            geography=geography,
        )
        
        # Build provenance record
        provenance = self._build_provenance_record(user_params, result)
        
        # Build structured outputs using canonical dimensions
        outputs = self._build_structured_outputs(result, dimensions)
        
        return FrameworkOutputEnvelope(
            framework_slug=self.metadata().slug,
            framework_version=self.metadata().version,
            dimensions=dimensions,
            provenance=provenance,
            outputs=outputs,
            metadata={
                "execution_id": result.execution_id,
                "steps_executed": result.steps_executed,
                "converged": result.converged,
                "duration_ms": result.duration_ms,
                "remsom_config": {
                    "n_sectors": cfg.n_sectors,
                    "n_age_groups": cfg.n_age_groups,
                    "labor_elasticity": cfg.labor_elasticity,
                    "capital_share": cfg.capital_share,
                },
            },
        )
    
    def _generate_cohort_labels(self, n_age_groups: int) -> list[str]:
        """Generate age cohort labels based on number of groups."""
        if n_age_groups <= 0:
            return ["All Ages"]
        
        # Standard age brackets
        brackets = [
            "18-24", "25-34", "35-44", "45-54", "55-64",
            "65-74", "75-84", "85+",
        ]
        
        if n_age_groups <= len(brackets):
            return brackets[:n_age_groups]
        
        # Generate generic labels if more groups needed
        return [f"Cohort {i+1}" for i in range(n_age_groups)]
    
    def _build_provenance_record(
        self,
        user_params: dict[str, Any],
        result: FrameworkExecutionResult,
    ) -> ProvenanceRecord:
        """Build provenance record tracking user inputs and fallbacks."""
        from krl_frameworks.core.output_envelope import ProvenanceRecord
        
        cfg = self.remsom_config
        provenance = ProvenanceRecord(
            user_parameters=user_params,
            data_hash=result.data_hash,
        )
        
        # Track data-driven fallbacks from _compute_initial_state
        for param_name, (value, reason) in getattr(self, '_data_fallbacks', {}).items():
            provenance.add_fallback(param_name, value, reason)
        
        # Track fallbacks for economic constants not provided by user
        if "labor_elasticity" not in user_params:
            provenance.add_fallback(
                "labor_elasticity",
                cfg.labor_elasticity,
                "Using default labor supply elasticity"
            )
        
        if "capital_share" not in user_params:
            provenance.add_fallback(
                "capital_share",
                cfg.capital_share,
                "Using default Cobb-Douglas capital share"
            )
        
        if "depreciation_rate" not in user_params:
            provenance.add_fallback(
                "depreciation_rate",
                cfg.depreciation_rate,
                "Using default capital depreciation rate"
            )
        
        if "discount_rate" not in user_params:
            provenance.add_fallback(
                "discount_rate",
                cfg.discount_rate,
                "Using default time preference discount rate"
            )
        
        if "sector_names" not in user_params:
            provenance.add_fallback(
                "sector_names",
                list(cfg.sector_names),
                "Using default NAICS-inspired sector names"
            )
        
        # Add simulation params for reproducibility
        provenance.simulation_params = {
            "random_seed": getattr(self, "seed", None),
            "n_periods": result.steps_executed,
            "convergence_method": str(self.config.simulation.convergence_method) if self.config else "FIXED_STEPS",
        }
        
        return provenance
    
    def _to_json_serializable(self, value: Any) -> Any:
        """Convert numpy types to native Python for JSON serialization."""
        if hasattr(value, 'item'):  # numpy scalar
            return value.item()
        elif hasattr(value, 'tolist'):  # numpy array
            return value.tolist()
        elif isinstance(value, dict):
            return {k: self._to_json_serializable(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [self._to_json_serializable(v) for v in value]
        return value
    
    def _build_structured_outputs(
        self,
        result: FrameworkExecutionResult,
        dimensions: "DimensionManifest",
    ) -> dict[str, Any]:
        """Build structured outputs using canonical dimensions. All values JSON-serializable."""
        from krl_frameworks.core.output_envelope import DimensionManifest
        
        metrics = result.metrics
        sector_names = list(dimensions.sectors)
        
        # Sector employment - keyed by canonical sector names, ensure float
        sector_employment_raw = metrics.get("sector_employment", {})
        sector_employment = {}
        for i, name in enumerate(sector_names):
            val = sector_employment_raw.get(name, sector_employment_raw.get(f"Sector_{i}", 0.0))
            sector_employment[name] = float(val) if hasattr(val, 'item') else float(val)
        
        # Sector output - keyed by canonical sector names, ensure float
        sector_output_raw = metrics.get("sector_output", {})
        sector_output = {}
        for i, name in enumerate(sector_names):
            val = sector_output_raw.get(name, sector_output_raw.get(f"Sector_{i}", 100.0))
            sector_output[name] = float(val) if hasattr(val, 'item') else float(val)
        
        # Build trajectory data if available - all values as native Python types
        trajectory_data = []
        if result.trajectory:
            for step, state in enumerate(result.trajectory.states):
                step_metrics = self._compute_remsom_metrics(state)
                step_data = {
                    "period": int(dimensions.time_periods[step]) if step < len(dimensions.time_periods) else int(step),
                    "employment_rate": float(step_metrics.employment_rate),
                    "total_output": float(step_metrics.total_output),
                    "human_capital_index": float(step_metrics.human_capital_index),
                    "health_adjusted_productivity": float(step_metrics.health_adjusted_productivity),
                    "sector_output": {
                        name: float(step_metrics.sector_output.get(name, 0.0))
                        for name in sector_names
                    },
                }
                trajectory_data.append(step_data)
        
        # Cohort vulnerability heatmap - using canonical dimensions
        vulnerability_heatmap = {
            "rows": list(dimensions.cohorts),
            "columns": sector_names,
            "data": [],  # Will be filled from state if available
        }
        
        if result.state and hasattr(result.state, "sector_output"):
            # Build heatmap from final state
            n_cohorts = min(len(dimensions.cohorts), result.state.n_cohorts)
            n_sectors = min(len(sector_names), result.state.n_sectors)
            
            cohort_vuln = float(metrics.get("mean_vulnerability", 0.3))
            for i in range(n_cohorts):
                row = []
                for j in range(n_sectors):
                    # Estimate sector-specific vulnerability
                    base_vuln = cohort_vuln + (i * 0.02) - (j * 0.01)
                    row.append(float(round(np.clip(base_vuln, 0, 1), 3)))
                vulnerability_heatmap["data"].append(row)
        
        # Ensure all numeric values are native Python types
        return {
            # Summary metrics - explicitly convert to float
            "employment_rate": float(metrics.get("employment_rate", 0.0)),
            "total_output": float(metrics.get("total_output", 0.0)),
            "human_capital_index": float(metrics.get("human_capital_index", 0.0)),
            "health_adjusted_productivity": float(metrics.get("health_adjusted_productivity", 0.0)),
            "gini_employment": float(metrics.get("gini_employment", 0.0)),
            "mean_vulnerability": float(metrics.get("mean_vulnerability", 0.0)),
            "max_vulnerability": float(metrics.get("max_vulnerability", 0.0)),
            
            # Sector-level outputs (keyed by canonical sector names)
            "sector_employment": sector_employment,
            "sector_output": sector_output,
            
            # Trajectory data (time-indexed)
            "trajectory": trajectory_data,
            
            # Heatmap (cohort × sector)
            "vulnerability_heatmap": vulnerability_heatmap,
        }

    @requires_tier(Tier.ENTERPRISE)
    def run_simulation(
        self,
        bundle: DataBundle,
        n_periods: int = 20,
        policy_shocks: Optional[Sequence[PolicyShock]] = None,
        config: Optional[FrameworkConfig] = None,
    ) -> SimulationResult:
        """
        Run full REMSOM simulation with CBSS engine.
        
        Enterprise-tier feature for multi-period projections
        with policy shock analysis.
        
        Args:
            bundle: Data bundle with labor and economic data.
            n_periods: Number of simulation periods.
            policy_shocks: Optional policy interventions.
            config: Framework configuration.
            
        Returns:
            SimulationResult with trajectory and metrics.
        """
        from krl_frameworks.core.config import FrameworkConfig
        
        config = config or FrameworkConfig(n_periods=n_periods)
        self.config = config  # Store for use in _compute_initial_state
        
        # Initialize state from bundle
        initial_state = self._compute_initial_state(bundle)
        
        # Create CBSS engine
        engine = CBSSEngine(seed=self.seed)
        
        # Run simulation
        result = engine.simulate(
            initial_state=initial_state,
            transition_fn=self._transition_fn,
            n_periods=n_periods,
            config=config,
            policy_shocks=policy_shocks,
        )
        
        # Add REMSOM-specific metrics
        result.metrics = self._compute_remsom_metrics(result.final_state).to_dict()
        
        return result
    
    def compute_static_metrics(
        self,
        bundle: DataBundle,
        config: Optional[FrameworkConfig] = None,
    ) -> REMSOMMetrics:
        """
        Compute REMSOM metrics without simulation.
        
        Available at COMMUNITY tier for static analysis.
        
        Args:
            bundle: Data bundle with labor and economic data.
            config: Framework configuration.
            
        Returns:
            REMSOMMetrics from initial state.
        """
        from krl_frameworks.core.config import FrameworkConfig
        config = config or FrameworkConfig()
        self.config = config  # Store for use in _compute_initial_state
        
        state = self._compute_initial_state(bundle)
        return self._compute_remsom_metrics(state)
    
    @requires_tier(Tier.ENTERPRISE)
    def run_scenario_analysis(
        self,
        bundle: DataBundle,
        scenarios: Sequence[Sequence[PolicyShock]],
        n_periods: int = 20,
        config: Optional[FrameworkConfig] = None,
    ) -> list[SimulationResult]:
        """
        Run multiple scenarios with different policy shock combinations.
        
        Enterprise-tier feature for comparative policy analysis.
        
        Args:
            bundle: Data bundle with labor and economic data.
            scenarios: List of policy shock sequences (one per scenario).
            n_periods: Periods per scenario.
            config: Framework configuration.
            
        Returns:
            List of SimulationResult, one per scenario.
        """
        results = []
        for i, shocks in enumerate(scenarios):
            logger.info(f"Running scenario {i+1}/{len(scenarios)}")
            result = self.run_simulation(
                bundle=bundle,
                n_periods=n_periods,
                policy_shocks=shocks,
                config=config,
            )
            result.diagnostics["scenario_index"] = i
            results.append(result)
        
        return results
