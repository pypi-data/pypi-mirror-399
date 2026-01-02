"""Custom AdamW optimizer implementation."""

from __future__ import annotations

from typing import Any, Dict, Tuple

import jax
import jax.numpy as jnp

from ..objective import Objective


class AdamW:
    """AdamW optimizer with decoupled weight decay.

    Implements AdamW (Loshchilov & Hutter, 2017) using custom JAX code.
    AdamW applies weight decay AFTER the Adam update direction is computed,
    unlike L2 regularization which adds to the gradients.

    Args:
        objective: The objective to optimize
        learning_rate: Learning rate (default: 1e-3)
        beta1: Exponential decay rate for first moment (default: 0.9)
        beta2: Exponential decay rate for second moment (default: 0.999)
        eps: Small constant for numerical stability (default: 1e-8)
        weight_decay: Weight decay coefficient (default: 1e-2)

    Example:
        >>> objective = Objective(terms=[pde_term, bc_term])
        >>> optimizer = AdamW(objective, learning_rate=1e-3, weight_decay=1e-2)
        >>> state = optimizer.init(state)
        >>> for batch in train_data:
        ...     state, metrics = optimizer.step(state, batch)

    References:
        Loshchilov & Hutter (2017): Decoupled Weight Decay Regularization.
        https://arxiv.org/abs/1711.05101
    """

    def __init__(
        self,
        objective: Objective,
        learning_rate: float = 1e-3,
        beta1: float = 0.9,
        beta2: float = 0.999,
        eps: float = 1e-8,
        weight_decay: float = 1e-2,
    ):
        self.objective = objective
        self.learning_rate = learning_rate
        self.beta1 = beta1
        self.beta2 = beta2
        self.eps = eps
        self.weight_decay = weight_decay

    def init(
        self,
        state: Any,
        *,
        example_batch: Any = None,
        validate: bool = False,
    ) -> Any:
        """Initialize AdamW optimizer state.

        Args:
            state: TrainState with params
            example_batch: Optional example batch for validation
            validate: Whether to validate objective evaluation

        Returns:
            TrainState with initialized opt_state containing:
                - m: First moment estimates (momentum)
                - v: Second moment estimates (variance)
                - t: Step counter
        """
        # Initialize first and second moments as zeros
        m = jax.tree_util.tree_map(lambda p: jnp.zeros_like(p), state.params)
        v = jax.tree_util.tree_map(lambda p: jnp.zeros_like(p), state.params)
        t = jnp.array(0, dtype=jnp.int32)

        opt_state = {"m": m, "v": v, "t": t}
        return state.replace(opt_state=opt_state)

    def step(
        self,
        state: Any,
        batch: Dict[str, Any],
    ) -> Tuple[Any, Dict[str, Any]]:
        """Perform one AdamW optimization step.

        Args:
            state: TrainState with params, opt_state, apply_fn, step
            batch: Batch dict

        Returns:
            (new_state, metrics) tuple where metrics includes loss and term losses
        """

        def loss_fn(params):
            variables = {"params": params}
            if hasattr(state, "batch_stats") and state.batch_stats is not None:
                variables["batch_stats"] = state.batch_stats

            metrics = self.objective.evaluate(
                apply_fn=state.apply_fn,
                variables=variables,
                batch=batch,
                step=state.step,
            )
            return metrics["loss"], metrics

        # Compute gradients
        (loss, metrics), grads = jax.value_and_grad(loss_fn, has_aux=True)(state.params)

        # Extract optimizer state
        m = state.opt_state["m"]
        v = state.opt_state["v"]
        t = state.opt_state["t"] + 1

        # Update biased first moment estimate
        m_new = jax.tree_util.tree_map(
            lambda m_i, g: self.beta1 * m_i + (1.0 - self.beta1) * g,
            m,
            grads,
        )

        # Update biased second raw moment estimate
        v_new = jax.tree_util.tree_map(
            lambda v_i, g: self.beta2 * v_i + (1.0 - self.beta2) * (g * g),
            v,
            grads,
        )

        # Compute bias-corrected first moment estimate
        m_hat = jax.tree_util.tree_map(
            lambda m_i: m_i / (1.0 - self.beta1**t),
            m_new,
        )

        # Compute bias-corrected second raw moment estimate
        v_hat = jax.tree_util.tree_map(
            lambda v_i: v_i / (1.0 - self.beta2**t),
            v_new,
        )

        # Compute Adam update direction
        direction = jax.tree_util.tree_map(
            lambda m_h, v_h: m_h / (jnp.sqrt(v_h) + self.eps),
            m_hat,
            v_hat,
        )

        # AdamW: Apply decoupled weight decay THEN gradient update
        # p_new = p * (1 - lr * wd) - lr * direction
        new_params = jax.tree_util.tree_map(
            lambda p, d: p * (1.0 - self.learning_rate * self.weight_decay)
            - self.learning_rate * d,
            state.params,
            direction,
        )

        # Update optimizer state
        new_opt_state = {"m": m_new, "v": v_new, "t": t}

        # Create new training state
        new_state = state.replace(
            step=state.step + 1,
            params=new_params,
            opt_state=new_opt_state,
        )

        return new_state, metrics
