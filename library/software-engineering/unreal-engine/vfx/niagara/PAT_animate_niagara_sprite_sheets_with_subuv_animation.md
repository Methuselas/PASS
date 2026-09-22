---
object_id: PAT_animate_niagara_sprite_sheets_with_subuv_animation
object_type: pattern
name: Animate Niagara Sprite Sheets with SubUV Animation
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 3 rough
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

# Animate Niagara Sprite Sheets with SubUV Animation

## Pattern Rule
**IF** particles use a flipbook or sprite-sheet material
**THEN** configure the renderer sub-image grid and use SubUV Animation over the intended frame range.

## Do
- Assign a material designed for the sprite sheet.
- Set Sub Image Size to the sheet's row/column layout.
- Add SubUV Animation and choose the start/end frames to play.

## Don't
- Do not assume Niagara can infer the sprite-sheet grid or desired frame range.

## Checklist
- Particle sprites animate through the expected cells in order.

## Notes
The frame range may use the full sheet or a deliberate subset.
