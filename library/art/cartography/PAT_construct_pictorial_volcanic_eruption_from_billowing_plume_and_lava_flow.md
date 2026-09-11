---
object_id: PAT_construct_pictorial_volcanic_eruption_from_billowing_plume_and_lava_flow
object_type: pattern
name: Construct Pictorial Volcanic Eruption From Billowing Plume and Lava Flow
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
- volcano
- eruption
- smoke
- lava
- glow
- regional-maps
cross_links:
- rel: related_to
  target_object_id: PAT_render_luminescent_emission_over_darker_base
- rel: related_to
  target_object_id: PAT_control_edge_hardness_from_form_light_and_focus
confidence: high
references: []
variants: []
---

# Construct Pictorial Volcanic Eruption From Billowing Plume and Lava Flow

## Pattern Rule
**IF** a pictorial volcano needs to read as actively erupting rather than merely dormant
**THEN** establish a narrow-base smoke mass that billows and drifts above the vent, break that mass into overlapping cloud lobes, block lava as branching flows and upward spray from the crater, then model the plume and lava with separate shadow, highlight, and local-glow passes while preserving their original large shapes

## Do
- Begin the plume with one simple envelope that sets its overall size, width growth, and wind-driven drift before drawing individual cloud bumps.
- Keep the plume narrower where it leaves the crater and broader higher up so the smoke expands rather than reading as a rigid column.
- Replace the guide envelope with broken, overlapping cloud contours whose overlaps create front-and-back billows without losing the original mass.
- Block the lava as broad flow shapes descending from the crater before outlining small channels; include a few upward streaks or sprays so the vent reads as active.
- Add interior cloud arcs and lava contour lines only after the main smoke and flow silhouettes are established, using them to show billowing volume and movement.
- Build plume shadows broadly first, then deepen the portions most obscured from the chosen light source instead of shading every lobe independently from scratch.
- Add broad highlights before sharper accents; reserve the crispest light marks for the lava where a hotter, more luminous read is needed.
- Let the lava act as a local secondary light source by bleeding a restrained warm influence onto the crater rim and nearby mountain surfaces.
- Preserve enough dark structure around the lava and vent that the final glow reads as emitted light rather than as a flat bright color.

## Don't
- Do not start with many disconnected smoke puffs before establishing the plume's overall envelope and drift.
- Do not make the plume equally wide from crater to top; a uniform tube loses the sense of hot material billowing outward.
- Do not outline tiny lava rivulets before the major downhill flow masses are placed.
- Do not add cloud detail until the large plume silhouette already reads; detail should subdivide the mass, not invent it piecemeal.
- Do not treat the lava as bright paint that has no lighting effect on the crater or surrounding rock when the scene calls for visible glow.
- Do not let highlight effects erase the shadow structure that gives the plume and mountain their volume.

## Checklist
- The smoke plume has a clear large envelope, narrower at the vent and fuller above, with a readable drift direction.
- Overlapping cloud contours create billowing depth while preserving one coherent plume mass.
- Lava originates at the crater, descends in readable flow masses, and includes enough vent activity to signal eruption.
- Interior detail clarifies cloud volume and lava movement without fragmenting either silhouette.
- Plume shadows and highlights follow a consistent light direction and retain broad-to-specific value structure.
- The lava reads as emissive where intended because nearby surfaces receive a restrained warm influence.
- The eruption remains legible at map scale before small texture and glow effects are considered.

## Notes
An eruption is easiest to control when its two dynamic systems are solved at large scale first: the expanding, drifting smoke envelope above the crater and the lava flow spreading down the mountain. Broken overlaps turn the smoke envelope into billowing volume; broad lava blocks establish downhill movement before smaller channels are described. Rendering then follows the established forms. Shadow and highlight passes model the plume, while the lava can additionally behave as a local emitter that warms nearby rock. Exact blend modes and color values are optional implementations rather than the durable construction logic.
