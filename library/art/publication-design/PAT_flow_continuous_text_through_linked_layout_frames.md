---
object_id: PAT_flow_continuous_text_through_linked_layout_frames
object_type: pattern
name: Flow Continuous Text Through Linked Layout Frames
library_path:
- art
- publication-design
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- publication_design
- text_flow
- columns
- pages
- layout
- reflow
cross_links: []
reference:
  source_title: 'Indie Publishing: How to Design and Produce Your Own Book'
  author: Joseph Galbreath
confidence: high
references: []
variants: []
---

# Flow Continuous Text Through Linked Layout Frames

## Pattern Rule
**IF** one continuous text stream must run across multiple columns or pages
**THEN** connect its text containers into one ordered flow so edits and reflow propagate through the sequence instead of manually dividing the copy into independent blocks
**ELSE** keep separate text containers independent when their contents are genuinely unrelated.

## Do
- Establish the intended reading order of columns and pages before linking the text flow.
- Keep one continuous article, chapter, or comparable text stream connected through the containers that belong to it.
- Let added or removed copy reflow through later containers, then inspect the affected pages for new breaks, widows, awkward whitespace, or displaced supporting elements.
- Separate unrelated sidebars, captions, marginal notes, or other independent content from the main flow when they need their own placement control.
- Recheck the end of the flow after major edits so no copy is overset, omitted, or stranded in an unintended container.

## Don't
- Do not cut one continuous text into manually maintained page-sized chunks merely to hold the current layout in place.
- Do not link unrelated content simply because it appears on adjacent pages.
- Do not assume automatic reflow preserves good page composition after the text changes.
- Do not ignore the final container; a visually clean earlier page can hide missing or overset text downstream.

## Checklist
- The linked containers follow the intended reading order.
- Continuous copy can grow or shrink without manual repasting into every later page.
- Independent content remains independently placeable.
- Reflow has been visually checked across every affected page or spread.
- The end of the flow contains all intended text without overset or accidental truncation.

## Notes
Page-layout software commonly implements this as threaded or linked text frames. The durable publication-design principle is to model a continuous text stream as one flow across its assigned containers, then treat reflow as a trigger for renewed page inspection rather than freezing the text into brittle page-by-page fragments.
