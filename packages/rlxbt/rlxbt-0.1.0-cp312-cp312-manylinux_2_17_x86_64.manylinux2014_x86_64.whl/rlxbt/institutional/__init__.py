"""
RLX Institutional SDK

High-level institutional trading framework built on top of RLX core engine.
Designed for hedge funds, asset managers, and institutional traders.

Features:
- Multi-strategy portfolio management
- Advanced risk management and limits
- Parameter optimization and walk-forward analysis
- Performance attribution and factor analysis
- Production-ready execution adapters
- Compliance and client reporting

Example:
    >>> from rlx_institutional import PortfolioManager
    >>> from rlx_sdk import Strategy
    >>>
    >>> strategies = [Strategy1(), Strategy2(), Strategy3()]
    >>> portfolio = PortfolioManager(
    ...     initial_capital=10_000_000,
    ...     strategies=strategies,
    ...     allocation='risk_parity'
    ... )
    >>> results = portfolio.backtest(data)
"""

__version__ = "0.1.0"

from .portfolio import PortfolioManager, CapitalAllocator
from .risk import RiskManager, VaRCalculator
from .optimization import GridSearchOptimizer, WalkForwardAnalysis

__all__ = [
    "PortfolioManager",
    "CapitalAllocator",
    "RiskManager",
    "VaRCalculator",
    "GridSearchOptimizer",
    "WalkForwardAnalysis",
]
