---
object_id: PAT_construct_top_down_cave_entrance_from_cliff_inset_and_recessed_darkness
object_type: pattern
name: Construct Top-Down Cave Entrance From Cliff Inset and Recessed Darkness
library_path:
- art
- cartography
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- cartography
- terrain
- cave
- cliff
- pictorial-symbols
- depth
cross_links:
- rel: related_to
  target_object_id: PAT_construct_pictorial_sea_arch_from_projecting_cliff_and_inset_opening
- rel: related_to
  target_object_id: PAT_construct_pictorial_chasm_from_opposing_cliff_rims_and_deepening_interior
- rel: related_to
  target_object_id: PAT_create_depth_sequence_with_overlap
- rel: related_to
  target_object_id: PAT_ground_contacts_with_occlusion_shadow
confidence: high
references: []
variants: []
---

# Construct Top-Down Cave Entrance From Cliff Inset and Recessed Darkness

## Pattern Rule
**IF** a pictorial map viewed from above needs a cave entrance to read as a passage entering a cliff or raised terrain
**THEN** interrupt the cliff edge with a clear inward recess, wrap the surrounding cliff structure around that recess, and concentrate the strongest depth cue inside the sheltered mouth so the opening reads as continuing beneath the terrain rather than as a flat mark on its surface
**ELSE** keep the cliff edge continuous when no recessed passage is intended

## Do
- Establish the large cliff edge or raised-terrain boundary first, then bend that boundary inward where the cave mouth will enter the landform.
- Build visible cliff layers or returning face contours around the inset so the ground above and the exposed rock face read as one mass wrapping around a recessed opening.
- Keep the cave-mouth shape simple and readable before adding cracks, grass, stones, or small rock texture.
- Let broken or layered rock marks follow the established cliff surfaces instead of crossing them as unrelated decoration.
- When dark marks or tone are used inside the entrance, keep the greatest concentration in the sheltered interior and reduce it toward the exposed mouth or surrounding ground so the recession supports the construction.
- Add nearby rocks or vegetation only after the entrance reads, and keep those transition details subordinate to the cave mouth.
- Keep directional lighting, cast shadows, and highlights subordinate to the accepted cliff-and-recess structure rather than using rendering to invent the opening after the fact.

## Don't
- Do not leave the cliff contour structurally unbroken and rely on a dark patch alone to represent the cave; the entrance needs an actual recess in the terrain boundary.
- Do not turn the mouth into an isolated freestanding arch when the intended feature is a passage entering the cliff beneath the surrounding ground.
- Do not detail cracks, grass, stones, or sediment before the inset and its surrounding cliff structure are legible.
- Do not keep interior darkness uniformly strong across the exposed ground; let the strongest dark remain associated with the sheltered recess when darkness is used as a depth cue.
- Do not let surface marks ignore the direction of the cliff layers they are meant to describe.

## Checklist
- The cliff or raised-terrain boundary visibly turns inward at the cave entrance rather than continuing straight behind a symbol.
- Surrounding cliff layers or face returns make the opening feel embedded in one terrain mass.
- The mouth remains recognizable when small stones, grass, cracks, color, and decorative texture are ignored.
- Any interior darkening is strongest in the sheltered recess and weakens toward more exposed ground rather than flattening the whole area into one value.
- Surface marks reinforce the established cliff direction.
- The feature reads as a passage entering beneath terrain, not as a pierced freestanding arch or a fissure between two opposing rims.

## Notes
A cave entrance is a recessed-edge problem. The cliff boundary must first fold inward around the mouth so the viewer reads a passage entering beneath the terrain. Layered or broken rock contours then clarify the surrounding cliff mass. Darkness, stippling, hatching, or another value cue can strengthen the sheltered interior by concentrating toward the recess and easing outward, but rendering is support rather than the owner of the topology. This differs from a sea arch, which is a through-opening inside projecting rock, and from a chasm, which is an opening between opposing ground rims.
