"""Test script for the progress meter implementation."""

from functools import partial

import jax
import jax.numpy as jnp
from jax.sharding import PartitionSpec as P

from jax_progress import TqdmProgressMeter


def test_vmap_vmap_with_limitation():
    """Nested vmap with max_bars limitation."""
    pbar = TqdmProgressMeter(total=5, max_bars=2)

    def inner(elements):
        state = pbar.init(vmapped_element=elements)

        def scan_body(carry, x):
            return pbar.step(carry, progress=1), x

        state, _ = jax.lax.scan(scan_body, state, elements)
        pbar.close(state)
        return state

    arr = jnp.ones((2, 3, 5))
    jax.vmap(jax.vmap(inner))(arr)


def test_shardmap():
    """Basic shard_map test."""
    mesh = jax.make_mesh((8,), ("x",))
    pbar = TqdmProgressMeter(total=5)

    @partial(jax.shard_map, mesh=mesh, in_specs=P("x"), out_specs=P("x"))
    def sharded(x):
        state = pbar.init(spec=P("x"))

        def scan_body(carry, i):
            return pbar.step(carry, progress=1), i

        state, _ = jax.lax.scan(scan_body, state, jnp.arange(5))
        pbar.close(state)
        return x

    sharded(jnp.ones(8))


def test_shardmap_vmap_with_limitation():
    """Combined shard_map + vmap with max_bars."""
    mesh = jax.make_mesh((4,), ("x",))
    pbar = TqdmProgressMeter(total=5, max_bars=2)

    @partial(jax.shard_map, mesh=mesh, in_specs=(P("x"), P()), out_specs=P("x"))
    def sharded(x, task_id):
        state = pbar.init(vmapped_element=task_id, spec=P("x"))

        def scan_body(carry, i):
            return pbar.step(carry, progress=1), i

        state, _ = jax.lax.scan(scan_body, state, jnp.arange(5))
        pbar.close(state)
        return x

    # vmap over 3 tasks, each sharded across 4 devices
    jax.vmap(sharded)(jnp.ones((3, 4)), jnp.arange(3.0))
