---
object_id: PAT_propagate_rust_failures_with_question_mark_at_a_compatible_boundary
object_type: pattern
name: Propagate Rust Failures with Question Mark at a Compatible Boundary
library_path: [software-engineering, languages, rust, error-handling]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, result, question-mark, propagation, conversion]
cross_links:
- rel: related_to
  target_object_id: PAT_return_result_type_to_convey_error_cause
- rel: related_to
  target_object_id: PAT_dont_hide_errors
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Propagate Rust Failures with Question Mark at a Compatible Boundary

## Pattern Rule
**IF** the current Rust function cannot add useful recovery behavior to a fallible operation
**THEN** return a compatible residual type and use `?` to propagate failure, relying only on intentional error conversions
**ELSE** handle the result explicitly where branching, retry, fallback, or added context is required.

## Do
- Give the enclosing function a return type compatible with every use of `?`.
- Define deliberate conversions when several lower-level errors become one public error type.
- Add context before propagation when the raw error does not identify the failed operation.
- Keep local matches when different error variants require different actions.

## Don't
- Don't use `?` as if it logs, retries, or explains an error; it propagates control and data.
- Don't add a broad conversion merely to make unrelated failures compile under one opaque type.
- Don't expand straightforward propagation into repetitive matches that return the same error unchanged.

## Checklist
- What residual type can leave this function?
- Is each conversion lossless enough for the caller's policy?
- Does this layer have recovery context worth using?
- Would added operation context make the propagated error actionable?

## Notes
For `Result`, `?` extracts success and returns early on failure through the language's residual-conversion machinery. It is an ergonomic propagation operator, not an error-handling policy by itself.
