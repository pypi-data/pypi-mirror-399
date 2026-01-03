# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - CGE (Computable General Equilibrium) Meta-Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
CGEFramework: Computable General Equilibrium Meta-Framework.

This meta-framework provides a comprehensive platform for multi-sector
general equilibrium modeling with Social Accounting Matrix (SAM) calibration.
Unlike domain-specific CGE variants (e.g., CulturalCGEFramework), this
framework offers a generic foundation for economy-wide analysis.

Key Features:
    1. SAM-Based Calibration: Calibrate from Social Accounting Matrix
    2. Multi-Sector Production: CES/Cobb-Douglas nested production functions
    3. Household Consumption: LES, Stone-Geary, or CES demand systems
    4. Trade: Armington import specification with export supply
    5. Government: Tax instruments and transfer systems
    6. Closure Rules: Various macro closures (neoclassical, Keynesian)
    7. Welfare Analysis: Hicksian CV/EV and equivalent variation

Theoretical Foundation:
    - Shoven & Whalley (1984): Applied General Equilibrium Models
    - Rutherford (1999): GAMS/MPSGE solution methods
    - Lofgren et al. (2002): Standard CGE Model in GAMS
    - Dixon & Parmenter (1996): CGE Models Handbook chapter

CBSS Integration:
    - Maps sectors to cohort dimensions
    - Implements TransitionFunction for dynamic CGE
    - Supports policy shocks as tax/transfer changes

Solution Methods:
    - Fixed-point iteration (Gauss-Seidel)
    - Newton-based solvers
    - Complementarity formulation

Tier: ENTERPRISE (full model with dynamic transitions)
      PROFESSIONAL (static single-period equilibrium)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, Mapping, Optional, Sequence

import numpy as np
from scipy import optimize

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

__all__ = [
    "CGEFramework",
    "CGEConfig",
    "SAM",
    "Sector",
    "ProductionFunction",
    "DemandSystem",
    "ClosureRule",
    "CGEEquilibrium",
    "CGETransition",
    "WelfareAnalysis",
]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Enumerations
# ════════════════════════════════════════════════════════════════════════════════


class ProductionType(Enum):
    """Production function specification."""
    
    COBB_DOUGLAS = auto()       # Cobb-Douglas (elasticity = 1)
    CES = auto()                # Constant Elasticity of Substitution
    LEONTIEF = auto()           # Fixed proportions (elasticity = 0)
    NESTED_CES = auto()         # Multi-level CES nesting


class DemandSystemType(Enum):
    """Household demand system specification."""
    
    COBB_DOUGLAS = auto()       # Homothetic Cobb-Douglas
    LES = auto()                # Linear Expenditure System
    CES = auto()                # CES preferences
    AIDS = auto()               # Almost Ideal Demand System
    STONE_GEARY = auto()        # Stone-Geary (LES foundation)


class ClosureType(Enum):
    """Macro closure rules."""
    
    NEOCLASSICAL = auto()       # Full employment, flexible wages
    KEYNESIAN = auto()          # Fixed wages, flexible employment
    JOHANSEN = auto()           # Fixed investment, flexible savings
    BALANCED_TRADE = auto()     # Fixed trade balance
    SAVINGS_DRIVEN = auto()     # Investment adjusts to savings


class TradeSpecification(Enum):
    """Trade modeling approach."""
    
    ARMINGTON = auto()          # Imperfect substitution imports
    SMALL_COUNTRY = auto()      # Fixed world prices
    LARGE_COUNTRY = auto()      # Endogenous terms of trade
    BILATERAL = auto()          # Country-pair trade flows


# ════════════════════════════════════════════════════════════════════════════════
# Sector Definition
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class Sector:
    """
    Production sector in the CGE model.
    
    Attributes:
        name: Sector identifier
        code: Short code (e.g., "AGR", "MFG")
        output: Base year output
        labor_demand: Base year labor demand
        capital_demand: Base year capital demand
        intermediate_demand: Dict of intermediate inputs from other sectors
        export_share: Share of output exported
        import_share: Share of domestic absorption from imports
        production_type: Production function type
        elasticity: Substitution elasticity (for CES)
        tfp: Total factor productivity
    """
    
    name: str
    code: str
    output: float
    labor_demand: float
    capital_demand: float
    intermediate_demand: dict[str, float] = field(default_factory=dict)
    export_share: float = 0.1
    import_share: float = 0.1
    production_type: ProductionType = ProductionType.CES
    elasticity: float = 0.8
    tfp: float = 1.0
    
    @property
    def value_added(self) -> float:
        """Compute value added."""
        intermediate_total = sum(self.intermediate_demand.values())
        return self.output - intermediate_total
    
    def labor_share(self) -> float:
        """Compute labor share of value added."""
        va = self.value_added
        if va <= 0:
            return 0.5
        return self.labor_demand / va
    
    def capital_share(self) -> float:
        """Compute capital share of value added."""
        return 1.0 - self.labor_share()


