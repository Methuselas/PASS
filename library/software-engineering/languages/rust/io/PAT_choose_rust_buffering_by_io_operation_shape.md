---
object_id: PAT_choose_rust_buffering_by_io_operation_shape
object_type: pattern
name: Choose Rust Buffering by I/O Operation Shape
library_path:
- software-engineering
- languages
- rust
- io
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- io
- buffering
- performance
- syscalls
cross_links:
- rel: related_to
  target_object_id: PAT_choose_rust_io_methods_by_completion_contract
confidence: medium
references: []
variants: []
---

# Choose Rust Buffering by I/O Operation Shape

## Pattern Rule
**IF** a Rust reader or writer performs many small operations across an operating-system I/O boundary
**THEN** wrap the underlying handle in `BufReader` or `BufWriter` so logical operations can be coalesced, while making buffered-output completion explicit where write failure must be observed

## Do
- Use `BufReader` for repeated small reads from an unbuffered source and `BufWriter` for repeated small writes to an unbuffered sink.
- Keep one buffering owner for a stream segment; preserve or deliberately consume buffered data before unwrapping, replacing, or bypassing a `BufReader`.
- Call `flush` on `BufWriter` at the boundary where buffered-write failure must still be returned or handled.
- Prefer direct I/O when transfers are already large and infrequent, and avoid adding a buffer around data already resident in memory unless another buffered operation is required.

## Don't
- Do not assume buffering makes every read or write faster; its value depends on operation size, frequency, and the underlying source or sink.
- Do not create competing `BufReader` instances over the same stream position or bypass a reader that may already have prefetched bytes.
- Do not rely on dropping `BufWriter` as proof that its buffered bytes reached the underlying writer; drop-time flush errors are ignored.

## Checklist
- Are calls small and repeated enough that reducing underlying I/O calls matters?
- Is the underlying source or sink already buffered or already in memory?
- Could replacing or bypassing this reader discard prefetched bytes?
- Where must buffered-write failure become observable?

## Notes
Buffering is a property of the I/O boundary, not of files specifically. Rust's buffered wrappers work over compatible readers and writers such as files and sockets, so the decision should follow the operation pattern of the underlying stream.
