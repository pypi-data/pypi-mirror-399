"""Nonlinear Truncated GCR solver for optimization.

JAX-compatible NLTGCR implementation using lax.fori_loop for JIT compilation.
NLTGCR combines search directions orthogonalized against curvature-mapped vectors.

References:
    https://arxiv.org/abs/2306.00325
"""

from __future__ import annotations

from typing import Any, Callable, NamedTuple, Optional, Tuple

import jax
import jax.numpy as jnp


class NLTGCRState(NamedTuple):
    """State for NLTGCR iteration."""

    x: Any  # Current solution (pytree)
    r: Any  # Residual = -gradient (pytree)
    P: Any  # Search directions (list of pytrees, length mem_size)
    AP: Any  # Curvature-mapped directions (list of pytrees, length mem_size)
    xrec: jnp.ndarray  # Worst-case tracking (mem_size,)
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


def _tree_zeros_like(x: Any) -> Any:
    """Create pytree of zeros with same structure."""
    return jax.tree_util.tree_map(jnp.zeros_like, x)


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


def nltgcr_solve(
    matvec: Callable[[Any], Any],
    grad_fn: Callable[[Any], Any],
    x0: Any,
    maxiter: int = 10,
    mem_size: int = 5,
    learning_rate: float = 1.0,
    safeguard: float = 1e3,
) -> Tuple[Any, int]:
    """Solve optimization using NLTGCR method.

    NLTGCR (Nonlinear Truncated GCR) combines search directions orthogonalized
    against curvature-mapped vectors to accelerate optimization.

    Args:
        matvec: Function that computes curvature-vector product (Fisher or Hessian).
            Must accept and return pytrees with same structure as x0.
        grad_fn: Function that computes gradient at a point.
            Must accept and return pytrees with same structure as x0.
        x0: Initial guess (pytree).
        maxiter: Maximum number of iterations.
        mem_size: Window size for stored vectors.
        learning_rate: Step size for updates (applied at each iteration).
        safeguard: Threshold for automatic restart (based on worst-case tracking).

    Returns:
        Tuple of (x, info) where:
            x: Solution pytree
            info: Number of iterations performed

    Example:
        >>> # Optimize using Fisher curvature
        >>> fisher_mv = build_fisher_matvec(objective, state, batch)
        >>> grad_fn = lambda x: objective.grad(x, batch)
        >>> x, iters = nltgcr_solve(fisher_mv, grad_fn, params, maxiter=10)
    """
    x = x0
    r = _tree_scale(-1.0, grad_fn(x))  # r = -grad
    Ar = matvec(r)

    # Normalize first direction
    t = jnp.sqrt(_tree_dot(Ar, Ar))
    eps = _get_eps(t)
    t_safe = t + eps

    # Initialize P, AP as lists with first entry
    P = [_tree_scale(1.0 / t_safe, r)]
    AP = [_tree_scale(1.0 / t_safe, Ar)]
    xrec = jnp.zeros(mem_size)
    w0 = _tree_norm_inf(r)
    xrec = xrec.at[0].set(w0 / t_safe)

    m = jnp.array(1)  # One vector stored

    for k in range(maxiter):
        # Compute combined search direction: gg = P * (AP' * r)
        # alpha[i] = AP[i] · r, then gg = sum_i alpha[i] * P[i]
        gg = _tree_zeros_like(r)
        for i in range(len(AP)):
            alpha_i = _tree_dot(AP[i], r)
            gg = _tree_axpy(alpha_i, P[i], gg)

        # Descent direction check
        tc = _tree_dot(gg, r)
        # If tc > 0 (using params -= lr*gg convention), flip direction
        gg = jax.lax.cond(tc > 0, lambda g: _tree_scale(-1.0, g), lambda g: g, gg)

        # Update solution
        x = _tree_axpy(-learning_rate, gg, x)  # x = x - learning_rate * gg
        r = _tree_scale(-1.0, grad_fn(x))  # r = -grad(x)

        # Orthonormalize new direction
        p = r
        w = _tree_norm_inf(p)
        Ap = matvec(r)

        # Orthogonalize against stored AP vectors
        for i in range(len(AP)):
            tau = _tree_dot(Ap, AP[i])
            p = _tree_axpy(-tau, P[i], p)
            Ap = _tree_axpy(-tau, AP[i], Ap)
            w = w + jnp.abs(tau) * xrec[i]

        # Normalize
        t = jnp.sqrt(_tree_dot(Ap, Ap))
        t_safe = t + eps

        # Check for restart condition
        if w / t_safe > safeguard or t < eps:
            # Restart: clear stored vectors, reinitialize
            r = _tree_scale(-1.0, grad_fn(x))
            Ar = matvec(r)
            t = jnp.sqrt(_tree_dot(Ar, Ar))
            t_safe = t + eps
            P = [_tree_scale(1.0 / t_safe, r)]
            AP = [_tree_scale(1.0 / t_safe, Ar)]
            xrec = jnp.zeros(mem_size)
            w0 = _tree_norm_inf(r)
            xrec = xrec.at[0].set(w0 / t_safe)
            continue

        # Store new vectors
        if len(P) < mem_size:
            P.append(_tree_scale(1.0 / t_safe, p))
            AP.append(_tree_scale(1.0 / t_safe, Ap))
            idx = len(P) - 1
        else:
            # Circular buffer: remove oldest, add newest
            P = P[1:] + [_tree_scale(1.0 / t_safe, p)]
            AP = AP[1:] + [_tree_scale(1.0 / t_safe, Ap)]
            xrec = jnp.roll(xrec, -1)
            idx = mem_size - 1

        xrec = xrec.at[idx].set(w / t_safe)

    return x, maxiter


