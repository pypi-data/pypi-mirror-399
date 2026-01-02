import abc
import importlib.util
import threading
from collections.abc import Callable
from typing import Any, Generic, TypeVar

import equinox as eqx
import jax
import jax.debug as jdg
import jax.numpy as jnp
import numpy as np
from jax import lax
from jax.experimental import io_callback
from jaxtyping import Array, Float, Int, PyTree

from .unshard import unshard_iota, unshard_size
from .unvmap import unvmap_iota, unvmap_size

_State = TypeVar("_State", bound=PyTree[Array])


class _TqdmProgressMeterState(eqx.Module):
    """State for TqdmProgressMeter tracking both vmap and shard_map context."""

    bar_idx: Int[Array, ""]  # Which bar this task uses (for bar management)
    step_count: Int[Array, ""]  # Number of steps taken (for increment mode)
    progress: Float[Array, ""]  # Current progress value

    # Vmap tracking (for task-level parallelism)
    v_index: Int[Array, ""]  # Vmap task index (0-indexed)
    v_size: Int[Array, ""]  # Total vmap tasks (1 if not vmapped)

    # Device tracking (for shard_map parallelism)
    rank: Int[Array, ""]  # Device rank/index (0-indexed)
    size: Int[Array, ""]  # Total devices (1 if not sharded)


def _default_description_callback(state: _TqdmProgressMeterState, args) -> str:
    """Default description showing device and/or task info.

    Runs on host side, so can use regular Python conditionals.
    Only shows info for contexts that are actually present (size > 1).
    """
    parts = []

    # Add device info if in shard_map context (size > 1)
    if int(state.size) > 1:
        parts.append(f"Device {int(state.rank) + 1}/{int(state.size)}")

    # Add task info if in vmap context (v_size > 1)
    if int(state.v_size) > 1:
        parts.append(f"task {int(state.v_index) + 1}/{int(state.v_size)}")

    # Join parts with space, or return generic description
    return " ".join(parts) if parts else "Progress"


class _ProgressMeterManager:
    """Host-side progress meter manager."""

    def __init__(self):
        self.bars = {}
        self.counter = 0  # For diffrax-style init without vmapped_element
        self.lock = threading.Lock()

    def create_bar(self, init_bar: Callable[[], Any], idx) -> None:
        def _host_side(idx):
            # idx may be batched (array) or scalar
            with self.lock:
                idx_val = int(idx)
                if idx_val == -1:
                    return  # No bar for this task
                if idx_val not in self.bars:
                    bar = init_bar()
                    self.bars[idx_val] = bar

        jdg.callback(_host_side, idx)

    def get_counter(self, size) -> Int[Array, ""]:
        """Create a bar using internal counter (diffrax-style)."""

        def _init(size):
            with self.lock:
                old_counter = self.counter
                self.counter += size
                return np.array(old_counter, dtype=np.int32)

        meter_idx = io_callback(_init, jax.ShapeDtypeStruct((), jnp.int32), size)
        return meter_idx

    def step(self, state: _TqdmProgressMeterState, description_callback, description_args):
        def _host_side(state_pytree, description_args):
            # Convert pytree to host values
            idx_val = int(state_pytree.bar_idx)
            if idx_val == -1:
                return  # No bar for this task

            bar = self.bars.get(idx_val)
            if bar is None:
                return  # Bar not found

            # Build description using callback (runs on host)
            if description_callback is not None:
                desc = description_callback(state_pytree, description_args)
                if desc is not None:
                    bar.set_description(desc)

            bar.n = float(state_pytree.progress)
            bar.refresh()

        jdg.callback(_host_side, state, description_args)

    def delete_bar(self, idx, terminate=False) -> None:
        def _host_side(idx):
            # idx may be batched (array) or scalar
            with self.lock:
                if idx is not None:
                    idx_val = int(idx)
                    if idx_val == -1:
                        return  # No bar to delete

                    bar = self.bars.get(idx_val)
                    if bar is not None:
                        if not terminate and bar.n < bar.total:
                            return
                        else:
                            bar.n = bar.total
                            bar.refresh()
                            bar.close()
                            del self.bars[idx_val]
                else:
                    # Delete all bars
                    for bar in self.bars.values():
                        if not terminate and bar.n < bar.total:
                            continue
                        else:
                            bar.n = bar.total
                            bar.refresh()
                            bar.close()
                    self.bars.clear()

        jdg.callback(_host_side, idx)


