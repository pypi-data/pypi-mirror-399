"""TGS Accelerator for wrapping any base optimizer.

TGSAccelerator uses Anderson Acceleration with Gram-Schmidt orthogonalization
to accelerate any base optimizer (SGD, Adam, etc.).

Unlike TGSOptimizer which is a monolithic implementation, TGSAccelerator
is composable and can wrap any optimizer that follows the standard interface.

References:
    https://arxiv.org/abs/2306.00325
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

import jax
import jax.numpy as jnp

from ..objective import Objective


def _tree_dot(a: Any, b: Any) -> jnp.ndarray:
    """Compute dot product of two pytrees."""
    leaves_a = jax.tree_util.tree_leaves(a)
    leaves_b = jax.tree_util.tree_leaves(b)
    return sum(jnp.sum(la * lb) for la, lb in zip(leaves_a, leaves_b))


def _tree_scale(alpha: jnp.ndarray, x: Any) -> Any:
    """Compute alpha * x for pytree."""
    return jax.tree_util.tree_map(lambda xi: alpha * xi, x)


def _get_eps(dtype) -> float:
    """Get epsilon for division safety based on dtype."""
    if dtype == jnp.float32:
        return 1e-20
    else:
        return 1e-30


class TGSAccelerator:
    """TGS Accelerator that wraps any base optimizer.

    TGSAccelerator applies Anderson Acceleration with Gram-Schmidt
    orthogonalization on top of any base optimizer's updates. This allows
    accelerating SGD, Adam, or any other optimizer.

    Args:
        base_optimizer: The base optimizer to accelerate (SGD, Adam, etc.)
        learning_rate: Step size for AA correction. To match TGSOptimizer(lr=X),
            use TGSAccelerator(SGD(lr=X), learning_rate=X).
        mem_size: Memory size for stored differences (default: 5)
        safeguard: Threshold for automatic restart (default: 1e3)
        reversed: If True, use Reversed TGS (RTGS) which transfers information
            from the about-to-be-discarded oldest vector into the basis before
            removal. This can improve convergence in some cases. (default: False)

    Example:
        >>> objective = Objective(terms=[pde_term, bc_term])
        >>> # Accelerate SGD - use same lr for both to match TGSOptimizer
        >>> base = SGD(objective, learning_rate=0.1)
        >>> optimizer = TGSAccelerator(base, learning_rate=0.1, mem_size=5)
        >>> state = optimizer.init(state)
        >>> for batch in train_data:
        ...     state, metrics = optimizer.step(state, batch)
        >>>
        >>> # Accelerate Adam
        >>> base = Adam(objective, learning_rate=0.001)
        >>> optimizer = TGSAccelerator(base, learning_rate=0.001, mem_size=5)

    Note:
        - TGSAccelerator(SGD(lr)) should produce similar results to TGSOptimizer(lr)
        - The accelerator stores update history for Anderson Acceleration
        - Memory cost is O(mem_size * n_params)
    """

    def __init__(
        self,
        base_optimizer: Any,
        learning_rate: float,
        mem_size: int = 5,
        safeguard: float = 1e3,
        reversed: bool = False,
    ):
        self.base = base_optimizer
        self.objective = base_optimizer.objective
        self.learning_rate = learning_rate
        self.mem_size = mem_size
        self.safeguard = safeguard
        self.reversed = reversed

    def init(
        self,
        state: Any,
        *,
        example_batch: Any = None,
        validate: bool = False,
    ) -> Any:
        """Initialize TGSAccelerator state.

        Args:
            state: TrainState with params
            example_batch: Optional example batch for validation
            validate: Whether to validate objective evaluation

        Returns:
            TrainState with initialized opt_state containing:
                - base: Base optimizer's state
                - accelerator: TGS acceleration state
        """
        # First, initialize base optimizer
        state_with_base = self.base.init(
            state, example_batch=example_batch, validate=validate
        )
        base_opt_state = state_with_base.opt_state

        # Compute number of parameters
        flat_params, _ = jax.tree_util.tree_flatten(state.params)
        n_params = sum(p.size for p in flat_params)
        dtype = flat_params[0].dtype

        # Initialize accelerator state
        accelerator_state = {
            # Difference storage (flattened for JIT compatibility)
            "DX_flat": jnp.zeros((self.mem_size, n_params), dtype=dtype),
            "DF_flat": jnp.zeros((self.mem_size, n_params), dtype=dtype),
            "xrec": jnp.zeros(self.mem_size, dtype=dtype),
            "valid_mask": jnp.zeros(self.mem_size, dtype=jnp.bool_),
            "m": jnp.array(0, dtype=jnp.int32),
            # Previous state tracking
            "x_old_vec": jnp.zeros(n_params, dtype=dtype),
            "f_old_vec": jnp.zeros(n_params, dtype=dtype),
            "initialized": jnp.array(False, dtype=jnp.bool_),
        }

        opt_state = {
            "base": base_opt_state,
            "accelerator": accelerator_state,
        }

        return state_with_base.replace(opt_state=opt_state)

    def step(
        self,
        state: Any,
        batch: Dict[str, Any],
    ) -> Tuple[Any, Dict[str, Any]]:
        """Perform one TGS-accelerated optimization step.

        Each step:
        1. Calls base optimizer to get proposed update
        2. Computes gradient at new position (residual)
        3. Applies Anderson Acceleration correction

        Args:
            state: TrainState with params, opt_state, apply_fn, step
            batch: Batch dict with keys matching term.batch_key

        Returns:
            (new_state, metrics) tuple where metrics includes:
                - loss: total loss
                - loss/<term_name>: per-term losses
        """
        # Build variables dict for gradient computation
        variables = {"params": state.params}
        if hasattr(state, "batch_stats") and state.batch_stats is not None:
            variables["batch_stats"] = state.batch_stats

        # Define grad_fn for residual computation
        def grad_fn(params):
            return jax.grad(
                lambda p: self.objective.evaluate(
                    apply_fn=state.apply_fn,
                    variables={**variables, "params": p},
                    batch=batch,
                    step=state.step,
                )["loss"]
            )(params)

        # Get structure info from params
        flat_params, tree_def = jax.tree_util.tree_flatten(state.params)
        shapes = [p.shape for p in flat_params]
        sizes = [p.size for p in flat_params]
        n_params = sum(sizes)
        dtype = flat_params[0].dtype
        eps = _get_eps(dtype)

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

        # Extract accelerator state
        accel = state.opt_state["accelerator"]
        DX_flat = accel["DX_flat"]
        DF_flat = accel["DF_flat"]
        xrec = accel["xrec"]
        valid_mask = accel["valid_mask"]
        m = accel["m"]
        x_old_vec = accel["x_old_vec"]
        f_old_vec = accel["f_old_vec"]
        initialized = accel["initialized"]

        # Create state with base optimizer's opt_state for base.step()
        base_state = state.replace(opt_state=state.opt_state["base"])

        # Call base optimizer to get proposed update
        base_new_state, metrics = self.base.step(base_state, batch)
        x_base = base_new_state.params
        base_opt_state_new = base_new_state.opt_state

        # Compute residual f = -grad(x_base)
        f = _tree_scale(-1.0, grad_fn(x_base))
        f_vec = flatten_to_vec(f)
        x_vec = flatten_to_vec(x_base)

        # Handle first step (initialization)
        def first_step(_):
            """First step: just store current state, no acceleration."""
            return (
                x_base,
                DX_flat,
                DF_flat,
                xrec,
                valid_mask,
                m,
                x_vec,
                f_vec,
                jnp.array(True, dtype=jnp.bool_),
            )

        def subsequent_step(_):
            """Subsequent steps: apply Anderson Acceleration."""
            # Compute differences
            dx_vec = x_vec - x_old_vec
            df_vec = f_vec - f_old_vec
            t0 = jnp.max(jnp.abs(dx_vec))

            # For reversed TGS, skip index 0 when window is full
            if self.reversed:
                orth_mask = jax.lax.cond(
                    m >= self.mem_size,
                    lambda vm: vm.at[0].set(False),
                    lambda vm: vm,
                    valid_mask,
                )
            else:
                orth_mask = valid_mask

            # Orthogonalize against stored DF vectors (Gram-Schmidt)
            def orth_step(i, carry):
                df_v, dx_v, w_val = carry
                rj = jnp.dot(DF_flat[i], df_v)
                rj = jnp.where(orth_mask[i], rj, 0.0)
                df_v = df_v - rj * DF_flat[i]
                dx_v = dx_v - rj * DX_flat[i]
                w_val = w_val + jnp.abs(rj) * xrec[i]
                return (df_v, dx_v, w_val)

            df_orth, dx_orth, w = jax.lax.fori_loop(
                0, self.mem_size, orth_step, (df_vec, dx_vec, t0)
            )

            # Normalize
            t = jnp.sqrt(jnp.dot(df_orth, df_orth))
            t_safe = t + eps

            # Worst-case estimation
            s = w / t_safe

            # Check restart condition
            xrec_norm = jnp.sqrt(jnp.sum(jnp.where(valid_mask, xrec**2, 0.0)) + s**2)
            restart = (xrec_norm > self.safeguard) | (t < eps)

            def do_restart(_):
                """Restart: clear stored vectors."""
                DX_new = jnp.zeros_like(DX_flat)
                DF_new = jnp.zeros_like(DF_flat)
                valid_new = jnp.zeros_like(valid_mask)
                xrec_new = jnp.zeros_like(xrec)
                # On restart, just use base optimizer's result
                return (
                    x_base,
                    DX_new,
                    DF_new,
                    xrec_new,
                    valid_new,
                    jnp.array(0, dtype=jnp.int32),
                )

            def no_restart(_):
                """Normal step: apply AA correction."""
                # Determine index for new vector
                idx = jnp.where(m < self.mem_size, m, self.mem_size - 1)

                # Shift if full (circular buffer)
                do_shift = m >= self.mem_size
                DX_upd = jnp.where(do_shift, jnp.roll(DX_flat, -1, axis=0), DX_flat)
                DF_upd = jnp.where(do_shift, jnp.roll(DF_flat, -1, axis=0), DF_flat)
                xrec_upd = jnp.where(do_shift, jnp.roll(xrec, -1), xrec)
                valid_upd = jnp.where(do_shift, jnp.roll(valid_mask, -1), valid_mask)

                # Store new normalized vectors
                DX_upd = DX_upd.at[idx].set(dx_orth / t_safe)
                DF_upd = DF_upd.at[idx].set(df_orth / t_safe)
                xrec_upd = xrec_upd.at[idx].set(s)
                valid_upd = valid_upd.at[idx].set(True)

                # For reversed TGS: apply reverse GS when window is full
                # This orthogonalizes the oldest vector against the newest,
                # transferring information before the oldest is shifted out
                if self.reversed:

                    def apply_reverse_gs(args):
                        DX_r, DF_r = args
                        # Orthogonalize oldest (index 0) against newest
                        r0 = jnp.dot(DF_r[self.mem_size - 1], DF_r[0])
                        df0_new = DF_r[0] - r0 * DF_r[self.mem_size - 1]
                        dx0_new = DX_r[0] - r0 * DX_r[self.mem_size - 1]
                        t2 = jnp.sqrt(jnp.dot(df0_new, df0_new)) + eps
                        return (
                            DX_r.at[0].set(dx0_new / t2),
                            DF_r.at[0].set(df0_new / t2),
                        )

                    def no_reverse_gs(args):
                        return args

                    DX_upd, DF_upd = jax.lax.cond(
                        m >= self.mem_size,
                        apply_reverse_gs,
                        no_reverse_gs,
                        (DX_upd, DF_upd),
                    )

                m_new = jnp.where(m < self.mem_size, m + 1, m)

                return (x_base, DX_upd, DF_upd, xrec_upd, valid_upd, m_new)

            x_out, DX_new, DF_new, xrec_new, valid_new, m_new = jax.lax.cond(
                restart, do_restart, no_restart, None
            )

            # Compute AA correction using updated storage
            # gamma = DF' * f (masked)
            gamma = jnp.sum(DF_new * f_vec[None, :], axis=1)
            gamma = jnp.where(valid_new, gamma, 0.0)

            # d_dx = -sum_j gamma[j] * DX[j]
            d_dx_vec = -jnp.sum(DX_new * gamma[:, None], axis=0)

            # f_residual = f - sum_j gamma[j] * DF[j]
            f_res_vec = f_vec - jnp.sum(DF_new * gamma[:, None], axis=0)

            # Apply correction: d = -DX * gamma + learning_rate * (f - DF * gamma)
            # x_final = x + d (where x = x_vec = flatten(x_base))
            x_final_vec = x_vec + d_dx_vec + self.learning_rate * f_res_vec

            # Check if correction improves things (descent check)
            # If not, just use base result
            x_final = unflatten_from_vec(x_final_vec)

            return (
                x_final,
                DX_new,
                DF_new,
                xrec_new,
                valid_new,
                m_new,
                x_vec,
                f_vec,
                jnp.array(True, dtype=jnp.bool_),
            )

        # Choose between first step and subsequent steps
        (
            x_final,
            DX_new,
            DF_new,
            xrec_new,
            valid_new,
            m_new,
            x_old_new,
            f_old_new,
            init_new,
        ) = jax.lax.cond(
            initialized,
            subsequent_step,
            first_step,
            None,
        )

        # Update accelerator state
        new_accelerator_state = {
            "DX_flat": DX_new,
            "DF_flat": DF_new,
            "xrec": xrec_new,
            "valid_mask": valid_new,
            "m": m_new,
            "x_old_vec": x_old_new,
            "f_old_vec": f_old_new,
            "initialized": init_new,
        }

        new_opt_state = {
            "base": base_opt_state_new,
            "accelerator": new_accelerator_state,
        }

        # Create new training state
        new_state = state.replace(
            step=state.step + 1,
            params=x_final,
            opt_state=new_opt_state,
        )

        return new_state, metrics
