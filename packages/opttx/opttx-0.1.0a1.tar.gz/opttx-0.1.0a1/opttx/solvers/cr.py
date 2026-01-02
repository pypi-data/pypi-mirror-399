"""Conjugate Residual solver for linear systems.

JAX-compatible CR implementation using lax.while_loop for JIT compilation.
CR can handle symmetric matrices that may be indefinite (unlike CG which
requires positive definiteness).

References:
    Saad, Y. (2003). Iterative Methods for Sparse Linear Systems.
    Section 6.8: The Conjugate Residual Method.
"""

from __future__ import annotations

from typing import Any, Callable, NamedTuple, Optional, Tuple

import jax
import jax.numpy as jnp


class CRState(NamedTuple):
    """State for CR iteration."""

    x: Any  # Current solution (pytree)
    r: Any  # Residual (pytree)
    p: Any  # Search direction (pytree)
    Ar: Any  # A @ r (pytree)
    Ap: Any  # A @ p (pytree)
    rAr: jnp.ndarray  # r^T Ar (scalar)
    k: jnp.ndarray  # Iteration count


def _tree_dot(a: Any, b: Any) -> jnp.ndarray:
    """Compute dot product of two pytrees."""
    leaves_a = jax.tree_util.tree_leaves(a)
    leaves_b = jax.tree_util.tree_leaves(b)
    return sum(jnp.sum(la * lb) for la, lb in zip(leaves_a, leaves_b))


def _tree_axpy(alpha: jnp.ndarray, x: Any, y: Any) -> Any:
    """Compute alpha * x + y for pytrees."""
    return jax.tree_util.tree_map(lambda xi, yi: alpha * xi + yi, x, y)


def _tree_zeros_like(x: Any) -> Any:
    """Create pytree of zeros with same structure."""
    return jax.tree_util.tree_map(jnp.zeros_like, x)


def _get_eps(x: jnp.ndarray) -> float:
    """Get epsilon for division safety based on dtype.

    Args:
        x: Array whose dtype determines the epsilon value.

    Returns:
        Epsilon value appropriate for the dtype.
    """
    if x.dtype == jnp.float32:
        return 1e-20
    else:  # float64 or other
        return 1e-30


