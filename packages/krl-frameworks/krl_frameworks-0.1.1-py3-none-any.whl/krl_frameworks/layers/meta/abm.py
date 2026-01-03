# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - ABM (Agent-Based Model) Meta-Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
ABMFramework: Generic Agent-Based Model Meta-Framework.

This meta-framework provides a general-purpose agent-based modeling platform
for socioeconomic simulation. Unlike domain-specific ABM implementations
(e.g., SDABMFramework), this framework offers:

1. Heterogeneous Agent Support: Multiple agent types with distinct behaviors
2. Interaction Rules: Spatial, network, and market-based interactions  
3. Emergent Behavior Analysis: Aggregate pattern detection from micro rules
4. Calibration Interface: Match macro moments from micro parameters

Key Features:
    - Agent Populations: Define populations with attributes and behavioral rules
    - Interaction Networks: Network-based, spatial, or random matching
    - Market Mechanisms: Price formation, auction, and matching markets
    - Equilibrium Detection: Steady-state and ergodic distribution analysis
    - Sensitivity Analysis: Monte Carlo and Sobol indices

CBSS Integration:
    - Maps agent populations to CohortStateVector dimensions
    - Implements TransitionFunction via agent behavior aggregation
    - Supports policy shocks as agent-level parameter changes

Theoretical Foundation:
    - Tesfatsion & Judd (2006): Handbook of Computational Economics Vol. 2
    - Epstein & Axtell (1996): Growing Artificial Societies
    - LeBaron (2006): Agent-based Financial Markets

Tier: ENTERPRISE (full orchestration requires advanced license)
      PROFESSIONAL tier for basic simulations
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, Mapping, Optional, Sequence

import numpy as np
from scipy import stats

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
    "ABMFramework",
    "ABMConfig",
    "AgentType",
    "InteractionMode",
    "Agent",
    "AgentPopulation",
    "InteractionNetwork",
    "ABMTransition",
    "ABMResults",
]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Enumerations
# ════════════════════════════════════════════════════════════════════════════════


class AgentType(Enum):
    """Types of agents in ABM."""
    
    HOUSEHOLD = auto()      # Consumer households
    FIRM = auto()           # Production firms
    BANK = auto()           # Financial intermediaries
    GOVERNMENT = auto()     # Public sector agents
    WORKER = auto()         # Labor market participants
    INVESTOR = auto()       # Portfolio investors
    CUSTOM = auto()         # User-defined agent type


class InteractionMode(Enum):
    """Agent interaction mechanisms."""
    
    RANDOM_MATCHING = auto()      # Random pairwise matching
    NETWORK = auto()              # Network-based (graph topology)
    SPATIAL = auto()              # Geographic proximity
    MARKET = auto()               # Double-auction market
    HIERARCHICAL = auto()         # Principal-agent relationships
    MIXED = auto()                # Combination of modes


class BehaviorRule(Enum):
    """Agent behavioral decision rules."""
    
    RATIONAL = auto()             # Full optimization
    BOUNDED_RATIONAL = auto()     # Satisficing / heuristics
    ADAPTIVE = auto()             # Learning and adaptation
    IMITATION = auto()            # Copy successful neighbors
    RULE_OF_THUMB = auto()        # Simple decision rules
    STOCHASTIC = auto()           # Random with probabilities


# ════════════════════════════════════════════════════════════════════════════════
# Agent Definitions
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class AgentAttributes:
    """
    Dynamic attributes of an agent.
    
    Attributes:
        wealth: Current wealth/assets
        income: Flow income
        consumption: Current consumption
        productivity: Production efficiency
        connections: Number of network connections
        beliefs: Subjective state beliefs (for bounded rationality)
        custom: User-defined attributes
    """
    
    wealth: float = 0.0
    income: float = 0.0
    consumption: float = 0.0
    productivity: float = 1.0
    connections: int = 0
    beliefs: dict[str, float] = field(default_factory=dict)
    custom: dict[str, Any] = field(default_factory=dict)
    
    def to_vector(self) -> np.ndarray:
        """Convert core attributes to numpy array."""
        return np.array([
            self.wealth,
            self.income,
            self.consumption,
            self.productivity,
            self.connections,
        ])


@dataclass
class Agent:
    """
    Individual agent in the ABM.
    
    Attributes:
        id: Unique agent identifier
        agent_type: Type classification
        attributes: Dynamic state
        behavior: Decision rule
        active: Whether agent participates
    """
    
    id: int
    agent_type: AgentType
    attributes: AgentAttributes = field(default_factory=AgentAttributes)
    behavior: BehaviorRule = BehaviorRule.BOUNDED_RATIONAL
    active: bool = True
    
    def copy(self) -> Agent:
        """Create a copy of this agent."""
        return Agent(
            id=self.id,
            agent_type=self.agent_type,
            attributes=AgentAttributes(
                wealth=self.attributes.wealth,
                income=self.attributes.income,
                consumption=self.attributes.consumption,
                productivity=self.attributes.productivity,
                connections=self.attributes.connections,
                beliefs=self.attributes.beliefs.copy(),
                custom=self.attributes.custom.copy(),
            ),
            behavior=self.behavior,
            active=self.active,
        )


