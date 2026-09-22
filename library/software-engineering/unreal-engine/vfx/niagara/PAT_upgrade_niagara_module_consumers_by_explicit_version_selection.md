---
object_id: PAT_upgrade_niagara_module_consumers_by_explicit_version_selection
object_type: pattern
name: Upgrade Niagara Module Consumers by Explicit Version Selection
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 4 final
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

# Upgrade Niagara Module Consumers by Explicit Version Selection

## Pattern Rule
**IF** multiple Niagara module versions coexist
**THEN** move each consumer to the newer version explicitly when that consumer is ready.

## Do
- Leave known-good consumers on their current version until validated.
- Use the module version selector to opt a consumer into the new implementation.
- Verify rollback by switching back when needed.

## Don't
- Do not assume creating a newer version automatically upgrades every consumer.

## Checklist
- Each consumer runs the intended module version.

## Notes
Per-consumer selection permits controlled adoption and rollback.
