---
object_id: PAT_program_rust_io_against_read_and_write_traits
object_type: pattern
name: Program Rust I/O Against Read and Write Traits
library_path:
- software-engineering
- languages
- rust
- io
stage_binding: 1 skeleton
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
- abstraction
- testability
cross_links:
- rel: related_to
  target_object_id: PAT_choose_rust_io_methods_by_completion_contract
- rel: related_to
  target_object_id: PAT_choose_rust_buffering_by_io_operation_shape
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Program Rust I/O Against Read and Write Traits

## Pattern Rule
**IF** Rust logic only needs byte-stream reading or writing and should work across more than one concrete I/O source or sink
**THEN** accept the narrow `Read`, `Write`, or `BufRead` capability the algorithm requires instead of coupling the algorithm to `File`, `TcpStream`, stdin, or another concrete handle
**ELSE** keep the concrete type when device-specific behavior is part of the contract

## Do
- Express reusable byte-processing functions with generic bounds, `impl Read`/`impl Write`, or trait objects according to the ownership and dispatch needs of the surrounding API.
- Request `BufRead` only when the algorithm actually needs buffered operations such as line-oriented or delimiter-oriented reads.
- Keep device-specific setup outside the generic algorithm, then pass the resulting reader or writer through the trait boundary.
- Test stream-processing logic with in-memory readers and writers when the behavior does not require a real operating-system device.

## Don't
- Don't make parsing, copying, encoding, or formatting logic take a `File` solely because the first caller happened to use a file.
- Don't generalize away methods the algorithm truly requires from a concrete device or protocol type; a narrower trait is useful only when it still states the real contract.
- Don't confuse trait-level portability with transfer completion; `Read::read` and `Write::write` may still make partial progress.

## Checklist
- Which I/O operations does the algorithm actually call?
- Can setup and device-specific behavior stay outside this function?
- Would an in-memory reader or writer satisfy the same contract for a test?
- Does the selected trait still expose every operation the algorithm legitimately requires?

## Notes
`std::io::Read` and `Write` are implemented by multiple I/O types, including files and TCP streams, so they form a capability boundary rather than a device identity. Depending on that boundary keeps data-processing logic reusable and testable while leaving concrete resource acquisition and protocol-specific controls at the edges.
