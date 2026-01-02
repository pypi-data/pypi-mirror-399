"""Conjugate Gradient solver for linear systems.

JAX-compatible CG implementation using lax.while_loop for JIT compilation.

References:
    Shewchuk, J. R. (1994). An introduction to the conjugate gradient method
    without the agonizing pain.
"""

from __future__ import annotations

from typing import Any, Callable, NamedTuple, Optional, Tuple

import jax
import jax.numpy as jnp


class CGState(NamedTuple):
    """State for CG iteration."""

    x: Any  # Current solution (pytree)
    r: Any  # Residual (pytree)
    p: Any  # Search direction (pytree)
    rr: jnp.ndarray  # r^T r (scalar)
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


def _get_eps(x: jnp.ndarray) -> float:
    """Get epsilon for division safety based on dtype.

    This epsilon prevents division by zero in degenerate cases while being
    small enough not to affect normal CG computations on SPD matrices.

    Args:
        x: Array whose dtype determines the epsilon value.

    Returns:
        Epsilon value appropriate for the dtype.

    Note:
        x.dtype is a static attribute (not traced), so the Python if
        statement is JIT-safe and will be resolved at trace time.
    """
    if x.dtype == jnp.float32:
        return 1e-20
    else:  # float64 or other
        return 1e-30


def cg_solve(
    matvec: Callable[[Any], Any],
    b: Any,
    x0: Optional[Any] = None,
    maxiter: int = 10,
    tol: float = 1e-5,
) -> Tuple[Any, int]:
    """Solve Ax = b using Conjugate Gradient method.

    Solves the linear system Ax = b where A is a symmetric positive definite
    matrix represented by its matrix-vector product function.

    The algorithm uses JAX's lax.while_loop for JIT compatibility, allowing
    it to be used inside jitted training loops.

    Args:
        matvec: Function that computes A @ v for a pytree v.
            Must accept and return pytrees with same structure as b.
        b: Right-hand side vector (pytree).
        x0: Initial guess (pytree with same structure as b).
            Defaults to zeros if not provided.
        maxiter: Maximum number of CG iterations.
        tol: Convergence tolerance. Stops when ||r||^2 < tol.

    Returns:
        Tuple of (x, info) where:
            x: Solution pytree (same structure as b)
            info: Number of iterations performed

    Example:
        >>> # Solve (H + λI)x = g for CG optimization
        >>> damped_mv = build_damped_matvec(hessian_mv, damping=1e-4)
        >>> x, iters = cg_solve(damped_mv, gradient, maxiter=10)

    Note:
        - The matvec function must represent a symmetric positive definite matrix
        - For CG optimization, use damped matvec to ensure positive definiteness
        - The solver terminates early if residual norm drops below tol
    """
    # Initialize
    if x0 is None:
        x = _tree_zeros_like(b)
    else:
        x = x0

    # r = b - A @ x
    Ax = matvec(x)
    r = jax.tree_util.tree_map(lambda bi, axi: bi - axi, b, Ax)
    p = r
    rr = _tree_dot(r, r)

    initial_state = CGState(x=x, r=r, p=p, rr=rr, k=jnp.array(0))

    def cond_fn(state: CGState) -> jnp.ndarray:
        """Continue while residual is large and under max iterations."""
        return (state.rr > tol) & (state.k < maxiter)

    def body_fn(state: CGState) -> CGState:
        """Perform one CG iteration."""
        x, r, p, rr, k = state

        # Compute A @ p
        Ap = matvec(p)

        # alpha = r^T r / (p^T A p)
        pAp = _tree_dot(p, Ap)
        alpha = rr / (pAp + _get_eps(rr))

        # x_{k+1} = x_k + alpha * p
        x_new = _tree_axpy(alpha, p, x)

        # r_{k+1} = r_k - alpha * A p
        r_new = _tree_axpy(-alpha, Ap, r)

        # rr_new = r_{k+1}^T r_{k+1}
        rr_new = _tree_dot(r_new, r_new)

        # beta = rr_new / rr
        beta = rr_new / (rr + _get_eps(rr))

        # p_{k+1} = r_{k+1} + beta * p_k
        p_new = _tree_axpy(beta, p, r_new)

        return CGState(x=x_new, r=r_new, p=p_new, rr=rr_new, k=k + 1)

    # Run CG iterations
    final_state = jax.lax.while_loop(cond_fn, body_fn, initial_state)

    return final_state.x, final_state.k


def cg_solve_fori(
    matvec: Callable[[Any], Any],
    b: Any,
    x0: Optional[Any] = None,
    maxiter: int = 10,
) -> Tuple[Any, int]:
    """Solve Ax = b using CG with fixed iteration count (fori_loop).

    This version uses jax.lax.fori_loop instead of while_loop, which can
    be more efficient when the number of iterations is known in advance
    or when early termination is not needed.

    Args:
        matvec: Function that computes A @ v for a pytree v.
        b: Right-hand side vector (pytree).
        x0: Initial guess (pytree). Defaults to zeros.
        maxiter: Exact number of CG iterations to perform.

    Returns:
        Tuple of (x, info) where:
            x: Solution pytree
            info: Number of iterations (always maxiter)

    Note:
        - This version always runs exactly maxiter iterations
        - Use cg_solve if you want early termination based on tolerance
    """
    if x0 is None:
        x = _tree_zeros_like(b)
    else:
        x = x0

    # r = b - A @ x
    Ax = matvec(x)
    r = jax.tree_util.tree_map(lambda bi, axi: bi - axi, b, Ax)
    p = r
    rr = _tree_dot(r, r)

    eps = _get_eps(rr)

    def body_fn(
        k: int, state: Tuple[Any, Any, Any, jnp.ndarray]
    ) -> Tuple[Any, Any, Any, jnp.ndarray]:
        """Perform one CG iteration."""
        x, r, p, rr = state

        Ap = matvec(p)
        pAp = _tree_dot(p, Ap)
        alpha = rr / (pAp + eps)

        x_new = _tree_axpy(alpha, p, x)
        r_new = _tree_axpy(-alpha, Ap, r)
        rr_new = _tree_dot(r_new, r_new)
        beta = rr_new / (rr + eps)
        p_new = _tree_axpy(beta, p, r_new)

        return (x_new, r_new, p_new, rr_new)

    final_x, _, _, _ = jax.lax.fori_loop(0, maxiter, body_fn, (x, r, p, rr))

    return final_x, maxiter
