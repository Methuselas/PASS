---
object_id: PAT_cross_unreal_blueprint_wildcards_with_reflection_safe_thunks
object_type: pattern
name: Cross Unreal Blueprint Wildcards with Reflection-Safe Thunks
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: PAT_cross_a_c_boundary_with_only_what_c_can_express
tags:
- unreal_engine
- blueprints
- custom_thunk
- reflection
- memory_safety
cross_links:
- rel: related_to
  target_object_id: PAT_shape_blueprint_function_nodes_for_graph_use
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Cross Unreal Blueprint Wildcards with Reflection-Safe Thunks

## Pattern Rule
**IF** a Blueprint-callable operation genuinely needs wildcard values that ordinary reflected signatures cannot express
**THEN** keep its custom thunk as a narrow VM-boundary adapter, validate the reflected property contract, and perform every initialize, copy, mutation and cleanup through the matching `FProperty` semantics.

## Do
- First verify that a normal typed function, template-generated family or custom K2 expansion cannot provide the interface with less VM coupling. Use `CustomThunk` only when runtime wildcard dispatch is the essential capability.
- Keep the declared UFUNCTION signature, wildcard metadata, `DECLARE_FUNCTION` name and stack-read order synchronized. Treat parameter order and reference direction as an ABI contract.
- Reset and step the `FFrame` deliberately, capture both `MostRecentProperty` and its address immediately, cast to the expected property class and fail the array/context operation when either is invalid.
- Finish parameter decoding before native work. Wrap the implementation call in the native profiling scope so Blueprint and native timings remain attributable.
- Delegate container layout and element lifetime to helpers such as `FScriptArrayHelper` and the container's inner `FProperty`. Use property initialization, copy and destruction operations appropriate to source and destination ownership.
- Validate indices, counts, empty containers, type dependencies and writable output addresses. Initialize every output on failure and emit a stable Blueprint execution diagnostic.
- Mark a mutated reflected property dirty through the engine-supported path when replication or change tracking depends on it.
- Mirror engine thunk behavior unless a deliberate deviation is supported by tests across all relevant property categories and engine versions.

## Don't
- Don't treat a wildcard address as trivially copyable memory; strings, object references, structs, arrays and destructor-bearing values require reflected lifetime operations.
- Don't remove an engine temporary buffer or initialization step because a narrow benchmark appears faster without proving aliasing, reference, initialization and cleanup equivalence.
- Don't let the never-called declaration body become a second implementation path; fail loudly if native code calls it directly.
- Don't continue decoding or mutating after the reflected property type fails validation.

## Checklist
- Does metadata make every wildcard and type-dependent parameter relationship explicit?
- Are stack values consumed in exactly the declared order and validated before use?
- Are destination values initialized and copied with the correct `FProperty` operation on every branch?
- Has the thunk been tested with nontrivial, reference-bearing and empty/error cases, not only integers?

## Notes
The thunk owns translation from Blueprint VM state to a small generic native function. Business logic belongs behind that boundary; VM macros and raw addresses do not.
