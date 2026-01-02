from math import prod

import jax
import jax.numpy as jnp
import numpy as np
import pytest
from jax import lax
from jax.sharding import Mesh, NamedSharding
from jax.sharding import PartitionSpec as P

from jax_progress.unshard import unshard_iota, unshard_max, unshard_min, unshard_size

# Helper functions


def make_test_mesh(mesh_shape, axis_names):
    """Create mesh from shape and names."""
    devices = jax.devices()[: prod(mesh_shape)]
    return Mesh(np.array(devices).reshape(mesh_shape), axis_names)


def create_sharded_array(mesh, spec, data):
    """Create properly sharded array from data."""
    sharding = NamedSharding(mesh, spec)
    return lax.with_sharding_constraint(data, sharding)


# Tests for unshard_size


def test_unshard_size_no_shard_map():
    """Test unshard_size outside shard_map context - should fail."""
    with pytest.raises(Exception):  # Expecting error without axis context
        unshard_size(P("x"))


@pytest.mark.parametrize(
    "mesh_shape,axis_names,spec,expected_size",
    [
        pytest.param((8,), ("x",), P("x"), 8, id="1d-x"),
        pytest.param((4, 2), ("x", "y"), P("x"), 4, id="2d-x"),
        pytest.param((4, 2), ("x", "y"), P("y"), 2, id="2d-y"),
        pytest.param((4, 2), ("x", "y"), P("x", "y"), 8, id="2d-xy"),
        pytest.param((2, 2, 2), ("x", "y", "z"), P("x", "y", "z"), 8, id="3d-xyz"),
        pytest.param((2, 2, 2), ("x", "y", "z"), P("x", "z"), 4, id="3d-xz"),
        pytest.param((2, 2, 2), ("x", "y", "z"), P("y"), 2, id="3d-y"),
        pytest.param((2, 2, 2), ("x", "y", "z"), P(), 1, id="3d-empty"),
    ],
)
def test_unshard_size_with_shard_map(mesh_shape, axis_names, spec, expected_size):
    """Test unshard_size computes correct product of axis sizes."""
    mesh = make_test_mesh(mesh_shape, axis_names)

    @jax.jit
    @jax.shard_map(mesh=mesh, in_specs=spec, out_specs=P())
    def test_fn(x):
        size = unshard_size(spec)
        return size * 1.0

    x = jnp.ones(mesh_shape)
    x_sharded = create_sharded_array(mesh, spec, x)

    result = test_fn(x_sharded)
    assert result == expected_size * 1.0


# Tests for unshard_min


def test_unshard_min_no_shard_map():
    """Test unshard_min outside shard_map with scalar value."""
    x = jnp.array(5.0)
    # Should work with empty spec (no axes to reduce over)
    result = unshard_min(x, P())
    assert result == 5.0


@pytest.mark.parametrize(
    "mesh_shape,axis_names,spec",
    [
        pytest.param((8,), ("x",), P("x"), id="1d-x"),
        pytest.param((4, 2), ("x", "y"), P("x", "y"), id="2d-xy"),
        pytest.param((2, 2, 2), ("x", "y", "z"), P("x", "y", "z"), id="3d-xyz"),
    ],
)
def test_unshard_min_with_shard_map(mesh_shape, axis_names, spec):
    """Test unshard_min finds global minimum across sharded axes."""
    mesh = make_test_mesh(mesh_shape, axis_names)
    num_devices = prod(mesh_shape)

    @jax.jit
    @jax.shard_map(mesh=mesh, in_specs=spec, out_specs=P())
    def test_fn(x):
        return unshard_min(x, spec)

    # Create array where values increase with device index
    # Each device gets a shard with value equal to its index
    # So global min should be 0.0
    data_shape = tuple([mesh_shape[i] if spec[i] is not None else 1 for i in range(len(mesh_shape))])
    x = jnp.arange(num_devices, dtype=jnp.float32).reshape(data_shape)
    x_sharded = create_sharded_array(mesh, spec, x)

    result = test_fn(x_sharded)
    assert result == 0.0


# Tests for unshard_max


def test_unshard_max_no_shard_map():
    """Test unshard_max outside shard_map with scalar value."""
    x = jnp.array(5.0)
    # Should work with empty spec (no axes to reduce over)
    result = unshard_max(x, P())
    assert result == 5.0


