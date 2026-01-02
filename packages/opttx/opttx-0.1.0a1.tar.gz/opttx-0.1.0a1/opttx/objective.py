"""Objective evaluation for multi-term optimization."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Union

import jax.numpy as jnp

from .apply import apply_with_method
from .metrics import ensure_metrics_static_and_scalar
from .terms import TermSpec


class Objective:
    """Multi-term objective for PINNs and SciML.

    Evaluates L_total = Σ_i w_i(step) * L_i where each term can use
    different forward methods and loss functions.

    Args:
        terms: List of term specifications
        loss_weights: Optional dict mapping term names to weights (float or callable).
            Defaults to 1.0 for all terms.

    Example:
        >>> pde_term = TermSpec(
        ...     name="pde",
        ...     batch_key="pde_batch",
        ...     method="compute_residual",
        ...     loss_fn=lambda pred, batch: jnp.mean(pred**2),
        ... )
        >>> bc_term = TermSpec(
        ...     name="bc",
        ...     batch_key="bc_batch",
        ...     loss_fn=lambda pred, batch: jnp.mean((pred - batch)**2),
        ... )
        >>> objective = Objective(
        ...     terms=[pde_term, bc_term],
        ...     loss_weights={"pde": 1.0, "bc": 10.0},
        ... )
    """

    def __init__(
        self,
        terms: List[TermSpec],
        loss_weights: Optional[Dict[str, Union[float, Callable[[Any], float]]]] = None,
    ):
        self.terms = terms
        self.loss_weights = loss_weights or {}

        for term in terms:
            if term.name not in self.loss_weights:
                self.loss_weights[term.name] = 1.0

    def evaluate(
        self,
        apply_fn: Callable[..., Any],
        variables: Dict[str, Any],
        batch: Dict[str, Any],
        step: Any,
    ) -> Dict[str, Any]:
        """Evaluate objective and return metrics.

        Args:
            apply_fn: Flax module apply function
            variables: Model variables dict
            batch: Batch dict with keys matching term.batch_key
            step: Current training step (scalar jax.Array)

        Returns:
            Dict with "loss" (total weighted loss) and "loss/<term_name>" entries
        """
        metrics = {}
        total_loss = 0.0

        for term in self.terms:
            term_batch = batch[term.batch_key]

            term_out = apply_with_method(
                apply_fn,
                variables,
                term_batch,
                method=term.method,
            )

            loss_result = term.loss_fn(term_out, term_batch)

            if isinstance(loss_result, tuple):
                term_loss, term_metrics = loss_result
                metrics.update(term_metrics)
            else:
                term_loss = loss_result

            metrics[f"loss/{term.name}"] = term_loss

            weight = self.loss_weights[term.name]
            if callable(weight):
                weight = weight(step)

            total_loss = total_loss + weight * term_loss

        metrics["loss"] = total_loss

        ensure_metrics_static_and_scalar(metrics)

        return metrics

    def evaluate_state(self, state: Any, batch: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate objective from TrainState.

        Args:
            state: TrainState with apply_fn, params, step, and optional batch_stats
            batch: Batch dict

        Returns:
            Metrics dict

        Raises:
            ValueError: If multi-term objective with batch_stats
        """
        if (
            len(self.terms) > 1
            and hasattr(state, "batch_stats")
            and state.batch_stats is not None
        ):
            raise ValueError(
                "Multi-term objectives with batch_stats are not supported. "
                "This is a design constraint to avoid ambiguity in mutable collection handling."
            )

        variables = {"params": state.params}
        if hasattr(state, "batch_stats") and state.batch_stats is not None:
            variables["batch_stats"] = state.batch_stats

        return self.evaluate(
            apply_fn=state.apply_fn,
            variables=variables,
            batch=batch,
            step=state.step,
        )
