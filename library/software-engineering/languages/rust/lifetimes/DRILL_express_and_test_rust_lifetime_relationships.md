---
object_id: DRILL_express_and_test_rust_lifetime_relationships
object_type: drill
name: Express and Test Rust Lifetime Relationships
library_path: [software-engineering, languages, rust, lifetimes]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, lifetimes, borrowing, compiler_diagnostics, api_design]
cross_links:
- rel: teaches
  target_object_id: PAT_tie_rust_borrowed_outputs_to_possible_input_sources
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
target_skill: expressing borrowed output provenance in Rust function signatures
references: []
variants: []
---

# Express and Test Rust Lifetime Relationships

## Practice Task
Write and test three Rust signatures whose borrowed outputs have different provenance: either input, only the first input, and local storage that cannot be returned.

## Target Skill
Expressing the actual relationship between borrowed inputs and outputs without using lifetime annotations to invent storage duration.

## Setup
Use a small Rust crate with compiler checks enabled and two nested scopes that can give input references observably different lifetimes.

## Instructions
1. Implement a function that may return either of two borrowed string slices, add the lifetime relation its return branches require, and run one accepted call.
2. Add a call that stores the result beyond the shorter input's scope and capture the compiler rejection.
3. Change a separate function so it always returns its first borrowed parameter while only inspecting the second, and write the least restrictive valid signature.
4. Demonstrate that the second function's result remains usable after the unrelated second input expires.
5. Attempt to return a reference to a locally created owned string and capture the compiler rejection.
6. Repair the local-value case by returning ownership, then run it after the function has returned.
7. For each signature, record the possible owner of the returned storage and why each shared or separate lifetime parameter is present.

## Success Check
- The either-input function is compiled and run in an accepted scope, and a second call is compiled as a deliberate rejection after one possible source expires. Predicting the rejection without invoking the compiler is the plausible near-miss because it does not test the signature.
- The first-input-only signature does not tie its result to the unrelated second reference, demonstrated by using the result after the second input's scope ends.
- The local-reference attempt produces a compiler rejection, and the repaired version returns an owned value that is used after the call.
- The report names the possible storage owner for every returned value; repeating lifetime syntax without provenance does not satisfy the check.
- No repair uses `'static` unless the returned reference truly points at program-lifetime storage.

## Common Failures
- Giving every reference one lifetime parameter even when only one input can supply the output.
- Treating a longer annotation as a way to extend a local value's storage.
- Recording expected compiler behavior without compiling the accepted and rejected cases.

## Notes
This exercise teaches the decision to tie Rust borrowed outputs only to possible input sources. Changing values and scope lengths turns abstract lifetime syntax into observable interface behavior, and the contrast among possible sources, unrelated inputs, and local storage makes the signature's claim concrete enough to test.
