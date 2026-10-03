---
object_id: PAT_match_rust_panic_tests_to_the_intended_failure
object_type: pattern
name: Match Rust Panic Tests to the Intended Failure
library_path: [software-engineering, languages, rust, testing]
stage_binding: 4 final
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_use_appropriate_assertion_matchers
tags: [rust, testing, panic, assertions, error_paths]
cross_links:
- rel: related_to
  target_object_id: PAT_test_behaviors_not_functions
- rel: related_to
  target_object_id: PAT_write_well_explained_test_failures
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Match Rust Panic Tests to the Intended Failure

## Pattern Rule
**IF** a Rust API's contract intentionally panics for a specific invalid use
**THEN** write a focused `#[should_panic(expected = "...")]` test whose expected substring distinguishes that failure from other possible panics.
**ELSE** assert the returned value or error instead of treating any panic as success.

## Do
- Keep the test body narrow enough that the operation named by the case is the only plausible panic source.
- Match a stable, distinctive portion of the panic message that identifies the violated contract while allowing dynamic detail to vary.
- Give separate invalid conditions separate tests when they should reach different panic branches.
- Prefer `Result` or another explicit error value in APIs where callers are expected to recover, and test that value directly.

## Don't
- Don't use an unqualified `#[should_panic]` around a broad setup-and-act sequence; a setup bug or unrelated panic can make the test pass.
- Don't match an entire message when file paths, values, formatting, or other incidental detail can change without changing the contract.
- Don't turn a recoverable error path into a panic merely because panic tests are convenient to write.

## Checklist
- Is panic truly the promised response to this misuse?
- Could any line before the intended operation panic and falsely satisfy the test?
- Does the expected substring identify the right branch without depending on unstable decoration?
- Would a returned error be the more appropriate contract for callers?

## Notes
The unqualified panic assertion checks only that the test thread panicked somewhere. Adding an expected substring makes the result branch-specific, but precision still depends on a focused body and a message fragment owned by the contract rather than by current diagnostic formatting.

