---
object_id: PAT_validate_unreal_camera_bookmarks_before_navigation
object_type: pattern
name: Validate Unreal Camera Bookmarks Before Navigation
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: PAT_barricade_dirty_data_at_a_named_boundary
tags:
- unreal_engine
- editor_tools
- navigation
cross_links: []
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Validate Unreal Camera Bookmarks Before Navigation

## Pattern Rule
**IF** an Unreal editor tool exchanges camera poses through text or the clipboard
**THEN** check the queried pose before publication, validate the entire declared external format before navigation, and change only a deliberately chosen viewport while keeping rejected input from changing the camera.

## Do
- Declare the marker, field count, location/rotation order, whitespace and numeric policies. A complete BugItGo pose has location X/Y/Z followed by pitch/yaw/roll.
- Require consumed numeric tokens and finite results; permissive conversion to zero does not establish validity.
- Initialize outputs and assign a complete parsed pose only after all fields validate. If supporting position-only input, define how rotation is retained or supplied explicitly.
- Check camera-query success before formatting or replacing the clipboard.
- Choose viewport scope explicitly and inspect the installed helper's implementation; first perspective viewport and focused viewport need not be the same.
- Serialize enough precision for the intended round trip and verify actual camera readback after navigation.
- Report invalid format, unavailable viewport and failed readback through the caller's interface.

## Don't
- Don't accept incomplete rotation, ignored trailing text or an uninitialized value by accident.
- Don't execute arbitrary clipboard text as a console command to implement pose parsing.

## Checklist
- Are missing, malformed, nonfinite and extra fields rejected before camera mutation?
- Does copy/parse preserve the supported pose precision?
- Does navigation affect exactly the declared viewport?

## Notes
This specializes `PAT_barricade_dirty_data_at_a_named_boundary` at the editor navigation boundary. A text bookmark is not a saved-map identity, actor transform edit or universal viewport persistence guarantee.
