---
object_id: AP_exchange_unreal_editor_camera_bookmarks
object_type: ap
name: Exchange Unreal Editor Camera Bookmarks
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
- rel: supports
  target_object_id: PAT_validate_unreal_camera_bookmarks_before_navigation
- rel: supports
  target_object_id: PAT_report_unreal_tool_outcomes_through_a_small_facade
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Exchange Unreal Editor Camera Bookmarks

## Objective
Copy a supported editor camera pose to text or navigate to an external bookmark with explicit viewport scope and useful outcomes.

## Steps / Flow
1. Declare copy or navigation, the text interface and the intended viewport. Apply `PAT_validate_unreal_camera_bookmarks_before_navigation` to establish the complete format and target policy.
2. For copy, query the chosen camera and stop on unavailable or invalid pose. Format the complete pose before publishing text or replacing the clipboard.
3. For navigation, read external text once at execution and validate the entire pose before resolving and changing the camera. Stop on invalid input with unchanged camera state.
4. Apply the pose to the chosen supported viewport, then read back location and rotation. On mismatch, report the observed partial outcome and recovery needs rather than silently reporting success.
5. Apply `PAT_report_unreal_tool_outcomes_through_a_small_facade` for completion or rejection through the caller's actual interface. Verify round-trip precision, target scope and rejected-input state before declaring the operation qualified.

## Notes
A utility may expose structured pose/text functions without using the operating-system clipboard. Testing that path does not establish the clipboard or toolbar path.
