---
object_id: PAT_lower_unreal_k2_exec_outputs_to_typed_delegate_events
object_type: pattern
name: Lower Unreal K2 Exec Outputs to Typed Delegate Events
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- k2_nodes
- delegates
- compiler
cross_links:
- rel: related_to
  target_object_id: PAT_expand_custom_unreal_k2_nodes_with_verified_pin_contracts
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Lower Unreal K2 Exec Outputs to Typed Delegate Events

## Pattern Rule
**IF** a custom K2 node presents asynchronous delegate callbacks as ordinary execution outputs
**THEN** lower each connected output to a uniquely named internal event whose signature is derived and checked against the destination delegate pin, while leaving unconnected optional callbacks absent.

## Do
- Keep the runtime registration function Blueprint-callable but mark it internal-use-only so graph authors enter through the lifecycle-shaped custom node.
- Represent callback parameters as typed dynamic delegates. Use auto-created reference terms only for callbacks that are genuinely optional; required lifecycle outputs should fail compilation when unconnected.
- During expansion, create an event node only for a connected execution output. Give it a deterministic graph-unique function name based on stable node identity and pin identity.
- Derive or validate the event signature from the actual delegate property accepted by the destination pin. Report a compiler error when parameter shape, const/reference flags or return semantics differ.
- Transfer the user's execution links to the internal event continuation, connect the event's delegate output to the runtime call and verify both connection responses.
- Preserve source mapping and diagnostic context so a failure in the generated event points back to the visible custom node and pin.
- Verify compilation after duplication, paste, reconstruction and rename; include two instances of the node in one graph to exercise name uniqueness.

## Don't
- Don't hard-code a delegate signature name by manually stripping a prefix when reflection can identify the required signature.
- Don't create hidden event functions for unused optional outputs.
- Don't expose the internal registration call as a competing public node.
- Don't let generated event names collide after copy/paste or node reconstruction.

## Checklist
- Does every connected exec output generate exactly one signature-compatible internal event?
- Are unconnected optional outputs absent without leaving invalid delegate inputs?
- Are generated names unique and stable enough for compilation and reconstruction?
- Do compile diagnostics identify the visible node and offending output pin?

## Notes
The visible exec pin is syntax sugar over a delegate binding. Correct lowering must preserve the delegate's full type contract and the graph author's expected execution path.