def nltgcr_solve_fori(
    matvec: Callable[[Any], Any],
    grad_fn: Callable[[Any], Any],
    x0: Any,
    maxiter: int = 10,
    mem_size: int = 5,
    learning_rate: float = 1.0,
    safeguard: float = 1e3,
) -> Tuple[Any, int]:
    """Solve optimization using NLTGCR with fixed iteration count (fori_loop).

    JIT-compatible version using flattened arrays for P and AP storage.
    Uses jax.lax.fori_loop for guaranteed compilation.

    Args:
        matvec: Function that computes curvature-vector product.
        grad_fn: Function that computes gradient at a point.
        x0: Initial guess (pytree).
        maxiter: Exact number of iterations to perform.
        mem_size: Window size for stored vectors.
        learning_rate: Step size for updates (applied at each iteration).
        safeguard: Threshold for automatic restart.

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
    r = _tree_scale(-1.0, grad_fn(x))
    Ar = matvec(r)

    r_vec = flatten_to_vec(r)
    Ar_vec = flatten_to_vec(Ar)

    t = jnp.sqrt(jnp.dot(Ar_vec, Ar_vec))
    t_safe = t + eps

    # Store P, AP as stacked arrays with mask for valid entries
    P_flat = jnp.zeros((mem_size, n_params), dtype=dtype)
    AP_flat = jnp.zeros((mem_size, n_params), dtype=dtype)
    valid_mask = jnp.zeros(mem_size, dtype=jnp.bool_)

    P_flat = P_flat.at[0].set(r_vec / t_safe)
    AP_flat = AP_flat.at[0].set(Ar_vec / t_safe)
    valid_mask = valid_mask.at[0].set(True)

    xrec = jnp.zeros(mem_size, dtype=dtype)
    w0 = jnp.max(jnp.abs(r_vec))
    xrec = xrec.at[0].set(w0 / t_safe)

    m = jnp.array(1, dtype=jnp.int32)  # Number of stored vectors

    def body_fn(k, carry):
        x, P_flat, AP_flat, xrec, valid_mask, m = carry

        r = _tree_scale(-1.0, grad_fn(x))
        r_vec = flatten_to_vec(r)

        # Compute gg using full arrays with masking
        # alphas[i] = AP[i] · r, but zero for invalid entries
        alphas = jnp.sum(AP_flat * r_vec[None, :], axis=1)  # (mem_size,)
        alphas = jnp.where(valid_mask, alphas, 0.0)

        # gg = sum_i alpha_i * P_i
        gg_vec = jnp.sum(P_flat * alphas[:, None], axis=0)  # (n_params,)
        gg = unflatten_from_vec(gg_vec)

        # Descent check
        tc = jnp.dot(gg_vec, r_vec)
        gg = jax.lax.cond(tc > 0, lambda g: _tree_scale(-1.0, g), lambda g: g, gg)

        # Update solution
        x_new = _tree_axpy(-learning_rate, gg, x)

        # Orthonormalize new direction
        r_new = _tree_scale(-1.0, grad_fn(x_new))
        p_vec = flatten_to_vec(r_new)
        w = jnp.max(jnp.abs(p_vec))

        Ap = matvec(r_new)
        Ap_vec = flatten_to_vec(Ap)

        # Orthogonalize against all stored vectors (masked)
        def orth_step(i, carry):
            p_v, Ap_v, w_val = carry
            tau = jnp.dot(Ap_v, AP_flat[i])
            tau = jnp.where(valid_mask[i], tau, 0.0)
            p_v = p_v - tau * P_flat[i]
            Ap_v = Ap_v - tau * AP_flat[i]
            w_val = w_val + jnp.abs(tau) * xrec[i]
            return (p_v, Ap_v, w_val)

        p_vec, Ap_vec, w = jax.lax.fori_loop(0, mem_size, orth_step, (p_vec, Ap_vec, w))

        t = jnp.sqrt(jnp.dot(Ap_vec, Ap_vec))
        t_safe = t + eps

        # Restart condition
        restart = (w / t_safe > safeguard) | (t < eps)

        def do_restart(_):
            r_rst = _tree_scale(-1.0, grad_fn(x_new))
            r_v = flatten_to_vec(r_rst)
            Ar_rst = matvec(r_rst)
            Ar_v = flatten_to_vec(Ar_rst)
            t_r = jnp.sqrt(jnp.dot(Ar_v, Ar_v))
            t_r_safe = t_r + eps

            P_new = jnp.zeros_like(P_flat).at[0].set(r_v / t_r_safe)
            AP_new = jnp.zeros_like(AP_flat).at[0].set(Ar_v / t_r_safe)
            valid_new = jnp.zeros_like(valid_mask).at[0].set(True)
            xrec_new = jnp.zeros_like(xrec)
            w0_r = jnp.max(jnp.abs(r_v))
            xrec_new = xrec_new.at[0].set(w0_r / t_r_safe)
            return (P_new, AP_new, xrec_new, valid_new, jnp.array(1, dtype=jnp.int32))

        def no_restart(_):
            # Determine index for new vector
            idx = jnp.where(m < mem_size, m, mem_size - 1)

            # Shift if full (roll all arrays)
            do_shift = m >= mem_size
            P_upd = jnp.where(do_shift, jnp.roll(P_flat, -1, axis=0), P_flat)
            AP_upd = jnp.where(do_shift, jnp.roll(AP_flat, -1, axis=0), AP_flat)
            xrec_upd = jnp.where(do_shift, jnp.roll(xrec, -1), xrec)
            valid_upd = jnp.where(do_shift, jnp.roll(valid_mask, -1), valid_mask)

            # Store new vector
            P_upd = P_upd.at[idx].set(p_vec / t_safe)
            AP_upd = AP_upd.at[idx].set(Ap_vec / t_safe)
            xrec_upd = xrec_upd.at[idx].set(w / t_safe)
            valid_upd = valid_upd.at[idx].set(True)

            m_new = jnp.where(m < mem_size, m + 1, m)
            return (P_upd, AP_upd, xrec_upd, valid_upd, m_new)

        P_new, AP_new, xrec_new, valid_new, m_new = jax.lax.cond(
            restart, do_restart, no_restart, None
        )

        return (x_new, P_new, AP_new, xrec_new, valid_new, m_new)

    init_carry = (x, P_flat, AP_flat, xrec, valid_mask, m)
    final_x, _, _, _, _, _ = jax.lax.fori_loop(0, maxiter, body_fn, init_carry)

    return final_x, maxiter
