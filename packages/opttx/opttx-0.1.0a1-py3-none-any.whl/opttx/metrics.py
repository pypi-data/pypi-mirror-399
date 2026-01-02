"""Metrics validation utilities for OptTx V2."""

from __future__ import annotations

from typing import Any, Dict

import jax


def ensure_loss_key(metrics: Dict[str, Any]) -> None:
    """Ensure metrics dict contains 'loss' key.

    Args:
        metrics: Metrics dictionary

    Raises:
        ValueError: If 'loss' key is missing
    """
    if "loss" not in metrics:
        raise ValueError("Metrics must contain 'loss' key")


def ensure_metrics_are_scalar(metrics: Dict[str, Any]) -> None:
    """Ensure all metric values are scalars.

    Args:
        metrics: Metrics dictionary

    Raises:
        ValueError: If any metric value is not scalar
    """
    for key, value in metrics.items():
        if not isinstance(value, jax.Array):
            continue  # Will be caught by ensure_metrics_are_jax_arrays
        if value.shape != ():
            raise ValueError(f"Metric '{key}' must be scalar, got shape {value.shape}")


def ensure_metrics_are_jax_arrays(metrics: Dict[str, Any]) -> None:
    """Ensure all metric values are JAX arrays.

    Args:
        metrics: Metrics dictionary

    Raises:
        ValueError: If any metric value is not a JAX array
    """
    for key, value in metrics.items():
        if not isinstance(value, jax.Array):
            raise ValueError(f"Metric '{key}' must be a jax.Array, got {type(value)}")


def ensure_metrics_static_and_scalar(metrics: Any) -> None:
    """Ensure metrics are a dict with static keys and scalar JAX array values.

    This is the main validation function for metrics in OptTx V2.
    It enforces:
    1. Metrics must be a dict
    2. All values must be JAX arrays
    3. All values must be scalars

    Args:
        metrics: Metrics to validate

    Raises:
        TypeError: If metrics is not a dict
        ValueError: If validation fails
    """
    if not isinstance(metrics, dict):
        raise TypeError(f"Metrics must be a dict, got {type(metrics)}")

    ensure_metrics_are_jax_arrays(metrics)
    ensure_metrics_are_scalar(metrics)
