"""TGS (Truncated Gram-Schmidt) accelerator for optimization.

JAX-compatible AATGS implementation using lax.fori_loop for JIT compilation.
TGS is an Anderson Acceleration variant using orthogonalized differences
instead of pseudoinverse, making it O(m) per iteration instead of O(m^3).

References:
    https://arxiv.org/abs/2306.00325
"""

from __future__ import annotations

from typing import Any, Callable, NamedTuple, Tuple

import jax
import jax.numpy as jnp


class TGSState(NamedTuple):
    """State for TGS iteration."""

    x: Any  # Current solution (pytree)
    f: Any  # Current residual = -gradient (pytree)
    DX: Any  # Solution differences (stacked array, mem_size x n_params)
    DF: Any  # Residual differences (stacked array, mem_size x n_params)
    xrec: jnp.ndarray  # Worst-case tracking (mem_size,)
    valid_mask: jnp.ndarray  # Which entries are valid (mem_size,)
    m: jnp.ndarray  # Number of stored vectors
    k: jnp.ndarray  # Iteration count


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


def _tree_sub(x: Any, y: Any) -> Any:
    """Compute x - y for pytrees."""
    return jax.tree_util.tree_map(lambda xi, yi: xi - yi, x, y)


def _tree_add(x: Any, y: Any) -> Any:
    """Compute x + y for pytrees."""
    return jax.tree_util.tree_map(lambda xi, yi: xi + yi, x, y)


def _tree_norm_inf(x: Any) -> jnp.ndarray:
    """Compute infinity norm of pytree."""
    leaves = jax.tree_util.tree_leaves(x)
    return max(jnp.max(jnp.abs(leaf)) for leaf in leaves)


def _get_eps(x: jnp.ndarray) -> float:
    """Get epsilon for division safety based on dtype."""
    if x.dtype == jnp.float32:
        return 1e-20
    else:
        return 1e-30


def tgs_solve(
    grad_fn: Callable[[Any], Any],
    x0: Any,
    maxiter: int = 10,
    mem_size: int = 5,
    learning_rate: float = 1.0,
    safeguard: float = 1e3,
) -> Tuple[Any, int]:
    """Solve optimization using TGS (Truncated Gram-Schmidt Anderson) method.

    TGS is an Anderson Acceleration variant that uses Gram-Schmidt
    orthogonalization instead of pseudoinverse. No curvature matvec needed.

    Args:
        grad_fn: Function that computes gradient at a point.
            Must accept and return pytrees with same structure as x0.
        x0: Initial guess (pytree).
        maxiter: Maximum number of iterations.
        mem_size: Window size for stored differences.
        learning_rate: Step size for updates (applied at each iteration).
        safeguard: Threshold for automatic restart (based on worst-case tracking).

    Returns:
        Tuple of (x, info) where:
            x: Solution pytree
            info: Number of iterations performed

    Example:
        >>> def grad_fn(x): return A @ x - b
        >>> x, iters = tgs_solve(grad_fn, x0, maxiter=10)
    """
    x = x0
    f = _tree_scale(-1.0, grad_fn(x))  # f = -grad(x)

    # First step: x = x + learning_rate * f
    x = _tree_axpy(learning_rate, f, x)

    # Storage for differences (as lists initially)
    DX_list = []
    DF_list = []
    xrec = jnp.zeros(mem_size)

    x_old = x0
    f_old = f

    eps = _get_eps(jnp.zeros((), dtype=jnp.float32))

    for k in range(maxiter):
        # Get new residual
        f = _tree_scale(-1.0, grad_fn(x))

        # Compute differences
        df = _tree_sub(f, f_old)
        dx = _tree_sub(x, x_old)
        t0 = _tree_norm_inf(dx)

        # Orthogonalize against stored DF vectors
        m = len(DF_list)
        for j in range(m):
            rj = _tree_dot(DF_list[j], df)
            df = _tree_axpy(-rj, DF_list[j], df)
            dx = _tree_axpy(-rj, DX_list[j], dx)

        # Normalize
        t = jnp.sqrt(_tree_dot(df, df))
        t_safe = t + eps

        # Check restart condition
        if m == 0:
            s = t0 / t_safe
        else:
            s = sum(jnp.abs(_tree_dot(DF_list[j], f)) * xrec[j] for j in range(m))
            s = (t0 + s) / t_safe
        xrec_norm = jnp.sqrt(jnp.sum(xrec[:m] ** 2) + s**2) if m > 0 else s

        if xrec_norm > safeguard or t < eps:
            # Restart
            DX_list = []
            DF_list = []
            xrec = jnp.zeros(mem_size)
            x_old = x
            f_old = f
            x = _tree_axpy(learning_rate, f, x)
            continue

        # Store normalized vectors
        if len(DF_list) < mem_size:
            DF_list.append(_tree_scale(1.0 / t_safe, df))
            DX_list.append(_tree_scale(1.0 / t_safe, dx))
            idx = len(DF_list) - 1
        else:
            # Circular buffer: remove oldest, add newest
            DF_list = DF_list[1:] + [_tree_scale(1.0 / t_safe, df)]
            DX_list = DX_list[1:] + [_tree_scale(1.0 / t_safe, dx)]
            xrec = jnp.roll(xrec, -1)
            idx = mem_size - 1

        xrec = xrec.at[idx].set(s)

        # Compute update direction: d = -DX * gamma + learning_rate * (f - DF * gamma)
        # where gamma = DF' * f
        m = len(DF_list)
        gamma = jnp.array([_tree_dot(DF_list[j], f) for j in range(m)])

        # d = -sum_j gamma[j] * DX[j] + learning_rate * (f - sum_j gamma[j] * DF[j])
        d_dx = _tree_scale(0.0, x)  # zero like x
        d_df = _tree_scale(0.0, x)
        for j in range(m):
            d_dx = _tree_axpy(-gamma[j], DX_list[j], d_dx)
            d_df = _tree_axpy(-gamma[j], DF_list[j], d_df)

        # d = d_dx + learning_rate * (f + d_df)
        f_residual = _tree_add(f, d_df)
        d = _tree_axpy(learning_rate, f_residual, d_dx)

        # Update
        x_old = x
        f_old = f
        x = _tree_add(x, d)

    return x, maxiter


