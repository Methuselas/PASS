---
object_id: PAT_choose_rust_io_methods_by_completion_contract
object_type: pattern
name: Choose Rust I/O Methods by Completion Contract
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
- read
- write
- protocols
cross_links:
- rel: related_to
  target_object_id: PAT_keep_rust_failures_as_result_until_recovery_context_exists
confidence: medium
references: []
variants: []
---

# Choose Rust I/O Methods by Completion Contract

## Pattern Rule
**IF** a Rust I/O step is correct only after a specific amount of data has been transferred
**THEN** choose an API whose completion contract matches that requirement: handle the count from `read` or `write` when partial progress is meaningful, or use `read_exact` or `write_all` when the whole buffer must complete

## Do
- Treat the `usize` returned by `Read::read` and `Write::write` as part of the operation result rather than assuming the supplied buffer was completely transferred.
- Use `read_exact` when the protocol requires the entire fixed-size input buffer before the next step can run.
- Use `write_all` when returning success means the entire supplied output buffer has been accepted by the writer.
- Preserve `io::Result` failures with `?` or explicit handling until code with enough context can choose retry, translation, reporting, or termination.

## Don't
- Do not discard the byte count from `read` or `write` when later code assumes the whole buffer moved.
- Do not use an exact-transfer helper when EOF or partial progress is a meaningful protocol event that the caller must observe incrementally.
- Do not replace ordinary environmental I/O failure with `unwrap` merely to obtain the successful value.

## Checklist
- May this operation legitimately make partial progress?
- Does the next parsing or protocol step require exactly this many bytes?
- What does zero-byte progress mean for this source or sink?
- At what boundary is there enough context to handle an I/O failure?

## Notes
`Read` and `Write` are partial-progress interfaces. The exact-transfer helpers encode a stronger completion contract by looping internally until the buffer is complete or a terminal error condition is reached.
