"""Shared utility functions for custom optimizers.

Pure JAX functions for common optimizer operations. All functions are
jittable and have no side effects.
"""

from __future__ import annotations

import jax
import jax.numpy as jnp
from typing import Any


def clip_gradients(grads: Any, max_norm: float) -> Any:
    """Clip gradients by global norm.

    Args:
        grads: Gradient pytree
        max_norm: Maximum global norm

    Returns:
        Clipped gradient pytree
    """
    global_norm = jnp.sqrt(
        sum(jnp.sum(jnp.square(g)) for g in jax.tree_util.tree_leaves(grads))
    )
    scale = jnp.minimum(1.0, max_norm / (global_norm + 1e-8))
    return jax.tree_util.tree_map(lambda g: g * scale, grads)


def normalize_gradients(grads: Any) -> Any:
    """Normalize gradients to unit norm.

    Args:
        grads: Gradient pytree

    Returns:
        Normalized gradient pytree with global norm = 1
    """
    global_norm = jnp.sqrt(
        sum(jnp.sum(jnp.square(g)) for g in jax.tree_util.tree_leaves(grads))
    )
    return jax.tree_util.tree_map(lambda g: g / (global_norm + 1e-8), grads)


def apply_momentum(grads: Any, momentum_state: Any, beta: float) -> Any:
    """Apply momentum: m = beta * m + (1-beta) * g

    Args:
        grads: Current gradients
        momentum_state: Previous momentum state
        beta: Momentum coefficient

    Returns:
        Updated momentum state
    """
    return jax.tree_util.tree_map(
        lambda m, g: beta * m + (1.0 - beta) * g,
        momentum_state,
        grads,
    )


def apply_nesterov(grads: Any, momentum_state: Any, beta: float) -> tuple[Any, Any]:
    """Apply Nesterov momentum.

    Computes velocity and Nesterov lookahead direction.

    Args:
        grads: Current gradients
        momentum_state: Previous velocity state
        beta: Momentum coefficient

    Returns:
        (nesterov_direction, new_velocity) tuple
    """
    # Update velocity: v_new = beta * v + grads
    new_velocity = jax.tree_util.tree_map(
        lambda v, g: beta * v + g,
        momentum_state,
        grads,
    )

    # Nesterov lookahead: direction = beta * v_new + grads
    direction = jax.tree_util.tree_map(
        lambda v, g: beta * v + g,
        new_velocity,
        grads,
    )

    return direction, new_velocity


def bias_correction(moment: Any, beta: float, step: jnp.ndarray) -> Any:
    """Apply bias correction: m_hat = m / (1 - beta^t)

    Args:
        moment: Moment to correct (first or second)
        beta: Decay coefficient (beta1 or beta2)
        step: Current step counter (jax.Array)

    Returns:
        Bias-corrected moment
    """
    correction_factor = 1.0 - jnp.power(beta, step)
    return jax.tree_util.tree_map(lambda m: m / correction_factor, moment)


def adam_update(
    grads: Any,
    m: Any,
    v: Any,
    beta1: float,
    beta2: float,
    eps: float,
    step: jnp.ndarray,
) -> tuple[Any, tuple[Any, Any]]:
    """Compute Adam update direction.

    Args:
        grads: Current gradients
        m: First moment
        v: Second moment
        beta1: First moment decay
        beta2: Second moment decay
        eps: Numerical stability epsilon
        step: Current step counter

    Returns:
        (direction, (new_m, new_v)) tuple
    """
    # Update moments
    m_new = jax.tree_util.tree_map(
        lambda m_i, g: beta1 * m_i + (1.0 - beta1) * g, m, grads
    )
    v_new = jax.tree_util.tree_map(
        lambda v_i, g: beta2 * v_i + (1.0 - beta2) * (g * g), v, grads
    )

    # Bias correction
    m_hat = bias_correction(m_new, beta1, step)
    v_hat = bias_correction(v_new, beta2, step)

    # Adam direction
    direction = jax.tree_util.tree_map(
        lambda m_h, v_h: m_h / (jnp.sqrt(v_h) + eps),
        m_hat,
        v_hat,
    )

    return direction, (m_new, v_new)


def apply_weight_decay(params: Any, learning_rate: float, weight_decay: float) -> Any:
    """Apply decoupled weight decay (AdamW style).

    Args:
        params: Parameter pytree
        learning_rate: Learning rate
        weight_decay: Weight decay coefficient

    Returns:
        Parameters with weight decay applied: p * (1 - lr * wd)
    """
    return jax.tree_util.tree_map(
        lambda p: p * (1.0 - learning_rate * weight_decay),
        params,
    )
