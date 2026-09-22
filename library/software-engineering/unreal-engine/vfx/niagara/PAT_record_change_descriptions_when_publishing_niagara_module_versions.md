---
object_id: PAT_record_change_descriptions_when_publishing_niagara_module_versions
object_type: pattern
name: Record Change Descriptions When Publishing Niagara Module Versions
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

# Record Change Descriptions When Publishing Niagara Module Versions

## Pattern Rule
**IF** a new reusable Niagara module version is published
**THEN** record a concise Change Description that explains what changed for downstream users.

## Do
- Describe the behavior/interface difference that matters to adopters.
- Keep the description with the module version metadata.

## Don't
- Do not create parallel versions that are indistinguishable to consumers.

## Checklist
- A consumer can tell why the new version exists before adopting it.

## Notes
The module versioning workflow includes an explicit Change Description field.
