---
object_id: PAT_build_repeated_page_elements_as_shared_system
object_type: pattern
name: Build Repeated Page Elements as a Shared System
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
- page_system
- consistency
- folios
- running_heads
- styles
cross_links: []
reference:
  source_title: 'Indie Publishing: How to Design and Produce Your Own Book'
  author: Joseph Galbreath
confidence: high
references: []
variants: []
---

# Build Repeated Page Elements as a Shared System

## Pattern Rule
**IF** page numbers, running heads, guides, rules, or other publication elements recur across many pages
**THEN** define their placement and appearance through shared page or style rules so repeated elements stay consistent and can be changed globally
**ELSE** place one-off elements locally when they are genuinely unique.

## Do
- Identify which page elements are structural repeats before populating the full publication.
- Define recurring positions, spacing, typography, and graphic rules once, then apply them consistently to the pages that use that family.
- Allow multiple page families when sections need genuinely different recurring structures, while keeping shared relationships compatible across the publication.
- Treat a local override as an exception that should remain visibly intentional and easy to distinguish from the underlying system.
- Recheck overridden pages after global changes because an exception may no longer inherit later corrections.

## Don't
- Do not redraw the same folio, header, rule, or guide independently on every page when one shared definition can own it.
- Do not create an exception merely to repair a weak underlying template; fix the shared system when the problem repeats.
- Do not assume an overridden page will continue to receive later system updates.
- Do not make every section mechanically identical when its function requires a different page family.

## Checklist
- Repeating page elements share consistent placement and styling.
- A global change can update the recurring system without manual page-by-page reconstruction.
- Local overrides are deliberate and limited.
- Distinct page families remain recognizably related.
- Folios, running heads, and recurring rules do not drift across the publication.

## Notes
Professional page-layout tools expose this principle through master pages, recurring page elements, and repeatable paragraph rules. The durable craft decision is tool-independent: repeated publication elements should be modeled as a system rather than copied as unrelated local marks. That makes consistency easier to preserve and makes later revision less destructive.
