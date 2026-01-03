import pandas as pd
import numpy as np
import os
import importlib
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union


def _import_rust_engine():
    """Import the compiled Rust extension.

    Supports both layouts:
    - packaged as rlxbt.rlx (recommended)
    - packaged as a top-level module named rlx (legacy/dev)
    """

    try:
        return importlib.import_module(f"{__package__}.rlx")
    except Exception:
        try:
            return importlib.import_module("rlx")
        except Exception as e:
            raise ImportError(
                "Failed to import RLX Rust engine. "
                "Build/install the extension (e.g. `maturin develop`) "
                "or ensure the wheel providing `rlxbt.rlx`/`rlx` is installed."
            ) from e


rust_engine = _import_rust_engine()


def get_license_key(license_key: Optional[str] = None) -> Optional[str]:
    """
    Get license key from parameter or environment variable.

    Args:
        license_key: Explicit license key (takes priority)

    Returns:
        License key string or None
    """
    if license_key:
        return license_key
    return os.environ.get("RLX_LICENSE_KEY")


class Strategy(ABC):
    """
    Base class for Institutional Strategies.
    Users should inherit from this class and implement `on_data` or `generate_signals`.
    """

    def __init__(self):
        self.params = {}

    def set_params(self, **kwargs):
        """Set strategy parameters."""
        self.params.update(kwargs)

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Vectorized signal generation.

        Args:
            data: DataFrame with OHLCV data (timestamp, open, high, low, close, volume)

        Returns:
            DataFrame with 'signal' column (1 for Long, -1 for Short, 0 for Neutral).
            Optional columns: 'take_profit', 'stop_loss' for dynamic risk management.
        """
        pass

    def generate_enhanced_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Wrapper for generate_signals that ensures correct format for the Rust engine.
        """
        df = self.generate_signals(data)

        # Ensure required columns exist
        if "signal" not in df.columns:
            raise ValueError("Strategy output must contain 'signal' column")

        # Add optional columns if missing
        if "take_profit" not in df.columns:
            df["take_profit"] = np.nan
        if "stop_loss" not in df.columns:
            df["stop_loss"] = np.nan

        return df[["signal", "take_profit", "stop_loss"]]


