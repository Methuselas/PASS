---
object_id: PAT_own_unreal_editor_debug_draw_lifetimes
object_type: pattern
name: Own Unreal Editor Debug Draw Lifetimes
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
- debugging
- rendering
- lifecycle
cross_links:
- rel: related_to
  target_object_id: PAT_centralize_selection_driven_unreal_editor_debug_ticks
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Own Unreal Editor Debug Draw Lifetimes

## Pattern Rule
**IF** an Unreal tool queues edit-time debug text or primitives for later viewport drawing
**THEN** retain drawing records in an owned service with explicit world/view scope, bounded duration and count, a user-visible show flag, and symmetric delegate/ticker teardown.

## Do
- Register one named custom show flag and one `UDebugDrawService` delegate; retain handles and unregister before module shutdown.
- Store each record with its intended world or scene, location, presentation data, expiration policy and optional stable owner/key.
- Define zero duration as one frame, clamp invalid durations/scales and age records with a monotonic editor time source. Remove expired records without invalidating iteration.
- Bound retained count and text length; let repeated owner/key submissions update an existing record when appropriate instead of growing without limit.
- In the draw callback, reject null canvas/view, wrong world/scene and out-of-view points before projection. Handle behind-camera or invalid projected coordinates.
- Expose a small runtime-safe facade only if non-editor callers genuinely need it; make absence of the drawing service a safe no-op with an optional diagnostic result.
- Clear records on world cleanup/map change and on owner invalidation where records are not meant to outlive the source.

## Don't
- Don't draw records into every editor viewport regardless of their world.
- Don't keep unbounded strings alive because a caller continually resubmits duration-based text.
- Don't assume the debug draw callback supplies a player controller in edit mode.
- Don't leave delegate or ticker handles registered after module unload.

## Checklist
- Are records scoped to the correct world/view and removed on map/module teardown?
- Are duration, count, scale and string size bounded?
- Can users disable the layer through a stable show flag?
- Does projection reject invalid/behind-camera points without leaking records or callbacks?

## Notes
Three-dimensional editor text is one consumer. The ownership contract also applies to transient labels, markers and overlays that cross a frame boundary between tool logic and viewport rendering.
