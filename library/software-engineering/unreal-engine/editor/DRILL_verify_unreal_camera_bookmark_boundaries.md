---
object_id: DRILL_verify_unreal_camera_bookmark_boundaries
object_type: drill
name: Verify Unreal Camera Bookmark Boundaries
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- editor_tools
- navigation
cross_links:
- rel: teaches
  target_object_id: AP_exchange_unreal_editor_camera_bookmarks
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
target_skill: Verify Unreal Camera Bookmark Boundaries
---

# Verify Unreal Camera Bookmark Boundaries

## Practice Task
Produce and run a disposable camera-bookmark fixture with a complete round trip, rejected text and two distinguishable viewport targets.

## Target Skill
Practise `AP_exchange_unreal_editor_camera_bookmarks` with explicit input and target contracts.

## Setup
An Unreal editor toolchain and disposable project with two camera clients; use visible viewports when qualifying interactive behavior.

## Instructions
1. State the accepted format, precision, incomplete-input and viewport-selection policies with reasons.
2. Query and serialize a distinguishable location/rotation, parse it and record the exact source, text and recovered pose.
3. Navigate one target and record before/after poses for both camera clients.
4. Run missing, malformed, nonfinite, extra-field and unavailable-target cases; record outcomes, reasons and before/after camera state.
5. Record which interfaces actually ran. If using the clipboard or toolbar, record their observed transfer/action separately from direct native calls.
6. Retain the built fixture and execution evidence.

## Success Check
- The fixture builds and executes; parser predictions or proposed code alone are insufficient.
- Recovered pose matches the declared precision, and only the declared target changes.
- Invalid input and unavailable targets supply useful reasons and leave camera state unchanged.
- Format and target choices have recorded reasons; clipboard/toolbar claims have evidence from those interfaces rather than being inferred from native helpers.

## Common Failures
- Treating a numeric conversion's zero as proof that text was valid.
- Accepting incomplete rotation without defining it.
- Moving the first viewport while claiming it was the focused viewport.

## Notes
Direct native checks and visible navigation qualify different interfaces.
