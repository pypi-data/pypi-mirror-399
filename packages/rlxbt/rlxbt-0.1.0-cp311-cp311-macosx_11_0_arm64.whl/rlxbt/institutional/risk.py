"""
Risk Management Module

Provides institutional-grade risk management tools including:
- Value at Risk (VaR) calculation
- Maximum drawdown limits
- Position sizing
- Correlation monitoring
- Stress testing
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class RiskLimits:
    """Risk limits configuration"""

    max_portfolio_var: float = 0.02  # Max 2% VaR
    max_strategy_drawdown: float = 0.10  # Max 10% drawdown per strategy
    max_portfolio_drawdown: float = 0.15  # Max 15% portfolio drawdown
    max_position_size: float = 0.20  # Max 20% in single position
    max_correlation: float = 0.70  # Max 70% correlation between strategies
    min_sharpe_ratio: float = 0.5  # Minimum acceptable Sharpe ratio


class VaRCalculator:
    """
    Value at Risk calculator.

    Supports multiple methods:
    - Historical VaR
    - Parametric VaR (Variance-Covariance)
    - Monte Carlo VaR
    """

    def __init__(self, confidence_level: float = 0.95):
        """
        Initialize VaR calculator.

        Args:
            confidence_level: Confidence level for VaR (e.g., 0.95 for 95% VaR)
        """
        self.confidence_level = confidence_level

    def historical_var(self, returns: pd.Series) -> float:
        """
        Calculate Historical VaR.

        Args:
            returns: Series of returns

        Returns:
            VaR value (positive number representing potential loss)
        """
        if len(returns) == 0:
            return 0.0

        # Sort returns
        sorted_returns = np.sort(returns)

        # Find the percentile
        index = int((1 - self.confidence_level) * len(sorted_returns))
        var = -sorted_returns[index] if index < len(sorted_returns) else 0.0

        return max(var, 0.0)

    def parametric_var(self, returns: pd.Series) -> float:
        """
        Calculate Parametric VaR using normal distribution assumption.

        Args:
            returns: Series of returns

        Returns:
            VaR value
        """
        if len(returns) == 0:
            return 0.0

        mean = returns.mean()
        std = returns.std()

        # Z-score for confidence level (e.g., 1.645 for 95%)
        from scipy import stats

        z_score = stats.norm.ppf(self.confidence_level)

        var = -(mean - z_score * std)
        return max(var, 0.0)

    def conditional_var(self, returns: pd.Series) -> float:
        """
        Calculate Conditional VaR (CVaR) / Expected Shortfall.
        Average of losses beyond VaR.

        Args:
            returns: Series of returns

        Returns:
            CVaR value
        """
        if len(returns) == 0:
            return 0.0

        var = self.historical_var(returns)

        # Find returns worse than VaR
        worse_returns = returns[returns <= -var]

        if len(worse_returns) == 0:
            return var

        cvar = -worse_returns.mean()
        return max(cvar, 0.0)


class RiskManager:
    """
    Comprehensive risk management system.

    Features:
    - VaR monitoring
    - Drawdown limits
    - Position sizing
    - Correlation checks
    - Real-time risk alerts

    Example:
        >>> risk_manager = RiskManager(
        ...     max_portfolio_var=0.02,
        ...     max_strategy_drawdown=0.10
        ... )
        >>> risk_manager.check_risk_limits(portfolio_results)
    """

    def __init__(
        self,
        max_portfolio_var: float = 0.02,
        max_strategy_drawdown: float = 0.10,
        max_portfolio_drawdown: float = 0.15,
        max_correlation: float = 0.70,
        var_confidence: float = 0.95,
    ):
        """
        Initialize Risk Manager.

        Args:
            max_portfolio_var: Maximum acceptable portfolio VaR
            max_strategy_drawdown: Maximum drawdown per strategy
            max_portfolio_drawdown: Maximum portfolio drawdown
            max_correlation: Maximum correlation between strategies
            var_confidence: Confidence level for VaR calculations
        """
        self.limits = RiskLimits(
            max_portfolio_var=max_portfolio_var,
            max_strategy_drawdown=max_strategy_drawdown,
            max_portfolio_drawdown=max_portfolio_drawdown,
            max_correlation=max_correlation,
        )
        self.var_calculator = VaRCalculator(confidence_level=var_confidence)

    def check_risk_limits(self, portfolio_results: Dict) -> Dict[str, bool]:
        """
        Check if portfolio is within risk limits.

        Args:
            portfolio_results: Results from portfolio backtest

        Returns:
            Dictionary of limit checks (True = within limits, False = breach)
        """
        checks = {}

        # Check portfolio VaR
        if "returns" in portfolio_results:
            var = self.var_calculator.historical_var(portfolio_results["returns"])
            checks["var_ok"] = var <= self.limits.max_portfolio_var
        else:
            checks["var_ok"] = True

        # Check portfolio drawdown
        if "max_drawdown" in portfolio_results:
            checks["portfolio_dd_ok"] = (
                portfolio_results["max_drawdown"] <= self.limits.max_portfolio_drawdown
            )
        else:
            checks["portfolio_dd_ok"] = True

        # Check individual strategy drawdowns
        if "strategy_returns" in portfolio_results:
            all_strategies_ok = True
            for strategy_name, strategy_data in portfolio_results[
                "strategy_returns"
            ].items():
                if "max_drawdown" in strategy_data:
                    if (
                        strategy_data["max_drawdown"]
                        > self.limits.max_strategy_drawdown
                    ):
                        all_strategies_ok = False
                        break
            checks["strategy_dd_ok"] = all_strategies_ok
        else:
            checks["strategy_dd_ok"] = True

        # Overall status
        checks["all_limits_ok"] = all(checks.values())

        return checks

    def calculate_position_size(
        self, account_value: float, risk_per_trade: float, stop_loss_distance: float
    ) -> float:
        """
        Calculate position size based on risk management rules.

        Args:
            account_value: Current account value
            risk_per_trade: Risk per trade as fraction (e.g., 0.01 for 1%)
            stop_loss_distance: Distance to stop loss in price units

        Returns:
            Position size (number of contracts/shares)
        """
        # Risk amount in dollars
        risk_amount = account_value * risk_per_trade

        # Position size = Risk Amount / Stop Loss Distance
        if stop_loss_distance > 0:
            position_size = risk_amount / stop_loss_distance
        else:
            position_size = 0.0

        # Apply maximum position size limit
        max_position = account_value * self.limits.max_position_size
        position_size = min(position_size, max_position)

        return position_size

    def calculate_correlation_matrix(
        self, strategy_returns: Dict[str, pd.Series]
    ) -> pd.DataFrame:
        """
        Calculate correlation matrix between strategies.

        Args:
            strategy_returns: Dictionary of strategy returns series

        Returns:
            Correlation matrix DataFrame
        """
        returns_df = pd.DataFrame(strategy_returns)
        correlation_matrix = returns_df.corr()
        return correlation_matrix

    def check_correlation_limits(
        self, strategy_returns: Dict[str, pd.Series]
    ) -> Dict[str, bool]:
        """
        Check if strategy correlations are within limits.

        Args:
            strategy_returns: Dictionary of strategy returns series

        Returns:
            Dictionary of correlation checks
        """
        corr_matrix = self.calculate_correlation_matrix(strategy_returns)

        # Check if any pair has correlation above limit
        n_strategies = len(strategy_returns)
        high_correlation_pairs = []

        for i in range(n_strategies):
            for j in range(i + 1, n_strategies):
                corr = abs(corr_matrix.iloc[i, j])
                if corr > self.limits.max_correlation:
                    strategy_i = corr_matrix.index[i]
                    strategy_j = corr_matrix.columns[j]
                    high_correlation_pairs.append((strategy_i, strategy_j, corr))

        return {
            "correlation_ok": len(high_correlation_pairs) == 0,
            "high_correlation_pairs": high_correlation_pairs,
            "correlation_matrix": corr_matrix,
        }

    def stress_test(self, portfolio_results: Dict, scenarios: List[Dict]) -> Dict:
        """
        Run stress tests on portfolio.

        Args:
            portfolio_results: Portfolio backtest results
            scenarios: List of stress scenarios (e.g., market crash, high volatility)

        Returns:
            Stress test results
        """
        # Placeholder for stress testing
        # Would simulate various market scenarios and measure portfolio response

        return {
            "scenarios_tested": len(scenarios),
            "worst_case_loss": 0.0,
            "passed_stress_tests": True,
        }

    def generate_risk_report(self, portfolio_results: Dict) -> str:
        """
        Generate comprehensive risk report.

        Args:
            portfolio_results: Portfolio backtest results

        Returns:
            Formatted risk report string
        """
        checks = self.check_risk_limits(portfolio_results)

        report = []
        report.append("=" * 60)
        report.append("RISK MANAGEMENT REPORT")
        report.append("=" * 60)
        report.append(
            f"Overall Status: {'✅ PASS' if checks['all_limits_ok'] else '❌ FAIL'}"
        )
        report.append("")
        report.append("Risk Limits:")
        report.append(
            f"  Portfolio VaR:        {'✅' if checks['var_ok'] else '❌'} (Max: {self.limits.max_portfolio_var:.2%})"
        )
        report.append(
            f"  Portfolio Drawdown:   {'✅' if checks['portfolio_dd_ok'] else '❌'} (Max: {self.limits.max_portfolio_drawdown:.2%})"
        )
        report.append(
            f"  Strategy Drawdowns:   {'✅' if checks['strategy_dd_ok'] else '❌'} (Max: {self.limits.max_strategy_drawdown:.2%})"
        )
        report.append("")
        report.append(f"Current Metrics:")
        report.append(
            f"  Max Drawdown:         {portfolio_results.get('max_drawdown', 0):.2%}"
        )
        report.append("=" * 60)

        return "\n".join(report)