def cr_solve(
    matvec: Callable[[Any], Any],
    b: Any,
    x0: Optional[Any] = None,
    maxiter: int = 10,
    tol: float = 1e-5,
) -> Tuple[Any, int]:
    """Solve Ax = b using Conjugate Residual method.

    Solves the linear system Ax = b where A is a symmetric matrix.
    Unlike CG, CR does not require A to be positive definite - it can
    handle indefinite symmetric matrices.

    The algorithm uses JAX's lax.while_loop for JIT compatibility, allowing
    it to be used inside jitted training loops.

    Args:
        matvec: Function that computes A @ v for a pytree v.
            Must accept and return pytrees with same structure as b.
            The matrix A must be symmetric.
        b: Right-hand side vector (pytree).
        x0: Initial guess (pytree with same structure as b).
            Defaults to zeros if not provided.
        maxiter: Maximum number of CR iterations.
        tol: Convergence tolerance. Stops when ||Ar||^2 < tol.

    Returns:
        Tuple of (x, info) where:
            x: Solution pytree (same structure as b)
            info: Number of iterations performed

    Example:
        >>> # Solve Hx = g for indefinite Hessian
        >>> x, iters = cr_solve(hessian_mv, gradient, maxiter=10)
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

    # Compute Ar and Ap
    Ar = matvec(r)
    Ap = Ar  # Initially p = r, so Ap = Ar

    # rAr = r^T Ar
    rAr = _tree_dot(r, Ar)

    initial_state = CRState(x=x, r=r, p=p, Ar=Ar, Ap=Ap, rAr=rAr, k=jnp.array(0))

    def cond_fn(state: CRState) -> jnp.ndarray:
        """Continue while residual is large and under max iterations."""
        # Use ||Ar||^2 as convergence criterion (related to residual norm)
        ApAp = _tree_dot(state.Ap, state.Ap)
        return (ApAp > tol) & (state.k < maxiter)

    def body_fn(state: CRState) -> CRState:
        """Perform one CR iteration."""
        x, r, p, Ar, Ap, rAr, k = state

        # alpha = (r^T Ar) / (Ap^T Ap)
        ApAp = _tree_dot(Ap, Ap)
        alpha = rAr / (ApAp + _get_eps(rAr))

        # x_{k+1} = x_k + alpha * p
        x_new = _tree_axpy(alpha, p, x)

        # r_{k+1} = r_k - alpha * Ap
        r_new = _tree_axpy(-alpha, Ap, r)

        # Ar_{k+1} = A @ r_{k+1} (the only new matvec per iteration)
        Ar_new = matvec(r_new)

        # rAr_new = r_{k+1}^T Ar_{k+1}
        rAr_new = _tree_dot(r_new, Ar_new)

        # beta = rAr_new / rAr
        beta = rAr_new / (rAr + _get_eps(rAr))

        # p_{k+1} = r_{k+1} + beta * p_k
        p_new = _tree_axpy(beta, p, r_new)

        # Ap_{k+1} = Ar_{k+1} + beta * Ap_k (no matvec needed)
        Ap_new = _tree_axpy(beta, Ap, Ar_new)

        return CRState(
            x=x_new, r=r_new, p=p_new, Ar=Ar_new, Ap=Ap_new, rAr=rAr_new, k=k + 1
        )

    # Run CR iterations
    final_state = jax.lax.while_loop(cond_fn, body_fn, initial_state)

    return final_state.x, final_state.k


def cr_solve_fori(
    matvec: Callable[[Any], Any],
    b: Any,
    x0: Optional[Any] = None,
    maxiter: int = 10,
) -> Tuple[Any, int]:
    """Solve Ax = b using CR with fixed iteration count (fori_loop).

    This version uses jax.lax.fori_loop instead of while_loop, which can
    be more efficient when the number of iterations is known in advance
    or when early termination is not needed.

    Args:
        matvec: Function that computes A @ v for a pytree v.
            The matrix A must be symmetric.
        b: Right-hand side vector (pytree).
        x0: Initial guess (pytree). Defaults to zeros.
        maxiter: Exact number of CR iterations to perform.

    Returns:
        Tuple of (x, info) where:
            x: Solution pytree
            info: Number of iterations (always maxiter)

    This version always runs exactly maxiter iterations.
    Use cr_solve for early termination based on tolerance.
    """
    if x0 is None:
        x = _tree_zeros_like(b)
    else:
        x = x0

    # r = b - A @ x
    Ax = matvec(x)
    r = jax.tree_util.tree_map(lambda bi, axi: bi - axi, b, Ax)
    p = r

    # Compute Ar and Ap
    Ar = matvec(r)
    Ap = Ar

    # rAr = r^T Ar
    rAr = _tree_dot(r, Ar)

    eps = _get_eps(rAr)

    def body_fn(
        k: int, state: Tuple[Any, Any, Any, Any, Any, jnp.ndarray]
    ) -> Tuple[Any, Any, Any, Any, Any, jnp.ndarray]:
        """Perform one CR iteration."""
        x, r, p, Ar, Ap, rAr = state

        # alpha = (r^T Ar) / (Ap^T Ap)
        ApAp = _tree_dot(Ap, Ap)
        alpha = rAr / (ApAp + eps)

        # x_{k+1} = x_k + alpha * p
        x_new = _tree_axpy(alpha, p, x)

        # r_{k+1} = r_k - alpha * Ap
        r_new = _tree_axpy(-alpha, Ap, r)

        # Ar_{k+1} = A @ r_{k+1}
        Ar_new = matvec(r_new)

        # rAr_new = r_{k+1}^T Ar_{k+1}
        rAr_new = _tree_dot(r_new, Ar_new)

        # beta = rAr_new / rAr
        beta = rAr_new / (rAr + eps)

        # p_{k+1} = r_{k+1} + beta * p_k
        p_new = _tree_axpy(beta, p, r_new)

        # Ap_{k+1} = Ar_{k+1} + beta * Ap_k
        Ap_new = _tree_axpy(beta, Ap, Ar_new)

        return (x_new, r_new, p_new, Ar_new, Ap_new, rAr_new)

    final_x, _, _, _, _, _ = jax.lax.fori_loop(
        0, maxiter, body_fn, (x, r, p, Ar, Ap, rAr)
    )

    return final_x, maxiter