_progress_meter_manager = _ProgressMeterManager()


class AbstractProgressMeter(eqx.Module, Generic[_State]):
    """Progress meters used to indicate how far along a solve is. Typically these
    perform some kind of printout as the solve progresses.
    """

    @abc.abstractmethod
    def init(self, vmapped_element=None, spec=None) -> _State:
        """Initialises the state for a new progress meter.

        **Arguments:**

        - `vmapped_element`: Optional array from vmapped context to detect vmap size.
        - `spec`: Optional PartitionSpec for shard_map context to detect device count.

        **Returns:**

        The initial state for the progress meter.
        """

    @abc.abstractmethod
    def step(self, state: _State, progress) -> _State:
        """Updates the progress meter. Called on every numerical step of a differential
        equation solve.

        **Arguments:**

        - `state`: the state from the previous step.
        - `progress`: how far along the solve is.

        **Returns:**

        The updated state. In addition, the meter is expected to update as a
        side-effect.
        """

    @abc.abstractmethod
    def close(self, state: _State):
        """Closes the progress meter. Called at the end of a differential equation
        solve.

        **Arguments:**

        - `state`: the final state from the end of the solve.

        *Returns:**

        None.
        """

    @abc.abstractmethod
    def terminate(self):
        """Terminates the progress meter. Called if the solve is interrupted.

        **Arguments:**

        - `state`: the current state when the solve is interrupted.

        **Returns:**

        None.
        """


class NoProgressMeter(AbstractProgressMeter):
    """Indicates that no progress meter should be displayed during the solve."""

    def init(self, vmapped_element=None, spec=None) -> _TqdmProgressMeterState:
        return _TqdmProgressMeterState(
            bar_idx=jnp.array(-1, dtype=jnp.int32),  # -1 means no bar
            step_count=jnp.array(0, dtype=jnp.int32),
            progress=jnp.array(0.0),
            v_index=jnp.array(0, dtype=jnp.int32),  # 0-indexed
            v_size=jnp.array(1, dtype=jnp.int32),  # size=1 means not vmapped
            rank=jnp.array(0, dtype=jnp.int32),  # 0-indexed
            size=jnp.array(1, dtype=jnp.int32),  # size=1 means not sharded
        )

    def step(self, state: _TqdmProgressMeterState, progress, description_args=None) -> _TqdmProgressMeterState:
        return state

    def close(self, state: _TqdmProgressMeterState):
        pass

    def terminate(self):
        pass


