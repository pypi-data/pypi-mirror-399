import jax
import jax.numpy as jnp
import pytest
from jax._src.dtypes import float0

from jax_progress.unvmap import unvmap_iota, unvmap_max, unvmap_min, unvmap_size


def test_unvmap_size_no_vmap():
    @jax.jit
    def test_size(x):
        a = unvmap_size(x)
        return a * 1.0

    a = jnp.arange(12.0)
    b = test_size(a)
    b_rev = jax.jacrev(test_size)(a)
    b_fwd = jax.jacfwd(test_size)(a)

    assert b == 1.0
    assert jnp.all(b_rev == 0.0)
    assert jnp.all(b_fwd == 0.0)


@pytest.mark.parametrize("array_size", [5, 12, 20])
def test_unvmap_size_with_vmap(array_size):
    @jax.jit
    @jax.vmap
    def test_size(x):
        a = unvmap_size(x)
        return a * 1.0

    a = jnp.arange(array_size * 1.0)
    b = test_size(a)
    b_rev = jax.jacrev(test_size)(a)
    b_fwd = jax.jacfwd(test_size)(a)

    assert jnp.all(b == array_size * 1.0)
    assert jnp.all(b_rev == 0.0)
    assert jnp.all(b_fwd == 0.0)


def test_unvmap_min_no_vmap():
    @jax.jit
    def test_min(x):
        a = unvmap_min(x)
        return a

    a = jnp.arange(12.0)
    b = test_min(a[0])
    _, vjp = jax.vjp(test_min, a[0])
    _, b_fwd = jax.jvp(test_min, (a[0],), (jnp.array(1.0),))
    (b_rev,) = vjp([jnp.array([1.0]), jnp.array([1.0])])

    assert b[0] == jnp.array(0.0)
    assert b[1] == jnp.array(0)
    assert jnp.all(b_rev == 0.0)
    assert b_fwd[0] == 0.0
    assert b_fwd[1] == jnp.array(b"", dtype=float0)


@pytest.mark.parametrize("array_size, nb", [(12, 5), (10, 3), (20, 7)])
def test_unvmap_min_with_vmap(array_size, nb):
    @jax.jit
    @jax.vmap
    def test_min(x):
        a = unvmap_min(x, nb=nb)
        return a

    a = jnp.arange(array_size * 1.0)
    b = test_min(a)
    _, vjp = jax.vjp(test_min, a)
    _, b_fwd = jax.jvp(test_min, (a,), (jnp.ones_like(a),))

    cot = jnp.ones((array_size, nb), dtype=a.dtype)
    (b_rev,) = vjp([cot, cot])
    top_k = jnp.arange(nb)
    top_k_inexact = jnp.arange(nb) * 1.0

    assert (b[0] == top_k_inexact[None, :]).all()
    assert (b[1] == top_k[None, :]).all()
    assert jnp.all(b_rev == 0.0)
    assert (b_fwd[0] == 0.0).all()
    assert (b_fwd[1] == jnp.array(b"", dtype=float0)).all()


def test_unvmap_max_no_vmap():
    @jax.jit
    def test_max(x):
        a = unvmap_max(x)
        return a

    a = jnp.arange(12.0)
    b = test_max(a[2])
    _, vjp = jax.vjp(test_max, a[0])
    _, b_fwd = jax.jvp(test_max, (a[0],), (jnp.array(1.0),))
    (b_rev,) = vjp([jnp.array([1.0]), jnp.array([1.0])])

    assert b[0] == a[2]
    assert b[1] == jnp.array(0)
    assert jnp.all(b_rev == 0.0)
    assert b_fwd[0] == 0.0
    assert b_fwd[1] == jnp.array(b"", dtype=float0)


@pytest.mark.parametrize("array_size, nb", [(12, 5), (10, 3), (20, 7)])
def test_unvmap_max_with_vmap(array_size, nb):
    @jax.jit
    @jax.vmap
    def test_max(x):
        a = unvmap_max(x, nb=nb)
        return a

    a = jnp.arange(array_size * 1.0)
    b = test_max(a)
    _, vjp = jax.vjp(test_max, a)
    _, b_fwd = jax.jvp(test_max, (a,), (jnp.ones_like(a),))

    cot = jnp.ones((array_size, nb), dtype=a.dtype)
    (b_rev,) = vjp([cot, cot])
    top_k = jnp.arange(array_size, array_size - nb, -1) - 1
    top_k_inexact = top_k * 1.0

    assert (b[0] == top_k_inexact[None, :]).all()
    assert (b[1] == top_k[None, :]).all()
    assert jnp.all(b_rev == 0.0)
    assert (b_fwd[0] == 0.0).all()
    assert (b_fwd[1] == jnp.array(b"", dtype=float0)).all()


def test_unvmap_iota_no_vmap():
    nb = 5

    @jax.jit
    def test_iota(x):
        a = unvmap_iota(x, nb=nb)
        return a

    a = jnp.arange(12.0)
    b = test_iota(a)
    _, vjp = jax.vjp(test_iota, a)
    _, b_fwd = jax.jvp(test_iota, (a,), (jnp.ones_like(a),))

    cot = jnp.array(1, dtype=a.dtype)
    (b_rev,) = vjp(cot)

    assert b == jnp.array(0)
    assert jnp.all(b_rev == 0.0)
    assert b_fwd == jnp.array(b"", dtype=float0)


@pytest.mark.parametrize("array_size, nb", [(12, 5), (10, 3), (20, 7), (8, 10)])
def test_unvmap_iota_with_vmap(array_size, nb):
    @jax.jit
    @jax.vmap
    def test_iota(x):
        a = unvmap_iota(x, nb=nb)
        return a

    a = jnp.arange(array_size * 1.0)
    b = test_iota(a)
    _, vjp = jax.vjp(test_iota, a)
    _, b_fwd = jax.jvp(test_iota, (a,), (jnp.ones_like(a),))

    cot = jnp.ones_like(b, dtype=a.dtype)
    (b_rev,) = vjp(cot)

    assert (b == jnp.where(jnp.arange(array_size) < nb, jnp.arange(array_size), -1)).all()
    assert jnp.all(b_rev == 0.0)
    assert (b_fwd == jnp.array(b"", dtype=float0)).all()
