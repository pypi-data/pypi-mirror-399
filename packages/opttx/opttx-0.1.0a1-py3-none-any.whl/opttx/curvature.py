"""Curvature matvec builders for second-order optimization.

Provides matrix-free Hessian and Fisher/GGN vector products for CG optimization.

References:
    - Hessian: Hv = d²L/dθ² @ v via jax.jvp(jax.grad(L), (θ,), (v,))
    - Fisher (GGN): Fv = Jᵀ @ H_y @ J @ v where J = df/dθ, H_y = d²L/dy²
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

import jax
import jax.numpy as jnp

from .objective import Objective
from .apply import apply_with_method


def build_hessian_matvec(
    objective: Objective,
    apply_fn: Callable[..., Any],
    variables: Dict[str, Any],
    batch: Dict[str, Any],
    step: Any,
) -> Callable[[Any], Any]:
    """Build a Hessian-vector product function.

    The Hessian matvec computes H @ v where H = d²L/dθ² is the Hessian
    of the total loss with respect to parameters.

    Uses the identity: Hv = d/dε [∇L(θ + εv)]|_{ε=0}
    Implemented via: jax.jvp(jax.grad(loss), (params,), (v,))[1]

    Args:
        objective: The Objective containing loss terms
        apply_fn: Model apply function
        variables: Model variables dict (must contain "params")
        batch: Batch dict with keys matching term.batch_key
        step: Current training step (scalar jax.Array)

    Returns:
        A function matvec(v) -> Hv that computes Hessian-vector products,
        where v and Hv are pytrees with same structure as params.

    Example:
        >>> hessian_mv = build_hessian_matvec(objective, model.apply, variables, batch, step)
        >>> Hv = hessian_mv(v)  # v is a pytree like params
    """
    params = variables["params"]

    def loss_fn(p):
        """Compute total weighted loss."""
        vars_with_p = {**variables, "params": p}
        metrics = objective.evaluate(
            apply_fn=apply_fn,
            variables=vars_with_p,
            batch=batch,
            step=step,
        )
        return metrics["loss"]

    def matvec(v):
        """Compute H @ v via forward-over-reverse autodiff."""
        # grad_fn: params -> gradient pytree
        grad_fn = jax.grad(loss_fn)
        # jvp of gradient gives Hessian-vector product
        _, Hv = jax.jvp(grad_fn, (params,), (v,))
        return Hv

    return matvec


def build_fisher_matvec(
    objective: Objective,
    apply_fn: Callable[..., Any],
    variables: Dict[str, Any],
    batch: Dict[str, Any],
    step: Any,
) -> Callable[[Any], Any]:
    """Build a Fisher/GGN matrix-vector product function.

    The Fisher (Generalized Gauss-Newton) matvec computes F @ v where:
        F = Σ_i w_i * Σ_j J_ij^T @ H_yij @ J_ij

    For each term i with N_i samples:
        - J_ij = df_i/dθ for sample j is the per-sample Jacobian
        - H_yij = d²L_ij/dy² is the per-sample output Hessian (already includes 1/N
          from mean-reduced loss)

    The Fisher matrix is positive semi-definite by construction, making it
    suitable for CG optimization.

    Implementation (per-sample VJP, then sum):
        1. Batched JVP: Jv = jvp(forward_batch, (params,), (v,))
        2. H_y @ Jv via forward-over-reverse autodiff (H_y includes 1/N factor)
        3. Per-sample VJP: J_j^T @ (H_y @ Jv)_j via vmap
        4. Sum over samples: Σ_j result_j (sum, not mean; H_y already contains 1/N)

    Args:
        objective: The Objective containing loss terms
        apply_fn: Model apply function
        variables: Model variables dict (must contain "params")
        batch: Batch dict with keys matching term.batch_key
        step: Current training step (scalar jax.Array)

    Returns:
        A function matvec(v) -> Fv that computes Fisher-vector products,
        where v and Fv are pytrees with same structure as params.

    Example:
        >>> fisher_mv = build_fisher_matvec(objective, model.apply, variables, batch, step)
        >>> Fv = fisher_mv(v)  # v is a pytree like params
    """
    params = variables["params"]

    def matvec(v):
        """Compute F @ v via per-sample JᵀH_yJv, then sum (H_y has 1/N)."""
        total_Fv = jax.tree_util.tree_map(jnp.zeros_like, params)

        for term in objective.terms:
            term_batch = batch[term.batch_key]

            # Get loss weight
            weight = objective.loss_weights[term.name]
            if callable(weight):
                weight = weight(step)

            # Extract input data from term_batch
            # term_batch is typically (points, targets) or just points
            if isinstance(term_batch, tuple):
                points = term_batch[0]
                has_tuple_batch = True
            else:
                points = term_batch
                has_tuple_batch = False

            # Helper to dynamically slice a single sample from an array
            def dynamic_slice_single(arr, idx):
                """Slice arr[idx:idx+1] using jax.lax.dynamic_slice for traced idx."""
                if not hasattr(arr, "shape") or arr.ndim == 0:
                    return arr
                # Build start indices: [idx, 0, 0, ...]
                start_indices = [idx] + [0] * (arr.ndim - 1)
                # Build slice sizes: [1, shape[1], shape[2], ...]
                slice_sizes = [1] + list(arr.shape[1:])
                return jax.lax.dynamic_slice(arr, start_indices, slice_sizes)

            # Single-point forward function (for per-sample VJP)
            def forward_single(p, idx):
                vars_with_p = {**variables, "params": p}
                # Reconstruct single-sample batch with same structure as term_batch
                if has_tuple_batch:
                    # term_batch is (points, targets, ...) - slice each element
                    single_batch = tuple(
                        dynamic_slice_single(arr, idx) for arr in term_batch
                    )
                else:
                    # term_batch is just points
                    single_batch = dynamic_slice_single(points, idx)
                out = apply_with_method(
                    apply_fn,
                    vars_with_p,
                    single_batch,
                    method=term.method,
                )
                return out[0]  # Remove batch dimension

            # Batched forward for JVP (more efficient)
            def forward_batch(p):
                vars_with_p = {**variables, "params": p}
                return apply_with_method(
                    apply_fn,
                    vars_with_p,
                    term_batch,
                    method=term.method,
                )

            # Compute batched forward and JVP: J @ v
            y_batch, Jv_batch = jax.jvp(forward_batch, (params,), (v,))

            # Compute H_y @ Jv via autodiff
            # H_y @ Jv = d/dy [grad_y(L).T @ Jv] = JVP of gradient
            # Use the actual loss function from the term
            def loss_wrt_output(output):
                """Loss as function of model output only."""
                loss_result = term.loss_fn(output, term_batch)
                if isinstance(loss_result, tuple):
                    return loss_result[0]
                return loss_result

            # Compute H_y @ Jv via forward-over-reverse autodiff
            grad_loss_wrt_y = jax.grad(loss_wrt_output)
            _, HyJv_batch = jax.jvp(grad_loss_wrt_y, (y_batch,), (Jv_batch,))

            # Per-sample VJP, then sum
            # This is the key fix: compute VJP per sample
            batch_size = points.shape[0]

            def single_vjp(idx, hy_jv):
                """Compute J^T @ (H_y @ Jv) for a single sample."""
                _, vjp_fn = jax.vjp(lambda p: forward_single(p, idx), params)
                (grad,) = vjp_fn(hy_jv)
                return grad

            # vmap over sample indices
            indices = jnp.arange(batch_size)
            per_sample_grads = jax.vmap(single_vjp, in_axes=(0, 0))(indices, HyJv_batch)

            # Aggregate per-sample gradients via summation.
            # For mean-reduced loss L = (1/N) * Σ_i ℓ_i, the output Hessian H_y
            # already contains the 1/N factor, so summing (not averaging) the
            # per-sample VJPs yields the correct Fisher: F = (1/N) * Σ_i J_i^T H_yi J_i
            term_Fv = jax.tree_util.tree_map(
                lambda g: jnp.sum(g, axis=0),
                per_sample_grads,
            )

            # Accumulate weighted contribution
            total_Fv = jax.tree_util.tree_map(
                lambda acc, contrib: acc + weight * contrib,
                total_Fv,
                term_Fv,
            )

        return total_Fv

    return matvec


def build_damped_matvec(
    base_matvec: Callable[[Any], Any],
    damping: float,
) -> Callable[[Any], Any]:
    """Add Tikhonov damping to a matvec function.

    Returns a function that computes (A + λI) @ v where A is the
    original matrix and λ is the damping coefficient.

    Args:
        base_matvec: Original matvec function A @ v
        damping: Damping coefficient λ

    Returns:
        Damped matvec function (A + λI) @ v

    Example:
        >>> hessian_mv = build_hessian_matvec(...)
        >>> damped_mv = build_damped_matvec(hessian_mv, damping=1e-4)
        >>> result = damped_mv(v)  # (H + λI) @ v
    """

    def damped_matvec(v):
        Av = base_matvec(v)
        return jax.tree_util.tree_map(
            lambda av, vi: av + damping * vi,
            Av,
            v,
        )

    return damped_matvec
