---
object_id: DRILL_verify_a_styled_unreal_editor_mode
object_type: drill
name: Verify a Styled Unreal Editor Mode
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- editor_modes
- slate
- verification
cross_links:
- rel: teaches
  target_object_id: AP_bootstrap_a_styled_unreal_editor_mode
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
target_skill: Wire and verify an editor-only mode with shared styles
variants: []
---

# Verify a Styled Unreal Editor Mode

## Practice Task
Build one empty editor mode with a shared style set containing a normal and a small icon. Demonstrate registration, factory creation, icon resolution and style cleanup in an isolated Unreal test project.

## Target Skill
This exercise gives practice in `AP_bootstrap_a_styled_unreal_editor_mode`.

Wire and verify an editor-only mode with shared styles, separating build errors, registration errors and resource-lifetime errors.

## Setup
An Unreal installation with its editor C++ toolchain, a disposable project, and an editor plugin module. Use a local icon image with known dimensions; no network or paid model calls are needed.

## Instructions
1. Apply `AP_bootstrap_a_styled_unreal_editor_mode` with unique fixture names so the exercise cannot overwrite another mode or style.
2. Build the editor target and retain the build result.
3. In the running editor process, inspect the registered factory and confirm the ID, name, visibility, ordering priority and icon keys. Create a mode instance and observe its property-widget policy.
4. Resolve both icon brushes through `FSlateIcon`, and record their image paths and requested dimensions.
5. Release consumers and remove the fixture's mode registration. Then unregister the style, reset its owner and observe that both registry lookups fail.
6. Repeat registration and cleanup with the same fixture names. Record the second result as well as the first.
7. Explain why this feature belongs in an editor module and why its style belongs to the shared module lifetime.

## Success Check
- A retained editor build result proves compilation and linking.
- Runtime observations prove factory metadata, instance creation and both icon resolutions; a screenshot or source listing alone is insufficient.
- The resource file exists and both requested brush sizes match the configuration. A fallback or missing brush does not count as an icon success.
- After cleanup, registry lookups for the fixture mode and style fail; the second cycle succeeds with the same names.
- The explanation distinguishes editor/runtime dependency boundaries and module/mode ownership.
- State whether viewport activation was actually tested. Registry success alone must not be reported as interactive tool success.

## Common Failures
- Changing includes while leaving the providing modules undeclared.
- Inspecting the code instead of observing the running registry.
- Resolving one icon key and assuming the small key works too.
- Resetting the style owner before unregistering its borrowed registry entry.
- Reporting a fixed shortcut from an ordering priority without observing the installed mode order.

## Notes
An empty mode makes the boundary checks small enough to diagnose independently. Its success establishes registration and shared resources; it cannot establish the correctness of tools that have not yet been added.
