"""Custom MUON optimizer implementation.

MUON (MomentUm Orthogonalized by Newton-schulz) applies Newton-Schulz
orthogonalization to momentum updates for 2D parameters, with AdamW-style
updates for non-2D parameters.

References:
    https://kellerjordan.github.io/posts/muon/
    Optax contrib implementation
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import jax
import jax.numpy as jnp

from ..objective import Objective


def _newton_schulz(
    X: jnp.ndarray,
    steps: int,
    eps: float,
    ns_a: float,
    ns_b: float,
    ns_c: float,
) -> jnp.ndarray:
    """Apply Newton-Schulz iteration to orthogonalize a matrix.

    Args:
        X: Input matrix to orthogonalize
        steps: Number of Newton-Schulz iterations
        eps: Small value for numerical stability
        ns_a, ns_b, ns_c: Newton-Schulz coefficients

    Returns:
        Orthogonalized matrix with same shape as input
    """
    # Normalize input
    X_norm = jnp.linalg.norm(X)
    X = X / jnp.maximum(X_norm, eps)

    # Handle rectangular matrices by working with smaller dimension
    transpose_flag = X.shape[0] > X.shape[1]

    def process_matrix(X_in: jnp.ndarray) -> jnp.ndarray:
        """Apply Newton-Schulz iterations."""

        def ns_step(X_curr: jnp.ndarray, _: Any) -> Tuple[jnp.ndarray, None]:
            A = X_curr @ X_curr.T
            B = ns_b * A + ns_c * (A @ A)
            X_new = ns_a * X_curr + B @ X_curr
            return X_new, None

        X_out, _ = jax.lax.scan(ns_step, X_in, jnp.arange(steps))
        return X_out

    # Process with appropriate orientation
    X_processed = jax.lax.cond(
        transpose_flag,
        lambda x: process_matrix(x.T).T,
        lambda x: process_matrix(x),
        X,
    )

    return X_processed


class MUON:
    """MUON optimizer with Newton-Schulz orthogonalization for 2D parameters.

    2D parameters use momentum with Newton-Schulz orthogonalization.
    Non-2D parameters use AdamW-style updates with special Nesterov momentum.

    Args:
        objective: The objective to optimize
        learning_rate: Learning rate (default: 2e-2)
        beta: Momentum decay for 2D parameters (default: 0.95)
        beta1_1d: First moment decay for non-2D parameters (default: 0.9)
        beta2_1d: Second moment decay for non-2D parameters (default: 0.999)
        ns_steps: Number of Newton-Schulz iterations (default: 5)
        nesterov: Whether to use Nesterov momentum (default: True)
        eps: Small constant for numerical stability (default: 1e-7)
        weight_decay: Weight decay coefficient (default: 0.0)
        wd_on_2d_only: Apply weight decay only to 2D params (default: True)
        ns_coeffs: Newton-Schulz coefficients [a, b, c] (default: [3.4445, -4.775, 2.0315])

    Example:
        >>> objective = Objective(terms=[pde_term, bc_term])
        >>> optimizer = MUON(objective, learning_rate=2e-2)
        >>> state = optimizer.init(state, example_batch=batch)
        >>> for batch in train_data:
        ...     state, metrics = optimizer.step(state, batch)
    """

    def __init__(
        self,
        objective: Objective,
        learning_rate: float = 2e-2,
        beta: float = 0.95,
        beta1_1d: float = 0.9,
        beta2_1d: float = 0.999,
        ns_steps: int = 5,
        nesterov: bool = True,
        eps: float = 1e-7,
        weight_decay: float = 0.0,
        wd_on_2d_only: bool = True,
        ns_coeffs: Optional[Tuple[float, float, float]] = None,
    ):
        self.objective = objective
        self.learning_rate = learning_rate
        self.beta = beta
        self.beta1_1d = beta1_1d
        self.beta2_1d = beta2_1d
        self.ns_steps = ns_steps
        self.nesterov = nesterov
        self.eps = eps
        self.weight_decay = weight_decay
        self.wd_on_2d_only = wd_on_2d_only

        # Newton-Schulz coefficients (optimized values from Optax)
        if ns_coeffs is None:
            ns_coeffs = (3.4445, -4.775, 2.0315)
        self.ns_a, self.ns_b, self.ns_c = ns_coeffs

    def init(
        self,
        state: Any,
        *,
        example_batch: Any = None,
        validate: bool = False,
    ) -> Any:
        """Initialize MUON optimizer state.

        Args:
            state: TrainState with params
            example_batch: Optional example batch for validation
            validate: Whether to validate objective evaluation

        Returns:
            TrainState with initialized opt_state
        """

        def init_param_state(p: jnp.ndarray) -> Dict[str, Any]:
            if p.ndim == 2:
                # 2D parameters: momentum only
                return {
                    "momentum": jnp.zeros_like(p),
                }
            else:
                # Non-2D parameters: AdamW style
                return {
                    "momentum": jnp.zeros_like(p),
                    "variance": jnp.zeros_like(p),
                }

        per_param_state = jax.tree_util.tree_map(
            init_param_state,
            state.params,
            is_leaf=lambda x: isinstance(x, jnp.ndarray),
        )

        opt_state = {
            "t": jnp.array(0, dtype=jnp.int32),
            "per_param": per_param_state,
        }

        return state.replace(opt_state=opt_state)

    def step(
        self,
        state: Any,
        batch: Dict[str, Any],
    ) -> Tuple[Any, Dict[str, Any]]:
        """Perform one MUON optimization step.

        Args:
            state: TrainState with params, opt_state, apply_fn, step
            batch: Batch dict

        Returns:
            (new_state, metrics) tuple
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

        # Get step counter and per-param state
        t = state.opt_state["t"] + 1
        per_param = state.opt_state["per_param"]

        # Update each parameter
        def update_2d(
            p: jnp.ndarray, g: jnp.ndarray, ps: Dict[str, Any]
        ) -> Tuple[jnp.ndarray, Dict[str, Any]]:
            """MUON update for 2D parameters."""
            momentum = ps["momentum"]

            # Update momentum
            momentum_new = self.beta * momentum + (1.0 - self.beta) * g

            # Apply Nesterov if enabled
            if self.nesterov:
                momentum_for_update = self.beta * momentum_new + (1.0 - self.beta) * g
            else:
                momentum_for_update = momentum_new

            # Apply Newton-Schulz orthogonalization
            update = _newton_schulz(
                momentum_for_update,
                self.ns_steps,
                self.eps,
                self.ns_a,
                self.ns_b,
                self.ns_c,
            )

            # Apply Optax's scaling formula: sqrt(max(1, n_cols/n_rows))
            n_rows, n_cols = g.shape[0], g.shape[1]
            scale = jnp.sqrt(jnp.maximum(1.0, n_cols / n_rows))
            update = update * scale

            # Apply weight decay (always for 2D when wd_on_2d_only=True)
            if self.weight_decay > 0:
                p_new = p * (1.0 - self.learning_rate * self.weight_decay)
                p_new = p_new - self.learning_rate * update
            else:
                p_new = p - self.learning_rate * update

            new_ps = {"momentum": momentum_new}
            return p_new, new_ps

        def update_non2d(
            p: jnp.ndarray, g: jnp.ndarray, ps: Dict[str, Any]
        ) -> Tuple[jnp.ndarray, Dict[str, Any]]:
            """AdamW update for non-2D parameters with special Nesterov."""
            m_prev = ps["momentum"]
            v_prev = ps["variance"]

            # Update moments
            m_new = self.beta1_1d * m_prev + (1.0 - self.beta1_1d) * g
            v_new = self.beta2_1d * v_prev + (1.0 - self.beta2_1d) * (g**2)

            # Apply Nesterov with special bias corrections
            if self.nesterov:
                # Optax uses different bias corrections:
                # - momentum term uses t+1
                # - gradient term uses t
                m_hat_next = m_new / (1.0 - self.beta1_1d ** (t + 1))
                g_hat = g / (1.0 - self.beta1_1d**t)
                m_for_update = (
                    self.beta1_1d * m_hat_next + (1.0 - self.beta1_1d) * g_hat
                )
            else:
                m_for_update = m_new / (1.0 - self.beta1_1d**t)

            # Bias correction for second moment
            v_hat = v_new / (1.0 - self.beta2_1d**t)

            # AdamW update direction
            direction = m_for_update / (jnp.sqrt(v_hat) + self.eps)

            # Apply weight decay (skip for non-2D if wd_on_2d_only=True)
            apply_wd = self.weight_decay > 0 and not self.wd_on_2d_only
            if apply_wd:
                p_new = p * (1.0 - self.learning_rate * self.weight_decay)
                p_new = p_new - self.learning_rate * direction
            else:
                p_new = p - self.learning_rate * direction

            new_ps = {"momentum": m_new, "variance": v_new}
            return p_new, new_ps

        def update_param(
            p: jnp.ndarray, g: jnp.ndarray, ps: Dict[str, Any]
        ) -> Tuple[jnp.ndarray, Dict[str, Any]]:
            """Route to appropriate update based on param dimensionality."""
            if p.ndim == 2:
                return update_2d(p, g, ps)
            else:
                return update_non2d(p, g, ps)

        # Helper to check if something is a per-param state dict
        def is_param_state(x):
            return isinstance(x, dict) and "momentum" in x

        new_params_and_states = jax.tree_util.tree_map(
            update_param,
            state.params,
            grads,
            per_param,
            is_leaf=lambda x: isinstance(x, jnp.ndarray) or is_param_state(x),
        )

        # Helper to check if this is a result tuple
        def is_result_tuple(x):
            return (
                isinstance(x, tuple)
                and len(x) == 2
                and isinstance(x[0], jnp.ndarray)
                and isinstance(x[1], dict)
            )

        # Split results
        new_params = jax.tree_util.tree_map(
            lambda x: x[0],
            new_params_and_states,
            is_leaf=is_result_tuple,
        )
        new_per_param = jax.tree_util.tree_map(
            lambda x: x[1],
            new_params_and_states,
            is_leaf=is_result_tuple,
        )

        new_opt_state = {
            "t": t,
            "per_param": new_per_param,
        }

        new_state = state.replace(
            step=state.step + 1,
            params=new_params,
            opt_state=new_opt_state,
        )

        return new_state, metrics
