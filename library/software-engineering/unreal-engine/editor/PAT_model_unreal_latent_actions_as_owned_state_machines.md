---
object_id: PAT_model_unreal_latent_actions_as_owned_state_machines
object_type: pattern
name: Model Unreal Latent Actions as Owned State Machines
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: PAT_reach_for_a_coroutine_when_work_must_pause_and_resume
tags:
- unreal_engine
- blueprints
- latent_actions
- lifetime
- state_machines
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

# Model Unreal Latent Actions as Owned State Machines

## Pattern Rule
**IF** a Blueprint operation must suspend graph execution across frames
**THEN** represent it as a finite latent-action state machine whose manager identity, referenced-object lifetimes, completion paths and continuation outputs are explicit.

## Do
- Enter through a Blueprint-callable function with `Latent`, a named `LatentInfo` parameter and a `WorldContext` when the owning world is not otherwise explicit.
- Resolve the world through the context object and register with that world's `FLatentActionManager`. Use callback target plus UUID as the operation identity and document whether a duplicate call is ignored, replaces the old action or joins it.
- Store the execution function, linkage and callback target needed to resume the graph. Keep UObject references weak unless another documented owner guarantees their lifetime; validate them before every use.
- Express start, running, success, cancellation and failure as explicit states. Set an expanded enum or other result before triggering the corresponding continuation.
- Finish exactly once. Every invalid world, destroyed dependency, unbound optional delegate, cancellation and normal result needs a deterministic terminal policy.
- Use `TriggerLink` only when the action continues and `FinishAndTriggerIf` when the selected continuation also ends it. Use `DoneIf` only when silent completion is part of the public contract.
- Prefer event or callback completion when available. If polling each frame is necessary, keep `UpdateOperation` bounded and free of blocking work.

## Don't
- Don't retain raw UObject pointers inside `FPendingLatentAction` as though garbage collection can see them.
- Don't call an optional delegate with `Execute()` before checking `IsBound()`; choose and document the empty-input behavior.
- Don't let repeated calls with the same latent identity create ambiguous parallel operations.
- Don't expose a latent node for work that can complete synchronously or whose lifetime belongs to a better engine subsystem.

## Checklist
- Which world and callback target own the action, and what happens when either disappears?
- Is duplicate invocation behavior stable for the same callback target and UUID?
- Can every running state reach exactly one terminal outcome?
- Are all captured UObject and delegate references validated at the moment of use?

## Notes
A latent action is not a UObject and not an actor tick. Its safety comes from manager registration, weak lifetime edges and a complete state-transition contract.
