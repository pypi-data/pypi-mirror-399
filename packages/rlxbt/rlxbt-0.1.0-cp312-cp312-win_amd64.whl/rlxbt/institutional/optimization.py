"""
Optimization Module

Provides strategy parameter optimization tools:
- Grid search
- Random search
- Bayesian optimization
- Walk-forward analysis
- Cross-validation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Callable, Optional
from itertools import product
import os

from ..core import Strategy, Backtester


class GridSearchOptimizer:
    """
    Grid search parameter optimization.

    Tests all combinations of parameters to find optimal settings.

    Example:
        >>> optimizer = GridSearchOptimizer()
        >>> param_grid = {
        ...     'fast_period': [5, 10, 20],
        ...     'slow_period': [20, 50, 100]
        ... }
        >>> best_params = optimizer.optimize(
        ...     strategy_class=SmaCrossover,
        ...     param_grid=param_grid,
        ...     data=data
        ... )
    """

    def __init__(self, metric: str = "sharpe_ratio"):
        """
        Initialize optimizer.

        Args:
            metric: Optimization metric ('sharpe_ratio', 'total_return', 'profit_factor')
        """
        self.metric = metric
        self.results = []

    def optimize(
        self,
        strategy_class: type,
        param_grid: Dict[str, List],
        data: pd.DataFrame,
        initial_capital: float = 100000.0,
        license_key: Optional[str] = None,
        verbose: bool = True,
        **backtester_kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Run grid search optimization.

        Args:
            strategy_class: Strategy class to optimize
            param_grid: Dictionary of parameters and their values to test
            data: OHLCV data
            initial_capital: Starting capital
            verbose: Print progress

        Returns:
            Best parameters and results
        """
        # Generate all parameter combinations
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        param_combinations = list(product(*param_values))

        total_combinations = len(param_combinations)

        if verbose:
            print(f"🔍 Grid Search Optimization")
            print(f"   Parameters: {param_names}")
            print(f"   Combinations: {total_combinations}")
            print("=" * 60)

        best_score = float("-inf")
        best_params = None
        best_result = None

        # Test each combination
        for i, param_combo in enumerate(param_combinations):
            # Create parameter dictionary
            params = dict(zip(param_names, param_combo))

            if verbose and i % max(1, total_combinations // 10) == 0:
                print(
                    f"Progress: {i}/{total_combinations} ({i / total_combinations * 100:.1f}%)"
                )

            try:
                # Create strategy with these parameters
                strategy = strategy_class(**params)

                # Run backtest
                backtester = Backtester(
                    initial_capital=initial_capital,
                    license_key=license_key,
                    **backtester_kwargs,
                )
                result = backtester.run(strategy, data)

                # Get metric value (supports metrics computed by Backtester.summary)
                if self.metric in (result or {}):
                    score = float(result.get(self.metric) or 0.0)
                else:
                    score = float(backtester.summary(result).get(self.metric) or 0.0)

                # Store result
                self.results.append(
                    {"params": params, "score": score, "result": result}
                )

                # Update best if better
                if score > best_score:
                    best_score = score
                    best_params = params
                    best_result = result

            except Exception as e:
                if verbose:
                    print(f"   ❌ Error with params {params}: {e}")
                continue

        if verbose:
            print("=" * 60)
            print(f"✅ Optimization Complete")
            print(f"   Best {self.metric}: {best_score:.4f}")
            print(f"   Best Parameters: {best_params}")

        return {
            "best_params": best_params,
            "best_score": best_score,
            "best_result": best_result,
            "all_results": self.results,
        }

    def plot_results(self, param_name: str):
        """
        Plot optimization results for a specific parameter.

        Args:
            param_name: Name of parameter to plot
        """
        # Extract parameter values and scores
        param_values = [
            r["params"][param_name] for r in self.results if param_name in r["params"]
        ]
        scores = [r["score"] for r in self.results if param_name in r["params"]]

        # Would use matplotlib here
        # import matplotlib.pyplot as plt
        # plt.plot(param_values, scores)
        # plt.xlabel(param_name)
        # plt.ylabel(self.metric)
        # plt.title(f'Optimization Results: {param_name}')
        # plt.show()

        print(f"Plot for {param_name} would be shown here")


class WalkForwardAnalysis:
    """
    Walk-forward analysis for out-of-sample testing.

    Divides data into multiple train/test periods:
    - Train on in-sample period
    - Test on out-of-sample period
    - Roll forward and repeat

    Example:
        >>> wfa = WalkForwardAnalysis(
        ...     train_size=0.7,
        ...     test_size=0.3,
        ...     n_splits=5
        ... )
        >>> results = wfa.run(strategy_class, param_grid, data)
    """

    def __init__(
        self, train_size: float = 0.7, test_size: float = 0.3, n_splits: int = 5
    ):
        """
        Initialize walk-forward analysis.

        Args:
            train_size: Fraction of data for training
            test_size: Fraction of data for testing
            n_splits: Number of walk-forward splits
        """
        self.train_size = train_size
        self.test_size = test_size
        self.n_splits = n_splits

    def run(
        self,
        strategy_class: type,
        param_grid: Dict[str, List],
        data: pd.DataFrame,
        initial_capital: float = 100000.0,
        license_key: Optional[str] = None,
        verbose: bool = True,
        **backtester_kwargs: Any,
    ) -> Dict:
        """
        Run walk-forward analysis.

        Args:
            strategy_class: Strategy class to test
            param_grid: Parameter grid for optimization
            data: OHLCV data
            verbose: Print progress

        Returns:
            Walk-forward results
        """
        if verbose:
            print(f"🚶 Walk-Forward Analysis")
            print(f"   Train Size: {self.train_size * 100:.0f}%")
            print(f"   Test Size: {self.test_size * 100:.0f}%")
            print(f"   Splits: {self.n_splits}")
            print("=" * 60)

        # Calculate split sizes
        total_size = len(data)
        train_size = int(total_size * self.train_size)
        test_size = int(total_size * self.test_size)
        step_size = total_size // self.n_splits

        results = []

        # Run each split
        for i in range(self.n_splits):
            start_idx = i * step_size
            train_end_idx = min(start_idx + train_size, total_size)
            test_end_idx = min(train_end_idx + test_size, total_size)

            if test_end_idx >= total_size:
                break

            # Split data
            train_data = data.iloc[start_idx:train_end_idx]
            test_data = data.iloc[train_end_idx:test_end_idx]

            if verbose:
                print(f"\n📊 Split {i + 1}/{self.n_splits}")
                print(f"   Train: {len(train_data)} bars")
                print(f"   Test:  {len(test_data)} bars")

            # Optimize on training data
            optimizer = GridSearchOptimizer()
            optimization_result = optimizer.optimize(
                strategy_class=strategy_class,
                param_grid=param_grid,
                data=train_data,
                initial_capital=initial_capital,
                license_key=license_key,
                **backtester_kwargs,
                verbose=False,
            )

            best_params = optimization_result["best_params"]

            # Test on out-of-sample data
            strategy = strategy_class(**best_params)
            backtester = Backtester(
                initial_capital=initial_capital,
                license_key=license_key,
                **backtester_kwargs,
            )
            test_result = backtester.run(strategy, test_data)

            if verbose:
                print(f"   In-Sample Score:  {optimization_result['best_score']:.4f}")
                print(f"   Out-Sample Return: {test_result['total_return']:.2%}")

            results.append(
                {
                    "split": i + 1,
                    "best_params": best_params,
                    "in_sample_score": optimization_result["best_score"],
                    "out_sample_return": test_result["total_return"],
                    "out_sample_result": test_result,
                }
            )

        # Calculate aggregate metrics
        avg_out_sample_return = np.mean([r["out_sample_return"] for r in results])

        if verbose:
            print("\n" + "=" * 60)
            print("📊 Walk-Forward Summary")
            print("=" * 60)
            print(f"Avg Out-Sample Return: {avg_out_sample_return:.2%}")
            print("=" * 60)

        return {
            "splits": results,
            "avg_out_sample_return": avg_out_sample_return,
            "n_splits": len(results),
        }
