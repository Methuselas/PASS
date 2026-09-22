---
object_id: PAT_classify_particle_changes_as_emission_simulation_or_rendering
object_type: pattern
name: Classify Particle Changes as Emission, Simulation, or Rendering
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 0 design
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

# Classify Particle Changes as Emission, Simulation, or Rendering

## Pattern Rule
**IF** you are deciding where a particle-system change belongs
**THEN** classify the change by responsibility: emission creates particles, simulation changes their behavior over time, and rendering determines how the simulated particles are displayed.

## Do
- Put spawn count, spawn timing, and spawn location concerns under emission.
- Put movement, forces, lifetime-driven scale/color, and other behavioral evolution under simulation.
- Put sprite, mesh, ribbon, and other display choices under rendering.

## Don't
- Don't change rendering to solve a simulation problem or simulation logic to solve a renderer-only problem.
- Don't mix responsibilities when a module or stage already has a clear execution purpose.

## Checklist
- The requested change is assigned to one primary responsibility.
- The chosen module/stage matches that responsibility.

## Notes
Niagara separates particle creation, behavioral evolution, and visual representation so each can be reasoned about independently.
