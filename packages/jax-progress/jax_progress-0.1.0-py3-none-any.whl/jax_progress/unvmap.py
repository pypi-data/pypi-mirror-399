from functools import partial

import jax
import jax.numpy as jnp
from jax import lax
from jax._src.dtypes import float0
from jax.custom_batching import custom_vmap


@jax.custom_jvp
@custom_vmap
def unvmap_size(x):
    """Get the size of the current vmap axis.

    Returns 1 when called outside of a vmap context, and returns the axis_size
    when called inside a vmap context. Useful for detecting whether code is
    running in a vmapped context and for getting the batch size.

    This function is differentiable with zero derivatives.

    Args:
        x: Any JAX array (the value is not used, only to provide context)

    Returns:
        int32 scalar: 1 outside vmap, axis_size inside vmap

    Examples:
        >>> unvmap_size(jnp.array(0.))  # Outside vmap
        Array(1, dtype=int32)
        >>> jax.vmap(lambda x: unvmap_size(x))(jnp.arange(10.))  # Inside vmap
        Array([10, 10, 10, 10, 10, 10, 10, 10, 10, 10], dtype=int32)
    """
    return jnp.array(1, dtype=jnp.int32)


@unvmap_size.def_vmap
def _unvmap_size_vmap_rule(axis_size, in_batched, x):
    out_batched = False
    return jnp.array(axis_size, dtype=jnp.int32), out_batched


@unvmap_size.defjvp
def _unvmap_size_jvp(primals, tangents):
    (x,) = primals
    y = unvmap_size(x)
    return y, jnp.zeros((), dtype=float0)


@partial(jax.jit, static_argnames=["nb"])
def unvmap_min(x, nb=1):
    """Get the top-nb minimum values from a vmapped array.

    Outside of vmap, returns [full(nb, x), zeros(nb)] where x is repeated nb times.
    Inside vmap, uses lax.approx_min_k to find the nb smallest values across the
    vmapped axis and returns them along with their indices.

    This function is differentiable with zero derivatives.

    Args:
        x: Scalar value (outside vmap) or batched array (inside vmap)
        nb: Number of minimum values to return (default: 1)

    Returns:
        tuple: [values, indices] where:
            - values: float array of shape (nb,) containing the nb minimum values
            - indices: int32 array of shape (nb,) containing the indices of those values

    Examples:
        >>> unvmap_min(jnp.array(5.0), nb=3)  # Outside vmap
        [Array([5., 5., 5.], dtype=float32), Array([0, 0, 0], dtype=int32)]
        >>> jax.vmap(lambda x: unvmap_min(x, nb=3))(jnp.arange(10.))  # Inside vmap
        # Returns the 3 smallest values (0, 1, 2) and their indices for each element
    """

    @jax.custom_jvp
    @custom_vmap
    def _unvmap_min_impl(x):
        if not jnp.isscalar(x):
            raise ValueError("Input must be a scalar.")
        return [jnp.full(nb, x), jnp.zeros(nb, dtype=jnp.int32)]

    @_unvmap_min_impl.def_vmap
    def _unvmap_min_vmap_rule(axis_size, in_batched, x):
        assert in_batched[0]
        assert x.shape[0] == axis_size
        out_batched = False
        return lax.approx_min_k(x, k=nb), [out_batched, out_batched]

    @_unvmap_min_impl.defjvp
    def _jvp(primals, tangents):
        (x,) = primals
        y = _unvmap_min_impl(x)
        return y, [jnp.zeros_like(y[0]), jnp.zeros((nb,), dtype=float0)]

    return _unvmap_min_impl(x)


