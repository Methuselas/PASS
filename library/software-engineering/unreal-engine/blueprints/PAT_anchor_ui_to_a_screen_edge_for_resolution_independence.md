---
object_id: PAT_anchor_ui_to_a_screen_edge_for_resolution_independence
object_type: pattern
name: Anchor UI to a Screen Edge for Resolution Independence
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- umg
- ui
- layout
- anchors
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Anchor UI to a Screen Edge for Resolution Independence

## Pattern Rule
**IF** a UI element should keep the same relative position on screen across different resolutions and aspect ratios — a HUD meter in a corner, a counter along the top
**THEN** anchor the element to a screen edge or corner rather than leaving it at absolute canvas coordinates, so its position is defined relative to the anchor and it stays put when the screen size or ratio changes.

## Do
- In the Details panel, open the Anchors dropdown and pick the edge or corner the element should stick to (top-left, top-center, top-right, and so on).
- Set the element's Position and Size relative to the anchor; a negative X offsets an element anchored to the right edge back toward the center.
- For a group of elements, anchor the container that holds them so the group moves as one.

## Don't
- Don't position elements with absolute canvas coordinates alone — they drift when the resolution or aspect ratio changes.
- Don't anchor each child of a group separately when the group should move as one — anchor the container.

## Checklist
- The element's anchor is set to the edge or corner it should stick to.
- The element's position is defined relative to the anchor, not absolute canvas coordinates.
- The element keeps the same relative position when the screen size or ratio changes.

## Notes
Anchors define a widget's desired position on the canvas regardless of screen size. Because screen sizes and aspect ratios vary, anchoring an element to an edge or corner keeps it in the same relative position — a corner, the top-center — across all of them, whereas absolute canvas coordinates would drift. Anchor the container that holds a group of elements so the group moves as one. A negative position offset moves an element anchored to one edge back toward the center: a top-right-anchored element with a negative X sits to the left of the right edge.
