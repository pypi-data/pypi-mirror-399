# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - DAG Composer
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
DAG Composer for Framework Orchestration.

This module provides directed acyclic graph (DAG) based orchestration
for composing multiple frameworks into analysis pipelines. Key components:

- FrameworkDAG: Graph structure representing framework dependencies
- TopologicalExecutor: Executes frameworks in dependency order
- PipelineBuilder: Fluent API for constructing pipelines
- DataFlowMapper: Routes outputs from one framework as inputs to another

Enterprise Tier Feature:
    DAG orchestration is an Enterprise-tier feature enabling:
    - Multi-framework composition
    - Automatic dependency resolution
    - Parallel execution where possible
    - State propagation between frameworks

Example:
    >>> dag = FrameworkDAG()
    >>> dag.add_framework(mpi)
    >>> dag.add_framework(hdi)
    >>> dag.add_framework(remsom, depends_on=["mpi", "hdi"])
    >>> executor = TopologicalExecutor(dag)
    >>> results = executor.execute(bundle)
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, Mapping, Optional, Sequence

import numpy as np

from krl_frameworks.core.base import BaseMetaFramework, FrameworkExecutionResult
from krl_frameworks.core.data_bundle import DataBundle
from krl_frameworks.core.exceptions import (
    CyclicDependencyError,
    DAGError,
    ExecutionError,
    FrameworkNotFoundError,
)
from krl_frameworks.core.state import CohortStateVector
from krl_frameworks.core.tier import Tier, requires_tier

if TYPE_CHECKING:
    from krl_frameworks.core.config import FrameworkConfig
    from krl_frameworks.core.registry import FrameworkRegistry

__all__ = [
    "FrameworkDAG",
    "DAGNode",
    "DAGEdge",
    "TopologicalExecutor",
    "PipelineBuilder",
    "DataFlowMapper",
    "ExecutionResult",
    "ExecutionStatus",
]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Execution Status
# ════════════════════════════════════════════════════════════════════════════════


class ExecutionStatus(Enum):
    """Status of framework execution in DAG."""
    
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    SKIPPED = auto()


# ════════════════════════════════════════════════════════════════════════════════
# DAG Node
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class DAGNode:
    """
    Node in the framework DAG representing a single framework.
    
    Attributes:
        framework_id: Unique identifier for the framework.
        framework: The framework instance.
        config: Framework-specific configuration overrides.
        status: Current execution status.
        result: Execution result (populated after run).
        error: Error message if failed.
    """
    
    framework_id: str
    framework: BaseMetaFramework
    config: Optional[FrameworkConfig] = None
    status: ExecutionStatus = ExecutionStatus.PENDING
    result: Optional[FrameworkExecutionResult] = None
    error: Optional[str] = None
    
    def reset(self) -> None:
        """Reset node state for re-execution."""
        self.status = ExecutionStatus.PENDING
        self.result = None
        self.error = None


# ════════════════════════════════════════════════════════════════════════════════
# DAG Edge
# ════════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class DAGEdge:
    """
    Edge in the framework DAG representing a dependency.
    
    Attributes:
        source_id: Framework providing output.
        target_id: Framework consuming input.
        data_mapper: Optional function to transform data between frameworks.
        field_mapping: Mapping of source output fields to target input fields.
    """
    
    source_id: str
    target_id: str
    data_mapper: Optional[Callable[[dict[str, Any]], dict[str, Any]]] = None
    field_mapping: Optional[Mapping[str, str]] = None


# ════════════════════════════════════════════════════════════════════════════════
# Data Flow Mapper
# ════════════════════════════════════════════════════════════════════════════════


