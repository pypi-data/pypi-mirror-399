# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Systemic Risk Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Systemic Risk Assessment Framework.

Implements multiple approaches to measuring systemic risk in financial networks:
- DebtRank: Feedback-based contagion
- CoVaR: Conditional Value-at-Risk
- SRISK: Systemic Risk Index (capital shortfall)
- Network centrality measures
- Systemic importance scoring

References:
    - Battiston et al. (2012). "DebtRank: Too Central to Fail?"
    - Adrian & Brunnermeier (2016). "CoVaR"
    - Acharya et al. (2017). "Measuring Systemic Risk"
    - Acemoglu et al. (2015). "Systemic Risk and Stability"

Tier: PROFESSIONAL
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Mapping, Optional

import numpy as np

from krl_frameworks.core.base import (
    BaseMetaFramework,
    FrameworkMetadata,
    VerticalLayer,
)
from krl_frameworks.core.data_bundle import DataBundle
from krl_frameworks.core.state import CohortStateVector, StateTrajectory
from krl_frameworks.core.tier import Tier, requires_tier
from krl_frameworks.core.dashboard_spec import (
    FrameworkDashboardSpec,
    OutputViewSpec,
    ParameterGroupSpec,
    ViewType,
    ResultClass,
    TemporalSemantics,
)
from krl_frameworks.simulation.cbss import TransitionFunction

if TYPE_CHECKING:
    from krl_frameworks.core.config import FrameworkConfig

