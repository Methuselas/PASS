---
object_id: PAT_use_a_data_table_for_data_driven_gameplay
object_type: pattern
name: Use a Data Table for Data-Driven Gameplay
library_path:
- software-engineering
- unreal-engine
- blueprints
- data-structures
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- data_structures
- data_tables
- data_driven
cross_links:
- rel: related_to
  target_object_id: PAT_use_a_structure_to_group_related_variables
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Use a Data Table for Data-Driven Gameplay

## Pattern Rule
**IF** game data needs to be frequently modified and balanced outside the code — by designers in a spreadsheet, not by editing Blueprints
**THEN** represent it as a data table based on a structure, so the data lives in an editable table (or an imported CSV) and the Blueprint reads rows by name.
**ELSE** where the data is fixed and small, a structure variable or a map is simpler.

## Do
- Define the row shape as a structure first; the data table is a table of that structure.
- Create the data table (Content Browser → ADD → Miscellaneous → Data Table) and choose the structure as its row type.
- Add rows in the Data Table Editor; each row has a unique row name (rename by right-click → Rename).
- Import the table from a CSV file (Content Browser → Import, choosing the structure in the Choose DataTable Row Type field) when the data is maintained in a spreadsheet.
- Reference the table in a Blueprint with a Data Table > Object Reference variable, set as the default value.
- Read a row with Get Data Table Row (which returns the row's structure and a Row Not Found output), all row names with Get Data Table Row Names, or a column as strings with Get Data Table Column as String.
- Branch on the Row Found / Row Not Found output before using the row.

## Don't
- Don't use a data table for fixed, small data — a structure variable or a map is simpler.
- Don't skip the Row Not Found check — a lookup can fail.
- Don't duplicate row names — they must be unique.
- Don't edit the data by changing Blueprints when it belongs in the table.

## Checklist
- Is the data modified or balanced outside the code?
- Is the row shape a structure?
- Are row names unique?
- Is the Row Not Found case handled?

## Notes
A data table is a table of values based on a structure, usable as a stand-in for a spreadsheet. Its value is data-driven gameplay: the data can be modified in a spreadsheet editor and imported (CSV) without touching the Blueprints, which is what makes balancing fast. The Blueprint side is a lookup by row name — Get Data Table Row returns the row as a structure (which you Break into its fields) and tells you via Row Not Found when the lookup failed.
