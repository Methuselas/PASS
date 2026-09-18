---
object_id: PAT_choose_an_explicit_unreal_tool_world
object_type: pattern
name: Choose an Explicit Unreal Tool World
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- editor_tools
cross_links: []
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Choose an Explicit Unreal Tool World

## Pattern Rule
**IF** an Unreal editor tool queries or changes actors
**THEN** choose the intended editor or play world explicitly and scope every target to that world.

## Do
- Use the editor world context for persistent level authoring.
- Treat a play-world debug operation as a separate deliberate contract; its changes normally disappear when play ends.
- Validate the world, level and target membership before changing data.
- For viewport placement, resolve a world-space point rather than treating a two-dimensional click as a world position.

## Don't
- Don't let the current global world silently choose a PIE target.
- Don't use actors from a different world merely because their class matches.

## Checklist
- Does each target belong to the declared world?
- Are invalid or foreign worlds rejected before mutation?
- Does the placement point have the intended world-space meaning?

## Notes
World choice precedes actor search, selection, placement and property changes. Debugging a running simulation and authoring a persistent level are different operations.
