"""Apply wrapper for Flax modules with method dispatch."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Sequence, Union


def apply_with_method(
    apply_fn: Callable[..., Any],
    variables: Dict[str, Any],
    *args: Any,
    method: Optional[Union[Callable, str]] = None,
    training: Optional[bool] = None,
    rngs: Optional[Dict[str, Any]] = None,
    mutable: Union[bool, Sequence[str]] = False,
    **kwargs: Any,
) -> Any:
    """Apply a Flax module with optional method dispatch.

    This wrapper enables using different forward methods for multi-term objectives,
    which is essential for PINNs where different terms may compute different outputs
    (e.g., residuals, boundary values, initial conditions).

    Args:
        apply_fn: The Flax module's apply function
        variables: Model variables dict (must contain "params")
        *args: Positional arguments to pass to the method
        method: Optional method to call. Can be:
            - None: Use default __call__ method
            - str: Name of module method (e.g., "pde_residual")
            - Callable: Custom callable(module, *args) -> output
        training: Whether in training mode. Only passed if explicitly set.
        rngs: Optional RNG keys dict for stochastic layers
        mutable: Collections to mark as mutable (e.g., ["batch_stats"])
        **kwargs: Additional keyword arguments

    Returns:
        If mutable=False: model output
        If mutable=True/list: (model_output, updates_dict)

    Example:
        >>> # Default forward (PINNs - no training flag needed)
        >>> out = apply_with_method(model.apply, variables, x)
        >>>
        >>> # Custom method for PDE residual
        >>> residual = apply_with_method(
        ...     model.apply, variables, x, method="compute_residual"
        ... )
        >>>
        >>> # CNN with BatchNorm (training flag needed)
        >>> out, updates = apply_with_method(
        ...     model.apply, variables, x,
        ...     training=True, mutable=["batch_stats"]
        ... )
    """
    # Build apply kwargs - only include training if explicitly set
    apply_kwargs = {}
    if training is not None:
        apply_kwargs["training"] = training
    apply_kwargs.update(kwargs)

    if rngs is not None:
        apply_kwargs["rngs"] = rngs

    if mutable:
        apply_kwargs["mutable"] = mutable

    # Dispatch based on method type
    if method is None:
        # Default __call__
        return apply_fn(variables, *args, **apply_kwargs)
    elif isinstance(method, str):
        # String method name - use Flax's method= argument
        return apply_fn(variables, *args, method=method, **apply_kwargs)
    elif callable(method):
        # Callable method - pass module as first arg
        # Note: Flax apply with method=callable expects the callable to receive module
        return apply_fn(variables, *args, method=method, **apply_kwargs)
    else:
        raise ValueError(f"method must be None, str, or callable, got {type(method)}")
