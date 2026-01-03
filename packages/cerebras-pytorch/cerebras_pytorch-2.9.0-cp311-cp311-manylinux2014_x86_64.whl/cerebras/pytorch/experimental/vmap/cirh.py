# Copyright 2016-2024 Cerebras Systems
# SPDX-License-Identifier: BSD-3-Clause

import cerebras.pytorch as cstorch

from . import utils as vmap

"""
Guidelines for adding new CIRH op wrappers with vmap support
============================================================

This module provides thin wrappers that make CIRH ops (cstorch.cirh.*)
compatible with functorch vmap batching. Follow these rules to keep behavior
correct, consistent, and debuggable.

Core invariants
---------------
1) Purity: Wrappers must be free of side effects on inputs. Don’t mutate
   user tensors in-place. Return new tensors.

2) Shape & Level Preservation: If any input is batched (i.e., wrapped in one
   or more functorch batch levels), all tensor outputs must be rewrapped with
   exactly those levels, in the same order.

3) Semantics Parity: With zero batch levels, the wrapper must be equivalent to
   calling the underlying CIRH op directly.

4) No Silent Broadcasting of Non-Tensor Args: If a non-tensor argument is
   logically per-batch (e.g., per-sample reduction dims), make that explicit.
   Otherwise, treat non-tensor args as global constants across the batch.

Input handling
--------------
- Accept tensors or sequences of tensors. For each tensor:
  a) Unwrap all functorch batch levels:  base, batch_info = unwrap_batched(t)
  b) Keep `batch_info` for each input so you can rewrap outputs correctly.

- Mixed batched/unbatched inputs:
  - If some inputs are batched and others aren’t, only adjust arguments (dims,
    paddings, etc.) according to the batched inputs actually used by the op.
  - Never add/remove batch levels yourself—just unwrap/rewrap.

Dimension & argument adjustments (the “dim-shift” rule)
-------------------------------------------------------
When an op takes a dimension index (e.g., reduction dim) relative to the
user tensor, that index must be shifted to account for every batch dimension
that sits at or before that dim.

- Normalize negative dims BEFORE shifting:
    dim = dim if dim >= 0 else x.dim() + dim
- For each (bdim, _) in batch_info (outermost → innermost):
    if bdim <= dim: dim += 1

Padding/unpadding-style arguments
---------------------------------
- Args that are lists/tuples per tensor dimension (e.g., edge paddings) must
  be expanded to reflect batch dims at their correct positions.
- For each (bdim, _) in batch_info (outermost → innermost), insert the neutral
  element at `bdim` (e.g., 0 for unpadding_high) so CIRH sees a spec that
  matches the unwrapped tensor’s actual rank.

Outputs
-------
- For single-tensor outputs: rewrap with the input’s `batch_info`.
- For multi-output/tuple outputs: rewrap each tensor output; passthrough
  non-tensor outputs unchanged unless they should be per-batch (rare).
- For sequence inputs (list/tuple of tensors), rewrap each output with the
  corresponding input’s batch_info (maintain positional mapping).

dtype/device
-----------------------
- Do not change dtype, device, or requires_grad. Let CIRH/autograd handle it.

RNG & determinism
-----------------
- If the underlying op uses randomness, ensure it is compatible with vmap (no
  cross-sample state sharing). Prefer stateless/randomness-as-input designs.
  Otherwise, document limitations.

Performance notes
-----------------
- Avoid Python-side loops over the batch dimension — use a single CIRH call on
  the unwrapped base tensor after correctly adjusting arguments.
- Keep unwrap/rewrap minimal and outside hot inner loops.

Error handling & validation
---------------------------
- Validate tensor inputs (type/shape assumptions) early. Raise clear errors.
- Never rely on private functorch APIs for behavior not covered by comments.
  We currently use:
    torch._C._functorch.is_batchedtensor
    torch._C._functorch.maybe_get_bdim
    torch._C._functorch.maybe_get_level
    torch._C._functorch.get_unwrapped
    torch._C._functorch._add_batch_dim
  These are version-dependent—add a short note if behavior changes for new
  PyTorch versions.

Testing checklist
-----------------
[ ] No-batch equivalence: wrapper(x) == raw CIRH op(x) for identical args.
[ ] Single-level vmap: shapes & results match vmap(expectation) with dim shifts.
[ ] Multi-level vmap: nesting preserved; dims correctly shifted for each level.
[ ] Negative dims: behave identically to positive normalized dims.
[ ] Sequence I/O: list/tuple inputs/outputs keep positional batch associations.
[ ] Edge argument expansion: padding/unpadding specs align with new rank.
[ ] Mixed batched/unbatched: correct behavior without accidental broadcasting.
"""


def AnnotateTensor(input, *, tensor_annotation):
    unwrapped = [vmap.unwrap_batched(t) for t in input]
    input, input_batch_info = zip(*unwrapped)

    output = cstorch.cirh.AnnotateTensor(
        input,
        tensor_annotation=tensor_annotation,
    )
    return [vmap.wrap_batched(t, b) for t, b in zip(output, input_batch_info)]


def ScopeBoundary(input, *, boundary_type, scope_name):
    unwrapped = [vmap.unwrap_batched(t) for t in input]
    input, input_batch_info = zip(*unwrapped)

    output = cstorch.cirh.ScopeBoundary(
        input,
        boundary_type=boundary_type,
        scope_name=scope_name,
    )
    return [vmap.wrap_batched(t, b) for t, b in zip(output, input_batch_info)]


def FusedTopK(input, *, k, dimension):
    dimension = dimension if dimension >= 0 else input.dim() + dimension
    input, batch_info = vmap.unwrap_batched(input)
    for bdim, _ in batch_info:
        dimension += 1 if bdim <= dimension else 0

    topKOutput = cstorch.cirh.FusedTopK(input, k=k, dimension=dimension)
    return vmap.wrap_batched(topKOutput, batch_info)


def TopK(
    input, *, k, dimension, original_scores=None, largest=True, sorted=True
):
    dimension = dimension if dimension >= 0 else input.dim() + dimension
    input, batch_info = vmap.unwrap_batched(input)
    for bdim, _ in batch_info:
        dimension += 1 if bdim <= dimension else 0

    if original_scores is None:
        values, indices, _ = cstorch.cirh.TopK(
            input,
            k=k,
            dimension=dimension,
            largest=largest,
            sorted=sorted,
        )
    else:
        original_scores, _ = vmap.unwrap_batched(original_scores)
        _, indices, values = cstorch.cirh.TopK(
            input,
            metadata=original_scores,
            k=k,
            dimension=dimension,
            largest=True,
            sorted=True,
        )

    return (
        vmap.wrap_batched(values, batch_info),
        vmap.wrap_batched(indices, batch_info),
    )


def unpad(operand, *, edge_unpadding_high):
    operand, batch_info = vmap.unwrap_batched(operand)
    for bdim, _ in batch_info:
        edge_unpadding_high.insert(bdim, 0)

    output = cstorch.cirh.unpad(
        operand,
        edge_unpadding_high=edge_unpadding_high,
    )
    return vmap.wrap_batched(output, batch_info)
