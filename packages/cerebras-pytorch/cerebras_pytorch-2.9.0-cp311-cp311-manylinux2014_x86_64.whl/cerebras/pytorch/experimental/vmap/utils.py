# Copyright 2016-2024 Cerebras Systems
# SPDX-License-Identifier: BSD-3-Clause

import torch


def _check_tensor(tensor):
    """
    Validate that the input is a torch.Tensor.

    Parameters
    ----------
    tensor : Any
        Object to validate.

    Raises
    ------
    ValueError
        If `tensor` is not an instance of `torch.Tensor`.
    """
    if not isinstance(tensor, torch.Tensor):
        raise ValueError("Only Tensor inputs are supported")


def unwrap_batched(tensor):
    """
    Recursively unwrap a functorch vmap-batched tensor to a plain Tensor.

    This walks down through nested functorch BatchedTensors, recording the
    batch dimension (bdim) and vmap level at each nesting depth, until a
    non-batched base tensor is reached.

    Parameters
    ----------
    tensor : torch.Tensor
        Possibly vmap-batched tensor to unwrap.

    Returns
    -------
    base : torch.Tensor
        The underlying (non-batched) tensor.
    batch_info : list[tuple[int, int]]
        Metadata for reconstructing batching, as a list of (bdim, level)
        pairs ordered from outermost → innermost. Each `bdim` is the batch
        dimension index used at that level; `level` is the functorch vmap
        level identifier.

    Raises
    ------
    ValueError
        If `tensor` is not a `torch.Tensor`.

    Notes
    -----
    Uses private functorch internals:
    - `torch._C._functorch.is_batchedtensor`
    - `torch._C._functorch.maybe_get_bdim`
    - `torch._C._functorch.maybe_get_level`
    - `torch._C._functorch.get_unwrapped`
    These are version-dependent and may change across PyTorch releases.
    """
    _check_tensor(tensor)
    batch_info = []
    while torch._C._functorch.is_batchedtensor(tensor):
        bdim = torch._C._functorch.maybe_get_bdim(tensor)
        level = torch._C._functorch.maybe_get_level(tensor)
        batch_info.append((bdim, level))
        tensor = torch._C._functorch.get_unwrapped(tensor)
    return tensor, batch_info


def wrap_batched(tensor, batch_info):
    """
    Re-wrap a plain tensor into a nested functorch BatchedTensor using recorded info.

    This is the inverse of `unwrap_batched`: it applies `_add_batch_dim`
    in reverse order to reconstruct the original BatchedTensor nesting.

    Parameters
    ----------
    tensor : torch.Tensor
        The base (non-batched) tensor to wrap.
    batch_info : list[tuple[int, int]]
        List of (bdim, level) pairs as returned by `unwrap_batched`, ordered
        outermost → innermost.

    Returns
    -------
    torch.Tensor
        The tensor rewrapped with functorch batch dimensions.

    Raises
    ------
    ValueError
        If `tensor` is not a `torch.Tensor`.

    Notes
    -----
    Uses private functorch API `torch._C._functorch._add_batch_dim`.
    """
    _check_tensor(tensor)
    for bdim, level in reversed(batch_info):
        tensor = torch._C._functorch._add_batch_dim(tensor, bdim, level)
    return tensor


def print_tensor_info(tensor, name):
    """
    Print tensor shape and per-level vmap batch metadata for debugging.

    For each nested BatchedTensor level, logs a tuple of
    `(bdim, level, shape_after_unwrap_at_this_step)`. The shapes listed
    correspond to the progressively unwrapped tensor at each step.

    Parameters
    ----------
    tensor : torch.Tensor
        Tensor to inspect (may be vmap-batched).
    name : str
        A short label used in the printed output.

    Side Effects
    ------------
    Prints to stdout:
      - `<name> shape: <shape>`
      - `<name> batch_info with shape: [(bdim, level, shape), ...]`

    Notes
    -----
    This function mutates a local copy during inspection; the original
    `tensor` reference outside the function is not modified.
    """
    print(f"{name} shape:", tensor.shape)
    batch_info = []
    while torch._C._functorch.is_batchedtensor(tensor):
        bdim = torch._C._functorch.maybe_get_bdim(tensor)
        level = torch._C._functorch.maybe_get_level(tensor)
        tensor = torch._C._functorch.get_unwrapped(tensor)
        batch_info.append((bdim, level, tensor.shape))
    print(f"{name} batch_info with shape:", batch_info)
