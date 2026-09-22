---
object_id: PAT_change_niagara_appearance_without_rewriting_simulation
object_type: pattern
name: Change Niagara Appearance Without Rewriting Simulation
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- niagara
- vfx
cross_links: []
reference:
  source_title: Build Stunning Real-time VFX with Unreal Engine 5
  author: Hrishikesh Andurlekar
confidence: high
references: []
variants: []
---

# Change Niagara Appearance Without Rewriting Simulation

## Pattern Rule
**IF** the simulated particle motion is correct but the particles should be represented differently
**THEN** change or add renderer modules instead of rewriting the simulation.

## Do
- Reuse the same simulated particle data with sprite, mesh, ribbon, or other renderers as appropriate.
- Add multiple renderers when one simulation needs more than one visible representation.
- Keep behavioral calculations independent from presentation where possible.

## Don't
- Don't duplicate simulation logic just to change how the particles look.
- Don't assume one emitter can have only one renderer.

## Checklist
- Changing the renderer leaves the intended particle motion unchanged.
- The selected renderer produces the required visual representation.

## Notes
Niagara rendering is independent of simulation, so the same particle state can be displayed in different forms.
