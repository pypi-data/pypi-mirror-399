# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Base Meta-Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Abstract base class for all KRL meta-frameworks.

This module defines the BaseMetaFramework ABC, which provides the standard
interface for all socioeconomic frameworks in the platform. It follows
patterns established by krl-causal-policy-toolkit's BasePolicyEstimator
while adding support for CBSS simulation, DAG composition, and tier gating.

All 25+ frameworks across the 6 vertical layers inherit from this base class,
ensuring consistent APIs, audit trails, and orchestration compatibility.
"""

from __future__ import annotations

import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, ClassVar
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

import numpy as np

from krl_frameworks.core.config import FrameworkConfig
from krl_frameworks.core.data_bundle import DataBundle, DataDomain
from krl_frameworks.core.exceptions import (
    ConfigurationError,
    DataBundleValidationError,
    ExecutionError,
    SimulationError,
)
from krl_frameworks.core.state import CohortStateVector, StateTrajectory
from krl_frameworks.core.tier import Tier

if TYPE_CHECKING:
    from numpy.typing import NDArray
    
    from krl_frameworks.core.dashboard_spec import FrameworkDashboardSpec
    from krl_frameworks.core.output_envelope import FrameworkOutputEnvelope
    from krl_frameworks.core.bindings import BindingRegistry
    from krl_frameworks.governance.binding_resolver import ResolutionResult

# Integration Spine imports (lazy to avoid circular imports)
from krl_frameworks.core.capabilities import CapabilityDeclaration
from krl_frameworks.core.execution_context import (
    ExecutionContext,
    ExecutionMode,
    get_execution_context,
    MissingCapabilityError,
)


# ════════════════════════════════════════════════════════════════════════════════
# Vertical Layer Enum
# ════════════════════════════════════════════════════════════════════════════════


class VerticalLayer(int, Enum):
    """
    The 6 vertical layers in the KRL Frameworks architecture.
    
    Each framework belongs to exactly one layer. The numeric values
    indicate the typical data flow direction (lower → higher),
    though bi-directional flows are supported in peer hub compositions.
    """
    
    SOCIOECONOMIC_ACADEMIC = 1
    GOVERNMENT_POLICY = 2
    EXPERIMENTAL_RESEARCH = 3
    FINANCIAL_ECONOMIC = 4
    ARTS_MEDIA_ENTERTAINMENT = 5
    META_PEER_FRAMEWORKS = 6
    
    @property
    def display_name(self) -> str:
        """Human-readable layer name."""
        names = {
            1: "Socioeconomic/Academic",
            2: "Government/Policy",
            3: "Experimental/Research",
            4: "Financial/Economic",
            5: "Arts/Media/Entertainment",
            6: "Meta/Peer Frameworks",
        }
        return names.get(self.value, self.name)
    
    @property
    def abbreviation(self) -> str:
        """Short layer abbreviation."""
        abbrevs = {
            1: "L1-SE",
            2: "L2-GP",
            3: "L3-ER",
            4: "L4-FE",
            5: "L5-AME",
            6: "L6-META",
        }
        return abbrevs.get(self.value, f"L{self.value}")


# ════════════════════════════════════════════════════════════════════════════════
# Framework Metadata
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class FrameworkMetadata:
    """
    Metadata describing a framework's identity and capabilities.
    
    This metadata is used by the FrameworkRegistry for discovery
    and by the DAG composer for compatibility checking.
    
    Attributes:
        slug: Unique identifier (e.g., "mpi", "remsom", "iam-dice").
        name: Human-readable name.
        version: Framework version (semver).
        layer: Which vertical layer this framework belongs to.
        tier: Minimum tier required for access.
        description: Brief description of capabilities.
        required_domains: Data domains required for execution.
        output_domains: Data domains produced as output.
        constituent_models: List of underlying models/methods.
        tags: Searchable tags.
        author: Framework author/maintainer.
        license: License identifier.
    """
    
    slug: str
    name: str
    version: str = "1.0.0"
    layer: VerticalLayer = VerticalLayer.SOCIOECONOMIC_ACADEMIC
    tier: Tier = Tier.COMMUNITY
    description: str = ""
    required_domains: list[str] = field(default_factory=list)
    output_domains: list[str] = field(default_factory=list)
    constituent_models: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    author: str = "Khipu Research Labs"
    license: str = "Apache-2.0"
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "slug": self.slug,
            "name": self.name,
            "version": self.version,
            "layer": self.layer.value,
            "layer_name": self.layer.display_name,
            "tier": self.tier.name,
            "description": self.description,
            "required_domains": self.required_domains,
            "output_domains": self.output_domains,
            "constituent_models": self.constituent_models,
            "tags": self.tags,
            "author": self.author,
            "license": self.license,
        }


# ════════════════════════════════════════════════════════════════════════════════
# Execution Result
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class FrameworkExecutionResult:
    """
    Result of a framework execution.
    
    Contains the final state, trajectory, metrics, and audit information
    from a framework simulation or projection.
    
    Attributes:
        execution_id: Unique execution identifier.
        framework_slug: Framework that produced this result.
        state: Final CohortStateVector.
        trajectory: Full simulation trajectory (optional).
        metrics: Computed output metrics.
        envelope: Self-describing output envelope (new architecture).
        started_at: Execution start time.
        completed_at: Execution completion time.
        steps_executed: Number of simulation steps.
        converged: Whether simulation converged.
        config: Configuration used for execution.
        data_hash: Hash of input data for reproducibility.
        metadata: Additional result metadata.
    """
    
    execution_id: str
    framework_slug: str
    state: CohortStateVector
    trajectory: StateTrajectory | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    envelope: "FrameworkOutputEnvelope | None" = None
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    steps_executed: int = 0
    converged: bool = False
    config: FrameworkConfig | None = None
    data_hash: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_ms(self) -> float | None:
        """Execution duration in milliseconds."""
        if self.completed_at is None:
            return None
        delta = self.completed_at - self.started_at
        return delta.total_seconds() * 1000
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization/API response."""
        result = {
            "execution_id": self.execution_id,
            "framework_slug": self.framework_slug,
            "state": self.state.to_dict(),
            "metrics": self.metrics,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms,
            "steps_executed": self.steps_executed,
            "converged": self.converged,
            "data_hash": self.data_hash,
            "metadata": self.metadata,
        }
        # Include envelope if present (new architecture)
        if self.envelope is not None:
            result["envelope"] = self.envelope.to_dict()
        return result