class TqdmProgressMeter(AbstractProgressMeter):
    """Uses tqdm to display a progress bar for the solve.

    Supports dynamic bar assignment when using vmap with max_bars < vmap_size.
    The slowest tasks get the progress bars via unvmap_min.
    """

    refresh_steps: int = 20
    total: int = eqx.field(default=100, static=True)
    bar_format: str = eqx.field(
        default="{desc}: {percentage:.0f}%|{bar}| {n:.01f}/{total:.01f} [{elapsed}<{remaining}]", static=True
    )
    description_callback: Callable[..., str] = eqx.field(default=_default_description_callback, static=True)
    max_bars: int = eqx.field(default=None, static=True)
    percent_progress: bool = eqx.field(default=False, static=True)
    leave: bool = eqx.field(default=True, static=True)

    def __check_init__(self):
        if importlib.util.find_spec("tqdm") is None:
            raise ValueError(
                "Cannot use `TqdmProgressMeter` without `tqdm` installed. " "Install it via `pip install tqdm`."
            )
        if self.max_bars is not None and self.max_bars <= 0:
            raise ValueError("max_bars must be a positive integer or None.")

    def init(self, vmapped_element=None, spec=None) -> _TqdmProgressMeterState:
        """Initialize progress meter state.

        **Arguments:**

        - `vmapped_element`: An array from the vmapped context to detect vmap size.
          If None, no vmap tracking.
        - `spec`: PartitionSpec for shard_map context to detect device count.
          If None, no device tracking.

        **Returns:**

        The initial state for the progress meter.
        """
        # Determine vmap context
        if vmapped_element is not None:
            v_size = unvmap_size(vmapped_element)
            max_bars = self.max_bars - 1 if self.max_bars is not None else None
            v_index = unvmap_iota(vmapped_element, nb=max_bars)
        else:
            v_size = jnp.array(1, dtype=jnp.int32)
            v_index = jnp.array(0, dtype=jnp.int32)

        # Determine shard_map context
        if spec is not None:
            size = unshard_size(spec)
            rank = unshard_iota(spec)
        else:
            size = jnp.array(1, dtype=jnp.int32)
            rank = jnp.array(0, dtype=jnp.int32)

        # Always use counter for bar assignment
        def _init_bar():
            from tqdm.auto import tqdm

            return tqdm(
                total=float(self.total),
                bar_format=self.bar_format,
                leave=self.leave,
            )

        counter = _progress_meter_manager.get_counter(v_size * size)
        bar_idx = rank + v_index + counter
        _progress_meter_manager.create_bar(_init_bar, bar_idx)

        return _TqdmProgressMeterState(
            bar_idx=bar_idx,
            step_count=jnp.array(0, dtype=jnp.int32),
            progress=jnp.array(0.0),
            v_index=v_index,
            v_size=v_size,
            rank=rank,
            size=size,
        )

    def step(self, state: _TqdmProgressMeterState, progress=1, description_args=None) -> _TqdmProgressMeterState:
        """Update the progress meter.

        **Arguments:**

        - `state`: the state from the previous step.
        - `progress`: If percent_progress=True, a float in [0, 1] representing
          fraction complete. Otherwise, an increment to add to the current progress.
        - `description_args`: Arguments passed to description_callback(state, args).

        **Returns:**

        The updated state.
        """
        # Calculate actual progress value
        if self.percent_progress:
            # Diffrax style: progress is [0, 1] fraction
            actual_progress = progress * self.total
        else:
            # Increment style: add progress to current
            actual_progress = state.progress + progress

        # Create updated state for this step
        updated_state = _TqdmProgressMeterState(
            bar_idx=state.bar_idx,
            step_count=state.step_count + 1,
            progress=actual_progress,
            v_index=state.v_index,
            v_size=state.v_size,
            rank=state.rank,
            size=state.size,
        )

        # Update the bar
        step_fn = jax.tree_util.Partial(
            _progress_meter_manager.step,
            description_callback=self.description_callback,
            description_args=description_args,
        )

        lax.cond(
            (updated_state.step_count % self.refresh_steps == 0) | (actual_progress == self.total),
            step_fn,
            lambda *args: None,
            updated_state,  # Pass the whole state
        )

        return updated_state

    def close(self, state: _TqdmProgressMeterState):
        """Close the progress meter.

        **Arguments:**

        - `state`: the final state from the end of the solve.

        **Returns:**

        None.
        """
        # print stack trace for debugging
        _progress_meter_manager.delete_bar(state.bar_idx, terminate=False)

    def terminate(self):
        """Terminate the progress meter.

        **Arguments:**

        - `state`: the current state when the solve is interrupted.

        **Returns:**

        None.
        """
        _progress_meter_manager.delete_bar(None, terminate=True)