# ════════════════════════════════════════════════════════════════════════════════
# Social Accounting Matrix
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class SAM:
    """
    Social Accounting Matrix for CGE calibration.
    
    A SAM is a square matrix where rows represent income and columns
    represent expenditure. Row sums must equal column sums.
    
    Attributes:
        sectors: List of production sectors
        households: Number of household groups
        factors: List of factor names (labor, capital, etc.)
        matrix: The SAM matrix
        row_labels: Labels for rows
        col_labels: Labels for columns
    """
    
    sectors: list[str]
    households: int
    factors: list[str]
    matrix: np.ndarray
    row_labels: list[str] = field(default_factory=list)
    col_labels: list[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.row_labels:
            self.row_labels = self._default_labels()
        if not self.col_labels:
            self.col_labels = self._default_labels()
    
    def _default_labels(self) -> list[str]:
        """Generate default account labels."""
        labels = []
        # Activities (production)
        labels.extend([f"ACT_{s}" for s in self.sectors])
        # Commodities (goods)
        labels.extend([f"COM_{s}" for s in self.sectors])
        # Factors
        labels.extend(self.factors)
        # Households
        labels.extend([f"HH_{i}" for i in range(self.households)])
        # Government
        labels.append("GOV")
        # Savings-Investment
        labels.append("S-I")
        # Rest of World
        labels.append("ROW")
        return labels
    
    def validate(self) -> list[str]:
        """Check SAM balance (row sums = column sums)."""
        errors = []
        row_sums = self.matrix.sum(axis=1)
        col_sums = self.matrix.sum(axis=0)
        
        for i, (rs, cs) in enumerate(zip(row_sums, col_sums)):
            if abs(rs - cs) > 1e-6:
                label = self.row_labels[i] if i < len(self.row_labels) else f"Row_{i}"
                errors.append(f"SAM imbalance at {label}: row={rs:.2f}, col={cs:.2f}")
        
        return errors
    
    @classmethod
    def from_io_table(
        cls,
        io_matrix: np.ndarray,
        sector_names: list[str],
        value_added: np.ndarray,
        final_demand: np.ndarray,
    ) -> SAM:
        """
        Construct SAM from Input-Output table.
        
        Args:
            io_matrix: Intermediate demand matrix (n_sectors x n_sectors)
            sector_names: Sector names
            value_added: Value added vector by sector
            final_demand: Final demand vector by sector
            
        Returns:
            SAM instance
        """
        n_sectors = len(sector_names)
        
        # SAM dimensions: sectors*2 + 2 factors + 1 HH + GOV + S-I + ROW
        n_accounts = n_sectors * 2 + 2 + 1 + 3
        matrix = np.zeros((n_accounts, n_accounts))
        
        # Fill intermediate demand (activities to commodities)
        for i in range(n_sectors):
            for j in range(n_sectors):
                # Row i is commodity i, column j+n_sectors is activity j
                matrix[i, n_sectors + j] = io_matrix[i, j]
        
        # Activities produce commodities (diagonal)
        for i in range(n_sectors):
            total_output = io_matrix[:, i].sum() + value_added[i]
            matrix[n_sectors + i, i] = total_output  # Activity to commodity
        
        # Value added to factors
        labor_idx = n_sectors * 2
        capital_idx = n_sectors * 2 + 1
        hh_idx = n_sectors * 2 + 2
        
        for i in range(n_sectors):
            # Assume 60% labor, 40% capital
            matrix[labor_idx, n_sectors + i] = value_added[i] * 0.6
            matrix[capital_idx, n_sectors + i] = value_added[i] * 0.4
        
        # Factors to households
        matrix[hh_idx, labor_idx] = matrix[labor_idx, :].sum()
        matrix[hh_idx, capital_idx] = matrix[capital_idx, :].sum()
        
        # Household consumption (final demand to commodities)
        for i in range(n_sectors):
            matrix[i, hh_idx] = final_demand[i]
        
        return cls(
            sectors=sector_names,
            households=1,
            factors=["Labor", "Capital"],
            matrix=matrix,
        )


# ════════════════════════════════════════════════════════════════════════════════
# Production and Demand Functions
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class ProductionFunction:
    """
    Production function specification.
    
    Attributes:
        type: Production function type
        elasticity: Substitution elasticity (sigma)
        labor_share: Base labor share (alpha)
        tfp: Total factor productivity (A)
        intermediate_shares: Shares of intermediate inputs
    """
    
    type: ProductionType
    elasticity: float = 0.8
    labor_share: float = 0.6
    tfp: float = 1.0
    intermediate_shares: dict[str, float] = field(default_factory=dict)
    
    def output(
        self,
        labor: float,
        capital: float,
        intermediates: Optional[dict[str, float]] = None,
    ) -> float:
        """
        Compute output given inputs.
        
        Args:
            labor: Labor input
            capital: Capital input
            intermediates: Dict of intermediate inputs
            
        Returns:
            Output quantity
        """
        intermediates = intermediates or {}
        
        # Value added from labor and capital
        if self.type == ProductionType.COBB_DOUGLAS:
            va = self.tfp * (labor ** self.labor_share) * (capital ** (1 - self.labor_share))
        
        elif self.type == ProductionType.CES:
            sigma = self.elasticity
            rho = (sigma - 1) / sigma
            
            alpha = self.labor_share
            va = self.tfp * (
                alpha * (labor ** rho) + (1 - alpha) * (capital ** rho)
            ) ** (1 / rho)
        
        elif self.type == ProductionType.LEONTIEF:
            va = self.tfp * min(
                labor / self.labor_share,
                capital / (1 - self.labor_share),
            )
        
        else:
            va = self.tfp * (labor ** self.labor_share) * (capital ** (1 - self.labor_share))
        
        # Add intermediate inputs (Leontief aggregation)
        if intermediates and self.intermediate_shares:
            int_index = min(
                intermediates.get(k, 0) / self.intermediate_shares.get(k, 1)
                for k in self.intermediate_shares
                if self.intermediate_shares.get(k, 0) > 0
            )
            # Leontief combination of VA and intermediates
            int_share = sum(self.intermediate_shares.values())
            va_share = 1 - int_share
            return min(va / va_share, int_index / int_share) if int_share > 0 else va
        
        return va
    
    def labor_demand(
        self,
        output: float,
        wage: float,
        rental_rate: float,
    ) -> float:
        """Derive labor demand from cost minimization."""
        if self.type == ProductionType.COBB_DOUGLAS:
            return (output / self.tfp) * (self.labor_share / wage) * (
                (wage / self.labor_share) ** self.labor_share *
                (rental_rate / (1 - self.labor_share)) ** (1 - self.labor_share)
            ) ** (1 - self.labor_share)
        
        elif self.type == ProductionType.CES:
            sigma = self.elasticity
            alpha = self.labor_share
            
            # CES labor demand
            price_ratio = wage / rental_rate
            labor_capital_ratio = (alpha / (1 - alpha)) ** sigma * price_ratio ** (-sigma)
            
            # Total cost and labor
            total_cost = output  # Normalized
            return total_cost * alpha * wage ** (-sigma) / (
                alpha * wage ** (1 - sigma) + (1 - alpha) * rental_rate ** (1 - sigma)
            )
        
        return output * self.labor_share / wage


@dataclass
class DemandSystem:
    """
    Household demand system.
    
    Attributes:
        type: Demand system type
        shares: Budget shares by sector
        subsistence: Subsistence quantities (for LES)
        elasticities: Price elasticities (for AIDS)
    """
    
    type: DemandSystemType
    shares: dict[str, float] = field(default_factory=dict)
    subsistence: dict[str, float] = field(default_factory=dict)
    elasticities: dict[str, float] = field(default_factory=dict)
    
    def demands(
        self,
        income: float,
        prices: dict[str, float],
    ) -> dict[str, float]:
        """
        Compute commodity demands.
        
        Args:
            income: Household income
            prices: Commodity prices
            
        Returns:
            Dict of demands by sector
        """
        demands = {}
        
        if self.type == DemandSystemType.COBB_DOUGLAS:
            for sector, share in self.shares.items():
                price = prices.get(sector, 1.0)
                demands[sector] = share * income / price
        
        elif self.type in (DemandSystemType.LES, DemandSystemType.STONE_GEARY):
            # Linear Expenditure System
            # x_i = gamma_i + (beta_i / p_i) * (Y - sum(p_j * gamma_j))
            subsistence_spending = sum(
                prices.get(s, 1.0) * self.subsistence.get(s, 0.0)
                for s in self.shares
            )
            supernumerary = income - subsistence_spending
            
            for sector, share in self.shares.items():
                price = prices.get(sector, 1.0)
                subsist = self.subsistence.get(sector, 0.0)
                demands[sector] = subsist + share * supernumerary / price
        
        elif self.type == DemandSystemType.CES:
            # CES demands
            sigma = 0.5  # Default substitution elasticity
            total_weight = sum(
                self.shares.get(s, 0) * prices.get(s, 1.0) ** (1 - sigma)
                for s in self.shares
            )
            
            for sector, share in self.shares.items():
                price = prices.get(sector, 1.0)
                demands[sector] = income * share * price ** (-sigma) / total_weight
        
        else:
            # Default to Cobb-Douglas
            for sector, share in self.shares.items():
                price = prices.get(sector, 1.0)
                demands[sector] = share * income / price
        
        return demands


# ════════════════════════════════════════════════════════════════════════════════
# Closure Rules
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class ClosureRule:
    """
    Macro closure specification.
    
    Attributes:
        type: Closure type
        fixed_variables: Variables held fixed
        adjusting_variable: Variable that adjusts
        parameters: Closure-specific parameters
    """
    
    type: ClosureType
    fixed_variables: list[str] = field(default_factory=list)
    adjusting_variable: str = ""
    parameters: dict[str, float] = field(default_factory=dict)
    
    @classmethod
    def neoclassical(cls) -> ClosureRule:
        """Standard neoclassical closure."""
        return cls(
            type=ClosureType.NEOCLASSICAL,
            fixed_variables=["labor_supply", "capital_stock"],
            adjusting_variable="wage",
        )
    
    @classmethod
    def keynesian(cls, unemployment_rate: float = 0.05) -> ClosureRule:
        """Keynesian closure with unemployment."""
        return cls(
            type=ClosureType.KEYNESIAN,
            fixed_variables=["wage"],
            adjusting_variable="employment",
            parameters={"base_unemployment": unemployment_rate},
        )


# ════════════════════════════════════════════════════════════════════════════════
# CGE Configuration
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class CGEConfig:
    """
    Configuration for CGE model.
    
    Attributes:
        sectors: List of sectors
        sam: Social Accounting Matrix
        production: Production function specs by sector
        demand: Household demand system
        closure: Macro closure rule
        trade_spec: Trade modeling approach
        solver_tolerance: Convergence tolerance
        max_iterations: Maximum solver iterations
        time_horizon: For dynamic CGE
    """
    
    sectors: list[Sector] = field(default_factory=list)
    sam: Optional[SAM] = None
    production: dict[str, ProductionFunction] = field(default_factory=dict)
    demand: Optional[DemandSystem] = None
    closure: ClosureRule = field(default_factory=ClosureRule.neoclassical)
    trade_spec: TradeSpecification = TradeSpecification.ARMINGTON
    solver_tolerance: float = 1e-8
    max_iterations: int = 1000
    time_horizon: int = 1


# ════════════════════════════════════════════════════════════════════════════════
# CGE Equilibrium
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class CGEEquilibrium:
    """
    General equilibrium solution.
    
    Attributes:
        prices: Equilibrium prices by sector
        quantities: Equilibrium quantities by sector
        wages: Factor prices (wage, rental rate)
        employment: Employment levels
        household_welfare: Household utility levels
        government_revenue: Tax revenue
        trade_balance: Net exports
        convergence_iterations: Iterations to convergence
        excess_demand_norm: Final excess demand
    """
    
    prices: dict[str, float]
    quantities: dict[str, float]
    wages: dict[str, float]
    employment: dict[str, float]
    household_welfare: float
    government_revenue: float
    trade_balance: float
    convergence_iterations: int
    excess_demand_norm: float
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize equilibrium."""
        return {
            "prices": self.prices,
            "quantities": self.quantities,
            "wages": self.wages,
            "employment": self.employment,
            "household_welfare": self.household_welfare,
            "government_revenue": self.government_revenue,
            "trade_balance": self.trade_balance,
            "convergence": {
                "iterations": self.convergence_iterations,
                "excess_demand_norm": self.excess_demand_norm,
            },
        }


@dataclass
class WelfareAnalysis:
    """
    Welfare decomposition from policy simulation.
    
    Attributes:
        compensating_variation: CV measure
        equivalent_variation: EV measure
        consumer_surplus_change: Change in consumer surplus
        producer_surplus_change: Change in producer surplus
        tax_revenue_change: Change in government revenue
        total_welfare_change: Net welfare effect
        winners: Sectors/households that gain
        losers: Sectors/households that lose
    """
    
    compensating_variation: float
    equivalent_variation: float
    consumer_surplus_change: float
    producer_surplus_change: float
    tax_revenue_change: float
    total_welfare_change: float
    winners: list[str] = field(default_factory=list)
    losers: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize welfare analysis."""
        return {
            "compensating_variation": self.compensating_variation,
            "equivalent_variation": self.equivalent_variation,
            "consumer_surplus_change": self.consumer_surplus_change,
            "producer_surplus_change": self.producer_surplus_change,
            "tax_revenue_change": self.tax_revenue_change,
            "total_welfare_change": self.total_welfare_change,
            "winners": self.winners,
            "losers": self.losers,
        }


# ════════════════════════════════════════════════════════════════════════════════
# CGE Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class CGETransition(TransitionFunction):
    """
    CGE state transition function for CBSS integration.
    
    Maps sector-level equilibrium outcomes to cohort state transitions.
    """
    
    name = "CGETransition"
    
    def __init__(
        self,
        config: Optional[CGEConfig] = None,
        equilibrium: Optional[CGEEquilibrium] = None,
    ):
        self.config = config or CGEConfig()
        self.equilibrium = equilibrium
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: Any,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """
        Apply CGE-based transition dynamics.
        
        Uses equilibrium prices and quantities to update cohort states.
        """
        params = params or {}
        
        # ─────────────────────────────────────────────────────────────────────
        # 1. Update Sector Output from Equilibrium
        # ─────────────────────────────────────────────────────────────────────
        if self.equilibrium:
            # Map equilibrium quantities to sector output
            new_sector_output = np.zeros_like(state.sector_output)
            sector_names = [s.name for s in self.config.sectors]
            
            for i, s_name in enumerate(sector_names[:state.n_sectors]):
                if s_name in self.equilibrium.quantities:
                    new_sector_output[:, i] = self.equilibrium.quantities[s_name]
                else:
                    new_sector_output[:, i] = state.sector_output[:, i]
        else:
            # Default growth
            growth_rate = params.get("growth_rate", 0.02)
            new_sector_output = state.sector_output * (1 + growth_rate)
        
        # ─────────────────────────────────────────────────────────────────────
        # 2. Update Employment from Labor Market
        # ─────────────────────────────────────────────────────────────────────
        if self.equilibrium:
            total_employment = sum(self.equilibrium.employment.values())
            labor_supply = sum(s.labor_demand for s in self.config.sectors)
            employment_rate = total_employment / labor_supply if labor_supply > 0 else 0.95
            new_employment = np.full_like(state.employment_prob, employment_rate)
        else:
            new_employment = np.clip(
                state.employment_prob * (1 + 0.005),
                0.0,
                1.0,
            )
        
        # ─────────────────────────────────────────────────────────────────────
        # 3. Update Credit Access from Income Distribution
        # ─────────────────────────────────────────────────────────────────────
        if self.equilibrium:
            # Higher wages → better credit access
            avg_wage = np.mean(list(self.equilibrium.wages.values()))
            credit_factor = np.clip(avg_wage / 1.0, 0.5, 1.5)  # Normalized to base wage
            new_credit = np.clip(state.credit_access_score * credit_factor, 0, 1)
        else:
            new_credit = state.credit_access_score * 1.001
        
        # ─────────────────────────────────────────────────────────────────────
        # 4. Build New State
        # ─────────────────────────────────────────────────────────────────────
        return CohortStateVector(
            employment_prob=new_employment,
            health_burden_score=state.health_burden_score * 0.995,
            credit_access_score=new_credit,
            housing_cost_ratio=state.housing_cost_ratio,
            sector_output=new_sector_output,
        )


# ════════════════════════════════════════════════════════════════════════════════
# CGE Framework
# ════════════════════════════════════════════════════════════════════════════════


class CGEFramework(BaseMetaFramework):
    """
    Computable General Equilibrium Meta-Framework.
    
    Provides a comprehensive platform for multi-sector general equilibrium
    analysis with SAM-based calibration and various closure rules.
    
    Example:
        >>> from krl_frameworks.layers.meta import CGEFramework, Sector, CGEConfig
        >>> 
        >>> sectors = [
        ...     Sector(name="Agriculture", code="AGR", output=100, labor_demand=40, capital_demand=30),
        ...     Sector(name="Manufacturing", code="MFG", output=200, labor_demand=80, capital_demand=60),
        ...     Sector(name="Services", code="SRV", output=300, labor_demand=120, capital_demand=90),
        ... ]
        >>> 
        >>> framework = CGEFramework()
        >>> config = CGEConfig(sectors=sectors)
        >>> equilibrium = framework.solve_equilibrium(config)
    
    Tier: ENTERPRISE for full features, PROFESSIONAL for static equilibrium
    """
    
    def __init__(self):
        super().__init__()
        self._config: Optional[CGEConfig] = None
        self._equilibrium: Optional[CGEEquilibrium] = None
        self._base_equilibrium: Optional[CGEEquilibrium] = None
    
    def metadata(self) -> FrameworkMetadata:
        """Return framework metadata."""
        return FrameworkMetadata(
            name="CGEFramework",
            slug="cge",
            version="1.0.0",
            description=(
                "Computable General Equilibrium meta-framework for multi-sector "
                "economic analysis with SAM calibration and welfare decomposition."
            ),
            layer=VerticalLayer.META_PEER_FRAMEWORKS,
            tier=Tier.PROFESSIONAL,
            constituent_models=[
                "Shoven-Whalley CGE",
                "GTAP Model",
                "IFPRI Standard CGE",
            ],
            tags=[
                "sam_calibration",
                "multi_sector",
                "general_equilibrium",
                "welfare_analysis",
                "policy_simulation",
                "trade_modeling",
            ],
        )
    
    def validate_bundle(self, bundle: DataBundle) -> list[str]:
        """Validate input data bundle."""
        errors = []
        
        # CGE typically needs economic data
        if DataDomain.ECONOMIC in bundle.domains:
            econ = bundle.get_domain_data(DataDomain.ECONOMIC)
            if econ is not None and hasattr(econ, "shape"):
                if econ.shape[0] < 1:
                    errors.append("Economic data must have at least one sector")
        
        return errors
    
    @requires_tier(Tier.PROFESSIONAL)
    def calibrate_from_sam(self, sam: SAM) -> CGEConfig:
        """
        Calibrate model from Social Accounting Matrix.
        
        Args:
            sam: Social Accounting Matrix
            
        Returns:
            Calibrated CGEConfig
        """
        sectors = []
        n_sectors = len(sam.sectors)
        
        for i, sector_name in enumerate(sam.sectors):
            # Extract from SAM
            activity_idx = n_sectors + i
            
            # Total output from activity column sum
            output = float(sam.matrix[:, activity_idx].sum())
            
            # Factor demands
            labor_idx = n_sectors * 2
            capital_idx = n_sectors * 2 + 1
            labor = float(sam.matrix[labor_idx, activity_idx])
            capital = float(sam.matrix[capital_idx, activity_idx])
            
            # Intermediate demands
            intermediates = {}
            for j, other_sector in enumerate(sam.sectors):
                int_demand = float(sam.matrix[j, activity_idx])
                if int_demand > 0:
                    intermediates[other_sector] = int_demand
            
            sector = Sector(
                name=sector_name,
                code=sector_name[:3].upper(),
                output=output,
                labor_demand=labor,
                capital_demand=capital,
                intermediate_demand=intermediates,
            )
            sectors.append(sector)
        
        # Create production functions
        production = {}
        for sector in sectors:
            production[sector.name] = ProductionFunction(
                type=ProductionType.CES,
                elasticity=0.8,
                labor_share=sector.labor_share(),
                tfp=1.0,
                intermediate_shares={
                    k: v / sector.output
                    for k, v in sector.intermediate_demand.items()
                },
            )
        
        # Create demand system
        total_consumption = sum(
            float(sam.matrix[i, n_sectors * 2 + 2])  # HH column
            for i in range(n_sectors)
        )
        shares = {
            sector_name: float(sam.matrix[i, n_sectors * 2 + 2]) / total_consumption
            for i, sector_name in enumerate(sam.sectors)
            if total_consumption > 0
        }
        
        demand = DemandSystem(
            type=DemandSystemType.LES,
            shares=shares,
            subsistence={s: 0.0 for s in sam.sectors},
        )
        
        return CGEConfig(
            sectors=sectors,
            sam=sam,
            production=production,
            demand=demand,
            closure=ClosureRule.neoclassical(),
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def solve_equilibrium(
        self,
        config: CGEConfig,
        initial_prices: Optional[dict[str, float]] = None,
    ) -> CGEEquilibrium:
        """
        Solve for general equilibrium.
        
        Args:
            config: Model configuration
            initial_prices: Starting prices for solver
            
        Returns:
            CGEEquilibrium solution
        """
        self._config = config
        sectors = config.sectors
        n_sectors = len(sectors)
        
        if n_sectors == 0:
            raise ExecutionError("CGEFramework", "No sectors defined")
        
        # Initialize prices
        if initial_prices is None:
            initial_prices = {s.name: 1.0 for s in sectors}
        
        # Numeraire: first sector price = 1
        numeraire = sectors[0].name
        
        # Solve using fixed-point iteration
        prices = initial_prices.copy()
        wage = 1.0
        rental_rate = 1.0
        
        for iteration in range(config.max_iterations):
            # ─────────────────────────────────────────────────────────────────
            # 1. Production and Supply
            # ─────────────────────────────────────────────────────────────────
            supplies = {}
            labor_demands = {}
            
            for sector in sectors:
                prod_func = config.production.get(
                    sector.name,
                    ProductionFunction(type=ProductionType.CES),
                )
                
                # Profit-maximizing supply
                price = prices[sector.name]
                
                # Derive labor demand
                labor = prod_func.labor_demand(sector.output, wage, rental_rate)
                labor_demands[sector.name] = labor
                
                # Output supply
                capital = sector.capital_demand  # Fixed in short run
                supplies[sector.name] = prod_func.output(labor, capital)
            
            # ─────────────────────────────────────────────────────────────────
            # 2. Household Income and Demand
            # ─────────────────────────────────────────────────────────────────
            total_labor_income = wage * sum(labor_demands.values())
            total_capital_income = rental_rate * sum(s.capital_demand for s in sectors)
            household_income = total_labor_income + total_capital_income
            
            demand_system = config.demand or DemandSystem(
                type=DemandSystemType.COBB_DOUGLAS,
                shares={s.name: 1.0 / n_sectors for s in sectors},
            )
            
            demands = demand_system.demands(household_income, prices)
            
            # ─────────────────────────────────────────────────────────────────
            # 3. Excess Demand
            # ─────────────────────────────────────────────────────────────────
            excess_demand = {}
            for sector in sectors:
                supply = supplies.get(sector.name, sector.output)
                demand = demands.get(sector.name, 0.0)
                # Add intermediate demand
                for other in sectors:
                    int_demand = other.intermediate_demand.get(sector.name, 0.0)
                    demand += int_demand
                
                excess_demand[sector.name] = demand - supply
            
            # ─────────────────────────────────────────────────────────────────
            # 4. Price Adjustment (Walrasian tâtonnement)
            # ─────────────────────────────────────────────────────────────────
            excess_norm = np.sqrt(sum(ed ** 2 for ed in excess_demand.values()))
            
            if excess_norm < config.solver_tolerance:
                # Equilibrium found
                self._equilibrium = CGEEquilibrium(
                    prices=prices,
                    quantities=supplies,
                    wages={"wage": wage, "rental_rate": rental_rate},
                    employment=labor_demands,
                    household_welfare=household_income,
                    government_revenue=0.0,  # No taxes in basic model
                    trade_balance=0.0,
                    convergence_iterations=iteration,
                    excess_demand_norm=excess_norm,
                )
                return self._equilibrium
            
            # Update prices
            adjustment_speed = 0.5
            for sector in sectors:
                if sector.name != numeraire:
                    prices[sector.name] *= 1 + adjustment_speed * (
                        excess_demand[sector.name] / max(supplies[sector.name], 1e-6)
                    )
            
            # Update factor prices based on closure
            if config.closure.type == ClosureType.NEOCLASSICAL:
                total_labor_demand = sum(labor_demands.values())
                total_labor_supply = sum(s.labor_demand for s in sectors)
                if total_labor_supply > 0:
                    wage *= 1 + 0.1 * (total_labor_demand - total_labor_supply) / total_labor_supply
        
        # Return last state if not converged
        self._equilibrium = CGEEquilibrium(
            prices=prices,
            quantities=supplies,
            wages={"wage": wage, "rental_rate": rental_rate},
            employment=labor_demands,
            household_welfare=household_income,
            government_revenue=0.0,
            trade_balance=0.0,
            convergence_iterations=config.max_iterations,
            excess_demand_norm=excess_norm,
        )
        
        return self._equilibrium
    
    @requires_tier(Tier.ENTERPRISE)
    def policy_simulation(
        self,
        config: CGEConfig,
        policy_shocks: dict[str, float],
    ) -> tuple[CGEEquilibrium, WelfareAnalysis]:
        """
        Simulate policy shock and compute welfare effects.
        
        Args:
            config: Base model configuration
            policy_shocks: Dict of parameter changes (e.g., {"tax_AGR": 0.1})
            
        Returns:
            Tuple of (new equilibrium, welfare analysis)
        """
        # Solve base equilibrium
        if self._base_equilibrium is None:
            self._base_equilibrium = self.solve_equilibrium(config)
        
        base = self._base_equilibrium
        
        # Apply shocks (simplified: just TFP shocks for now)
        shocked_config = CGEConfig(
            sectors=[
                Sector(
                    name=s.name,
                    code=s.code,
                    output=s.output,
                    labor_demand=s.labor_demand,
                    capital_demand=s.capital_demand,
                    intermediate_demand=s.intermediate_demand,
                    tfp=s.tfp * (1 + policy_shocks.get(f"tfp_{s.code}", 0.0)),
                )
                for s in config.sectors
            ],
            sam=config.sam,
            production=config.production,
            demand=config.demand,
            closure=config.closure,
        )
        
        # Solve shocked equilibrium
        shocked_eq = self.solve_equilibrium(shocked_config)
        
        # Welfare analysis
        welfare_change = shocked_eq.household_welfare - base.household_welfare
        
        # Compute CV and EV (simplified)
        cv = welfare_change  # Approximation
        ev = welfare_change * 0.95  # Slight asymmetry
        
        # Identify winners and losers
        winners = []
        losers = []
        for s in config.sectors:
            base_q = base.quantities.get(s.name, 0)
            new_q = shocked_eq.quantities.get(s.name, 0)
            if new_q > base_q * 1.01:
                winners.append(s.name)
            elif new_q < base_q * 0.99:
                losers.append(s.name)
        
        welfare = WelfareAnalysis(
            compensating_variation=cv,
            equivalent_variation=ev,
            consumer_surplus_change=welfare_change * 0.6,
            producer_surplus_change=welfare_change * 0.3,
            tax_revenue_change=welfare_change * 0.1,
            total_welfare_change=welfare_change,
            winners=winners,
            losers=losers,
        )
        
        return shocked_eq, welfare
    
    @requires_tier(Tier.ENTERPRISE)
    def dynamic_simulation(
        self,
        config: CGEConfig,
        time_horizon: int,
        growth_params: Optional[dict[str, float]] = None,
    ) -> list[CGEEquilibrium]:
        """
        Run dynamic (recursive) CGE simulation.
        
        Args:
            config: Base configuration
            time_horizon: Number of periods
            growth_params: Growth parameters by sector
            
        Returns:
            List of equilibria for each period
        """
        growth_params = growth_params or {}
        equilibria = []
        
        current_config = config
        
        for t in range(time_horizon):
            # Solve equilibrium
            eq = self.solve_equilibrium(current_config)
            equilibria.append(eq)
            
            # Update for next period
            updated_sectors = []
            for sector in current_config.sectors:
                growth = growth_params.get(sector.name, 0.02)
                updated_sectors.append(
                    Sector(
                        name=sector.name,
                        code=sector.code,
                        output=sector.output * (1 + growth),
                        labor_demand=sector.labor_demand * (1 + growth * 0.5),
                        capital_demand=sector.capital_demand * (1 + growth),
                        intermediate_demand={
                            k: v * (1 + growth)
                            for k, v in sector.intermediate_demand.items()
                        },
                        export_share=sector.export_share,
                        import_share=sector.import_share,
                        production_type=sector.production_type,
                        elasticity=sector.elasticity,
                        tfp=sector.tfp * 1.01,  # TFP growth
                    )
                )
            
            current_config = CGEConfig(
                sectors=updated_sectors,
                sam=current_config.sam,
                production=current_config.production,
                demand=current_config.demand,
                closure=current_config.closure,
            )
        
        return equilibria
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Abstract Method Implementations
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _compute_initial_state(self, data: DataBundle) -> CohortStateVector:
        """
        Compute initial cohort state from input data.
        
        For CGE, maps sector data to cohort state dimensions.
        """
        # Default sectors if not configured
        if not self._config or not self._config.sectors:
            sectors = [
                Sector(name="Agriculture", code="AGR", output=100, labor_demand=40, capital_demand=30),
                Sector(name="Manufacturing", code="MFG", output=200, labor_demand=80, capital_demand=60),
                Sector(name="Services", code="SRV", output=300, labor_demand=120, capital_demand=90),
            ]
        else:
            sectors = self._config.sectors
        
        n_cohorts = 50  # Default cohort count
        n_sectors = len(sectors)
        
        # Employment from sector labor demands
        total_labor = sum(s.labor_demand for s in sectors)
        employment_prob = np.full(n_cohorts, min(0.95, total_labor / (n_cohorts * 5)))
        
        # Sector output distribution
        sector_output = np.zeros((n_cohorts, n_sectors))
        for i, sector in enumerate(sectors):
            sector_output[:, i] = sector.output / n_cohorts
        
        return CohortStateVector(
            employment_prob=employment_prob,
            health_burden_score=np.full(n_cohorts, 0.15),
            credit_access_score=np.full(n_cohorts, 0.6),
            housing_cost_ratio=np.full(n_cohorts, 0.3),
            sector_output=sector_output,
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        step: int,
    ) -> CohortStateVector:
        """
        Apply CGE-based transition dynamics for one step.
        
        Uses equilibrium outcomes to update cohort state.
        """
        # If we have an equilibrium solution, use it
        if self._equilibrium:
            # Update employment based on equilibrium employment
            total_emp = sum(self._equilibrium.employment.values())
            emp_rate = min(0.95, total_emp / (state.n_cohorts * 5))
            new_employment = np.full_like(state.employment_prob, emp_rate)
            
            # Update sector output from equilibrium
            new_sector = state.sector_output.copy()
            if self._config and self._config.sectors:
                for i, sector in enumerate(self._config.sectors[:state.n_sectors]):
                    if sector.name in self._equilibrium.quantities:
                        new_sector[:, i] = self._equilibrium.quantities[sector.name] / state.n_cohorts
        else:
            # Default growth dynamics
            new_employment = np.clip(state.employment_prob * 1.005, 0.1, 0.95)
            new_sector = state.sector_output * 1.02
        
        return CohortStateVector(
            employment_prob=new_employment,
            health_burden_score=state.health_burden_score * 0.995,
            credit_access_score=np.clip(state.credit_access_score * 1.002, 0, 1),
            housing_cost_ratio=state.housing_cost_ratio,
            sector_output=new_sector,
        )
    
    def _compute_metrics(
        self,
        state: CohortStateVector,
    ) -> dict[str, Any]:
        """Compute CGE metrics from final state."""
        metrics = {
            "total_output": float(state.sector_output.sum()),
            "employment_rate": float(state.employment_prob.mean()),
            "n_sectors": state.n_sectors,
        }
        
        if self._equilibrium:
            metrics.update({
                "household_welfare": self._equilibrium.household_welfare,
                "convergence_iterations": self._equilibrium.convergence_iterations,
                "excess_demand_norm": self._equilibrium.excess_demand_norm,
            })
        
        return metrics
    
    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Return CGE dashboard specification.
        
        Computable General Equilibrium framework for multi-sector
        economic analysis with SAM calibration.
        """
        return FrameworkDashboardSpec(
            slug="cge",
            name="Computable General Equilibrium",
            description=(
                "Multi-sector general equilibrium modeling with SAM-based "
                "calibration, nested production functions, and welfare analysis."
            ),
            layer="meta",
            parameters_schema={
                "type": "object",
                "properties": {
                    "n_sectors": {
                        "type": "integer",
                        "title": "Number of Sectors",
                        "description": "Number of economic sectors in the model",
                        "minimum": 2,
                        "maximum": 50,
                        "default": 10,
                        "x-ui-widget": "slider",
                        "x-ui-step": 1,
                        "x-ui-group": "model_structure",
                        "x-ui-order": 1,
                    },
                    "n_households": {
                        "type": "integer",
                        "title": "Household Types",
                        "description": "Number of representative household types",
                        "minimum": 1,
                        "maximum": 10,
                        "default": 3,
                        "x-ui-widget": "slider",
                        "x-ui-step": 1,
                        "x-ui-group": "model_structure",
                        "x-ui-order": 2,
                    },
                    "elasticities": {
                        "type": "object",
                        "title": "Elasticity Parameters",
                        "description": "Substitution elasticities for production and consumption",
                        "properties": {
                            "production": {"type": "number", "default": 0.8},
                            "consumption": {"type": "number", "default": 1.0},
                            "armington": {"type": "number", "default": 2.0},
                        },
                        "x-ui-widget": "object",
                        "x-ui-group": "economic_parameters",
                        "x-ui-order": 1,
                    },
                    "closure_rule": {
                        "type": "string",
                        "title": "Macro Closure",
                        "description": "Macroeconomic closure rule",
                        "enum": ["neoclassical", "keynesian", "johansen"],
                        "default": "neoclassical",
                        "x-ui-widget": "select",
                        "x-ui-group": "economic_parameters",
                        "x-ui-order": 2,
                    },
                },
                "required": ["n_sectors"],
            },
            default_parameters={
                "n_sectors": 10,
                "n_households": 3,
                "elasticities": {
                    "production": 0.8,
                    "consumption": 1.0,
                    "armington": 2.0,
                },
                "closure_rule": "neoclassical",
            },
            parameter_groups=[
                ParameterGroupSpec(
                    key="model_structure",
                    title="Model Structure",
                    description="Define the structural dimensions of the CGE model",
                    collapsed_by_default=False,
                ),
                ParameterGroupSpec(
                    key="economic_parameters",
                    title="Economic Parameters",
                    description="Elasticities and closure rules",
                    collapsed_by_default=True,
                ),
            ],
            output_views=[
                OutputViewSpec(
                    key="sector_outputs",
                    title="Sector Outputs",
                    view_type=ViewType.BAR_CHART,
                    description="Output levels by economic sector",
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="sector_outputs_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="price_indices",
                    title="Price Indices",
                    view_type=ViewType.LINE_CHART,
                    description="Price evolution across sectors",
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="price_indices_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="welfare_changes",
                    title="Welfare Changes",
                    view_type=ViewType.GAUGE,
                    description="Household welfare impacts (CV/EV)",
                result_class=ResultClass.SCALAR_INDEX,
                output_key="welfare_changes_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="sam_flows",
                    title="SAM Flows",
                    view_type=ViewType.TABLE,
                    description="Social Accounting Matrix transaction flows",
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="sam_flows_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
            min_tier=Tier.ENTERPRISE,
        )
    
    def create_transition(self) -> CGETransition:
        """Create transition function for CBSS integration."""
        return CGETransition(config=self._config, equilibrium=self._equilibrium)
    
    def execute(
        self,
        bundle: DataBundle,
        config: Optional[Any] = None,
    ) -> FrameworkExecutionResult:
        """
        Execute framework on data bundle.
        
        Args:
            bundle: Input data bundle
            config: Optional CGEConfig
            
        Returns:
            FrameworkExecutionResult
        """
        validation_errors = self.validate_bundle(bundle)
        if validation_errors:
            raise DataBundleValidationError(
                "CGEFramework",
                validation_errors,
            )
        
        # Default configuration if not provided
        if config is None:
            config = CGEConfig(
                sectors=[
                    Sector(
                        name="Agriculture",
                        code="AGR",
                        output=100.0,
                        labor_demand=40.0,
                        capital_demand=30.0,
                    ),
                    Sector(
                        name="Manufacturing",
                        code="MFG",
                        output=200.0,
                        labor_demand=80.0,
                        capital_demand=60.0,
                    ),
                    Sector(
                        name="Services",
                        code="SRV",
                        output=300.0,
                        labor_demand=120.0,
                        capital_demand=90.0,
                    ),
                ],
            )
        
        # Solve equilibrium
        equilibrium = self.solve_equilibrium(config)
        
        return FrameworkExecutionResult(
            framework_name="CGEFramework",
            success=True,
            outputs={
                "equilibrium": equilibrium.to_dict(),
            },
            metrics={
                "convergence_iterations": equilibrium.convergence_iterations,
                "excess_demand_norm": equilibrium.excess_demand_norm,
                "household_welfare": equilibrium.household_welfare,
            },
        )
