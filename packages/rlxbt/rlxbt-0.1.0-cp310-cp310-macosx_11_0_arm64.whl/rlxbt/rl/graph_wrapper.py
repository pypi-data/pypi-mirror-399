from typing import Any

import gymnasium as gym
import numpy as np

try:
    import torch
    from torch_geometric.data import Data

    HAS_PYG = True
except ImportError:
    HAS_PYG = False


class RlxGraphObservationWrapper(gym.ObservationWrapper):
    """
    Wrapper that extracts graph-based features from the RLXBT environment.
    Converts the internal Rust graph representation into PyTorch Geometric Data objects.

    Nodes:
    - Type 0: Price Bars (OHLCV)
    - Type 1: Account State (Portfolio Value, Position, etc.)

    Edges:
    - Temporal links between consecutive price bars.
    - Causal link between the latest bar and the account state.
    """

    def __init__(self, env):
        super().__init__(env)

        # We redefine the observation space to be a Dict or a custom object
        # For simplicity in many RL frameworks, we might just return the raw Dict
        # but here we provide a method to get PyG Data objects.
        self.observation_space = gym.spaces.Dict(
            {
                "x": gym.spaces.Box(
                    low=-np.inf,
                    high=np.inf,
                    shape=(env.window_size + 1, 5),
                    dtype=np.float32,
                ),
                "edge_index": gym.spaces.Box(
                    low=0,
                    high=env.window_size,
                    shape=(2, env.window_size),
                    dtype=np.int64,
                ),
                "node_types": gym.spaces.Box(
                    low=0, high=1, shape=(env.window_size + 1,), dtype=np.int64
                ),
            }
        )

    def observation(self, obs):
        """
        Interprets the standard vector observation as a graph structured observation.
        """
        # Call the underlying rust environment to get the structured graph
        graph_data = self.env.get_graph_observation()
        return graph_data

    def get_pyg_data(self) -> Any:
        """
        Helper to get the current observation as a PyTorch Geometric Data object.
        """
        if not HAS_PYG:
            raise ImportError(
                "torch_geometric is required for get_pyg_data(). Run 'pip install torch-geometric'"
            )

        graph_data = self.env.get_graph_observation()

        x = torch.from_numpy(graph_data["x"])
        edge_index = torch.from_numpy(graph_data["edge_index"])
        node_types = torch.from_numpy(graph_data["node_types"])

        return Data(x=x, edge_index=edge_index, node_type=node_types)

    def get_backtest_result(self):
        """Delegate to underlying environment"""
        return self.env.get_backtest_result()

    def get_graph_observation(self):
        """Delegate to underlying environment"""
        return self.env.get_graph_observation()


def wrap_for_graph_rl(env):
    """
    Convenience function to wrap an RlxEnv with the Graph Observer.
    """
    return RlxGraphObservationWrapper(env)
