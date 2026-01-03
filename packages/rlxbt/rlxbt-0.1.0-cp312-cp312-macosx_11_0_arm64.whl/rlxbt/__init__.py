"""
RLXBT - RLX Backtester SDK
"""

from .core import Backtester, Strategy

# Import institutional components
from .institutional import (
    CapitalAllocator,
    GridSearchOptimizer,
    PortfolioManager,
    RiskManager,
    VaRCalculator,
    WalkForwardAnalysis,
)
from .rl_env import RlxEnv, RlxMultiAssetEnv
from .stability import StabilityAnalyzer
from .utils import load_data

# Re-export the rust engine components if needed
try:
    from . import rlx
except ImportError:
    pass

__all__ = [
    "Strategy",
    "Backtester",
    "load_data",
    "RlxEnv",
    "RlxMultiAssetEnv",
    "PortfolioManager",
    "CapitalAllocator",
    "RiskManager",
    "VaRCalculator",
    "GridSearchOptimizer",
    "WalkForwardAnalysis",
    "StabilityAnalyzer",
    "rlx",
]
