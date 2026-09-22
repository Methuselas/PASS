---
object_id: PAT_use_niagara_debug_console_commands_when_debugging_must_run_outside_the_debugger_ui
object_type: pattern
name: Use Niagara Debug Console Commands When Debugging Must Run Outside the Debugger
  UI
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 3 rough
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- niagara
- vfx
cross_links: []
reference:
  source_title: Build Stunning Real-time VFX with Unreal Engine 5
  author: Hrishikesh Andurlekar
confidence: high
references: []
variants: []
---

# Use Niagara Debug Console Commands When Debugging Must Run Outside the Debugger UI

## Pattern Rule
**IF** Niagara diagnostics must be activated at runtime, from Blueprint, or at a specific gameplay point
**THEN** configure the Niagara Debug HUD through its console commands instead of relying only on the debugger window.

## Do
- Use fx.Niagara.Debug.Hud arguments to enable the needed runtime information.
- Invoke the command through Execute Console Command when a Blueprint-controlled trigger is useful.

## Don't
- Do not memorize one fixed command string when the HUD options should match the diagnostic question.

## Checklist
- The required Niagara diagnostics appear in the runtime context where the issue occurs.

## Notes
Console control provides the same diagnostic surface in contexts where the full debugger UI is inconvenient.
