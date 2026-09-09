---
object_id: PAT_control_brush_ink_tone_with_moisture_and_pressure
object_type: pattern
name: Control Brush-Ink Tone With Dilution, Load, and Pressure
library_path:
- art
- drawing
- rendering
stage_binding: 4 final
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: medium
foundation_object_id: PAT_consolidate_resolved_form_with_tone
tags:
- brush_ink
- value
- dry_brush
- wash
- dilution
- pressure
cross_links:
- rel: supports
  target_object_id: PAT_render_material_from_optical_response
reference:
  source_title: The Art of Animal Drawing
  author: Ken Hultgren
confidence: high
references: []
variants:
- variant_id: VAR_build_transparent_ink_tone_with_diluted_layered_washes
  variant_name: Build Transparent Ink Tone With Diluted Layered Washes
  variant_basis: method_sequence
  difference_from_foundation: Establish a lighter transparent wash with diluted ink, preserve protected neighboring areas, let the passage dry, then deepen selected regions with later transparent passes.
  when_to_use: Use when tone needs to build gradually through transparent brush-ink layers rather than one opaque or dry-brush statement.
  when_not_to_use: Do not use when the passage must remain dry, broken, or sharply separated without wash spread.
  absorbed_from_object_id: none
---

# Control Brush-Ink Tone With Dilution, Load, and Pressure

## Pattern Rule
**IF** a brush-and-ink passage needs controlled tone, broken texture, or transparent wash variation without changing medium
**THEN** control ink concentration, brush load or moisture, pressure, and the wet region independently, testing the brush state before committing the passage
**ELSE** use the value controls native to the chosen medium rather than imitating brush-ink behavior mechanically

## Do
- Dilute ink when a lighter transparent wash is needed instead of relying only on a smaller brush load.
- For a drier broken mark, work excess ink out on scratch paper before taking the brush to the drawing.
- Treat dilution, brush load, and contact pressure as separate controls; changing one does not automatically solve the others.
- Wet or brush only the region intended to receive a wash when a clean neighboring boundary must be preserved.
- Test strokes or small wash passages before the final application so the brush arrives at the drawing at the intended strength and load.

## Don't
- Do not expect one fixed concentration and brush load to produce every value and texture.
- Do not use a saturated brush when the goal is the broken paper-catching quality of dry brush.
- Do not flood across a boundary that needs to stay clean.
- Do not scrub randomly to manufacture texture; the mark should still support the intended form or value structure.

## Checklist
- Ink concentration, brush load, and pressure can each be changed without being confused for the same control.
- Dry passages leave intentional paper breaks rather than accidental gaps.
- Wash passages stay inside their intended region when a protected boundary matters.
- A tested stroke or wash closely predicts the mark that appears on the drawing.
- Texture or wash variation does not destroy the larger light-and-form statement underneath it.

## Notes
Dry-brush and diluted-wash behavior belong to the same brush-ink medium but use different control states. The variant `VAR_build_transparent_ink_tone_with_diluted_layered_washes` starts with a lighter diluted wash, lets that passage dry, then adds localized transparent passes where stronger value definition is needed.
