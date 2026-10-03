---
object_id: PAT_keep_rust_failures_as_result_until_recovery_context_exists
object_type: pattern
name: Keep Rust Failures as Result Until Recovery Context Exists
library_path: [software-engineering, languages, rust, error-handling]
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, result, errors, recovery, api]
cross_links:
- rel: related_to
  target_object_id: PAT_classify_error_recoverability_by_caller
- rel: related_to
  target_object_id: PAT_make_callers_aware_of_recoverable_errors
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Keep Rust Failures as Result Until Recovery Context Exists

## Pattern Rule
**IF** a Rust operation can fail for a reason that some caller could report, retry, replace, or translate
**THEN** return a `Result` carrying the successful value or structured error until code with enough context deliberately handles it
**ELSE** reserve a panic for a broken invariant or contract that requires a code fix rather than runtime recovery.

## Do
- Classify recoverability from the caller's position and the origin of the input.
- Preserve distinct error information long enough for a recovery boundary to choose a policy.
- Match specific error categories only when they imply genuinely different actions.
- Let applications convert an error to a process exit or user message at an outer boundary.

## Don't
- Don't panic merely because the current function lacks a recovery policy.
- Don't collapse every error into one message before a caller can inspect its cause.
- Don't make a reusable library decide that an environmental failure must terminate the process.

## Checklist
- Could another caller recover differently?
- Does the error value preserve the information that policy needs?
- Is this layer detecting the failure or actually responsible for recovery?
- Would a panic mean the program is buggy rather than the environment is adverse?

## Notes
`Result` keeps a failure in the type contract and leaves policy to a layer with context. A panic is a different signal: the code has reached a state its contract says should not exist.
