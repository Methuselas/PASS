---
object_id: PAT_generate_repeated_level_content_in_the_construction_script
object_type: pattern
name: Generate Repeated Level Content in the Construction Script
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- construction_script
- procedural_generation
cross_links:
- rel: related_to
  target_object_id: PAT_use_construction_script_for_per_instance_configuration
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Generate Repeated Level Content in the Construction Script

## Pattern Rule
**IF** a level needs repeated content laid out in a regular pattern (rows, grids, evenly spaced copies) and the level designer should be able to tune the layout per placed instance
**THEN** generate the content in the Construction Script with nested For Loops over Instance Editable parameters, computing each copy's offset as the loop index multiplied by a spacing value, instead of placing every copy by hand.

## Do
- Expose the layout knobs (mesh, count per row, number of rows, spacing) as Instance Editable variables so each placed instance can be tuned in the Level Editor.
- Drive the outer loop with one count variable and the inner loop with another, so rows and columns stay independent.
- Compute each instance's position as loop index × spacing and feed it into the instance transform, so the spacing variables directly control the layout.
- Store a per-row offset in a local variable so the inner loop reuses the same value for every instance in that row.

## Don't
- Don't place each copy manually in the level when a loop can generate them — manual placement does not scale and cannot be re-tuned per instance.
- Don't put the generation in the Event Graph or Begin Play; the Construction Script is what re-runs when a designer changes an instance's parameters in the editor.

## Checklist
- Changing a count or spacing variable on a placed instance in the Level Editor regenerates the layout without playing the level.
- Two instances of the same class can show different layouts at the same time.
- The generation logic lives in the Construction Script, not the Event Graph.

## Notes
Procedural generation replaces repetitive manual placement with a script that lays out copies from a few parameters. The Construction Script is the right home because it runs when the instance is added to the level and re-runs whenever its Instance Editable properties change, so the designer gets live feedback. The index × spacing formula is what turns a couple of spacing variables into a full grid; small parameter changes produce very different layouts, which is the point of making the knobs Instance Editable.
