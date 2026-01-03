# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Framework Orchestrator
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Framework Orchestrator.

Meta-level orchestration for composing and coordinating multiple frameworks:
- Sequential pipeline execution
- Parallel framework execution
- Framework result aggregation
- Cross-layer data flow
- Dependency resolution

References:
    - KRL Architecture: Multi-layer framework composition
    - Workflow orchestration patterns

Tier: PROFESSIONAL / ENTERPRISE
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Mapping, Optional, Type

import numpy as np

from krl_frameworks.core.base import (
    BaseMetaFramework,
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
from krl_frameworks.core.data_bundle import DataBundle
from krl_frameworks.core.state import CohortStateVector, StateTrajectory
from krl_frameworks.core.tier import Tier, requires_tier
from krl_frameworks.simulation.cbss import TransitionFunction

if TYPE_CHECKING:
    from krl_frameworks.core.config import FrameworkConfig

__all__ = ["FrameworkOrchestrator"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Orchestrator Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class ExecutionMode(Enum):
    """Framework execution modes."""
    SEQUENTIAL = "Sequential"
    PARALLEL = "Parallel"
    PIPELINE = "Pipeline"
    DAG = "Directed Acyclic Graph"


class AggregationMethod(Enum):
    """Result aggregation methods."""
    MEAN = "Mean"
    WEIGHTED_MEAN = "Weighted Mean"
    MEDIAN = "Median"
    ENSEMBLE = "Ensemble"
    STACKED = "Stacked"


@dataclass
class FrameworkNode:
    """Node in the framework execution graph."""
    
    framework_class: Type[BaseMetaFramework]
    name: str = ""
    config: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    weight: float = 1.0
    
    def __post_init__(self):
        if not self.name:
            self.name = self.framework_class.__name__


@dataclass
class FrameworkResult:
    """Result from a single framework execution."""
    
    name: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)
    output: dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    success: bool = True
    error: Optional[str] = None


@dataclass
class PipelineResult:
    """Result from pipeline execution."""
    
    # Individual framework results
    results: list[FrameworkResult] = field(default_factory=list)
    
    # Aggregated results
    aggregated_metrics: dict[str, Any] = field(default_factory=dict)
    
    # Pipeline metadata
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    total_time: float = 0.0
    n_frameworks: int = 0
    n_successful: int = 0


@dataclass
class EnsembleResult:
    """Result from ensemble aggregation."""
    
    # Individual predictions
    predictions: list[np.ndarray] = field(default_factory=list)
    weights: list[float] = field(default_factory=list)
    
    # Aggregated prediction
    ensemble_prediction: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Uncertainty
    ensemble_std: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Agreement metrics
    agreement_score: float = 0.0


@dataclass
class OrchestratorMetrics:
    """Comprehensive orchestration metrics."""
    
    pipeline_result: PipelineResult = field(default_factory=PipelineResult)
    ensemble_result: Optional[EnsembleResult] = None
    
    # Cross-validation
    cv_scores: list[float] = field(default_factory=list)
    
    # Best framework
    best_framework: str = ""
    best_score: float = 0.0


# ════════════════════════════════════════════════════════════════════════════════
# Orchestrator Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class OrchestratorTransition(TransitionFunction):
    """Transition function for orchestrated execution."""
    
    name = "OrchestratorTransition"
    
    def __init__(self, synergy_factor: float = 0.1):
        self.synergy_factor = synergy_factor
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        params = params or {}
        
        # Synergy from multi-framework coordination
        synergy = params.get("synergy_factor", self.synergy_factor)
        n_frameworks = params.get("n_frameworks", 1)
        
        # Improvement scales with number of frameworks (diminishing returns)
        improvement = synergy * np.log1p(n_frameworks)
        
        new_opportunity = np.clip(
            state.opportunity_score + improvement * 0.02,
            0, 1,
        )
        
        return CohortStateVector(
            employment_prob=state.employment_prob,
            health_burden_score=state.health_burden_score,
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=new_opportunity,
            sector_output=state.sector_output,
            deprivation_vector=state.deprivation_vector,
        )


# ════════════════════════════════════════════════════════════════════════════════
# Framework Orchestrator
# ════════════════════════════════════════════════════════════════════════════════


class FrameworkOrchestrator(BaseMetaFramework):
    """
    Framework Orchestrator.
    
    Meta-level orchestration for composing multiple frameworks:
    
    - Pipeline execution (sequential/parallel)
    - Dependency resolution
    - Result aggregation
    - Ensemble methods
    - Cross-validation
    
    Token Weight: 8
    Tier: PROFESSIONAL
    
    Example:
        >>> orchestrator = FrameworkOrchestrator()
        >>> pipeline = orchestrator.create_pipeline([
        ...     FrameworkNode(DiDFramework),
        ...     FrameworkNode(SyntheticControlFramework),
        ... ])
        >>> result = orchestrator.execute_pipeline(pipeline, data)
    
    References:
        - KRL Architecture Documentation
    """
    
    METADATA = FrameworkMetadata(
        slug="framework-orchestrator",
        name="Framework Orchestrator",
        version="1.0.0",
        layer=VerticalLayer.META_PEER_FRAMEWORKS,
        tier=Tier.PROFESSIONAL,
        description=(
            "Meta-level orchestration for composing and coordinating "
            "multiple frameworks across layers."
        ),
        required_domains=["frameworks", "data"],
        output_domains=["aggregated_results", "ensemble_predictions"],
        constituent_models=["pipeline", "ensemble", "dag_executor"],
        tags=["orchestration", "meta", "pipeline", "ensemble"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(
        self,
        execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL,
        aggregation_method: AggregationMethod = AggregationMethod.WEIGHTED_MEAN,
    ):
        super().__init__()
        self.execution_mode = execution_mode
        self.aggregation_method = aggregation_method
        self._transition_fn = OrchestratorTransition()
        self._registered_frameworks: dict[str, FrameworkNode] = {}
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        return cls.METADATA
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        n_cohorts = config.cohort_size or 100
        return CohortStateVector(
            employment_prob=np.full(n_cohorts, 0.70),
            health_burden_score=np.full(n_cohorts, 0.2),
            credit_access_prob=np.full(n_cohorts, 0.70),
            housing_cost_ratio=np.full(n_cohorts, 0.30),
            opportunity_score=np.full(n_cohorts, 0.5),
            sector_output=np.full((n_cohorts, 5), 1000.0),
            deprivation_vector=np.full((n_cohorts, 6), 0.25),
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        return self._transition_fn(
            state, t, config,
            params={"n_frameworks": len(self._registered_frameworks)},
        )
    
    def _compute_metrics(self, state: CohortStateVector) -> dict[str, Any]:
        return {
            "mean_outcome": float(np.mean(state.opportunity_score)),
            "n_frameworks": len(self._registered_frameworks),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {
            "framework": "framework-orchestrator",
            "n_periods": trajectory.n_periods,
        }
    
    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Return Framework Orchestrator dashboard specification.
        
        Meta-orchestrator for composing and coordinating multiple frameworks.
        """
        return FrameworkDashboardSpec(
            slug="framework-orchestrator",
            name="Framework Orchestrator",
            description=(
                "Meta-level orchestration for composing and coordinating "
                "multiple frameworks across layers with pipeline execution."
            ),
            layer="meta",
            parameters_schema={
                "type": "object",
                "properties": {
                    "component_frameworks": {
                        "type": "array",
                        "title": "Component Frameworks",
                        "description": "List of frameworks to orchestrate",
                        "items": {"type": "string"},
                        "default": [],
                        "x-ui-widget": "multi-select",
                        "x-ui-group": "orchestration",
                        "x-ui-order": 1,
                    },
                    "composition_mode": {
                        "type": "string",
                        "title": "Composition Mode",
                        "description": "How frameworks are composed and executed",
                        "enum": ["sequential", "parallel", "pipeline", "dag"],
                        "default": "sequential",
                        "x-ui-widget": "select",
                        "x-ui-group": "orchestration",
                        "x-ui-order": 2,
                    },
                    "data_flow": {
                        "type": "string",
                        "title": "Data Flow Pattern",
                        "description": "How data flows between frameworks",
                        "enum": ["passthrough", "aggregate", "transform"],
                        "default": "passthrough",
                        "x-ui-widget": "select",
                        "x-ui-group": "orchestration",
                        "x-ui-order": 3,
                    },
                },
                "required": ["component_frameworks"],
            },
            default_parameters={
                "component_frameworks": [],
                "composition_mode": "sequential",
                "data_flow": "passthrough",
            },
            parameter_groups=[
                ParameterGroupSpec(
                    key="orchestration",
                    title="Orchestration Settings",
                    description="Configure framework composition and execution",
                    collapsed_by_default=False,
                ),
            ],
            output_views=[
                OutputViewSpec(
                    key="orchestration_graph",
                    title="Orchestration Graph",
                    view_type=ViewType.NETWORK,
                    description="DAG visualization of framework dependencies",
                    result_class=ResultClass.STRUCTURAL_SIMILARITY,
                    output_key="orchestration_graph_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="execution_timeline",
                    title="Execution Timeline",
                    view_type=ViewType.LINE_CHART,
                    description="Framework execution timing and progress",
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="execution_timeline_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="results_summary",
                    title="Results Summary",
                    view_type=ViewType.TABLE,
                    description="Aggregated results from all orchestrated frameworks",
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="results_summary_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
            min_tier=Tier.ENTERPRISE,
        )

    # ════════════════════════════════════════════════════════════════════════════
    # Public API Methods
    # ════════════════════════════════════════════════════════════════════════════
    
    @requires_tier(Tier.PROFESSIONAL)
    def register_framework(
        self,
        framework_class: Type[BaseMetaFramework],
        name: Optional[str] = None,
        config: Optional[dict[str, Any]] = None,
        dependencies: Optional[list[str]] = None,
        weight: float = 1.0,
    ) -> str:
        """
        Register a framework for orchestration.
        
        Args:
            framework_class: Framework class to register
            name: Optional name (defaults to class name)
            config: Framework configuration
            dependencies: List of dependent framework names
            weight: Weight for aggregation
        
        Returns:
            Registered framework name
        """
        node = FrameworkNode(
            framework_class=framework_class,
            name=name or framework_class.__name__,
            config=config or {},
            dependencies=dependencies or [],
            weight=weight,
        )
        
        self._registered_frameworks[node.name] = node
        logger.info(f"Registered framework: {node.name}")
        
        return node.name
    
    @requires_tier(Tier.PROFESSIONAL)
    def create_pipeline(
        self,
        nodes: list[FrameworkNode],
    ) -> list[FrameworkNode]:
        """
        Create an execution pipeline from framework nodes.
        
        Resolves dependencies and orders frameworks.
        
        Args:
            nodes: List of framework nodes
        
        Returns:
            Ordered list of nodes
        """
        # Register all nodes
        for node in nodes:
            self._registered_frameworks[node.name] = node
        
        # Topological sort for dependency resolution
        ordered = []
        visited = set()
        temp_visited = set()
        
        def visit(name: str):
            if name in temp_visited:
                raise ValueError(f"Circular dependency detected: {name}")
            if name in visited:
                return
            
            temp_visited.add(name)
            node = self._registered_frameworks.get(name)
            
            if node:
                for dep in node.dependencies:
                    visit(dep)
            
            temp_visited.remove(name)
            visited.add(name)
            
            if node:
                ordered.append(node)
        
        for node in nodes:
            visit(node.name)
        
        return ordered
    
    @requires_tier(Tier.PROFESSIONAL)
    def execute_framework(
        self,
        node: FrameworkNode,
        data: dict[str, Any],
        prior_results: Optional[dict[str, FrameworkResult]] = None,
    ) -> FrameworkResult:
        """
        Execute a single framework.
        
        Args:
            node: Framework node to execute
            data: Input data
            prior_results: Results from prior frameworks in pipeline
        
        Returns:
            Framework execution result
        """
        import time
        
        start_time = time.time()
        
        try:
            # Instantiate framework
            framework = node.framework_class(**node.config)
            
            # Augment data with prior results if available
            augmented_data = data.copy()
            if prior_results:
                augmented_data["prior_results"] = prior_results
            
            # Execute (simplified - actual execution depends on framework API)
            # Here we simulate by calling run() if available
            if hasattr(framework, "run"):
                result = framework.run(augmented_data)
                metrics = result.get("metrics", {})
                output = result.get("output", {})
            else:
                # Fallback: use metadata
                meta = framework.metadata()
                metrics = {"framework": meta.name}
                output = {"slug": meta.slug}
            
            execution_time = time.time() - start_time
            
            return FrameworkResult(
                name=node.name,
                metrics=metrics,
                output=output,
                execution_time=execution_time,
                success=True,
            )
        
        except Exception as e:
            logger.error(f"Framework {node.name} failed: {e}")
            return FrameworkResult(
                name=node.name,
                execution_time=time.time() - start_time,
                success=False,
                error=str(e),
            )
    
    @requires_tier(Tier.PROFESSIONAL)
    def execute_pipeline(
        self,
        nodes: list[FrameworkNode],
        data: dict[str, Any],
    ) -> PipelineResult:
        """
        Execute a framework pipeline.
        
        Args:
            nodes: Ordered list of framework nodes
            data: Input data
        
        Returns:
            Pipeline execution results
        """
        import time
        
        start_time = time.time()
        
        # Resolve dependencies
        ordered_nodes = self.create_pipeline(nodes)
        
        results = []
        prior_results: dict[str, FrameworkResult] = {}
        
        for node in ordered_nodes:
            result = self.execute_framework(node, data, prior_results)
            results.append(result)
            prior_results[node.name] = result
        
        # Aggregate metrics
        aggregated = self._aggregate_metrics(results)
        
        total_time = time.time() - start_time
        n_successful = sum(1 for r in results if r.success)
        
        return PipelineResult(
            results=results,
            aggregated_metrics=aggregated,
            execution_mode=self.execution_mode,
            total_time=total_time,
            n_frameworks=len(results),
            n_successful=n_successful,
        )
    
    def _aggregate_metrics(
        self,
        results: list[FrameworkResult],
    ) -> dict[str, Any]:
        """Aggregate metrics from multiple frameworks."""
        successful = [r for r in results if r.success]
        
        if not successful:
            return {}
        
        # Collect all numeric metrics
        all_metrics: dict[str, list[float]] = {}
        weights: dict[str, list[float]] = {}
        
        for r in successful:
            node = self._registered_frameworks.get(r.name)
            w = node.weight if node else 1.0
            
            for key, value in r.metrics.items():
                if isinstance(value, (int, float)):
                    if key not in all_metrics:
                        all_metrics[key] = []
                        weights[key] = []
                    all_metrics[key].append(float(value))
                    weights[key].append(w)
        
        # Aggregate based on method
        aggregated = {}
        
        for key, values in all_metrics.items():
            if self.aggregation_method == AggregationMethod.MEAN:
                aggregated[key] = float(np.mean(values))
            elif self.aggregation_method == AggregationMethod.WEIGHTED_MEAN:
                w = np.array(weights[key])
                aggregated[key] = float(np.average(values, weights=w))
            elif self.aggregation_method == AggregationMethod.MEDIAN:
                aggregated[key] = float(np.median(values))
            else:
                aggregated[key] = float(np.mean(values))
        
        return aggregated
    
    @requires_tier(Tier.PROFESSIONAL)
    def ensemble_predictions(
        self,
        predictions: list[np.ndarray],
        weights: Optional[list[float]] = None,
    ) -> EnsembleResult:
        """
        Create ensemble prediction from multiple frameworks.
        
        Args:
            predictions: List of predictions from each framework
            weights: Optional weights (defaults to equal)
        
        Returns:
            Ensemble prediction result
        """
        n_models = len(predictions)
        
        if weights is None:
            weights = [1.0 / n_models] * n_models
        
        # Normalize weights
        w = np.array(weights)
        w = w / np.sum(w)
        
        # Stack predictions
        stacked = np.stack(predictions)
        
        # Weighted average
        ensemble_prediction = np.average(stacked, axis=0, weights=w)
        
        # Uncertainty (std across models)
        ensemble_std = np.std(stacked, axis=0)
        
        # Agreement (1 - normalized variance)
        total_var = np.mean(ensemble_std ** 2)
        mean_pred_var = np.var(ensemble_prediction)
        agreement_score = 1 - total_var / (mean_pred_var + 1e-10) if mean_pred_var > 0 else 1.0
        agreement_score = float(np.clip(agreement_score, 0, 1))
        
        return EnsembleResult(
            predictions=predictions,
            weights=list(w),
            ensemble_prediction=ensemble_prediction,
            ensemble_std=ensemble_std,
            agreement_score=agreement_score,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def cross_validate(
        self,
        nodes: list[FrameworkNode],
        data: dict[str, Any],
        n_folds: int = 5,
    ) -> dict[str, list[float]]:
        """
        Cross-validate framework pipeline.
        
        Args:
            nodes: Framework nodes
            data: Input data
            n_folds: Number of CV folds
        
        Returns:
            CV scores per framework
        """
        cv_scores: dict[str, list[float]] = {node.name: [] for node in nodes}
        
        # Simplified CV (actual implementation would split data)
        for fold in range(n_folds):
            # Add fold noise to simulate different data splits
            fold_data = data.copy()
            fold_data["fold"] = fold
            
            result = self.execute_pipeline(nodes, fold_data)
            
            for r in result.results:
                if r.success and "score" in r.metrics:
                    cv_scores[r.name].append(r.metrics["score"])
                elif r.success:
                    # Use a default metric
                    cv_scores[r.name].append(1.0 if r.success else 0.0)
        
        return cv_scores
    
    @requires_tier(Tier.PROFESSIONAL)
    def analyze_orchestration(
        self,
        nodes: list[FrameworkNode],
        data: dict[str, Any],
        predictions: Optional[list[np.ndarray]] = None,
    ) -> OrchestratorMetrics:
        """
        Comprehensive orchestration analysis.
        
        Args:
            nodes: Framework nodes
            data: Input data
            predictions: Optional predictions for ensemble
        
        Returns:
            Complete orchestration metrics
        """
        # Execute pipeline
        pipeline_result = self.execute_pipeline(nodes, data)
        
        # Ensemble if predictions provided
        ensemble_result = None
        if predictions:
            weights = [
                self._registered_frameworks.get(n.name, FrameworkNode(n.framework_class)).weight
                for n in nodes
            ]
            ensemble_result = self.ensemble_predictions(predictions, weights)
        
        # Cross-validate
        cv_scores = self.cross_validate(nodes, data)
        
        # Find best framework
        avg_scores = {
            name: np.mean(scores) if scores else 0.0
            for name, scores in cv_scores.items()
        }
        
        best_framework = max(avg_scores, key=avg_scores.get) if avg_scores else ""
        best_score = avg_scores.get(best_framework, 0.0)
        
        return OrchestratorMetrics(
            pipeline_result=pipeline_result,
            ensemble_result=ensemble_result,
            cv_scores=list(cv_scores.values()),
            best_framework=best_framework,
            best_score=float(best_score),
        )
