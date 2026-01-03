from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from ..core import Backtester
from ..stability import StabilityAnalyzer


class WalkForwardML:
    """
    Orchestrates the Walk-Forward ML training and testing workflow.

    Cycles through training and testing windows, re-training the model
    periodically and concatenating the out-of-sample results.
    """

    def __init__(self, backtester: Backtester):
        self.backtester = backtester
        self.analyzer = StabilityAnalyzer()

    def run(
        self,
        strategy_class: type,
        data: pd.DataFrame,
        train_size: int,
        test_size: int,
        step_size: int,
        anchored: bool = False,
        base_params: Dict = {},
        optuna_config: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Run the walk-forward ML backtest with optional hyperparameter optimization.

        Args:
            strategy_class: The ML strategy class to use.
            data: Market data.
            train_size: Number of bars for training.
            test_size: Number of bars for testing.
            step_size: Number of bars to roll forward.
            anchored: Whether to anchor the training window start.
            base_params: Initial parameters for the strategy.
            optuna_config: Optional dict with keys:
                - n_trials: Number of optimization trials.
                - timeout: Max time in seconds.
                - param_space: Dict mapping param names to (type, low, high, [log]).
        """
        import importlib

        optuna = None
        if optuna_config:
            try:
                optuna = importlib.import_module("optuna")
            except ImportError:
                print(
                    "⚠️ Optuna not found. Please install it to use hyperparameter tuning."
                )
                optuna_config = None
        # 1. Get windows from the fast Rust engine
        windows = self.analyzer.get_wfa_windows(
            total_len=len(data),
            train_size=train_size,
            test_size=test_size,
            step_size=step_size,
            anchored=anchored,
        )

        if not windows:
            raise ValueError("No windows generated. Check your sizes.")

        all_trades = []
        equity_curves = []
        last_equity = self.backtester.initial_capital
        total_commission = 0.0

        print(f"🧠 Starting Walk-Forward ML with {len(windows)} splits...")

        for i, w in enumerate(windows):
            # Split data
            train_data = data.iloc[w.train_start : w.train_end]
            test_data = data.iloc[w.test_start : w.test_end]

            # Optional: Hyperparameter Optimization
            current_params = base_params.copy()
            if optuna and optuna_config:
                print(f"   [{i + 1}/{len(windows)}] Optimizing hyperparameters...")

                def objective(trial):
                    trial_params = current_params.copy()
                    for p_name, p_def in optuna_config.get("param_space", {}).items():
                        p_type = p_def[0]
                        if p_type == "int":
                            trial_params[p_name] = trial.suggest_int(
                                p_name,
                                p_def[1],
                                p_def[2],
                                log=p_def[3] if len(p_def) > 3 else False,
                            )
                        elif p_type == "float":
                            trial_params[p_name] = trial.suggest_float(
                                p_name,
                                p_def[1],
                                p_def[2],
                                log=p_def[3] if len(p_def) > 3 else False,
                            )
                        elif p_type == "categorical":
                            trial_params[p_name] = trial.suggest_categorical(
                                p_name, p_def[1]
                            )

                    # Create temporary strategy for trial
                    t_strategy = strategy_class(**trial_params)
                    t_strategy.train(train_data)

                    # Run quick backtest on training data (val split) or use cross-val?
                    # For simplicity in this engine, we'll use a small validation tail of train_data
                    val_size = max(1, int(len(train_data) * 0.2))
                    v_train = train_data.iloc[:-val_size]
                    v_val = train_data.iloc[-val_size:]

                    t_strategy.train(v_train)

                    # Run validation backtest
                    v_bt = Backtester(
                        initial_capital=last_equity,
                        license_key=self.backtester.license_key,
                    )
                    v_res = v_bt.run(t_strategy, v_val)

                    # We want to maximize sharpe_ratio
                    return v_res.get("sharpe_ratio", -10.0)

                study = optuna.create_study(direction="maximize")
                study.optimize(
                    objective,
                    n_trials=optuna_config.get("n_trials", 20),
                    timeout=optuna_config.get("timeout"),
                )

                best_params = study.best_params
                print(f"      Best params: {best_params}")
                current_params.update(best_params)

            # Instantiate strategy with optimized params
            strategy = strategy_class(**current_params)

            # Train model
            print(
                f"   [{i + 1}/{len(windows)}] Training on bars {w.train_start}:{w.train_end}..."
            )
            strategy.train(train_data)

            # Create a fresh backtester for this segment to handle updated capital
            bt = Backtester(
                initial_capital=last_equity,
                commission=self.backtester.commission,
                slippage=self.backtester.slippage,
                contract_size=self.backtester.contract_size,
                enable_dynamic_tp_sl=self.backtester.enable_dynamic_tp_sl,
                exit_controller=self.backtester.exit_controller,
                use_intrabar_resolution=self.backtester.use_intrabar_resolution,
                license_key=self.backtester.license_key,
            )

            # Run backtest on test window
            res = bt.run(strategy, test_data, return_result=True)

            # Collect results
            all_trades.extend(res.trades)
            # Offset equity curve by previous value (relative to initial)
            # res.equity_curve includes the starting value at index 0
            seg_curve = np.array(res.equity_curve[1:])
            equity_curves.append(seg_curve)

            last_equity = res.final_capital
            total_commission += res.total_commission

        # Consolidate results
        full_equity_curve = [self.backtester.initial_capital] + list(
            np.concatenate(equity_curves)
        )

        # Calculate final metrics from stitched results
        # We'll return a dictionary that matches the structure expected by the user
        final_return = (
            last_equity - self.backtester.initial_capital
        ) / self.backtester.initial_capital

        return {
            "total_return": final_return,
            "final_capital": last_equity,
            "total_trades": len(all_trades),
            "trades": all_trades,
            "equity_curve": full_equity_curve,
            "total_commission": total_commission,
            "splits_count": len(windows),
        }
