# jax-progress

Progress meters for JAX loops, scans, and Diffrax solves.

## Features

- Tqdm progress bars for JAX loops (`scan`, `while_loop`).
- Support for `vmap` with correct progress tracking (skips batched updates, tracks n slowest processes).
- Support for `shard_map` with device-level progress tracking.
- `diffrax` compatible progress meter.

## Installation

```bash
pip install jax-progress
```

## Usage

### Basic vmap example

```python
import jax
import jax.numpy as jnp
from jax_progress import TqdmProgressMeter

# Limit to 3 progress bars (shows 3 slowest tasks)
pbar = TqdmProgressMeter(total=100, max_bars=3)

def task(data):
    state = pbar.init(vmapped_element=data)
    def body(carry, x):
        return pbar.step(carry, progress=1), x
    state, _ = jax.lax.scan(body, state, data)
    pbar.close(state)
    return data.sum()

# Run 10 tasks in parallel, but only show 3 slowest
results = jax.vmap(task)(jnp.ones((10, 100)))
```

### shard_map example

```python
from jax.sharding import PartitionSpec as P
from functools import partial

mesh = jax.make_mesh((4,), ('x',))
pbar = TqdmProgressMeter(total=100)

@partial(jax.shard_map, mesh=mesh, in_specs=P('x'), out_specs=P('x'))
def sharded_task(data):
    state = pbar.init(spec=P('x'))
    def body(carry, x):
        return pbar.step(carry, progress=1), x
    state, _ = jax.lax.scan(body, state, jnp.arange(100))
    pbar.close(state)
    return data

results = sharded_task(jnp.ones(4))
```

### Diffrax integration (drop-in replacement)

`TqdmProgressMeter` can be used as a drop-in replacement for Diffrax's default progress meter:

```python
import diffrax

# Create progress meter with percent_progress=True for Diffrax
pbar = TqdmProgressMeter(total=100, percent_progress=True)

# Use directly in diffeqsolve
sol = diffrax.diffeqsolve(
    term, solver, t0=0.0, t1=10.0, dt0=0.01, y0=y0,
    stepsize_controller=stepsize_controller,
    progress_meter=pbar  # Drop-in replacement
)
pbar.terminate()
```

> **Note:** You can combine `vmap` and `shard_map` for multi-level parallelism. See `examples/` directory for more.