# ════════════════════════════════════════════════════════════════════════════════
# Base Meta-Framework ABC
# ════════════════════════════════════════════════════════════════════════════════


class BaseMetaFramework(ABC):
    """
    Abstract base class for all KRL meta-frameworks.
    
    This class defines the standard interface that all 25+ frameworks
    must implement. It provides:
    
    - Consistent lifecycle methods: fit(), simulate(), project()
    - Automatic data validation against required_domains
    - Audit logging for all executions
    - Tier-based access control hooks
    - State management and trajectory tracking
    
    Subclasses must implement:
    - _compute_initial_state(): Create initial CohortStateVector from data
    - _transition(): Apply one simulation step to transform state
    - _compute_metrics(): Calculate output metrics from final state
    
    Subclasses may override:
    - _validate_data(): Custom data validation logic
    - _pre_simulation_hook(): Custom setup before simulation
    - _post_simulation_hook(): Custom cleanup after simulation
    
    Example:
        >>> class MPIFramework(BaseMetaFramework):
        ...     METADATA = FrameworkMetadata(
        ...         slug="mpi",
        ...         name="Multidimensional Poverty Index",
        ...         layer=VerticalLayer.SOCIOECONOMIC_ACADEMIC,
        ...         tier=Tier.COMMUNITY,
        ...         required_domains=["health", "education", "income"],
        ...     )
        ...     
        ...     def _compute_initial_state(self, data: DataBundle) -> CohortStateVector:
        ...         # Compute deprivation vectors from domain data
        ...         ...
        ...     
        ...     def _transition(self, state: CohortStateVector, step: int) -> CohortStateVector:
        ...         # MPI is typically static, so return unchanged
        ...         return state
        ...     
        ...     def _compute_metrics(self, state: CohortStateVector) -> dict[str, Any]:
        ...         return {
        ...             "headcount_ratio": state.deprivation_headcount(),
        ...             "intensity": np.mean(state.deprivation_vector),
        ...             "mpi": state.deprivation_headcount() * np.mean(state.deprivation_vector),
        ...         }
    """
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Class Attributes (override in subclasses)
    # ═══════════════════════════════════════════════════════════════════════════
    
    METADATA: ClassVar[FrameworkMetadata]
    
    # Capability declaration (override in subclasses for integration spine)
    # If not overridden, capabilities are inferred from METADATA.required_domains
    CAPABILITIES: ClassVar[CapabilityDeclaration | None] = None
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Dashboard Specification Hook
    # ═══════════════════════════════════════════════════════════════════════════
    
    @classmethod
    def dashboard_spec(cls) -> "FrameworkDashboardSpec | None":
        """
        Return the dashboard specification for this framework.
        
        Override in subclasses to make the framework renderable in the
        generic dashboard UI. If this returns None (default), the framework
        will not appear in the dashboard's framework catalog.
        
        The returned specification defines:
        - Parameters schema (JSON Schema) for UI generation
        - Default parameter values
        - Output view declarations (chart types, tables, etc.)
        
        Returns:
            FrameworkDashboardSpec if dashboard-enabled, None otherwise.
        
        Example:
            @classmethod
            def dashboard_spec(cls) -> FrameworkDashboardSpec:
                return FrameworkDashboardSpec(
                    slug=cls.METADATA.slug,
                    name=cls.METADATA.name,
                    ...
                )
        """
        return None
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Instance Attributes
    # ═══════════════════════════════════════════════════════════════════════════
    
    def __init__(
        self,
        config: FrameworkConfig | None = None,
        *,
        logger: logging.Logger | None = None,
        execution_context: ExecutionContext | None = None,
    ) -> None:
        """
        Initialize the framework.
        
        Args:
            config: Framework configuration. Uses defaults if not provided.
            logger: Custom logger. Creates one if not provided.
            execution_context: Execution context for runtime validation.
                If not provided, uses the current context from context var.
        """
        self.config = config or FrameworkConfig()
        self.logger = logger or logging.getLogger(
            f"krl_frameworks.{self.__class__.__name__}"
        )
        
        # Execution context (from param, context var, or default)
        self._execution_context = (
            execution_context
            or get_execution_context()
            or ExecutionContext.from_env()
        )
        
        # State tracking
        self._data: DataBundle | None = None
        self._state: CohortStateVector | None = None
        self._trajectory: StateTrajectory | None = None
        self._fitted: bool = False
        self._execution_id: str = ""
        
        # Validate capabilities on initialization (fail-fast)
        self._validate_capabilities_on_init()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Properties
    # ═══════════════════════════════════════════════════════════════════════════
    
    @property
    def slug(self) -> str:
        """Framework unique identifier."""
        return self.METADATA.slug
    
    @property
    def name(self) -> str:
        """Framework display name."""
        return self.METADATA.name
    
    @property
    def layer(self) -> VerticalLayer:
        """Vertical layer this framework belongs to."""
        return self.METADATA.layer
    
    @property
    def tier(self) -> Tier:
        """Minimum tier required for access."""
        return self.METADATA.tier
    
    @property
    def required_domains(self) -> list[str]:
        """Data domains required for execution."""
        return self.METADATA.required_domains
    
    @property
    def is_fitted(self) -> bool:
        """Whether fit() has been called successfully."""
        return self._fitted
    
    @property
    def state(self) -> CohortStateVector | None:
        """Current state vector (None before fit)."""
        return self._state
    
    @property
    def trajectory(self) -> StateTrajectory | None:
        """Simulation trajectory (None before simulate)."""
        return self._trajectory
    
    @property
    def capabilities(self) -> CapabilityDeclaration:
        """
        Get the capability declaration for this framework.
        
        If CAPABILITIES is not explicitly defined, infers from METADATA.required_domains.
        """
        if self.CAPABILITIES is not None:
            return self.CAPABILITIES
        # Infer from METADATA for backward compatibility
        return CapabilityDeclaration.from_domains(self.required_domains)
    
    @property
    def execution_mode(self) -> ExecutionMode:
        """Current execution mode."""
        return self._execution_context.mode
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Capability Validation (Integration Spine)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _validate_capabilities_on_init(self) -> None:
        """
        Validate that required toolkit dependencies are available.
        
        This is called during __init__ to fail fast if required toolkits
        are not installed. Connector validation is deferred to fit().
        """
        caps = self.capabilities
        
        # Only validate toolkit imports on init (connectors need data)
        for toolkit in caps.required_toolkits:
            try:
                if toolkit.toolkit == "causal":
                    from krl_frameworks.adapters.causal import check_causal_toolkit_installed
                    if not check_causal_toolkit_installed():
                        raise MissingCapabilityError(
                            capability_type="toolkit",
                            capability_name=toolkit.full_name if hasattr(toolkit, 'full_name') else f"{toolkit.toolkit}.{toolkit.method}",
                            message=f"Required toolkit not installed. Install with: pip install {toolkit.package}",
                        )
            except ImportError as e:
                if self._execution_context.mode.requires_strict_validation:
                    raise MissingCapabilityError(
                        capability_type="toolkit",
                        capability_name=f"{toolkit.toolkit}.{toolkit.method}",
                        message=str(e),
                    ) from e
                else:
                    self._execution_context.log_warning(f"Toolkit import failed: {e}")
    
    def _validate_capabilities_on_fit(self, data: DataBundle) -> None:
        """
        Validate that all required connectors have provided data.
        
        Called during fit() to ensure data bundle satisfies requirements.
        In LIVE mode, missing data causes hard failure.
        In TEST mode, missing data causes warning but allows synthetic fallback.
        """
        caps = self.capabilities
        
        # Create bindings from the data bundle
        from krl_frameworks.core.bindings import BindingRegistry
        bindings = BindingRegistry.from_data_bundle(data)
        
        # Check required connectors have data
        for connector in caps.required_connectors:
            domain = connector.domain
            has_data = data.has_domain(domain) if hasattr(data, 'has_domain') else domain in (data.domains or [])
            
            if not has_data:
                if self._execution_context.mode.requires_strict_validation:
                    raise MissingCapabilityError(
                        capability_type="connector",
                        capability_name=domain,
                        message=f"Required data domain '{domain}' not in DataBundle. "
                                f"LIVE mode requires real data from connectors.",
                    )
                else:
                    self._execution_context.log_warning(
                        f"Missing data for domain '{domain}', synthetic data may be used"
                    )
    
    def _auto_resolve_bindings(
        self,
        user_tier: str | None = None,
        connector_config: dict[str, dict[str, Any]] | None = None,
    ) -> "ResolutionResult":
        """
        Automatically resolve capability declarations to bindings.
        
        Uses the BindingResolver from the governance layer to map
        CAPABILITIES → BindingRegistry using registered factories.
        
        This method is called during fit() if auto_resolve=True.
        In LIVE mode, all REQUIRED capabilities must resolve.
        In TEST mode, resolution failures are logged as warnings.
        
        Args:
            user_tier: User's subscription tier (default: from context).
            connector_config: Per-connector configuration dictionaries.
        
        Returns:
            ResolutionResult with resolved bindings and any failures.
        
        Raises:
            BindingResolutionError: In LIVE mode if REQUIRED fails.
        """
        from krl_frameworks.governance.binding_resolver import (
            BindingResolver,
            get_binding_resolver,
        )
        from krl_frameworks.governance.audit import get_audit_logger
        
        resolver = get_binding_resolver()
        audit = get_audit_logger()
        
        # Determine user tier
        tier = user_tier or getattr(self._execution_context, 'user_tier', 'community')
        
        # Log resolution start
        audit.log_resolution_start(
            framework_name=self.__class__.__name__,
            user_tier=tier,
            execution_mode=self._execution_context.mode.value,
            capabilities_count=(
                len(self.capabilities.connectors) +
                len(self.capabilities.toolkits) +
                len(self.capabilities.models)
            ),
        )
        
        try:
            result = resolver.resolve(
                capabilities=self.capabilities,
                user_tier=tier,
                mode=self._execution_context.mode,
                existing_bindings=self._execution_context.bindings,
                connector_config=connector_config,
            )
            
            # Log success
            audit.log_resolution_success(
                framework_name=self.__class__.__name__,
                resolved=result.resolved,
                user_tier=tier,
                execution_mode=self._execution_context.mode.value,
                warnings=result.warnings,
            )
            
            return result
            
        except Exception as e:
            # Log failure
            from krl_frameworks.governance.binding_resolver import BindingResolutionError
            if isinstance(e, BindingResolutionError):
                audit.log_resolution_failure(
                    framework_name=self.__class__.__name__,
                    failures=[
                        {"name": f.requirement_name, "reason": f.reason}
                        for f in e.failures
                    ],
                    user_tier=tier,
                    execution_mode=self._execution_context.mode.value,
                )
            raise
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Lifecycle Methods
    # ═══════════════════════════════════════════════════════════════════════════
    
    def fit(
        self,
        data: DataBundle,
        *,
        validate: bool = True,
        auto_resolve: bool = False,
        user_tier: str | None = None,
        connector_config: dict[str, dict[str, Any]] | None = None,
    ) -> Self:
        """
        Fit the framework to input data.
        
        This method validates the input data, computes the initial
        cohort state vector, and prepares the framework for simulation.
        
        Args:
            data: DataBundle containing required domain data.
            validate: Whether to validate data against requirements.
            auto_resolve: If True, use governance layer to auto-resolve
                capability bindings before execution.
            user_tier: User's subscription tier for binding resolution.
            connector_config: Per-connector configuration for resolution.
        
        Returns:
            Self for method chaining.
        
        Raises:
            DataBundleValidationError: If required domains are missing.
            ConfigurationError: If configuration is invalid.
            BindingResolutionError: If auto_resolve and LIVE mode with missing REQUIRED.
        """
        self._execution_id = str(uuid.uuid4())
        self.logger.info(
            "Fitting framework %s (execution_id=%s, mode=%s)",
            self.slug,
            self._execution_id[:8],
            self._execution_context.mode.value,
        )
        
        # Auto-resolve bindings if requested (Governance Layer)
        if auto_resolve:
            resolution_result = self._auto_resolve_bindings(
                user_tier=user_tier,
                connector_config=connector_config,
            )
            self.logger.info(
                "Auto-resolved %d bindings for %s",
                len(resolution_result.resolved),
                self.slug,
            )
        
        # Validate capabilities (Integration Spine - fail-fast)
        self._validate_capabilities_on_fit(data)
        
        # Validate data
        if validate:
            self._validate_data_bundle(data)
        
        # Store data reference
        self._data = data
        
        # Compute initial state
        try:
            self._state = self._compute_initial_state(data)
            self._state.execution_id = self._execution_id
        except Exception as e:
            raise ExecutionError(
                f"Failed to compute initial state: {e}",
                execution_id=self._execution_id,
                framework_slug=self.slug,
            ) from e
        
        # Initialize trajectory
        self._trajectory = StateTrajectory(
            framework_slug=self.slug,
            metadata={"execution_id": self._execution_id},
        )
        self._trajectory.append(self._state)
        
        self._fitted = True
        self.logger.info("Framework %s fitted successfully", self.slug)
        
        return self
    
    def simulate(
        self,
        steps: int | None = None,
        *,
        record_trajectory: bool = True,
    ) -> FrameworkExecutionResult:
        """
        Run CBSS simulation for specified steps.
        
        This method applies the framework's transition function
        iteratively to evolve the cohort state over time.
        
        Args:
            steps: Number of simulation steps. Uses config.max_steps if None.
            record_trajectory: Whether to record all intermediate states.
        
        Returns:
            FrameworkExecutionResult with final state and metrics.
        
        Raises:
            ExecutionError: If framework has not been fitted.
            SimulationError: If simulation fails.
        """
        if not self._fitted or self._state is None:
            raise ExecutionError(
                "Framework must be fitted before simulation",
                framework_slug=self.slug,
            )
        
        steps = steps or self.config.simulation.max_steps
        started_at = datetime.now(timezone.utc)
        
        self.logger.info(
            "Starting simulation for %s: %d steps",
            self.slug,
            steps,
        )
        
        # Pre-simulation hook
        self._pre_simulation_hook()
        
        # Run simulation
        current_state = self._state
        steps_executed = 0
        converged = False
        
        try:
            for step in range(steps):
                # Apply transition
                next_state = self._transition(current_state, step)
                next_state = next_state.increment_step()
                
                # Record trajectory
                if record_trajectory:
                    self._trajectory.append(next_state)
                
                # Check convergence (if not fixed steps)
                if self._check_convergence(current_state, next_state, step):
                    converged = True
                    current_state = next_state
                    steps_executed = step + 1
                    break
                
                current_state = next_state
                steps_executed = step + 1
        
        except Exception as e:
            raise SimulationError(
                f"Simulation failed at step {steps_executed}: {e}",
                current_state=current_state,
                execution_id=self._execution_id,
                step=steps_executed,
                framework_slug=self.slug,
            ) from e
        
        # Update final state
        self._state = current_state
        
        # Post-simulation hook
        self._post_simulation_hook()
        
        # Compute metrics
        metrics = self._compute_metrics(current_state)
        
        completed_at = datetime.now(timezone.utc)
        
        result = FrameworkExecutionResult(
            execution_id=self._execution_id,
            framework_slug=self.slug,
            state=current_state,
            trajectory=self._trajectory if record_trajectory else None,
            metrics=metrics,
            started_at=started_at,
            completed_at=completed_at,
            steps_executed=steps_executed,
            converged=converged,
            config=self.config,
            data_hash=self._data.content_hash() if self._data else "",
        )
        
        # Build and attach output envelope (post-simulation hook pattern)
        try:
            result.envelope = self.build_output_envelope(result)
        except Exception as e:
            self.logger.warning(
                "Failed to build output envelope: %s. Continuing without envelope.",
                e,
            )
        
        self.logger.info(
            "Simulation completed: %d steps, %.1fms, converged=%s",
            steps_executed,
            result.duration_ms or 0,
            converged,
        )
        
        return result
    
    def project(
        self,
        horizon: int,
        *,
        scenario: dict[str, Any] | None = None,
    ) -> FrameworkExecutionResult:
        """
        Project the framework forward with optional scenario modifications.
        
        This is a convenience method that combines fit (if needed)
        and simulate with policy scenario support.
        
        Args:
            horizon: Number of time periods to project.
            scenario: Optional policy scenario parameters.
        
        Returns:
            FrameworkExecutionResult with projection results.
        """
        if not self._fitted:
            raise ExecutionError(
                "Framework must be fitted before projection",
                framework_slug=self.slug,
            )
        
        # Apply scenario if provided
        if scenario:
            self._apply_scenario(scenario)
        
        return self.simulate(steps=horizon, record_trajectory=True)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Abstract Methods (must be implemented by subclasses)
    # ═══════════════════════════════════════════════════════════════════════════
    
    @abstractmethod
    def _compute_initial_state(self, data: DataBundle) -> CohortStateVector:
        """
        Compute the initial cohort state from input data.
        
        This method transforms raw domain data into the canonical
        CohortStateVector format. Subclasses must implement domain-specific
        logic for computing employment_prob, health_burden_score, etc.
        
        Args:
            data: Validated DataBundle with required domains.
        
        Returns:
            Initial CohortStateVector for simulation.
        """
        ...
    
    @abstractmethod
    def _transition(
        self,
        state: CohortStateVector,
        step: int,
    ) -> CohortStateVector:
        """
        Apply one simulation step to transform the state.
        
        This is the core CBSS transition function. It should be:
        - Deterministic (same inputs → same outputs)
        - Vectorized (operates on full cohort arrays)
        - Stateless (no side effects beyond the returned state)
        
        Args:
            state: Current CohortStateVector.
            step: Current simulation step (0-indexed).
        
        Returns:
            New CohortStateVector after transition.
        """
        ...
    
    @abstractmethod
    def _compute_metrics(
        self,
        state: CohortStateVector,
    ) -> dict[str, Any]:
        """
        Compute output metrics from the final state.
        
        Subclasses implement domain-specific metric calculations
        (e.g., MPI headcount ratio, HDI index, OES elasticity score).
        
        Args:
            state: Final CohortStateVector after simulation.
        
        Returns:
            Dictionary of named metrics.
        """
        ...
    
    def build_output_envelope(
        self,
        result: FrameworkExecutionResult,
        user_parameters: dict[str, Any] | None = None,
    ) -> "FrameworkOutputEnvelope":
        """
        Build a self-describing output envelope for this framework's results.
        
        The envelope declares canonical dimensions, provenance, and
        framework-unique outputs. The API layer MUST NOT invent structure -
        it passes the envelope through unchanged.
        
        Default implementation creates a minimal envelope using the metrics
        from the result. Subclasses SHOULD override to provide full
        dimension manifests and structured outputs.
        
        Args:
            result: FrameworkExecutionResult from simulation.
            user_parameters: Original user parameters (for provenance).
        
        Returns:
            FrameworkOutputEnvelope with self-describing outputs.
        """
        from krl_frameworks.core.output_envelope import (
            DimensionManifest,
            FrameworkOutputEnvelope,
            ProvenanceRecord,
        )
        
        return FrameworkOutputEnvelope(
            framework_slug=self.slug,
            framework_version=self.METADATA.version,
            dimensions=DimensionManifest(),
            provenance=ProvenanceRecord(
                user_parameters=user_parameters or {},
                data_hash=result.data_hash,
            ),
            outputs=result.metrics,
            metadata={
                "execution_id": result.execution_id,
                "steps_executed": result.steps_executed,
                "converged": result.converged,
                "duration_ms": result.duration_ms,
            },
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Overridable Hooks
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _validate_data_bundle(self, data: DataBundle) -> None:
        """
        Validate input data bundle.
        
        Default implementation checks that all required_domains
        are present. Subclasses can override for custom validation.
        
        Args:
            data: DataBundle to validate.
        
        Raises:
            DataBundleValidationError: If validation fails.
        """
        data.validate_requirements(self.required_domains)
    
    def _pre_simulation_hook(self) -> None:
        """
        Hook called before simulation starts.
        
        Override for custom setup logic (e.g., initializing caches,
        setting random seeds).
        """
        if self.config.simulation.random_seed is not None:
            np.random.seed(self.config.simulation.random_seed)
    
    def _post_simulation_hook(self) -> None:
        """
        Hook called after simulation completes.
        
        Override for custom cleanup logic (e.g., clearing caches,
        logging diagnostics).
        """
        pass
    
    def _apply_scenario(self, scenario: dict[str, Any]) -> None:
        """
        Apply a policy scenario to modify simulation parameters.
        
        Override to implement scenario-specific modifications
        (e.g., policy shocks, parameter changes).
        
        Args:
            scenario: Scenario parameters.
        """
        self.logger.debug("Applying scenario: %s", scenario)
    
    def _check_convergence(
        self,
        prev_state: CohortStateVector,
        curr_state: CohortStateVector,
        step: int,
    ) -> bool:
        """
        Check if simulation has converged.
        
        Default implementation uses config.convergence_method to determine:
        - FIXED_STEPS: Never converges early
        - TOLERANCE: Converges when max state change < tolerance
        - COMBINED: Requires min_steps + tolerance check
        
        Args:
            prev_state: Previous state.
            curr_state: Current state.
            step: Current step number.
        
        Returns:
            True if converged, False otherwise.
        """
        from krl_frameworks.core.config import ConvergenceMethod
        
        method = self.config.simulation.convergence_method
        
        if method == ConvergenceMethod.FIXED_STEPS:
            return False
        
        # Check minimum steps
        if method == ConvergenceMethod.COMBINED:
            if step < self.config.simulation.min_steps:
                return False
        
        # Compute max change across canonical fields
        max_change = 0.0
        for field_name in prev_state.canonical_fields[:5]:  # 1D fields
            prev_arr = getattr(prev_state, field_name)
            curr_arr = getattr(curr_state, field_name)
            change = float(np.max(np.abs(curr_arr - prev_arr)))
            max_change = max(max_change, change)
        
        return max_change < self.config.simulation.tolerance
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Utility Methods
    # ═══════════════════════════════════════════════════════════════════════════
    
    def reset(self) -> Self:
        """
        Reset framework to unfitted state.
        
        Clears all state, trajectory, and data references.
        
        Returns:
            Self for method chaining.
        """
        self._data = None
        self._state = None
        self._trajectory = None
        self._fitted = False
        self._execution_id = ""
        return self
    
    def get_metadata(self) -> FrameworkMetadata:
        """Get framework metadata."""
        return self.METADATA
    
    def to_dict(self) -> dict[str, Any]:
        """Convert framework state to dictionary."""
        return {
            "metadata": self.METADATA.to_dict(),
            "is_fitted": self._fitted,
            "execution_id": self._execution_id,
            "state": self._state.to_dict() if self._state else None,
            "trajectory_steps": self._trajectory.n_steps if self._trajectory else 0,
        }
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"slug={self.slug!r}, "
            f"layer={self.layer.abbreviation}, "
            f"tier={self.tier.name}, "
            f"fitted={self._fitted})"
        )


# ════════════════════════════════════════════════════════════════════════════════
# Exports
# ════════════════════════════════════════════════════════════════════════════════

__all__ = [
    "BaseMetaFramework",
    "VerticalLayer",
    "FrameworkMetadata",
    "FrameworkExecutionResult",
]
