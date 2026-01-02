"""Graph Neural Network models for Flax.

This module provides GCN and GAT implementations that work with
standard Flax training loops and OptTx optimizers.
"""

from .gcn import GCN, GCNLayer, normalize_adjacency
from .gat import GAT, GATLayer

__all__ = [
    "GCN",
    "GCNLayer",
    "GAT",
    "GATLayer",
    "normalize_adjacency",
]
