"""TGS optimizer for accelerated gradient descent.

TGS (Truncated Gram-Schmidt) optimizer uses Anderson Acceleration with
Gram-Schmidt orthogonalization to accelerate gradient descent. Unlike
NLTGCR, TGS does not require curvature (Hessian/Fisher) computation.

References:
    https://arxiv.org/abs/2306.00325
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

import jax
import jax.numpy as jnp

from ..objective import Objective
from ..solvers.tgs import tgs_solve_fori


class TGSOptimizer:
    """TGS optimizer using Anderson Acceleration with Gram-Schmidt orthogonalization.

    TGS (Truncated Gram-Schmidt) accelerates gradient descent by using stored
    differences to extrapolate better solutions. Unlike NLTGCR or CG, TGS does
    NOT require curvature (Hessian/Fisher) computation, making it cheaper per step.

    Args:
        objective: The objective to optimize
        learning_rate: Step size for TGS updates (default: 0.1)
            This is applied at each internal iteration within TGS.
        tgs_iters: Number of TGS iterations per optimizer step (default: 5)
        mem_size: Memory size for stored differences (default: 5)
        safeguard: Threshold for automatic restart (default: 1e3)
        reversed: If True, use Reversed TGS (RTGS) which transfers information
            from the about-to-be-discarded oldest vector into the basis before
            removal. This can improve convergence in some cases. (default: False)

    Example:
        >>> objective = Objective(terms=[pde_term, bc_term])
        >>> optimizer = TGSOptimizer(objective, learning_rate=0.1, tgs_iters=5)
        >>> state = optimizer.init(state)
        >>> for batch in train_data:
        ...     state, metrics = optimizer.step(state, batch)

    Note:
        - TGS is a first-order method (no curvature needed)
        - It accelerates gradient descent via Anderson Acceleration
        - Memory cost is O(mem_size * n_params)
    """

    def __init__(
        self,
        objective: Objective,
        learning_rate: float = 0.1,
        tgs_iters: int = 5,
        mem_size: int = 5,
        safeguard: float = 1e3,
        reversed: bool = False,
    ):
        self.objective = objective
        self.learning_rate = learning_rate
        self.tgs_iters = tgs_iters
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
        """Initialize TGS optimizer state.

        Args:
            state: TrainState with params
            example_batch: Optional example batch for validation
            validate: Whether to validate objective evaluation

        Returns:
            TrainState with initialized opt_state
        """
        # TGS state tracking - minimal for now
        # The solver handles internal DX, DF storage
        opt_state = {
            "total_tgs_iters": jnp.array(0, dtype=jnp.int32),
        }
        return state.replace(opt_state=opt_state)

    def step(
        self,
        state: Any,
        batch: Dict[str, Any],
    ) -> Tuple[Any, Dict[str, Any]]:
        """Perform one TGS optimization step.

        Each step runs tgs_iters internal TGS iterations:
        1. Define grad_fn for current batch
        2. Run TGS iterations to update params
        3. Return updated state and metrics

        Args:
            state: TrainState with params, opt_state, apply_fn, step
            batch: Batch dict with keys matching term.batch_key

        Returns:
            (new_state, metrics) tuple where metrics includes:
                - loss: total loss
                - loss/<term_name>: per-term losses
                - tgs_iters: number of TGS iterations this step
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

        # Define grad_fn for TGS
        def grad_fn(params):
            return jax.grad(
                lambda p: self.objective.evaluate(
                    apply_fn=state.apply_fn,
                    variables={**variables, "params": p},
                    batch=batch,
                    step=state.step,
                )["loss"]
            )(params)

        # Run TGS: returns updated params directly
        new_params, tgs_iters = tgs_solve_fori(
            grad_fn=grad_fn,
            x0=state.params,
            maxiter=self.tgs_iters,
            mem_size=self.mem_size,
            learning_rate=self.learning_rate,
            safeguard=self.safeguard,
            reversed=self.reversed,
        )

        # Update optimizer state
        new_opt_state = {
            "total_tgs_iters": state.opt_state["total_tgs_iters"] + tgs_iters,
        }

        # Add TGS diagnostics to metrics
        metrics = {**metrics, "tgs_iters": tgs_iters}

        # Create new training state
        new_state = state.replace(
            step=state.step + 1,
            params=new_params,
            opt_state=new_opt_state,
        )

        return new_state, metrics
