# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Social Accounting Matrix - CGE (SAM-CGE)
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Social Accounting Matrix - Computable General Equilibrium (SAM-CGE) Framework.

A SAM-CGE model combines Social Accounting Matrix (SAM) data with Computable
General Equilibrium (CGE) modeling to analyze economy-wide impacts of policy
changes, shocks, or structural transformations.

Methodology:
    - SAM: Comprehensive snapshot of economy (production, income, expenditure)
    - CGE: Multi-sector equilibrium model with price endogeneity
    - Production: CES/Cobb-Douglas functions by sector
    - Consumption: Linear Expenditure System (LES)
    - Market Clearing: Walrasian equilibrium across all markets
    - Numeraire: Fix one price (usually labor) for homogeneity

CBSS Integration:
    - State vector: Sector outputs, prices, household incomes, trade flows
    - Transition: Iterative equilibrium solver (Gauss-Seidel or Newton-Raphson)
    - Metrics: GDP, employment, wage rates, sector outputs, welfare

Key Features:
    - Multi-sector production (agriculture, industry, services)
    - Factor markets (labor, capital)
    - Household consumption with income elasticities
    - Government revenue/expenditure
    - International trade (imports, exports)
    - Market equilibrium conditions

Data Requirements:
    - SAM table (Make/Use matrices from BEA Input-Output tables)
    - Elasticities (production, consumption, trade)
    - Base year quantities and prices

References:
    - Lofgren, H., Harris, R. L., & Robinson, S. (2002). "A Standard Computable
      General Equilibrium (CGE) Model in GAMS." International Food Policy
      Research Institute (IFPRI) Microcomputers in Policy Research 5.
    - Dervis, K., de Melo, J., & Robinson, S. (1982). "General Equilibrium
      Models for Development Policy." Cambridge University Press.
    - Miller, R. & Blair, P. (2009). "Input-Output Analysis: Foundations and
      Extensions." Cambridge University Press.

Tier: TEAM (multi-sector economic modeling for organizations)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Mapping, Optional

import numpy as np
from numpy.typing import NDArray

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
from krl_frameworks.core.tier import Tier
from krl_frameworks.simulation.cbss import TransitionFunction

if TYPE_CHECKING:
    from krl_frameworks.core.config import FrameworkConfig

