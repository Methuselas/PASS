---
object_id: PAT_use_niagara_stacks_for_routine_behavior_and_graphs_for_custom_logic
object_type: pattern
name: Use Niagara Stacks for Routine Behavior and Graphs for Custom Logic
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- niagara
- modules
- graphs
- vfx
cross_links: []
reference:
  source_title: Build Stunning Real-time VFX with Unreal Engine 5
  author: Hrishikesh Andurlekar
confidence: high
references: []
variants: []
---

# Use Niagara Stacks for Routine Behavior and Graphs for Custom Logic

## Pattern Rule
**IF** you are deciding where Niagara particle behavior should be authored
**THEN** use the module stack for straightforward particle behavior and move into node-graph module logic when the effect needs custom or more flexible behavior.

## Do
- Start with stack modules when an existing module expresses the behavior.
- Use graph-authored Niagara modules when stack configuration alone cannot express the required logic.
- Keep the stack readable while concentrating custom calculations inside modules.

## Don't
- Don't build custom graph logic when a stock stack module already expresses the behavior clearly.
- Don't force complex custom behavior into a flat stack of unrelated workaround modules.

## Checklist
- Routine behavior remains visible as a readable module stack.
- Custom behavior is isolated inside graph-authored modules instead of obscuring the stack.

## Notes
When custom graph behavior should be reusable beyond one particle system, put that graph in a separate Niagara Module Script asset rather than keeping the custom logic embedded in a single system.

Use Dynamic Inputs as the parameter-level extension step when a stock module exists but one parameter needs function-driven or composed logic; escalate to a custom module graph when the behavior itself needs custom reusable logic.

Niagara deliberately combines Cascade-like stack readability with the power of Unreal node graphs.
