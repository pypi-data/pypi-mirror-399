from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import pandas as pd

from .core import rust_engine as rlx


class StabilityAnalyzer:
    """
    High-level analyzer for strategy stability and robustness.
    Uses high-performance Rust engines for simulations and partitioning.
    """

    def __init__(self):
        self.mc_engine = rlx.MonteCarloEngine()
        self.wfa_engine = rlx.WalkForwardAnalyzer()
        self.sensitivity_engine = rlx.SensitivityEngine()

    def run_monte_carlo(
        self, trades: List, initial_capital: float = 100000.0, iterations: int = 1000
    ):
        """
        Runs Monte Carlo simulation by shuffling trades.

        Args:
            trades: List of TradeResult objects from a backtest.
            initial_capital: Starting balance for simulations.
            iterations: Number of simulated equity curves to generate.
        """
        return self.mc_engine.run_simulation(trades, initial_capital, iterations)

    def plot_monte_carlo(self, result, save_path: Optional[str] = None):
        """
        Plots the equity bands from Monte Carlo simulation.
        """
        plt.figure(figsize=(12, 7))

        # Use fill_between for bands
        if 5 in result.equity_percentiles and 95 in result.equity_percentiles:
            plt.fill_between(
                range(len(result.equity_percentiles[5])),
                result.equity_percentiles[5],
                result.equity_percentiles[95],
                color="gray",
                alpha=0.2,
                label="5th-95th Band",
            )

        if 25 in result.equity_percentiles and 75 in result.equity_percentiles:
            plt.fill_between(
                range(len(result.equity_percentiles[25])),
                result.equity_percentiles[25],
                result.equity_percentiles[75],
                color="blue",
                alpha=0.1,
                label="25th-75th Band",
            )

        # Plot 50th percentile (Median)
        if 50 in result.equity_percentiles:
            plt.plot(
                result.equity_percentiles[50],
                color="black",
                linewidth=2,
                label="Median (50th)",
            )

        plt.title(
            f"Monte Carlo Simulation: Equity Bands ({result.iterations} iterations)",
            fontsize=14,
        )
        plt.xlabel("Trade Number", fontsize=12)
        plt.ylabel("Portfolio Value ($)", fontsize=12)
        plt.legend(loc="upper left")
        plt.grid(True, linestyle="--", alpha=0.7)

        # Add Risk of Ruin text
        plt.annotate(
            f"Risk of Ruin: {result.risk_of_ruin:.1%}",
            xy=(0.02, 0.05),
            xycoords="axes fraction",
            bbox=dict(boxstyle="round", fc="w", alpha=0.5),
            fontsize=12,
            color="red" if result.risk_of_ruin > 0 else "green",
        )

        if save_path:
            plt.savefig(save_path)
            print(f"Plot saved to {save_path}")
        else:
            plt.show()

    def get_wfa_windows(
        self,
        total_len: int,
        train_size: int,
        test_size: int,
        step_size: int,
        anchored: bool = False,
    ):
        """
        Generates window indices for Walk-Forward Analysis.
        """
        return self.wfa_engine.get_windows(
            total_len, train_size, test_size, step_size, anchored
        )

    def calculate_wfe(self, is_return: float, oos_return: float) -> float:
        """
        Calculates Walk-Forward Efficiency.
        WFE = Annualized OOS Return / Annualized IS Return
        """
        return self.wfa_engine.calculate_wfe(is_return, oos_return)

    def analyze_parameter_importance(
        self,
        backtester,
        strategy_class: type,
        data: pd.DataFrame,
        base_params: Dict,
        param_variations: Dict[str, List],
        metric: str = "sharpe_ratio",
    ):
        """
        Analyze parameter importance by running multiple one-at-a-time backtests.

        Args:
            backtester: Backtester instance.
            strategy_class: The Strategy class to instantiate.
            data: Market data for backtests.
            base_params: Baseline parameters for the strategy.
            param_variations: Variations for each parameter to test.
            metric: Performance metric to measure impact on.
        """
        # 1. Get base performance
        base_strat = strategy_class(**base_params)
        base_res = backtester.run(base_strat, data, return_result=True)
        base_perf = (
            getattr(base_res, metric)
            if hasattr(base_res, metric)
            else base_res.metrics.get(metric, 0.0)
        )

        # 2. Run variations
        variations_results = {}
        for param_name, values in param_variations.items():
            param_outputs = []
            for val in values:
                test_params = base_params.copy()
                test_params[param_name] = val

                test_strat = strategy_class(**test_params)
                res = backtester.run(test_strat, data, return_result=True)

                perf = (
                    getattr(res, metric)
                    if hasattr(res, metric)
                    else res.metrics.get(metric, 0.0)
                )
                param_outputs.append(perf)
            variations_results[param_name] = param_outputs

        # 3. Use Rust engine for analysis
        return self.sensitivity_engine.analyze_importance(base_perf, variations_results)

    def plot_parameter_importance(self, result, save_path: Optional[str] = None):
        """
        Plot bar chart of parameter importance.
        """
        items = sorted(
            result.importance_scores.items(), key=lambda x: x[1], reverse=True
        )
        names = [x[0] for x in items]
        scores = [x[1] for x in items]

        plt.figure(figsize=(10, 6))
        bars = plt.barh(names, scores, color="teal", alpha=0.8)
        plt.xlabel("Importance Score (%)", fontsize=12)
        plt.title("Strategy Parameter Importance (Sensitivity Analysis)", fontsize=14)
        plt.grid(axis="x", linestyle="--", alpha=0.6)

        # Add score labels
        for bar in bars:
            width = bar.get_width()
            plt.text(
                width + 1,
                bar.get_y() + bar.get_height() / 2,
                f"{width:.1f}%",
                va="center",
            )

        plt.xlim(0, 110)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
            print(f"Plot saved to {save_path}")
        else:
            plt.show()