__all__ = ["SAMCGEFramework", "SAMCGEConfig", "SAMCGEMetrics"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# SAM-CGE Configuration
# ════════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class SAMCGEConfig:
    """
    Configuration for SAM-CGE model.

    Attributes:
        n_sectors: Number of production sectors (default 10).
        elasticity_substitution: CES elasticity of substitution in production.
        elasticity_transformation: CET elasticity of transformation (exports).
        convergence_tolerance: Equilibrium convergence threshold.
        max_iterations: Maximum solver iterations.
        numeraire_factor: Which factor price to fix (0=labor, 1=capital).
        closure_rule: Macroeconomic closure ("savings_driven" or "investment_driven").
    """

    n_sectors: int = 10
    elasticity_substitution: float = 0.8  # CES production
    elasticity_transformation: float = 2.0  # CET trade
    convergence_tolerance: float = 1e-4
    max_iterations: int = 100
    numeraire_factor: int = 0  # Fix labor price
    closure_rule: str = "savings_driven"  # or "investment_driven"


@dataclass(frozen=True)
class SAMCGEMetrics:
    """
    Computed metrics from SAM-CGE model.

    Attributes:
        gdp: Gross Domestic Product (expenditure approach).
        sector_outputs: Output by sector (n_sectors,).
        sector_employment: Employment by sector (n_sectors,).
        wage_rate: Average wage rate.
        capital_return: Return on capital.
        household_income: Total household income.
        government_revenue: Government tax revenue.
        trade_balance: Exports - Imports.
        welfare_index: Equivalent variation or compensating variation.
        price_index: Consumer price index.
    """

    gdp: float
    sector_outputs: NDArray[np.float64]
    sector_employment: NDArray[np.float64]
    wage_rate: float
    capital_return: float
    household_income: float
    government_revenue: float
    trade_balance: float
    welfare_index: float
    price_index: float


# ════════════════════════════════════════════════════════════════════════════════
# SAM-CGE Framework
# ════════════════════════════════════════════════════════════════════════════════


class SAMCGEFramework(BaseMetaFramework):
    """
    Social Accounting Matrix - Computable General Equilibrium Framework.

    This framework implements a multi-sector CGE model based on a Social
    Accounting Matrix (SAM) to analyze economy-wide impacts of policies,
    shocks, or structural changes.

    The model includes:
        - Production sectors with CES technology
        - Factor markets (labor, capital)
        - Household consumption (LES demand system)
        - Government fiscal operations
        - International trade (Armington imports, CET exports)
        - Market clearing conditions

    Example:
        >>> from krl_frameworks.layers.socioeconomic.sam_cge import SAMCGEFramework
        >>> from krl_frameworks.core.data_bundle import DataBundle
        >>> from krl_frameworks.core.config import FrameworkConfig
        >>>
        >>> # Prepare SAM data bundle
        >>> bundle = DataBundle.from_dataframes({
        ...     "sam": sam_table_df,
        ...     "economic": macro_indicators_df,
        ...     "sectors": sector_detail_df,
        ... }, sources={"sam": "BEA I-O Tables"})
        >>>
        >>> # Run SAM-CGE simulation
        >>> framework = SAMCGEFramework(config=SAMCGEConfig(n_sectors=10))
        >>> result = framework.fit(bundle).simulate(steps=20)
        >>> print(f"Final GDP: {result.metrics['gdp']:.2f}")
    """

    METADATA = FrameworkMetadata(
        slug="sam_cge",
        name="SAM-CGE Framework",
        version="1.0.0",
        description=(
            "Social Accounting Matrix - Computable General Equilibrium model "
            "for economy-wide policy analysis with multi-sector production, "
            "factor markets, and international trade."
        ),
        tier=Tier.TEAM,
        layer=VerticalLayer.SOCIOECONOMIC_ACADEMIC,
        required_domains=[
            DataDomain.SAM.value,
            DataDomain.ECONOMIC.value,
            DataDomain.SECTORS.value,
        ],
        tags=[
            "cge",
            "sam",
            "general-equilibrium",
            "multi-sector",
            "economic-modeling",
            "policy-analysis",
        ],
    )

    def __init__(self, config: Optional[SAMCGEConfig] = None):
        """
        Initialize SAM-CGE Framework.

        Args:
            config: SAM-CGE configuration. If None, uses default configuration.
        """
        super().__init__()
        self.config = config or SAMCGEConfig()
        self._sam_matrix: Optional[NDArray[np.float64]] = None
        self._base_prices: Optional[NDArray[np.float64]] = None
        self._base_quantities: Optional[NDArray[np.float64]] = None

    def _compute_initial_state(
        self, bundle: DataBundle, config: FrameworkConfig
    ) -> CohortStateVector:
        """
        Compute initial CGE state from SAM data.

        Extracts base year SAM, calibrates model parameters, and computes
        initial equilibrium.

        Args:
            bundle: DataBundle with SAM, economic, and sector data.
            config: Framework configuration.

        Returns:
            CohortStateVector with initial sector outputs, prices, incomes.

        Raises:
            DataBundleValidationError: If required SAM data is missing.
        """
        # Validate required domains
        if not bundle.has_domain(DataDomain.SAM.value):
            raise DataBundleValidationError(
                "SAM domain is required for SAM-CGE framework"
            )

        # Extract SAM data
        sam_data = bundle.get(DataDomain.SAM.value)
        economic_data = bundle.get(DataDomain.ECONOMIC.value)

        # Infer number of sectors from SAM or use config default
        if hasattr(sam_data.data, "shape"):
            # SAM is typically a square matrix
            n_sectors = min(sam_data.data.shape[0], self.config.n_sectors)
        else:
            # Fallback to config or data length
            n_sectors = self.config.n_sectors

        # Build SAM matrix (simplified for CBSS)
        # In production, this would parse Make/Use tables from BEA
        self._sam_matrix = self._build_sam_matrix(sam_data, n_sectors)

        # Calibrate base prices and quantities from SAM
        self._base_prices = np.ones(n_sectors)  # Numeraire normalization
        self._base_quantities = self._extract_base_quantities(
            self._sam_matrix, n_sectors
        )

        # Initialize state vector
        # Mapping CGE variables to CohortStateVector fields:
        # - sector_output: Sector outputs (n_sectors) - PRIMARY CGE OUTPUT
        # - health_burden_score: Unemployment rate by sector (n_sectors) - always 0.05 in equilibrium
        # - opportunity_score: Relative prices (n_sectors)
        # - credit_access_prob: Capital stock by sector (n_sectors)
        # - employment_prob: Labor share by sector (n_sectors) - sums to 1.0
        # - housing_cost_ratio: Government revenue share (1,)
        # - deprivation_vector: [household_income, trade_balance] (2,)

        # Initial labor distribution (equal shares across sectors)
        initial_labor_shares = np.ones(n_sectors) / n_sectors

        state = CohortStateVector(
            sector_output=self._base_quantities.copy(),  # Sector outputs (n_sectors)
            health_burden_score=np.ones(n_sectors) * 0.05,  # 5% unemployment (fixed in equilibrium)
            opportunity_score=self._base_prices.copy(),  # Initial prices
            credit_access_prob=self._base_quantities * 0.3,  # 30% capital share
            employment_prob=initial_labor_shares,  # Labor shares (sum to 1.0)
            housing_cost_ratio=np.ones(n_sectors) * 0.20,  # Gov revenue 20% of GDP per sector
            deprivation_vector=np.array([
                self._base_quantities.sum() * 0.6,  # Household income
                0.0,  # Balanced trade initially
            ]),
        )

        logger.info(
            f"SAM-CGE initial state computed: {n_sectors} sectors, "
            f"GDP={self._base_quantities.sum():.2f}"
        )

        return state

    def _transition(
        self, state: CohortStateVector, step: int, config: FrameworkConfig
    ) -> CohortStateVector:
        """
        Compute CGE equilibrium transition.

        Solves for new equilibrium given current state and exogenous shocks.
        Uses iterative Gauss-Seidel method to find market-clearing prices.

        Args:
            state: Current CGE state.
            step: Simulation step (used for time-varying shocks).
            config: Framework configuration.

        Returns:
            New equilibrium state.
        """
        n_sectors = len(state.sector_output)

        # Current values
        sector_outputs = state.sector_output.copy()
        prices = state.opportunity_score.copy()
        employment = state.employment_prob.copy()
        capital_stock = state.credit_access_prob.copy()
        household_income = state.deprivation_vector[0]
        trade_balance = state.deprivation_vector[1]

        # Exogenous shocks (example: productivity growth)
        productivity_growth = 1.01 ** step  # 1% annual productivity growth

        # Calibrate TFP to match base outputs
        # Note: employment is in shares (summing to 1.0), capital_stock is in absolute units
        labor_share = 0.7
        capital_share = 0.3

        # Initial total labor (normalized to 1.0)
        total_labor_supply = 1.0

        # Calibrate TFP such that Q_i = A_i * L_i^α * K_i^(1-α)
        tfp = sector_outputs / (
            ((employment * total_labor_supply)**labor_share) *
            (capital_stock**capital_share) + 1e-8
        )

        # Iterative equilibrium solver (simplified Gauss-Seidel with damping)
        damping_factor = 0.3  # Damping to improve stability

        for iteration in range(self.config.max_iterations):
            # Production: Calibrated Cobb-Douglas
            # Q_i = A_i * (L_i_share * L_total)^α * K_i^(1-α)
            labor_input = employment * total_labor_supply
            new_outputs = (
                tfp
                * productivity_growth
                * (labor_input**labor_share)
                * (capital_stock**capital_share)
            )

            # Demand: Linear Expenditure System (LES)
            # Household consumption proportional to income and prices
            consumption = (
                household_income * 0.8 / n_sectors
            ) / prices  # Equal budget shares

            # Government demand (fixed share of GDP)
            gov_demand = sector_outputs * 0.15

            # Investment demand (savings-driven closure)
            investment_rate = 0.20
            investment = sector_outputs * investment_rate

            # Exports (CET transformation)
            export_share = 0.10
            exports = sector_outputs * export_share

            # Imports (Armington aggregation)
            import_share = 0.12
            imports = sector_outputs * import_share

            # Market clearing: Q_i = C_i + G_i + I_i + X_i - M_i
            total_demand = consumption + gov_demand + investment + exports - imports

            # Update prices based on excess demand (with damping)
            excess_demand = total_demand - new_outputs
            price_adjustment = 1.0 + damping_factor * excess_demand / (new_outputs + 1e-8)
            new_prices = prices * price_adjustment

            # Normalize prices (numeraire: fix first sector price)
            new_prices = new_prices / (new_prices[self.config.numeraire_factor] + 1e-8)

            # Factor market clearing
            # Labor: Derive labor demand shares from marginal product = wage
            # From Cobb-Douglas FOC: w_i * L_i = α * P_i * Q_i
            # With common wage: w * L_i = α * P_i * Q_i → L_i = α * (P_i * Q_i) / w

            # Wage rate (numeraire-normalized)
            wage_rate = new_prices.mean()  # Average price proxy for wage

            # Labor demand by sector (in absolute units)
            labor_value = new_prices * new_outputs  # Value of output
            labor_demand_absolute = labor_share * labor_value / (wage_rate + 1e-8)

            # Convert to shares (employment is a fraction of total labor)
            total_labor_demand = labor_demand_absolute.sum()
            if total_labor_demand > 1e-8:
                labor_demand_shares = labor_demand_absolute / total_labor_demand
            else:
                labor_demand_shares = employment.copy()  # Fallback to current

            # Update employment with damping for stability
            new_employment = (
                (1 - damping_factor) * employment +
                damping_factor * labor_demand_shares
            )
            # Ensure shares sum to ~1.0 and are positive
            new_employment = np.clip(new_employment, 0.001, 0.99)
            new_employment = new_employment / (new_employment.sum() + 1e-8)

            # Capital: Accumulation from investment (gradual adjustment)
            depreciation_rate = 0.05
            new_capital = capital_stock * (1 - depreciation_rate) + investment * 0.1

            # Check convergence
            output_change = np.abs(new_outputs - sector_outputs).max()
            price_change = np.abs(new_prices - prices).max()

            if (
                output_change < self.config.convergence_tolerance
                and price_change < self.config.convergence_tolerance
            ):
                logger.debug(
                    f"CGE converged at iteration {iteration+1}: "
                    f"output_change={output_change:.6f}, price_change={price_change:.6f}"
                )
                break

            # Update for next iteration (with damping for stability)
            sector_outputs = (1 - damping_factor) * sector_outputs + damping_factor * new_outputs
            prices = new_prices.copy()
            employment = new_employment.copy()
            capital_stock = new_capital.copy()

        # Update household income (factor incomes)
        # Labor income: wage * total labor supply (employment shares sum to 1.0)
        wage_rate = prices.mean()  # Average price as wage proxy
        labor_income = wage_rate * total_labor_supply  # Total labor supply = 1.0

        # Capital income: return to capital (capital share of output)
        capital_return = (sector_outputs * capital_share).sum()

        household_income = labor_income + capital_return

        # Update government revenue (taxes)
        tax_rate = 0.20
        government_revenue = sector_outputs.sum() * tax_rate

        # Update trade balance
        trade_balance = exports.sum() - imports.sum()

        # Construct new state
        # Note: health_burden_score represents unemployment rate (fixed at 5% in full employment equilibrium)
        # employment_prob represents labor shares across sectors (sum to 1.0)
        unemployment_rate = 0.05  # Assume full employment equilibrium (5% frictional unemployment)

        new_state = CohortStateVector(
            sector_output=sector_outputs,
            health_burden_score=np.ones(n_sectors) * unemployment_rate,  # Fixed unemployment rate
            opportunity_score=prices,
            credit_access_prob=capital_stock,
            employment_prob=employment,  # Labor shares (sum to 1.0)
            housing_cost_ratio=np.ones(n_sectors) * (government_revenue / sector_outputs.sum()),
            deprivation_vector=np.array([household_income, trade_balance]),
        )

        return new_state

    def _compute_metrics(self, state: CohortStateVector) -> dict[str, Any]:
        """
        Compute SAM-CGE metrics from state.

        Args:
            state: Current CGE state.

        Returns:
            Dictionary of metrics (GDP, sector outputs, employment, etc.).
        """
        sector_outputs = state.sector_output
        prices = state.opportunity_score
        employment_shares = state.employment_prob  # Labor shares (sum to 1.0)
        unemployment_rate = state.health_burden_score.mean()  # Fixed at ~0.05
        capital_stock = state.credit_access_prob
        household_income = state.deprivation_vector[0]
        gov_revenue_share = state.housing_cost_ratio.mean()
        trade_balance = state.deprivation_vector[1]

        # GDP (expenditure approach)
        gdp = sector_outputs.sum()

        # Sector employment (employment shares * total labor supply = 1.0)
        # Convert to absolute numbers for display (normalized by average output)
        total_labor_supply = 1.0
        sector_employment = employment_shares * total_labor_supply

        # Wage rate (average price)
        wage_rate = prices.mean()

        # Capital return (residual)
        capital_return = (sector_outputs * 0.3).mean()

        # Government revenue
        government_revenue = gdp * gov_revenue_share

        # Welfare index (real household income)
        price_index = prices.mean()
        welfare_index = household_income / price_index

        metrics = {
            "gdp": float(gdp),
            "sector_outputs": sector_outputs.tolist(),
            "sector_employment": sector_employment.tolist(),  # Labor shares (sum to 1.0)
            "unemployment_rate": float(unemployment_rate),  # Fixed at ~0.05 (5%)
            "wage_rate": float(wage_rate),
            "capital_return": float(capital_return),
            "household_income": float(household_income),
            "government_revenue": float(government_revenue),
            "trade_balance": float(trade_balance),
            "welfare_index": float(welfare_index),
            "price_index": float(price_index),
            "prices": prices.tolist(),
            "capital_stock": capital_stock.tolist(),
        }

        return metrics

    def _build_sam_matrix(
        self, sam_data: Any, n_sectors: int
    ) -> NDArray[np.float64]:
        """
        Build SAM matrix from data.

        In production, this would parse BEA Make/Use tables.
        For now, creates a balanced SAM with realistic structure.

        Args:
            sam_data: SAM data from DataBundle.
            n_sectors: Number of sectors.

        Returns:
            SAM matrix (n_accounts, n_accounts).
        """
        # SAM structure:
        # Rows: Receipts (who receives)
        # Columns: Expenditures (who pays)
        # Accounts: Activities, Commodities, Factors, Households, Government, ROW

        # Simplified: Just use sector dimension
        sam = np.zeros((n_sectors, n_sectors))

        # Inter-industry flows (input-output structure)
        # Simplified Leontief inverse with some structure
        for i in range(n_sectors):
            for j in range(n_sectors):
                if i == j:
                    sam[i, j] = 0.3  # Diagonal: own-sector use
                elif abs(i - j) == 1:
                    sam[i, j] = 0.1  # Adjacent sectors: supply chain
                else:
                    sam[i, j] = 0.02  # Sparse cross-sector flows

        return sam

    def _extract_base_quantities(
        self, sam_matrix: NDArray[np.float64], n_sectors: int
    ) -> NDArray[np.float64]:
        """
        Extract base year quantities from SAM.

        Args:
            sam_matrix: SAM matrix.
            n_sectors: Number of sectors.

        Returns:
            Base year sector outputs.
        """
        # Row sums = total receipts = sector output
        base_quantities = sam_matrix.sum(axis=1)

        # Normalize to realistic scale (GDP ~ 100)
        total_output = base_quantities.sum()
        if total_output > 0:
            base_quantities = base_quantities * (100.0 / total_output)
        else:
            # Fallback: equal initial outputs
            base_quantities = np.ones(n_sectors) * (100.0 / n_sectors)

        return base_quantities

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Get SAM-CGE dashboard specification.

        Returns:
            Dashboard specification with parameter schema and output views.
        """
        return FrameworkDashboardSpec(
            slug="sam_cge",
            name="SAM-CGE Framework",
            description="Social Accounting Matrix - Computable General Equilibrium model for policy analysis",
            layer="socioeconomic",
            parameters_schema={
                "type": "object",
                "properties": {
                    "n_sectors": {
                        "type": "integer",
                        "minimum": 3,
                        "maximum": 50,
                        "default": 10,
                        "title": "Number of Sectors",
                        "description": "Number of production sectors in CGE model",
                    },
                    "simulation_steps": {
                        "type": "integer",
                        "minimum": 5,
                        "maximum": 100,
                        "default": 20,
                        "title": "Simulation Steps",
                        "description": "Number of time periods to simulate",
                    },
                    "elasticity_substitution": {
                        "type": "number",
                        "minimum": 0.1,
                        "maximum": 5.0,
                        "default": 0.8,
                        "title": "Elasticity of Substitution",
                        "description": "CES production function elasticity",
                    },
                    "policy_shock": {
                        "type": "string",
                        "enum": ["none", "tax_increase", "tariff", "subsidy"],
                        "default": "none",
                        "title": "Policy Shock",
                        "description": "Type of policy shock to simulate",
                    },
                },
                "required": ["simulation_steps"],
            },
            default_parameters={
                "n_sectors": 10,
                "simulation_steps": 20,
                "elasticity_substitution": 0.8,
                "policy_shock": "none",
            },
            parameter_groups=[
                ParameterGroupSpec(
                    key="model_structure",
                    title="Model Structure",
                    description="Configure CGE model dimensions",
                    parameters=["n_sectors", "elasticity_substitution"],
                ),
                ParameterGroupSpec(
                    key="simulation_settings",
                    title="Simulation Settings",
                    description="Configure simulation parameters",
                    parameters=["simulation_steps", "policy_shock"],
                ),
            ],
            output_views=[
                OutputViewSpec(
                    key="gdp",
                    title="GDP",
                    view_type=ViewType.GAUGE,
                    description="Gross Domestic Product",
                    config={"min": 0, "max": 200, "unit": "billion USD"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="gdp_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="sector_outputs",
                    title="Sector Outputs",
                    view_type=ViewType.BAR_CHART,
                    description="Output by economic sector",
                    config={"x_label": "Sector", "y_label": "Output"},
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="sector_outputs_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="gdp_trajectory",
                    title="GDP Trajectory",
                    view_type=ViewType.LINE_CHART,
                    description="GDP over simulation period",
                    config={"x_label": "Period", "y_label": "GDP"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="gdp_trajectory_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="economic_indicators",
                    title="Economic Indicators",
                    view_type=ViewType.TABLE,
                    description="Summary of key economic indicators",
                    config={
                        "columns": [
                            "gdp",
                            "unemployment_rate",
                            "wage_rate",
                            "welfare_index",
                        ]
                    },
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="economic_indicators_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="sector_employment",
                    title="Sector Employment",
                    view_type=ViewType.HEATMAP,
                    description="Employment distribution across sectors",
                    config={"color_scale": "blues"},
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="sector_employment_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )


# ════════════════════════════════════════════════════════════════════════════════
# Helper Functions
# ════════════════════════════════════════════════════════════════════════════════


def compute_sam_cge_metrics(state: CohortStateVector) -> SAMCGEMetrics:
    """
    Compute typed SAM-CGE metrics from state.

    Args:
        state: CGE state vector.

    Returns:
        SAMCGEMetrics dataclass.
    """
    return SAMCGEMetrics(
        gdp=float(state.sector_output.sum()),
        sector_outputs=state.sector_output.copy(),
        sector_employment=state.employment_prob
        * (state.sector_output.sum() / len(state.sector_output)),
        wage_rate=float(state.opportunity_score.mean()),
        capital_return=float((state.sector_output * 0.3).mean()),
        household_income=float(state.deprivation_vector[0]),
        government_revenue=float(
            state.sector_output.sum() * state.housing_cost_ratio.mean()
        ),
        trade_balance=float(state.deprivation_vector[1]),
        welfare_index=float(
            state.deprivation_vector[0] / state.opportunity_score.mean()
        ),
        price_index=float(state.opportunity_score.mean()),
    )
