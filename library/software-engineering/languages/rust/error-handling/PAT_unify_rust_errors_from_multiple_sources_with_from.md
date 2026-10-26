---
object_id: PAT_unify_rust_errors_from_multiple_sources_with_from
object_type: pattern
name: Unify Rust Errors From Multiple Sources With From Conversions
library_path:
- software-engineering
- languages
- rust
- error-handling
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- error-handling
- result
- from
- question-mark
cross_links:
- rel: related_to
  target_object_id: PAT_keep_rust_failures_as_result_until_recovery_context_exists
- rel: related_to
  target_object_id: PAT_propagate_rust_failures_with_question_mark_at_a_compatible_boundary
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Unify Rust Errors From Multiple Sources With From Conversions

## Pattern Rule
**IF** one Rust API boundary composes fallible operations with different error types but should expose one structured error type
**THEN** define the boundary error and implement meaningful `From` conversions from each source error type so `?` can propagate each source failure through that single contract
**ELSE** return the existing error type directly when no unification boundary is needed

## Do
- Give the boundary error variants or fields that preserve the source distinction callers may need for reporting, retry, or recovery.
- Implement `From` conversions from each source error type when conversion is unconditional and has one clear meaning; then let `?` perform that conversion during propagation.
- When the boundary type is a public error meant to compose with the Rust error ecosystem, implement `Display` and `std::error::Error`; return wrapped causes from `source()` so diagnostic chains remain available.
- Implement `Display` from the error's fields or wrapped source, not by formatting `self` through its own `Display` implementation, which recursively re-enters the same formatter.
- Use explicit handling or `map_err` when conversion depends on local context rather than pretending a context-dependent policy is a universal `From` conversion.
- Keep one natural source error type when the function already has a coherent error contract instead of manufacturing a wrapper only for uniformity.

## Don't
- Don't use `unwrap` merely because adjacent calls return different error types.
- Don't flatten source errors into strings before the boundary has finished making recovery and reporting decisions.
- Don't implement a lossy `From` conversion that discards the source error or collapses materially different failures into an indistinguishable variant.

## Checklist
- Does this boundary genuinely need to expose one error type?
- Can every automatic conversion preserve the information callers still need?
- If callers need standard error chaining, does the boundary type implement `Error` and expose wrapped causes through `source()`?
- Does `Display` format concrete fields or causes without recursively formatting `self`?
- Is each `From` conversion unconditional, or should a local `map_err` make the policy explicit?
- Can the resulting function use `?` without hiding where distinct failures came from?

## Notes
For `Result`, the `?` operator propagates an error after converting it with `From::from` when the enclosing result uses a different error type. That makes `From` a useful boundary tool: heterogeneous low-level failures can remain structured while the public function presents one stable error contract. The conversion should encode representation, not erase policy-relevant information.
