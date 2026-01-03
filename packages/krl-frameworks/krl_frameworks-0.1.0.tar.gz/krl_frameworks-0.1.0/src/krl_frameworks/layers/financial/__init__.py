# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Layer 4: Financial / Economic Frameworks
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Layer 4: Financial and Economic Regulatory Frameworks.

This module provides frameworks for financial risk assessment,
regulatory compliance, and economic stress testing.

Community Tier:
    - RiskIndicesFramework: Composite financial risk indices

Professional Tier:
    - MacroFinancialCGEFramework: Macro-finance with CGE integration
    - NetworkedFinancialFramework: Financial network contagion
    - CompositeRiskFramework: Aggregated risk/solvency scoring
    - LiquidityRiskFramework: LCR/NSFR liquidity risk assessment
    - HANKFramework: Heterogeneous Agent New Keynesian model
    - DSGEFramework: Dynamic Stochastic General Equilibrium

Enterprise Tier:
    - BaselIIIFramework: Basel III capital adequacy and liquidity
    - CECLFramework: Current Expected Credit Losses (CECL)
    - StressTestFramework: CCAR/DFAST stress testing
    - FinancialMetaOrchestratorFramework: Cross-model orchestration
"""

from krl_frameworks.layers.financial.basel_iii import BaselIIIFramework
from krl_frameworks.layers.financial.cecl import CECLFramework
from krl_frameworks.layers.financial.stress_test import StressTestFramework
from krl_frameworks.layers.financial.liquidity_risk import LiquidityRiskFramework
from krl_frameworks.layers.financial.systemic_risk import SystemicRiskFramework
from krl_frameworks.layers.financial.credit_risk import CreditRiskFramework
from krl_frameworks.layers.financial.market_risk import MarketRiskFramework
from krl_frameworks.layers.financial.hank import HANKFramework
from krl_frameworks.layers.financial.dsge import DSGEFramework
from krl_frameworks.layers.financial.advanced import (
    MacroFinancialCGEFramework,
    NetworkedFinancialFramework,
    RiskIndicesFramework,
    CompositeRiskFramework,
    FinancialMetaOrchestratorFramework,
)

__all__ = [
    "BaselIIIFramework",
    "CECLFramework",
    "StressTestFramework",
    "LiquidityRiskFramework",
    "SystemicRiskFramework",
    "CreditRiskFramework",
    "MarketRiskFramework",
    "HANKFramework",
    "DSGEFramework",
    "MacroFinancialCGEFramework",
    "NetworkedFinancialFramework",
    "RiskIndicesFramework",
    "CompositeRiskFramework",
    "FinancialMetaOrchestratorFramework",
]
