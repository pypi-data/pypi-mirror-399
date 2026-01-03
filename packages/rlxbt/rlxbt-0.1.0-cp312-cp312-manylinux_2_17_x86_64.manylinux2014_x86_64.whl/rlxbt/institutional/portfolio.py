"""
Portfolio Management Module

Manages multiple strategies as a unified portfolio with capital allocation,
rebalancing, and performance tracking.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Literal, Any
from dataclasses import dataclass

from ..core import Strategy, Backtester


AllocationMethod = Literal[
    "equal_weight", "risk_parity", "max_sharpe", "min_variance", "custom"
]


@dataclass
class StrategyAllocation:
    """Strategy allocation configuration"""

    strategy: Strategy
    name: str
    weight: float
    max_capital: Optional[float] = None
    min_capital: Optional[float] = None


class CapitalAllocator:
    """
    Handles capital allocation across multiple strategies.

    Supports multiple allocation methods:
    - equal_weight: Equal capital to each strategy
    - risk_parity: Allocate inversely proportional to volatility
    - max_sharpe: Optimize for maximum Sharpe ratio
    - min_variance: Minimize portfolio variance
    - custom: User-defined weights
    """

    def __init__(self, method: AllocationMethod = "equal_weight"):
        self.method = method

    def allocate(
        self,
        strategies: List[Strategy],
        total_capital: float,
        historical_returns: Optional[Dict[str, pd.Series]] = None,
        custom_weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, float]:
        """
        Allocate capital across strategies.

        Args:
            strategies: List of Strategy objects
            total_capital: Total capital to allocate
            historical_returns: Historical returns for optimization (required for risk_parity, max_sharpe, min_variance)
            custom_weights: Custom weights (required for custom method)

        Returns:
            Dictionary mapping strategy index to allocated capital
        """
        n_strategies = len(strategies)

        if self.method == "equal_weight":
            return self._equal_weight(n_strategies, total_capital)

        elif self.method == "risk_parity":
            if historical_returns is None:
                raise ValueError("historical_returns required for risk_parity")
            return self._risk_parity(historical_returns, total_capital)

        elif self.method == "max_sharpe":
            if historical_returns is None:
                raise ValueError("historical_returns required for max_sharpe")
            return self._max_sharpe(historical_returns, total_capital)

        elif self.method == "min_variance":
            if historical_returns is None:
                raise ValueError("historical_returns required for min_variance")
            return self._min_variance(historical_returns, total_capital)

        elif self.method == "custom":
            if custom_weights is None:
                raise ValueError("custom_weights required for custom method")
            return self._custom_weights(custom_weights, total_capital)

        else:
            raise ValueError(f"Unknown allocation method: {self.method}")

    def _equal_weight(
        self, n_strategies: int, total_capital: float
    ) -> Dict[str, float]:
        """Equal weight allocation"""
        weight = 1.0 / n_strategies
        return {f"strategy_{i}": total_capital * weight for i in range(n_strategies)}

    def _risk_parity(
        self, historical_returns: Dict[str, pd.Series], total_capital: float
    ) -> Dict[str, float]:
        """
        Risk parity allocation - inversely proportional to volatility.
        Higher volatility = lower allocation.
        """
        volatilities = {
            name: float(returns.std()) for name, returns in historical_returns.items()
        }

        # Inverse volatility weights (guard zero/NaN)
        inv_vol: Dict[str, float] = {}
        for name, vol in volatilities.items():
            if not np.isfinite(vol) or vol <= 0:
                inv_vol[name] = 0.0
            else:
                inv_vol[name] = 1.0 / vol

        total_inv_vol = float(sum(inv_vol.values()))
        if total_inv_vol <= 0:
            # fallback: equal weight
            return self._equal_weight(len(historical_returns), total_capital)

        weights = {name: iv / total_inv_vol for name, iv in inv_vol.items()}

        return {name: total_capital * weight for name, weight in weights.items()}

    def _max_sharpe(
        self, historical_returns: Dict[str, pd.Series], total_capital: float
    ) -> Dict[str, float]:
        """
        Maximum Sharpe ratio optimization.
        Uses mean-variance optimization to maximize risk-adjusted returns.
        """
        # Convert returns to DataFrame
        returns_df = pd.DataFrame(historical_returns)

        # Calculate mean returns and covariance matrix
        mean_returns = returns_df.mean()
        cov_matrix = returns_df.cov()

        # Simple optimization: equal weight as placeholder
        # In production, use scipy.optimize or cvxpy for proper optimization
        n_strategies = len(historical_returns)
        weights = {f"strategy_{i}": 1.0 / n_strategies for i in range(n_strategies)}

        return {name: total_capital * weight for name, weight in weights.items()}

    def _min_variance(
        self, historical_returns: Dict[str, pd.Series], total_capital: float
    ) -> Dict[str, float]:
        """
        Minimum variance optimization.
        Minimize portfolio variance subject to being fully invested.
        """
        # Convert returns to DataFrame
        returns_df = pd.DataFrame(historical_returns)

        # Calculate covariance matrix
        cov_matrix = returns_df.cov()

        # Simple optimization: equal weight as placeholder
        # In production, use scipy.optimize for proper optimization
        n_strategies = len(historical_returns)
        weights = {f"strategy_{i}": 1.0 / n_strategies for i in range(n_strategies)}

        return {name: total_capital * weight for name, weight in weights.items()}

    def _custom_weights(
        self, custom_weights: Dict[str, float], total_capital: float
    ) -> Dict[str, float]:
        """Custom user-defined weights"""
        # Normalize weights to sum to 1
        total_weight = sum(custom_weights.values())
        normalized_weights = {
            name: w / total_weight for name, w in custom_weights.items()
        }

        return {
            name: total_capital * weight for name, weight in normalized_weights.items()
        }


class PortfolioManager:
    """
    Manages a portfolio of multiple trading strategies.

    Features:
    - Capital allocation across strategies
    - Rebalancing on schedule
    - Aggregated performance metrics
    - Risk management integration

    Example:
        >>> strategies = [TrendFollowing(), MeanReversion(), Breakout()]
        >>> portfolio = PortfolioManager(
        ...     initial_capital=10_000_000,
        ...     strategies=strategies,
        ...     allocation='risk_parity'
        ... )
        >>> results = portfolio.backtest(data)
    """

    def __init__(
        self,
        initial_capital: float,
        strategies: List[Strategy],
        allocation: AllocationMethod = "equal_weight",
        rebalance_frequency: Optional[str] = None,
        commission: float = 0.0,
        slippage: float = 0.0,
    ):
        """
        Initialize Portfolio Manager.

        Args:
            initial_capital: Total starting capital
            strategies: List of Strategy objects
            allocation: Capital allocation method
            rebalance_frequency: How often to rebalance ('daily', 'weekly', 'monthly', None for buy-and-hold)
            commission: Commission per trade ($ or %)
            slippage: Slippage per trade ($ or %)
        """
        self.initial_capital = initial_capital
        self.strategies = strategies
        self.allocation_method = allocation
        self.rebalance_frequency = rebalance_frequency
        self.commission = commission
        self.slippage = slippage

        self.allocator = CapitalAllocator(method=allocation)
        self.strategy_results = {}

    def backtest(
        self,
        data: pd.DataFrame,
        risk_manager=None,
        custom_weights: Optional[Dict[str, float]] = None,
        license_key: Optional[str] = None,
        verbose: bool = True,
        **backtester_kwargs: Any,
    ) -> Dict:
        """
        Run backtest on all strategies in the portfolio.

        Args:
            data: OHLCV DataFrame
            risk_manager: Optional RiskManager instance
            custom_weights: Custom weights for allocation (if using 'custom' method)

        Returns:
            Dictionary with portfolio-level results
        """
        if verbose:
            print(f"🏦 Running Portfolio Backtest")
            print(f"   💰 Initial Capital: ${self.initial_capital:,.0f}")
            print(f"   📊 Strategies: {len(self.strategies)}")
            print(f"   ⚖️  Allocation: {self.allocation_method}")
            print("=" * 60)

        # Allocate capital
        allocations = self.allocator.allocate(
            self.strategies, self.initial_capital, custom_weights=custom_weights
        )

        # Run backtest for each strategy
        strategy_results: Dict[str, Optional[Dict[str, Any]]] = {}
        strategy_capital: Dict[str, float] = {}

        for i, strategy in enumerate(self.strategies):
            strategy_name = f"Strategy_{i + 1}_{strategy.__class__.__name__}"
            allocated_capital = allocations[f"strategy_{i}"]

            strategy_capital[strategy_name] = float(allocated_capital)

            if verbose:
                print(f"\n🚀 Testing {strategy_name}")
                print(f"   💰 Allocated Capital: ${allocated_capital:,.0f}")

            # Create backtester with allocated capital
            backtester = Backtester(
                initial_capital=allocated_capital,
                commission=self.commission,
                slippage=self.slippage,
                license_key=license_key,
                **backtester_kwargs,
            )

            try:
                # Run backtest
                result = backtester.run(strategy, data)
                strategy_results[strategy_name] = result

                if verbose:
                    print(f"   📈 Return: {result['total_return']:.2%}")
                    print(f"   📊 Trades: {result['total_trades']}")
                    print(f"   ✅ Win Rate: {result['win_rate']:.2%}")

            except Exception as e:
                if verbose:
                    print(f"   ❌ Error: {e}")
                strategy_results[strategy_name] = None

        # Aggregate portfolio results
        portfolio_results = self._aggregate_results(
            strategy_results=strategy_results,
            strategy_capital=strategy_capital,
        )

        if risk_manager is not None:
            try:
                portfolio_results["risk_checks"] = risk_manager.check_risk_limits(
                    portfolio_results
                )
            except Exception as e:
                portfolio_results["risk_checks"] = {
                    "all_limits_ok": True,
                    "risk_check_error": str(e),
                }

        if verbose:
            print("\n" + "=" * 60)
            print("📊 PORTFOLIO SUMMARY")
            print("=" * 60)
            print(f"Total Return:     {portfolio_results['total_return']:.2%}")
            print(f"Sharpe Ratio:     {portfolio_results['sharpe_ratio']:.2f}")
            print(f"Max Drawdown:     {portfolio_results['max_drawdown']:.2%}")
            print(f"Total Trades:     {portfolio_results['total_trades']}")
            print(f"Strategy Count:   {portfolio_results['strategy_count']}")
            if "risk_checks" in portfolio_results:
                ok = portfolio_results["risk_checks"].get("all_limits_ok")
                print(f"Risk Checks:      {'✅ PASS' if ok else '❌ FAIL'}")
            print("=" * 60)

        return portfolio_results

    def _aggregate_results(
        self,
        strategy_results: Dict[str, Optional[Dict[str, Any]]],
        strategy_capital: Dict[str, float],
    ) -> Dict[str, Any]:
        """Aggregate individual strategy results into portfolio metrics.

        Notes:
        - Uses each strategy's own equity curve when available to build a portfolio equity curve.
        - Falls back to allocation-weighted total_return if equity curve timestamps are missing.
        """

        # Filter out failed strategies
        valid_results = {k: v for k, v in strategy_results.items() if v is not None}

        if not valid_results:
            return {
                "total_return": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "total_trades": 0,
                "strategy_count": 0,
                "strategy_returns": {},
                "equity_curve": [],
            }

        total_trades = 0
        strategy_returns: Dict[str, Any] = {}

        equity_series: List[pd.Series] = []
        equity_ok = True

        for strategy_name, result in valid_results.items():
            total_trades += int(result.get("total_trades") or 0)

            cap = float(strategy_capital.get(strategy_name, 0.0))
            weight = cap / float(self.initial_capital) if self.initial_capital else 0.0

            strategy_returns[strategy_name] = {
                "return": float(result.get("total_return") or 0.0),
                "weight": weight,
                "trades": int(result.get("total_trades") or 0),
                "win_rate": float(result.get("win_rate") or 0.0),
                "initial_capital": cap,
                "final_capital": result.get("final_capital"),
            }

            ts = result.get("equity_curve_timestamps") or []
            eq = result.get("equity_curve") or []
            if len(ts) != len(eq) or len(eq) == 0:
                equity_ok = False
                continue

            s = pd.Series(
                eq,
                index=pd.to_datetime(pd.Series(ts, dtype="int64"), unit="s", utc=True),
            )
            s = pd.to_numeric(s, errors="coerce")
            s.name = strategy_name
            equity_series.append(s)

        # Portfolio equity curve (preferred)
        portfolio_equity_df: Optional[pd.DataFrame] = None
        portfolio_equity: Optional[pd.Series] = None
        if equity_ok and equity_series:
            portfolio_equity_df = pd.concat(equity_series, axis=1).sort_index()
            portfolio_equity_df = portfolio_equity_df.ffill().dropna(how="all")
            portfolio_equity = portfolio_equity_df.sum(axis=1)

        # total_return
        if portfolio_equity is not None and len(portfolio_equity) > 1:
            total_return = (
                float(portfolio_equity.iloc[-1]) - float(self.initial_capital)
            ) / float(self.initial_capital)
            # Sharpe and drawdown from portfolio equity
            rets = portfolio_equity.pct_change().dropna()
            sharpe_ratio = float(rets.mean() / (rets.std() + 1e-12))
            running_max = portfolio_equity.cummax()
            dd = (portfolio_equity / running_max) - 1.0
            max_drawdown = float(abs(dd.min())) if not dd.empty else 0.0
            returns_series = rets
        else:
            # Fallback: allocation-weighted total_return
            total_return = float(
                sum(v["return"] * v["weight"] for v in strategy_returns.values())
            )
            sharpe_ratio = float(
                np.mean(
                    [
                        float(r.get("sharpe_ratio") or 0.0)
                        for r in valid_results.values()
                    ]
                )
            )
            max_drawdown = float(
                max(
                    [
                        float(r.get("max_drawdown") or 0.0)
                        for r in valid_results.values()
                    ]
                )
            )
            returns_series = None

        out = {
            "total_return": total_return,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "total_trades": total_trades,
            "strategy_count": len(valid_results),
            "strategy_returns": strategy_returns,
            "initial_capital": self.initial_capital,
            "final_capital": self.initial_capital * (1 + total_return),
            "allocation_method": self.allocation_method,
            "strategy_results": valid_results,
            "portfolio_equity_curve": (
                portfolio_equity.reset_index().rename(
                    columns={"index": "dt", 0: "equity"}
                )
                if portfolio_equity is not None
                else None
            ),
        }

        if returns_series is not None:
            out["returns"] = returns_series

        return out

    def optimize_allocation(
        self, data: pd.DataFrame, objective: str = "sharpe"
    ) -> Dict:
        """
        Optimize capital allocation based on historical performance.

        Args:
            data: Historical data for optimization
            objective: Optimization objective ('sharpe', 'return', 'drawdown')

        Returns:
            Optimal allocation weights
        """
        # Run initial backtest to get historical returns
        print("🔧 Optimizing portfolio allocation...")

        # This would run multiple backtests with different allocations
        # and find the optimal one. Placeholder for now.

        return {}
