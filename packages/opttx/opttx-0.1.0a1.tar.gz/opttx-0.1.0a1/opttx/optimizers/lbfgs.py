"""L-BFGS optimizer using optax.

L-BFGS is a quasi-Newton method that approximates the inverse Hessian using
limited memory. It's well-suited for:
- Full-batch optimization (SciML, PINNs)
- Small to medium problems where full batch fits in memory
- Problems where second-order information improves convergence

References:
    Nocedal, J. (1980): Updating Quasi-Newton Matrices with Limited Storage
    Liu, D.C. & Nocedal, J. (1989): On the Limited Memory BFGS Method
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import jax
import jax.numpy as jnp
import optax

from ..objective import Objective


class LBFGSOptimizer:
    """L-BFGS optimizer using optax.lbfgs().

    This is a full-batch quasi-Newton method with automatic line search.
    Best for:
    - Small/medium problems where full batch fits in memory
    - SciML/PINNs with limited data points

    Note: L-BFGS is designed for full-batch optimization. Using mini-batches
    may lead to instability. For stochastic settings, consider SGD, Adam, or SOAP.

    Args:
        objective: The objective to optimize
        learning_rate: Optional global scaling factor. By default (None), the
            step size is determined entirely by line search. Set to a value
            to apply additional scaling after line search.
        memory_size: Number of past gradients/updates to store (default: 10)
        scale_init_precond: Scale initial preconditioner (default: True)
        max_linesearch_steps: Max line search iterations (default: 20)

    Example:
        >>> objective = Objective(terms=[pde_term, bc_term])
        >>> optimizer = LBFGSOptimizer(objective, memory_size=20)
        >>> state = optimizer.init(state, example_batch=batch)
        >>> for batch in train_data:
        ...     state, metrics = optimizer.step(state, batch)
    """

    def __init__(
        self,
        objective: Objective,
        learning_rate: Optional[float] = None,
        memory_size: int = 10,
        scale_init_precond: bool = True,
        max_linesearch_steps: int = 20,
    ):
        self.objective = objective
        self.learning_rate = learning_rate
        self.memory_size = memory_size
        self.scale_init_precond = scale_init_precond
        self.max_linesearch_steps = max_linesearch_steps

        # Create optax L-BFGS optimizer with zoom line search
        self._opt = optax.lbfgs(
            learning_rate=learning_rate,
            memory_size=memory_size,
            scale_init_precond=scale_init_precond,
            linesearch=optax.scale_by_zoom_linesearch(
                max_linesearch_steps=max_linesearch_steps,
            ),
        )

    def _build_value_fn(self, state: Any, batch: Any):
        """Build value function for line search."""

        def value_fn(params):
            variables = {"params": params}
            if hasattr(state, "batch_stats") and state.batch_stats is not None:
                variables["batch_stats"] = state.batch_stats
            metrics = self.objective.evaluate(
                apply_fn=state.apply_fn,
                variables=variables,
                batch=batch,
                step=state.step,
            )
            return metrics["loss"]

        return value_fn

    def init(
        self,
        state: Any,
        *,
        example_batch: Any = None,
        validate: bool = False,
    ) -> Any:
        """Initialize L-BFGS optimizer state.

        Args:
            state: TrainState with params
            example_batch: Optional example batch for validation
            validate: Whether to validate objective evaluation

        Returns:
            TrainState with initialized opt_state
        """
        opt_state = self._opt.init(state.params)
        return state.replace(opt_state=opt_state)

    def step(
        self,
        state: Any,
        batch: Dict[str, Any],
    ) -> Tuple[Any, Dict[str, Any]]:
        """Perform one L-BFGS optimization step.

        Args:
            state: TrainState with params, opt_state, apply_fn, step
            batch: Full batch dict (L-BFGS works best with full batch)

        Returns:
            (new_state, metrics) tuple
        """
        # Build value function for this batch
        value_fn = self._build_value_fn(state, batch)

        # Compute value and gradient
        value, grad = jax.value_and_grad(value_fn)(state.params)

        # L-BFGS update requires value, grad, and value_fn for line search
        updates, new_opt_state = self._opt.update(
            grad,
            state.opt_state,
            state.params,
            value=value,
            grad=grad,
            value_fn=value_fn,
        )

        # Apply updates
        new_params = optax.apply_updates(state.params, updates)

        # Compute metrics with new params
        variables = {"params": new_params}
        if hasattr(state, "batch_stats") and state.batch_stats is not None:
            variables["batch_stats"] = state.batch_stats

        metrics = self.objective.evaluate(
            apply_fn=state.apply_fn,
            variables=variables,
            batch=batch,
            step=state.step,
        )

        new_state = state.replace(
            step=state.step + 1,
            params=new_params,
            opt_state=new_opt_state,
        )

        return new_state, metrics
