---
object_id: PAT_check_the_niagara_plugin_when_niagara_asset_options_are_missing
object_type: pattern
name: Check the Niagara Plugin When Niagara Asset Options Are Missing
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
- vfx
cross_links: []
reference:
  source_title: Build Stunning Real-time VFX with Unreal Engine 5
  author: Hrishikesh Andurlekar
confidence: high
references: []
variants: []
---

# Check the Niagara Plugin When Niagara Asset Options Are Missing

## Pattern Rule
**IF** Niagara asset creation options are missing in an Unreal Engine 5 project
**THEN** verify that the Niagara plugin is enabled before troubleshooting the asset workflow itself.

## Do
- Open Edit > Plugins and locate Niagara.
- Enable Niagara when the expected asset types are unavailable, then restart if Unreal requests it.

## Don't
- Do not assume a missing menu entry means the project or assets are corrupted.

## Checklist
- Niagara is enabled or an explicit plugin-state cause has been ruled out.

## Notes
Niagara is normally enabled by default in UE5, so plugin state is a bounded first check.
