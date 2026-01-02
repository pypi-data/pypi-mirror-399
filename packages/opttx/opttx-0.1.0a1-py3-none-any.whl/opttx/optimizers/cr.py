"""Conjugate Residual optimizer for second-order optimization.

CR optimizer uses curvature information (typically Hessian) to compute
natural gradient updates by solving (H + λI)p = g via Conjugate Residual.
Unlike CG, CR can handle indefinite symmetric matrices.

References:
    - Saad, Y. (2003). Iterative Methods for Sparse Linear Systems.
    - Martens, J. (2010). Deep learning via Hessian-free optimization.
"""

from __future__ import annotations

from typing import Any, Dict, Literal, Tuple

import jax
import jax.numpy as jnp

from ..objective import Objective
from ..curvature import build_hessian_matvec, build_fisher_matvec, build_damped_matvec
from ..solvers.cr import cr_solve


class CROptimizer:
    """Conjugate Residual optimizer using second-order curvature information.

    Computes natural gradient updates by solving the linear system:
        (H + λI) p = g
    where H is either the Hessian or Fisher/GGN matrix, λ is damping,
    g is the gradient, and p is the update direction.

    The update is then: θ_new = θ - lr * p

    Unlike CGOptimizer, CROptimizer uses the Conjugate Residual method which
    can handle indefinite symmetric matrices. This makes it suitable for
    non-convex problems where the Hessian may have negative eigenvalues.

    Args:
        objective: The objective to optimize
        learning_rate: Learning rate (default: 1.0)
        damping: Damping coefficient λ for (H + λI) (default: 1e-3)
        cr_iters: Maximum CR iterations (default: 10)
        cr_tol: CR convergence tolerance (default: 1e-5)
        curvature_type: Type of curvature matrix, "fisher" or "hessian"
            (default: "hessian" - CR is designed for indefinite Hessian)

    Example:
        >>> objective = Objective(terms=[pde_term, bc_term])
        >>> optimizer = CROptimizer(objective, learning_rate=1.0, damping=1e-3)
        >>> state = optimizer.init(state)
        >>> for batch in train_data:
        ...     state, metrics = optimizer.step(state, batch)

    CR can handle indefinite Hessian matrices. For PSD matrices (like
    Fisher/GGN), CG may be more efficient.
    """

    def __init__(
        self,
        objective: Objective,
        learning_rate: float = 1.0,
        damping: float = 1e-3,
        cr_iters: int = 10,
        cr_tol: float = 1e-5,
        curvature_type: Literal["fisher", "hessian"] = "hessian",
    ):
        self.objective = objective
        self.learning_rate = learning_rate
        self.damping = damping
        self.cr_iters = cr_iters
        self.cr_tol = cr_tol
        self.curvature_type = curvature_type

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
        """Initialize CR optimizer state.

        CR optimizer has minimal state - just tracks CR iterations.

        Args:
            state: TrainState with params
            example_batch: Optional example batch for validation
            validate: Whether to validate objective evaluation

        Returns:
            TrainState with initialized opt_state
        """
        # CR optimizer tracks cumulative CR iterations for diagnostics
        opt_state = {
            "total_cr_iters": jnp.array(0, dtype=jnp.int32),
        }
        return state.replace(opt_state=opt_state)

    def step(
        self,
        state: Any,
        batch: Dict[str, Any],
    ) -> Tuple[Any, Dict[str, Any]]:
        """Perform one CR optimization step.

        1. Compute gradient g = ∇L(θ)
        2. Build curvature matvec Hv
        3. Solve (H + λI)p = g via CR
        4. Update θ_new = θ - lr * p

        Args:
            state: TrainState with params, opt_state, apply_fn, step
            batch: Batch dict with keys matching term.batch_key

        Returns:
            (new_state, metrics) tuple where metrics includes:
                - loss: total loss
                - loss/<term_name>: per-term losses
                - cr_iters: number of CR iterations this step
        """
        # Build variables dict
        variables = {"params": state.params}
        if hasattr(state, "batch_stats") and state.batch_stats is not None:
            variables["batch_stats"] = state.batch_stats

        # Define loss function for gradient computation
        def loss_fn(params):
            vars_with_p = {**variables, "params": params}
            metrics = self.objective.evaluate(
                apply_fn=state.apply_fn,
                variables=vars_with_p,
                batch=batch,
                step=state.step,
            )
            return metrics["loss"], metrics

        # Compute gradients
        (loss, metrics), grads = jax.value_and_grad(loss_fn, has_aux=True)(state.params)

        # Build curvature matvec
        if self.curvature_type == "fisher":
            base_matvec = build_fisher_matvec(
                self.objective, state.apply_fn, variables, batch, state.step
            )
        else:  # hessian
            base_matvec = build_hessian_matvec(
                self.objective, state.apply_fn, variables, batch, state.step
            )

        # Add damping: (H + λI)v
        damped_matvec = build_damped_matvec(base_matvec, self.damping)

        # Solve (H + λI)p = g via CR
        update_direction, cr_iters = cr_solve(
            matvec=damped_matvec,
            b=grads,
            x0=None,  # Start from zeros
            maxiter=self.cr_iters,
            tol=self.cr_tol,
        )

        # Update parameters: θ_new = θ - lr * p
        new_params = jax.tree_util.tree_map(
            lambda p, d: p - self.learning_rate * d,
            state.params,
            update_direction,
        )

        # Update optimizer state
        new_opt_state = {
            "total_cr_iters": state.opt_state["total_cr_iters"] + cr_iters,
        }

        # Add CR diagnostics to metrics
        metrics = {**metrics, "cr_iters": cr_iters}

        # Create new training state
        new_state = state.replace(
            step=state.step + 1,
            params=new_params,
            opt_state=new_opt_state,
        )

        return new_state, metrics