class DataFlowMapper:
    """
    Maps data flow between frameworks in a DAG.
    
    Handles:
    - State propagation from upstream to downstream frameworks
    - Metric aggregation from multiple sources
    - Bundle enrichment with upstream outputs
    """
    
    def __init__(self):
        self._transformers: dict[tuple[str, str], Callable] = {}
    
    def register_transformer(
        self,
        source_id: str,
        target_id: str,
        transformer: Callable[[dict[str, Any]], dict[str, Any]],
    ) -> None:
        """Register a data transformer for an edge."""
        self._transformers[(source_id, target_id)] = transformer
    
    def transform(
        self,
        source_id: str,
        target_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply transformation for an edge."""
        key = (source_id, target_id)
        if key in self._transformers:
            return self._transformers[key](data)
        return data
    
    def merge_upstream_results(
        self,
        results: Sequence[FrameworkExecutionResult],
    ) -> dict[str, Any]:
        """Merge results from multiple upstream frameworks."""
        merged = {}
        for result in results:
            framework_id = result.framework_id
            merged[f"{framework_id}_metrics"] = result.metrics
            if result.final_state is not None:
                merged[f"{framework_id}_state"] = result.final_state.to_dict()
        return merged


# ════════════════════════════════════════════════════════════════════════════════
# Framework DAG
# ════════════════════════════════════════════════════════════════════════════════


class FrameworkDAG:
    """
    Directed Acyclic Graph for framework orchestration.
    
    Manages framework dependencies and execution order. Ensures
    no circular dependencies and provides topological ordering
    for execution.
    
    Example:
        >>> dag = FrameworkDAG()
        >>> dag.add_framework(MPIFramework(), "mpi")
        >>> dag.add_framework(HDIFramework(), "hdi")
        >>> dag.add_framework(REMSOMFramework(), "remsom", 
        ...                   depends_on=["mpi", "hdi"])
        >>> order = dag.topological_sort()
        >>> print(order)  # ['mpi', 'hdi', 'remsom']
    """
    
    def __init__(self):
        self._nodes: dict[str, DAGNode] = {}
        self._edges: list[DAGEdge] = []
        self._adjacency: dict[str, set[str]] = defaultdict(set)
        self._reverse_adjacency: dict[str, set[str]] = defaultdict(set)
        self._data_mapper = DataFlowMapper()
    
    def add_framework(
        self,
        framework: BaseMetaFramework,
        framework_id: Optional[str] = None,
        *,
        depends_on: Optional[Sequence[str]] = None,
        config: Optional[FrameworkConfig] = None,
    ) -> str:
        """
        Add a framework to the DAG.
        
        Args:
            framework: Framework instance to add.
            framework_id: Optional ID (defaults to framework metadata ID).
            depends_on: List of framework IDs this framework depends on.
            config: Framework-specific configuration.
            
        Returns:
            The framework ID assigned.
            
        Raises:
            CyclicDependencyError: If adding this framework creates a cycle.
        """
        framework_id = framework_id or framework.metadata().framework_id
        
        if framework_id in self._nodes:
            logger.warning(f"Replacing existing framework: {framework_id}")
        
        self._nodes[framework_id] = DAGNode(
            framework_id=framework_id,
            framework=framework,
            config=config,
        )
        
        # Add dependency edges
        if depends_on:
            for source_id in depends_on:
                if source_id not in self._nodes:
                    raise FrameworkNotFoundError(
                        f"Dependency '{source_id}' not found in DAG"
                    )
                self.add_edge(source_id, framework_id)
        
        # Validate no cycles
        try:
            self.topological_sort()
        except CyclicDependencyError:
            # Rollback
            del self._nodes[framework_id]
            for edge in list(self._edges):
                if edge.target_id == framework_id:
                    self._edges.remove(edge)
            raise
        
        logger.info(f"Added framework '{framework_id}' to DAG")
        return framework_id
    
    def add_edge(
        self,
        source_id: str,
        target_id: str,
        *,
        data_mapper: Optional[Callable] = None,
        field_mapping: Optional[Mapping[str, str]] = None,
    ) -> None:
        """
        Add a dependency edge between frameworks.
        
        Args:
            source_id: Upstream framework ID.
            target_id: Downstream framework ID.
            data_mapper: Optional data transformation function.
            field_mapping: Optional field mapping dict.
        """
        if source_id not in self._nodes:
            raise FrameworkNotFoundError(f"Source framework '{source_id}' not found")
        if target_id not in self._nodes:
            raise FrameworkNotFoundError(f"Target framework '{target_id}' not found")
        
        edge = DAGEdge(
            source_id=source_id,
            target_id=target_id,
            data_mapper=data_mapper,
            field_mapping=field_mapping,
        )
        
        self._edges.append(edge)
        self._adjacency[source_id].add(target_id)
        self._reverse_adjacency[target_id].add(source_id)
        
        if data_mapper:
            self._data_mapper.register_transformer(source_id, target_id, data_mapper)
    
    def get_dependencies(self, framework_id: str) -> set[str]:
        """Get immediate dependencies of a framework."""
        return self._reverse_adjacency.get(framework_id, set())
    
    def get_dependents(self, framework_id: str) -> set[str]:
        """Get frameworks that depend on this framework."""
        return self._adjacency.get(framework_id, set())
    
    def topological_sort(self) -> list[str]:
        """
        Return frameworks in topological execution order.
        
        Returns:
            List of framework IDs in dependency order.
            
        Raises:
            CyclicDependencyError: If the graph contains a cycle.
        """
        # Kahn's algorithm
        in_degree = {node_id: 0 for node_id in self._nodes}
        
        for edge in self._edges:
            in_degree[edge.target_id] += 1
        
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node_id = queue.pop(0)
            result.append(node_id)
            
            for dependent in self._adjacency.get(node_id, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        if len(result) != len(self._nodes):
            # Find the cycle
            remaining = set(self._nodes.keys()) - set(result)
            raise CyclicDependencyError(
                f"Cycle detected involving frameworks: {remaining}",
                cycle=list(remaining),
            )
        
        return result
    
    def get_node(self, framework_id: str) -> DAGNode:
        """Get a node by framework ID."""
        if framework_id not in self._nodes:
            raise FrameworkNotFoundError(f"Framework '{framework_id}' not in DAG")
        return self._nodes[framework_id]
    
    def reset(self) -> None:
        """Reset all nodes to PENDING state."""
        for node in self._nodes.values():
            node.reset()
    
    def __len__(self) -> int:
        return len(self._nodes)
    
    def __contains__(self, framework_id: str) -> bool:
        return framework_id in self._nodes
    
    @property
    def framework_ids(self) -> list[str]:
        """List of all framework IDs in the DAG."""
        return list(self._nodes.keys())
    
    @property
    def data_mapper(self) -> DataFlowMapper:
        """Get the data flow mapper."""
        return self._data_mapper


# ════════════════════════════════════════════════════════════════════════════════
# Execution Result
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class ExecutionResult:
    """
    Container for DAG execution results.
    
    Attributes:
        framework_results: Dict mapping framework_id to execution result.
        execution_order: Order in which frameworks were executed.
        total_time_ms: Total execution time in milliseconds.
        success: Whether all frameworks succeeded.
        failed_frameworks: List of failed framework IDs.
    """
    
    framework_results: dict[str, FrameworkExecutionResult]
    execution_order: list[str]
    total_time_ms: float = 0.0
    success: bool = True
    failed_frameworks: list[str] = field(default_factory=list)
    
    def get_result(self, framework_id: str) -> Optional[FrameworkExecutionResult]:
        """Get result for a specific framework."""
        return self.framework_results.get(framework_id)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "success": self.success,
            "execution_order": self.execution_order,
            "total_time_ms": self.total_time_ms,
            "failed_frameworks": self.failed_frameworks,
            "framework_results": {
                k: v.to_dict() if hasattr(v, "to_dict") else str(v)
                for k, v in self.framework_results.items()
            },
        }


# ════════════════════════════════════════════════════════════════════════════════
# Topological Executor
# ════════════════════════════════════════════════════════════════════════════════


class TopologicalExecutor:
    """
    Executes frameworks in a DAG in topological order.
    
    Handles:
    - Dependency resolution
    - State propagation between frameworks
    - Error handling and recovery
    - Execution logging
    
    Enterprise Tier Feature.
    """
    
    def __init__(
        self,
        dag: FrameworkDAG,
        *,
        fail_fast: bool = True,
        propagate_state: bool = True,
    ):
        """
        Initialize executor.
        
        Args:
            dag: The framework DAG to execute.
            fail_fast: Stop on first failure if True.
            propagate_state: Pass state between dependent frameworks.
        """
        self.dag = dag
        self.fail_fast = fail_fast
        self.propagate_state = propagate_state
    
    @requires_tier(Tier.ENTERPRISE)
    def execute(
        self,
        bundle: DataBundle,
        config: Optional[FrameworkConfig] = None,
    ) -> ExecutionResult:
        """
        Execute all frameworks in the DAG.
        
        Args:
            bundle: Input data bundle.
            config: Default configuration for all frameworks.
            
        Returns:
            ExecutionResult with all framework results.
        """
        import time
        from krl_frameworks.core.config import FrameworkConfig
        
        start_time = time.perf_counter()
        config = config or FrameworkConfig()
        
        self.dag.reset()
        execution_order = self.dag.topological_sort()
        
        results: dict[str, FrameworkExecutionResult] = {}
        failed: list[str] = []
        
        logger.info(f"Executing DAG with {len(execution_order)} frameworks")
        
        for framework_id in execution_order:
            node = self.dag.get_node(framework_id)
            
            # Check if dependencies failed
            deps_failed = any(
                dep_id in failed
                for dep_id in self.dag.get_dependencies(framework_id)
            )
            
            if deps_failed:
                node.status = ExecutionStatus.SKIPPED
                node.error = "Dependency failed"
                logger.warning(f"Skipping '{framework_id}': dependency failed")
                continue
            
            # Prepare input (enrich bundle with upstream results)
            enriched_bundle = self._enrich_bundle(bundle, framework_id, results)
            
            # Execute framework
            node.status = ExecutionStatus.RUNNING
            try:
                framework_config = node.config or config
                result = self._execute_framework(
                    node.framework,
                    enriched_bundle,
                    framework_config,
                )
                node.result = result
                node.status = ExecutionStatus.COMPLETED
                results[framework_id] = result
                
                logger.info(f"Completed '{framework_id}'")
                
            except Exception as e:
                node.status = ExecutionStatus.FAILED
                node.error = str(e)
                failed.append(framework_id)
                
                logger.error(f"Failed '{framework_id}': {e}")
                
                if self.fail_fast:
                    break
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        return ExecutionResult(
            framework_results=results,
            execution_order=execution_order,
            total_time_ms=elapsed_ms,
            success=len(failed) == 0,
            failed_frameworks=failed,
        )
    
    def _execute_framework(
        self,
        framework: BaseMetaFramework,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> FrameworkExecutionResult:
        """Execute a single framework."""
        # Use the framework's simulate method
        return framework.fit(bundle, config).simulate(
            n_periods=config.n_periods,
        )
    
    def _enrich_bundle(
        self,
        bundle: DataBundle,
        framework_id: str,
        upstream_results: dict[str, FrameworkExecutionResult],
    ) -> DataBundle:
        """Enrich bundle with upstream framework outputs."""
        if not self.propagate_state:
            return bundle
        
        dependencies = self.dag.get_dependencies(framework_id)
        if not dependencies:
            return bundle
        
        # Collect upstream results
        upstream = [
            upstream_results[dep_id]
            for dep_id in dependencies
            if dep_id in upstream_results
        ]
        
        if not upstream:
            return bundle
        
        # Merge upstream data into bundle metadata
        merged = self.dag.data_mapper.merge_upstream_results(upstream)
        
        # Return bundle with enriched metadata
        return bundle.with_metadata({"upstream_results": merged})


# ════════════════════════════════════════════════════════════════════════════════
# Pipeline Builder
# ════════════════════════════════════════════════════════════════════════════════


class PipelineBuilder:
    """
    Fluent API for building framework pipelines.
    
    Example:
        >>> pipeline = (
        ...     PipelineBuilder()
        ...     .add(MPIFramework(), "mpi")
        ...     .add(HDIFramework(), "hdi")
        ...     .add(REMSOMFramework(), "remsom", depends_on=["mpi", "hdi"])
        ...     .build()
        ... )
        >>> results = pipeline.execute(bundle)
    """
    
    def __init__(self):
        self._dag = FrameworkDAG()
        self._config: Optional[FrameworkConfig] = None
    
    def add(
        self,
        framework: BaseMetaFramework,
        framework_id: Optional[str] = None,
        *,
        depends_on: Optional[Sequence[str]] = None,
        config: Optional[FrameworkConfig] = None,
    ) -> PipelineBuilder:
        """Add a framework to the pipeline."""
        self._dag.add_framework(
            framework,
            framework_id,
            depends_on=depends_on,
            config=config,
        )
        return self
    
    def with_config(self, config: FrameworkConfig) -> PipelineBuilder:
        """Set default configuration for the pipeline."""
        self._config = config
        return self
    
    def build(self) -> TopologicalExecutor:
        """Build the executor from the pipeline definition."""
        return TopologicalExecutor(self._dag)
    
    @property
    def dag(self) -> FrameworkDAG:
        """Access the underlying DAG."""
        return self._dag