__all__ = ["SystemicRiskFramework"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Systemic Risk Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class SystemicRiskMeasure(Enum):
    """Types of systemic risk measures."""
    DEBTRANK = "DebtRank"
    COVAR = "CoVaR"
    SRISK = "SRISK"
    MES = "Marginal Expected Shortfall"
    DELTA_COVAR = "Delta CoVaR"


class ContagionMechanism(Enum):
    """Contagion transmission mechanisms."""
    DIRECT_EXPOSURE = "Direct Credit Exposure"
    FIRE_SALES = "Fire Sales"
    FUNDING_LIQUIDITY = "Funding Liquidity"
    INFORMATION = "Information Contagion"


@dataclass
class NetworkNode:
    """Financial institution node in network."""
    
    id: str = ""
    name: str = ""
    total_assets: float = 0.0
    equity: float = 0.0
    interbank_assets: float = 0.0
    interbank_liabilities: float = 0.0
    external_assets: float = 0.0
    
    @property
    def leverage(self) -> float:
        """Compute leverage ratio."""
        return self.total_assets / max(self.equity, 1e-10)
    
    @property
    def interbank_exposure_ratio(self) -> float:
        """Interbank assets as share of total."""
        return self.interbank_assets / max(self.total_assets, 1e-10)


@dataclass
class ExposureMatrix:
    """Bilateral exposure matrix between institutions."""
    
    exposures: np.ndarray = field(default_factory=lambda: np.array([]))
    node_ids: list[str] = field(default_factory=list)
    
    @property
    def n_nodes(self) -> int:
        return len(self.node_ids)
    
    def get_exposure(self, from_id: str, to_id: str) -> float:
        """Get bilateral exposure from one node to another."""
        if from_id not in self.node_ids or to_id not in self.node_ids:
            return 0.0
        i = self.node_ids.index(from_id)
        j = self.node_ids.index(to_id)
        return float(self.exposures[i, j])


@dataclass
class DebtRankResult:
    """DebtRank computation results."""
    
    # Node-level DebtRank
    debtrank_scores: dict[str, float] = field(default_factory=dict)
    
    # System-level
    system_debtrank: float = 0.0
    
    # Contagion dynamics
    rounds_to_stability: int = 0
    cumulative_losses: float = 0.0
    
    # Node rankings
    systemic_importance_rank: list[str] = field(default_factory=list)


@dataclass
class CoVaRResult:
    """CoVaR computation results."""
    
    # Node-level CoVaR
    covar_values: dict[str, float] = field(default_factory=dict)
    delta_covar: dict[str, float] = field(default_factory=dict)
    
    # System contribution
    system_var: float = 0.0
    
    # Confidence level
    confidence_level: float = 0.95


@dataclass
class SRISKResult:
    """SRISK (capital shortfall) results."""
    
    # Node-level SRISK
    srisk_values: dict[str, float] = field(default_factory=dict)
    
    # System-level
    aggregate_srisk: float = 0.0
    
    # Components
    mes_values: dict[str, float] = field(default_factory=dict)  # Marginal Expected Shortfall
    lrmes_values: dict[str, float] = field(default_factory=dict)  # Long-run MES
    
    # Prudential capital ratio
    prudential_ratio: float = 0.08


@dataclass
class NetworkMetrics:
    """Network topology metrics."""
    
    # Centrality measures
    degree_centrality: dict[str, float] = field(default_factory=dict)
    betweenness_centrality: dict[str, float] = field(default_factory=dict)
    eigenvector_centrality: dict[str, float] = field(default_factory=dict)
    
    # Network properties
    density: float = 0.0
    clustering_coefficient: float = 0.0
    average_path_length: float = 0.0
    
    # Concentration
    herfindahl_index: float = 0.0
    top_5_share: float = 0.0


@dataclass
class SystemicRiskMetrics:
    """Comprehensive systemic risk assessment."""
    
    # Primary measures
    debtrank: DebtRankResult = field(default_factory=DebtRankResult)
    covar: CoVaRResult = field(default_factory=CoVaRResult)
    srisk: SRISKResult = field(default_factory=SRISKResult)
    
    # Network analysis
    network: NetworkMetrics = field(default_factory=NetworkMetrics)
    
    # Overall assessment
    systemic_risk_score: float = 0.0  # 0-1 composite
    risk_category: str = ""  # Low, Medium, High, Critical
    top_systemic_institutions: list[str] = field(default_factory=list)
    
    # Stress scenario impacts
    stress_scenarios: dict[str, float] = field(default_factory=dict)


# ════════════════════════════════════════════════════════════════════════════════
# Systemic Risk Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class SystemicRiskTransition(TransitionFunction):
    """
    Transition function modeling systemic risk contagion.
    
    Simulates cascading failures through financial network.
    """
    
    name = "SystemicRiskTransition"
    
    def __init__(
        self,
        default_threshold: float = 0.0,
        recovery_rate: float = 0.4,
        contagion_factor: float = 0.5,
    ):
        self.default_threshold = default_threshold
        self.recovery_rate = recovery_rate
        self.contagion_factor = contagion_factor
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply systemic contagion dynamics."""
        params = params or {}
        
        n_cohorts = state.n_cohorts
        
        # Initial shock
        shock = params.get("shock_vector", np.zeros(n_cohorts))
        
        # Credit access as proxy for financial health
        new_credit = state.credit_access_prob - shock
        
        # Contagion from distressed institutions
        distressed = new_credit < 0.3
        contagion_loss = self.contagion_factor * np.sum(distressed) / n_cohorts
        
        new_credit = np.clip(new_credit - contagion_loss, 0.0, 1.0)
        
        # Sector output affected
        sector_multiplier = 0.95 + 0.1 * np.mean(new_credit)
        new_sector = state.sector_output * sector_multiplier
        
        return CohortStateVector(
            employment_prob=state.employment_prob,
            health_burden_score=state.health_burden_score,
            credit_access_prob=new_credit,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=state.opportunity_score,
            sector_output=new_sector,
            deprivation_vector=state.deprivation_vector,
        )


# ════════════════════════════════════════════════════════════════════════════════
# Systemic Risk Framework
# ════════════════════════════════════════════════════════════════════════════════


class SystemicRiskFramework(BaseMetaFramework):
    """
    Systemic Risk Assessment Framework.
    
    Production-grade implementation of multiple systemic risk measures
    for financial network analysis:
    
    - DebtRank: Feedback centrality measure
    - CoVaR: Conditional Value-at-Risk
    - SRISK: Systemic capital shortfall
    - Network centrality and topology analysis
    
    Token Weight: 6
    Tier: PROFESSIONAL
    
    Example:
        >>> framework = SystemicRiskFramework()
        >>> result = framework.compute_debtrank(
        ...     nodes=institutions,
        ...     exposures=exposure_matrix,
        ...     initial_shock={bank_a: 1.0}
        ... )
        >>> print(f"System DebtRank: {result.system_debtrank:.3f}")
    
    References:
        - Battiston et al. (2012): DebtRank
        - Adrian & Brunnermeier (2016): CoVaR
        - Acharya et al. (2017): SRISK
    """
    
    METADATA = FrameworkMetadata(
        slug="systemic-risk",
        name="Systemic Risk Assessment",
        version="1.0.0",
        layer=VerticalLayer.FINANCIAL_ECONOMIC,
        tier=Tier.PROFESSIONAL,
        description=(
            "Multi-method systemic risk assessment including DebtRank, "
            "CoVaR, SRISK, and network analysis."
        ),
        required_domains=["financial_network", "exposures", "balance_sheets"],
        output_domains=["debtrank", "covar", "srisk", "network_metrics"],
        constituent_models=["debtrank", "covar", "srisk", "network_centrality"],
        tags=["systemic-risk", "financial-stability", "contagion", "network"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(
        self,
        recovery_rate: float = 0.4,
        max_iterations: int = 100,
        convergence_threshold: float = 1e-6,
    ):
        super().__init__()
        self.recovery_rate = recovery_rate
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        self._transition_fn = SystemicRiskTransition(recovery_rate=recovery_rate)
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        """Return framework metadata."""
        return cls.METADATA
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Initialize state for financial network."""
        n_cohorts = config.cohort_size or 100
        
        return CohortStateVector(
            employment_prob=np.full(n_cohorts, 0.65),
            health_burden_score=np.full(n_cohorts, 0.2),
            credit_access_prob=np.random.beta(8, 2, n_cohorts),  # healthy baseline
            housing_cost_ratio=np.full(n_cohorts, 0.30),
            opportunity_score=np.random.beta(2, 2, n_cohorts),
            sector_output=np.full((n_cohorts, 5), 1000.0),
            deprivation_vector=np.full((n_cohorts, 6), 0.25),
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Apply systemic risk transition."""
        return self._transition_fn(state, t, config)
    
    def _compute_metrics(
        self,
        state: CohortStateVector,
    ) -> dict[str, Any]:
        """Compute systemic risk metrics from state."""
        distressed = state.credit_access_prob < 0.3
        return {
            "distress_rate": float(np.mean(distressed)),
            "mean_credit_health": float(np.mean(state.credit_access_prob)),
            "min_credit_health": float(np.min(state.credit_access_prob)),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        """Compute final output."""
        return {
            "framework": "systemic-risk",
            "n_periods": trajectory.n_periods,
        }

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return Systemic Risk dashboard specification."""
        return FrameworkDashboardSpec(
            slug="systemic-risk",
            name="Systemic Risk Assessment",
            description=(
                "Multi-method systemic risk assessment including DebtRank, "
                "CoVaR, SRISK, and network contagion analysis."
            ),
            layer="financial",
            parameters_schema={
                "type": "object",
                "properties": {
                    "initial_shock_node": {
                        "type": "string",
                        "title": "Initial Shock Node",
                        "description": "Node ID to apply initial shock",
                        "x-ui-widget": "select",
                        "x-ui-group": "shock",
                    },
                    "shock_magnitude": {
                        "type": "number",
                        "title": "Shock Magnitude",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0.5,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.05,
                        "x-ui-format": ".0%",
                        "x-ui-group": "shock",
                    },
                    "cascade_rounds": {
                        "type": "integer",
                        "title": "Cascade Rounds",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20,
                        "x-ui-widget": "slider",
                        "x-ui-group": "simulation",
                    },
                    "risk_method": {
                        "type": "string",
                        "title": "Risk Measure",
                        "enum": ["debtrank", "covar", "srisk"],
                        "default": "debtrank",
                        "x-ui-widget": "select",
                        "x-ui-group": "methodology",
                    },
                },
            },
            default_parameters={
                "initial_shock_node": "",
                "shock_magnitude": 0.5,
                "cascade_rounds": 20,
                "risk_method": "debtrank",
            },
            parameter_groups=[
                ParameterGroupSpec(key="shock", title="Shock Configuration", parameters=["initial_shock_node", "shock_magnitude"]),
                ParameterGroupSpec(key="simulation", title="Simulation Settings", parameters=["cascade_rounds"]),
                ParameterGroupSpec(key="methodology", title="Methodology", parameters=["risk_method"]),
            ],
            required_domains=["financial_network", "exposures", "balance_sheets"],
            min_tier=Tier.PROFESSIONAL,
            output_views=[
                OutputViewSpec(
                    key="system_debtrank",
                    title="System DebtRank",
                    view_type=ViewType.GAUGE,
                    config={"min": 0, "max": 1, "thresholds": [0.2, 0.5, 0.8], "format": ".1%"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="system_debtrank_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="network_graph",
                    title="Financial Network",
                    view_type=ViewType.NETWORK,
                    config={"node_field": "institution", "edge_field": "exposure", "color_by": "distress"},
                    result_class=ResultClass.STRUCTURAL_SIMILARITY,
                    output_key="network_graph_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="cascade_timeline",
                    title="Contagion Cascade",
                    view_type=ViewType.LINE_CHART,
                    config={"x_field": "round", "y_fields": ["cumulative_loss", "affected_nodes"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="cascade_timeline_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="risk_metrics",
                    title="Risk Metrics",
                    view_type=ViewType.METRIC_GRID,
                    config={"metrics": [
                        {"key": "debtrank", "label": "DebtRank", "format": ".1%"},
                        {"key": "covar", "label": "CoVaR", "format": ".1%"},
                        {"key": "srisk", "label": "SRISK", "format": "$,.0f"},
                        {"key": "affected_fraction", "label": "Affected Nodes", "format": ".0%"},
                    ]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="risk_metrics_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )
    
    # ════════════════════════════════════════════════════════════════════════════
    # Public API Methods
    # ════════════════════════════════════════════════════════════════════════════
    
    @requires_tier(Tier.PROFESSIONAL)
    def compute_debtrank(
        self,
        nodes: list[NetworkNode],
        exposures: ExposureMatrix,
        initial_shock: dict[str, float],
    ) -> DebtRankResult:
        """
        Compute DebtRank systemic risk measure.
        
        DebtRank measures the fraction of total economic value in the
        network affected by the distress/default of a set of nodes.
        
        Args:
            nodes: List of financial institution nodes
            exposures: Bilateral exposure matrix
            initial_shock: Initial relative equity loss per node (0-1)
        
        Returns:
            DebtRank results with node-level and system scores
        """
        n = len(nodes)
        if n == 0:
            return DebtRankResult()
        
        # Create node lookup
        node_map = {node.id: i for i, node in enumerate(nodes)}
        
        # Economic value weights (equity-based)
        total_equity = sum(node.equity for node in nodes)
        weights = np.array([node.equity / max(total_equity, 1e-10) for node in nodes])
        
        # Relative exposure matrix W[i,j] = exposure[i,j] / equity[j]
        W = np.zeros((n, n))
        for i, from_node in enumerate(nodes):
            for j, to_node in enumerate(nodes):
                exp = exposures.get_exposure(from_node.id, to_node.id)
                W[i, j] = exp / max(to_node.equity, 1e-10)
        
        # Initialize health levels (1 = healthy, 0 = defaulted)
        h = np.ones(n)
        
        # Apply initial shock
        for node_id, shock in initial_shock.items():
            if node_id in node_map:
                idx = node_map[node_id]
                h[idx] = max(0.0, 1.0 - shock)
        
        # Track if nodes have already transmitted distress
        transmitted = np.zeros(n, dtype=bool)
        for node_id in initial_shock:
            if node_id in node_map:
                transmitted[node_map[node_id]] = True
        
        # Iterate until convergence
        cumulative_loss = 0.0
        for round_num in range(self.max_iterations):
            h_new = h.copy()
            
            for i in range(n):
                if transmitted[i]:
                    continue
                
                # Sum losses from counterparties
                loss = 0.0
                for j in range(n):
                    if i != j:
                        loss += W[j, i] * (1 - h[j])
                
                # Apply loss (bounded)
                h_new[i] = max(0.0, h[i] - loss)
                
                if h_new[i] < 1.0:
                    transmitted[i] = True
            
            # Check convergence
            delta = np.sum(np.abs(h_new - h))
            cumulative_loss += np.sum(weights * (h - h_new))
            h = h_new
            
            if delta < self.convergence_threshold:
                break
        
        # Compute DebtRank scores
        debtrank_scores = {}
        for i, node in enumerate(nodes):
            debtrank_scores[node.id] = float(weights[i] * (1 - h[i]))
        
        # System DebtRank
        system_debtrank = float(np.sum(weights * (1 - h)))
        
        # Rank by systemic importance
        ranked = sorted(debtrank_scores.items(), key=lambda x: -x[1])
        
        return DebtRankResult(
            debtrank_scores=debtrank_scores,
            system_debtrank=system_debtrank,
            rounds_to_stability=round_num + 1,
            cumulative_losses=float(cumulative_loss),
            systemic_importance_rank=[node_id for node_id, _ in ranked],
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def compute_covar(
        self,
        returns: np.ndarray,
        system_returns: np.ndarray,
        confidence_level: float = 0.95,
        node_names: Optional[list[str]] = None,
    ) -> CoVaRResult:
        """
        Compute Conditional Value-at-Risk (CoVaR).
        
        CoVaR measures the VaR of the system conditional on an
        institution being in distress.
        
        Args:
            returns: Matrix of institution returns (T, n)
            system_returns: System-wide returns (T,)
            confidence_level: VaR confidence level
            node_names: Optional names for institutions
        
        Returns:
            CoVaR results
        """
        T, n = returns.shape
        names = node_names or [f"Node_{i}" for i in range(n)]
        
        # System VaR
        system_var = float(np.percentile(system_returns, (1 - confidence_level) * 100))
        
        covar_values = {}
        delta_covar = {}
        
        for i in range(n):
            inst_returns = returns[:, i]
            inst_var = np.percentile(inst_returns, (1 - confidence_level) * 100)
            
            # Conditional on institution being at its VaR
            distress_mask = inst_returns <= inst_var
            if np.sum(distress_mask) > 5:
                conditional_system = system_returns[distress_mask]
                covar_i = float(np.percentile(conditional_system, (1 - confidence_level) * 100))
            else:
                covar_i = system_var
            
            # Conditional on institution at median (normal state)
            median_mask = np.abs(inst_returns - np.median(inst_returns)) < np.std(inst_returns)
            if np.sum(median_mask) > 5:
                normal_system = system_returns[median_mask]
                covar_normal = float(np.percentile(normal_system, (1 - confidence_level) * 100))
            else:
                covar_normal = system_var
            
            covar_values[names[i]] = covar_i
            delta_covar[names[i]] = covar_i - covar_normal
        
        return CoVaRResult(
            covar_values=covar_values,
            delta_covar=delta_covar,
            system_var=system_var,
            confidence_level=confidence_level,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def compute_srisk(
        self,
        nodes: list[NetworkNode],
        expected_shortfall: dict[str, float],
        prudential_ratio: float = 0.08,
        crisis_threshold: float = 0.40,
    ) -> SRISKResult:
        """
        Compute SRISK (Systemic Risk Index).
        
        SRISK measures expected capital shortfall during a crisis.
        
        Args:
            nodes: List of financial institutions
            expected_shortfall: Expected loss during crisis per node
            prudential_ratio: Required capital ratio
            crisis_threshold: Market decline defining crisis
        
        Returns:
            SRISK results
        """
        srisk_values = {}
        mes_values = {}
        lrmes_values = {}
        aggregate_srisk = 0.0
        
        for node in nodes:
            # Marginal Expected Shortfall
            mes = expected_shortfall.get(node.id, 0.05)
            mes_values[node.id] = float(mes)
            
            # Long-run MES (approximation: MES * 1 / (1 - LRMES) - 1)
            lrmes = 1 - np.exp(-18 * mes)  # Approximation from Brownlees & Engle
            lrmes_values[node.id] = float(lrmes)
            
            # SRISK = max(0, k*A - W*(1 - LRMES))
            # k = prudential ratio, A = total assets, W = market equity
            k = prudential_ratio
            A = node.total_assets
            W = node.equity
            
            srisk = max(0.0, k * A - W * (1 - lrmes))
            srisk_values[node.id] = float(srisk)
            aggregate_srisk += srisk
        
        return SRISKResult(
            srisk_values=srisk_values,
            aggregate_srisk=float(aggregate_srisk),
            mes_values=mes_values,
            lrmes_values=lrmes_values,
            prudential_ratio=prudential_ratio,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def compute_network_metrics(
        self,
        exposures: ExposureMatrix,
    ) -> NetworkMetrics:
        """
        Compute network topology metrics.
        
        Args:
            exposures: Bilateral exposure matrix
        
        Returns:
            Network centrality and topology metrics
        """
        n = exposures.n_nodes
        if n == 0:
            return NetworkMetrics()
        
        A = (exposures.exposures > 0).astype(float)  # Adjacency matrix
        
        # Degree centrality
        out_degree = A.sum(axis=1)
        in_degree = A.sum(axis=0)
        total_degree = out_degree + in_degree
        max_degree = 2 * (n - 1)
        
        degree_centrality = {
            exposures.node_ids[i]: float(total_degree[i] / max_degree)
            for i in range(n)
        }
        
        # Network density
        max_edges = n * (n - 1)
        actual_edges = np.sum(A)
        density = float(actual_edges / max_edges) if max_edges > 0 else 0.0
        
        # Eigenvector centrality (power iteration)
        x = np.ones(n) / n
        for _ in range(100):
            x_new = A.T @ x
            norm = np.linalg.norm(x_new)
            if norm > 0:
                x_new = x_new / norm
            if np.linalg.norm(x_new - x) < 1e-6:
                break
            x = x_new
        
        eigenvector_centrality = {
            exposures.node_ids[i]: float(x[i])
            for i in range(n)
        }
        
        # Betweenness centrality (simplified)
        betweenness = np.zeros(n)
        for s in range(n):
            for t in range(n):
                if s != t and A[s, t] > 0:
                    # Simple approximation: nodes on direct path
                    for v in range(n):
                        if v != s and v != t:
                            if A[s, v] > 0 and A[v, t] > 0:
                                betweenness[v] += 1
        
        max_betweenness = (n - 1) * (n - 2)
        betweenness_centrality = {
            exposures.node_ids[i]: float(betweenness[i] / max_betweenness) if max_betweenness > 0 else 0.0
            for i in range(n)
        }
        
        # Clustering coefficient
        triangles = 0
        possible_triangles = 0
        for i in range(n):
            neighbors = np.where(A[i] > 0)[0]
            k = len(neighbors)
            if k >= 2:
                possible_triangles += k * (k - 1) / 2
                for j1 in neighbors:
                    for j2 in neighbors:
                        if j1 < j2 and A[j1, j2] > 0:
                            triangles += 1
        
        clustering = float(triangles / possible_triangles) if possible_triangles > 0 else 0.0
        
        # Concentration (based on exposure volumes)
        total_exposure = np.sum(exposures.exposures)
        if total_exposure > 0:
            node_exposures = exposures.exposures.sum(axis=1)
            shares = node_exposures / total_exposure
            hhi = float(np.sum(shares ** 2))
            top_5_share = float(np.sum(np.sort(shares)[-5:]))
        else:
            hhi = 0.0
            top_5_share = 0.0
        
        return NetworkMetrics(
            degree_centrality=degree_centrality,
            betweenness_centrality=betweenness_centrality,
            eigenvector_centrality=eigenvector_centrality,
            density=density,
            clustering_coefficient=clustering,
            average_path_length=2.0,  # Simplified
            herfindahl_index=hhi,
            top_5_share=top_5_share,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def assess_systemic_risk(
        self,
        nodes: list[NetworkNode],
        exposures: ExposureMatrix,
        returns: Optional[np.ndarray] = None,
        system_returns: Optional[np.ndarray] = None,
    ) -> SystemicRiskMetrics:
        """
        Comprehensive systemic risk assessment.
        
        Args:
            nodes: Financial institutions
            exposures: Exposure matrix
            returns: Optional return history for CoVaR
            system_returns: Optional system returns for CoVaR
        
        Returns:
            Complete systemic risk metrics
        """
        # DebtRank from largest institution shock
        largest_node = max(nodes, key=lambda x: x.total_assets) if nodes else None
        initial_shock = {largest_node.id: 1.0} if largest_node else {}
        debtrank = self.compute_debtrank(nodes, exposures, initial_shock)
        
        # CoVaR (if returns provided)
        if returns is not None and system_returns is not None:
            covar = self.compute_covar(returns, system_returns)
        else:
            covar = CoVaRResult()
        
        # SRISK
        expected_shortfall = {node.id: 0.05 for node in nodes}  # Default 5%
        srisk = self.compute_srisk(nodes, expected_shortfall)
        
        # Network metrics
        network = self.compute_network_metrics(exposures)
        
        # Composite score
        score_components = [
            debtrank.system_debtrank,
            min(1.0, srisk.aggregate_srisk / sum(n.equity for n in nodes) if nodes else 0),
            1 - network.density,  # High density = more stable
        ]
        systemic_risk_score = float(np.mean(score_components))
        
        # Risk category
        if systemic_risk_score < 0.2:
            risk_category = "Low"
        elif systemic_risk_score < 0.4:
            risk_category = "Medium"
        elif systemic_risk_score < 0.6:
            risk_category = "High"
        else:
            risk_category = "Critical"
        
        # Top institutions
        top_institutions = debtrank.systemic_importance_rank[:5]
        
        return SystemicRiskMetrics(
            debtrank=debtrank,
            covar=covar,
            srisk=srisk,
            network=network,
            systemic_risk_score=systemic_risk_score,
            risk_category=risk_category,
            top_systemic_institutions=top_institutions,
        )
