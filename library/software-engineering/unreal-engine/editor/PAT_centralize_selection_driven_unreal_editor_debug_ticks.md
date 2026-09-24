---
object_id: PAT_centralize_selection_driven_unreal_editor_debug_ticks
object_type: pattern
name: Centralize Selection-Driven Unreal Editor Debug Ticks
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
- selection
- performance
cross_links:
- rel: related_to
  target_object_id: PAT_enforce_an_explicit_unreal_selection_policy
- rel: related_to
  target_object_id: PAT_keep_unreal_editor_dependencies_in_editor_modules
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Centralize Selection-Driven Unreal Editor Debug Ticks

## Pattern Rule
**IF** selected Unreal actors or components need edit-time debug updates without a dedicated visualizer
**THEN** let one editor-owned ticker discover a bounded selection, invoke a runtime-safe development interface, and remove the ticker before its module owner disappears.

## Do
- Put only the Blueprint-callable interface and runtime-safe data contract in a shared/runtime module; keep selection APIs, editor ticking and editor rendering in an editor module.
- Mark the interface callable in editor and development-only when shipping execution is not intended. Still guard callers by world type/build context; metadata is not lifecycle control.
- Register one ticker in module startup, retain its handle and remove/reset it during shutdown.
- Snapshot the current editor selection, define deterministic actor/component order and invoke only valid objects implementing the interface.
- Bound work by a nonnegative local editor preference and a time/work budget. Make zero mean disabled and surface truncation so missing debug output is understandable.
- Prevent re-entrant or duplicate invocation when an object is reachable through more than one selected owner.
- Keep interface implementations observational by default. Any edit-time mutation needs its own transaction, dirtying and undo contract.

## Don't
- Don't enable editor tick on every actor merely for conditional debug drawing.
- Don't subscribe every actor instance to global selection delegates.
- Don't place editor-only dependencies in the runtime module that declares the interface.
- Don't make a selection-size cap depend on unspecified iteration order.

## Checklist
- Is there exactly one owned ticker and can it be disabled locally?
- Are actor and component invocations deterministic, deduplicated and bounded?
- Does a packaged/runtime build remain free of editor-module dependencies and unintended calls?
- Are skipped items and budget exhaustion observable?

## Notes
Centralization changes the scaling cost from every placed actor observing editor state to one service examining only the current selection. The interface is a capability boundary, not permission to mutate authored data each frame.
