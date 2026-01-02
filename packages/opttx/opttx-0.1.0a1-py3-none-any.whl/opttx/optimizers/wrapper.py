"""Optax optimizer wrapper for OptTx."""

from __future__ import annotations

from typing import Any, Dict, Tuple

import jax
import optax

from ..objective import Objective


class OptaxOptimizer:
    """Wrapper for optax optimizers.

    Wraps any optax GradientTransformation (Adam, AdamW, SGD, etc.) to work with
    OptTx's Objective and TrainState. This serves as a baseline for comparison
    with custom optimizer implementations.

    Args:
        objective: The objective to optimize
        optax_optimizer: An optax GradientTransformation (e.g., optax.adam(1e-3))

    Example:
        >>> objective = Objective(terms=[pde_term, bc_term])
        >>> optimizer = OptaxOptimizer(
        ...     objective=objective,
        ...     optax_optimizer=optax.adam(learning_rate=1e-3),
        ... )
        >>> state = optimizer.init(state, example_batch=batch)
        >>> for batch in train_data:
        ...     state, metrics = optimizer.step(state, batch)
    """

    def __init__(
        self,
        objective: Objective,
        optax_optimizer: optax.GradientTransformation,
    ):
        self.objective = objective
        self.optax_optimizer = optax_optimizer

    def init(
        self,
        state: Any,
        *,
        example_batch: Any = None,
        validate: bool = False,
    ) -> Any:
        """Initialize optimizer state.

        Args:
            state: TrainState with params
            example_batch: Optional example batch for validation
            validate: Whether to validate objective evaluation

        Returns:
            TrainState with initialized opt_state
        """
        opt_state = self.optax_optimizer.init(state.params)
        return state.replace(opt_state=opt_state)

    def step(
        self,
        state: Any,
        batch: Dict[str, Any],
    ) -> Tuple[Any, Dict[str, Any]]:
        """Perform one optimization step.

        Args:
            state: TrainState with params, opt_state, apply_fn, step
            batch: Batch dict

        Returns:
            (new_state, metrics) tuple where metrics includes loss and term losses
        """

        def loss_fn(params):
            variables = {"params": params}
            if hasattr(state, "batch_stats") and state.batch_stats is not None:
                variables["batch_stats"] = state.batch_stats

            metrics = self.objective.evaluate(
                apply_fn=state.apply_fn,
                variables=variables,
                batch=batch,
                step=state.step,
            )
            return metrics["loss"], metrics

        (loss, metrics), grads = jax.value_and_grad(loss_fn, has_aux=True)(state.params)

        updates, new_opt_state = self.optax_optimizer.update(
            grads, state.opt_state, state.params
        )
        new_params = optax.apply_updates(state.params, updates)

        new_state = state.replace(
            step=state.step + 1,
            params=new_params,
            opt_state=new_opt_state,
        )

        return new_state, metrics
