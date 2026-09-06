---
object_id: PAT_trace_foundational_design_changes_through_dependent_work
object_type: pattern
name: Trace Foundational Design Changes Through Dependent Work
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
- design
- dependencies
- revision
- change-impact
cross_links:
- rel: related_to
  target_object_id: PAT_propagate_world_assumptions_along_actual_dependencies
- rel: related_to
  target_object_id: PAT_repair_the_smallest_correct_owner_of_a_confirmed_defect
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Trace Foundational Design Changes Through Dependent Work

## Pattern Rule
**IF** evidence changes a foundational game assumption, requirement, system contract, interface, or other design decision with downstream dependents
**THEN** identify the systems, content, assumptions, interfaces, and production requirements that depend on it and review those dependents before continuing work that assumes the old foundation
**ELSE** keep the revision local when no downstream dependency actually consumes the changed decision.

## Do
- Name the changed foundation before editing downstream material so the impact search has a concrete starting point.
- Trace which systems, content domains, assumptions, interfaces, and production requirements consume that foundation.
- Stop or defer dependent implementation when the known change makes further work against the old assumption predictably disposable.
- Review affected dependents for required revision rather than assuming a local fix automatically propagates through the design.
- Keep unaffected work outside the repair radius when it does not actually depend on the changed decision.

## Don't
- Change a foundation and continue downstream implementation as though existing dependents were automatically still valid.
- Treat thematic proximity as dependency; review what actually consumes the changed assumption.
- Rewrite unrelated material merely because it sits near an affected system in the document or library.
- Keep producing knowingly disposable dependent work while the new foundation is unresolved.

## Checklist
- The foundational change is stated in a form that makes its dependents identifiable.
- Every affected system, content domain, interface, assumption, or production requirement has been named or deliberately ruled out.
- Dependent work is reviewed before additional work compounds the obsolete assumption.
- Unaffected areas remain untouched unless a real dependency is found.
- The project can explain which downstream decisions changed because of the foundation and which did not.

## Notes
A foundational revision is expensive because of what already depends on it, not because the sentence describing it is large. Treat the design as a dependency surface: change the owner, find the consumers, and review the affected radius before building more on an obsolete assumption. A living game design specification can make those dependencies recoverable, but the change-impact decision remains useful even when the project uses a lighter form of specification.
