"""Graph Convolutional Network (GCN) layers.

Implementation based on Kipf & Welling (2017):
"Semi-Supervised Classification with Graph Convolutional Networks"
https://arxiv.org/abs/1609.02907

Key formula: H' = sigma(D_tilde^(-1/2) A_tilde D_tilde^(-1/2) H W)
where A_tilde = A + I (adjacency with self-loops)
      D_tilde = degree matrix of A_tilde
"""

from __future__ import annotations

from typing import Callable, Optional

import jax.numpy as jnp
from flax import linen as nn


def normalize_adjacency(adj: jnp.ndarray, add_self_loops: bool = True) -> jnp.ndarray:
    """Compute symmetric normalized adjacency matrix.

    Args:
        adj: Adjacency matrix (N, N), can be weighted
        add_self_loops: If True, add self-loops (A_tilde = A + I)

    Returns:
        Normalized adjacency: D^(-1/2) A D^(-1/2)
    """
    if add_self_loops:
        adj = adj + jnp.eye(adj.shape[0], dtype=adj.dtype)

    # Compute degree
    deg = adj.sum(axis=1)
    deg_inv_sqrt = jnp.where(deg > 0, deg**-0.5, 0.0)

    # D^(-1/2) A D^(-1/2)
    return deg_inv_sqrt[:, None] * adj * deg_inv_sqrt[None, :]


class GCNLayer(nn.Module):
    """Single Graph Convolutional Layer.

    Args:
        features: Output feature dimension
        use_bias: Whether to add bias term
        activation: Activation function (default: relu)
        add_self_loops: If True, add self-loops before normalization
        normalize: If True, apply symmetric normalization

    Example:
        >>> layer = GCNLayer(features=64)
        >>> x = jnp.ones((100, 32))  # 100 nodes, 32 features
        >>> adj = jnp.eye(100)  # adjacency matrix
        >>> y = layer(x, adj)  # (100, 64)
    """

    features: int
    use_bias: bool = True
    activation: Optional[Callable] = nn.relu
    add_self_loops: bool = True
    normalize: bool = True

    @nn.compact
    def __call__(self, x: jnp.ndarray, adj: jnp.ndarray) -> jnp.ndarray:
        """Forward pass.

        Args:
            x: Node features (N, F_in)
            adj: Adjacency matrix (N, N)

        Returns:
            Updated node features (N, features)
        """
        # Normalize adjacency if requested
        if self.normalize:
            adj_norm = normalize_adjacency(adj, add_self_loops=self.add_self_loops)
        elif self.add_self_loops:
            adj_norm = adj + jnp.eye(adj.shape[0], dtype=adj.dtype)
        else:
            adj_norm = adj

        # Linear transform: X @ W
        x = nn.Dense(self.features, use_bias=self.use_bias)(x)

        # Aggregate neighbors: A_norm @ X
        x = adj_norm @ x

        # Apply activation
        if self.activation is not None:
            x = self.activation(x)

        return x


class GCN(nn.Module):
    """Graph Convolutional Network (stacked GCN layers).

    Args:
        hidden_features: List of hidden layer dimensions
        out_features: Output dimension (e.g., number of classes)
        dropout_rate: Dropout rate between layers
        add_self_loops: If True, add self-loops in each layer
        normalize: If True, apply symmetric normalization

    Example:
        >>> model = GCN(hidden_features=[64, 32], out_features=7)
        >>> x = jnp.ones((100, 1433))  # Cora: 100 nodes, 1433 features
        >>> adj = jnp.eye(100)
        >>> y = model(x, adj, training=True)  # (100, 7)
    """

    hidden_features: tuple[int, ...]
    out_features: int
    dropout_rate: float = 0.5
    add_self_loops: bool = True
    normalize: bool = True

    @nn.compact
    def __call__(
        self, x: jnp.ndarray, adj: jnp.ndarray, training: bool = False
    ) -> jnp.ndarray:
        """Forward pass.

        Args:
            x: Node features (N, F_in)
            adj: Adjacency matrix (N, N)
            training: If True, apply dropout

        Returns:
            Node logits (N, out_features)
        """
        # Hidden layers
        for features in self.hidden_features:
            x = GCNLayer(
                features=features,
                add_self_loops=self.add_self_loops,
                normalize=self.normalize,
            )(x, adj)
            if training and self.dropout_rate > 0:
                x = nn.Dropout(rate=self.dropout_rate, deterministic=not training)(x)

        # Output layer (no activation)
        x = GCNLayer(
            features=self.out_features,
            activation=None,
            add_self_loops=self.add_self_loops,
            normalize=self.normalize,
        )(x, adj)

        return x
