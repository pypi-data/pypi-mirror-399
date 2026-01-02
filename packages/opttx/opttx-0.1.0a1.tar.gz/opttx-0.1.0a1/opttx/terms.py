"""TermSpec implementation for multi-term objectives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional, Union


@dataclass(frozen=True)
class TermSpec:
    """Specification for a single term in a multi-term objective.

    For PINNs/SciML objectives, each term represents a different component
    (e.g., PDE residual, boundary conditions, initial conditions).

    Attributes:
        name: Term identifier (used for metrics like "loss/<name>")
        batch_key: Key to extract this term's batch from the full batch dict
        loss_fn: Loss function mapping (term_output, term_batch) -> scalar or (scalar, metrics)
        method: Optional Flax module method name or callable for forward pass.
                None means use the default apply_fn.

    Example:
        >>> def pde_loss(residual, batch):
        ...     return jnp.mean(residual ** 2)
        >>>
        >>> term = TermSpec(
        ...     name="pde",
        ...     batch_key="pde_data",
        ...     method="compute_residual",  # Flax module method
        ...     loss_fn=pde_loss,
        ... )
    """

    name: str
    batch_key: str
    loss_fn: Callable[..., Any]
    method: Optional[Union[Callable, str]] = None

    def __post_init__(self):
        """Validate TermSpec fields."""
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("name must be a non-empty string")
        if not isinstance(self.batch_key, str) or not self.batch_key:
            raise ValueError("batch_key must be a non-empty string")
        if not callable(self.loss_fn):
            raise ValueError("loss_fn must be callable")
        if self.method is not None:
            if not (callable(self.method) or isinstance(self.method, str)):
                raise ValueError("method must be None, callable, or string")
