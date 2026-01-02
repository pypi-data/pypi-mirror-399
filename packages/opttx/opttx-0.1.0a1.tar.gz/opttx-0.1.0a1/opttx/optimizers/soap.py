"""Custom SOAP optimizer implementation.

SOAP (Shampoo-like Adaptive Preconditioning) applies different treatments to
2D and non-2D parameters:
- 2D parameters: Use left/right preconditioners with feature-space Adam
- Non-2D parameters: Standard Adam

References:
    Shampoo (Gupta et al., 2018): Shampoo: Preconditioned Stochastic Tensor Optimization
    https://arxiv.org/abs/1802.09568
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import jax
import jax.numpy as jnp

from ..objective import Objective


def _eigh_desc(A: jnp.ndarray, jitter: float) -> jnp.ndarray:
    """Eigendecomposition with eigenvalues sorted in descending order."""
    eye = jnp.eye(A.shape[0], dtype=A.dtype)
    w, Q = jnp.linalg.eigh(A + jitter * eye)
    idx = jnp.argsort(w)[::-1]
    return Q[:, idx]


def _qr_refresh(
    A: jnp.ndarray,
    Q: jnp.ndarray,
    V: jnp.ndarray,
    axis: int,
    jitter: float,
    power_iter_steps: int,
) -> Tuple[jnp.ndarray, jnp.ndarray]:
    """Refresh basis using power iteration and QR decomposition."""
    est_eig = jnp.diag(Q.T @ A @ Q)
    sort_idx = jnp.argsort(est_eig)[::-1]
    V_perm = jnp.take(V, sort_idx, axis=axis)
    Q_sorted = Q[:, sort_idx]
    eye = jnp.eye(A.shape[0], dtype=A.dtype)

    def iter_step(_: int, Q_curr: jnp.ndarray) -> jnp.ndarray:
        power_iter = (A + jitter * eye) @ Q_curr
        Q_new, _ = jnp.linalg.qr(power_iter)
        return Q_new

    Q_new = jax.lax.fori_loop(0, power_iter_steps, iter_step, Q_sorted)
    return Q_new, V_perm


class SOAP:
    """SOAP optimizer with Shampoo-like preconditioning for 2D parameters.

    2D parameters (weight matrices) use left/right preconditioners with
    feature-space Adam. Non-2D parameters (biases, norms) use standard Adam.

    Args:
        objective: The objective to optimize
        learning_rate: Learning rate (default: 1e-2)
        beta1: Exponential decay rate for first moment (default: 0.95)
        beta2: Exponential decay rate for second moment (default: 0.95)
        precond_beta: Decay rate for preconditioner matrices (default: 0.95)
        eps: Small constant for numerical stability (default: 1e-8)
        jitter: Jitter for eigendecomposition stability (default: 1e-6)
        precond_frequency: Frequency of basis refresh (default: 10)
        power_iter_steps: Power iteration steps for basis refresh (default: 1)
        weight_decay: Weight decay coefficient (default: 0.0)
        wd_on_2d_only: Apply weight decay only to 2D params (default: True)
        max_precond_dim: Max dimension for preconditioning (default: 10000)

    Example:
        >>> objective = Objective(terms=[pde_term, bc_term])
        >>> optimizer = SOAP(objective, learning_rate=1e-2)
        >>> state = optimizer.init(state, example_batch=batch)
        >>> for batch in train_data:
        ...     state, metrics = optimizer.step(state, batch)
    """

    def __init__(
        self,
        objective: Objective,
        learning_rate: float = 1e-2,
        beta1: float = 0.95,
        beta2: float = 0.95,
        precond_beta: float = 0.95,
        eps: float = 1e-8,
        jitter: float = 1e-6,
        precond_frequency: int = 10,
        power_iter_steps: int = 1,
        weight_decay: float = 0.0,
        wd_on_2d_only: bool = True,
        max_precond_dim: Optional[int] = 10000,
    ):
        self.objective = objective
        self.learning_rate = learning_rate
        self.beta1 = beta1
        self.beta2 = beta2
        self.precond_beta = precond_beta
        self.eps = eps
        self.jitter = jitter
        self.precond_frequency = precond_frequency
        self.power_iter_steps = power_iter_steps
        self.weight_decay = weight_decay
        self.wd_on_2d_only = wd_on_2d_only
        self.max_precond_dim = max_precond_dim

    def _should_use_soap(self, p: jnp.ndarray) -> Tuple[bool, bool, bool]:
        """Determine if a parameter should use SOAP and which preconditioners.

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
        """Initialize SOAP optimizer state.

        Args:
            state: TrainState with params
            example_batch: Optional example batch for validation
            validate: Whether to validate objective evaluation

        Returns:
            TrainState with initialized opt_state containing per-parameter state
        """
        # Build static labels for routing (computed once, used for dispatch)
        self._param_labels = jax.tree_util.tree_map(
            lambda p: self._should_use_soap(p),
            state.params,
            is_leaf=lambda x: isinstance(x, jnp.ndarray),
        )

        def init_param_state(
            p: jnp.ndarray, label: Tuple[bool, bool, bool]
        ) -> Dict[str, Any]:
            is_2d, use_left, use_right = label

            if is_2d and (use_left or use_right):
                m, n = p.shape
                # SOAP state - use placeholder zeros for unused L/R
                param_state = {
                    # Gram matrices (zero-sized if not used)
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
                    # Orthonormal bases (identity if used, empty if not)
                    "QL": (
                        jnp.eye(m, dtype=p.dtype)
                        if use_left
                        else jnp.zeros((0, 0), dtype=p.dtype)
                    ),
                    "QR": (
                        jnp.eye(n, dtype=p.dtype)
                        if use_right
                        else jnp.zeros((0, 0), dtype=p.dtype)
                    ),
                    # Feature-space moments
                    "M": jnp.zeros_like(p),
                    "V": jnp.zeros_like(p),
                    # Initialization flag
                    "initialized": jnp.array(False),
                }
            else:
                # Adam-style for non-2D or oversized parameters
                param_state = {
                    "L": jnp.zeros((0, 0), dtype=p.dtype),  # Empty marker
                    "R": jnp.zeros((0, 0), dtype=p.dtype),
                    "QL": jnp.zeros((0, 0), dtype=p.dtype),
                    "QR": jnp.zeros((0, 0), dtype=p.dtype),
                    "M": jnp.zeros_like(p),  # Used as m for Adam
                    "V": jnp.zeros_like(p),  # Used as v for Adam
                    "initialized": jnp.array(True),  # Adam is always "initialized"
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
        """Perform one SOAP optimization step.

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

        # Get step counter
        t = state.opt_state["t"]
        per_param = state.opt_state["per_param"]

        # Helper to check if something is a per-param state dict
        def is_param_state(x):
            return isinstance(x, dict) and "M" in x and "V" in x

        # Helper to check if something is a label tuple
        def is_label(x):
            return (
                isinstance(x, tuple)
                and len(x) == 3
                and all(isinstance(v, bool) for v in x)
            )

        # Update each parameter using static labels
        def update_param(
            p: jnp.ndarray,
            g: jnp.ndarray,
            ps: Dict[str, Any],
            label: Tuple[bool, bool, bool],
        ) -> Tuple[jnp.ndarray, Dict[str, Any]]:
            is_2d, use_left, use_right = label
            if is_2d and (use_left or use_right):
                return self._soap_update(p, g, ps, t, use_left, use_right)
            else:
                return self._adam_update(p, g, ps, t)

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

        # Helper to check if this is a result tuple (param, state)
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

        # Check if any SOAP param was initialized (for step counter logic)
        def was_initialized(
            ps: Dict[str, Any], label: Tuple[bool, bool, bool]
        ) -> jnp.ndarray:
            is_2d, use_left, use_right = label
            if is_2d and (use_left or use_right):
                return ps["initialized"]
            return jnp.array(True)  # Adam params always "initialized"

        init_flags = jax.tree_util.tree_map(
            was_initialized,
            per_param,
            self._param_labels,
            is_leaf=lambda x: is_param_state(x) or is_label(x),
        )
        any_initialized = jax.tree_util.tree_reduce(
            jnp.logical_or,
            jax.tree_util.tree_leaves(init_flags),
            jnp.array(False),
        )

        # Only advance step counter if at least one param was already initialized
        t_new = jnp.where(any_initialized, t + 1, t)

        new_opt_state = {
            "t": t_new,
            "per_param": new_per_param,
        }

        new_state = state.replace(
            step=state.step + 1,
            params=new_params,
            opt_state=new_opt_state,
        )

        return new_state, metrics

    def _adam_update(
        self,
        p: jnp.ndarray,
        g: jnp.ndarray,
        ps: Dict[str, Any],
        t: jnp.ndarray,
    ) -> Tuple[jnp.ndarray, Dict[str, Any]]:
        """Standard Adam update for non-2D parameters.

        Uses M and V fields from the unified state structure.
        """
        t_new = t + 1

        m = ps["M"]  # Use M field (unified with SOAP)
        v = ps["V"]  # Use V field (unified with SOAP)

        m_new = self.beta1 * m + (1.0 - self.beta1) * g
        v_new = self.beta2 * v + (1.0 - self.beta2) * (g * g)

        m_hat = m_new / (1.0 - self.beta1**t_new)
        v_hat = v_new / (1.0 - self.beta2**t_new)

        direction = m_hat / (jnp.sqrt(v_hat) + self.eps)

        # Apply weight decay (skip for 1D params if wd_on_2d_only=True)
        apply_wd = self.weight_decay > 0 and not self.wd_on_2d_only
        if apply_wd:
            p_new = p * (1.0 - self.learning_rate * self.weight_decay)
            p_new = p_new - self.learning_rate * direction
        else:
            p_new = p - self.learning_rate * direction

        # Unified state structure (same keys as SOAP for pytree compatibility)
        new_ps = {
            "L": ps["L"],  # Keep empty placeholder
            "R": ps["R"],
            "QL": ps["QL"],
            "QR": ps["QR"],
            "M": m_new,
            "V": v_new,
            "initialized": ps["initialized"],
        }

        return p_new, new_ps

    def _soap_update(
        self,
        p: jnp.ndarray,
        g: jnp.ndarray,
        ps: Dict[str, Any],
        t: jnp.ndarray,
        use_left: bool,
        use_right: bool,
    ) -> Tuple[jnp.ndarray, Dict[str, Any]]:
        """SOAP update for 2D parameters.

        Args:
            p: Parameter array
            g: Gradient array
            ps: Per-parameter state
            t: Step counter
            use_left: Whether to use left preconditioner (static)
            use_right: Whether to use right preconditioner (static)
        """
        initialized = ps["initialized"]

        L = ps["L"]
        R = ps["R"]
        QL = ps["QL"]
        QR = ps["QR"]
        M = ps["M"]
        V = ps["V"]

        # Update Gram matrices
        def update_grams(g_in, L_in, R_in):
            L_new = L_in
            R_new = R_in
            if use_left:
                GGt = g_in @ g_in.T
                L_new = self.precond_beta * L_in + (1.0 - self.precond_beta) * 0.5 * (
                    GGt + GGt.T
                )
            if use_right:
                GtG = g_in.T @ g_in
                R_new = self.precond_beta * R_in + (1.0 - self.precond_beta) * 0.5 * (
                    GtG + GtG.T
                )
            return L_new, R_new

        def project_to_basis(x, QL_mat, QR_mat):
            if use_left:
                x = QL_mat.T @ x
            if use_right:
                x = x @ QR_mat
            return x

        def project_from_basis(x, QL_mat, QR_mat):
            if use_left:
                x = QL_mat @ x
            if use_right:
                x = x @ QR_mat.T
            return x

        def first_time_init(_):
            """First call: initialize preconditioner, no update."""
            L_new, R_new = update_grams(g, L, R)
            QL_new = QL
            QR_new = QR
            if use_left:
                QL_new = _eigh_desc(L_new, self.jitter)
            if use_right:
                QR_new = _eigh_desc(R_new, self.jitter)
            M_new = jnp.zeros_like(g)
            V_new = jnp.zeros_like(g)
            return (
                jnp.zeros_like(g),  # No update direction
                L_new,
                R_new,
                QL_new,
                QR_new,
                M_new,
                V_new,
                jnp.array(True),
            )

        def normal_update(_):
            """Normal path: feature-space Adam update."""
            t_new = t + 1

            # Project gradient to feature space
            g_feat = project_to_basis(g, QL, QR)

            # Adam update in feature space
            M_new = self.beta1 * M + (1.0 - self.beta1) * g_feat
            V_new = self.beta2 * V + (1.0 - self.beta2) * (g_feat * g_feat)

            m_hat = M_new / (1.0 - self.beta1**t_new)
            v_hat = V_new / (1.0 - self.beta2**t_new)

            upd_feat = m_hat / (jnp.sqrt(v_hat) + self.eps)

            # Project back to original space
            upd = project_from_basis(upd_feat, QL, QR)

            # Update Gram matrices
            L_new, R_new = update_grams(g, L, R)

            # Check if we should refresh bases
            should_refresh = jnp.equal(
                jnp.mod(t_new, jnp.array(self.precond_frequency, dtype=jnp.int32)), 0
            )

            def do_refresh(_):
                # Project moment back to original space before refresh
                m_orig = M_new
                if use_left:
                    m_orig = QL @ m_orig
                if use_right:
                    m_orig = m_orig @ QR.T

                QL_ref = QL
                QR_ref = QR
                V_ref = V_new

                if use_left:
                    QL_ref, V_ref = _qr_refresh(
                        L_new,
                        QL,
                        V_ref,
                        axis=0,
                        jitter=self.jitter,
                        power_iter_steps=self.power_iter_steps,
                    )
                if use_right:
                    QR_ref, V_ref = _qr_refresh(
                        R_new,
                        QR,
                        V_ref,
                        axis=1,
                        jitter=self.jitter,
                        power_iter_steps=self.power_iter_steps,
                    )

                # Project moment back to new feature space
                M_ref = m_orig
                if use_left:
                    M_ref = QL_ref.T @ M_ref
                if use_right:
                    M_ref = M_ref @ QR_ref

                return QL_ref, QR_ref, M_ref, V_ref

            def no_refresh(_):
                return QL, QR, M_new, V_new

            QL_final, QR_final, M_final, V_final = jax.lax.cond(
                should_refresh, do_refresh, no_refresh, operand=None
            )

            return (
                upd,
                L_new,
                R_new,
                QL_final,
                QR_final,
                M_final,
                V_final,
                jnp.array(True),
            )

        # Choose between first-time init and normal update
        direction, L_new, R_new, QL_new, QR_new, M_new, V_new, init_new = jax.lax.cond(
            initialized, normal_update, first_time_init, operand=None
        )

        # Apply weight decay and update
        if self.weight_decay > 0:
            p_new = p * (1.0 - self.learning_rate * self.weight_decay)
            p_new = p_new - self.learning_rate * direction
        else:
            p_new = p - self.learning_rate * direction

        # Unified state structure
        new_ps = {
            "L": L_new,
            "R": R_new,
            "QL": QL_new,
            "QR": QR_new,
            "M": M_new,
            "V": V_new,
            "initialized": init_new,
        }

        return p_new, new_ps
