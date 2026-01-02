"""Graph Attention Network (GAT) layers.

Implementation based on Velickovic et al. (2018):
"Graph Attention Networks"
https://arxiv.org/abs/1710.10903

Key features:
- Attention mechanism for neighbor aggregation
- LeakyReLU with alpha=0.2 for attention coefficients
- Multi-head attention support
"""

from __future__ import annotations

from typing import Callable, Optional

import jax.numpy as jnp
from flax import linen as nn


class GATLayer(nn.Module):
    """Single Graph Attention Layer.

    Args:
        features: Output feature dimension per head
        num_heads: Number of attention heads
        concat_heads: If True, concatenate heads; else average
        dropout_rate: Dropout rate for attention coefficients
        negative_slope: Negative slope for LeakyReLU (default: 0.2)
        add_self_loops: If True, add self-loops to adjacency

    Example:
        >>> layer = GATLayer(features=8, num_heads=8)
        >>> x = jnp.ones((100, 32))  # 100 nodes, 32 features
        >>> adj = jnp.eye(100)
        >>> y = layer(x, adj)  # (100, 64) if concat, (100, 8) if average
    """

    features: int
    num_heads: int = 1
    concat_heads: bool = True
    dropout_rate: float = 0.0
    negative_slope: float = 0.2
    add_self_loops: bool = True

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
            Updated node features (N, num_heads * features) if concat
            or (N, features) if average
        """
        N = x.shape[0]

        # Add self-loops
        if self.add_self_loops:
            adj = adj + jnp.eye(N, dtype=adj.dtype)

        # Linear transform for all heads: (N, F_in) -> (N, H, F)
        h = nn.Dense(self.features * self.num_heads, use_bias=False)(x)
        h = h.reshape(N, self.num_heads, self.features)  # (N, H, F)

        # Compute attention coefficients
        # a_src[i] and a_dst[j] are combined to get attention for edge (i, j)
        a_src = nn.Dense(1, use_bias=False, name="attn_src")(h)  # (N, H, 1)
        a_dst = nn.Dense(1, use_bias=False, name="attn_dst")(h)  # (N, H, 1)

        # e[i, j, h] = LeakyReLU(a_src[i, h] + a_dst[j, h])
        # Broadcast: (N, H, 1) + (N, H, 1).T -> need to be careful with dims
        # a_src: (N, H, 1), a_dst: (N, H, 1)
        # We want e[i, j, h] = a_src[i, h] + a_dst[j, h]
        # So: (N, 1, H, 1) + (1, N, H, 1) -> (N, N, H, 1) -> squeeze -> (N, N, H)
        e = a_src[:, None, :, :] + a_dst[None, :, :, :]  # (N, N, H, 1)
        e = e.squeeze(-1)  # (N, N, H)
        e = nn.leaky_relu(e, negative_slope=self.negative_slope)

        # Mask non-edges with large negative value
        mask = adj == 0  # (N, N)
        e = jnp.where(mask[:, :, None], -1e9, e)  # (N, N, H)

        # Softmax over neighbors (axis=1 for source nodes)
        alpha = nn.softmax(e, axis=1)  # (N, N, H)

        # Dropout on attention coefficients
        if training and self.dropout_rate > 0:
            alpha = nn.Dropout(rate=self.dropout_rate, deterministic=not training)(
                alpha
            )

        # Aggregate: out[i, h, f] = sum_j alpha[i, j, h] * h[j, h, f]
        # alpha: (N, N, H), h: (N, H, F) -> need einsum
        out = jnp.einsum("ijh,jhf->ihf", alpha, h)  # (N, H, F)

        # Combine heads
        if self.concat_heads:
            return out.reshape(N, -1)  # (N, H * F)
        else:
            return out.mean(axis=1)  # (N, F)


class GAT(nn.Module):
    """Graph Attention Network (stacked GAT layers).

    Args:
        hidden_features: List of (features, num_heads) tuples for hidden layers
        out_features: Output dimension (e.g., number of classes)
        out_heads: Number of heads for output layer (usually 1)
        dropout_rate: Dropout rate for features and attention
        add_self_loops: If True, add self-loops in each layer

    Example:
        >>> model = GAT(
        ...     hidden_features=[(8, 8)],  # 8 features x 8 heads = 64 hidden
        ...     out_features=7,
        ...     out_heads=1
        ... )
        >>> x = jnp.ones((100, 1433))  # Cora
        >>> adj = jnp.eye(100)
        >>> y = model(x, adj, training=True)  # (100, 7)
    """

    hidden_features: tuple[tuple[int, int], ...]
    out_features: int
    out_heads: int = 1
    dropout_rate: float = 0.6
    add_self_loops: bool = True

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
        # Input dropout
        if training and self.dropout_rate > 0:
            x = nn.Dropout(rate=self.dropout_rate, deterministic=not training)(x)

        # Hidden layers (concat heads, then ELU)
        for features, num_heads in self.hidden_features:
            x = GATLayer(
                features=features,
                num_heads=num_heads,
                concat_heads=True,
                dropout_rate=self.dropout_rate if training else 0.0,
                add_self_loops=self.add_self_loops,
            )(x, adj, training=training)
            x = nn.elu(x)

            if training and self.dropout_rate > 0:
                x = nn.Dropout(rate=self.dropout_rate, deterministic=not training)(x)

        # Output layer (average heads, no activation)
        x = GATLayer(
            features=self.out_features,
            num_heads=self.out_heads,
            concat_heads=False,  # Average for output
            dropout_rate=0.0,  # No dropout on output attention
            add_self_loops=self.add_self_loops,
        )(x, adj, training=training)

        return x
