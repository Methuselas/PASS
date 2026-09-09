---
object_id: PAT_switch_from_pictorial_to_simplified_settlement_icons_when_map_scale_or_density_demands_it
object_type: pattern
name: Switch From Pictorial to Simplified Settlement Icons When Map Scale or Density Demands It
library_path:
- art
- cartography
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- cartography
- settlements
- icons
- abstraction
- scale
- density
cross_links: []
confidence: high
references: []
variants: []
---

# Switch From Pictorial to Simplified Settlement Icons When Map Scale or Density Demands It

## Pattern Rule
**IF** a map covers enough area or contains enough settlements that pictorial settlement artwork becomes crowded or difficult to read
**THEN** reduce settlements to compact simplified symbols that preserve the class distinctions the map needs while discarding architectural detail that no longer survives at map scale

## Do
- Judge the settlement layer at the intended map scale.
- Simplify when pictorial detail begins to crowd neighboring information or lose readability.
- Keep only distinctions that matter to the map’s information system.
- Retain pictorial treatment when its detail still reads clearly and a denser symbol vocabulary is unnecessary.

## Don't
- Do not keep miniature architecture solely because it was used on a less dense map.
- Do not simplify away distinctions the reader still needs.
- Do not mix abstraction levels arbitrarily across equivalent settlement classes.

## Checklist
- Simplified symbols remain legible at the map scale.
- Required settlement classes remain distinguishable.
- The location layer no longer depends on architectural micro-detail.
- Equivalent settlements use a coherent representation level.

## Notes
Settlement representation can change with map scale and information density. Simplification is a cartographic abstraction choice, not a statement that pictorial symbols are inherently inferior.