@dataclass
class AgentPopulation:
    """
    Collection of homogeneous agents.
    
    Attributes:
        name: Population identifier
        agent_type: Type of agents in population
        count: Number of agents
        initial_distribution: Distribution of initial attributes
        behavior: Default behavior rule
        mortality_rate: Agent exit rate per period
        birth_rate: Agent entry rate per period
    """
    
    name: str
    agent_type: AgentType
    count: int
    initial_distribution: dict[str, tuple[str, dict]] = field(default_factory=dict)
    behavior: BehaviorRule = BehaviorRule.BOUNDED_RATIONAL
    mortality_rate: float = 0.0
    birth_rate: float = 0.0
    
    def initialize_agents(self, seed: Optional[int] = None) -> list[Agent]:
        """
        Create agent population with distributed attributes.
        
        Returns:
            List of initialized agents
        """
        rng = np.random.default_rng(seed)
        agents = []
        
        for i in range(self.count):
            attrs = AgentAttributes()
            
            # Sample attributes from distributions
            for attr_name, (dist_type, dist_params) in self.initial_distribution.items():
                if dist_type == "normal":
                    value = rng.normal(**dist_params)
                elif dist_type == "lognormal":
                    value = rng.lognormal(**dist_params)
                elif dist_type == "uniform":
                    value = rng.uniform(**dist_params)
                elif dist_type == "exponential":
                    value = rng.exponential(**dist_params)
                elif dist_type == "pareto":
                    value = rng.pareto(**dist_params)
                else:
                    value = dist_params.get("value", 0.0)
                
                if hasattr(attrs, attr_name):
                    setattr(attrs, attr_name, max(0, value))
                else:
                    attrs.custom[attr_name] = value
            
            agent = Agent(
                id=i,
                agent_type=self.agent_type,
                attributes=attrs,
                behavior=self.behavior,
            )
            agents.append(agent)
        
        return agents


# ════════════════════════════════════════════════════════════════════════════════
# Interaction Network
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class InteractionNetwork:
    """
    Network structure for agent interactions.
    
    Attributes:
        mode: Type of interaction mechanism
        adjacency: Adjacency matrix (for network mode)
        coordinates: Spatial coordinates (for spatial mode)
        parameters: Mode-specific parameters
    """
    
    mode: InteractionMode
    adjacency: Optional[np.ndarray] = None
    coordinates: Optional[np.ndarray] = None
    parameters: dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def random_network(
        cls,
        n_agents: int,
        edge_probability: float = 0.1,
        seed: Optional[int] = None,
    ) -> InteractionNetwork:
        """Create Erdős-Rényi random network."""
        rng = np.random.default_rng(seed)
        adj = rng.random((n_agents, n_agents)) < edge_probability
        adj = (adj | adj.T).astype(float)  # Symmetric
        np.fill_diagonal(adj, 0)
        
        return cls(
            mode=InteractionMode.NETWORK,
            adjacency=adj,
            parameters={"type": "erdos_renyi", "p": edge_probability},
        )
    
    @classmethod
    def scale_free_network(
        cls,
        n_agents: int,
        m: int = 2,
        seed: Optional[int] = None,
    ) -> InteractionNetwork:
        """Create Barabási-Albert scale-free network."""
        rng = np.random.default_rng(seed)
        adj = np.zeros((n_agents, n_agents))
        
        # Start with complete graph on m+1 nodes
        for i in range(m + 1):
            for j in range(i + 1, m + 1):
                adj[i, j] = adj[j, i] = 1.0
        
        # Preferential attachment
        degrees = adj.sum(axis=1)
        for new_node in range(m + 1, n_agents):
            probs = degrees[:new_node] / degrees[:new_node].sum()
            targets = rng.choice(new_node, size=m, replace=False, p=probs)
            for t in targets:
                adj[new_node, t] = adj[t, new_node] = 1.0
            degrees = adj.sum(axis=1)
        
        return cls(
            mode=InteractionMode.NETWORK,
            adjacency=adj,
            parameters={"type": "barabasi_albert", "m": m},
        )
    
    @classmethod
    def spatial_grid(
        cls,
        n_agents: int,
        grid_size: tuple[int, int] = (10, 10),
        seed: Optional[int] = None,
    ) -> InteractionNetwork:
        """Create spatial grid layout."""
        rng = np.random.default_rng(seed)
        coords = np.column_stack([
            rng.uniform(0, grid_size[0], n_agents),
            rng.uniform(0, grid_size[1], n_agents),
        ])
        
        return cls(
            mode=InteractionMode.SPATIAL,
            coordinates=coords,
            parameters={"grid_size": grid_size},
        )
    
    def get_neighbors(
        self,
        agent_id: int,
        radius: float = 1.0,
    ) -> list[int]:
        """Get neighbors of an agent."""
        if self.mode == InteractionMode.NETWORK and self.adjacency is not None:
            return list(np.where(self.adjacency[agent_id] > 0)[0])
        
        elif self.mode == InteractionMode.SPATIAL and self.coordinates is not None:
            distances = np.linalg.norm(
                self.coordinates - self.coordinates[agent_id],
                axis=1,
            )
            neighbors = np.where((distances > 0) & (distances <= radius))[0]
            return list(neighbors)
        
        return []


