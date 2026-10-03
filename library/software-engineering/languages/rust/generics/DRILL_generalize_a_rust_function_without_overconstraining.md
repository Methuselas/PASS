---
object_id: DRILL_generalize_a_rust_function_without_overconstraining
object_type: drill
name: Generalize a Rust Function Without Overconstraining It
library_path: [software-engineering, languages, rust, generics]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, generics, trait_bounds, borrowing, refactoring]
cross_links:
- rel: teaches
  target_object_id: PAT_constrain_rust_generics_by_required_behavior
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
target_skill: deriving minimal Rust trait bounds and ownership requirements from a generic implementation
references: []
variants: []
---

# Generalize a Rust Function Without Overconstraining It

## Practice Task
Merge two duplicated slice-processing functions into one generic Rust function, then remove a convenience bound that excludes a non-copyable type.

## Target Skill
Deriving minimal behavioral and ownership constraints from the operations a generic implementation actually performs.

## Setup
Prepare two functions that return an owned maximum from a documented nonempty slice by copying elements through the same comparison loop. Use different copyable element types, plus a third test type that is comparable but not `Copy`.

## Instructions
1. State the nonempty-input precondition, then compile and run the two concrete functions on representative inputs, recording their outputs as the behavior to preserve.
2. Replace them with one generic function and record the first compiler diagnostic produced by the unbounded body.
3. Add the behavioral bound needed for comparison, compile again, and record the remaining ownership diagnostic separately.
4. Produce one working version that returns an owned item by declaring the `Copy` capability it consumes.
5. Produce a second working version that returns a reference into the input and therefore does not consume or clone an item.
6. Compile both versions with the original copyable types and compile the borrowed version with the non-copyable comparable type.
7. Record which bound was removed, why the borrowed result makes that removal sound, and when the owned version would still be preferable.

## Success Check
- The original outputs and the outputs of both generic versions agree on nonempty inputs; merely compiling the definitions does not demonstrate preserved behavior.
- The nonempty-input precondition remains explicit at the call boundary; silently indexing an empty slice is not accepted as an unexamined edge.
- The first diagnostic is distinguished from the second: one identifies a missing comparison capability, while the other identifies an attempted move from borrowed storage.
- The borrowed version compiles and runs with the non-copyable comparable type. Adding `Clone` and cloning every item is the plausible near-miss: it makes the example compile while preserving an avoidable capability and cost.
- The report names the removed ownership bound and connects its removal to returning a reference rather than to the comparison behavior.
- The final choice between the owned and borrowed interfaces includes a reason based on caller ownership needs, not a preference for shorter syntax.

## Common Failures
- Adding `Copy` immediately and missing that comparison and ownership are separate constraints.
- Exercising only copyable primitives, which cannot reveal whether the generic interface is unnecessarily narrow.
- Returning a reference without checking that it points into the caller-provided slice.

## Notes
This exercise teaches the decision to constrain Rust generics by required behavior. The staged compiler errors expose two independent assumptions hidden by the concrete version, and the exercise succeeds when the implementation preserves comparison while making copying an explicit interface choice instead of an accidental requirement.
