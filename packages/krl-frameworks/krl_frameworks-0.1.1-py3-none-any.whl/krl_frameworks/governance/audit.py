# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Audit Logger
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Structured Audit Logging for Runtime Governance.

All governance events are logged as structured JSON for:
    - Compliance auditing
    - Debugging resolution failures
    - Performance monitoring
    - Security event tracking
"""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, TextIO

__all__ = [
    "AuditEventType",
    "AuditEvent",
    "AuditLogger",
    "get_audit_logger",
]


class AuditEventType(str, Enum):
    """Types of audit events."""
    
    # Resolution events
    RESOLUTION_START = "resolution.start"
    RESOLUTION_SUCCESS = "resolution.success"
    RESOLUTION_FAILURE = "resolution.failure"
    RESOLUTION_SKIP = "resolution.skip"
    
    # Capability events
    CAPABILITY_VALIDATED = "capability.validated"
    CAPABILITY_VIOLATION = "capability.violation"
    
    # Production guard events
    PRODUCTION_MODE_ENFORCED = "production.mode_enforced"
    PRODUCTION_VIOLATION = "production.violation"
    
    # Tier access events
    TIER_ACCESS_GRANTED = "tier.access_granted"
    TIER_ACCESS_DENIED = "tier.access_denied"
    
    # Framework lifecycle events
    FRAMEWORK_INIT = "framework.init"
    FRAMEWORK_FIT_START = "framework.fit.start"
    FRAMEWORK_FIT_COMPLETE = "framework.fit.complete"
    FRAMEWORK_FIT_FAILURE = "framework.fit.failure"


@dataclass
class AuditEvent:
    """
    A single audit event.
    
    Attributes:
        event_type: Type of event.
        timestamp: ISO 8601 timestamp.
        framework_name: Name of the framework (if applicable).
        user_tier: User's subscription tier.
        execution_mode: Execution mode (LIVE/TEST/DEBUG).
        details: Event-specific details.
        correlation_id: ID for correlating related events.
    """
    event_type: AuditEventType
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    framework_name: str | None = None
    user_tier: str | None = None
    execution_mode: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        data = {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "framework_name": self.framework_name,
            "user_tier": self.user_tier,
            "execution_mode": self.execution_mode,
            "details": self.details,
            "correlation_id": self.correlation_id,
        }
        return json.dumps(data, default=str)


class AuditLogger:
    """
    Structured audit logger for governance events.
    
    Writes events as JSON lines to the configured output.
    
    Example:
        >>> logger = AuditLogger()
        >>> logger.log_resolution_success(
        ...     framework_name="MPIFramework",
        ...     resolved=["fred", "census"],
        ...     user_tier="professional",
        ... )
    """
    
    def __init__(
        self,
        output: TextIO | None = None,
        python_logger: logging.Logger | None = None,
    ) -> None:
        """
        Initialize audit logger.
        
        Args:
            output: File-like object for JSON output.
            python_logger: Standard Python logger for events.
        """
        self._output = output or sys.stderr
        self._python_logger = python_logger or logging.getLogger("krl.governance.audit")
        self._correlation_id: str | None = None
    
    def set_correlation_id(self, correlation_id: str) -> None:
        """Set correlation ID for subsequent events."""
        self._correlation_id = correlation_id
    
    def clear_correlation_id(self) -> None:
        """Clear correlation ID."""
        self._correlation_id = None
    
    def _emit(self, event: AuditEvent) -> None:
        """Emit an audit event."""
        if self._correlation_id:
            event.correlation_id = self._correlation_id
        
        # Write JSON line
        json_line = event.to_json()
        self._output.write(json_line + "\n")
        self._output.flush()
        
        # Also log to Python logger
        self._python_logger.info(
            "%s: %s",
            event.event_type.value,
            event.details.get("message", json.dumps(event.details)),
        )
    
    # ────────────────────────────────────────────────────────────────────────────
    # Resolution Events
    # ────────────────────────────────────────────────────────────────────────────
    
    def log_resolution_start(
        self,
        framework_name: str,
        user_tier: str,
        execution_mode: str,
        capabilities_count: int,
    ) -> None:
        """Log resolution start."""
        self._emit(AuditEvent(
            event_type=AuditEventType.RESOLUTION_START,
            framework_name=framework_name,
            user_tier=user_tier,
            execution_mode=execution_mode,
            details={
                "message": f"Starting resolution for {framework_name}",
                "capabilities_count": capabilities_count,
            },
        ))
    
    def log_resolution_success(
        self,
        framework_name: str,
        resolved: list[str],
        user_tier: str,
        execution_mode: str,
        warnings: list[str] | None = None,
    ) -> None:
        """Log successful resolution."""
        self._emit(AuditEvent(
            event_type=AuditEventType.RESOLUTION_SUCCESS,
            framework_name=framework_name,
            user_tier=user_tier,
            execution_mode=execution_mode,
            details={
                "message": f"Resolution succeeded for {framework_name}",
                "resolved": resolved,
                "resolved_count": len(resolved),
                "warnings": warnings or [],
            },
        ))
    
    def log_resolution_failure(
        self,
        framework_name: str,
        failures: list[dict[str, Any]],
        user_tier: str,
        execution_mode: str,
    ) -> None:
        """Log resolution failure."""
        self._emit(AuditEvent(
            event_type=AuditEventType.RESOLUTION_FAILURE,
            framework_name=framework_name,
            user_tier=user_tier,
            execution_mode=execution_mode,
            details={
                "message": f"Resolution failed for {framework_name}",
                "failures": failures,
                "failure_count": len(failures),
            },
        ))
    
    # ────────────────────────────────────────────────────────────────────────────
    # Production Guard Events
    # ────────────────────────────────────────────────────────────────────────────
    
    def log_production_violation(
        self,
        attempted_mode: str,
        framework_name: str | None = None,
    ) -> None:
        """Log production mode violation."""
        self._emit(AuditEvent(
            event_type=AuditEventType.PRODUCTION_VIOLATION,
            framework_name=framework_name,
            execution_mode=attempted_mode,
            details={
                "message": f"Production violation: attempted {attempted_mode} mode",
                "attempted_mode": attempted_mode,
            },
        ))
    
    # ────────────────────────────────────────────────────────────────────────────
    # Tier Access Events
    # ────────────────────────────────────────────────────────────────────────────
    
    def log_tier_access_denied(
        self,
        connector_type: str,
        user_tier: str,
        required_tier: str,
    ) -> None:
        """Log tier access denial."""
        self._emit(AuditEvent(
            event_type=AuditEventType.TIER_ACCESS_DENIED,
            user_tier=user_tier,
            details={
                "message": f"Tier access denied for {connector_type}",
                "connector_type": connector_type,
                "required_tier": required_tier,
            },
        ))
    
    # ────────────────────────────────────────────────────────────────────────────
    # Framework Lifecycle Events
    # ────────────────────────────────────────────────────────────────────────────
    
    def log_framework_init(
        self,
        framework_name: str,
        user_tier: str | None = None,
        execution_mode: str | None = None,
    ) -> None:
        """Log framework initialization."""
        self._emit(AuditEvent(
            event_type=AuditEventType.FRAMEWORK_INIT,
            framework_name=framework_name,
            user_tier=user_tier,
            execution_mode=execution_mode,
            details={
                "message": f"Framework {framework_name} initialized",
            },
        ))
    
    def log_framework_fit_start(
        self,
        framework_name: str,
        user_tier: str,
        execution_mode: str,
        data_sources: list[str] | None = None,
    ) -> None:
        """Log framework fit start."""
        self._emit(AuditEvent(
            event_type=AuditEventType.FRAMEWORK_FIT_START,
            framework_name=framework_name,
            user_tier=user_tier,
            execution_mode=execution_mode,
            details={
                "message": f"Framework {framework_name} fit started",
                "data_sources": data_sources or [],
            },
        ))
    
    def log_framework_fit_complete(
        self,
        framework_name: str,
        user_tier: str,
        execution_mode: str,
        duration_seconds: float | None = None,
    ) -> None:
        """Log framework fit completion."""
        self._emit(AuditEvent(
            event_type=AuditEventType.FRAMEWORK_FIT_COMPLETE,
            framework_name=framework_name,
            user_tier=user_tier,
            execution_mode=execution_mode,
            details={
                "message": f"Framework {framework_name} fit completed",
                "duration_seconds": duration_seconds,
            },
        ))
    
    def log_framework_fit_failure(
        self,
        framework_name: str,
        user_tier: str,
        execution_mode: str,
        error: str,
        error_type: str | None = None,
    ) -> None:
        """Log framework fit failure."""
        self._emit(AuditEvent(
            event_type=AuditEventType.FRAMEWORK_FIT_FAILURE,
            framework_name=framework_name,
            user_tier=user_tier,
            execution_mode=execution_mode,
            details={
                "message": f"Framework {framework_name} fit failed: {error}",
                "error": error,
                "error_type": error_type,
            },
        ))


# ════════════════════════════════════════════════════════════════════════════════
# Global Logger
# ════════════════════════════════════════════════════════════════════════════════

_global_audit_logger: AuditLogger | None = None


def get_audit_logger() -> AuditLogger:
    """Get the global audit logger."""
    global _global_audit_logger
    if _global_audit_logger is None:
        _global_audit_logger = AuditLogger()
    return _global_audit_logger
