"""Cross-batch NLTGCR optimizer for second-order optimization.

CrossBatchNLTGCROptimizer stores the subspace (P, AP) across mini-batches,
enabling cross-batch accumulation for better convergence on stochastic problems.

The key difference from NLTGCROptimizer is that the subspace persists across
optimizer steps (mini-batches), allowing information to accumulate over time.

References:
    https://arxiv.org/abs/2306.00325
"""

from __future__ import annotations

from typing import Any, Dict, Literal, Tuple

import jax
import jax.numpy as jnp

from ..objective import Objective
from ..curvature import build_damped_matvec, build_fisher_matvec, build_hessian_matvec


def _tree_dot(a: Any, b: Any) -> jnp.ndarray:
    """Compute dot product of two pytrees."""
    leaves_a = jax.tree_util.tree_leaves(a)
    leaves_b = jax.tree_util.tree_leaves(b)
    return sum(jnp.sum(la * lb) for la, lb in zip(leaves_a, leaves_b))


def _tree_axpy(alpha: jnp.ndarray, x: Any, y: Any) -> Any:
    """Compute alpha * x + y for pytrees."""
    return jax.tree_util.tree_map(lambda xi, yi: alpha * xi + yi, x, y)


def _tree_scale(alpha: jnp.ndarray, x: Any) -> Any:
    """Compute alpha * x for pytree."""
    return jax.tree_util.tree_map(lambda xi: alpha * xi, x)


def _get_eps(dtype) -> float:
    """Get epsilon for division safety based on dtype."""
    if dtype == jnp.float32:
        return 1e-20
    else:
        return 1e-30


