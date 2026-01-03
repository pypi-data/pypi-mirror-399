# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Backend Integration
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Backend Integration Module.

Provides integration with krl-premium-backend:
- FrameworkExecutionService: Execute frameworks through backend API
- FrameworkRegistrationService: Register frameworks in backend registry
- TCUCalculator: Calculate TCU costs for framework execution
- BackendClient: HTTP client for backend communication

This module enables remote framework execution with:
- Tier-based access control
- Usage tracking and billing
- Distributed execution
- Result caching
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, Protocol
from uuid import UUID, uuid4

import numpy as np
import pandas as pd

from krl_frameworks.core import (
    BaseMetaFramework,
    CohortStateVector,
    DataBundle,
    DomainData,
    FrameworkConfig,
    FrameworkMetadata,
    Tier,
    VerticalLayer,
)


logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Enums and Constants
# ════════════════════════════════════════════════════════════════════════════════


class ExecutionStatus(Enum):
    """Framework execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OutputFormat(Enum):
    """Result output format."""
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"


# TCU multipliers by framework tier
TCU_MULTIPLIERS = {
    Tier.COMMUNITY: 0.0,
    Tier.PROFESSIONAL: 1.0,
    Tier.TEAM: 2.0,
    Tier.ENTERPRISE: 5.0,
}

# Base TCU costs by layer
LAYER_BASE_TCU = {
    VerticalLayer.SOCIOECONOMIC_ACADEMIC: 10,
    VerticalLayer.GOVERNMENT_POLICY: 15,
    VerticalLayer.EXPERIMENTAL_RESEARCH: 20,
    VerticalLayer.FINANCIAL_ECONOMIC: 25,
    VerticalLayer.ARTS_MEDIA_ENTERTAINMENT: 12,
    VerticalLayer.META_PEER_FRAMEWORKS: 30,
}


# ════════════════════════════════════════════════════════════════════════════════
# Data Structures
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class BackendConfig:
    """Configuration for backend connection."""
    
    base_url: str = "http://localhost:8000"
    api_version: str = "v1"
    timeout_seconds: int = 60
    max_retries: int = 3
    
    # Authentication
    api_key: Optional[str] = None
    bearer_token: Optional[str] = None
    
    # Features
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    async_execution: bool = False


@dataclass
class ExecutionRequest:
    """Request to execute a framework."""
    
    framework_id: str
    input_data: dict[str, Any]
    parameters: dict[str, Any] = field(default_factory=dict)
    config: FrameworkConfig = field(default_factory=FrameworkConfig)
    output_format: OutputFormat = OutputFormat.JSON
    async_mode: bool = False
    idempotency_key: Optional[str] = None
    
    def to_api_payload(self) -> dict[str, Any]:
        """Convert to API request payload."""
        return {
            "framework_id": self.framework_id,
            "input_data": self.input_data,
            "parameters": self.parameters,
            "config": {
                "n_cohorts": self.config.n_cohorts,
                "time_steps": self.config.time_steps,
                "random_seed": self.config.random_seed,
            },
            "output_format": self.output_format.value,
            "async_mode": self.async_mode,
            "idempotency_key": self.idempotency_key,
        }


@dataclass
class ExecutionResult:
    """Result from framework execution."""
    
    execution_id: UUID
    framework_id: str
    status: ExecutionStatus
    
    # Results
    result: Optional[dict[str, Any]] = None
    metrics: Optional[dict[str, Any]] = None
    trajectory: Optional[list[dict[str, Any]]] = None
    
    # Billing
    tcu_cost: float = 0.0
    
    # Timing
    execution_time_ms: Optional[int] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    
    # Errors
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "ExecutionResult":
        """Create from API response."""
        return cls(
            execution_id=UUID(data["execution_id"]),
            framework_id=data["framework_id"],
            status=ExecutionStatus(data["status"]),
            result=data.get("result"),
            metrics=data.get("metrics"),
            trajectory=data.get("trajectory"),
            tcu_cost=data.get("tcu_cost", 0.0),
            execution_time_ms=data.get("execution_time_ms"),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(timezone.utc),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            error_message=data.get("error_message"),
            error_code=data.get("error_code"),
        )


@dataclass
class FrameworkRegistration:
    """Registration entry for a framework."""
    
    framework_id: str
    name: str
    version: str
    layer: VerticalLayer
    tier: Tier
    
    # Schema
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    
    # Documentation
    description: str = ""
    authors: list[str] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)
    
    # Domains
    required_domains: list[str] = field(default_factory=list)
    optional_domains: list[str] = field(default_factory=list)
    
    # Billing
    base_tcu_cost: int = 10
    
    # Status
    enabled: bool = True
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    @classmethod
    def from_metadata(cls, metadata: FrameworkMetadata) -> "FrameworkRegistration":
        """Create from framework metadata."""
        return cls(
            framework_id=metadata.framework_id,
            name=metadata.name,
            version=metadata.version,
            layer=metadata.layer,
            tier=metadata.tier,
            description=metadata.description,
            authors=metadata.authors,
            citations=metadata.citations,
            required_domains=metadata.required_domains,
            optional_domains=metadata.optional_domains,
            base_tcu_cost=LAYER_BASE_TCU.get(metadata.layer, 10),
        )


# ════════════════════════════════════════════════════════════════════════════════
# TCU Calculator
# ════════════════════════════════════════════════════════════════════════════════


class TCUCalculator:
    """
    Calculate TCU (Transaction Compute Units) costs.
    
    TCU is the billing unit for framework execution.
    
    Cost = base_cost * tier_multiplier * size_factor * complexity_factor
    """
    
    def __init__(
        self,
        base_multiplier: float = 1.0,
        size_scaling: float = 0.5,
        complexity_scaling: float = 0.3,
    ):
        """
        Initialize TCU calculator.
        
        Args:
            base_multiplier: Global multiplier for all costs
            size_scaling: Scaling factor for data size
            complexity_scaling: Scaling factor for computation complexity
        """
        self.base_multiplier = base_multiplier
        self.size_scaling = size_scaling
        self.complexity_scaling = complexity_scaling
    
    def calculate(
        self,
        framework: BaseMetaFramework,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> float:
        """
        Calculate TCU cost for execution.
        
        Args:
            framework: Framework to execute
            bundle: Input data bundle
            config: Framework configuration
        
        Returns:
            TCU cost as float
        """
        metadata = framework.metadata()
        
        # Base cost from layer
        base_cost = LAYER_BASE_TCU.get(metadata.layer, 10)
        
        # Tier multiplier
        tier_mult = TCU_MULTIPLIERS.get(metadata.tier, 1.0)
        
        # Size factor (log scale)
        total_rows = sum(d.data.shape[0] for d in bundle._domains.values())
        size_factor = 1.0 + self.size_scaling * np.log10(max(1, total_rows))
        
        # Complexity factor (based on config)
        complexity = (
            1.0 
            + self.complexity_scaling * (config.time_steps / 10)
            + self.complexity_scaling * (config.n_cohorts / 100)
        )
        
        # Total cost
        cost = base_cost * tier_mult * size_factor * complexity * self.base_multiplier
        
        return round(cost, 2)
    
    def estimate(
        self,
        framework_id: str,
        layer: VerticalLayer,
        tier: Tier,
        n_rows: int,
        n_steps: int,
        n_cohorts: int,
    ) -> float:
        """
        Estimate TCU cost without full framework instance.
        
        Args:
            framework_id: Framework identifier
            layer: Vertical layer
            tier: Required tier
            n_rows: Estimated input rows
            n_steps: Time steps
            n_cohorts: Number of cohorts
        
        Returns:
            Estimated TCU cost
        """
        base_cost = LAYER_BASE_TCU.get(layer, 10)
        tier_mult = TCU_MULTIPLIERS.get(tier, 1.0)
        size_factor = 1.0 + self.size_scaling * np.log10(max(1, n_rows))
        complexity = (
            1.0 
            + self.complexity_scaling * (n_steps / 10)
            + self.complexity_scaling * (n_cohorts / 100)
        )
        
        cost = base_cost * tier_mult * size_factor * complexity * self.base_multiplier
        
        return round(cost, 2)


# ════════════════════════════════════════════════════════════════════════════════
# Backend Client Protocol
# ════════════════════════════════════════════════════════════════════════════════


class BackendClientProtocol(Protocol):
    """Protocol for backend communication."""
    
    async def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        """Execute a framework."""
        ...
    
    async def get_result(
        self,
        execution_id: UUID,
    ) -> ExecutionResult:
        """Get execution result by ID."""
        ...
    
    async def register_framework(
        self,
        registration: FrameworkRegistration,
    ) -> bool:
        """Register a framework."""
        ...
    
    async def list_frameworks(
        self,
        layer: Optional[VerticalLayer] = None,
        tier: Optional[Tier] = None,
    ) -> list[FrameworkRegistration]:
        """List registered frameworks."""
        ...


# ════════════════════════════════════════════════════════════════════════════════
# Framework Execution Service
# ════════════════════════════════════════════════════════════════════════════════


class FrameworkExecutionService:
    """
    Service for executing frameworks through the backend.
    
    Handles:
    - Remote framework execution
    - Result caching
    - Retry logic
    - TCU billing
    
    Example:
        >>> config = BackendConfig(api_key="...")
        >>> service = FrameworkExecutionService(config)
        >>> 
        >>> request = ExecutionRequest(
        ...     framework_id="mpi",
        ...     input_data={"health": [...], "education": [...]},
        ... )
        >>> result = await service.execute(request)
        >>> print(f"MPI: {result.metrics['mpi']}")
    """
    
    def __init__(
        self,
        config: BackendConfig,
        client: Optional[BackendClientProtocol] = None,
    ):
        """
        Initialize execution service.
        
        Args:
            config: Backend configuration
            client: Optional custom client (for testing)
        """
        self.config = config
        self._client = client
        self._cache: dict[str, ExecutionResult] = {}
        self.tcu_calculator = TCUCalculator()
    
    def _get_cache_key(self, request: ExecutionRequest) -> str:
        """Generate cache key for request."""
        content = json.dumps(
            {
                "framework_id": request.framework_id,
                "input_data": request.input_data,
                "parameters": request.parameters,
            },
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(content.encode()).hexdigest()[:32]
    
    async def execute(
        self,
        request: ExecutionRequest,
        skip_cache: bool = False,
    ) -> ExecutionResult:
        """
        Execute a framework.
        
        Args:
            request: Execution request
            skip_cache: If True, bypass cache
        
        Returns:
            Execution result
        
        Raises:
            ValueError: If framework not found
            RuntimeError: If execution fails
        """
        # Check cache
        if self.config.enable_caching and not skip_cache:
            cache_key = self._get_cache_key(request)
            if cache_key in self._cache:
                logger.info(f"Cache hit for {request.framework_id}")
                return self._cache[cache_key]
        
        # Execute through client
        if self._client:
            result = await self._client.execute(request)
        else:
            # Local execution fallback
            result = await self._execute_local(request)
        
        # Cache result
        if self.config.enable_caching and result.status == ExecutionStatus.COMPLETED:
            self._cache[self._get_cache_key(request)] = result
        
        return result
    
    async def _execute_local(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        """Execute framework locally (fallback mode)."""
        from krl_frameworks.core import get_framework
        
        start_time = datetime.now(timezone.utc)
        execution_id = uuid4()
        
        try:
            # Get framework
            framework = get_framework(request.framework_id)
            if framework is None:
                return ExecutionResult(
                    execution_id=execution_id,
                    framework_id=request.framework_id,
                    status=ExecutionStatus.FAILED,
                    error_message=f"Framework not found: {request.framework_id}",
                    error_code="FRAMEWORK_NOT_FOUND",
                )
            
            # Build DataBundle
            bundle = self._build_bundle(request.input_data)
            
            # Configure
            config = FrameworkConfig(**request.parameters) if request.parameters else FrameworkConfig()
            
            # Execute
            framework.fit(bundle, config)
            sim_result = framework.simulate(steps=config.time_steps)
            
            # Calculate cost
            tcu_cost = self.tcu_calculator.calculate(framework, bundle, config)
            
            # Build result
            end_time = datetime.now(timezone.utc)
            execution_time = int((end_time - start_time).total_seconds() * 1000)
            
            return ExecutionResult(
                execution_id=execution_id,
                framework_id=request.framework_id,
                status=ExecutionStatus.COMPLETED,
                result={"states": len(sim_result.trajectory)},
                metrics=sim_result.metrics,
                tcu_cost=tcu_cost,
                execution_time_ms=execution_time,
                created_at=start_time,
                completed_at=end_time,
            )
            
        except Exception as e:
            logger.exception(f"Local execution failed: {e}")
            return ExecutionResult(
                execution_id=execution_id,
                framework_id=request.framework_id,
                status=ExecutionStatus.FAILED,
                error_message=str(e),
                error_code="EXECUTION_ERROR",
            )
    
    def _build_bundle(self, input_data: dict[str, Any]) -> DataBundle:
        """Build DataBundle from input data."""
        domains = {}
        
        for domain_name, data in input_data.items():
            if isinstance(data, pd.DataFrame):
                df = data
            elif isinstance(data, dict):
                df = pd.DataFrame(data)
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame([data])
            
            domains[domain_name] = df
        
        return DataBundle.from_dataframes(domains)
    
    async def poll_result(
        self,
        execution_id: UUID,
        timeout_seconds: int = 300,
        poll_interval: float = 1.0,
    ) -> ExecutionResult:
        """
        Poll for async execution result.
        
        Args:
            execution_id: Execution ID to poll
            timeout_seconds: Maximum wait time
            poll_interval: Seconds between polls
        
        Returns:
            Final execution result
        """
        import asyncio
        
        start = datetime.now(timezone.utc)
        
        while True:
            if self._client:
                result = await self._client.get_result(execution_id)
            else:
                raise RuntimeError("No client configured for polling")
            
            if result.status in (ExecutionStatus.COMPLETED, ExecutionStatus.FAILED):
                return result
            
            elapsed = (datetime.now(timezone.utc) - start).total_seconds()
            if elapsed >= timeout_seconds:
                return ExecutionResult(
                    execution_id=execution_id,
                    framework_id="unknown",
                    status=ExecutionStatus.FAILED,
                    error_message="Polling timeout exceeded",
                    error_code="TIMEOUT",
                )
            
            await asyncio.sleep(poll_interval)


# ════════════════════════════════════════════════════════════════════════════════
# Framework Registration Service
# ════════════════════════════════════════════════════════════════════════════════


class FrameworkRegistrationService:
    """
    Service for registering frameworks with the backend.
    
    Handles:
    - Framework registration
    - Schema generation
    - Tier validation
    - Discovery
    
    Example:
        >>> service = FrameworkRegistrationService(config)
        >>> from krl_frameworks.layers.socioeconomic import MPIFramework
        >>> 
        >>> registration = service.create_registration(MPIFramework())
        >>> await service.register(registration)
    """
    
    def __init__(
        self,
        config: BackendConfig,
        client: Optional[BackendClientProtocol] = None,
    ):
        self.config = config
        self._client = client
        self._registrations: dict[str, FrameworkRegistration] = {}
    
    def create_registration(
        self,
        framework: BaseMetaFramework,
    ) -> FrameworkRegistration:
        """
        Create registration from framework instance.
        
        Args:
            framework: Framework to register
        
        Returns:
            FrameworkRegistration instance
        """
        metadata = framework.metadata()
        registration = FrameworkRegistration.from_metadata(metadata)
        
        # Generate schemas
        registration.input_schema = self._generate_input_schema(metadata)
        registration.output_schema = self._generate_output_schema(metadata)
        
        return registration
    
    def _generate_input_schema(
        self,
        metadata: FrameworkMetadata,
    ) -> dict[str, Any]:
        """Generate input schema from metadata."""
        properties = {}
        
        for domain in metadata.required_domains:
            properties[domain] = {
                "type": "object",
                "description": f"Required domain: {domain}",
                "required": True,
            }
        
        for domain in metadata.optional_domains:
            properties[domain] = {
                "type": "object",
                "description": f"Optional domain: {domain}",
                "required": False,
            }
        
        return {
            "type": "object",
            "properties": properties,
            "required": metadata.required_domains,
        }
    
    def _generate_output_schema(
        self,
        metadata: FrameworkMetadata,
    ) -> dict[str, Any]:
        """Generate output schema."""
        return {
            "type": "object",
            "properties": {
                "metrics": {
                    "type": "object",
                    "description": "Computed metrics from framework",
                },
                "trajectory": {
                    "type": "array",
                    "description": "State trajectory over time",
                },
                "final_state": {
                    "type": "object",
                    "description": "Final cohort state",
                },
            },
        }
    
    async def register(
        self,
        registration: FrameworkRegistration,
    ) -> bool:
        """
        Register a framework with the backend.
        
        Args:
            registration: Registration details
        
        Returns:
            True if successful
        """
        if self._client:
            success = await self._client.register_framework(registration)
        else:
            # Local registration
            self._registrations[registration.framework_id] = registration
            success = True
            logger.info(f"Registered framework locally: {registration.framework_id}")
        
        return success
    
    async def register_all(
        self,
        frameworks: list[BaseMetaFramework],
    ) -> dict[str, bool]:
        """
        Register multiple frameworks.
        
        Args:
            frameworks: List of frameworks to register
        
        Returns:
            Dictionary of framework_id -> success
        """
        results = {}
        
        for framework in frameworks:
            registration = self.create_registration(framework)
            success = await self.register(registration)
            results[registration.framework_id] = success
        
        return results
    
    async def list_registered(
        self,
        layer: Optional[VerticalLayer] = None,
        tier: Optional[Tier] = None,
    ) -> list[FrameworkRegistration]:
        """
        List registered frameworks.
        
        Args:
            layer: Filter by layer
            tier: Filter by tier
        
        Returns:
            List of registrations
        """
        if self._client:
            return await self._client.list_frameworks(layer, tier)
        
        # Local filtering
        registrations = list(self._registrations.values())
        
        if layer:
            registrations = [r for r in registrations if r.layer == layer]
        
        if tier:
            registrations = [r for r in registrations if r.tier == tier]
        
        return registrations


# ════════════════════════════════════════════════════════════════════════════════
# Convenience Functions
# ════════════════════════════════════════════════════════════════════════════════


def create_execution_service(
    base_url: str = "http://localhost:8000",
    api_key: Optional[str] = None,
    **kwargs: Any,
) -> FrameworkExecutionService:
    """
    Create a configured execution service.
    
    Args:
        base_url: Backend base URL
        api_key: API key for authentication
        **kwargs: Additional BackendConfig options
    
    Returns:
        Configured FrameworkExecutionService
    """
    config = BackendConfig(
        base_url=base_url,
        api_key=api_key,
        **kwargs,
    )
    return FrameworkExecutionService(config)


def create_registration_service(
    base_url: str = "http://localhost:8000",
    api_key: Optional[str] = None,
    **kwargs: Any,
) -> FrameworkRegistrationService:
    """
    Create a configured registration service.
    
    Args:
        base_url: Backend base URL
        api_key: API key for authentication
        **kwargs: Additional BackendConfig options
    
    Returns:
        Configured FrameworkRegistrationService
    """
    config = BackendConfig(
        base_url=base_url,
        api_key=api_key,
        **kwargs,
    )
    return FrameworkRegistrationService(config)


# ════════════════════════════════════════════════════════════════════════════════
# Exports
# ════════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    "ExecutionStatus",
    "OutputFormat",
    # Config
    "BackendConfig",
    # Data classes
    "ExecutionRequest",
    "ExecutionResult",
    "FrameworkRegistration",
    # Services
    "FrameworkExecutionService",
    "FrameworkRegistrationService",
    "TCUCalculator",
    # Protocol
    "BackendClientProtocol",
    # Convenience
    "create_execution_service",
    "create_registration_service",
    # Constants
    "TCU_MULTIPLIERS",
    "LAYER_BASE_TCU",
]
