---
object_id: PAT_use_rust_expect_only_when_failure_proves_a_broken_assumption
object_type: pattern
name: Use Rust Expect Only When Failure Proves a Broken Assumption
library_path: [software-engineering, languages, rust, error-handling]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, expect, unwrap, panic, invariants]
cross_links:
- rel: related_to
  target_object_id: PAT_enforce_contracts_at_runtime_with_checks
- rel: related_to
  target_object_id: PAT_fail_fast_near_error_source
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Use Rust Expect Only When Failure Proves a Broken Assumption

## Pattern Rule
**IF** a Rust `Result` or `Option` can fail only when a nearby, reviewable program assumption is false
**THEN** use `expect` with a message stating that assumption so failure is loud and diagnostic
**ELSE** preserve and handle or propagate the recoverable case.

## Do
- Tie each `expect` to an invariant established by hard-coded data, prior validation, or the test's setup.
- Write the message as what should have been true, not merely that an operation failed.
- Use panic-producing extraction naturally when failure should fail the current test.
- Replace prototype markers before production whenever real inputs can reach the failure.

## Don't
- Don't use `unwrap` or `expect` on user, file, network, timing, or configuration failures merely for brevity.
- Don't claim an invariant that can drift independently from the value being extracted.
- Don't catch the resulting panic as ordinary local error control.

## Checklist
- What exact assumption makes failure impossible?
- Is that assumption enforced near this call?
- Would any valid runtime circumstance still produce failure?
- Does the message identify the violated assumption?

## Notes
`expect` converts a typed possible failure into an invariant assertion. It is appropriate only when the corrective action is to fix code or test setup, not to recover from runtime conditions.
