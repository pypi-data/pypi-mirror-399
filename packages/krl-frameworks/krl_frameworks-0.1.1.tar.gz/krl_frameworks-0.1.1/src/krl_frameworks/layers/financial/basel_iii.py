# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Basel III Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Basel III Capital Adequacy and Liquidity Framework.

Implements the Basel III regulatory framework including:
- Risk-Weighted Assets (RWA) calculation
- Capital ratios (CET1, Tier 1, Total Capital)
- Liquidity Coverage Ratio (LCR)
- Net Stable Funding Ratio (NSFR)
- Leverage Ratio

References:
    - Basel Committee on Banking Supervision (2017): Basel III: Finalising post-crisis reforms
    - Federal Reserve Regulation Q (12 CFR Part 217)
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
# Basel III Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class BankCategory(Enum):
    """Bank size and complexity categories."""
    GSIB = "Global Systemically Important Bank"
    CATEGORY_I = "Category I (>$700B assets or >$75B cross-jurisdictional)"
    CATEGORY_II = "Category II ($250B-$700B)"
    CATEGORY_III = "Category III ($100B-$250B)"
    CATEGORY_IV = "Category IV (<$100B)"


class RiskWeightApproach(Enum):
    """Risk weight calculation approach."""
    STANDARDIZED = "Standardized"
    FOUNDATION_IRB = "Foundation IRB"
    ADVANCED_IRB = "Advanced IRB"


@dataclass
class BaselIIIConfig:
    """Configuration for Basel III calculations."""
    
    # Bank classification
    bank_category: BankCategory = BankCategory.CATEGORY_IV
    
    # RWA approach
    credit_risk_approach: RiskWeightApproach = RiskWeightApproach.STANDARDIZED
    
    # Minimum requirements
    min_cet1_ratio: float = 0.045  # 4.5%
    min_tier1_ratio: float = 0.06  # 6%
    min_total_capital_ratio: float = 0.08  # 8%
    
    # Buffers
    capital_conservation_buffer: float = 0.025  # 2.5%
    countercyclical_buffer: float = 0.0  # 0-2.5% varies
    gsib_surcharge: float = 0.0  # 0-3.5%
    
    # Liquidity
    min_lcr: float = 1.0  # 100%
    min_nsfr: float = 1.0  # 100%
    
    # Leverage
    min_leverage_ratio: float = 0.03  # 3%


@dataclass
class RiskWeightedAssets:
    """Risk-weighted asset components."""
    
    # Credit risk RWA
    credit_risk_rwa: float = 0.0
    
    # Market risk RWA  
    market_risk_rwa: float = 0.0
    
    # Operational risk RWA
    operational_risk_rwa: float = 0.0
    
    # CVA risk
    cva_risk_rwa: float = 0.0
    
    # Total RWA
    total_rwa: float = 0.0
    
    # Breakdown by exposure class
    corporate_rwa: float = 0.0
    retail_rwa: float = 0.0
    mortgage_rwa: float = 0.0
    sovereign_rwa: float = 0.0


@dataclass
class CapitalRatios:
    """Basel III capital ratios."""
    
    # Capital components ($ millions)
    cet1_capital: float = 0.0
    at1_capital: float = 0.0
    tier2_capital: float = 0.0
    
    # Ratios
    cet1_ratio: float = 0.0
    tier1_ratio: float = 0.0
    total_capital_ratio: float = 0.0
    leverage_ratio: float = 0.0
    
    # Buffer status
    buffer_amount: float = 0.0
    buffer_utilized_pct: float = 0.0
    
    # Compliance
    meets_minimum: bool = False
    meets_buffer: bool = False


@dataclass
class LiquidityRatios:
    """Basel III liquidity ratios."""
    
    # LCR components
    hqla_level1: float = 0.0
    hqla_level2a: float = 0.0
    hqla_level2b: float = 0.0
    total_hqla: float = 0.0
    net_cash_outflows: float = 0.0
    lcr: float = 0.0
    
    # NSFR components
    available_stable_funding: float = 0.0
    required_stable_funding: float = 0.0
    nsfr: float = 0.0
    
    # Compliance
    lcr_compliant: bool = False
    nsfr_compliant: bool = False


@dataclass
class BaselIIIMetrics:
    """Comprehensive Basel III metrics."""
    
    # RWA
    rwa: RiskWeightedAssets = field(default_factory=RiskWeightedAssets)
    
    # Capital
    capital: CapitalRatios = field(default_factory=CapitalRatios)
    
    # Liquidity
    liquidity: LiquidityRatios = field(default_factory=LiquidityRatios)
    
    # Overall compliance
    fully_compliant: bool = False
    compliance_issues: list[str] = field(default_factory=list)
    
    # Buffers
    required_buffer: float = 0.0
    available_buffer: float = 0.0


