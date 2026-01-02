"""NLTGCR optimizer for second-order optimization.

NLTGCR (Nonlinear Truncated GCR) optimizer uses curvature information
(Hessian or Fisher/GGN) combined with orthogonalized search directions
to accelerate optimization.

References:
    https://arxiv.org/abs/2306.00325
"""

from __future__ import annotations

from typing import Any, Dict, Literal, Tuple

import jax
import jax.numpy as jnp

from ..objective import Objective
from ..curvature import build_damped_matvec, build_fisher_matvec, build_hessian_matvec
from ..solvers.nltgcr import nltgcr_solve_fori


class NLTGCROptimizer:
    """NLTGCR optimizer using second-order curvature information.

    NLTGCR (Nonlinear Truncated GCR) combines search directions orthogonalized
    against curvature-mapped vectors to accelerate optimization. Unlike CG which
    solves a linear system once per step, NLTGCR runs multiple internal iterations.

    Args:
        objective: The objective to optimize
        learning_rate: Step size for internal NLTGCR updates (default: 0.01)
            Note: This is applied at EACH internal iteration, so use smaller
            values than you would for CG's learning_rate.
        damping: Damping coefficient for curvature (default: 1e-3)
        nltgcr_iters: Number of NLTGCR iterations per optimizer step (default: 5)
        mem_size: Memory size for stored vectors (default: 5)
        curvature_type: Type of curvature matrix, "fisher" or "hessian"
            (default: "fisher")
        safeguard: Threshold for automatic restart (default: 1e3)

    Example:
        >>> objective = Objective(terms=[pde_term, bc_term])
        >>> optimizer = NLTGCROptimizer(objective, learning_rate=0.01, nltgcr_iters=5)
        >>> state = optimizer.init(state)
        >>> for batch in train_data:
        ...     state, metrics = optimizer.step(state, batch)

    Note:
        - NLTGCR runs multiple internal iterations per step (unlike CG)
        - learning_rate is applied at each internal iteration
        - Uses Fisher/GGN by default for stability
    """

    def __init__(
        self,
        objective: Objective,
        learning_rate: float = 0.01,
        damping: float = 1e-3,
        nltgcr_iters: int = 5,
        mem_size: int = 5,
        curvature_type: Literal["fisher", "hessian"] = "fisher",
        safeguard: float = 1e3,
    ):
        self.objective = objective
        self.learning_rate = learning_rate
        self.damping = damping
        self.nltgcr_iters = nltgcr_iters
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
        """Initialize NLTGCR optimizer state.

        Args:
            state: TrainState with params
            example_batch: Optional example batch for validation
            validate: Whether to validate objective evaluation

        Returns:
            TrainState with initialized opt_state
        """
        # NLTGCR state tracking - minimal for now
        # The solver handles internal P, AP storage
        opt_state = {
            "total_nltgcr_iters": jnp.array(0, dtype=jnp.int32),
        }
        return state.replace(opt_state=opt_state)

    def step(
        self,
        state: Any,
        batch: Dict[str, Any],
    ) -> Tuple[Any, Dict[str, Any]]:
        """Perform one NLTGCR optimization step.

        Each step runs nltgcr_iters internal NLTGCR iterations:
        1. Compute gradient g = grad(L(params))
        2. Build curvature matvec Hv
        3. Run NLTGCR iterations to update params
        4. Return updated state and metrics

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

        # Build curvature matvec
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

        # Run NLTGCR: returns updated params directly
        new_params, nltgcr_iters = nltgcr_solve_fori(
            matvec=damped_matvec,
            grad_fn=grad_fn,
            x0=state.params,
            maxiter=self.nltgcr_iters,
            mem_size=self.mem_size,
            learning_rate=self.learning_rate,
            safeguard=self.safeguard,
        )

        # Update optimizer state
        new_opt_state = {
            "total_nltgcr_iters": state.opt_state["total_nltgcr_iters"] + nltgcr_iters,
        }

        # Add NLTGCR diagnostics to metrics
        metrics = {**metrics, "nltgcr_iters": nltgcr_iters}

        # Create new training state
        new_state = state.replace(
            step=state.step + 1,
            params=new_params,
            opt_state=new_opt_state,
        )

        return new_state, metrics
