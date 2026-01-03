# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Tests for Framework Security Module
"""

import pytest
from krl_frameworks.security import (
    # Validation
    validate_parameter_schema,
    sanitize_parameters,
    sanitize_string_parameter,
    ValidationResult,
    # Circuit Breaker
    CircuitBreaker,
    CircuitState,
    get_circuit_breaker,
    # Fingerprinting
    compute_request_fingerprint,
    validate_fingerprint_consistency,
    # Tier Enforcement
    tier_allows_access,
    validate_framework_tier_access,
    TIER_HIERARCHY,
    # Audit
    SecurityAuditEvent,
    hash_parameters,
)


# =============================================================================
# PARAMETER VALIDATION TESTS
# =============================================================================

class TestParameterValidation:
    """Tests for parameter validation against JSON Schema."""
    
    def test_valid_parameters(self):
        """Test validation passes for valid parameters."""
        schema = {
            "type": "object",
            "properties": {
                "rate": {"type": "number", "minimum": 0, "maximum": 1},
                "name": {"type": "string"},
            },
            "required": ["rate"],
        }
        parameters = {"rate": 0.5, "name": "test"}
        
        result = validate_parameter_schema(parameters, schema)
        assert result.valid
        assert len(result.errors) == 0
    
    def test_missing_required_parameter(self):
        """Test validation fails for missing required parameter."""
        schema = {
            "type": "object",
            "properties": {
                "rate": {"type": "number"},
            },
            "required": ["rate"],
        }
        parameters = {}
        
        result = validate_parameter_schema(parameters, schema)
        assert not result.valid
        assert any("required" in e.lower() for e in result.errors)
    
    def test_wrong_type_parameter(self):
        """Test validation fails for wrong type."""
        schema = {
            "type": "object",
            "properties": {
                "rate": {"type": "number"},
            },
        }
        parameters = {"rate": "not a number"}
        
        result = validate_parameter_schema(parameters, schema)
        assert not result.valid
    
    def test_value_out_of_range(self):
        """Test validation fails for value outside allowed range."""
        schema = {
            "type": "object",
            "properties": {
                "rate": {"type": "number", "minimum": 0, "maximum": 1},
            },
        }
        parameters = {"rate": 1.5}
        
        result = validate_parameter_schema(parameters, schema)
        assert not result.valid


class TestParameterSanitization:
    """Tests for parameter sanitization."""
    
    def test_sanitize_normal_string(self):
        """Test normal strings pass through."""
        result = sanitize_string_parameter("Hello, World!")
        assert result == "Hello, World!"
    
    def test_sanitize_removes_null_bytes(self):
        """Test null bytes are removed."""
        result = sanitize_string_parameter("Hello\x00World")
        assert result == "HelloWorld"
    
    def test_sanitize_preserves_newlines(self):
        """Test newlines are preserved."""
        result = sanitize_string_parameter("Line1\nLine2")
        assert result == "Line1\nLine2"
    
    def test_rejects_dangerous_patterns(self):
        """Test dangerous patterns are rejected."""
        with pytest.raises(ValueError, match="Dangerous pattern"):
            sanitize_string_parameter("eval(user_input)")
        
        with pytest.raises(ValueError, match="Dangerous pattern"):
            sanitize_string_parameter("__import__('os')")
        
        with pytest.raises(ValueError, match="Dangerous pattern"):
            sanitize_string_parameter("<script>alert('xss')</script>")
    
    def test_sanitize_nested_dict(self):
        """Test nested dictionaries are sanitized."""
        params = {
            "outer": {
                "inner": "value",
                "number": 42,
            },
            "list": ["a", "b", "c"],
        }
        
        result = sanitize_parameters(params)
        assert result["outer"]["inner"] == "value"
        assert result["outer"]["number"] == 42
        assert result["list"] == ["a", "b", "c"]
    
    def test_rejects_too_deep_nesting(self):
        """Test excessively nested objects are rejected."""
        deep = {"level": None}
        current = deep
        for i in range(15):  # Exceed MAX_OBJECT_DEPTH (10)
            current["level"] = {"level": None}
            current = current["level"]
        
        with pytest.raises(ValueError, match="maximum depth"):
            sanitize_parameters(deep)


# =============================================================================
# CIRCUIT BREAKER TESTS
# =============================================================================

class TestCircuitBreaker:
    """Tests for circuit breaker functionality."""
    
    def test_initial_state_closed(self):
        """Test circuit breaker starts closed."""
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED
        assert cb.can_execute()
    
    def test_opens_after_threshold_failures(self):
        """Test circuit opens after threshold failures."""
        cb = CircuitBreaker()
        
        for _ in range(5):  # CIRCUIT_OPEN_THRESHOLD
            cb.record_failure()
        
        assert cb.state == CircuitState.OPEN
        assert not cb.can_execute()
    
    def test_success_decrements_failure_count(self):
        """Test successful execution reduces failure count."""
        cb = CircuitBreaker()
        cb.failure_count = 3
        
        cb.record_success()
        assert cb.failure_count == 2
    
    def test_half_open_recovers_after_successes(self):
        """Test circuit recovers after successes in half-open state."""
        cb = CircuitBreaker()
        cb.state = CircuitState.HALF_OPEN
        
        cb.record_success()
        cb.record_success()
        cb.record_success()
        
        assert cb.state == CircuitState.CLOSED


class TestCircuitBreakerRegistry:
    """Tests for circuit breaker registry."""
    
    def test_get_circuit_breaker_creates_new(self):
        """Test getting circuit breaker creates new if not exists."""
        cb = get_circuit_breaker("test-framework-unique")
        assert isinstance(cb, CircuitBreaker)
        assert cb.state == CircuitState.CLOSED
    
    def test_get_circuit_breaker_returns_same(self):
        """Test getting circuit breaker returns same instance."""
        cb1 = get_circuit_breaker("test-framework-same")
        cb2 = get_circuit_breaker("test-framework-same")
        assert cb1 is cb2


# =============================================================================
# FINGERPRINTING TESTS
# =============================================================================

class TestFingerprinting:
    """Tests for request fingerprinting."""
    
    def test_compute_fingerprint(self):
        """Test fingerprint computation produces consistent hash."""
        fp1 = compute_request_fingerprint(
            user_agent="Mozilla/5.0",
            accept_language="en-US",
            accept_encoding="gzip",
            client_ip="1.2.3.4",
        )
        
        fp2 = compute_request_fingerprint(
            user_agent="Mozilla/5.0",
            accept_language="en-US",
            accept_encoding="gzip",
            client_ip="1.2.3.4",
        )
        
        assert fp1 == fp2
        assert len(fp1) == 32  # Truncated SHA-256
    
    def test_different_user_agent_different_fingerprint(self):
        """Test different user agents produce different fingerprints."""
        fp1 = compute_request_fingerprint(
            user_agent="Mozilla/5.0",
            accept_language="en-US",
            accept_encoding="gzip",
            client_ip="1.2.3.4",
        )
        
        fp2 = compute_request_fingerprint(
            user_agent="Chrome/120",
            accept_language="en-US",
            accept_encoding="gzip",
            client_ip="1.2.3.4",
        )
        
        assert fp1 != fp2
    
    def test_validate_fingerprint_consistency(self):
        """Test fingerprint consistency validation."""
        current = "abc123"
        
        assert validate_fingerprint_consistency(current, None)  # No session fingerprint
        assert validate_fingerprint_consistency(current, current)  # Match
        assert not validate_fingerprint_consistency(current, "different")  # No match


# =============================================================================
# TIER ENFORCEMENT TESTS
# =============================================================================

class TestTierEnforcement:
    """Tests for tier-based access control."""
    
    def test_tier_hierarchy(self):
        """Test tier hierarchy is correct."""
        assert TIER_HIERARCHY == ["community", "professional", "team", "enterprise"]
    
    def test_same_tier_allows_access(self):
        """Test same tier allows access."""
        assert tier_allows_access("professional", "professional")
    
    def test_higher_tier_allows_access(self):
        """Test higher tier allows access to lower tier resource."""
        assert tier_allows_access("enterprise", "community")
        assert tier_allows_access("enterprise", "professional")
        assert tier_allows_access("enterprise", "team")
    
    def test_lower_tier_denies_access(self):
        """Test lower tier denies access to higher tier resource."""
        assert not tier_allows_access("community", "professional")
        assert not tier_allows_access("community", "enterprise")
        assert not tier_allows_access("professional", "enterprise")
    
    def test_validate_framework_tier_access_allowed(self):
        """Test framework access validation when allowed."""
        allowed, error = validate_framework_tier_access(
            framework_slug="test-framework",
            framework_min_tier="professional",
            user_tier="enterprise",
        )
        assert allowed
        assert error is None
    
    def test_validate_framework_tier_access_denied(self):
        """Test framework access validation when denied."""
        allowed, error = validate_framework_tier_access(
            framework_slug="test-framework",
            framework_min_tier="enterprise",
            user_tier="professional",
        )
        assert not allowed
        assert "requires ENTERPRISE tier" in error
        assert "Your tier: PROFESSIONAL" in error


# =============================================================================
# AUDIT TESTS
# =============================================================================

class TestSecurityAudit:
    """Tests for security audit functionality."""
    
    def test_security_audit_event_creation(self):
        """Test SecurityAuditEvent creation."""
        event = SecurityAuditEvent(
            event_type="framework_execution",
            framework_slug="mpi",
            user_id="user-123",
            user_tier="professional",
            client_ip="1.2.3.4",
            success=True,
        )
        
        assert event.event_type == "framework_execution"
        assert event.framework_slug == "mpi"
        assert event.success
        assert event.timestamp is not None
    
    def test_security_audit_event_to_dict(self):
        """Test SecurityAuditEvent serialization."""
        event = SecurityAuditEvent(
            event_type="tier_violation",
            framework_slug="enterprise-framework",
            user_id="user-456",
            user_tier="community",
            client_ip="5.6.7.8",
            success=False,
            error_message="Tier access denied",
        )
        
        d = event.to_dict()
        assert d["event_type"] == "tier_violation"
        assert d["success"] is False
        assert d["error_message"] == "Tier access denied"
    
    def test_hash_parameters(self):
        """Test parameter hashing for audit."""
        params1 = {"rate": 0.5, "name": "test"}
        params2 = {"rate": 0.5, "name": "test"}
        params3 = {"rate": 0.6, "name": "test"}
        
        hash1 = hash_parameters(params1)
        hash2 = hash_parameters(params2)
        hash3 = hash_parameters(params3)
        
        assert hash1 == hash2  # Same parameters = same hash
        assert hash1 != hash3  # Different parameters = different hash
        assert len(hash1) == 16  # Truncated
