"""Anderson Acceleration (AA) Accelerator for wrapping any base optimizer.

AAAccelerator uses standard Type-II Anderson Acceleration with QR-based
least-squares solve to accelerate any base optimizer (SGD, Adam, etc.).

This provides a baseline for comparison with TGSAccelerator, which uses
Gram-Schmidt orthonormalization instead of direct least-squares.

References:
    Walker & Ni (2011): "Anderson Acceleration for Fixed-Point Iterations"
    https://doi.org/10.1137/10078356X
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


class AAAccelerator:
    """Anderson Acceleration wrapper for any base optimizer.

    AAAccelerator applies Type-II Anderson Acceleration using standard
    least-squares solve. This is simpler than TGS but may be less
    numerically stable for ill-conditioned problems.

    Args:
        base_optimizer: The base optimizer to accelerate (SGD, Adam, etc.)
        learning_rate: Step size mu for fixed-point mapping (default: 1.0)
        beta: Damping parameter for mixing (default: 1.0)
        mem_size: Memory size for stored differences (default: 5)
        regularization: Tikhonov regularization for least-squares (default: 1e-10)

    Example:
        >>> objective = Objective(terms=[pde_term, bc_term])
        >>> base = SGD(objective, learning_rate=0.1)
        >>> optimizer = AAAccelerator(base, learning_rate=0.1, mem_size=5)
        >>> state = optimizer.init(state)
        >>> for batch in train_data:
        ...     state, metrics = optimizer.step(state, batch)

    Note:
        - AAAccelerator is a baseline for comparison with TGSAccelerator
        - TGS uses Gram-Schmidt which is more numerically stable
        - AA uses direct least-squares which is simpler but may have issues
    """

    def __init__(
        self,
        base_optimizer: Any,
        learning_rate: float = 1.0,
        beta: float = 1.0,
        mem_size: int = 5,
        regularization: float = 1e-10,
    ):
        self.base = base_optimizer
        self.objective = base_optimizer.objective
        self.learning_rate = learning_rate
        self.beta = beta
        self.mem_size = mem_size
        self.regularization = regularization

    def init(
        self,
        state: Any,
        *,
        example_batch: Any = None,
        validate: bool = False,
    ) -> Any:
        """Initialize AAAccelerator state.

        Args:
            state: TrainState with params
            example_batch: Optional example batch for validation
            validate: Whether to validate objective evaluation

        Returns:
            TrainState with initialized opt_state containing:
                - base: Base optimizer's state
                - aa: AA acceleration state
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

        # Initialize AA state
        aa_state = {
            # Difference storage (rows are vectors, columns are memory slots)
            "DX_flat": jnp.zeros((self.mem_size, n_params), dtype=dtype),
            "DF_flat": jnp.zeros((self.mem_size, n_params), dtype=dtype),
            "valid_mask": jnp.zeros(self.mem_size, dtype=jnp.bool_),
            "m": jnp.array(0, dtype=jnp.int32),
            # Previous state tracking
            "x_old_vec": jnp.zeros(n_params, dtype=dtype),
            "f_old_vec": jnp.zeros(n_params, dtype=dtype),
            "initialized": jnp.array(False, dtype=jnp.bool_),
        }

        opt_state = {
            "base": base_opt_state,
            "aa": aa_state,
        }

        return state_with_base.replace(opt_state=opt_state)

    def step(
        self,
        state: Any,
        batch: Dict[str, Any],
    ) -> Tuple[Any, Dict[str, Any]]:
        """Perform one AA-accelerated optimization step.

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

        # Extract AA state
        aa = state.opt_state["aa"]
        DX_flat = aa["DX_flat"]
        DF_flat = aa["DF_flat"]
        valid_mask = aa["valid_mask"]
        m = aa["m"]
        x_old_vec = aa["x_old_vec"]
        f_old_vec = aa["f_old_vec"]
        initialized = aa["initialized"]

        # Create state with base optimizer's opt_state for base.step()
        base_state = state.replace(opt_state=state.opt_state["base"])

        # Call base optimizer to get proposed update
        base_new_state, metrics = self.base.step(base_state, batch)
        x_base = base_new_state.params
        base_opt_state_new = base_new_state.opt_state

        # Compute residual f = -learning_rate * grad(x_base)
        # This matches the fixed-point form: g(x) = x - lr * grad(x), f = g(x) - x
        grad_x = grad_fn(x_base)
        f = _tree_scale(-self.learning_rate, grad_x)
        f_vec = flatten_to_vec(f)
        x_vec = flatten_to_vec(x_base)

        # Handle first step (initialization)
        def first_step(_):
            """First step: just store current state, no acceleration."""
            return (
                x_base,
                DX_flat,
                DF_flat,
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

            # Determine index for new vector (circular buffer)
            idx = jnp.where(m < self.mem_size, m, self.mem_size - 1)

            # Shift if full
            do_shift = m >= self.mem_size
            DX_upd = jnp.where(do_shift, jnp.roll(DX_flat, -1, axis=0), DX_flat)
            DF_upd = jnp.where(do_shift, jnp.roll(DF_flat, -1, axis=0), DF_flat)
            valid_upd = jnp.where(do_shift, jnp.roll(valid_mask, -1), valid_mask)

            # Store new vectors
            DX_upd = DX_upd.at[idx].set(dx_vec)
            DF_upd = DF_upd.at[idx].set(df_vec)
            valid_upd = valid_upd.at[idx].set(True)

            m_new = jnp.where(m < self.mem_size, m + 1, m)

            # Solve least-squares using masking (no dynamic slicing)
            # Build gram matrix DF @ DF.T with masking
            # G[i,j] = DF[i] @ DF[j] if both valid, else identity contribution
            G = DF_upd @ DF_upd.T  # (mem_size, mem_size)

            # Mask invalid entries: set G[i,j] = 0 if either i or j is invalid
            # Also add regularization + identity for invalid entries
            mask_2d = valid_upd[:, None] & valid_upd[None, :]  # (mem_size, mem_size)
            G_masked = jnp.where(mask_2d, G, 0.0)

            # Add regularization to diagonal for valid entries
            # Add 1.0 to diagonal for invalid entries (makes them identity)
            diag_reg = jnp.where(valid_upd, self.regularization, 1.0)  # (mem_size,)
            G_reg = G_masked + jnp.diag(diag_reg)

            # Right-hand side: b = DF @ f, masked
            b = DF_upd @ f_vec  # (mem_size,)
            b_masked = jnp.where(valid_upd, b, 0.0)

            # Solve for gamma
            gamma = jnp.linalg.solve(G_reg, b_masked)

            # Mask gamma for invalid entries
            gamma_masked = jnp.where(valid_upd, gamma, 0.0)

            # Compute correction
            # dx_correction = DX.T @ gamma
            dx_correction = DX_upd.T @ gamma_masked  # (n_params,)

            # df_correction = DF.T @ gamma
            df_correction = DF_upd.T @ gamma_masked  # (n_params,)
            f_residual = f_vec - df_correction

            # x_next = y + beta * f_residual
            #        = (x - DX @ gamma) + beta * (f - DF @ gamma)
            x_new_vec = x_vec - dx_correction + self.beta * f_residual

            x_final = unflatten_from_vec(x_new_vec)

            return (
                x_final,
                DX_upd,
                DF_upd,
                valid_upd,
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

        # Update AA state
        new_aa_state = {
            "DX_flat": DX_new,
            "DF_flat": DF_new,
            "valid_mask": valid_new,
            "m": m_new,
            "x_old_vec": x_old_new,
            "f_old_vec": f_old_new,
            "initialized": init_new,
        }

        new_opt_state = {
            "base": base_opt_state_new,
            "aa": new_aa_state,
        }

        # Create new training state
        new_state = state.replace(
            step=state.step + 1,
            params=x_final,
            opt_state=new_opt_state,
        )

        return new_state, metrics
