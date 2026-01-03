import sys
from typing import Dict, Optional, Tuple

import gymnasium as gym
import numpy as np
import pandas as pd
from gymnasium import spaces

try:
    from . import rlx
    from .core import get_license_key
except ImportError:
    # Fallback if running directly or if relative import fails
    try:
        from rlxbt import rlx
        from rlxbt.core import get_license_key
    except ImportError:
        print("❌ Failed to import RLX. Please run 'maturin develop' first.")
        sys.exit(1)


class RlxEnv(gym.Env):
    """
    Gymnasium environment for RLX Trading Engine.

    Note: RLEnvironment requires Pro plan or higher for production use.
    """

    metadata = {"render_modes": ["human"]}

    def __init__(
        self,
        data: pd.DataFrame,
        initial_capital: float = 100000.0,
        window_size: int = 20,
        exit_rules: Optional[Dict] = None,
        license_key: Optional[str] = None,
        reward_type: str = "PortfolioReturn",
        reward_multiplier: float = 1.0,
        risk_free_rate: float = 0.0,
        use_continuous_actions: bool = False,
    ):
        super().__init__()

        self.window_size = window_size
        self.initial_capital = initial_capital
        self.use_continuous_actions = use_continuous_actions

        # Map reward type string to Rust enum
        rt_map = {
            "PortfolioReturn": rlx.RewardType.PortfolioReturn,
            "LogReturn": rlx.RewardType.LogReturn,
            "SharpeRatio": rlx.RewardType.SharpeRatio,
            "CalmarRatio": rlx.RewardType.CalmarRatio,
            "RiskAdjustedReturn": rlx.RewardType.RiskAdjustedReturn,
        }
        rust_reward_type = rt_map.get(reward_type, rlx.RewardType.PortfolioReturn)

        # Configure Exit Controller if rules provided
        exit_controller = None
        if exit_rules:
            rules = rlx.ExitRules(
                hold_bars=exit_rules.get("hold_bars"),
                exit_at_night=exit_rules.get("exit_at_night"),
                max_hold_minutes=exit_rules.get("max_hold_minutes"),
                night_start_hour=exit_rules.get("night_start_hour"),
                night_end_hour=exit_rules.get("night_end_hour"),
                max_drawdown_percent=exit_rules.get("max_drawdown_percent"),
                min_profit_percent=exit_rules.get("min_profit_percent"),
                custom_rules=None,
            )
            exit_controller = rlx.ExitController(rules)

        # Initialize Rust Environment
        resolved_license_key = get_license_key(license_key)

        self.rust_env = rlx.RLEnvironment(
            initial_capital=initial_capital,
            commission=0.001,  # Adding small commission for realism
            slippage=0.0005,
            window_size=window_size,
            exit_controller=exit_controller,
            license_key=resolved_license_key,
            reward_type=rust_reward_type,
            reward_multiplier=reward_multiplier,
            risk_free_rate=risk_free_rate,
        )

        # Load data into Rust engine
        self.rust_env.load_data(data)

        # Define Action Space
        if use_continuous_actions:
            # -1 = Short, 0 = Neutral, 1 = Long
            self.action_space = spaces.Box(
                low=-1.0, high=1.0, shape=(1,), dtype=np.float32
            )
        else:
            # 0=Neutral, 1=Long, 2=Short
            self.action_space = spaces.Discrete(3)

        # Define Observation Space
        # [Open, High, Low, Close, Volume] * window_size + [PortfolioValue, PositionSize, IsOpen]
        obs_dim = window_size * 5 + 3
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float64
        )

    def reset(
        self, seed: Optional[int] = None, options: Optional[Dict] = None
    ) -> Tuple[np.ndarray, Dict]:
        super().reset(seed=seed)

        obs, info = self.rust_env.reset()
        return np.array(obs, dtype=np.float64), info

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        obs, reward, done, truncated, info = self.rust_env.step(action)
        return np.array(obs, dtype=np.float64), reward, done, truncated, info

    def get_backtest_result(self):
        """
        Returns the full BacktestResult object from the Rust environment.
        """
        return self.rust_env.get_backtest_result()

    def get_graph_observation(self) -> Dict[str, np.ndarray]:
        """
        Returns the current market state as a graph observation.
        Suitable for GNN-based RL agents.
        """
        data = self.rust_env.get_graph_observation()
        # Convert to numpy for convenience
        return {
            "x": np.array(data["x"], dtype=np.float32),
            "edge_index": np.array(data["edge_index"], dtype=np.int64).T,
            "node_types": np.array(data["node_types"], dtype=np.int64),
        }

    def render(self):
        pass


class RlxMultiAssetEnv(gym.Env):
    """
    Multi-Asset Gymnasium environment for RLX.
    Supports trading multiple symbols simultaneously.
    """

    metadata = {"render_modes": ["human"]}

    def __init__(
        self,
        data: Dict[str, pd.DataFrame],
        initial_capital: float = 100000.0,
        window_size: int = 20,
        reward_type: str = "PortfolioReturn",
        reward_multiplier: float = 1.0,
        risk_free_rate: float = 0.0,
        use_continuous_actions: bool = True,
    ):
        super().__init__()

        self.symbols = list(data.keys())
        self.num_assets = len(self.symbols)
        self.window_size = window_size
        self.initial_capital = initial_capital

        # Map reward type
        rt_map = {
            "PortfolioReturn": rlx.RewardType.PortfolioReturn,
            "LogReturn": rlx.RewardType.LogReturn,
            "SharpeRatio": rlx.RewardType.SharpeRatio,
        }
        rust_reward_type = rt_map.get(reward_type, rlx.RewardType.PortfolioReturn)

        # Initialize Rust Environment
        self.rust_env = rlx.MultiAssetRLEnvironment(
            symbols=self.symbols,
            initial_capital=initial_capital,
            commission=0.001,
            slippage=0.0005,
            window_size=window_size,
            reward_type=rust_reward_type,
            reward_multiplier=reward_multiplier,
            risk_free_rate=risk_free_rate,
        )

        # Load data for each symbol
        for symbol, df in data.items():
            self.rust_env.load_data(symbol, df)

        # Action Space: Vector of continuous weights [-1, 1] for each asset
        self.action_space = spaces.Box(
            low=-1.0, high=1.0, shape=(self.num_assets,), dtype=np.float32
        )

        # Observation Space: [num_assets * window_size * 5] + [PortfolioValue, PositionSummary]
        obs_dim = self.num_assets * window_size * 5 + 2
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float64
        )

    def reset(
        self, seed: Optional[int] = None, options: Optional[Dict] = None
    ) -> Tuple[np.ndarray, Dict]:
        super().reset(seed=seed)
        obs, info = self.rust_env.reset()
        return np.array(obs, dtype=np.float64), info

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        # action is expected to be a numpy array/list of floats
        obs, reward, done, truncated, info = self.rust_env.step(action.tolist())
        return np.array(obs, dtype=np.float64), reward, done, truncated, info

    def get_graph_observation(self) -> Dict[str, np.ndarray]:
        """
        Returns a multi-asset graph observation.
        """
        data = self.rust_env.get_graph_observation()
        return {
            "x": np.array(data["x"], dtype=np.float32),
            "edge_index": np.array(data["edge_index"], dtype=np.int64).T,
            "node_types": np.array(data["node_types"], dtype=np.int64),
        }

    def render(self):
        pass