class CrossBatchNLTGCROptimizer:
    """Cross-batch NLTGCR optimizer with persistent subspace.

    Stores search directions (P) and curvature-mapped directions (AP) across
    mini-batches, enabling cross-batch accumulation. This is closer to the
    PyTorch reference implementation where subspace persists across steps.

    Args:
        objective: The objective to optimize
        learning_rate: Step size for NLTGCR updates (default: 0.01)
        damping: Damping coefficient for curvature (default: 1e-3)
        iters_per_batch: Number of NLTGCR iterations per mini-batch (default: 1)
            - iters_per_batch=1: Closest to PyTorch reference (one update per batch)
            - iters_per_batch=N: More updates per batch (closer to fresh-start behavior)
        mem_size: Memory size for stored vectors (default: 5)
        curvature_type: Type of curvature matrix, "fisher" or "hessian"
            (default: "fisher")
        safeguard: Threshold for automatic restart (default: 1e3)

    Example:
        >>> objective = Objective(terms=[pde_term, bc_term])
        >>> optimizer = CrossBatchNLTGCROptimizer(
        ...     objective, learning_rate=0.01, iters_per_batch=1
        ... )
        >>> state = optimizer.init(state)
        >>> for batch in train_data:
        ...     state, metrics = optimizer.step(state, batch)

    Note:
        - Subspace (P, AP) persists across steps for cross-batch accumulation
        - Curvature changes between batches may make subspace stale
        - Safeguard mechanism triggers restart if subspace becomes numerically unstable
    """

    def __init__(
        self,
        objective: Objective,
        learning_rate: float = 0.01,
        damping: float = 1e-3,
        iters_per_batch: int = 1,
        mem_size: int = 5,
        curvature_type: Literal["fisher", "hessian"] = "fisher",
        safeguard: float = 1e3,
    ):
        self.objective = objective
        self.learning_rate = learning_rate
        self.damping = damping
        self.iters_per_batch = iters_per_batch
        self.mem_size = mem_size
        self.curvature_type = curvature_type
        self.safeguard = safeguard

        if curvature_type not in ("fisher", "hessian"):
            raise ValueError(
                f"curvature_type must be 'fisher' or 'hessian', got {curvature_type}"
            )

    def init(
        self,
        state: Any,
        *,
        example_batch: Any = None,
        validate: bool = False,
    ) -> Any:
        """Initialize CrossBatchNLTGCR optimizer state.

        Args:
            state: TrainState with params
            example_batch: Optional example batch for validation
            validate: Whether to validate objective evaluation

        Returns:
            TrainState with initialized opt_state containing subspace storage
        """
        # Compute number of parameters
        flat_params, _ = jax.tree_util.tree_flatten(state.params)
        n_params = sum(p.size for p in flat_params)
        dtype = flat_params[0].dtype

        # Initialize subspace storage
        # Note: We don't store tree_def/shapes/sizes because they're not JAX types.
        # Instead, we reconstruct them from state.params at each step.
        opt_state = {
            # Subspace storage (flattened for JIT compatibility)
            "P_flat": jnp.zeros((self.mem_size, n_params), dtype=dtype),
            "AP_flat": jnp.zeros((self.mem_size, n_params), dtype=dtype),
            "xrec": jnp.zeros(self.mem_size, dtype=dtype),
            "valid_mask": jnp.zeros(self.mem_size, dtype=jnp.bool_),
            "m": jnp.array(0, dtype=jnp.int32),
            # Tracking
            "total_iters": jnp.array(0, dtype=jnp.int32),
        }
        return state.replace(opt_state=opt_state)

    def step(
        self,
        state: Any,
        batch: Dict[str, Any],
    ) -> Tuple[Any, Dict[str, Any]]:
        """Perform one CrossBatchNLTGCR optimization step.

        Each step runs iters_per_batch NLTGCR iterations using the stored
        subspace from previous steps:
        1. Build curvature matvec for current batch
        2. Compute gradient
        3. Run iters_per_batch iterations with persistent subspace
        4. Return updated state with new subspace

        Args:
            state: TrainState with params, opt_state, apply_fn, step
            batch: Batch dict with keys matching term.batch_key

        Returns:
            (new_state, metrics) tuple where metrics includes:
                - loss: total loss
                - loss/<term_name>: per-term losses
                - nltgcr_iters: number of NLTGCR iterations this step
        """
        # Build variables dict
        variables = {"params": state.params}
        if hasattr(state, "batch_stats") and state.batch_stats is not None:
            variables["batch_stats"] = state.batch_stats

        # Define loss function for gradient and metrics computation
        def loss_fn(params):
            vars_with_p = {**variables, "params": params}
            metrics = self.objective.evaluate(
                apply_fn=state.apply_fn,
                variables=vars_with_p,
                batch=batch,
                step=state.step,
            )
            return metrics["loss"], metrics

        # Compute initial metrics (for reporting)
        _, metrics = loss_fn(state.params)

        # Build curvature matvec for current batch
        if self.curvature_type == "fisher":
            base_matvec = build_fisher_matvec(
                self.objective, state.apply_fn, variables, batch, state.step
            )
        else:  # hessian
            base_matvec = build_hessian_matvec(
                self.objective, state.apply_fn, variables, batch, state.step
            )

        # Add damping: (H + lambda*I)v
        damped_matvec = build_damped_matvec(base_matvec, self.damping)

        # Define grad_fn for NLTGCR
        def grad_fn(params):
            return jax.grad(
                lambda p: self.objective.evaluate(
                    apply_fn=state.apply_fn,
                    variables={**variables, "params": p},
                    batch=batch,
                    step=state.step,
                )["loss"]
            )(params)

        # Get stored subspace from opt_state
        P_flat = state.opt_state["P_flat"]
        AP_flat = state.opt_state["AP_flat"]
        xrec = state.opt_state["xrec"]
        valid_mask = state.opt_state["valid_mask"]
        m = state.opt_state["m"]

        # Get structure info from params (reconstructed each step for JIT compatibility)
        flat_params, tree_def = jax.tree_util.tree_flatten(state.params)
        shapes = [p.shape for p in flat_params]
        sizes = [p.size for p in flat_params]

        # Helper functions
        def flatten_to_vec(pytree):
            leaves = jax.tree_util.tree_leaves(pytree)
            return jnp.concatenate([leaf.ravel() for leaf in leaves])

        def unflatten_from_vec(vec):
            splits = []
            offset = 0
            for shape, size in zip(shapes, sizes):
                splits.append(vec[offset : offset + size].reshape(shape))
                offset += size
            return jax.tree_util.tree_unflatten(tree_def, splits)

        dtype = P_flat.dtype
        eps = _get_eps(dtype)

        # Initialize subspace if empty (first step)
        x = state.params
        r = _tree_scale(-1.0, grad_fn(x))
        r_vec = flatten_to_vec(r)

        def init_subspace():
            """Initialize subspace from current gradient."""
            Ar = damped_matvec(r)
            Ar_vec = flatten_to_vec(Ar)
            t = jnp.sqrt(jnp.dot(Ar_vec, Ar_vec))
            t_safe = t + eps

            P_new = jnp.zeros_like(P_flat).at[0].set(r_vec / t_safe)
            AP_new = jnp.zeros_like(AP_flat).at[0].set(Ar_vec / t_safe)
            valid_new = jnp.zeros_like(valid_mask).at[0].set(True)
            xrec_new = jnp.zeros_like(xrec)
            w0 = jnp.max(jnp.abs(r_vec))
            xrec_new = xrec_new.at[0].set(w0 / t_safe)
            return P_new, AP_new, xrec_new, valid_new, jnp.array(1, dtype=jnp.int32)

        def use_existing():
            """Use existing subspace."""
            return P_flat, AP_flat, xrec, valid_mask, m

        # If subspace is empty (m=0), initialize it
        P_flat, AP_flat, xrec, valid_mask, m = jax.lax.cond(
            m == 0, init_subspace, use_existing
        )

        # Run iters_per_batch iterations
        def body_fn(_, carry):
            x, P_flat, AP_flat, xrec, valid_mask, m = carry

            r = _tree_scale(-1.0, grad_fn(x))
            r_vec = flatten_to_vec(r)

            # Compute gg using full arrays with masking
            alphas = jnp.sum(AP_flat * r_vec[None, :], axis=1)
            alphas = jnp.where(valid_mask, alphas, 0.0)
            gg_vec = jnp.sum(P_flat * alphas[:, None], axis=0)
            gg = unflatten_from_vec(gg_vec)

            # Descent check
            tc = jnp.dot(gg_vec, r_vec)
            gg = jax.lax.cond(tc > 0, lambda g: _tree_scale(-1.0, g), lambda g: g, gg)

            # Update solution
            x_new = _tree_axpy(-self.learning_rate, gg, x)

            # Orthonormalize new direction
            r_new = _tree_scale(-1.0, grad_fn(x_new))
            p_vec = flatten_to_vec(r_new)
            w = jnp.max(jnp.abs(p_vec))

            Ap = damped_matvec(r_new)
            Ap_vec = flatten_to_vec(Ap)

            # Orthogonalize against all stored vectors
            def orth_step(i, carry):
                p_v, Ap_v, w_val = carry
                tau = jnp.dot(Ap_v, AP_flat[i])
                tau = jnp.where(valid_mask[i], tau, 0.0)
                p_v = p_v - tau * P_flat[i]
                Ap_v = Ap_v - tau * AP_flat[i]
                w_val = w_val + jnp.abs(tau) * xrec[i]
                return (p_v, Ap_v, w_val)

            p_vec, Ap_vec, w = jax.lax.fori_loop(
                0, self.mem_size, orth_step, (p_vec, Ap_vec, w)
            )

            t = jnp.sqrt(jnp.dot(Ap_vec, Ap_vec))
            t_safe = t + eps

            # Restart condition
            restart = (w / t_safe > self.safeguard) | (t < eps)

            def do_restart(_):
                r_rst = _tree_scale(-1.0, grad_fn(x_new))
                r_v = flatten_to_vec(r_rst)
                Ar_rst = damped_matvec(r_rst)
                Ar_v = flatten_to_vec(Ar_rst)
                t_r = jnp.sqrt(jnp.dot(Ar_v, Ar_v))
                t_r_safe = t_r + eps

                P_new = jnp.zeros_like(P_flat).at[0].set(r_v / t_r_safe)
                AP_new = jnp.zeros_like(AP_flat).at[0].set(Ar_v / t_r_safe)
                valid_new = jnp.zeros_like(valid_mask).at[0].set(True)
                xrec_new = jnp.zeros_like(xrec)
                w0_r = jnp.max(jnp.abs(r_v))
                xrec_new = xrec_new.at[0].set(w0_r / t_r_safe)
                return (
                    P_new,
                    AP_new,
                    xrec_new,
                    valid_new,
                    jnp.array(1, dtype=jnp.int32),
                )

            def no_restart(_):
                idx = jnp.where(m < self.mem_size, m, self.mem_size - 1)
                do_shift = m >= self.mem_size

                P_upd = jnp.where(do_shift, jnp.roll(P_flat, -1, axis=0), P_flat)
                AP_upd = jnp.where(do_shift, jnp.roll(AP_flat, -1, axis=0), AP_flat)
                xrec_upd = jnp.where(do_shift, jnp.roll(xrec, -1), xrec)
                valid_upd = jnp.where(do_shift, jnp.roll(valid_mask, -1), valid_mask)

                P_upd = P_upd.at[idx].set(p_vec / t_safe)
                AP_upd = AP_upd.at[idx].set(Ap_vec / t_safe)
                xrec_upd = xrec_upd.at[idx].set(w / t_safe)
                valid_upd = valid_upd.at[idx].set(True)

                m_new = jnp.where(m < self.mem_size, m + 1, m)
                return (P_upd, AP_upd, xrec_upd, valid_upd, m_new)

            P_new, AP_new, xrec_new, valid_new, m_new = jax.lax.cond(
                restart, do_restart, no_restart, None
            )

            return (x_new, P_new, AP_new, xrec_new, valid_new, m_new)

        # Run iterations
        init_carry = (x, P_flat, AP_flat, xrec, valid_mask, m)
        final_x, P_final, AP_final, xrec_final, valid_final, m_final = (
            jax.lax.fori_loop(0, self.iters_per_batch, body_fn, init_carry)
        )

        # Update optimizer state with new subspace
        new_opt_state = {
            "P_flat": P_final,
            "AP_flat": AP_final,
            "xrec": xrec_final,
            "valid_mask": valid_final,
            "m": m_final,
            "total_iters": state.opt_state["total_iters"] + self.iters_per_batch,
        }

        # Add diagnostics to metrics
        metrics = {**metrics, "nltgcr_iters": self.iters_per_batch}

        # Create new training state
        new_state = state.replace(
            step=state.step + 1,
            params=final_x,
            opt_state=new_opt_state,
        )

        return new_state, metrics
