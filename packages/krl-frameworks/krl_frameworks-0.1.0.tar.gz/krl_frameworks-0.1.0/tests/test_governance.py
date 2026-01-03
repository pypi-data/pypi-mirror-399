# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Governance Layer Tests
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Comprehensive test suite for the Runtime Governance Layer.

Tests cover:
    - ProductionGuard: Environment detection, mode enforcement
    - ConnectorFactoryRegistry: Registration, tier gating, domain lookup
    - BindingResolver: Auto-resolution, failure handling
    - AuditLogger: Event emission, JSON formatting
    - ClosureValidator: Pipeline conflict detection
"""

from __future__ import annotations

import io
import json
import os
from unittest.mock import patch

import pytest

from krl_frameworks.core.capabilities import (
    CapabilityDeclaration,
    CapabilityScope,
    ConnectorRequirement,
    ToolkitRequirement,
    ModelZooRequirement,
)
from krl_frameworks.core.execution_context import ExecutionMode
from krl_frameworks.core.bindings import BindingRegistry


# ════════════════════════════════════════════════════════════════════════════════
# ProductionGuard Tests
# ════════════════════════════════════════════════════════════════════════════════


class TestProductionGuard:
    """Tests for ProductionGuard and environment detection."""
    
    def test_detect_development_environment(self) -> None:
        """Development detected when no production env vars set."""
        from krl_frameworks.governance.production_guard import (
            detect_environment,
            ProductionEnvironment,
        )
        
        # Clear all production-related env vars
        env_vars = [
            "PRODUCTION", "ENVIRONMENT", "NODE_ENV",
            "RAILWAY_ENVIRONMENT", "RENDER", "AWS_EXECUTION_ENV",
            "KUBERNETES_SERVICE_HOST", "DYNO",
        ]
        
        with patch.dict(os.environ, {}, clear=True):
            for var in env_vars:
                os.environ.pop(var, None)
            
            result = detect_environment()
            assert result == ProductionEnvironment.DEVELOPMENT
    
    def test_detect_production_via_production_env(self) -> None:
        """Production detected via PRODUCTION=true."""
        from krl_frameworks.governance.production_guard import (
            detect_environment,
            ProductionEnvironment,
        )
        
        with patch.dict(os.environ, {"PRODUCTION": "true"}, clear=True):
            result = detect_environment()
            assert result == ProductionEnvironment.PRODUCTION
    
    def test_detect_production_via_kubernetes(self) -> None:
        """Production detected via KUBERNETES_SERVICE_HOST."""
        from krl_frameworks.governance.production_guard import (
            detect_environment,
            ProductionEnvironment,
        )
        
        with patch.dict(os.environ, {"KUBERNETES_SERVICE_HOST": "10.0.0.1"}, clear=True):
            result = detect_environment()
            assert result == ProductionEnvironment.PRODUCTION
    
    def test_enforce_live_mode_in_production(self) -> None:
        """ProductionGuard.enforce() raises on non-LIVE mode in production."""
        from krl_frameworks.governance.production_guard import (
            ProductionGuard,
            ProductionViolationError,
        )
        
        guard = ProductionGuard.for_testing(force_production=True)
        
        # LIVE mode should pass
        guard.enforce_mode(ExecutionMode.LIVE)
        
        # TEST mode should fail
        with pytest.raises(ProductionViolationError) as exc_info:
            guard.enforce_mode(ExecutionMode.TEST)
        
        assert "TEST" in str(exc_info.value)
        assert "production" in str(exc_info.value).lower()
    
    def test_enforce_allows_all_modes_in_development(self) -> None:
        """ProductionGuard.enforce() allows all modes in development."""
        from krl_frameworks.governance.production_guard import ProductionGuard
        
        guard = ProductionGuard.for_testing(force_production=False)
        
        # All modes should pass in development
        guard.enforce_mode(ExecutionMode.LIVE)
        guard.enforce_mode(ExecutionMode.TEST)
        guard.enforce_mode(ExecutionMode.DEBUG)
    
    def test_is_production_helper(self) -> None:
        """is_production() returns correct boolean."""
        from krl_frameworks.governance.production_guard import is_production
        
        with patch.dict(os.environ, {"PRODUCTION": "true"}, clear=True):
            assert is_production() is True
        
        with patch.dict(os.environ, {}, clear=True):
            assert is_production() is False


# ════════════════════════════════════════════════════════════════════════════════
# ConnectorFactoryRegistry Tests
# ════════════════════════════════════════════════════════════════════════════════


class TestConnectorFactoryRegistry:
    """Tests for ConnectorFactoryRegistry."""
    
    def test_register_and_retrieve_factory(self) -> None:
        """Basic factory registration and retrieval."""
        from krl_frameworks.governance.connector_registry import (
            ConnectorFactoryRegistry,
        )
        
        registry = ConnectorFactoryRegistry()
        
        # Create a mock factory function
        def mock_factory(config: dict) -> object:
            return type("MockConnector", (), {"config": config})()
        
        registry.register(
            connector_type="test_connector",
            factory_fn=mock_factory,
            min_tier="community",
            domains=["test"],
        )
        
        factory = registry.get_factory("test_connector", user_tier="community")
        assert factory.connector_type == "test_connector"
        
        connector = factory.create({"key": "value"})
        assert connector.config == {"key": "value"}
    
    def test_tier_access_denied(self) -> None:
        """Access denied when user tier insufficient."""
        from krl_frameworks.governance.connector_registry import (
            ConnectorFactoryRegistry,
            TierAccessDeniedError,
        )
        
        registry = ConnectorFactoryRegistry()
        
        def mock_factory(config: dict) -> object:
            return object()
        
        registry.register(
            connector_type="enterprise_connector",
            factory_fn=mock_factory,
            min_tier="enterprise",
        )
        
        with pytest.raises(TierAccessDeniedError) as exc_info:
            registry.get_factory("enterprise_connector", user_tier="community")
        
        assert exc_info.value.required_tier == "enterprise"
        assert exc_info.value.user_tier == "community"
    
    def test_connector_not_found(self) -> None:
        """ConnectorNotFoundError raised for unknown connector."""
        from krl_frameworks.governance.connector_registry import (
            ConnectorFactoryRegistry,
            ConnectorNotFoundError,
        )
        
        registry = ConnectorFactoryRegistry()
        
        with pytest.raises(ConnectorNotFoundError) as exc_info:
            registry.get_factory("nonexistent", user_tier="enterprise")
        
        assert "nonexistent" in str(exc_info.value)
    
    def test_domain_based_lookup(self) -> None:
        """get_factory_for_domain returns appropriate connector."""
        from krl_frameworks.governance.connector_registry import (
            ConnectorFactoryRegistry,
        )
        
        registry = ConnectorFactoryRegistry()
        
        def health_factory(config: dict) -> object:
            return type("HealthConnector", (), {"domain": "health"})()
        
        registry.register(
            connector_type="health_connector",
            factory_fn=health_factory,
            min_tier="community",
            domains=["health", "demographic"],
        )
        
        factory = registry.get_factory_for_domain("health", user_tier="community")
        assert factory is not None
        assert factory.connector_type == "health_connector"
        
        # Unknown domain returns None
        factory = registry.get_factory_for_domain("unknown", user_tier="community")
        assert factory is None
    
    def test_list_connectors_with_tier_filter(self) -> None:
        """list_connectors respects tier filter."""
        from krl_frameworks.governance.connector_registry import (
            ConnectorFactoryRegistry,
        )
        
        registry = ConnectorFactoryRegistry()
        
        registry.register("community_conn", lambda c: None, min_tier="community")
        registry.register("pro_conn", lambda c: None, min_tier="professional")
        registry.register("enterprise_conn", lambda c: None, min_tier="enterprise")
        
        # Community sees only community
        community_list = registry.list_connectors(user_tier="community")
        assert "community_conn" in community_list
        assert "pro_conn" not in community_list
        
        # Enterprise sees all
        enterprise_list = registry.list_connectors(user_tier="enterprise")
        assert len(enterprise_list) == 3


# ════════════════════════════════════════════════════════════════════════════════
# BindingResolver Tests
# ════════════════════════════════════════════════════════════════════════════════


class TestBindingResolver:
    """Tests for BindingResolver."""
    
    def test_resolve_with_registered_factory(self) -> None:
        """Resolver uses registered factories."""
        from krl_frameworks.governance.binding_resolver import BindingResolver
        from krl_frameworks.governance.connector_registry import (
            ConnectorFactoryRegistry,
        )
        
        # Create registry with test factory
        registry = ConnectorFactoryRegistry()
        
        class TestConnector:
            def fetch(self, **kwargs):
                import pandas as pd
                return pd.DataFrame()
        
        registry.register(
            connector_type="test_source",
            factory_fn=lambda c: TestConnector(),
            min_tier="community",
            domains=["test"],
        )
        
        resolver = BindingResolver(connector_registry=registry)
        
        capabilities = CapabilityDeclaration(
            connectors=[
                ConnectorRequirement(
                    connector_type="test_source",
                    scope=CapabilityScope.REQUIRED,
                    domains=["test"],
                ),
            ],
        )
        
        result = resolver.resolve(
            capabilities=capabilities,
            user_tier="community",
            mode=ExecutionMode.TEST,
        )
        
        assert result.success
        assert "test_source" in result.resolved
        assert "test_source" in result.bindings.connectors
    
    def test_resolve_fails_live_mode_missing_required(self) -> None:
        """LIVE mode raises on missing REQUIRED capability."""
        from krl_frameworks.governance.binding_resolver import (
            BindingResolver,
            BindingResolutionError,
        )
        from krl_frameworks.governance.connector_registry import (
            ConnectorFactoryRegistry,
        )
        
        registry = ConnectorFactoryRegistry()  # Empty registry
        resolver = BindingResolver(connector_registry=registry)
        
        capabilities = CapabilityDeclaration(
            connectors=[
                ConnectorRequirement(
                    connector_type="missing_connector",
                    scope=CapabilityScope.REQUIRED,
                    domains=["health"],
                ),
            ],
        )
        
        with pytest.raises(BindingResolutionError) as exc_info:
            resolver.resolve(
                capabilities=capabilities,
                user_tier="community",
                mode=ExecutionMode.LIVE,
            )
        
        assert len(exc_info.value.failures) == 1
        assert exc_info.value.failures[0].is_fatal
    
    def test_resolve_warns_test_mode_missing_optional(self) -> None:
        """TEST mode logs warning for missing OPTIONAL."""
        from krl_frameworks.governance.binding_resolver import BindingResolver
        from krl_frameworks.governance.connector_registry import (
            ConnectorFactoryRegistry,
        )
        
        registry = ConnectorFactoryRegistry()
        resolver = BindingResolver(connector_registry=registry)
        
        capabilities = CapabilityDeclaration(
            connectors=[
                ConnectorRequirement(
                    connector_type="optional_connector",
                    scope=CapabilityScope.OPTIONAL,
                    domains=["extra"],
                ),
            ],
        )
        
        result = resolver.resolve(
            capabilities=capabilities,
            user_tier="community",
            mode=ExecutionMode.TEST,
        )
        
        # Should succeed (optional)
        assert result.success
        assert len(result.failures) == 1
        assert not result.failures[0].is_fatal
        assert len(result.warnings) >= 1
    
    def test_explicit_bindings_not_overwritten(self) -> None:
        """Existing bindings are preserved, not overwritten."""
        from krl_frameworks.governance.binding_resolver import BindingResolver
        from krl_frameworks.governance.connector_registry import (
            ConnectorFactoryRegistry,
        )
        from krl_frameworks.core.bindings import ConnectorBinding
        
        registry = ConnectorFactoryRegistry()
        
        class NewConnector:
            def fetch(self, **kwargs):
                import pandas as pd
                return pd.DataFrame()
        
        registry.register(
            connector_type="test_conn",
            factory_fn=lambda c: NewConnector(),
            min_tier="community",
        )
        
        resolver = BindingResolver(connector_registry=registry)
        
        # Pre-existing binding
        class ExistingConnector:
            pass
        
        existing = BindingRegistry()
        existing.bind_connector(
            "test_conn",
            ConnectorBinding(name="test_conn", connector=ExistingConnector()),
        )
        
        capabilities = CapabilityDeclaration(
            connectors=[
                ConnectorRequirement(
                    connector_type="test_conn",
                    scope=CapabilityScope.REQUIRED,
                ),
            ],
        )
        
        result = resolver.resolve(
            capabilities=capabilities,
            user_tier="community",
            mode=ExecutionMode.TEST,
            existing_bindings=existing,
        )
        
        # Should skip, not replace
        assert "test_conn" in result.skipped
        assert "test_conn" not in result.resolved
        
        # Original binding preserved
        assert isinstance(
            result.bindings.connectors["test_conn"].connector,
            ExistingConnector,
        )


# ════════════════════════════════════════════════════════════════════════════════
# AuditLogger Tests
# ════════════════════════════════════════════════════════════════════════════════


class TestAuditLogger:
    """Tests for AuditLogger."""
    
    def test_emit_json_event(self) -> None:
        """Events are emitted as valid JSON."""
        from krl_frameworks.governance.audit import AuditLogger
        
        output = io.StringIO()
        logger = AuditLogger(output=output)
        
        logger.log_resolution_success(
            framework_name="TestFramework",
            resolved=["connector_a", "connector_b"],
            user_tier="professional",
            execution_mode="LIVE",
        )
        
        output.seek(0)
        line = output.readline()
        
        event = json.loads(line)
        assert event["event_type"] == "resolution.success"
        assert event["framework_name"] == "TestFramework"
        assert event["details"]["resolved_count"] == 2
    
    def test_correlation_id_propagation(self) -> None:
        """Correlation ID added to all events."""
        from krl_frameworks.governance.audit import AuditLogger
        
        output = io.StringIO()
        logger = AuditLogger(output=output)
        
        logger.set_correlation_id("test-correlation-123")
        
        logger.log_resolution_start(
            framework_name="Test",
            user_tier="community",
            execution_mode="TEST",
            capabilities_count=3,
        )
        
        output.seek(0)
        event = json.loads(output.readline())
        
        assert event["correlation_id"] == "test-correlation-123"
    
    def test_production_violation_logging(self) -> None:
        """Production violations logged with appropriate event type."""
        from krl_frameworks.governance.audit import AuditLogger
        
        output = io.StringIO()
        logger = AuditLogger(output=output)
        
        logger.log_production_violation(
            attempted_mode="TEST",
            framework_name="MyFramework",
        )
        
        output.seek(0)
        event = json.loads(output.readline())
        
        assert event["event_type"] == "production.violation"
        assert event["execution_mode"] == "TEST"


# ════════════════════════════════════════════════════════════════════════════════
# ClosureValidator Tests
# ════════════════════════════════════════════════════════════════════════════════


class TestClosureValidator:
    """Tests for ClosureValidator."""
    
    def test_compute_closure_single_framework(self) -> None:
        """Closure of single framework equals its capabilities."""
        from krl_frameworks.governance.closure_validator import ClosureValidator
        
        validator = ClosureValidator()
        
        # Create a mock framework class
        class MockFramework:
            CAPABILITIES = CapabilityDeclaration(
                connectors=[
                    ConnectorRequirement("health", CapabilityScope.REQUIRED, ["health"]),
                    ConnectorRequirement("education", CapabilityScope.REQUIRED, ["education"]),
                ],
            )
        
        closure = validator.compute_closure([MockFramework])
        
        assert len(closure.frameworks) == 1
        assert "MockFramework" in closure.frameworks
        assert len(closure.connectors) == 2
        assert not closure.has_conflicts
    
    def test_compute_closure_merges_requirements(self) -> None:
        """Closure merges requirements from multiple frameworks."""
        from krl_frameworks.governance.closure_validator import ClosureValidator
        
        validator = ClosureValidator()
        
        class FrameworkA:
            CAPABILITIES = CapabilityDeclaration(
                connectors=[
                    ConnectorRequirement("health", CapabilityScope.REQUIRED),
                ],
            )
        
        class FrameworkB:
            CAPABILITIES = CapabilityDeclaration(
                connectors=[
                    ConnectorRequirement("education", CapabilityScope.REQUIRED),
                ],
            )
        
        closure = validator.compute_closure([FrameworkA, FrameworkB])
        
        assert len(closure.frameworks) == 2
        assert len(closure.connectors) == 2
        assert "health" in closure.connectors
        assert "education" in closure.connectors
    
    def test_detects_version_conflict(self) -> None:
        """Version conflicts detected between frameworks."""
        from krl_frameworks.governance.closure_validator import ClosureValidator
        
        validator = ClosureValidator()
        
        class FrameworkA:
            CAPABILITIES = CapabilityDeclaration(
                connectors=[
                    ConnectorRequirement(
                        "shared",
                        CapabilityScope.REQUIRED,
                        version="1.0.0",
                    ),
                ],
            )
        
        class FrameworkB:
            CAPABILITIES = CapabilityDeclaration(
                connectors=[
                    ConnectorRequirement(
                        "shared",
                        CapabilityScope.REQUIRED,
                        version="2.0.0",
                    ),
                ],
            )
        
        closure = validator.compute_closure([FrameworkA, FrameworkB])
        
        assert closure.has_conflicts
        assert len(closure.conflicts) == 1
        assert closure.conflicts[0].conflict_type == "version"
    
    def test_validate_raises_on_conflict(self) -> None:
        """validate() raises ClosureValidationError on conflicts."""
        from krl_frameworks.governance.closure_validator import (
            ClosureValidator,
            ClosureValidationError,
            CapabilityClosure,
            ClosureConflict,
        )
        
        validator = ClosureValidator()
        
        closure = CapabilityClosure(
            frameworks=["A", "B"],
            conflicts=[
                ClosureConflict(
                    requirement_name="shared",
                    framework_a="A",
                    framework_b="B",
                    conflict_type="version",
                    message="Version conflict",
                ),
            ],
        )
        
        with pytest.raises(ClosureValidationError) as exc_info:
            validator.validate(closure, user_tier="community")
        
        assert len(exc_info.value.conflicts) == 1
    
    def test_scope_upgrade_to_required(self) -> None:
        """REQUIRED scope wins over OPTIONAL when merging."""
        from krl_frameworks.governance.closure_validator import ClosureValidator
        
        validator = ClosureValidator()
        
        class FrameworkA:
            CAPABILITIES = CapabilityDeclaration(
                connectors=[
                    ConnectorRequirement("shared", CapabilityScope.OPTIONAL),
                ],
            )
        
        class FrameworkB:
            CAPABILITIES = CapabilityDeclaration(
                connectors=[
                    ConnectorRequirement("shared", CapabilityScope.REQUIRED),
                ],
            )
        
        closure = validator.compute_closure([FrameworkA, FrameworkB])
        
        # Should be REQUIRED (stricter wins)
        assert closure.connectors["shared"].scope == CapabilityScope.REQUIRED


# ════════════════════════════════════════════════════════════════════════════════
# Integration Tests
# ════════════════════════════════════════════════════════════════════════════════


class TestGovernanceIntegration:
    """End-to-end governance integration tests."""
    
    def test_full_resolution_flow(self) -> None:
        """Complete flow: capabilities → resolver → bindings."""
        from krl_frameworks.governance.binding_resolver import BindingResolver
        from krl_frameworks.governance.connector_registry import (
            ConnectorFactoryRegistry,
        )
        from krl_frameworks.governance.audit import AuditLogger
        
        # Setup
        output = io.StringIO()
        audit = AuditLogger(output=output)
        registry = ConnectorFactoryRegistry()
        
        class HealthConnector:
            def fetch(self, **kwargs):
                import pandas as pd
                return pd.DataFrame({"health": [1, 2, 3]})
        
        registry.register(
            connector_type="health_source",
            factory_fn=lambda c: HealthConnector(),
            min_tier="community",
            domains=["health"],
        )
        
        resolver = BindingResolver(connector_registry=registry)
        
        capabilities = CapabilityDeclaration(
            connectors=[
                ConnectorRequirement(
                    connector_type="health_source",
                    scope=CapabilityScope.REQUIRED,
                    domains=["health"],
                ),
            ],
        )
        
        # Execute
        result = resolver.resolve(
            capabilities=capabilities,
            user_tier="community",
            mode=ExecutionMode.LIVE,
        )
        
        # Verify
        assert result.success
        assert "health_source" in result.bindings.connectors
        
        # Verify connector works
        connector = result.bindings.connectors["health_source"].connector
        df = connector.fetch()
        assert len(df) == 3
