import os

import torch
import torch.nn as nn

try:
    from stable_baselines3.common.policies import ActorCriticPolicy
except ImportError:
    ActorCriticPolicy = object  # Fallback if SB3 not installed


class MarketPPOPolicy(
    ActorCriticPolicy if ActorCriticPolicy is not object else nn.Module
):
    """
    Optimized MLP policy for financial time-series data.

    Features:
    - Layer-normalization for stable training on non-stationary price data.
    - Orthogonal initialization for better gradient flow.
    - Configurable network depth and width.
    """

    def __init__(self, *args, **kwargs):
        if ActorCriticPolicy is not object:
            # If using SB3, we'll configure the net_arch via kwargs
            if "net_arch" not in kwargs:
                kwargs["net_arch"] = dict(pi=[128, 128], vf=[128, 128])
            if "ortho_init" not in kwargs:
                kwargs["ortho_init"] = True
            super().__init__(*args, **kwargs)
        else:
            super().__init__()
            # Minimal torch implementation if SB3 is missing
            self.pi = nn.Sequential(
                nn.Linear(64, 128),
                nn.LayerNorm(128),
                nn.ReLU(),
                nn.Linear(128, 128),
                nn.LayerNorm(128),
                nn.ReLU(),
                nn.Linear(128, 3),
            )
            self.vf = nn.Sequential(
                nn.Linear(64, 128),
                nn.LayerNorm(128),
                nn.ReLU(),
                nn.Linear(128, 1),
            )

    def save_weights(self, path: str):
        """Save policy weights for transfer learning."""
        torch.save(self.state_dict(), path)

    def load_weights(self, path: str):
        """Load policy weights."""
        if os.path.exists(path):
            self.load_state_dict(torch.load(path))
        else:
            raise FileNotFoundError(f"Weight file not found: {path}")


class MarketGNNPolicy(nn.Module):
    """
    Pre-configured Graph Neural Network policy for multi-asset correlation.

    Optimized for RLX graph observations where:
    - Nodes represent historical bars or account state.
    - Edges represent temporal or cross-asset connections.
    """

    def __init__(self, in_channels=5, hidden_channels=128, out_channels=3):
        super().__init__()
        self.conv1 = nn.Linear(in_channels, hidden_channels)
        self.layernorm1 = nn.LayerNorm(hidden_channels)
        self.conv2 = nn.Linear(hidden_channels, hidden_channels)
        self.layernorm2 = nn.LayerNorm(hidden_channels)
        self.fc = nn.Linear(hidden_channels, hidden_channels)

        self.actor = nn.Linear(hidden_channels, out_channels)
        self.critic = nn.Linear(hidden_channels, 1)

    def forward(self, x, edge_index):
        # Optimized Message Passing (simplified for demo/base)
        # In a full implementation, we'd use torch_geometric.nn layers
        adj = torch.zeros((x.size(0), x.size(0)), device=x.device)
        adj[edge_index[0], edge_index[1]] = 1.0
        adj = adj + torch.eye(x.size(0), device=x.device)
        deg = torch.sum(adj, dim=1)
        norm_adj = adj / deg.view(-1, 1)

        h = torch.mm(norm_adj, x)
        h = torch.relu(self.layernorm1(self.conv1(h)))
        h = torch.mm(norm_adj, h)
        h = torch.relu(self.layernorm2(self.conv2(h)))

        # Latent extraction from the Account node (assumed to be the last node)
        latent = torch.relu(self.fc(h[-1]))

        return self.actor(latent), self.critic(latent)

    def save_weights(self, path: str):
        torch.save(self.state_dict(), path)

    def load_weights(self, path: str):
        self.load_state_dict(torch.load(path))
