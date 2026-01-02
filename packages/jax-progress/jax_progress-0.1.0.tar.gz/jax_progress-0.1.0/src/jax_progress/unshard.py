"""Utility functions for JAX shard_map operations.

This module provides helper functions for working with sharded computations
in JAX. All functions require execution within a jax.shard_map context and
use collective operations to coordinate across devices.

Functions:
    - unshard_size: Count total devices across axes
    - unshard_min: Global minimum reduction
    - unshard_max: Global maximum reduction
    - unshard_iota: Unique device index assignment
"""

from math import prod

import jax.numpy as jnp
from jax import lax


def unshard_size(spec):
    """Compute the total number of devices across specified sharding axes.

    This function calculates the product of device counts across all named axes
    in the partition spec. Only works inside jax.shard_map context.

    Args:
        spec: PartitionSpec defining which mesh axes to count across.
              Use P('x', 'y') to count devices across x and y axes.

    Returns:
        int: Product of axis sizes. Returns 1 for empty spec P().

    Example:
        >>> # Inside shard_map with mesh shape (2, 4) and axes ('x', 'y')
        >>> @jax.shard_map(mesh=mesh, in_specs=P('x', 'y'), out_specs=P())
        >>> def fn(x):
        >>>     return unshard_size(P('x', 'y'))  # Returns 8
    """
    return prod([lax.axis_size(axis_name=axis) for axis in spec if axis is not None])


def unshard_min(x, spec):
    """Compute the global minimum value across sharded devices.

    Reduces a sharded value to its minimum across specified mesh axes using
    collective operations (lax.pmin). Only works inside jax.shard_map context.

    Args:
        x: Value to reduce. Each device shard contains a local value.
        spec: PartitionSpec defining which axes to reduce across.

    Returns:
        Scalar: Global minimum value across all specified axes.

    Example:
        >>> # Inside shard_map with mesh (2, 2) and axes ('x', 'y')
        >>> @jax.shard_map(mesh=mesh, in_specs=P('x', 'y'), out_specs=P())
        >>> def fn(x):
        >>>     return unshard_min(x, P('x', 'y'))  # Global min
    """
    # We compute the global min by reducing across all axes in the spec
    for axis in spec:
        if axis is not None:
            x = lax.pmin(x, axis_name=axis)
    return jnp.min(x)


def unshard_max(x, spec):
    """Compute the global maximum value across sharded devices.

    Reduces a sharded value to its maximum across specified mesh axes using
    collective operations (lax.pmax). Only works inside jax.shard_map context.

    Args:
        x: Value to reduce. Each device shard contains a local value.
        spec: PartitionSpec defining which axes to reduce across.

    Returns:
        Scalar: Global maximum value across all specified axes.

    Example:
        >>> # Inside shard_map with mesh (2, 2) and axes ('x', 'y')
        >>> @jax.shard_map(mesh=mesh, in_specs=P('x', 'y'), out_specs=P())
        >>> def fn(x):
        >>>     return unshard_max(x, P('x', 'y'))  # Global max
    """
    # We compute the global max by reducing across all axes in the spec
    for axis in spec:
        if axis is not None:
            x = lax.pmax(x, axis_name=axis)
    return jnp.max(x)


def unshard_iota(spec):
    """Compute a unique device index based on mesh position.

    Returns a unique integer index for each device based on its position in the
    mesh along the specified axes. Uses row-major ordering where the first axis
    varies slowest. Only works inside jax.shard_map context.

    Args:
        spec: PartitionSpec defining which axes contribute to the index.
              The index is computed as a flattened position in row-major order.

    Returns:
        int: Unique device index in range [0, prod(axis_sizes)).
             Returns 0 for empty spec P().

    Example:
        >>> # Inside shard_map with mesh (2, 4) and axes ('x', 'y')
        >>> # Device at position (x=0, y=0) gets index 0
        >>> # Device at position (x=0, y=3) gets index 3
        >>> # Device at position (x=1, y=0) gets index 4
        >>> @jax.shard_map(mesh=mesh, in_specs=P('x', 'y'), out_specs=P('x', 'y'))
        >>> def fn(x):
        >>>     idx = unshard_iota(P('x', 'y'))
        >>>     return x + idx  # Each shard gets different offset

    Note:
        Uses row-major (C-style) ordering: index = x * size_y + y
    """
    # We accumulate the index: idx = idx * size + current_coord
    indx = 0
    for axis in spec:
        if axis is not None:
            # Shift previous indices up by the size of the current dimension
            indx *= lax.axis_size(axis_name=axis)
            # Add the current coordinate
            indx += lax.axis_index(axis_name=axis)
    return indx