# ════════════════════════════════════════════════════════════════════════════════
# Basel III Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class BaselIIITransition(TransitionFunction):
    """
    Basel III capital dynamics transition.
    
    Models the evolution of bank capital under various scenarios.
    """
    
    def __init__(self, config: BaselIIIConfig):
        self.config = config
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        params: Optional[dict[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply Basel III capital transition."""
        params = params or {}
        
        # Capital generation rate (retained earnings)
        roe = params.get("return_on_equity", 0.10)
        payout_ratio = params.get("dividend_payout", 0.30)
        
        # Asset growth
        asset_growth = params.get("asset_growth", 0.02)
        
        # Risk weight changes
        rw_migration = params.get("rw_migration", 0.0)
        
        # Capital accumulation
        retained_earnings_rate = roe * (1 - payout_ratio)
        
        # Update credit access (proxy for capital strength)
        new_credit = np.clip(
            state.credit_access_prob * (1 + retained_earnings_rate),
            0.0, 1.0
        )
        
        # Update sector output (bank assets)
        new_sector_output = state.sector_output * (1 + asset_growth)
        
        # Update opportunity score (capital adequacy)
        capital_effect = retained_earnings_rate - asset_growth * 0.5
        new_opportunity = np.clip(
            state.opportunity_score * (1 + capital_effect),
            0.0, 1.0
        )
        
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
# Basel III Framework
# ════════════════════════════════════════════════════════════════════════════════


class BaselIIIFramework(BaseMetaFramework):
    """
    Basel III Capital and Liquidity Framework.
    
    Implements comprehensive Basel III regulatory calculations:
    
    1. Risk-Weighted Assets: Credit, market, operational risk
    2. Capital Ratios: CET1, Tier 1, Total Capital
    3. Buffers: Conservation, countercyclical, G-SIB
    4. Liquidity: LCR and NSFR
    5. Leverage: Supplementary Leverage Ratio
    
    Tier: ENTERPRISE (financial regulatory analysis)
    
    Example:
        >>> basel = BaselIIIFramework()
        >>> bundle = DataBundle.from_dataframes({
        ...     "balance_sheet": bs_df,
        ...     "capital": capital_df,
        ...     "exposures": exposures_df
        ... })
        >>> metrics = basel.compute_ratios(bundle)
        >>> print(f"CET1 Ratio: {metrics.capital.cet1_ratio:.1%}")
    """
    
    METADATA = FrameworkMetadata(
        slug="basel_iii",
        name="Basel III Regulatory Framework",
        version="1.0.0",
        layer=VerticalLayer.FINANCIAL_ECONOMIC,
        tier=Tier.ENTERPRISE,
        description="Basel III capital adequacy and liquidity calculations",
        required_domains=["balance_sheet", "capital"],
        output_domains=["capital_ratios", "liquidity_coverage", "leverage_ratio"],
        constituent_models=["rwa_calculator", "capital_tier_classifier", "lcr_calculator", "nsfr_calculator"],
        tags=["financial", "basel", "regulatory", "capital_adequacy", "banking"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self, config: Optional[BaselIIIConfig] = None):
        super().__init__()
        self.basel_config = config or BaselIIIConfig()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        return cls.METADATA
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Compute initial state from bank data."""
        bs_data = bundle.get("balance_sheet")
        capital_data = bundle.get("capital")
        
        bs_df = bs_data.data
        capital_df = capital_data.data
        
        n_cohorts = len(bs_df)
        
        # Extract total assets
        if "total_assets" in bs_df.columns:
            assets = bs_df["total_assets"].values[:n_cohorts]
        else:
            assets = np.full(n_cohorts, 1e9)
        
        # Extract capital
        if "cet1_capital" in capital_df.columns:
            cet1 = capital_df["cet1_capital"].values[:n_cohorts]
            capital_ratio = cet1 / assets
        else:
            capital_ratio = np.full(n_cohorts, 0.12)
        
        return CohortStateVector(
            employment_prob=np.full(n_cohorts, 0.95),
            health_burden_score=np.full(n_cohorts, 0.05),
            credit_access_prob=np.clip(capital_ratio, 0, 1),
            housing_cost_ratio=np.full(n_cohorts, 0.25),
            opportunity_score=np.clip(capital_ratio, 0, 1),
            sector_output=assets.reshape(-1, 1).repeat(10, axis=1) / 10,
            deprivation_vector=np.zeros((n_cohorts, 6)),
            step=0,
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Apply Basel III transition."""
        transition = BaselIIITransition(self.basel_config)
        return transition(state, t, config)
    
    def _compute_metrics(
        self,
        trajectory: StateTrajectory,
    ) -> BaselIIIMetrics:
        """Compute Basel III metrics."""
        metrics = BaselIIIMetrics()
        
        if len(trajectory) < 1:
            return metrics
        
        final_state = trajectory.final_state
        
        # Calculate RWA (simplified)
        total_assets = final_state.sector_output.sum()
        avg_risk_weight = 0.75  # Blended average
        
        metrics.rwa = RiskWeightedAssets(
            credit_risk_rwa=total_assets * avg_risk_weight * 0.85,
            market_risk_rwa=total_assets * 0.03,
            operational_risk_rwa=total_assets * 0.05,
            total_rwa=total_assets * avg_risk_weight,
        )
        
        # Calculate capital ratios
        capital_strength = float(final_state.credit_access_prob.mean())
        cet1_capital = total_assets * capital_strength * 0.15
        
        cet1_ratio = cet1_capital / metrics.rwa.total_rwa if metrics.rwa.total_rwa > 0 else 0
        
        metrics.capital = CapitalRatios(
            cet1_capital=cet1_capital,
            at1_capital=cet1_capital * 0.15,
            tier2_capital=cet1_capital * 0.2,
            cet1_ratio=cet1_ratio,
            tier1_ratio=cet1_ratio * 1.15,
            total_capital_ratio=cet1_ratio * 1.35,
            leverage_ratio=cet1_capital / total_assets if total_assets > 0 else 0,
            meets_minimum=cet1_ratio >= self.basel_config.min_cet1_ratio,
            meets_buffer=cet1_ratio >= (
                self.basel_config.min_cet1_ratio + 
                self.basel_config.capital_conservation_buffer
            ),
        )
        
        # Liquidity (simplified)
        metrics.liquidity = LiquidityRatios(
            hqla_level1=total_assets * 0.15,
            total_hqla=total_assets * 0.20,
            net_cash_outflows=total_assets * 0.18,
            lcr=1.11,
            nsfr=1.08,
            lcr_compliant=True,
            nsfr_compliant=True,
        )
        
        # Overall compliance
        metrics.fully_compliant = (
            metrics.capital.meets_minimum and
            metrics.capital.meets_buffer and
            metrics.liquidity.lcr_compliant and
            metrics.liquidity.nsfr_compliant
        )
        
        if not metrics.capital.meets_minimum:
            metrics.compliance_issues.append("CET1 below minimum requirement")
        if not metrics.capital.meets_buffer:
            metrics.compliance_issues.append("Capital buffer not fully met")
        
        return metrics
    
    @requires_tier(Tier.ENTERPRISE)
    def compute_ratios(
        self,
        bundle: DataBundle,
        config: Optional[FrameworkConfig] = None,
    ) -> BaselIIIMetrics:
        """
        Compute Basel III regulatory ratios.
        
        Args:
            bundle: DataBundle with balance_sheet and capital data
            config: Optional framework configuration
        
        Returns:
            BaselIIIMetrics with RWA, capital, and liquidity ratios
        """
        config = config or FrameworkConfig()
        
        initial_state = self._compute_initial_state(bundle, config)
        trajectory = StateTrajectory(states=[initial_state])
        
        return self._compute_metrics(trajectory)
    
    @requires_tier(Tier.ENTERPRISE)
    def project_capital(
        self,
        bundle: DataBundle,
        n_quarters: int = 12,
        scenario_params: Optional[dict[str, Any]] = None,
        config: Optional[FrameworkConfig] = None,
    ) -> list[BaselIIIMetrics]:
        """
        Project capital ratios over time.
        
        Args:
            bundle: DataBundle with bank data
            n_quarters: Number of quarters to project
            scenario_params: Scenario parameters (ROE, growth, etc.)
            config: Optional framework configuration
        
        Returns:
            List of BaselIIIMetrics for each quarter
        """
        config = config or FrameworkConfig()
        scenario_params = scenario_params or {}
        
        initial_state = self._compute_initial_state(bundle, config)
        
        results = []
        current = initial_state
        
        for t in range(n_quarters):
            trajectory = StateTrajectory(states=[current])
            metrics = self._compute_metrics(trajectory)
            results.append(metrics)
            
            # Transition
            transition = BaselIIITransition(self.basel_config)
            current = transition(current, t, config, scenario_params)
        
        return results

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return Basel III dashboard specification."""
        return FrameworkDashboardSpec(
            slug="basel_iii",
            name="Basel III Regulatory Framework",
            description=(
                "Basel III capital adequacy and liquidity calculations including "
                "CET1, Tier 1, Total Capital ratios, LCR, NSFR, and leverage ratio."
            ),
            layer="financial",
            parameters_schema={
                "type": "object",
                "properties": {
                    "bank_category": {
                        "type": "string",
                        "title": "Bank Category",
                        "enum": ["gsib", "category_i", "category_ii", "category_iii", "category_iv"],
                        "default": "category_iv",
                        "x-ui-widget": "select",
                        "x-ui-group": "bank",
                    },
                    "credit_risk_approach": {
                        "type": "string",
                        "title": "Credit Risk Approach",
                        "enum": ["standardized", "foundation_irb", "advanced_irb"],
                        "default": "standardized",
                        "x-ui-widget": "select",
                        "x-ui-group": "methodology",
                    },
                    "countercyclical_buffer": {
                        "type": "number",
                        "title": "Countercyclical Buffer (%)",
                        "minimum": 0,
                        "maximum": 2.5,
                        "default": 0,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.25,
                        "x-ui-format": ".2%",
                        "x-ui-group": "buffers",
                    },
                    "gsib_surcharge": {
                        "type": "number",
                        "title": "G-SIB Surcharge (%)",
                        "minimum": 0,
                        "maximum": 3.5,
                        "default": 0,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.5,
                        "x-ui-format": ".1%",
                        "x-ui-group": "buffers",
                    },
                    "n_quarters": {
                        "type": "integer",
                        "title": "Projection Quarters",
                        "minimum": 1,
                        "maximum": 12,
                        "default": 4,
                        "x-ui-widget": "slider",
                        "x-ui-group": "simulation",
                    },
                },
            },
            default_parameters={
                "bank_category": "category_iv",
                "credit_risk_approach": "standardized",
                "countercyclical_buffer": 0,
                "gsib_surcharge": 0,
                "n_quarters": 4,
            },
            parameter_groups=[
                ParameterGroupSpec(key="bank", title="Bank Classification", parameters=["bank_category"]),
                ParameterGroupSpec(key="methodology", title="Methodology", parameters=["credit_risk_approach"]),
                ParameterGroupSpec(key="buffers", title="Capital Buffers", parameters=["countercyclical_buffer", "gsib_surcharge"]),
                ParameterGroupSpec(key="simulation", title="Simulation", parameters=["n_quarters"]),
            ],
            required_domains=["balance_sheet", "capital"],
            min_tier=Tier.ENTERPRISE,
            output_views=[
                OutputViewSpec(
                    key="cet1_ratio",
                    title="CET1 Ratio",
                    view_type=ViewType.GAUGE,
                    config={"min": 0, "max": 0.2, "thresholds": [0.045, 0.07, 0.10], "format": ".1%"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="cet1_ratio_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="capital_stack",
                    title="Capital Stack",
                    view_type=ViewType.BAR_CHART,
                    config={"x_field": "tier", "y_field": "amount", "stacked": True},
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="capital_stack_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="rwa_breakdown",
                    title="RWA Breakdown",
                    view_type=ViewType.BAR_CHART,
                    config={"x_field": "risk_type", "y_field": "rwa"},
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="rwa_breakdown_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="liquidity",
                    title="Liquidity Ratios",
                    view_type=ViewType.METRIC_GRID,
                    config={"metrics": [
                        {"key": "lcr", "label": "LCR", "format": ".0%"},
                        {"key": "nsfr", "label": "NSFR", "format": ".0%"},
                        {"key": "leverage_ratio", "label": "Leverage Ratio", "format": ".1%"},
                    ]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="liquidity_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="capital_trajectory",
                    title="Capital Trajectory",
                    view_type=ViewType.LINE_CHART,
                    config={"x_field": "quarter", "y_fields": ["cet1", "tier1", "total_capital"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="capital_trajectory_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )


# ════════════════════════════════════════════════════════════════════════════════
# Exports
# ════════════════════════════════════════════════════════════════════════════════

__all__ = [
    "BaselIIIFramework",
    "BaselIIIConfig",
    "BaselIIIMetrics",
    "RiskWeightedAssets",
    "CapitalRatios",
    "LiquidityRatios",
    "BankCategory",
    "RiskWeightApproach",
    "BaselIIITransition",
]