@pytest.mark.parametrize(
    "mesh_shape,axis_names,spec",
    [
        pytest.param((8,), ("x",), P("x"), id="1d-x"),
        pytest.param((4, 2), ("x", "y"), P("x", "y"), id="2d-xy"),
        pytest.param((2, 2, 2), ("x", "y", "z"), P("x", "y", "z"), id="3d-xyz"),
    ],
)
def test_unshard_max_with_shard_map(mesh_shape, axis_names, spec):
    """Test unshard_max finds global maximum across sharded axes."""
    mesh = make_test_mesh(mesh_shape, axis_names)
    num_devices = prod(mesh_shape)

    @jax.jit
    @jax.shard_map(mesh=mesh, in_specs=spec, out_specs=P())
    def test_fn(x):
        return unshard_max(x, spec)

    # Create array where values increase with device index
    # Global max should be num_devices - 1
    data_shape = tuple([mesh_shape[i] if spec[i] is not None else 1 for i in range(len(mesh_shape))])
    x = jnp.arange(num_devices, dtype=jnp.float32).reshape(data_shape)
    x_sharded = create_sharded_array(mesh, spec, x)

    result = test_fn(x_sharded)
    assert result == float(num_devices - 1)


# Tests for unshard_iota


def test_unshard_iota_no_shard_map():
    """Test unshard_iota outside shard_map - should return 0 or fail."""
    # With empty spec, should return 0
    result = unshard_iota(P())
    assert result == 0


@pytest.mark.parametrize(
    "mesh_shape,axis_names,spec",
    [
        pytest.param((8,), ("x",), P("x"), id="1d-x"),
        pytest.param((4, 2), ("x", "y"), P("x", "y"), id="2d-xy"),
        pytest.param((2, 4), ("x", "y"), P("x", "y"), id="2d-xy-alt"),
        pytest.param((2, 2, 2), ("x", "y", "z"), P("x", "y", "z"), id="3d-xyz"),
    ],
)
def test_unshard_iota_with_shard_map(mesh_shape, axis_names, spec):
    """Test unshard_iota assigns correct device indices."""
    mesh = make_test_mesh(mesh_shape, axis_names)
    num_devices = prod(mesh_shape)

    @jax.jit
    @jax.shard_map(mesh=mesh, in_specs=spec, out_specs=spec)
    def test_fn(x):
        iota = unshard_iota(spec)
        return x + iota

    # Create array with zeros
    x = jnp.zeros(mesh_shape)
    x_sharded = create_sharded_array(mesh, spec, x)

    result = test_fn(x_sharded)

    # Verify each device gets the correct index
    for device_idx in range(num_devices):
        device_data = jax.device_get(result.addressable_data(device_idx))
        added_value = device_data.flatten()[0]
        assert int(added_value) == device_idx


def test_unshard_iota_ordering():
    """Test unshard_iota follows row-major ordering (first axis varies slowest)."""
    mesh = make_test_mesh((2, 4), ("x", "y"))

    @jax.jit
    @jax.shard_map(mesh=mesh, in_specs=P("x", "y"), out_specs=P())
    def test_fn(x):
        return unshard_iota(P("x", "y"))

    x = jnp.zeros((2, 4))
    x_sharded = create_sharded_array(mesh, P("x", "y"), x)

    # Collect iota values from each device
    indices = []
    for device_idx in range(8):

        @jax.jit
        @jax.shard_map(mesh=mesh, in_specs=P("x", "y"), out_specs=P("x", "y"))
        def get_iota(x):
            return unshard_iota(P("x", "y")) * jnp.ones_like(x)

        result = get_iota(x_sharded)
        device_data = jax.device_get(result.addressable_data(device_idx))
        indices.append(int(device_data.flatten()[0]))

    # Verify row-major ordering: [0,1,2,3, 4,5,6,7]
    # x=0: [0,1,2,3], x=1: [4,5,6,7]
    assert indices == list(range(8))


def test_unshard_iota_empty_spec():
    """Test unshard_iota with empty spec."""
    mesh = make_test_mesh((2, 4), ("x", "y"))

    @jax.jit
    @jax.shard_map(mesh=mesh, in_specs=P("x", "y"), out_specs=P("x", "y"))
    def test_fn(x):
        # Empty spec should return 0
        iota = unshard_iota(P())
        return x + iota

    x = jnp.ones((2, 4))
    x_sharded = create_sharded_array(mesh, P("x", "y"), x)

    result = test_fn(x_sharded)
    # With empty spec, iota should be 0, so result should equal x
    expected = x
    assert jnp.allclose(result, expected)
