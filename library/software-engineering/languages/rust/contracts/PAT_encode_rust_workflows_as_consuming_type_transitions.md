---
object_id: PAT_encode_rust_workflows_as_consuming_type_transitions
object_type: pattern
name: Encode Rust Workflows as Consuming Type Transitions
library_path: [software-engineering, languages, rust, contracts]
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_make_misuse_impossible_by_removing_invalid_states
tags: [rust, typestate, state_machine, ownership, api_design]
cross_links:
- rel: related_to
  target_object_id: PAT_construct_rust_validated_types_through_the_only_open_boundary
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Encode Rust Workflows as Consuming Type Transitions

## Pattern Rule
**IF** a Rust workflow has a small stable set of states whose available operations differ and callers can accept the type changing at each step
**THEN** represent each state with a distinct type and make legal transitions consume the old value and return the next type
**ELSE** use a runtime state representation when one stable outer type, runtime-selected states, or open extension is more important than compile-time transition exclusion.

## Do
- Put only the operations legal in a state on that state's type, so an invalid call is absent rather than checked and ignored at runtime.
- Take `self` by value for a one-way transition and move the shared payload into the returned state type.
- Keep state fields private and expose only constructors and transitions that preserve the workflow graph.
- Let callers shadow the binding with the returned state when a linear workflow should read as a sequence of transformations.
- Use a runtime enum or private `dyn State` object instead when values in different states must share one storage type or change state behind a stable public handle.

## Don't
- Don't leave the old state usable after a transition that logically consumes it.
- Don't provide methods that return placeholder values for operations that should be impossible in the current state.
- Don't force typestate onto a highly dynamic or externally extensible workflow if it makes storage and composition harder than the invalid transitions it removes.
- Don't hide a temporary missing-state sentinel inside the implementation without ensuring every exit path restores a valid state.

## Checklist
- Which operations exist in each state?
- Can the state set be represented as stable compile-time types?
- Does each transition consume the previous state and preserve the shared payload?
- Can outside code construct or mutate a state illegally?
- Do callers need one stable type or heterogeneous storage across states?

## Notes
Consuming transitions turn the workflow graph into the type graph: a draft value has draft operations, a review transition produces a review value, and only an approved value exposes published behavior. A runtime state object centralizes behavior behind one outer type and supports dynamic substitution, but invalid transitions must then be handled by runtime policy. The two designs trade caller-visible types for compile-time exclusion; neither is universally preferable.