class Backtester:
    """
    Institutional Grade Backtester powered by Rust.

    Args:
        initial_capital: Starting capital for the backtest (default: 100000.0)
        commission: Commission rate per trade (default: 0.0)
        slippage: Slippage per trade (default: 0.0)
        license_key: License key for production use. Can also be set via
                     RLX_LICENSE_KEY environment variable. Get your key at
                     https://rlxbt.com/pricing
    """

    def __init__(
        self,
        initial_capital: float = 100000.0,
        commission: float = 0.0,
        slippage: float = 0.0,
        contract_size: float = 1.0,
        enable_dynamic_tp_sl: bool = True,
        exit_controller=None,
        use_intrabar_resolution: bool = True,
        license_key: Optional[str] = None,
    ):
        self.license_key = get_license_key(license_key)
        self.engine = rust_engine.TradingEngine(
            initial_capital=initial_capital,
            commission=commission,
            slippage=slippage,
            contract_size=contract_size,
            enable_dynamic_tp_sl=enable_dynamic_tp_sl,
            exit_controller=exit_controller,
            license_key=self.license_key,
        )
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.contract_size = contract_size
        self.enable_dynamic_tp_sl = enable_dynamic_tp_sl
        self.exit_controller = exit_controller
        self.use_intrabar_resolution = use_intrabar_resolution
        self.last_result = None
        self.last_results_dict: Optional[Dict] = None
        self.last_dashboard_result = None

    def run(
        self, strategy: Strategy, data: pd.DataFrame, return_result: bool = False
    ) -> Union[Dict, Any]:
        """
        Run the backtest.

        Args:
            strategy: Instance of Strategy class
            data: DataFrame with OHLCV data

        Returns:
            By default returns a dictionary with backtest results and metrics.
            If return_result=True returns the Rust BacktestResult object.
        """
        print(f"🚀 Running backtest on {len(data)} bars...")

        # Execute backtest using Rust engine
        # The engine calls strategy.generate_enhanced_signals(data) internally
        result = self.engine.execute_backtest(strategy, data)
        self.last_result = result

        if return_result:
            return result

        processed = self._process_results(result)
        self.last_results_dict = processed
        return processed

    def results_dict(self, result: Optional[Any] = None) -> Dict:
        """Return results as a rich Python dict.

        Accepts either a Rust BacktestResult (preferred) or an already processed dict.
        If result is omitted, uses the most recent run.
        """

        if result is None:
            if self.last_results_dict is not None:
                return self.last_results_dict
            result = self.last_result

        if result is None:
            raise ValueError(
                "No backtest result available — run backtester.run(...) first or pass result=..."
            )

        if isinstance(result, dict):
            return result

        return self._process_results(result)

    def to_frames(self, result: Optional[Any] = None) -> Dict[str, pd.DataFrame]:
        """Convert a backtest result into Pandas DataFrames for research/tuning."""

        r = self.results_dict(result)

        trades_df = pd.DataFrame(r.get("trades") or [])
        if not trades_df.empty:
            if "entry_time" in trades_df.columns:
                trades_df["entry_dt"] = pd.to_datetime(
                    trades_df["entry_time"], unit="s", utc=True
                )
            if "exit_time" in trades_df.columns:
                trades_df["exit_dt"] = pd.to_datetime(
                    trades_df["exit_time"], unit="s", utc=True
                )
            if "entry_time" in trades_df.columns and "exit_time" in trades_df.columns:
                trades_df["holding_seconds"] = (
                    trades_df["exit_time"] - trades_df["entry_time"]
                )

        equity_curve = r.get("equity_curve") or []
        equity_ts = r.get("equity_curve_timestamps") or []
        if len(equity_ts) == len(equity_curve) and len(equity_curve) > 0:
            equity_df = pd.DataFrame({"timestamp": equity_ts, "equity": equity_curve})
            equity_df["dt"] = pd.to_datetime(equity_df["timestamp"], unit="s", utc=True)
        else:
            equity_df = pd.DataFrame({"equity": equity_curve})

        drawdown_df = pd.DataFrame(r.get("drawdown_series") or [])
        if not drawdown_df.empty and "timestamp" in drawdown_df.columns:
            drawdown_df["dt"] = pd.to_datetime(
                drawdown_df["timestamp"], unit="s", utc=True
            )

        daily_returns_df = pd.DataFrame(r.get("daily_returns") or [])
        if not daily_returns_df.empty and "date" in daily_returns_df.columns:
            daily_returns_df["date"] = pd.to_datetime(daily_returns_df["date"]).dt.date

        return {
            "trades": trades_df,
            "equity": equity_df,
            "drawdown": drawdown_df,
            "daily_returns": daily_returns_df,
        }

    def summary(self, result: Optional[Any] = None) -> Dict[str, Any]:
        """Return a compact, research-friendly summary (adds a few computed stats)."""

        r = self.results_dict(result)

        initial_capital = r.get("initial_capital")
        final_capital = r.get("final_capital")
        total_return = r.get("total_return")
        total_trades = r.get("total_trades") or 0
        win_rate = r.get("win_rate")

        trades = r.get("trades") or []
        pnls = [t.get("pnl") for t in trades if t.get("pnl") is not None]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]

        gross_profit = float(sum(wins)) if wins else 0.0
        gross_loss = float(-sum(losses)) if losses else 0.0

        profit_factor: Optional[float]
        if gross_loss > 0:
            profit_factor = gross_profit / gross_loss
        elif gross_profit > 0:
            profit_factor = float("inf")
        else:
            profit_factor = 0.0

        avg_trade_pnl = float(np.mean(pnls)) if pnls else 0.0
        avg_win_pnl = float(np.mean(wins)) if wins else 0.0
        avg_loss_pnl = float(np.mean(losses)) if losses else 0.0

        if win_rate is None and total_trades > 0:
            win_rate = len(wins) / total_trades

        expectancy_pnl = None
        if win_rate is not None:
            expectancy_pnl = (win_rate * avg_win_pnl) + (
                (1.0 - win_rate) * avg_loss_pnl
            )

        holding_seconds = []
        for t in trades:
            et = t.get("entry_time")
            xt = t.get("exit_time")
            if et is not None and xt is not None:
                holding_seconds.append(xt - et)
        avg_holding_seconds = (
            float(np.mean(holding_seconds)) if holding_seconds else 0.0
        )

        def _max_streak(signs: list[int], target: int) -> int:
            best = 0
            cur = 0
            for s in signs:
                if s == target:
                    cur += 1
                    best = max(best, cur)
                else:
                    cur = 0
            return best

        signs = [1 if p > 0 else (-1 if p < 0 else 0) for p in pnls]
        max_consecutive_wins = _max_streak(signs, 1)
        max_consecutive_losses = _max_streak(signs, -1)

        net_pnl = None
        if initial_capital is not None and final_capital is not None:
            try:
                net_pnl = float(final_capital) - float(initial_capital)
            except Exception:
                net_pnl = None

        return {
            "initial_capital": initial_capital,
            "final_capital": final_capital,
            "net_pnl": net_pnl,
            "total_return": total_return,
            "sharpe_ratio": r.get("sharpe_ratio"),
            "max_drawdown": r.get("max_drawdown"),
            "total_commission": r.get("total_commission"),
            "total_trades": total_trades,
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "avg_trade_pnl": avg_trade_pnl,
            "avg_win_pnl": avg_win_pnl,
            "avg_loss_pnl": avg_loss_pnl,
            "expectancy_pnl": expectancy_pnl,
            "avg_holding_seconds": avg_holding_seconds,
            "max_consecutive_wins": max_consecutive_wins,
            "max_consecutive_losses": max_consecutive_losses,
        }

    def breakdowns(
        self,
        result: Optional[Any] = None,
        data: Optional[pd.DataFrame] = None,
        *,
        timestamp_col: str = "timestamp",
        open_col: str = "open",
        high_col: str = "high",
        low_col: str = "low",
        close_col: str = "close",
        atr_window: int = 14,
        vol_window: int = 48,
        trend_window: int = 200,
        trend_slope_lookback: int = 20,
    ) -> Dict[str, pd.DataFrame]:
        """Return common research breakdown tables for strategy tuning.

        Output is a dict of DataFrames keyed by breakdown name.

        If `data` is provided, additional "market regime" breakdowns are computed by
        attaching entry-time context to each trade (ATR%%, realized vol, trend state).
        """

        frames = self.to_frames(result)
        trades_df = frames.get("trades")
        if trades_df is None or trades_df.empty:
            return {}

        df = trades_df.copy()

        if "exit_dt" in df.columns:
            exit_dt = pd.to_datetime(df["exit_dt"], utc=True, errors="coerce")
            exit_idx = pd.DatetimeIndex(exit_dt)
            # Use string month to avoid timezone/Period warnings
            df["exit_month"] = exit_idx.strftime("%Y-%m")
            df["exit_weekday"] = exit_idx.day_name()
            df["exit_hour"] = exit_idx.hour

        if "entry_dt" in df.columns:
            entry_dt = pd.to_datetime(df["entry_dt"], utc=True, errors="coerce")
            entry_idx = pd.DatetimeIndex(entry_dt)
            df["entry_month"] = entry_idx.strftime("%Y-%m")
            df["entry_weekday"] = entry_idx.day_name()
            df["entry_hour"] = entry_idx.hour

        if "holding_seconds" in df.columns:
            # Simple buckets for quick tuning diagnostics
            bins = [
                -1,
                5 * 60,
                30 * 60,
                2 * 60 * 60,
                8 * 60 * 60,
                24 * 60 * 60,
                7 * 24 * 60 * 60,
                float("inf"),
            ]
            labels = [
                "<5m",
                "5-30m",
                "30m-2h",
                "2-8h",
                "8-24h",
                "1-7d",
                ">7d",
            ]
            df["holding_bucket"] = pd.cut(
                df["holding_seconds"].fillna(0), bins=bins, labels=labels
            )

        # Optional: attach market-regime context at trade entry
        if data is not None and "entry_time" in df.columns:
            try:
                bars = data.copy()
                if timestamp_col not in bars.columns or close_col not in bars.columns:
                    raise KeyError(
                        f"data must contain '{timestamp_col}' and '{close_col}' columns"
                    )

                bars = bars.sort_values(timestamp_col)
                bars_ts = pd.to_numeric(bars[timestamp_col], errors="coerce")
                bars_ts = bars_ts.astype("Int64").fillna(pd.NA)
                bars = bars.assign(_ts=bars_ts)
                bars = bars.dropna(subset=["_ts"]).copy()
                bars["_ts"] = bars["_ts"].astype(int)

                close = pd.to_numeric(bars[close_col], errors="coerce")

                # ATR%% (requires high/low; falls back gracefully)
                atr_pct = None
                if high_col in bars.columns and low_col in bars.columns:
                    high = pd.to_numeric(bars[high_col], errors="coerce")
                    low = pd.to_numeric(bars[low_col], errors="coerce")
                    prev_close = close.shift(1)
                    tr = pd.concat(
                        [
                            (high - low).abs(),
                            (high - prev_close).abs(),
                            (low - prev_close).abs(),
                        ],
                        axis=1,
                    ).max(axis=1)
                    atr = tr.rolling(window=int(atr_window), min_periods=1).mean()
                    atr_pct = (atr / close.replace(0, np.nan)).astype(float)

                # Realized volatility (returns std)
                rets = close.pct_change()
                vol = rets.rolling(window=int(vol_window), min_periods=2).std()

                # Trend regime (price vs SMA, and SMA slope)
                sma = close.rolling(window=int(trend_window), min_periods=1).mean()
                trend_up = (close > sma).astype(int)
                slope = sma - sma.shift(int(trend_slope_lookback))
                trend_slope_up = (slope > 0).astype(int)

                context_cols = {
                    "_ts": bars["_ts"],
                    "entry_close": close.astype(float),
                    "entry_vol": vol.astype(float),
                    "entry_trend_up": trend_up,
                    "entry_trend_slope_up": trend_slope_up,
                }
                if atr_pct is not None:
                    context_cols["entry_atr_pct"] = atr_pct

                context = pd.DataFrame(context_cols)
                context = context.sort_values("_ts")

                trades_ts = pd.to_numeric(df["entry_time"], errors="coerce")
                trades_ctx = pd.DataFrame({"entry_time": trades_ts}).dropna()
                trades_ctx["entry_time"] = trades_ctx["entry_time"].astype(int)

                merged = pd.merge_asof(
                    trades_ctx.sort_values("entry_time"),
                    context,
                    left_on="entry_time",
                    right_on="_ts",
                    direction="backward",
                    allow_exact_matches=True,
                ).drop(columns=["_ts"], errors="ignore")

                df = df.merge(merged, on="entry_time", how="left")

                # Buckets
                def _bucket_by_quantiles(
                    s: Optional[pd.Series], labels: list[str]
                ) -> pd.Series:
                    if s is None:
                        return pd.Series([pd.NA] * len(df), index=df.index)
                    s = pd.to_numeric(s, errors="coerce")
                    if s.isna().all():
                        return pd.Series([pd.NA] * len(s), index=s.index)
                    qs = s.quantile([0.33, 0.66]).tolist()
                    q1, q2 = float(qs[0]), float(qs[1])
                    if not np.isfinite(q1) or not np.isfinite(q2) or q1 == q2:
                        return pd.Series([labels[1]] * len(s), index=s.index)
                    bins = [-float("inf"), q1, q2, float("inf")]
                    return pd.cut(s, bins=bins, labels=labels)

                entry_vol_series = (
                    df["entry_vol"] if "entry_vol" in df.columns else None
                )
                df["entry_vol_bucket"] = _bucket_by_quantiles(
                    entry_vol_series, ["low", "mid", "high"]
                )
                if "entry_atr_pct" in df.columns:
                    entry_atr_series = df["entry_atr_pct"]
                    df["entry_atr_bucket"] = _bucket_by_quantiles(
                        entry_atr_series, ["low", "mid", "high"]
                    )

                def _safe_int(v: Any) -> Optional[int]:
                    try:
                        if v is None or (isinstance(v, float) and np.isnan(v)):
                            return None
                        return int(v)
                    except Exception:
                        return None

                def _trend_label(row: pd.Series) -> str:
                    up_i = _safe_int(row.get("entry_trend_up"))
                    slope_i = _safe_int(row.get("entry_trend_slope_up"))
                    if up_i is None or slope_i is None:
                        return "unknown"
                    if up_i == 1 and slope_i == 1:
                        return "uptrend"
                    if up_i == 1 and slope_i == 0:
                        return "uptrend_flat"
                    if up_i == 0 and slope_i == 0:
                        return "downtrend"
                    return "downtrend_flat"

                df["entry_trend"] = df.apply(_trend_label, axis=1).astype(str)
                df["entry_regime"] = (
                    df["entry_trend"].astype(str)
                    + ":vol="
                    + df["entry_vol_bucket"].astype(str)
                ).astype(str)
                if "entry_atr_bucket" in df.columns:
                    df["entry_regime"] = (
                        df["entry_regime"].astype(str)
                        + ":atr="
                        + df["entry_atr_bucket"].astype(str)
                    ).astype(str)
            except Exception:
                # Regime enrichment is best-effort; breakdowns still work without it.
                pass

        def _safe_profit_factor(gross_profit: float, gross_loss: float) -> float:
            if gross_loss > 0:
                return gross_profit / gross_loss
            if gross_profit > 0:
                return float("inf")
            return 0.0

        def _aggregate(group_col: str) -> pd.DataFrame:
            if group_col not in df.columns:
                return pd.DataFrame()

            g = df.groupby(group_col, dropna=False, observed=False)

            def _wins(x: pd.Series) -> int:
                return int((x > 0).sum())

            def _losses(x: pd.Series) -> int:
                return int((x < 0).sum())

            agg = g.agg(
                trades=("pnl", "count"),
                wins=("pnl", _wins),
                losses=("pnl", _losses),
                pnl_sum=("pnl", "sum"),
                pnl_mean=("pnl", "mean"),
                pnl_median=("pnl", "median"),
                pnl_std=("pnl", "std"),
            )

            if "holding_seconds" in df.columns:
                agg["avg_holding_seconds"] = g["holding_seconds"].mean()

            if "commission_amount" in df.columns:
                agg["commission_sum"] = g["commission_amount"].sum()

            # Gross profit/loss and PF
            gross_profit = g["pnl"].apply(lambda s: float(s[s > 0].sum()))
            gross_loss = g["pnl"].apply(lambda s: float(-s[s < 0].sum()))
            agg["gross_profit"] = gross_profit
            agg["gross_loss"] = gross_loss
            agg["profit_factor"] = [
                _safe_profit_factor(gp, gl)
                for gp, gl in zip(gross_profit.tolist(), gross_loss.tolist())
            ]

            agg["win_rate"] = np.where(
                agg["trades"] > 0, agg["wins"] / agg["trades"], 0.0
            )

            return agg.reset_index().sort_values(
                by=["pnl_sum"], ascending=False, kind="mergesort"
            )

        out: Dict[str, pd.DataFrame] = {}

        for name, col in (
            ("by_exit_reason", "exit_reason"),
            ("by_side", "side"),
            ("by_exit_month", "exit_month"),
            ("by_exit_weekday", "exit_weekday"),
            ("by_exit_hour", "exit_hour"),
            ("by_entry_month", "entry_month"),
            ("by_entry_weekday", "entry_weekday"),
            ("by_entry_hour", "entry_hour"),
            ("by_holding_bucket", "holding_bucket"),
            ("by_entry_vol_bucket", "entry_vol_bucket"),
            ("by_entry_atr_bucket", "entry_atr_bucket"),
            ("by_entry_trend", "entry_trend"),
            ("by_entry_regime", "entry_regime"),
        ):
            table = _aggregate(col)
            if not table.empty:
                out[name] = table

        return out

    def _make_dashboard_generator(
        self,
        initial_capital: Optional[float] = None,
        commission: Optional[float] = None,
        slippage: Optional[float] = None,
        contract_size: Optional[float] = None,
        use_intrabar_resolution: Optional[bool] = None,
    ):
        return rust_engine.DashboardGenerator(
            initial_capital=self.initial_capital
            if initial_capital is None
            else float(initial_capital),
            commission=self.commission if commission is None else float(commission),
            slippage=self.slippage if slippage is None else float(slippage),
            contract_size=self.contract_size
            if contract_size is None
            else float(contract_size),
            use_intrabar_resolution=self.use_intrabar_resolution
            if use_intrabar_resolution is None
            else bool(use_intrabar_resolution),
        )

    def dashboard(
        self,
        data: pd.DataFrame,
        intrabar_data: Optional[pd.DataFrame] = None,
        result=None,
        **dashboard_kwargs,
    ):
        """Generate dashboard data for the most recent run.

        Args:
            data: Main OHLCV dataframe used for the backtest.
            intrabar_data: Optional higher-resolution data for intrabar execution details.
            result: Optional BacktestResult; defaults to backtester.last_result.
            **dashboard_kwargs: Overrides for DashboardGenerator settings.

        Returns:
            DashboardResult produced by Rust DashboardGenerator.
        """
        bt_result = result if result is not None else self.last_result
        if bt_result is None:
            raise ValueError(
                "backtester.last_result is missing — run backtester.run(...) first or pass result=..."
            )

        generator = self._make_dashboard_generator(**dashboard_kwargs)

        try:
            if intrabar_data is not None:
                dashboard_result = generator.generate_dashboard(
                    bt_result, data, intrabar_data
                )
            else:
                dashboard_result = generator.generate_dashboard(bt_result, data)
        except TypeError:
            # Compatibility with older/newer signatures
            if intrabar_data is None:
                dashboard_result = generator.generate_dashboard(bt_result, data)
            else:
                dashboard_result = generator.generate_dashboard(bt_result, data)

        self.last_dashboard_result = dashboard_result
        return dashboard_result

    def plot(
        self,
        data: pd.DataFrame,
        intrabar_data: Optional[pd.DataFrame] = None,
        result=None,
        port: int = 8000,
        auto_open: bool = True,
        **dashboard_kwargs,
    ):
        """Generate + launch the web dashboard for the most recent run."""
        generator = self._make_dashboard_generator(**dashboard_kwargs)
        dashboard_result = self.dashboard(
            data=data,
            intrabar_data=intrabar_data,
            result=result,
            **dashboard_kwargs,
        )
        return generator.plot(
            dashboard_result, port=int(port), auto_open=bool(auto_open)
        )

    def _process_results(self, result) -> Dict:
        """Convert Rust result object to Python dictionary."""
        metrics = dict(getattr(result, "metrics", {}) or {})
        trade_analysis = dict(getattr(result, "trade_analysis", {}) or {})

        # Direct fields from BacktestResult
        total_return = getattr(result, "total_return", 0.0)
        initial_capital = getattr(result, "initial_capital", self.initial_capital)
        final_capital = getattr(result, "final_capital", None)
        total_commission = getattr(result, "total_commission", None)

        # Metrics from HashMap (keep legacy top-level keys)
        sharpe_ratio = metrics.get("sharpe_ratio", 0.0)
        max_drawdown = metrics.get("max_drawdown", 0.0)

        # Calculate win rate
        total_trades = getattr(result, "total_trades", 0)
        winning_trades = getattr(result, "winning_trades", 0)
        losing_trades = getattr(result, "losing_trades", 0)

        if total_trades > 0:
            win_rate = winning_trades / total_trades
        else:
            win_rate = 0.0

        # Handle equity curve (Rust Vec<f64> -> Python list)
        equity_curve = getattr(result, "equity_curve", [])
        equity_curve_timestamps = getattr(result, "equity_curve_timestamps", [])

        drawdown_series = getattr(result, "drawdown_series", [])
        daily_returns = getattr(result, "daily_returns", [])

        def _exit_reason_to_str(exit_reason: Any) -> str:
            if exit_reason is None:
                return "None"
            name = getattr(exit_reason, "name", None)
            if name:
                return str(name)
            return str(exit_reason)

        return {
            # Core summary
            "initial_capital": initial_capital,
            "final_capital": final_capital,
            "total_return": total_return,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "win_rate": win_rate,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            # Additional engine stats
            "total_commission": total_commission,
            "metrics": metrics,
            "trade_analysis": trade_analysis,
            "equity_curve": equity_curve,
            "equity_curve_timestamps": equity_curve_timestamps,
            "drawdown_series": [
                {
                    "timestamp": p.timestamp,
                    "drawdown": p.drawdown,
                }
                for p in (drawdown_series or [])
            ],
            "daily_returns": [
                {
                    "date": r.date,
                    "return_pct": r.return_pct,
                }
                for r in (daily_returns or [])
            ],
            "trades": [
                {
                    "entry_time": t.entry_time,
                    "exit_time": t.exit_time,
                    "entry_price": t.entry_price,
                    "exit_price": t.exit_price,
                    "pnl": t.pnl,
                    "returns": getattr(t, "returns", None),
                    "side": t.side,
                    "exit_reason": _exit_reason_to_str(getattr(t, "exit_reason", None)),
                    "contract_size": getattr(t, "contract_size", None),
                    "quantity": getattr(t, "quantity", None),
                    "commission_amount": getattr(t, "commission_amount", None),
                    "take_profit": getattr(t, "take_profit", None),
                    "stop_loss": getattr(t, "stop_loss", None),
                }
                for t in result.trades
            ],
        }