@partial(jax.jit, static_argnames=["nb"])
def unvmap_max(x, nb=1):
    """Get the top-nb maximum values from a vmapped array.

    Outside of vmap, returns [full(nb, x), zeros(nb)] where x is repeated nb times.
    Inside vmap, uses lax.approx_max_k to find the nb largest values across the
    vmapped axis and returns them along with their indices.

    This function is differentiable with zero derivatives.

    Args:
        x: Scalar value (outside vmap) or batched array (inside vmap)
        nb: Number of maximum values to return (default: 1)

    Returns:
        tuple: [values, indices] where:
            - values: float array of shape (nb,) containing the nb maximum values
            - indices: int32 array of shape (nb,) containing the indices of those values

    Examples:
        >>> unvmap_max(jnp.array(5.0), nb=3)  # Outside vmap
        [Array([5., 5., 5.], dtype=float32), Array([0, 0, 0], dtype=int32)]
        >>> jax.vmap(lambda x: unvmap_max(x, nb=3))(jnp.arange(10.))  # Inside vmap
        # Returns the 3 largest values (9, 8, 7) and their indices for each element
    """

    @jax.custom_jvp
    @custom_vmap
    def _unvmap_max_impl(x):
        if not jnp.isscalar(x):
            raise ValueError("Input must be a scalar.")
        return [jnp.full(nb, x), jnp.zeros(nb, dtype=jnp.int32)]

    @_unvmap_max_impl.def_vmap
    def _unvmap_max_vmap_rule(axis_size, in_batched, x):
        assert in_batched[0]
        assert x.shape[0] == axis_size
        out_batched = False
        return lax.approx_max_k(x, k=nb), [out_batched, out_batched]

    @_unvmap_max_impl.defjvp
    def _jvp(primals, tangents):
        (x,) = primals
        y = _unvmap_max_impl(x)
        return y, [jnp.zeros_like(y[0]), jnp.zeros((nb,), dtype=float0)]

    return _unvmap_max_impl(x)


@partial(jax.jit, static_argnames=["nb"])
def unvmap_iota(x, nb=None):
    """Get the index of each element in a vmapped computation.

    Returns 0 when called outside of a vmap context. Inside vmap, returns an array
    of indices corresponding to the position along the vmapped axis. When nb is
    specified and axis_size > nb, only the first nb indices are returned (0 to nb-1),
    with remaining positions set to -1.

    This function is differentiable with zero derivatives. Useful for tracking
    position/rank in a vmapped computation or for selecting a subset of iterations.

    Args:
        x: Any JAX array (the value is not used, only to provide context)
        nb: Optional limit on the number of indices to return. If None or if
            axis_size <= nb, returns all indices. If axis_size > nb, returns
            indices 0 to nb-1 and sets remaining positions to -1 (default: None)

    Returns:
        int32 scalar or array:
            - Outside vmap: 0
            - Inside vmap with nb=None or axis_size <= nb: arange(axis_size)
            - Inside vmap with axis_size > nb: first nb indices, then -1

    Examples:
        >>> unvmap_iota(jnp.array(0.))  # Outside vmap
        Array(0, dtype=int32)
        >>> jax.vmap(lambda x: unvmap_iota(x))(jnp.arange(5.))  # Inside vmap, no limit
        Array([0, 1, 2, 3, 4], dtype=int32)
        >>> jax.vmap(lambda x: unvmap_iota(x, nb=3))(jnp.arange(5.))  # With limit
        Array([0, 1, 2, -1, -1], dtype=int32)
    """

    @jax.custom_jvp
    @custom_vmap
    def _unvmap_iota_impl(x):
        return jnp.array(0, dtype=jnp.int32)

    @_unvmap_iota_impl.def_vmap
    def _unvmap_iota_vmap_rule(axis_size, in_batched, x):
        out_batched = True
        if nb is None or axis_size <= nb:
            return jnp.arange(axis_size, dtype=jnp.int32), out_batched
        else:
            indices = jnp.where(
                jnp.arange(axis_size) < nb, jnp.arange(axis_size, dtype=jnp.int32), jnp.array(-1, dtype=jnp.int32)
            )
            return indices, out_batched

    @_unvmap_iota_impl.defjvp
    def _jvp(primals, tangents):
        (x,) = primals
        y = _unvmap_iota_impl(x)
        return y, jnp.array(b"", dtype=float0)

    return _unvmap_iota_impl(x)
