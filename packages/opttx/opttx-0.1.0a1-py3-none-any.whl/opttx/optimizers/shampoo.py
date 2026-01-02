"""Shampoo optimizer implementation.

Shampoo is a second-order optimization method that uses Kronecker-factored
preconditioning. For a 2D parameter (weight matrix), it maintains left and
right preconditioners that approximate the inverse Fisher information.

Key formula:
    L_t = β L_{t-1} + (1-β) G_t G_t^T     (left Gram matrix, EMA)
    R_t = β R_{t-1} + (1-β) G_t^T G_t     (right Gram matrix, EMA)
    P_t = L_t^{-1/4} @ G_t @ R_t^{-1/4}   (preconditioned gradient)
    W_{t+1} = W_t - η * P_t

The 1/4 power arises because (L ⊗ R)^{-1/2} ≈ L^{-1/4} ⊗ R^{-1/4}.

References:
    Gupta, Koren & Singer (2018): Shampoo: Preconditioned Stochastic Tensor Optimization
    https://arxiv.org/abs/1802.09568
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import jax
import jax.numpy as jnp

from ..objective import Objective


def _compute_matrix_power(
    A: jnp.ndarray,
    power: float,
    eps: float,
) -> jnp.ndarray:
    """Compute A^power via eigendecomposition with proper damping.

    Uses ridge regularization to handle small/zero eigenvalues:
    (A + eps * max(lambda) * I)^power

    Args:
        A: Symmetric positive semi-definite matrix
        power: The power to raise eigenvalues to (e.g., -0.25 for inverse 4th root)
        eps: Regularization factor relative to max eigenvalue

    Returns:
        (A + damping)^power
    """
    # Eigendecomposition (A is symmetric)
    eigenvalues, eigenvectors = jnp.linalg.eigh(A)

    # Ridge regularization: add eps * max(eigenvalue) to all eigenvalues
    # This ensures numerical stability while preserving relative scaling
    max_eig = jnp.maximum(jnp.max(eigenvalues), 1e-16)
    damping = eps * max_eig
    eigenvalues_damped = eigenvalues + damping

    # Compute power of damped eigenvalues
    eigenvalues_power = eigenvalues_damped**power

    # Reconstruct: U @ diag(lambda^power) @ U^T
    return eigenvectors @ (eigenvalues_power[:, None] * eigenvectors.T)


class Shampoo:
    """Shampoo optimizer with Kronecker-factored preconditioning.

    Applies L^{-1/4} G R^{-1/4} preconditioning to 2D parameters.
    Non-2D parameters use standard SGD with momentum.

    Compared to SOAP:
    - Simpler: No inner Adam, just direct preconditioning
    - Lower memory: No M, V momentum/variance tracking
    - Lower per-step cost: No Adam computations in eigenbasis

    Args:
        objective: The objective to optimize
        learning_rate: Learning rate (default: 1e-2)
        momentum: Momentum coefficient for SGD fallback (default: 0.9)
        precond_beta: Decay rate for Gram matrices (default: 0.9)
        eps: Damping factor for eigenvalue regularization (default: 1e-4)
        precond_frequency: Frequency of preconditioner updates (default: 10)
        weight_decay: Weight decay coefficient (default: 0.0)
        grafting: Grafting strategy - 'none', 'sgd', or 'adam' (default: 'none')
        grafting_beta1: Adam beta1 for grafting EMA (default: 0.9)
        grafting_beta2: Adam beta2 for grafting EMA (default: 0.999)
        max_precond_dim: Max dimension for preconditioning (default: 8192)
        start_preconditioning_step: Step to start preconditioning (default: 10)

    Example:
        >>> objective = Objective(terms=[pde_term, bc_term])
        >>> optimizer = Shampoo(objective, learning_rate=1e-2)
        >>> state = optimizer.init(state, example_batch=batch)
        >>> for batch in train_data:
        ...     state, metrics = optimizer.step(state, batch)
    """

    def __init__(
        self,
        objective: Objective,
        learning_rate: float = 1e-2,
        momentum: float = 0.9,
        precond_beta: float = 0.9,
        eps: float = 1e-4,
        precond_frequency: int = 10,
        weight_decay: float = 0.0,
        grafting: str = "none",
        grafting_beta1: float = 0.9,
        grafting_beta2: float = 0.999,
        max_precond_dim: Optional[int] = 8192,
        start_preconditioning_step: int = 10,
    ):
        self.objective = objective
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.precond_beta = precond_beta
        self.eps = eps
        self.precond_frequency = precond_frequency
        self.weight_decay = weight_decay
        self.grafting = grafting
        self.grafting_beta1 = grafting_beta1
        self.grafting_beta2 = grafting_beta2
        self.max_precond_dim = max_precond_dim
        self.start_preconditioning_step = start_preconditioning_step

        if grafting not in ("none", "sgd", "adam"):
            raise ValueError(
                f"grafting must be 'none', 'sgd', or 'adam', got {grafting}"
            )

    def _should_use_shampoo(self, p: jnp.ndarray) -> Tuple[bool, bool, bool]:
        """Determine if a parameter should use Shampoo and which preconditioners.

        Returns:
            (is_2d, use_left, use_right)
        """
        if p.ndim != 2:
            return False, False, False

        m, n = p.shape
        if self.max_precond_dim is None:
            return True, True, True

        use_left = m <= self.max_precond_dim
        use_right = n <= self.max_precond_dim

        if not use_left and not use_right:
            return False, False, False

        return True, use_left, use_right

    def init(
        self,
        state: Any,
        *,
        example_batch: Any = None,
        validate: bool = False,
    ) -> Any:
        """Initialize Shampoo optimizer state.

        Args:
            state: TrainState with params
            example_batch: Optional example batch for validation
            validate: Whether to validate objective evaluation

        Returns:
            TrainState with initialized opt_state
        """
        # Build static labels for routing
        self._param_labels = jax.tree_util.tree_map(
            lambda p: self._should_use_shampoo(p),
            state.params,
            is_leaf=lambda x: isinstance(x, jnp.ndarray),
        )

        def init_param_state(
            p: jnp.ndarray, label: Tuple[bool, bool, bool]
        ) -> Dict[str, Any]:
            is_2d, use_left, use_right = label

            if is_2d and (use_left or use_right):
                m, n = p.shape
                param_state = {
                    # Gram matrices
                    "L": (
                        jnp.zeros((m, m), dtype=p.dtype)
                        if use_left
                        else jnp.zeros((0, 0), dtype=p.dtype)
                    ),
                    "R": (
                        jnp.zeros((n, n), dtype=p.dtype)
                        if use_right
                        else jnp.zeros((0, 0), dtype=p.dtype)
                    ),
                    # Preconditioner roots (L^{-1/4}, R^{-1/4})
                    "L_inv_4": (
                        jnp.eye(m, dtype=p.dtype)
                        if use_left
                        else jnp.zeros((0, 0), dtype=p.dtype)
                    ),
                    "R_inv_4": (
                        jnp.eye(n, dtype=p.dtype)
                        if use_right
                        else jnp.zeros((0, 0), dtype=p.dtype)
                    ),
                    # Momentum buffer for grafting
                    "momentum": jnp.zeros_like(p),
                    # Adam state for grafting (if needed)
                    "adam_m": jnp.zeros_like(p),
                    "adam_v": jnp.zeros_like(p),
                }
            else:
                # SGD with momentum for non-2D parameters
                param_state = {
                    "L": jnp.zeros((0, 0), dtype=p.dtype),
                    "R": jnp.zeros((0, 0), dtype=p.dtype),
                    "L_inv_4": jnp.zeros((0, 0), dtype=p.dtype),
                    "R_inv_4": jnp.zeros((0, 0), dtype=p.dtype),
                    "momentum": jnp.zeros_like(p),
                    "adam_m": jnp.zeros_like(p),
                    "adam_v": jnp.zeros_like(p),
                }

            return param_state

        per_param_state = jax.tree_util.tree_map(
            init_param_state,
            state.params,
            self._param_labels,
            is_leaf=lambda x: isinstance(x, jnp.ndarray) or isinstance(x, tuple),
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
        """Perform one Shampoo optimization step.

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

        t = state.opt_state["t"]
        per_param = state.opt_state["per_param"]

        def is_param_state(x):
            return isinstance(x, dict) and "L" in x and "momentum" in x

        def is_label(x):
            return (
                isinstance(x, tuple)
                and len(x) == 3
                and all(isinstance(v, bool) for v in x)
            )

        def update_param(
            p: jnp.ndarray,
            g: jnp.ndarray,
            ps: Dict[str, Any],
            label: Tuple[bool, bool, bool],
        ) -> Tuple[jnp.ndarray, Dict[str, Any]]:
            is_2d, use_left, use_right = label
            if is_2d and (use_left or use_right):
                return self._shampoo_update(p, g, ps, t, use_left, use_right)
            else:
                return self._sgd_update(p, g, ps, t)

        new_params_and_states = jax.tree_util.tree_map(
            update_param,
            state.params,
            grads,
            per_param,
            self._param_labels,
            is_leaf=lambda x: isinstance(x, jnp.ndarray)
            or is_param_state(x)
            or is_label(x),
        )

        def is_result_tuple(x):
            return (
                isinstance(x, tuple)
                and len(x) == 2
                and isinstance(x[0], jnp.ndarray)
                and isinstance(x[1], dict)
            )

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
            "t": t + 1,
            "per_param": new_per_param,
        }

        new_state = state.replace(
            step=state.step + 1,
            params=new_params,
            opt_state=new_opt_state,
        )

        return new_state, metrics

    def _sgd_update(
        self,
        p: jnp.ndarray,
        g: jnp.ndarray,
        ps: Dict[str, Any],
        t: jnp.ndarray,
    ) -> Tuple[jnp.ndarray, Dict[str, Any]]:
        """SGD with momentum for non-2D parameters."""
        mom = ps["momentum"]

        # Weight decay
        if self.weight_decay > 0:
            g = g + self.weight_decay * p

        # Momentum update
        new_mom = self.momentum * mom + g

        # Parameter update
        p_new = p - self.learning_rate * new_mom

        new_ps = {
            "L": ps["L"],
            "R": ps["R"],
            "L_inv_4": ps["L_inv_4"],
            "R_inv_4": ps["R_inv_4"],
            "momentum": new_mom,
            "adam_m": ps["adam_m"],
            "adam_v": ps["adam_v"],
        }

        return p_new, new_ps

    def _shampoo_update(
        self,
        p: jnp.ndarray,
        g: jnp.ndarray,
        ps: Dict[str, Any],
        t: jnp.ndarray,
        use_left: bool,
        use_right: bool,
    ) -> Tuple[jnp.ndarray, Dict[str, Any]]:
        """Shampoo update for 2D parameters.

        Args:
            p: Parameter array (m x n)
            g: Gradient array (m x n)
            ps: Per-parameter state
            t: Step counter
            use_left: Whether to use left preconditioner
            use_right: Whether to use right preconditioner
        """
        L = ps["L"]
        R = ps["R"]
        L_inv_4 = ps["L_inv_4"]
        R_inv_4 = ps["R_inv_4"]
        mom = ps["momentum"]
        adam_m = ps["adam_m"]
        adam_v = ps["adam_v"]

        t_new = t + 1

        # Apply weight decay to gradient
        g_wd = g
        if self.weight_decay > 0:
            g_wd = g + self.weight_decay * p

        # Update Gram matrices (EMA)
        L_new = L
        R_new = R
        if use_left:
            GGt = g @ g.T
            L_new = self.precond_beta * L + (1.0 - self.precond_beta) * 0.5 * (
                GGt + GGt.T
            )
        if use_right:
            GtG = g.T @ g
            R_new = self.precond_beta * R + (1.0 - self.precond_beta) * 0.5 * (
                GtG + GtG.T
            )

        # Conditionally update preconditioner roots
        should_update = jnp.logical_and(
            jnp.equal(
                jnp.mod(t_new, jnp.array(self.precond_frequency, dtype=jnp.int32)), 0
            ),
            t_new >= self.start_preconditioning_step,
        )

        def update_precond(_):
            L_inv_4_new = L_inv_4
            R_inv_4_new = R_inv_4
            if use_left:
                L_inv_4_new = _compute_matrix_power(L_new, -0.25, self.eps)
            if use_right:
                R_inv_4_new = _compute_matrix_power(R_new, -0.25, self.eps)
            return L_inv_4_new, R_inv_4_new

        def keep_precond(_):
            return L_inv_4, R_inv_4

        L_inv_4_new, R_inv_4_new = jax.lax.cond(
            should_update, update_precond, keep_precond, operand=None
        )

        # Compute preconditioned gradient: L^{-1/4} @ G @ R^{-1/4}
        precond_g = g_wd
        if use_left:
            precond_g = L_inv_4_new @ precond_g
        if use_right:
            precond_g = precond_g @ R_inv_4_new

        # Update Adam state (for grafting)
        beta1 = self.grafting_beta1
        beta2 = self.grafting_beta2
        adam_m_new = beta1 * adam_m + (1 - beta1) * g_wd
        adam_v_new = beta2 * adam_v + (1 - beta2) * (g_wd * g_wd)

        # Grafting: scale Shampoo update to match reference optimizer's norm
        if self.grafting == "sgd":
            # Match SGD update norm
            sgd_norm = jnp.linalg.norm(g_wd)
            shampoo_norm = jnp.linalg.norm(precond_g) + self.eps
            scale = sgd_norm / shampoo_norm
            precond_g = scale * precond_g
        elif self.grafting == "adam":
            # Match Adam update norm
            m_hat = adam_m_new / (1.0 - beta1**t_new)
            v_hat = adam_v_new / (1.0 - beta2**t_new)
            adam_update = m_hat / (jnp.sqrt(v_hat) + 1e-8)
            adam_norm = jnp.linalg.norm(adam_update)
            shampoo_norm = jnp.linalg.norm(precond_g) + self.eps
            scale = adam_norm / shampoo_norm
            precond_g = scale * precond_g

        # Apply momentum
        new_mom = self.momentum * mom + precond_g

        # Parameter update
        p_new = p - self.learning_rate * new_mom

        new_ps = {
            "L": L_new,
            "R": R_new,
            "L_inv_4": L_inv_4_new,
            "R_inv_4": R_inv_4_new,
            "momentum": new_mom,
            "adam_m": adam_m_new,
            "adam_v": adam_v_new,
        }

        return p_new, new_ps
