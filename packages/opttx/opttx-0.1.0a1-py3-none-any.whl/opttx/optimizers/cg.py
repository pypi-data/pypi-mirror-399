"""Conjugate Gradient optimizer for second-order optimization.

CG optimizer uses curvature information (Hessian or Fisher/GGN) to compute
natural gradient updates by solving (H + λI)p = g via Conjugate Gradient.

References:
    - Martens, J. (2010). Deep learning via Hessian-free optimization.
    - Martens & Grosse (2015). Optimizing Neural Networks with Kronecker-factored
      Approximate Curvature.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Literal, Tuple

import jax
import jax.numpy as jnp

from ..objective import Objective
from ..curvature import build_hessian_matvec, build_fisher_matvec, build_damped_matvec
from ..solvers.cg import cg_solve


class CGOptimizer:
    """Conjugate Gradient optimizer using second-order curvature information.

    Computes natural gradient updates by solving the linear system:
        (H + λI) p = g
    where H is either the Hessian or Fisher/GGN matrix, λ is damping,
    g is the gradient, and p is the update direction.

    The update is then: θ_new = θ - lr * p

    Args:
        objective: The objective to optimize
        learning_rate: Learning rate (default: 1.0)
        damping: Damping coefficient λ for (H + λI) (default: 1e-3)
        cg_iters: Maximum CG iterations (default: 10)
        cg_tol: CG convergence tolerance (default: 1e-5)
        curvature_type: Type of curvature matrix, "fisher" or "hessian"
            (default: "fisher")

    Example:
        >>> objective = Objective(terms=[pde_term, bc_term])
        >>> optimizer = CGOptimizer(objective, learning_rate=1.0, damping=1e-3)
        >>> state = optimizer.init(state)
        >>> for batch in train_data:
        ...     state, metrics = optimizer.step(state, batch)

    Note:
        - Fisher (GGN) is positive semi-definite, making CG stable
        - Hessian may be indefinite for non-convex problems; use larger damping
        - For PINNs, Fisher often works better than exact Hessian
    """

    def __init__(
        self,
        objective: Objective,
        learning_rate: float = 1.0,
        damping: float = 1e-3,
        cg_iters: int = 10,
        cg_tol: float = 1e-5,
        curvature_type: Literal["fisher", "hessian"] = "fisher",
    ):
        self.objective = objective
        self.learning_rate = learning_rate
        self.damping = damping
        self.cg_iters = cg_iters
        self.cg_tol = cg_tol
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
        """Initialize CG optimizer state.

        CG optimizer has minimal state - just tracks CG iterations.

        Args:
            state: TrainState with params
            example_batch: Optional example batch for validation
            validate: Whether to validate objective evaluation

        Returns:
            TrainState with initialized opt_state
        """
        # CG optimizer tracks cumulative CG iterations for diagnostics
        opt_state = {
            "total_cg_iters": jnp.array(0, dtype=jnp.int32),
        }
        return state.replace(opt_state=opt_state)

    def step(
        self,
        state: Any,
        batch: Dict[str, Any],
    ) -> Tuple[Any, Dict[str, Any]]:
        """Perform one CG optimization step.

        1. Compute gradient g = ∇L(θ)
        2. Build curvature matvec Hv
        3. Solve (H + λI)p = g via CG
        4. Update θ_new = θ - lr * p

        Args:
            state: TrainState with params, opt_state, apply_fn, step
            batch: Batch dict with keys matching term.batch_key

        Returns:
            (new_state, metrics) tuple where metrics includes:
                - loss: total loss
                - loss/<term_name>: per-term losses
                - cg_iters: number of CG iterations this step
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

        # Solve (H + λI)p = g via CG
        # Note: grads is the negative gradient direction, but we want to minimize
        # so we solve (H + λI)p = g and then update θ_new = θ - lr * p
        update_direction, cg_iters = cg_solve(
            matvec=damped_matvec,
            b=grads,
            x0=None,  # Start from zeros
            maxiter=self.cg_iters,
            tol=self.cg_tol,
        )

        # Update parameters: θ_new = θ - lr * p
        new_params = jax.tree_util.tree_map(
            lambda p, d: p - self.learning_rate * d,
            state.params,
            update_direction,
        )

        # Update optimizer state
        new_opt_state = {
            "total_cg_iters": state.opt_state["total_cg_iters"] + cg_iters,
        }

        # Add CG diagnostics to metrics
        metrics = {**metrics, "cg_iters": cg_iters}

        # Create new training state
        new_state = state.replace(
            step=state.step + 1,
            params=new_params,
            opt_state=new_opt_state,
        )

        return new_state, metrics
