"""Custom SGD optimizer implementation."""

from __future__ import annotations

from typing import Any, Dict, Tuple

import jax
import jax.numpy as jnp

from ..objective import Objective


class SGD:
    """Stochastic Gradient Descent optimizer with momentum and Nesterov support.

    Implements SGD with optional momentum and Nesterov accelerated gradient.
    When momentum=0, this is vanilla SGD. The velocity state is always
    initialized for consistency.

    Args:
        objective: The objective to optimize
        learning_rate: Learning rate (default: 1e-2)
        momentum: Momentum coefficient (default: 0.0)
        nesterov: Whether to use Nesterov accelerated gradient (default: False)

    Example:
        >>> objective = Objective(terms=[pde_term, bc_term])
        >>> # Vanilla SGD
        >>> optimizer = SGD(objective, learning_rate=1e-2)
        >>> # SGD with momentum
        >>> optimizer = SGD(objective, learning_rate=1e-2, momentum=0.9)
        >>> # SGD with Nesterov momentum
        >>> optimizer = SGD(objective, learning_rate=1e-2, momentum=0.9, nesterov=True)

    References:
        Polyak (1964): Some methods of speeding up the convergence of iteration methods
        Nesterov (1983): A method for unconstrained convex minimization problem with the
            rate of convergence O(1/k^2)
    """

    def __init__(
        self,
        objective: Objective,
        learning_rate: float = 1e-2,
        momentum: float = 0.0,
        nesterov: bool = False,
    ):
        self.objective = objective
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.nesterov = nesterov

    def init(
        self,
        state: Any,
        *,
        example_batch: Any = None,
        validate: bool = False,
    ) -> Any:
        """Initialize SGD optimizer state.

        Args:
            state: TrainState with params
            example_batch: Optional example batch for validation
            validate: Whether to validate objective evaluation

        Returns:
            TrainState with initialized opt_state containing:
                - velocity: Momentum accumulator (always initialized, even for momentum=0)
        """
        # Always initialize velocity for consistency
        velocity = jax.tree_util.tree_map(lambda p: jnp.zeros_like(p), state.params)

        opt_state = {"velocity": velocity}
        return state.replace(opt_state=opt_state)

    def step(
        self,
        state: Any,
        batch: Dict[str, Any],
    ) -> Tuple[Any, Dict[str, Any]]:
        """Perform one SGD optimization step.

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

        # Compute gradients
        (loss, metrics), grads = jax.value_and_grad(loss_fn, has_aux=True)(state.params)

        # Extract velocity from optimizer state
        velocity = state.opt_state["velocity"]

        # Compute update direction based on momentum setting
        if self.momentum == 0:
            # Vanilla SGD: direction = gradients
            direction = grads
            new_velocity = velocity  # Keep zeros for consistency
        else:
            # Update velocity: v_new = momentum * v + grads
            new_velocity = jax.tree_util.tree_map(
                lambda v, g: self.momentum * v + g,
                velocity,
                grads,
            )

            if self.nesterov:
                # Nesterov: direction = momentum * v_new + grads
                direction = jax.tree_util.tree_map(
                    lambda v, g: self.momentum * v + g,
                    new_velocity,
                    grads,
                )
            else:
                # Classical momentum: direction = v_new
                direction = new_velocity

        # Update parameters
        new_params = jax.tree_util.tree_map(
            lambda p, d: p - self.learning_rate * d,
            state.params,
            direction,
        )

        # Update optimizer state
        new_opt_state = {"velocity": new_velocity}

        # Create new training state
        new_state = state.replace(
            step=state.step + 1,
            params=new_params,
            opt_state=new_opt_state,
        )

        return new_state, metrics