def tgs_solve_fori(
    grad_fn: Callable[[Any], Any],
    x0: Any,
    maxiter: int = 10,
    mem_size: int = 5,
    learning_rate: float = 1.0,
    safeguard: float = 1e3,
    reversed: bool = False,
) -> Tuple[Any, int]:
    """Solve optimization using TGS with fixed iteration count (fori_loop).

    JIT-compatible version using flattened arrays for DX and DF storage.
    Uses jax.lax.fori_loop for guaranteed compilation.

    Args:
        grad_fn: Function that computes gradient at a point.
        x0: Initial guess (pytree).
        maxiter: Exact number of iterations to perform.
        mem_size: Window size for stored differences.
        learning_rate: Step size for updates (applied at each iteration).
        safeguard: Threshold for automatic restart.
        reversed: If True, use Reversed TGS (RTGS) which transfers information
            from the about-to-be-discarded oldest vector into the basis before
            removal. This can improve convergence in some cases.

    Returns:
        Tuple of (x, info) where:
            x: Solution pytree
            info: Number of iterations (always maxiter)
    """
    # Get structure info from x0 (traced-safe)
    flat_x0, tree_def = jax.tree_util.tree_flatten(x0)
    shapes = [p.shape for p in flat_x0]
    sizes = [p.size for p in flat_x0]
    n_params = sum(sizes)
    dtype = flat_x0[0].dtype
    eps = _get_eps(jnp.zeros((), dtype=dtype))

    # Helper functions that are trace-safe
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

    # Initialize
    x = x0
    f = _tree_scale(-1.0, grad_fn(x))

    # First step: x = x + learning_rate * f
    x = _tree_axpy(learning_rate, f, x)

    x_old = x0
    f_old_vec = flatten_to_vec(f)
    x_old_vec = flatten_to_vec(x0)

    # Store DX, DF as stacked arrays with mask for valid entries
    DX_flat = jnp.zeros((mem_size, n_params), dtype=dtype)
    DF_flat = jnp.zeros((mem_size, n_params), dtype=dtype)
    valid_mask = jnp.zeros(mem_size, dtype=jnp.bool_)
    xrec = jnp.zeros(mem_size, dtype=dtype)

    m = jnp.array(0, dtype=jnp.int32)  # Number of stored vectors

    def body_fn(k, carry):
        x, x_old_vec, f_old_vec, DX_flat, DF_flat, xrec, valid_mask, m = carry

        # Get new residual
        f = _tree_scale(-1.0, grad_fn(x))
        f_vec = flatten_to_vec(f)
        x_vec = flatten_to_vec(x)

        # Compute differences
        df_vec = f_vec - f_old_vec
        dx_vec = x_vec - x_old_vec
        t0 = jnp.max(jnp.abs(dx_vec))

        # For reversed TGS, skip index 0 when window is full
        if reversed:
            orth_mask = jax.lax.cond(
                m >= mem_size,
                lambda vm: vm.at[0].set(False),
                lambda vm: vm,
                valid_mask,
            )
        else:
            orth_mask = valid_mask

        # Orthogonalize against stored DF vectors (masked)
        def orth_step(i, carry):
            df_v, dx_v, w_val = carry
            rj = jnp.dot(DF_flat[i], df_v)
            rj = jnp.where(orth_mask[i], rj, 0.0)
            df_v = df_v - rj * DF_flat[i]
            dx_v = dx_v - rj * DX_flat[i]
            w_val = w_val + jnp.abs(rj) * xrec[i]
            return (df_v, dx_v, w_val)

        df_vec, dx_vec, w = jax.lax.fori_loop(
            0, mem_size, orth_step, (df_vec, dx_vec, t0)
        )

        # Normalize
        t = jnp.sqrt(jnp.dot(df_vec, df_vec))
        t_safe = t + eps

        # Worst-case estimation
        s = w / t_safe

        # Check restart condition
        xrec_norm = jnp.sqrt(jnp.sum(jnp.where(valid_mask, xrec**2, 0.0)) + s**2)
        restart = (xrec_norm > safeguard) | (t < eps)

        def do_restart(_):
            # Restart: clear stored vectors
            DX_new = jnp.zeros_like(DX_flat)
            DF_new = jnp.zeros_like(DF_flat)
            valid_new = jnp.zeros_like(valid_mask)
            xrec_new = jnp.zeros_like(xrec)

            # First step after restart
            x_new = _tree_axpy(learning_rate, f, x)
            x_new_vec = flatten_to_vec(x_new)

            return (
                x_new,
                x_vec,
                f_vec,
                DX_new,
                DF_new,
                xrec_new,
                valid_new,
                jnp.array(0, dtype=jnp.int32),
            )

        def no_restart(_):
            # Determine index for new vector
            idx = jnp.where(m < mem_size, m, mem_size - 1)

            # Shift if full (roll all arrays)
            do_shift = m >= mem_size
            DX_upd = jnp.where(do_shift, jnp.roll(DX_flat, -1, axis=0), DX_flat)
            DF_upd = jnp.where(do_shift, jnp.roll(DF_flat, -1, axis=0), DF_flat)
            xrec_upd = jnp.where(do_shift, jnp.roll(xrec, -1), xrec)
            valid_upd = jnp.where(do_shift, jnp.roll(valid_mask, -1), valid_mask)

            # Store new vectors
            DX_upd = DX_upd.at[idx].set(dx_vec / t_safe)
            DF_upd = DF_upd.at[idx].set(df_vec / t_safe)
            xrec_upd = xrec_upd.at[idx].set(s)
            valid_upd = valid_upd.at[idx].set(True)

            # For reversed TGS: apply reverse GS when window is full
            # This orthogonalizes the oldest vector against the newest,
            # transferring information before the oldest is shifted out
            if reversed:

                def apply_reverse_gs(args):
                    DX_r, DF_r = args
                    # Orthogonalize oldest (index 0) against newest (index mem_size-1)
                    r0 = jnp.dot(DF_r[mem_size - 1], DF_r[0])
                    df0_new = DF_r[0] - r0 * DF_r[mem_size - 1]
                    dx0_new = DX_r[0] - r0 * DX_r[mem_size - 1]
                    t2 = jnp.sqrt(jnp.dot(df0_new, df0_new)) + eps
                    return (
                        DX_r.at[0].set(dx0_new / t2),
                        DF_r.at[0].set(df0_new / t2),
                    )

                def no_reverse_gs(args):
                    return args

                DX_upd, DF_upd = jax.lax.cond(
                    m >= mem_size,
                    apply_reverse_gs,
                    no_reverse_gs,
                    (DX_upd, DF_upd),
                )

            m_new = jnp.where(m < mem_size, m + 1, m)

            # Compute update direction: d = -DX * gamma + learning_rate * (f - DF * gamma)
            # gamma = DF' * f (masked)
            gamma = jnp.sum(DF_upd * f_vec[None, :], axis=1)
            gamma = jnp.where(valid_upd, gamma, 0.0)

            # d_dx = -sum_j gamma[j] * DX[j]
            d_dx_vec = -jnp.sum(DX_upd * gamma[:, None], axis=0)

            # f_residual = f - sum_j gamma[j] * DF[j]
            f_res_vec = f_vec - jnp.sum(DF_upd * gamma[:, None], axis=0)

            # d = d_dx + learning_rate * f_residual
            d_vec = d_dx_vec + learning_rate * f_res_vec

            # Update: x_new = x + d
            x_new_vec = x_vec + d_vec
            x_new = unflatten_from_vec(x_new_vec)

            return (
                x_new,
                x_vec,
                f_vec,
                DX_upd,
                DF_upd,
                xrec_upd,
                valid_upd,
                m_new,
            )

        return jax.lax.cond(restart, do_restart, no_restart, None)

    init_carry = (x, x_old_vec, f_old_vec, DX_flat, DF_flat, xrec, valid_mask, m)
    final_x, _, _, _, _, _, _, _ = jax.lax.fori_loop(0, maxiter, body_fn, init_carry)

    return final_x, maxiter
