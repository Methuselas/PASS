---
object_id: PAT_keep_game_design_specification_living_and_dependency_aware
object_type: pattern
name: Keep the Current Game Design Specification Living
library_path:
- game-design
- foundations
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- gdd
- specification
- revision
cross_links:
- rel: related_to
  target_object_id: PAT_trace_foundational_design_changes_through_dependent_work
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Keep the Current Game Design Specification Living

## Pattern Rule
**IF** a game has multiple interacting systems, content domains, interfaces, or production requirements
**THEN** keep a recoverable game design document or equivalent specification that records the current intended design, revise it when accepted evidence changes the design, and preserve recoverable versions through major revisions
**ELSE** use a lighter recoverable specification that still makes the current design and its dependencies explicit.

## Do
- Record the intended game's fundamentals before they disappear into scattered notes or hidden designer memory.
- Include enough specification to establish the intended player and experience, core activity, major systems, player capabilities, important resources or progression, challenge structures, components or interfaces, major content domains, dependencies, and current production-facing design requirements where relevant.
- Revise the specification when evidence shows that the design itself should change instead of treating the document as an immutable promise made before testing.
- Preserve recoverable versions of both the game and the matching specification through major revisions.
- Keep the document focused on the current design rather than turning it into a speculative encyclopedia of every idea the project may someday contain.

## Don't
- Treat the game design document (GDD) as an immutable prophecy that cannot change after development begins.
- Treat the GDD as a novel or setting encyclopedia full of features the current game may never need.
- Allow fundamental requirements to remain only in the creator's head.
- Overwrite the only recoverable version of the specification during a major redesign.

## Checklist
- The current intended design is recorded somewhere recoverable.
- The specification changes when the design changes rather than forcing later evidence back into an obsolete plan.
- Prior game and specification states remain recoverable through major revisions.
- The specification describes the current game rather than accumulating every possible future feature.

## Notes
A living design specification is not valuable because it is long. It is valuable because it externalizes the current intended game and changes when the game changes. Preserve recoverable versions through major revisions, keep speculative ideas out of the current contract, and let evidence outrank an obsolete plan. Dependency impact from a foundational change is a separate decision owned by **Trace Foundational Design Changes Through Dependent Work**.
