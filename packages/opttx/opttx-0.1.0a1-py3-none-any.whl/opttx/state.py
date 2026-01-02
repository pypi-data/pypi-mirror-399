"""TrainState implementation for OptTx V2."""

from __future__ import annotations

from dataclasses import replace as dataclass_replace
from typing import Any, Callable, Dict, Optional

import jax
import jax.numpy as jnp
from flax import struct


def _normalize_step(step: Any) -> jax.Array:
    """Normalize step to a scalar integer jax.Array.

    Args:
        step: Step value (Python int or jax.Array)

    Returns:
        Normalized step as scalar integer jax.Array

    Raises:
        ValueError: If step is not scalar or not integer dtype
    """
    step_arr = jnp.asarray(step)
    if step_arr.shape != ():
        raise ValueError("step must be a scalar jax.Array")
    if not jnp.issubdtype(step_arr.dtype, jnp.integer):
        raise ValueError("step must be an integer dtype")
    return step_arr


@struct.dataclass
class TrainState:
    """Training state for OptTx.

    This is the core training state container following the TrainState protocol
    defined in DESIGN.md. It enforces strict step normalization to ensure
    JIT compatibility.

    Attributes:
        step: Training step counter (scalar integer jax.Array)
        params: Model parameters (PyTree)
        opt_state: Optimizer state (PyTree, may be None before init)
        apply_fn: Flax-style apply function
        batch_stats: Optional mutable statistics (e.g., BatchNorm)
        rngs: Optional PRNG keys dict
    """

    step: jax.Array
    params: Any
    opt_state: Any
    apply_fn: Callable[..., Any] = struct.field(pytree_node=False)
    batch_stats: Any = None
    rngs: Optional[Dict[str, jax.Array]] = None

    def __post_init__(self):
        """Normalize step after initialization."""
        object.__setattr__(self, "step", _normalize_step(self.step))

    def replace(self, **updates: Any) -> "TrainState":
        """Functional update with step normalization.

        Args:
            **updates: Fields to update

        Returns:
            New TrainState with updates applied
        """
        if "step" in updates:
            updates["step"] = _normalize_step(updates["step"])
        return dataclass_replace(self, **updates)

    @classmethod
    def create(
        cls,
        *,
        apply_fn: Callable[..., Any],
        params: Any,
        optimizer: Optional[Any] = None,
        opt_state: Any = None,
        step: Any = 0,
        batch_stats: Any = None,
        rngs: Optional[Dict[str, jax.Array]] = None,
    ) -> "TrainState":
        """Create a new TrainState with optional optimizer initialization.

        Args:
            apply_fn: Model apply function
            params: Model parameters
            optimizer: Optional optimizer (calls optimizer.init if provided)
            opt_state: Optional optimizer state (mutually exclusive with optimizer)
            step: Initial step (default 0)
            batch_stats: Optional mutable statistics
            rngs: Optional PRNG keys

        Returns:
            New TrainState instance

        Raises:
            ValueError: If both optimizer and opt_state are provided
        """
        if optimizer is not None and opt_state is not None:
            raise ValueError("Provide optimizer or opt_state, not both")

        step_arr = _normalize_step(step)
        state = cls(
            step=step_arr,
            params=params,
            opt_state=opt_state,
            apply_fn=apply_fn,
            batch_stats=batch_stats,
            rngs=rngs,
        )
        if optimizer is not None:
            state = optimizer.init(state)
        return state