# ════════════════════════════════════════════════════════════════════════════════
# ABM Configuration
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class ABMConfig:
    """
    Configuration for ABM simulation.
    
    Attributes:
        populations: List of agent populations
        interaction: Interaction network structure
        time_horizon: Number of simulation periods
        interaction_rate: Probability of interaction per period
        market_mechanism: Market clearing mechanism
        equilibrium_tolerance: Tolerance for convergence
        monte_carlo_runs: Number of MC replications
        seed: Random seed
    """
    
    populations: list[AgentPopulation] = field(default_factory=list)
    interaction: Optional[InteractionNetwork] = None
    time_horizon: int = 100
    interaction_rate: float = 0.1
    market_mechanism: str = "walrasian"
    equilibrium_tolerance: float = 1e-6
    monte_carlo_runs: int = 100
    seed: Optional[int] = None
    
    def total_agents(self) -> int:
        """Total number of agents across all populations."""
        return sum(p.count for p in self.populations)


# ════════════════════════════════════════════════════════════════════════════════
# ABM Results
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class ABMResults:
    """
    Results from ABM simulation.
    
    Attributes:
        wealth_distribution: Final wealth distribution
        gini_coefficient: Wealth inequality
        mean_wealth: Average wealth
        median_wealth: Median wealth
        top_1_share: Share of wealth held by top 1%
        network_clustering: Clustering coefficient
        convergence_time: Periods to equilibrium
        steady_state_achieved: Whether steady state was reached
        aggregate_output: Total production
        agent_trajectories: Time series of agent states
    """
    
    wealth_distribution: np.ndarray
    gini_coefficient: float
    mean_wealth: float
    median_wealth: float
    top_1_share: float
    network_clustering: float
    convergence_time: int
    steady_state_achieved: bool
    aggregate_output: float
    agent_trajectories: Optional[np.ndarray] = None
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize results."""
        return {
            "gini_coefficient": self.gini_coefficient,
            "mean_wealth": self.mean_wealth,
            "median_wealth": self.median_wealth,
            "top_1_share": self.top_1_share,
            "network_clustering": self.network_clustering,
            "convergence_time": self.convergence_time,
            "steady_state_achieved": self.steady_state_achieved,
            "aggregate_output": self.aggregate_output,
            "wealth_percentiles": {
                "p10": float(np.percentile(self.wealth_distribution, 10)),
                "p25": float(np.percentile(self.wealth_distribution, 25)),
                "p50": float(np.percentile(self.wealth_distribution, 50)),
                "p75": float(np.percentile(self.wealth_distribution, 75)),
                "p90": float(np.percentile(self.wealth_distribution, 90)),
            },
        }


# ════════════════════════════════════════════════════════════════════════════════
# ABM Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class ABMTransition(TransitionFunction):
    """
    ABM state transition function for CBSS integration.
    
    Maps agent-level dynamics to cohort-level state transitions,
    enabling integration with the broader KRL simulation engine.
    """
    
    name = "ABMTransition"
    
    def __init__(
        self,
        config: Optional[ABMConfig] = None,
        agents: Optional[list[Agent]] = None,
    ):
        self.config = config or ABMConfig()
        self.agents = agents or []
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: Any,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """
        Apply ABM transition dynamics.
        
        Maps micro-level agent interactions to macro state updates.
        """
        params = params or {}
        
        # ─────────────────────────────────────────────────────────────────────
        # 1. Agent Interaction Phase
        # ─────────────────────────────────────────────────────────────────────
        interaction_rate = params.get("interaction_rate", self.config.interaction_rate)
        
        # Update agent states based on interactions
        if self.agents:
            self._execute_interactions(interaction_rate)
        
        # ─────────────────────────────────────────────────────────────────────
        # 2. Map Agent States to Cohort State
        # ─────────────────────────────────────────────────────────────────────
        
        # Aggregate wealth distribution affects credit access
        if self.agents:
            wealth_arr = np.array([a.attributes.wealth for a in self.agents])
            mean_wealth = wealth_arr.mean() if len(wealth_arr) > 0 else 1.0
            wealth_std = wealth_arr.std() if len(wealth_arr) > 0 else 0.1
            
            # Map to cohort credit access (normalized by mean wealth)
            normalized_wealth = wealth_arr / max(mean_wealth, 1e-6)
            
            # Update cohort credit access based on wealth distribution
            n_cohorts = state.n_cohorts
            n_agents_per_cohort = max(1, len(self.agents) // n_cohorts)
            
            new_credit_access = np.zeros(n_cohorts)
            for i in range(n_cohorts):
                start_idx = i * n_agents_per_cohort
                end_idx = min((i + 1) * n_agents_per_cohort, len(self.agents))
                if start_idx < len(normalized_wealth):
                    cohort_wealth = normalized_wealth[start_idx:end_idx]
                    new_credit_access[i] = np.clip(cohort_wealth.mean() * 0.5, 0, 1)
        else:
            new_credit_access = state.credit_access_score * 1.001  # Small growth
        
        # ─────────────────────────────────────────────────────────────────────
        # 3. Update Employment Based on Firm Productivity
        # ─────────────────────────────────────────────────────────────────────
        productivity_shock = params.get("productivity_shock", 0.0)
        new_employment = np.clip(
            state.employment_prob * (1 + 0.01 + productivity_shock),
            0.0,
            1.0,
        )
        
        # ─────────────────────────────────────────────────────────────────────
        # 4. Sector Output from Agent Production
        # ─────────────────────────────────────────────────────────────────────
        output_growth = params.get("output_growth", 0.02)
        new_sector_output = state.sector_output * (1 + output_growth)
        
        # ─────────────────────────────────────────────────────────────────────
        # 5. Build New State
        # ─────────────────────────────────────────────────────────────────────
        return CohortStateVector(
            employment_prob=new_employment,
            health_burden_score=state.health_burden_score * 0.99,  # Small improvement
            credit_access_score=np.clip(new_credit_access, 0, 1),
            housing_cost_ratio=state.housing_cost_ratio,
            sector_output=new_sector_output,
        )
    
    def _execute_interactions(self, rate: float) -> None:
        """Execute agent interactions for one period."""
        rng = np.random.default_rng()
        n_interactions = int(len(self.agents) * rate)
        
        for _ in range(n_interactions):
            if len(self.agents) < 2:
                break
            
            # Random matching
            i, j = rng.choice(len(self.agents), size=2, replace=False)
            agent_a = self.agents[i]
            agent_b = self.agents[j]
            
            # Simple exchange dynamics
            if agent_a.active and agent_b.active:
                # Wealth transfer based on productivity differential
                prod_diff = agent_a.attributes.productivity - agent_b.attributes.productivity
                transfer = prod_diff * 0.01 * min(
                    agent_a.attributes.wealth,
                    agent_b.attributes.wealth,
                )
                agent_a.attributes.wealth += transfer
                agent_b.attributes.wealth -= transfer
                
                # Learning: adjust productivity towards average
                avg_prod = (agent_a.attributes.productivity + agent_b.attributes.productivity) / 2
                agent_a.attributes.productivity = 0.99 * agent_a.attributes.productivity + 0.01 * avg_prod
                agent_b.attributes.productivity = 0.99 * agent_b.attributes.productivity + 0.01 * avg_prod


# ════════════════════════════════════════════════════════════════════════════════
# ABM Framework
# ════════════════════════════════════════════════════════════════════════════════


class ABMFramework(BaseMetaFramework):
    """
    Generic Agent-Based Model Meta-Framework.
    
    Provides a flexible platform for building heterogeneous agent
    models with various interaction mechanisms and behavioral rules.
    
    Example:
        >>> from krl_frameworks.layers.meta import ABMFramework, AgentPopulation, AgentType
        >>> 
        >>> # Define populations
        >>> households = AgentPopulation(
        ...     name="households",
        ...     agent_type=AgentType.HOUSEHOLD,
        ...     count=1000,
        ...     initial_distribution={
        ...         "wealth": ("lognormal", {"mean": 10.0, "sigma": 1.5}),
        ...         "productivity": ("normal", {"loc": 1.0, "scale": 0.2}),
        ...     },
        ... )
        >>> 
        >>> framework = ABMFramework()
        >>> config = ABMConfig(populations=[households], time_horizon=50)
        >>> results = framework.run_simulation(config)
    
    Tier: ENTERPRISE for full features, PROFESSIONAL for basic simulation
    """
    
    def __init__(self):
        super().__init__()
        self._agents: list[Agent] = []
        self._network: Optional[InteractionNetwork] = None
        self._config: Optional[ABMConfig] = None
    
    def metadata(self) -> FrameworkMetadata:
        """Return framework metadata."""
        return FrameworkMetadata(
            name="ABMFramework",
            slug="abm",
            version="1.0.0",
            description=(
                "Generic Agent-Based Model meta-framework for heterogeneous "
                "agent simulations with network interactions and market mechanisms."
            ),
            layer=VerticalLayer.META_PEER_FRAMEWORKS,
            tier=Tier.PROFESSIONAL,
            constituent_models=[
                "Epstein-Axtell Sugarscape",
                "LeBaron Financial ABM",
                "Tesfatsion ACE",
            ],
            tags=[
                "heterogeneous_agents",
                "network_interactions",
                "market_mechanisms",
                "emergent_behavior",
                "wealth_dynamics",
                "monte_carlo_simulation",
            ],
        )
    
    def validate_bundle(self, bundle: DataBundle) -> list[str]:
        """Validate input data bundle."""
        errors = []
        
        # ABM can work with minimal data - populations can be generated
        if DataDomain.DEMOGRAPHIC in bundle.domains:
            demo = bundle.get_domain_data(DataDomain.DEMOGRAPHIC)
            if demo is not None and hasattr(demo, "shape"):
                if demo.shape[0] < 1:
                    errors.append("Demographic data must have at least one record")
        
        return errors
    
    @requires_tier(Tier.PROFESSIONAL)
    def initialize_agents(
        self,
        config: ABMConfig,
        seed: Optional[int] = None,
    ) -> list[Agent]:
        """
        Initialize agent populations.
        
        Args:
            config: ABM configuration
            seed: Random seed
            
        Returns:
            List of initialized agents
        """
        self._config = config
        self._agents = []
        
        for population in config.populations:
            pop_agents = population.initialize_agents(seed=seed)
            self._agents.extend(pop_agents)
        
        # Re-assign IDs to be unique across populations
        for i, agent in enumerate(self._agents):
            agent.id = i
        
        # Initialize network if not provided
        if config.interaction is None:
            self._network = InteractionNetwork.scale_free_network(
                n_agents=len(self._agents),
                m=3,
                seed=seed,
            )
        else:
            self._network = config.interaction
        
        # Set connection counts from network
        if self._network.adjacency is not None:
            for agent in self._agents:
                if agent.id < self._network.adjacency.shape[0]:
                    agent.attributes.connections = int(
                        self._network.adjacency[agent.id].sum()
                    )
        
        return self._agents
    
    @requires_tier(Tier.PROFESSIONAL)
    def run_simulation(
        self,
        config: ABMConfig,
        initial_state: Optional[CohortStateVector] = None,
    ) -> ABMResults:
        """
        Run ABM simulation.
        
        Args:
            config: Simulation configuration
            initial_state: Optional initial cohort state
            
        Returns:
            ABMResults with simulation outcomes
        """
        # Initialize agents if needed
        if not self._agents or self._config != config:
            self.initialize_agents(config, seed=config.seed)
        
        rng = np.random.default_rng(config.seed)
        
        # Track trajectories
        wealth_history = []
        
        # Initial wealth distribution
        wealth_arr = np.array([a.attributes.wealth for a in self._agents])
        wealth_history.append(wealth_arr.copy())
        
        # Run simulation
        convergence_time = config.time_horizon
        steady_state_achieved = False
        prev_gini = self._compute_gini(wealth_arr)
        
        for t in range(config.time_horizon):
            # Execute interactions
            self._step(config, rng)
            
            # Record wealth
            wealth_arr = np.array([a.attributes.wealth for a in self._agents])
            wealth_history.append(wealth_arr.copy())
            
            # Check convergence
            current_gini = self._compute_gini(wealth_arr)
            if abs(current_gini - prev_gini) < config.equilibrium_tolerance:
                convergence_time = t + 1
                steady_state_achieved = True
                break
            prev_gini = current_gini
        
        # Compute final statistics
        final_wealth = np.array([a.attributes.wealth for a in self._agents])
        
        return ABMResults(
            wealth_distribution=final_wealth,
            gini_coefficient=self._compute_gini(final_wealth),
            mean_wealth=float(final_wealth.mean()),
            median_wealth=float(np.median(final_wealth)),
            top_1_share=self._compute_top_share(final_wealth, 0.01),
            network_clustering=self._compute_clustering(),
            convergence_time=convergence_time,
            steady_state_achieved=steady_state_achieved,
            aggregate_output=float(final_wealth.sum()),
            agent_trajectories=np.array(wealth_history),
        )
    
    def _step(self, config: ABMConfig, rng: np.random.Generator) -> None:
        """Execute one simulation step."""
        n_interactions = int(len(self._agents) * config.interaction_rate)
        
        for _ in range(n_interactions):
            if len(self._agents) < 2:
                break
            
            # Select interacting pair
            if config.interaction and config.interaction.mode == InteractionMode.NETWORK:
                # Network-based selection
                i = rng.integers(0, len(self._agents))
                neighbors = config.interaction.get_neighbors(i)
                if neighbors:
                    j = rng.choice(neighbors)
                else:
                    j = rng.integers(0, len(self._agents))
                    while j == i:
                        j = rng.integers(0, len(self._agents))
            else:
                # Random matching
                i, j = rng.choice(len(self._agents), size=2, replace=False)
            
            self._interact(self._agents[i], self._agents[j], rng)
        
        # Agent entry/exit
        for pop in config.populations:
            if pop.mortality_rate > 0:
                for agent in self._agents:
                    if agent.agent_type == pop.agent_type:
                        if rng.random() < pop.mortality_rate:
                            agent.active = False
    
    def _interact(
        self,
        agent_a: Agent,
        agent_b: Agent,
        rng: np.random.Generator,
    ) -> None:
        """Execute interaction between two agents."""
        if not (agent_a.active and agent_b.active):
            return
        
        # Proportional exchange based on productivity
        total_wealth = agent_a.attributes.wealth + agent_b.attributes.wealth
        if total_wealth <= 0:
            return
        
        # Share goes to more productive agent
        prod_a = agent_a.attributes.productivity
        prod_b = agent_b.attributes.productivity
        share_a = prod_a / (prod_a + prod_b) if (prod_a + prod_b) > 0 else 0.5
        
        # Small reallocation
        exchange_rate = 0.01
        target_a = total_wealth * share_a
        target_b = total_wealth * (1 - share_a)
        
        agent_a.attributes.wealth += exchange_rate * (target_a - agent_a.attributes.wealth)
        agent_b.attributes.wealth += exchange_rate * (target_b - agent_b.attributes.wealth)
        
        # Productivity learning
        avg_prod = (prod_a + prod_b) / 2
        learning_rate = 0.01
        agent_a.attributes.productivity = (1 - learning_rate) * prod_a + learning_rate * avg_prod
        agent_b.attributes.productivity = (1 - learning_rate) * prod_b + learning_rate * avg_prod
    
    @staticmethod
    def _compute_gini(values: np.ndarray) -> float:
        """Compute Gini coefficient."""
        if len(values) == 0 or values.sum() == 0:
            return 0.0
        
        sorted_vals = np.sort(values)
        n = len(sorted_vals)
        cumsum = np.cumsum(sorted_vals)
        return (2 * np.sum((np.arange(1, n + 1) * sorted_vals)) - (n + 1) * cumsum[-1]) / (n * cumsum[-1])
    
    @staticmethod
    def _compute_top_share(values: np.ndarray, percentile: float) -> float:
        """Compute share of total held by top percentile."""
        if len(values) == 0 or values.sum() == 0:
            return 0.0
        
        sorted_vals = np.sort(values)[::-1]
        n_top = max(1, int(len(sorted_vals) * percentile))
        return float(sorted_vals[:n_top].sum() / sorted_vals.sum())
    
    def _compute_clustering(self) -> float:
        """Compute network clustering coefficient."""
        if self._network is None or self._network.adjacency is None:
            return 0.0
        
        adj = self._network.adjacency
        n = adj.shape[0]
        
        total_triangles = 0
        total_triplets = 0
        
        for i in range(n):
            neighbors = np.where(adj[i] > 0)[0]
            k = len(neighbors)
            if k < 2:
                continue
            
            # Count triangles
            for ni in range(len(neighbors)):
                for nj in range(ni + 1, len(neighbors)):
                    if adj[neighbors[ni], neighbors[nj]] > 0:
                        total_triangles += 1
            total_triplets += k * (k - 1) / 2
        
        if total_triplets == 0:
            return 0.0
        
        return total_triangles / total_triplets
    
    @requires_tier(Tier.ENTERPRISE)
    def monte_carlo_analysis(
        self,
        config: ABMConfig,
        n_runs: Optional[int] = None,
        parallel: bool = False,
    ) -> dict[str, Any]:
        """
        Run Monte Carlo analysis over multiple simulation runs.
        
        Args:
            config: Base configuration
            n_runs: Number of runs (defaults to config.monte_carlo_runs)
            parallel: Whether to parallelize (future feature)
            
        Returns:
            Dictionary with distributional statistics
        """
        n_runs = n_runs or config.monte_carlo_runs
        
        gini_dist = []
        mean_wealth_dist = []
        top_1_dist = []
        convergence_dist = []
        
        for run in range(n_runs):
            run_config = ABMConfig(
                populations=config.populations,
                interaction=config.interaction,
                time_horizon=config.time_horizon,
                interaction_rate=config.interaction_rate,
                market_mechanism=config.market_mechanism,
                equilibrium_tolerance=config.equilibrium_tolerance,
                seed=run,  # Different seed each run
            )
            
            results = self.run_simulation(run_config)
            gini_dist.append(results.gini_coefficient)
            mean_wealth_dist.append(results.mean_wealth)
            top_1_dist.append(results.top_1_share)
            convergence_dist.append(results.convergence_time)
        
        return {
            "n_runs": n_runs,
            "gini": {
                "mean": float(np.mean(gini_dist)),
                "std": float(np.std(gini_dist)),
                "ci_95": [
                    float(np.percentile(gini_dist, 2.5)),
                    float(np.percentile(gini_dist, 97.5)),
                ],
            },
            "mean_wealth": {
                "mean": float(np.mean(mean_wealth_dist)),
                "std": float(np.std(mean_wealth_dist)),
            },
            "top_1_share": {
                "mean": float(np.mean(top_1_dist)),
                "std": float(np.std(top_1_dist)),
            },
            "convergence_time": {
                "mean": float(np.mean(convergence_dist)),
                "std": float(np.std(convergence_dist)),
            },
        }
    
    @requires_tier(Tier.ENTERPRISE)
    def sensitivity_analysis(
        self,
        config: ABMConfig,
        parameter_ranges: dict[str, tuple[float, float]],
        n_samples: int = 100,
    ) -> dict[str, Any]:
        """
        Perform sensitivity analysis on model parameters.
        
        Uses Latin Hypercube Sampling to explore parameter space.
        
        Args:
            config: Base configuration
            parameter_ranges: Dict mapping parameter names to (min, max)
            n_samples: Number of parameter samples
            
        Returns:
            Sensitivity indices and partial dependence
        """
        from scipy.stats import qmc
        
        # Generate LHS samples
        n_params = len(parameter_ranges)
        sampler = qmc.LatinHypercube(d=n_params)
        samples = sampler.random(n=n_samples)
        
        param_names = list(parameter_ranges.keys())
        
        # Scale samples to parameter ranges
        scaled_samples = np.zeros_like(samples)
        for i, name in enumerate(param_names):
            low, high = parameter_ranges[name]
            scaled_samples[:, i] = samples[:, i] * (high - low) + low
        
        # Run simulations
        outputs = []
        for sample in scaled_samples:
            # Modify config based on sample
            modified_config = ABMConfig(
                populations=config.populations,
                interaction=config.interaction,
                time_horizon=config.time_horizon,
                interaction_rate=sample[param_names.index("interaction_rate")] if "interaction_rate" in param_names else config.interaction_rate,
                seed=config.seed,
            )
            
            results = self.run_simulation(modified_config)
            outputs.append(results.gini_coefficient)
        
        outputs = np.array(outputs)
        
        # Compute first-order sensitivity (correlation-based)
        sensitivities = {}
        for i, name in enumerate(param_names):
            corr = np.corrcoef(scaled_samples[:, i], outputs)[0, 1]
            sensitivities[name] = {
                "correlation": float(corr),
                "importance": float(corr ** 2),
            }
        
        return {
            "sensitivities": sensitivities,
            "output_variance": float(outputs.var()),
            "n_samples": n_samples,
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Abstract Method Implementations
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _compute_initial_state(self, data: DataBundle) -> CohortStateVector:
        """
        Compute initial cohort state from input data.
        
        For ABM, maps agent populations to cohort state dimensions.
        """
        # Initialize agents if not already done
        if not self._agents:
            default_config = ABMConfig(
                populations=[
                    AgentPopulation(
                        name="default",
                        agent_type=AgentType.HOUSEHOLD,
                        count=100,
                        initial_distribution={
                            "wealth": ("lognormal", {"mean": 10.0, "sigma": 1.0}),
                        },
                    ),
                ],
            )
            self.initialize_agents(default_config)
        
        n_cohorts = min(len(self._agents), 100)
        n_sectors = 5
        
        # Map agent wealth to credit access
        wealth_arr = np.array([a.attributes.wealth for a in self._agents[:n_cohorts]])
        max_wealth = max(wealth_arr.max(), 1e-6)
        credit_access = np.clip(wealth_arr / max_wealth, 0.1, 0.9)
        
        # Productivity maps to employment probability
        prod_arr = np.array([a.attributes.productivity for a in self._agents[:n_cohorts]])
        employment_prob = np.clip(0.5 + 0.3 * prod_arr, 0.1, 0.95)
        
        return CohortStateVector(
            employment_prob=employment_prob,
            health_burden_score=np.full(n_cohorts, 0.15),
            credit_access_score=credit_access,
            housing_cost_ratio=np.full(n_cohorts, 0.3),
            sector_output=np.full((n_cohorts, n_sectors), 100.0),
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        step: int,
    ) -> CohortStateVector:
        """
        Apply ABM transition dynamics for one step.
        
        Executes agent interactions and maps to cohort state.
        """
        # Execute interactions
        if self._agents and self._config:
            rng = np.random.default_rng(step)
            self._step(self._config, rng)
        
        # Map agent states back to cohort
        if self._agents:
            n_cohorts = state.n_cohorts
            wealth_arr = np.array([a.attributes.wealth for a in self._agents[:n_cohorts]])
            max_wealth = max(wealth_arr.max(), 1e-6)
            new_credit = np.clip(wealth_arr / max_wealth, 0.1, 0.9)
        else:
            new_credit = state.credit_access_score * 1.001
        
        # Small updates
        new_employment = np.clip(state.employment_prob * 1.002, 0.1, 0.95)
        new_sector = state.sector_output * 1.01
        
        return CohortStateVector(
            employment_prob=new_employment,
            health_burden_score=state.health_burden_score * 0.99,
            credit_access_score=new_credit,
            housing_cost_ratio=state.housing_cost_ratio,
            sector_output=new_sector,
        )
    
    def _compute_metrics(
        self,
        state: CohortStateVector,
    ) -> dict[str, Any]:
        """Compute ABM metrics from final state."""
        if self._agents:
            wealth_arr = np.array([a.attributes.wealth for a in self._agents])
            gini = self._compute_gini(wealth_arr)
            mean_wealth = float(wealth_arr.mean())
        else:
            gini = 0.0
            mean_wealth = 0.0
        
        return {
            "gini_coefficient": gini,
            "mean_wealth": mean_wealth,
            "employment_rate": float(state.employment_prob.mean()),
            "total_output": float(state.sector_output.sum()),
            "n_agents": len(self._agents),
        }
    
    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Return ABM dashboard specification.
        
        Agent-Based Modeling framework for heterogeneous agent
        simulations with network interactions.
        """
        return FrameworkDashboardSpec(
            slug="abm",
            name="Agent-Based Model",
            description=(
                "Generic agent-based modeling platform for heterogeneous "
                "agent simulations with network interactions and market mechanisms."
            ),
            layer="meta",
            parameters_schema={
                "type": "object",
                "properties": {
                    "n_agents": {
                        "type": "integer",
                        "title": "Number of Agents",
                        "description": "Total number of agents in simulation",
                        "minimum": 10,
                        "maximum": 100000,
                        "default": 1000,
                        "x-ui-widget": "slider",
                        "x-ui-step": 100,
                        "x-ui-group": "agent_config",
                        "x-ui-order": 1,
                    },
                    "agent_types": {
                        "type": "array",
                        "title": "Agent Types",
                        "description": "Types of agents to include in simulation",
                        "items": {
                            "type": "string",
                            "enum": ["household", "firm", "bank", "government", "worker"],
                        },
                        "default": ["household", "firm"],
                        "x-ui-widget": "multi-select",
                        "x-ui-group": "agent_config",
                        "x-ui-order": 2,
                    },
                    "interaction_topology": {
                        "type": "string",
                        "title": "Interaction Topology",
                        "description": "Network structure for agent interactions",
                        "enum": ["random", "scale_free", "small_world", "lattice", "complete"],
                        "default": "scale_free",
                        "x-ui-widget": "select",
                        "x-ui-group": "network_config",
                        "x-ui-order": 1,
                    },
                    "simulation_steps": {
                        "type": "integer",
                        "title": "Simulation Steps",
                        "description": "Number of time steps to simulate",
                        "minimum": 10,
                        "maximum": 1000,
                        "default": 100,
                        "x-ui-widget": "slider",
                        "x-ui-step": 10,
                        "x-ui-group": "simulation",
                        "x-ui-order": 1,
                    },
                },
                "required": ["n_agents"],
            },
            default_parameters={
                "n_agents": 1000,
                "agent_types": ["household", "firm"],
                "interaction_topology": "scale_free",
                "simulation_steps": 100,
            },
            parameter_groups=[
                ParameterGroupSpec(
                    key="agent_config",
                    title="Agent Configuration",
                    description="Define agent populations and types",
                    collapsed_by_default=False,
                ),
                ParameterGroupSpec(
                    key="network_config",
                    title="Network Configuration",
                    description="Configure interaction network topology",
                    collapsed_by_default=True,
                ),
                ParameterGroupSpec(
                    key="simulation",
                    title="Simulation Settings",
                    description="Simulation runtime parameters",
                    collapsed_by_default=True,
                ),
            ],
            output_views=[
                OutputViewSpec(
                    key="agent_distribution",
                    title="Agent Distribution",
                    view_type=ViewType.HISTOGRAM,
                    description="Distribution of agent attributes (wealth, productivity)",
                result_class=ResultClass.DOMAIN_DECOMPOSITION,
                output_key="agent_distribution_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="network_structure",
                    title="Network Structure",
                    view_type=ViewType.NETWORK,
                    description="Agent interaction network visualization",
                    result_class=ResultClass.STRUCTURAL_SIMILARITY,
                    output_key="network_structure_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="emergent_patterns",
                    title="Emergent Patterns",
                    view_type=ViewType.LINE_CHART,
                    description="Time series of emergent aggregate behavior",
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="emergent_patterns_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="aggregate_metrics",
                    title="Aggregate Metrics",
                    view_type=ViewType.METRIC_GRID,
                    description="Key summary statistics (Gini, mean wealth, etc.)",
                result_class=ResultClass.SCALAR_INDEX,
                output_key="aggregate_metrics_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
            ],
            min_tier=Tier.ENTERPRISE,
        )
    
    def create_transition(self) -> ABMTransition:
        """Create transition function for CBSS integration."""
        return ABMTransition(config=self._config, agents=self._agents)
    
    def execute(
        self,
        bundle: DataBundle,
        config: Optional[Any] = None,
    ) -> FrameworkExecutionResult:
        """
        Execute framework on data bundle.
        
        Args:
            bundle: Input data bundle
            config: Optional ABMConfig
            
        Returns:
            FrameworkExecutionResult
        """
        validation_errors = self.validate_bundle(bundle)
        if validation_errors:
            raise DataBundleValidationError(
                "ABMFramework",
                validation_errors,
            )
        
        # Default configuration if not provided
        if config is None:
            config = ABMConfig(
                populations=[
                    AgentPopulation(
                        name="default_households",
                        agent_type=AgentType.HOUSEHOLD,
                        count=500,
                        initial_distribution={
                            "wealth": ("lognormal", {"mean": 10.0, "sigma": 1.0}),
                            "productivity": ("normal", {"loc": 1.0, "scale": 0.2}),
                        },
                    ),
                ],
                time_horizon=50,
            )
        
        # Run simulation
        results = self.run_simulation(config)
        
        return FrameworkExecutionResult(
            framework_name="ABMFramework",
            success=True,
            outputs={
                "results": results.to_dict(),
                "wealth_distribution": results.wealth_distribution.tolist(),
            },
            metrics={
                "gini_coefficient": results.gini_coefficient,
                "mean_wealth": results.mean_wealth,
                "convergence_time": results.convergence_time,
            },
        )
